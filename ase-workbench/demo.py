"""Reference Flask service image used in the generated local lab."""

import hmac
import math
import os
import re
from pathlib import Path

import jwt
import requests
from flask import Flask, jsonify, request
from pymongo import MongoClient
from pymongo.errors import PyMongoError

app = Flask(__name__)
ROLE = os.getenv("ROLE", "calc")
BACKENDS = {"calc": "http://calc:5000", "string": "http://string:5000"}
WORD = re.compile(r"[A-Za-z0-9]{1,64}")


def read_secret(name):
    return (Path("/run/secrets") / name).read_text(encoding="utf-8").strip()


def record(category, operation):
    url = os.getenv("DB_MANAGER_URL")
    if url:
        response = requests.post(url + "/notify", json={"category": category, "op": operation}, timeout=3)
        response.raise_for_status()


def events():
    return MongoClient(os.getenv("MONGO_URL", "mongodb://mongo:27017"), serverSelectionTimeoutMS=2000).lab.events


@app.errorhandler(requests.RequestException)
@app.errorhandler(PyMongoError)
def dependency_error(_error):
    return jsonify(error="Dependency unavailable"), 503


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/add")
@app.get("/sub")
@app.get("/mul")
@app.get("/div")
@app.get("/mod")
def arithmetic():
    if ROLE != "calc":
        return jsonify(error="Unknown operation"), 404
    op = request.path[1:]
    try:
        a, b = (float(request.args[name]) for name in ("a", "b"))
        if not (math.isfinite(a) and math.isfinite(b)):
            raise ValueError
        if op in {"div", "mod"} and b == 0:
            raise ValueError
        result = {"add": lambda: a+b, "sub": lambda: a-b, "mul": lambda: a*b,
                  "div": lambda: a/b, "mod": lambda: a%b}[op]()
        if not math.isfinite(result):
            raise ValueError
    except (KeyError, ValueError, OverflowError):
        return jsonify(error="Invalid operands"), 400
    record("calc", op)
    return jsonify(s=result)


@app.get("/upper")
@app.get("/lower")
@app.get("/concat")
def text_operation():
    if ROLE != "string":
        return jsonify(error="Unknown operation"), 404
    op = request.path[1:]
    a, b = (request.args.get(name, "") for name in ("a", "b"))
    operations = {"upper": lambda: a.upper(), "lower": lambda: a.lower(), "concat": lambda: a+b}
    if not WORD.fullmatch(a) or (op == "concat" and not WORD.fullmatch(b)):
        return jsonify(error="Invalid text"), 400
    record("string", op)
    return jsonify(s=operations[op]())


@app.post("/notify")
def notify():
    if ROLE != "db-manager":
        return jsonify(error="Unknown operation"), 404
    data = request.get_json(silent=True)
    if (not isinstance(data, dict) or data.get("category") not in ("calc", "string")
            or not isinstance(data.get("op"), str) or not WORD.fullmatch(data["op"])):
        return jsonify(error="Invalid event"), 400
    events().insert_one({"category": data["category"], "op": data["op"]})
    return jsonify(status="recorded"), 201


@app.post("/login")
def login():
    if ROLE != "gateway" or os.getenv("SECURE") != "1":
        return jsonify(error="Secure demo unavailable"), 404
    from datetime import datetime, timedelta, timezone
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get("password"), str):
        return jsonify(error="Invalid credentials"), 401
    user = data.get("username")
    if user not in ("math", "text") or not hmac.compare_digest(
            data["password"].encode(), read_secret("password_" + user).encode()):
        return jsonify(error="Invalid credentials"), 401
    now = datetime.now(timezone.utc)
    token = jwt.encode({"sub": user, "iss": "ase-lab", "aud": "ase-gateway", "iat": now,
                        "exp": now + timedelta(minutes=10), "scope": "calc" if user == "math" else "string"},
                       read_secret("jwt"), algorithm="HS256")
    return jsonify(access_token=token, token_type="Bearer", expires_in=600)


@app.get("/calc/<operation>")
@app.get("/str/<operation>")
def gateway(operation):
    if ROLE != "gateway":
        return jsonify(error="Unknown operation"), 404
    namespace = "calc" if request.path.startswith("/calc/") else "string"
    allowed = {"calc": {"add", "sub", "mul", "div", "mod"}, "string": {"upper", "lower", "concat"}}
    if operation not in allowed[namespace]:
        return jsonify(error="Unknown operation"), 404
    if os.getenv("SECURE") == "1":
        scheme, _, token = request.headers.get("Authorization", "").partition(" ")
        if scheme.lower() != "bearer" or not token:
            return jsonify(error="Bearer token required"), 401
        try:
            claims = jwt.decode(token, read_secret("jwt"), algorithms=["HS256"], audience="ase-gateway",
                                issuer="ase-lab", options={"require": ["exp", "iss", "aud", "sub", "scope"]})
        except jwt.InvalidTokenError:
            return jsonify(error="Invalid token"), 401
        if claims["scope"] != namespace:
            return jsonify(error="Insufficient scope"), 403
    response = requests.get(BACKENDS[namespace] + "/" + operation,
                            params=list(request.args.items(multi=True)), timeout=5)
    return jsonify(response.json()), response.status_code
