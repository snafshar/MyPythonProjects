"""Build a reproducible ASE reference project in a new or existing workspace."""

import json
from pathlib import Path

SOURCE = Path(__file__).resolve().parent

REQUIREMENTS = """Flask>=3.1,<4
requests>=2.32,<3
PyJWT>=2.10,<3
pymongo>=4.9,<5
"""

DOCKERFILE = """FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
USER 65534:65534
EXPOSE 5000
CMD ["python", "-m", "flask", "--app", "app", "run", "--host=0.0.0.0", "--port=5000"]
"""

WORKFLOW = """name: ASE reference project
on: [push, pull_request]
permissions:
  contents: read
jobs:
  isolated:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [calc, string]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: python -m pip install -r requirements.txt pytest
      - run: python -m pytest -q tests/test_service.py -k ${{ matrix.service }}
  integration:
    needs: isolated
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - run: npm install --global newman@6
      - run: docker compose -f compose.json up --build -d --wait --wait-timeout 90
      - run: newman run tests/gateway.postman_collection.json
      - if: failure()
        run: docker compose -f compose.json logs --no-color
      - if: always()
        run: docker compose -f compose.json down
"""

TESTS = """from unittest.mock import patch

import pytest
import app


@pytest.fixture
def client():
    return app.app.test_client()


@pytest.mark.parametrize("query,status,result", [
    ("a=0&b=9", 200, 9),
    ("a=9&b=0", 200, 9),
    ("b=9", 400, None),
    ("a=NaN&b=9", 400, None),
    ("a=hello&b=9", 400, None),
])
def test_calc(client, query, status, result):
    with patch.object(app, "ROLE", "calc"), patch.object(app, "record") as record:
        response = client.get("/add?" + query)
        assert response.status_code == status
        if status == 200:
            assert response.json == {"s": result}
            record.assert_called_once_with("calc", "add")
        else:
            record.assert_not_called()


@pytest.mark.parametrize("query,status,result", [
    ("a=AbC", 200, "abc"), ("a=abc!", 400, None), ("", 400, None),
])
def test_string(client, query, status, result):
    with patch.object(app, "ROLE", "string"), patch.object(app, "record") as record:
        response = client.get("/lower?" + query)
        assert response.status_code == status
        if status == 200:
            assert response.json == {"s": result}
            record.assert_called_once_with("string", "lower")
        else:
            record.assert_not_called()
"""

LOCUST = """from locust import HttpUser, between, task


class GatewayUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task
    def add(self):
        self.client.get("/calc/add?a=0&b=9", name="/calc/add")

    @task
    def lower(self):
        self.client.get("/str/lower?a=ASE", name="/str/lower")
"""


def compose_model(port, secure=False):
    health = {"test": ["CMD", "python", "-c",
                       "import socket; socket.create_connection(('127.0.0.1', 5000), 2).close()"],
              "interval": "2s", "timeout": "3s", "retries": 20}
    services = {}
    for role in ("gateway", "calc", "string", "db-manager"):
        services[role] = {"build": ".", "environment": {"ROLE": role}, "healthcheck": health}
    services["mongo"] = {
        "image": "mongo:7", "volumes": ["mongo-data:/data/db"],
        "healthcheck": {"test": ["CMD", "mongosh", "--quiet", "--eval", "db.adminCommand({ping:1})"],
                        "interval": "2s", "timeout": "3s", "retries": 25},
    }

    def depends(role, *targets):
        services[role]["depends_on"] = {target: {"condition": "service_healthy"} for target in targets}

    depends("db-manager", "mongo")
    for role in ("calc", "string"):
        services[role]["environment"]["DB_MANAGER_URL"] = "http://db-manager:5000"
        depends(role, "db-manager")
    depends("gateway", "calc", "string")
    gateway = services["gateway"]
    gateway["ports"] = [f"127.0.0.1:{port}:5000"]
    model = {"services": services, "volumes": {"mongo-data": {}}}
    if secure:
        names = ("cert", "key", "jwt", "password_math", "password_text")
        gateway["secrets"] = list(names)
        model["secrets"] = {name: {"file": f"./.ase-secrets/{name}"} for name in names}
        gateway["environment"]["SECURE"] = "1"
        # Compose file-based secrets preserve local owner and file mode.
        gateway["user"] = "${ASE_UID:-1000}:${ASE_GID:-1000}"
        gateway["command"] = ["python", "-m", "flask", "--app", "app", "run", "--host=0.0.0.0",
                              "--port=5000", "--cert=/run/secrets/cert", "--key=/run/secrets/key"]
    return model


def api_contract(port):
    paths = {}
    for group, operations in {"calc": ["add", "sub", "mul", "div", "mod"],
                              "str": ["upper", "lower", "concat"]}.items():
        for op in operations:
            inputs = ("a", "b") if group == "calc" or op == "concat" else ("a",)
            value_type = "number" if group == "calc" else "string"
            responses = {"200": {"description": "Operation result", "content": {"application/json": {
                "schema": {"type": "object", "required": ["s"], "properties": {"s": {"type": value_type}}}}}},
                "400": {"description": "Invalid input"}, "503": {"description": "Dependency unavailable"}}
            paths[f"/{group}/{op}"] = {"get": {
                "operationId": f"{group}_{op}",
                "parameters": [{"name": name, "in": "query", "required": True, "schema": {"type": value_type}}
                               for name in inputs], "responses": responses}}
    return {"openapi": "3.0.3", "info": {"title": "ASE reference gateway", "version": "1.0.0"},
            "servers": [{"url": f"http://127.0.0.1:{port}"}], "paths": paths}


def postman_collection(port):
    items = []
    for path, status, expected in [
        ("/calc/add?a=0&b=9", 200, 9),
        ("/calc/add?a=9&b=0", 200, 9),
        ("/calc/add?b=9", 400, "Invalid operands"),
        ("/calc/mod?a=8&b=3", 200, 2),
        ("/str/lower?a=ASE", 200, "ase"),
        ("/str/concat?a=A&b=B", 200, "AB"),
        ("/str/lower", 400, "Invalid text"),
    ]:
        key = "s" if status == 200 else "error"
        items.append({"name": path, "request": {"method": "GET", "url": "{{baseUrl}}" + path},
                      "event": [{"listen": "test", "script": {"exec": [
                          f"pm.test('status', () => pm.response.to.have.status({status}));",
                          f"pm.test('body', () => pm.expect(pm.response.json().{key}).to.eql({json.dumps(expected)}));"
                      ]}}]})
    return {"info": {"name": "ASE Gateway",
                     "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},
            "variable": [{"key": "baseUrl", "value": f"http://127.0.0.1:{port}"}], "item": items}


def generate(root, port=8500):
    files = {
        "app.py": (SOURCE / "demo.py").read_text(encoding="utf-8"),
        "requirements.txt": REQUIREMENTS,
        "requirements-dev.txt": "-r requirements.txt\npytest>=8,<10\nlocust>=2,<3\nbandit>=1.7,<2\n"
                                "pip-audit>=2.7,<3\nopenapi-spec-validator>=0.7,<0.9\n",
        "Dockerfile": DOCKERFILE,
        "compose.json": compose_model(port),
        "compose.secure.json": compose_model(port + 1, secure=True),
        "openapi.json": api_contract(port),
        "tests/test_service.py": TESTS,
        "tests/gateway.postman_collection.json": postman_collection(port),
        "locustfile.py": LOCUST,
        ".github/workflows/ase.yml": WORKFLOW,
        ".gitignore": ".ase-*\n.venv/\n__pycache__/\n.pytest_cache/\n*.pyc\n.env\n",
        ".dockerignore": ".git\n.ase-*\n.venv\n__pycache__\n.env\n",
        "README.md": "# Generated ASE reference project\n\n"
                     "Run from this folder. The normal stack publishes only the loopback gateway.\n\n"
                     "- Start: `docker compose -f compose.json up -d --build --wait`\n"
                     "- Test: `newman run tests/gateway.postman_collection.json`\n"
                     "- Stop: `docker compose -f compose.json down`\n\n"
                     "The HTTPS/JWT profile is a local teaching demo. Internal calls and MongoDB are local Compose services.\n",
    }
    created, kept = [], []
    for relative, value in files.items():
        dest = root / relative
        if not dest.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"Path leaves workspace: {relative}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            with dest.open("x", encoding="utf-8") as handle:
                handle.write(value if isinstance(value, str) else json.dumps(value, indent=2) + "\n")
            created.append(relative)
        except FileExistsError:
            kept.append(relative)
    return created, kept
