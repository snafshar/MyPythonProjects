"""Terminal entry point using the same workspaces and checks as the desktop app."""

import argparse
import json
import signal
import sys
from pathlib import Path
from threading import Event

from engine import CHECKS, DEPENDENCIES, PROFILES, Workspace
from execution import RunCancelled
from stages import NOTE_TEMPLATES, STAGES


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.cwd(), help="Project directory")
    actions = parser.add_subparsers(dest="action", required=True)

    scaffold = actions.add_parser("scaffold", help="Create the reference project")
    scaffold.add_argument("--http-port", type=int, help="HTTP gateway port (default 8500)")
    scaffold.add_argument("--https-port", type=int, help="HTTPS gateway port (default HTTP + 1)")

    actions.add_parser("doctor", help="Check tool availability and Docker connectivity")
    actions.add_parser("install", help="Install the workspace Python dependencies")
    status = actions.add_parser("status", help="Show workflow stage status")
    status.add_argument("--json", action="store_true", help="Print machine-readable status")
    actions.add_parser("stop", help="Stop the two Compose stacks")
    run = actions.add_parser("run", help="Run a check profile")
    run.add_argument("profile", choices=PROFILES)
    check = actions.add_parser("check", help="Run individual checks in the order supplied")
    check.add_argument("checks", choices=CHECKS, nargs="+")
    report = actions.add_parser("report", help="Export a Markdown evidence report")
    report.add_argument("destination", type=Path)
    note = actions.add_parser("note", help="Save a stage note from a Markdown or text file")
    note.add_argument("stage", choices=STAGES)
    note.add_argument("source", type=Path)
    review = actions.add_parser("review", help="Mark a stage reviewed using the usual evidence checks")
    review.add_argument("stage", choices=STAGES)
    actions.add_parser("candidate", help="Record a local release candidate")
    history = actions.add_parser("history", help="List recorded checks and their log paths")
    history.add_argument("--check", choices=CHECKS)
    history.add_argument("--limit", type=int, help="Maximum number of matching results")
    history.add_argument("--json", action="store_true", help="Print machine-readable history")
    actions.add_parser("stages", help="List stage identifiers and titles")
    actions.add_parser("checks", help="List check identifiers and labels")
    stage = actions.add_parser("stage", help="Show a stage's tools, expected output and checks")
    stage.add_argument("stage", choices=STAGES)
    plan = actions.add_parser("plan", help="Preview a profile and its dependencies")
    plan.add_argument("profile", choices=PROFILES)
    prompts = actions.add_parser("prompts", help="Print a Markdown note template")
    prompts.add_argument("stage", choices=STAGES)
    show_note = actions.add_parser("show-note", help="Read the saved stage note")
    show_note.add_argument("stage", choices=STAGES)
    log = actions.add_parser("log", help="Print the latest log for a check")
    log.add_argument("check", choices=CHECKS)
    actions.add_parser("readiness", help="List outstanding release requirements and exit 1 if any remain")
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


def describe(args):
    if args.action in {"stages", "checks"}:
        items = {key: stage.title for key, stage in STAGES.items()} if args.action == "stages" else CHECKS
        for key, label in items.items():
            print(f"{key:16} {label}")
    elif args.action == "stage":
        stage = STAGES[args.stage]
        print(f"{stage.title}\n\nTools: {stage.tools}\n\n{stage.action}\n\nExpected output: {stage.output}")
        for check in stage.checks:
            print(f"- {check}: {CHECKS[check]}")
    elif args.action == "plan":
        selected = PROFILES[args.profile]
        for number, check in enumerate(selected, 1):
            dependencies = [item for item in DEPENDENCIES.get(check, ()) if item in selected[:number - 1]]
            suffix = f" (after {', '.join(dependencies)})" if dependencies else ""
            print(f"{number:2}. {check}: {CHECKS[check]}{suffix}")
    else:
        for heading in NOTE_TEMPLATES.get(args.stage, ("Decision", "Evidence", "Follow-up")):
            print(f"## {heading}\n")


def main(argv=None):
    args = parse_args(argv)
    if args.action in {"stages", "checks", "stage", "plan", "prompts"}:
        describe(args)
        return 0
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
            statuses = {key: workspace.status(key, revision) for key in STAGES}
            if args.json:
                print(json.dumps(statuses, indent=2))
            else:
                for key, status in statuses.items():
                    print(f"{status:16} {STAGES[key].title}")
            return 0
        if args.action == "note":
            workspace.set_note(args.stage, args.source.read_text(encoding="utf-8"))
            print(f"Saved notes for {STAGES[args.stage].title}")
            return 0
        if args.action == "review":
            workspace.review(args.stage)
            print(f"Reviewed {STAGES[args.stage].title}")
            return 0
        if args.action == "candidate":
            print(workspace.release_candidate())
            return 0
        if args.action == "show-note":
            print(workspace.data["notes"].get(args.stage, ""), end="")
            return 0
        if args.action == "log":
            entry = workspace.data["checks"].get(args.check)
            if not entry:
                raise ValueError(f"No log recorded for {args.check}.")
            path = (workspace.root / entry["log"]).resolve()
            if not path.is_relative_to(workspace.root) or not path.is_relative_to(workspace.state.resolve()):
                raise ValueError("Log path is outside the workspace evidence folder.")
            print(path.read_text(encoding="utf-8"), end="")
            return 0
        if args.action == "readiness":
            revision = workspace.fingerprint()
            outstanding = workspace.release_waiting(revision)
            if not outstanding and workspace.status("delivery", revision) != "Reviewed":
                outstanding = ["Review the delivery stage."]
            print("\n".join(outstanding) if outstanding else "Ready to record a local release candidate.")
            return int(bool(outstanding))
        if args.action == "history":
            if args.limit is not None and args.limit < 0:
                raise ValueError("History limit must be nonnegative.")
            entries = [entry for entry in reversed(workspace.data["history"])
                       if args.check is None or entry["check"] == args.check][:args.limit]
            if args.json:
                print(json.dumps(entries, indent=2))
            else:
                for entry in entries:
                    label = CHECKS.get(entry["check"], entry["check"])
                    print(f"{entry['when']}  {entry['status']:10}  {label}  {entry['log']}")
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
