"""Workflow execution, local probes and persisted evidence."""

import csv
import hashlib
import json
import os
import secrets
import ssl
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from functools import partial
from pathlib import Path
from time import monotonic
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, HTTPSHandler, ProxyHandler, Request, build_opener

from execution import RunCancelled, file_lock, run_command
from scaffold import DEFAULT_PORT, DEFAULT_TLS_PORT, gateway_port, generate, valid_port
from stages import STAGES

CHECKS = {
    "setup": "Install project tools into .venv",
    "contract": "Validate OpenAPI",
    "compose_config": "Validate Compose",
    "docker_build": "Build service images",
    "compose_up": "Start the local stack",
    "smoke": "Smoke-test the gateway",
    "unit": "Run pytest isolation tests",
    "newman": "Run Newman integration tests",
    "load": "Run Locust on loopback",
    "cert": "Create local TLS and JWT secrets",
    "secure_up": "Start the HTTPS stack",
    "tls": "Verify TLS trust",
    "bandit": "Scan source with Bandit",
    "audit": "Audit dependencies with pip-audit",
    "trivy": "Scan the gateway image with Trivy",
    "access": "Verify bearer token and scope checks",
    "logs": "Collect Compose logs",
    "down": "Stop reference stacks",
}
QUICK = ("contract", "unit", "bandit")
BASELINE = ("contract", "unit", "compose_config", "docker_build", "compose_up", "smoke", "newman")
SECURE = ("cert", "secure_up", "tls", "access")
SCANS = ("bandit", "audit", "trivy")
FULL_RUN = BASELINE + ("load",) + SECURE + SCANS + ("logs",)
PROFILES = {"quick": QUICK, "baseline": BASELINE, "full": FULL_RUN}
DEPENDENCIES = {
    "docker_build": ("compose_config",),
    "compose_up": ("compose_config", "docker_build"),
    "smoke": ("compose_up",),
    "newman": ("compose_up",),
    "load": ("compose_up", "smoke"),
    "secure_up": ("cert",),
    "tls": ("secure_up",),
    "access": ("secure_up", "tls"),
    "trivy": ("compose_up",),
}
PROJECT_FILES = {"Dockerfile", ".dockerignore", "Pipfile", "Pipfile.lock", "uv.lock", "poetry.lock"}
PROJECT_SUFFIXES = {".py", ".json", ".toml", ".yaml", ".yml", ".ini", ".cfg", ".txt", ".in", ".lock"}


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def atomic_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, filename = tempfile.mkstemp(dir=path.parent)
    temporary = Path(filename)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


class Workspace:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.state = self.root / ".ase-workbench"
        self.state_path = self.state / "workspace.json"
        self.project = "ase-" + hashlib.sha256(os.fsencode(self.root)).hexdigest()[:10]
        self.reload()

    def reload(self):
        try:
            loaded = json.loads(self.state_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            loaded = {"notes": {}, "reviews": {}, "checks": {}, "history": []}
        if not isinstance(loaded, dict) or any(not isinstance(loaded.get(k), dict)
                                               for k in ("notes", "reviews", "checks")):
            raise ValueError("Unrecognized workspace state")
        if "history" not in loaded:
            loaded["history"] = sorted((dict(result, check=key) for key, result in loaded["checks"].items()),
                                       key=lambda record: record["log"])
        if not isinstance(loaded["history"], list):
            raise ValueError("Unrecognized workspace run history")
        self.data = loaded

    def prepare_state_folder(self):
        if self.state.is_symlink():
            raise ValueError("The evidence folder must be local to the workspace.")
        self.state.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def edit_state(self):
        self.prepare_state_folder()
        with file_lock(self.state / "state.lock"):
            self.reload()
            yield
            atomic_text(self.state_path, json.dumps(self.data, indent=2) + "\n")

    def set_note(self, key, value):
        with self.edit_state():
            if self.data["notes"].get(key, "") != value:
                self.data["notes"][key] = value
                self.data["reviews"].pop(key, None)

    def scaffold(self, port=None, tls_port=None):
        existing_port = self.port() if (self.root / "compose.json").is_file() else None
        existing_tls = self.port(secure=True) if (self.root / "compose.secure.json").is_file() else None
        if port is not None and existing_port is not None and valid_port(port) != existing_port:
            raise ValueError("The existing HTTP port is set in compose.json.")
        if tls_port is not None and existing_tls is not None and valid_port(tls_port) != existing_tls:
            raise ValueError("The existing HTTPS port is set in compose.secure.json.")
        if port is None:
            port = existing_port or DEFAULT_PORT
        if tls_port is None:
            http = valid_port(port)
            tls_port = existing_tls or (http + 1 if http < 65535 else DEFAULT_TLS_PORT)
        self.root.mkdir(parents=True, exist_ok=True)
        return generate(self.root, port, tls_port)

    def port(self, *, secure=False):
        file = "compose.secure.json" if secure else "compose.json"
        return gateway_port(self.root / file)

    def endpoint(self, *, secure=False):
        scheme = "https" if secure else "http"
        return f"{scheme}://127.0.0.1:{self.port(secure=secure)}"

    def fingerprint(self):
        digest = hashlib.sha256()
        inputs = [file for file in self.root.glob("*")
                  if file.name in PROJECT_FILES or file.suffix in PROJECT_SUFFIXES]
        for directory in ("src", "app", "tests", "config", ".github/workflows"):
            base = self.root / directory
            if base.resolve().is_relative_to(self.root):
                inputs.extend(base.rglob("*"))
        for file in sorted(inputs):
            relative = file.relative_to(self.root)
            if any(part.startswith(".") and part not in {".github", ".dockerignore"}
                   or part == "__pycache__" for part in relative.parts):
                continue
            if file.is_symlink():
                content = b"symlink\0" + os.fsencode(file.readlink())
            elif file.is_file() and file.resolve().is_relative_to(self.root) and file.suffix != ".pyc":
                content = file.read_bytes()
            else:
                continue
            digest.update(relative.as_posix().encode() + b"\0")
            digest.update(hashlib.sha256(content).digest())
        return digest.hexdigest()

    def result(self, key, revision=None):
        item = self.data["checks"].get(key)
        if item and item["fingerprint"] != (revision if revision is not None else self.fingerprint()):
            return "Stale"
        return item["status"] if item else "Pending"

    def release_waiting(self, revision):
        required = ("vision", "stories", "architecture", "smells")
        return ([STAGES[stage].title for stage in required if self.status(stage, revision) != "Reviewed"]
                + [CHECKS[check] for check in FULL_RUN if self.result(check, revision) != "Passed"])

    def review(self, key):
        with self.edit_state():
            revision = self.fingerprint()
            if not self.data["notes"].get(key, "").strip():
                raise ValueError("Record the decision or evidence in the stage notes first.")
            if any(self.result(check, revision) != "Passed" for check in STAGES[key].checks):
                raise ValueError("Pass the stage checks for the current project revision first.")
            if key == "delivery":
                waiting = self.release_waiting(revision)
                if waiting:
                    raise ValueError("Complete the release evidence first.\n" + "\n".join(waiting))
            self.data["reviews"][key] = revision

    def status(self, key, revision=None):
        stage = STAGES[key]
        revision = revision if revision is not None else self.fingerprint()
        results = [self.result(check, revision) for check in stage.checks]
        if any(result in {"Failed", "Blocked", "Cancelled"} for result in results):
            return "Needs attention"
        if self.data["reviews"].get(key) == revision:
            if key == "delivery" and self.release_waiting(revision):
                return "Needs attention"
            if any(result != "Passed" for result in results):
                return "Needs attention"
            return "Reviewed"
        if results and all(result == "Passed" for result in results):
            return "Verified"
        if "Stale" in results or key in self.data["reviews"]:
            return "Stale"
        if self.data["notes"].get(key, "").strip():
            return "In progress"
        return "Pending"

    def report(self, destination):
        revision = self.fingerprint()
        lines = ["# ASE workflow evidence", "", f"Generated {stamp()}", "",
                 f"Project fingerprint: `{revision}`", ""]
        for key, stage in STAGES.items():
            lines.extend([f"## {stage.title}", "", f"Status: **{self.status(key, revision)}**", "",
                          f"Tools: {stage.tools}", f"Expected output: {stage.output}", "",
                          self.data["notes"].get(key, "").strip() or "No notes recorded.", ""])
            for check in stage.checks:
                result = self.data["checks"].get(check, {})
                detail = f" · {result['when']} · {result['log']}" if result else ""
                if result.get("seconds") is not None:
                    detail += f" · {result['seconds']:.1f} s"
                lines.append(f"- {CHECKS[check]}: {self.result(check, revision)}{detail}")
                lines.extend(f"  - Evidence file: `{file}`" for file in result.get("artifacts", ()))
            lines.append("")
        atomic_text(Path(destination), "\n".join(lines))

    def release_candidate(self):
        self.reload()
        fingerprint = self.fingerprint()
        if self.status("delivery", fingerprint) != "Reviewed":
            raise ValueError("Review the release stage for this project revision first.")
        checks = {key: self.data["checks"][key] for key in FULL_RUN}
        release = self.state / "releases" / fingerprint[:16]
        release.mkdir(parents=True, exist_ok=True)
        manifest = {
            "kind": "local-release-candidate",
            "created_at": stamp(),
            "fingerprint": fingerprint,
            "checks": checks,
            "release_notes": self.data["notes"]["delivery"],
        }
        atomic_text(release / "manifest.json", json.dumps(manifest, indent=2) + "\n")
        self.report(release / "evidence.md")
        return release

    @property
    def python(self):
        relative = "Scripts/python.exe" if os.name == "nt" else "bin/python"
        return self.root / ".venv" / relative

    def compose(self, *args, secure=False):
        variant = "compose.secure.json" if secure else "compose.json"
        return ("docker", "compose", "-p", self.project + ("-tls" if secure else ""), "-f", variant, *args)

    def command(self, args, timeout=120, capture=False, *, output=None, cancel=None):
        result = run_command(args, self.root, timeout=timeout, output=output, cancel=cancel)
        return result.strip() if capture else result or "Command completed."

    def doctor(self, *, cancel=None):
        probes = (
            ("Python project tools", (str(self.python), "-I", "-c",
             "import bandit, locust, openapi_spec_validator, pip_audit, pytest; print('Python tools installed')"),
             "Use Install project tools to prepare .venv."),
            ("Docker Compose", ("docker", "compose", "version"), "Install Docker with Compose v2."),
            ("Docker Engine", ("docker", "info", "--format", "{{.ServerVersion}}"), "Start Docker and retry."),
            ("Newman", ("newman", "--version"), "Install Newman 6 and put it on PATH."),
            ("OpenSSL", ("openssl", "req", "-help"), "Use OpenSSL with the req -addext option."),
            ("Trivy", ("trivy", "--version"), "Install Trivy for the image check."),
        )
        for name, args, hint in probes:
            try:
                version = self.command(args, timeout=8, capture=True, cancel=cancel)
                if name == "OpenSSL":
                    if "-addext" not in version:
                        yield name, False, hint
                        continue
                    version = "req supports -addext"
                yield name, True, version.splitlines()[0] if version else "Available"
            except RunCancelled:
                raise
            except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
                detail = str(error).strip().splitlines()[0]
                yield name, False, f"{hint} ({detail})"

    def http(self, path, *, secure=False, data=None, token=None, cancel=None):
        if cancel is not None and cancel.is_set():
            raise RunCancelled("Run cancelled.")
        handlers = [ProxyHandler({})]
        if secure:
            handlers.append(HTTPSHandler(context=ssl.create_default_context(
                cafile=str(self.root / ".ase-secrets/cert"))))
        headers = {}
        if data is not None:
            headers["Content-Type"] = "application/json"
        if token is not None:
            headers["Authorization"] = "Bearer " + token
        req = Request(self.endpoint(secure=secure) + path,
                      data=json.dumps(data).encode() if data is not None else None, headers=headers)
        try:
            response = build_opener(*handlers, NoRedirect()).open(req, timeout=7)
        except HTTPError as error:
            response = error
        with response:
            return response.status, json.loads(response.read())

    def certificates(self, command=None):
        command = command or self.command
        folder = self.root / ".ase-secrets"
        folder.mkdir(mode=0o700, exist_ok=True)
        if folder.is_symlink():
            raise ValueError("The secrets directory must be local to this workspace.")
        if not all((folder / name).is_file() for name in ("cert", "key")):
            with tempfile.TemporaryDirectory(dir=folder) as temp:
                cert, key = (Path(temp) / name for name in ("cert", "key"))
                command(("openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "30",
                         "-subj", "/CN=localhost", "-addext", "subjectAltName=DNS:localhost,IP:127.0.0.1",
                         "-keyout", str(key), "-out", str(cert)))
                key.chmod(0o600)
                key.replace(folder / "key")
                cert.replace(folder / "cert")
        for name in ("jwt", "password_math", "password_text"):
            filename = folder / name
            try:
                with open(filename, "x", opener=_secret_opener, encoding="utf-8") as handle:
                    handle.write(secrets.token_urlsafe(48) + "\n")
            except FileExistsError:
                pass
        command(("openssl", "x509", "-in", str(folder / "cert"), "-checkend", "0", "-noout"))
        return "Development TLS certificate and local secret files are ready."

    def access(self, cancel=None):
        def probe(token, expected):
            code, body = self.http("/calc/add?a=0&b=9", secure=True, token=token, cancel=cancel)
            if code != expected or (code == 200 and body != {"s": 9}):
                raise RuntimeError(f"Expected HTTP {expected}; received HTTP {code}.")

        probe(None, 401)
        probe("invalid-token", 401)
        for user, expected in (("math", 200), ("text", 403)):
            password = (self.root / ".ase-secrets" / ("password_" + user)).read_text().strip()
            code, body = self.http("/login", secure=True, data={"username": user, "password": password}, cancel=cancel)
            if code != 200 or not body.get("access_token"):
                raise RuntimeError(f"Expected successful login for lab user {user}; received HTTP {code}.")
            probe(body["access_token"], expected)
        return "Passed: missing 401, invalid 401, authorized zero input 200, insufficient scope 403."

    def execute(self, key, *, output=None, cancel=None, build=True, artifact_prefix=None):
        if key not in CHECKS:
            raise ValueError(f"Unknown check: {key}")
        command = partial(self.command, output=output, cancel=cancel)
        py = str(self.python)
        commands = {
            "contract": (py, "-m", "openapi_spec_validator", "openapi.json"),
            "compose_config": self.compose("config", "--quiet"),
            "docker_build": self.compose("build"),
            "unit": (py, "-m", "pytest", "-q", "tests/test_service.py"),
            "bandit": (py, "-m", "bandit", "app.py"),
            "audit": (py, "-m", "pip_audit", "-r", "requirements.txt"),
        }
        if key in commands:
            return command(commands[key], timeout=600)
        if key in {"compose_up", "secure_up"}:
            secure = key == "secure_up"
            self.port(secure=secure)
            build_flag = "--build" if build or secure else "--no-build"
            return command(self.compose("up", "-d", build_flag, "--wait", "--wait-timeout", "90", secure=secure),
                           timeout=600)
        if key == "newman":
            return command(("newman", "run", "tests/gateway.postman_collection.json",
                            "--env-var", f"baseUrl={self.endpoint()}"), timeout=600)
        if key == "load":
            prefix = artifact_prefix or self.state / "load"
            prefix.parent.mkdir(parents=True, exist_ok=True)
            stdout = command((py, "-m", "locust", "-f", "locustfile.py", "--headless", "-u", "5", "-r", "2",
                              "-t", "15s", "--host", self.endpoint(), "--csv", str(prefix)), timeout=60)
            summary = self.load_summary(prefix)
            if output:
                output(f"\n{summary}\n")
            return f"{stdout}\n{summary}"
        if key == "setup":
            command((sys.executable, "-m", "venv", ".venv"), timeout=180)
            return command((py, "-m", "pip", "install", "-r", "requirements-dev.txt"), timeout=600)
        if key == "cert":
            return self.certificates(command)
        if key == "access":
            return self.access(cancel)
        if key == "trivy":
            image = command(self.compose("images", "-q", "gateway"), capture=True)
            if not image or len(image.splitlines()) != 1:
                raise RuntimeError("Start the normal Compose stack before scanning its gateway image.")
            return command(("trivy", "image", "--severity", "HIGH,CRITICAL", "--ignore-unfixed",
                            "--exit-code", "1", image), timeout=600)
        if key == "down":
            lines, failed = [], False
            for secure, name in ((False, "compose.json"), (True, "compose.secure.json")):
                if not (self.root / name).is_file():
                    continue
                try:
                    lines.append(command(self.compose("down", secure=secure)))
                except RunCancelled:
                    raise
                except (RuntimeError, subprocess.TimeoutExpired) as error:
                    failed = True
                    lines.append(f"{name}: {error}")
            if failed:
                raise RuntimeError("\n".join(lines))
            return "\n".join(lines) or "No Compose profiles in this workspace."
        if key == "logs":
            result = command(self.compose("logs", "--no-color", "--tail", "100"), capture=True)
            if not result:
                raise RuntimeError("No runtime logs were returned. Start the local stack first.")
            return result
        cases = [("/health", {"status": "ok"})] if key == "tls" else [
            ("/calc/add?a=0&b=9", {"s": 9}), ("/str/lower?a=ASE", {"s": "ase"})]
        for path, expected in cases:
            code, body = self.http(path, secure=key == "tls", cancel=cancel)
            if (code, body) != (200, expected):
                raise RuntimeError(f"{path}: expected 200 and {expected}; received {code} and {body}.")
        return "\n".join(f"{path} → HTTP 200 {body}" for path, body in cases)

    @staticmethod
    def load_summary(prefix):
        with prefix.with_name(prefix.name + "_stats.csv").open(encoding="utf-8", newline="") as handle:
            total = next((row for row in csv.DictReader(handle) if row.get("Name") == "Aggregated"), None)
        if total is None:
            raise ValueError("Locust did not produce aggregate statistics.")
        count = int(total.get("Request Count") or "0")
        failures = int(total.get("Failure Count") or "0")
        if not count or failures:
            raise ValueError(f"Locust returned {count} requests and {failures} failures.")
        return (f"Locust: {count} requests, {failures} failures, {total.get('Requests/s', '—')} req/s, "
                f"median {total.get('Median Response Time', '—')} ms, p95 {total.get('95%', '—')} ms.")

    def run(self, key, *, output=None, cancel=None, build=True, blocked=None):
        if key not in CHECKS:
            raise ValueError(f"Unknown check: {key}")
        fingerprint = self.fingerprint()
        start = monotonic()
        self.prepare_state_folder()
        directory = self.state / "logs"
        directory.mkdir(parents=True, exist_ok=True)
        identifier = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
        prefix = directory / f"{identifier}-{key}"
        streamed = False

        def emit(content):
            nonlocal streamed
            streamed = True
            output(content)

        try:
            if blocked:
                status, detail = "Blocked", blocked
            elif cancel is not None and cancel.is_set():
                status, detail = "Cancelled", "Run cancelled."
            else:
                detail = self.execute(key, output=emit if output else None, cancel=cancel, build=build,
                                      artifact_prefix=prefix)
                status = "Passed"
                if fingerprint != self.fingerprint():
                    status = "Stale"
                    detail = "Project files changed during the check. Rerun for the current revision.\n" + detail
        except RunCancelled as error:
            status, detail = "Cancelled", str(error)
        except subprocess.TimeoutExpired as error:
            status, detail = "Blocked", f"{error}\n{error.output or ''}"
        except FileNotFoundError as error:
            status, detail = "Blocked", str(error)
        except (OSError, RuntimeError, ValueError) as error:
            status, detail = "Failed", str(error)
        path = prefix.with_suffix(".log")
        atomic_text(path, (detail + "\n") if detail else "")
        record = {"check": key, "status": status, "when": stamp(), "fingerprint": fingerprint,
                  "seconds": round(monotonic() - start, 2), "log": path.relative_to(self.root).as_posix(),
                  "artifacts": [file.relative_to(self.root).as_posix()
                                for file in sorted(directory.glob(prefix.name + "_*.csv"))]}
        with self.edit_state():
            self.data["checks"][key] = record
            self.data["history"].append(record)
        if output and detail and (not streamed or status != "Passed"):
            output((detail if not streamed else detail.splitlines()[0]) + "\n")
        return status, detail

    def run_plan(self, checks, *, cancel=None, output=None, on_start=None):
        self.prepare_state_folder()
        try:
            with file_lock(self.state / "run.lock", wait=False):
                results = {}
                for key in checks:
                    if cancel is not None and cancel.is_set():
                        break
                    if on_start:
                        on_start(key)
                    blocked = [CHECKS[item] for item in DEPENDENCIES.get(key, ())
                               if item in results and results[item] != "Passed"]
                    reason = "Waiting for: " + ", ".join(blocked) if blocked else None
                    status, detail = self.run(key, output=output, cancel=cancel, blocked=reason,
                                              build=results.get("docker_build") != "Passed")
                    results[key] = status
                    yield key, status, detail
                    if status == "Cancelled":
                        break
        except BlockingIOError as error:
            raise ValueError("A check run is already active in this workspace.") from error


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _secret_opener(path, flags):
    return os.open(path, flags, 0o600)
