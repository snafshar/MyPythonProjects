"""Five small educational servers. Python 3.10+, no dependencies."""
import argparse
import json
import os
import socketserver
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
from urllib.request import urlopen

ROOT = Path(__file__).parent
FILES = ROOT / "received_files"
MAIL = ROOT / "received_mail"
TOKEN = os.environ.get("SERVER_TOKEN", "change-me")
MAX_FILE = 10 * 1024 * 1024
COUNTS = dict.fromkeys(("file", "api", "proxy", "monitor", "mail"), 0)
LOCK = threading.Lock()


def tick(service):
    with LOCK:
        COUNTS[service] += 1


def safe_filename(url):
    name = unquote(urlsplit(url).path.removeprefix("/files/"))
    if not name or name in (".", "..") or "/" in name or "\\" in name or "\x00" in name:
        return None
    return name


class Handler(BaseHTTPRequestHandler):
    service = ""

    def reply(self, status, data, content_type="application/json"):
        if isinstance(data, dict):
            data = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def authorized(self):
        return self.headers.get("X-Token") == TOKEN

    def do_GET(self):
        tick(self.service)
        self.get()

    def do_POST(self):
        tick(self.service)
        self.post()

    def get(self):
        self.reply(404, {"error": "Not found"})

    def post(self):
        self.reply(405, {"error": "Method not allowed"})


class FileServer(Handler):
    service = "file"

    def get(self):
        if not self.authorized():
            return self.reply(403, {"error": "Invalid token"})
        name = safe_filename(self.path)
        if name is None:
            return self.reply(400, {"error": "Use /files/<filename>"})
        path = FILES / name
        if not path.is_file():
            return self.reply(404, {"error": "File not found"})
        self.reply(200, path.read_bytes(), "application/octet-stream")

    def post(self):
        if not self.authorized():
            return self.reply(403, {"error": "Invalid token"})
        name = safe_filename(self.path)
        try:
            size = int(self.headers.get("Content-Length", "-1"))
        except ValueError:
            size = -1
        if name is None or not 0 <= size <= MAX_FILE:
            return self.reply(400, {"error": "Invalid filename or size (max 10 MB)"})
        data = self.rfile.read(size)
        if len(data) != size:
            return self.reply(400, {"error": "Incomplete upload"})
        FILES.mkdir(exist_ok=True)
        (FILES / name).write_bytes(data)
        self.reply(201, {"saved": name, "bytes": size})


class APIServer(Handler):
    service = "api"

    def get(self):
        if urlsplit(self.path).path == "/api/hello":
            self.reply(200, {"message": "Hello from the API!"})
        else:
            self.reply(404, {"error": "Try /api/hello"})


class ProxyServer(Handler):
    service = "proxy"

    def get(self):
        # Deliberately a fixed reverse proxy, never an open proxy.
        if urlsplit(self.path).path != "/api/hello":
            return self.reply(404, {"error": "Only /api/hello is proxied"})
        try:
            with urlopen("http://127.0.0.1:8002/api/hello", timeout=3) as upstream:
                self.reply(upstream.status, upstream.read(1024 * 1024))
        except OSError:
            self.reply(502, {"error": "API upstream unavailable"})


class MonitoringServer(Handler):
    service = "monitor"

    def get(self):
        if urlsplit(self.path).path != "/metrics":
            return self.reply(404, {"error": "Try /metrics"})
        if not self.authorized():
            return self.reply(403, {"error": "Invalid token"})
        with LOCK:
            snapshot = COUNTS.copy()
        self.reply(200, {"requests_by_service": snapshot})


class MailServer(socketserver.StreamRequestHandler):
    """Minimal SMTP test inbox; no sending or relaying."""
    def handle(self):
        self.wfile.write(b"220 localhost Demo SMTP inbox\r\n")
        sender = recipient = None
        while True:
            line = self.rfile.readline(4096)
            if not line:
                return
            command = line.decode("utf-8", errors="replace").strip()
            upper = command.upper()
            if upper.startswith(("HELO ", "EHLO ")):
                self.wfile.write(b"250 localhost\r\n")
            elif upper.startswith("MAIL FROM:"):
                sender = command[10:].strip()
                recipient = None
                self.wfile.write(b"250 OK\r\n")
            elif upper.startswith("RCPT TO:") and sender is not None:
                recipient = command[8:].strip()
                self.wfile.write(b"250 OK\r\n")
            elif upper == "DATA" and sender is not None and recipient is not None:
                self.wfile.write(b"354 End with a dot line\r\n")
                lines, total = [], 0
                while True:
                    part = self.rfile.readline(4096)
                    if not part:
                        return
                    if part in (b".\r\n", b".\n"):
                        break
                    if part.startswith(b".."):
                        part = part[1:]
                    total += len(part)
                    if total <= 1024 * 1024:
                        lines.append(part)
                if total > 1024 * 1024:
                    self.wfile.write(b"552 Message too large\r\n")
                else:
                    MAIL.mkdir(exist_ok=True)
                    (MAIL / f"{uuid.uuid4().hex}.eml").write_bytes(b"".join(lines))
                    tick("mail")
                    self.wfile.write(b"250 Saved locally (not delivered)\r\n")
                sender = recipient = None
            elif upper == "RSET":
                sender = recipient = None
                self.wfile.write(b"250 OK\r\n")
            elif upper == "NOOP":
                self.wfile.write(b"250 OK\r\n")
            elif upper == "QUIT":
                self.wfile.write(b"221 Bye\r\n")
                return
            else:
                self.wfile.write(b"502 Command not supported\r\n")


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    parser = argparse.ArgumentParser(description="Educational server framework")
    parser.add_argument("--host", default="127.0.0.1",
                        help="Use 0.0.0.0 to open file and proxy on LAN")
    host = parser.parse_args().host
    servers = []
    try:
        for name, port, handler in [
            ("file", 8001, FileServer),
            ("api", 8002, APIServer),
            ("proxy", 8003, ProxyServer),
            ("monitor", 8004, MonitoringServer),
        ]:
            bind = host if name in ("file", "proxy") else "127.0.0.1"
            server = ThreadingHTTPServer((bind, port), handler)
            servers.append(server)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            print(f"{name}: http://{bind}:{port}")
        smtp = ThreadedTCPServer(("127.0.0.1", 1025), MailServer)
        servers.append(smtp)
        threading.Thread(target=smtp.serve_forever, daemon=True).start()
        print("mail: smtp://127.0.0.1:1025 (local inbox)")
        print("Ctrl+C to stop")
        threading.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        for server in servers:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    main()
