"""Workflow execution, local probes and persisted evidence."""

import hashlib
import json
import os
import secrets
import shutil
import ssl
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, HTTPSHandler, ProxyHandler, Request, build_opener

from scaffold import generate
from stages import STAGES

PORT = 8500
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
BASELINE = ("contract", "compose_config", "docker_build", "compose_up", "smoke", "unit", "newman")
SECURE = ("cert", "secure_up", "tls", "access")
SCANS = ("bandit", "audit", "trivy")
FULL_RUN = BASELINE + ("load",) + SECURE + SCANS + ("logs",)


def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def atomic_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(content)
    Path(handle.name).replace(path)


class Workspace:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.state = self.root / ".ase-workbench"
        self.state_path = self.state / "workspace.json"
        self.project = "ase-" + hashlib.sha256(os.fsencode(self.root)).hexdigest()[:10]
        self.data = {"notes": {}, "reviews": {}, "checks": {}}
        if self.state_path.exists():
            loaded = json.loads(self.state_path.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict) or any(not isinstance(loaded.get(k), dict) for k in self.data):
                raise ValueError("Unrecognized workspace state")
            self.data = loaded

    def save(self):
        atomic_text(self.state_path, json.dumps(self.data, indent=2) + "\n")

    def scaffold(self):
        return generate(self.root, PORT)

    def fingerprint(self):
        digest = hashlib.sha256()
        for name in ("app.py", "openapi.json", "Dockerfile", "compose.json", "compose.secure.json",
                     "requirements.txt", "requirements-dev.txt", "locustfile.py", ".github/workflows/ase.yml"):
            file = self.root / name
            if file.is_file():
                digest.update(name.encode() + b"\0" + file.read_bytes())
        for file in sorted((self.root / "tests").glob("*")):
            if file.is_file():
                digest.update(file.name.encode() + b"\0" + file.read_bytes())
        return digest.hexdigest()

    def result(self, key):
        item = self.data["checks"].get(key)
        if item and item["fingerprint"] != self.fingerprint():
            return "Stale"
        return item["status"] if item else "Pending"

    def review(self, key):
        if not self.data["notes"].get(key, "").strip():
            raise ValueError("Record the decision or evidence in the stage notes first.")
        if any(self.result(check) != "Passed" for check in STAGES[key].checks):
            raise ValueError("Pass the stage checks for the current project revision first.")
        if key == "delivery":
            required = ("vision", "stories", "architecture", "smells")
            waiting = [STAGES[stage].title for stage in required if self.status(stage) != "Reviewed"]
            waiting += [CHECKS[check] for check in FULL_RUN if self.result(check) != "Passed"]
            if waiting:
                raise ValueError("Complete the release evidence first.\n" + "\n".join(waiting))
        self.data["reviews"][key] = self.fingerprint()
        self.save()

    def status(self, key):
        stage = STAGES[key]
        if any(self.result(check) in {"Failed", "Blocked"} for check in stage.checks):
            return "Needs attention"
        if self.data["reviews"].get(key) == self.fingerprint():
            return "Reviewed"
        if stage.checks and all(self.result(check) == "Passed" for check in stage.checks):
            return "Verified"
        if self.data["notes"].get(key, "").strip():
            return "In progress"
        return "Pending"

    def report(self, destination):
        lines = ["# ASE workflow evidence", "", f"Generated {stamp()}", "",
                 f"Project fingerprint: `{self.fingerprint()}`", ""]
        for key, stage in STAGES.items():
            lines.extend([f"## {stage.title}", "", f"Status: **{self.status(key)}**", "",
                          f"Tools: {stage.tools}", f"Expected output: {stage.output}", "",
                          self.data["notes"].get(key, "").strip() or "No notes recorded.", ""])
            for check in stage.checks:
                result = self.data["checks"].get(check, {})
                detail = f" · {result['when']} · {result['log']}" if result else ""
                lines.append(f"- {CHECKS[check]}: {self.result(check)}{detail}")
            lines.append("")
        Path(destination).write_text("\n".join(lines), encoding="utf-8")

    def release_candidate(self):
        if self.status("delivery") != "Reviewed":
            raise ValueError("Review the release stage for this project revision first.")
        checks = {key: self.result(key) for key in FULL_RUN}
        if any(status != "Passed" for status in checks.values()):
            raise ValueError("The recorded checks must pass for this project revision.")
        fingerprint = self.fingerprint()
        release = self.state / "releases" / fingerprint[:16]
        release.mkdir(parents=True, exist_ok=True)
        manifest = {
            "kind": "local-release-candidate",
            "created_at": stamp(),
            "fingerprint": fingerprint,
            "checks": {key: self.data["checks"][key] for key in checks},
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

    def command(self, args, timeout=120, capture=False):
        if not shutil.which(os.fspath(args[0])):
            raise FileNotFoundError(f"Required tool is unavailable: {args[0]}")
        env = os.environ.copy()
        if hasattr(os, "getuid"):
            env.update(ASE_UID=str(os.getuid()), ASE_GID=str(os.getgid()))
        finished = subprocess.run(args, cwd=self.root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  text=True, errors="replace", timeout=timeout, env=env)
        if finished.returncode:
            raise RuntimeError(f"Exit {finished.returncode}\n{finished.stdout}")
        return finished.stdout.strip() if capture else finished.stdout or "Command completed."

    def http(self, path, *, secure=False, data=None, token=None):
        handlers = [ProxyHandler({})]
        scheme, port = "http", PORT
        if secure:
            scheme, port = "https", PORT + 1
            handlers.append(HTTPSHandler(context=ssl.create_default_context(
                cafile=str(self.root / ".ase-secrets/cert"))))
        headers = {}
        if data is not None:
            headers["Content-Type"] = "application/json"
        if token is not None:
            headers["Authorization"] = "Bearer " + token
        req = Request(f"{scheme}://127.0.0.1:{port}{path}",
                      data=json.dumps(data).encode() if data is not None else None, headers=headers)
        try:
            response = build_opener(*handlers, NoRedirect()).open(req, timeout=7)
        except HTTPError as error:
            response = error
        with response:
            return response.status, json.loads(response.read())

    def certificates(self):
        folder = self.root / ".ase-secrets"
        folder.mkdir(mode=0o700, exist_ok=True)
        if folder.is_symlink():
            raise ValueError("The secrets directory must be local to this workspace.")
        if not all((folder / name).is_file() for name in ("cert", "key")):
            with tempfile.TemporaryDirectory(dir=folder) as temp:
                cert, key = (Path(temp) / name for name in ("cert", "key"))
                self.command(("openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "30",
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
        self.command(("openssl", "x509", "-in", str(folder / "cert"), "-checkend", "0", "-noout"))
        return "Development TLS certificate and local secret files are ready."

    def access(self):
        def probe(token, expected):
            code, body = self.http("/calc/add?a=0&b=9", secure=True, token=token)
            if code != expected or (code == 200 and body != {"s": 9}):
                raise RuntimeError(f"Expected HTTP {expected}; received HTTP {code}.")

        probe(None, 401)
        probe("invalid-token", 401)
        for user, expected in (("math", 200), ("text", 403)):
            password = (self.root / ".ase-secrets" / ("password_" + user)).read_text().strip()
            code, body = self.http("/login", secure=True, data={"username": user, "password": password})
            if code != 200 or not body.get("access_token"):
                raise RuntimeError(f"Expected successful login for lab user {user}; received HTTP {code}.")
            probe(body["access_token"], expected)
        return "Passed: missing 401, invalid 401, authorized zero input 200, insufficient scope 403."

    def execute(self, key):
        if key not in CHECKS:
            raise ValueError(f"Unknown check: {key}")
        py = str(self.python)
        commands = {
            "contract": (py, "-m", "openapi_spec_validator", "openapi.json"),
            "compose_config": self.compose("config", "--quiet"),
            "docker_build": self.compose("build"),
            "compose_up": self.compose("up", "-d", "--build", "--wait", "--wait-timeout", "90"),
            "unit": (py, "-m", "pytest", "-q", "tests/test_service.py"),
            "newman": ("newman", "run", "tests/gateway.postman_collection.json",
                       "--env-var", f"baseUrl=http://127.0.0.1:{PORT}"),
            "load": (py, "-m", "locust", "-f", "locustfile.py", "--headless", "-u", "5", "-r", "2",
                     "-t", "15s", "--host", f"http://127.0.0.1:{PORT}", "--csv", ".ase-workbench/load"),
            "secure_up": self.compose("up", "-d", "--build", "--wait", "--wait-timeout", "90", secure=True),
            "bandit": (py, "-m", "bandit", "app.py"),
            "audit": (py, "-m", "pip_audit", "-r", "requirements.txt"),
            "logs": self.compose("logs", "--no-color", "--tail", "100"),
        }
        if key in commands:
            return self.command(commands[key], timeout=600)
        if key == "setup":
            self.command((sys.executable, "-m", "venv", ".venv"), timeout=180)
            return self.command((py, "-m", "pip", "install", "-r", "requirements-dev.txt"), timeout=600)
        if key == "cert":
            return self.certificates()
        if key == "access":
            return self.access()
        if key == "trivy":
            image = self.command(self.compose("images", "-q", "gateway"), capture=True)
            if not image or len(image.splitlines()) != 1:
                raise RuntimeError("Start the normal Compose stack before scanning its gateway image.")
            return self.command(("trivy", "image", "--severity", "HIGH,CRITICAL", "--ignore-unfixed",
                                 "--exit-code", "1", image), timeout=600)
        if key == "down":
            normal = self.command(self.compose("down"))
            return normal + "\n" + self.command(self.compose("down", secure=True))
        cases = [("/health", {"status": "ok"})] if key == "tls" else [
            ("/calc/add?a=0&b=9", {"s": 9}), ("/str/lower?a=ASE", {"s": "ase"})]
        for path, expected in cases:
            code, body = self.http(path, secure=key == "tls")
            if (code, body) != (200, expected):
                raise RuntimeError(f"{path}: expected 200 and {expected}; received {code} and {body}.")
        return "\n".join(f"{path} → HTTP 200 {body}" for path, body in cases)

    def run(self, key):
        fingerprint = self.fingerprint()
        try:
            output = self.execute(key)
            status = "Passed"
        except (FileNotFoundError, subprocess.TimeoutExpired) as error:
            status, output = "Blocked", str(error)
        except (OSError, RuntimeError, ValueError) as error:
            status, output = "Failed", str(error)
        directory = self.state / "logs"
        directory.mkdir(parents=True, exist_ok=True)
        identifier = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
        path = directory / f"{identifier}-{key}.log"
        atomic_text(path, output + "\n")
        self.data["checks"][key] = {"status": status, "when": stamp(), "fingerprint": fingerprint,
                                    "log": str(path.relative_to(self.root))}
        self.save()
        return status, output


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _secret_opener(path, flags):
    return os.open(path, flags, 0o600)
