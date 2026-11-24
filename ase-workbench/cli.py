"""Terminal entry point using the same workspaces and checks as the desktop app."""

import argparse
import signal
import sys
from pathlib import Path
from threading import Event

from engine import CHECKS, PROFILES, Workspace
from execution import RunCancelled
from stages import STAGES


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.cwd(), help="Project directory")
    actions = parser.add_subparsers(dest="action", required=True)

    scaffold = actions.add_parser("scaffold", help="Create the reference project")
    scaffold.add_argument("--http-port", type=int, help="HTTP gateway port (default 8500)")
    scaffold.add_argument("--https-port", type=int, help="HTTPS gateway port (default HTTP + 1)")

    actions.add_parser("doctor", help="Check tool availability and Docker connectivity")
    actions.add_parser("install", help="Install the workspace Python dependencies")
    actions.add_parser("status", help="Show the current status of each workflow stage")
    actions.add_parser("stop", help="Stop the two Compose stacks")
    run = actions.add_parser("run", help="Run a check profile")
    run.add_argument("profile", choices=PROFILES)
    check = actions.add_parser("check", help="Run individual checks in the order supplied")
    check.add_argument("checks", choices=CHECKS, nargs="+")
    report = actions.add_parser("report", help="Export a Markdown evidence report")
    report.add_argument("destination", type=Path)
    return parser.parse_args(argv)


def run_checks(workspace, checks, cancel):
    def start(key):
        print(f"\n▶ {CHECKS[key]}", flush=True)

    def write(text):
        print(text, end="", flush=True)

    results = []
    for key, status, _ in workspace.run_plan(checks, cancel=cancel, output=write, on_start=start):
        print(f"\n{status} · {CHECKS[key]}", flush=True)
        results.append(status)
    passed = results.count("Passed")
    print(f"\n{passed}/{len(checks)} checks passed.")
    if cancel.is_set():
        return 130
    return int(passed != len(checks))


def main(argv=None):
    args = parse_args(argv)
    cancel = Event()
    previous_handler = signal.signal(signal.SIGINT, lambda *_: cancel.set())
    try:
        workspace = Workspace(args.workspace)
        if args.action == "scaffold":
            created, kept = workspace.scaffold(args.http_port, args.https_port)
            print(f"{len(created)} created, {len(kept)} kept.")
            print(f"HTTP  {workspace.endpoint()}")
            print(f"HTTPS {workspace.endpoint(secure=True)}")
            return 0
        if not workspace.root.is_dir():
            raise ValueError(f"Workspace folder does not exist: {workspace.root}")
        if args.action == "doctor":
            readiness = []
            for name, ready, details in workspace.doctor(cancel=cancel):
                print(f"{'Ready' if ready else 'Unavailable':11} {name}: {details}", flush=True)
                readiness.append(ready)
            return int(not all(readiness))
        if args.action == "status":
            revision = workspace.fingerprint()
            for key, stage in STAGES.items():
                print(f"{workspace.status(key, revision):16} {stage.title}")
            return 0
        if args.action == "report":
            workspace.report(args.destination)
            print(args.destination.resolve())
            return 0
        if args.action == "install":
            checks = ("setup",)
        elif args.action == "stop":
            checks = ("down",)
        elif args.action == "check":
            checks = tuple(dict.fromkeys(args.checks))
        else:
            checks = PROFILES[args.profile]
        if checks != ("down",) and not (workspace.root / "compose.json").is_file():
            raise ValueError("Scaffold the project first.")
        return run_checks(workspace, checks, cancel)
    except RunCancelled:
        print("Run cancelled.", file=sys.stderr)
        return 130
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    finally:
        signal.signal(signal.SIGINT, previous_handler)


if __name__ == "__main__":
    sys.exit(main())
