"""Run local tools with streamed output, deadlines and cancellation."""

import codecs
import errno
import os
import shutil
import signal
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from threading import Event
from time import monotonic


class RunCancelled(RuntimeError):
    """The operator cancelled the active command."""


@contextmanager
def file_lock(path, *, wait=True):
    """Hold a workspace lock for the lifetime of an open descriptor."""
    with path.open("a+b") as handle:
        if os.name == "nt":
            import msvcrt

            if handle.tell() == 0:
                handle.write(b"\0")
                handle.flush()
            handle.seek(0)
            try:
                msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK if wait else msvcrt.LK_NBLCK, 1)
            except OSError as error:
                if not wait and error.errno in {errno.EACCES, errno.EAGAIN}:
                    raise BlockingIOError(errno.EAGAIN, "File is locked", path) from error
                raise
        else:
            import fcntl

            mode = fcntl.LOCK_EX if wait else fcntl.LOCK_EX | fcntl.LOCK_NB
            fcntl.flock(handle, mode)
        yield


def stop_process(process):
    if os.name == "nt":
        taskkill = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "taskkill.exe"
        try:
            subprocess.run((taskkill, "/PID", str(process.pid), "/T", "/F"), check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
        except (OSError, subprocess.SubprocessError):
            process.kill()
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=2)
        except ProcessLookupError:
            pass
        except subprocess.TimeoutExpired:
            pass
        # A shell can exit before the children it started.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    process.wait()


def run_command(args, cwd, *, timeout=120, output=None, cancel=None):
    cancel = cancel if cancel is not None else Event()
    if cancel.is_set():
        raise RunCancelled("Run cancelled.")
    if not shutil.which(os.fspath(args[0])):
        raise FileNotFoundError(f"Required tool is unavailable: {args[0]}")

    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")
    if hasattr(os, "getuid"):
        env.update(ASE_UID=str(os.getuid()), ASE_GID=str(os.getgid()))

    # Two handles let tools write freely while the reader tails the log in bounded chunks.
    with tempfile.TemporaryDirectory() as directory:
        log = Path(directory) / "command.log"
        with log.open("wb") as writer, log.open("rb") as reader:
            process = subprocess.Popen(args, cwd=cwd, env=env, stdout=writer,
                                       stderr=subprocess.STDOUT, start_new_session=os.name != "nt")
            decoder = codecs.getincrementaldecoder("utf-8")(errors="replace")
            parts = []
            deadline = monotonic() + timeout

            def drain():
                while data := reader.read(16_384):
                    content = decoder.decode(data)
                    parts.append(content)
                    if output and content:
                        output(content)
                    if process.poll() is None and (cancel.is_set() or monotonic() >= deadline):
                        break

            interrupted = None
            try:
                while process.poll() is None:
                    drain()
                    if cancel.is_set():
                        interrupted = RunCancelled("Run cancelled.")
                        break
                    if monotonic() >= deadline:
                        interrupted = subprocess.TimeoutExpired(args, timeout)
                        break
                    cancel.wait(0.1)
            finally:
                if process.poll() is None or interrupted is not None:
                    stop_process(process)

            drain()
            tail = decoder.decode(b"", final=True)
            if tail and output:
                output(tail)
            stdout = "".join(parts) + tail
            if isinstance(interrupted, subprocess.TimeoutExpired):
                interrupted.output = stdout
            elif interrupted and stdout:
                interrupted = RunCancelled(f"{interrupted}\n{stdout}")
            if interrupted:
                raise interrupted
            if process.returncode:
                raise RuntimeError(f"Exit {process.returncode}\n{stdout}")
            return stdout
