import json
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event
from unittest.mock import patch

from engine import FULL_RUN, Workspace, stamp
from execution import RunCancelled, file_lock, run_command

CLI = Path(__file__).resolve().parents[1] / "cli.py"


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name)
        self.workspace = Workspace(self.path)

    def test_scaffold_adopts_existing_ports_and_preserves_files(self):
        created, kept = self.workspace.scaffold(8610, 8620)
        self.assertIn("compose.json", created)
        self.assertFalse(kept)
        self.assertEqual(self.workspace.endpoint(), "http://127.0.0.1:8610")
        self.assertEqual(self.workspace.endpoint(secure=True), "https://127.0.0.1:8620")

        postman = json.loads((self.path / "tests/gateway.postman_collection.json").read_text())
        self.assertEqual(postman["variable"][0]["value"], self.workspace.endpoint())
        app = self.path / "app.py"
        app.write_text("# Local edits\n", encoding="utf-8")
        self.assertEqual(self.workspace.scaffold(), ([], created))
        self.assertEqual(app.read_text(), "# Local edits\n")

        with self.assertRaisesRegex(ValueError, "existing HTTP port"):
            self.workspace.scaffold(8625)

    def test_scaffold_rejects_duplicates_before_creating_files(self):
        with self.assertRaisesRegex(ValueError, "different host ports"):
            self.workspace.scaffold(8610, 8610)
        self.assertEqual(list(self.path.iterdir()), [])

    def test_ports_allow_compose_long_form_and_reject_non_loopback(self):
        self.workspace.scaffold()
        config = self.path / "compose.json"
        data = json.loads(config.read_text())
        mapping = {"host_ip": "127.0.0.1", "published": "9100", "target": 5000, "protocol": "tcp"}
        data["services"]["gateway"]["ports"] = [mapping]
        config.write_text(json.dumps(data))
        self.assertEqual(self.workspace.port(), 9100)
        mapping["host_ip"] = "0.0.0.0"
        config.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "gateway binding"):
            self.workspace.port()

    def test_evidence_stales_when_nested_source_changes(self):
        self.workspace.scaffold()
        source = self.path / "src" / "service.py"
        source.parent.mkdir()
        source.write_text("version = 1")
        with patch.object(self.workspace, "execute", return_value="OK"):
            self.assertEqual(self.workspace.run("unit")[0], "Passed")
        source.write_text("version = 2")
        self.assertEqual(self.workspace.result("unit"), "Stale")

    def test_run_plan_continues_independent_checks_and_preserves_logs(self):
        self.workspace.scaffold()

        def execute(key, **_options):
            if key == "compose_up":
                raise RuntimeError("Docker unavailable")
            return "OK"

        with patch.object(self.workspace, "execute", side_effect=execute) as mock:
            results = list(self.workspace.run_plan(("compose_up", "smoke", "unit")))
        self.assertEqual([status for _, status, _ in results], ["Failed", "Blocked", "Passed"])
        self.assertEqual([call.args[0] for call in mock.call_args_list], ["compose_up", "unit"])
        reopened = Workspace(self.path)
        records = reopened.data["history"]
        self.assertEqual([record["check"] for record in records], ["compose_up", "smoke", "unit"])
        self.assertEqual((self.path / records[0]["log"]).read_text().strip(), "Docker unavailable")

    def test_baseline_uses_build_result_for_start(self):
        self.workspace.scaffold()
        with patch.object(self.workspace, "execute", return_value="OK") as mock:
            list(self.workspace.run_plan(("docker_build", "compose_up")))
        self.assertFalse(mock.call_args_list[1].kwargs["build"])

    def test_legacy_workspace_retains_notes_and_run_history(self):
        old = {"notes": {"vision": "Original note"}, "reviews": {},
               "checks": {"unit": {"status": "Passed", "when": stamp(), "log": ".ase-workbench/logs/old.log",
                                    "fingerprint": "legacy-fingerprint"}}}
        self.workspace.state.mkdir()
        self.workspace.state_path.write_text(json.dumps(old))
        workspace = Workspace(self.path)
        self.assertEqual(workspace.data["notes"]["vision"], "Original note")
        self.assertEqual(workspace.data["history"][0]["check"], "unit")
        self.assertEqual(workspace.result("unit"), "Stale")

    def test_parallel_app_instances_keep_independent_updates(self):
        self.workspace.scaffold()
        other = Workspace(self.path)
        self.workspace.set_note("vision", "Keep this note")
        with patch.object(other, "execute", return_value="OK"):
            list(other.run_plan(("unit",)))
        reopened = Workspace(self.path)
        self.assertEqual(reopened.data["notes"]["vision"], "Keep this note")
        self.assertEqual(reopened.result("unit"), "Passed")

    def test_duplicate_run_reports_workspace_busy(self):
        self.workspace.prepare_state_folder()
        with file_lock(self.workspace.state / "run.lock"):
            with self.assertRaisesRegex(ValueError, "already active"):
                list(Workspace(self.path).run_plan(("down",)))

    def test_release_review_checks_current_prerequisites(self):
        self.workspace.scaffold()
        for stage in ("vision", "stories", "architecture", "smells"):
            self.workspace.set_note(stage, "Reviewed")
            self.workspace.review(stage)
        self.workspace.set_note("delivery", "Local release review")
        with patch.object(self.workspace, "execute", return_value="OK"):
            list(self.workspace.run_plan(FULL_RUN))
        self.workspace.review("delivery")
        candidate = self.workspace.release_candidate()
        self.assertTrue((candidate / "manifest.json").is_file())
        with patch.object(self.workspace, "execute", side_effect=RuntimeError("Regression")):
            self.workspace.run("unit")
        self.assertEqual(self.workspace.status("delivery"), "Needs attention")
        with self.assertRaises(ValueError):
            self.workspace.release_candidate()

    def test_cli_reports_unavailable_checks_with_nonzero_exit(self):
        command = (sys.executable, str(CLI), "--workspace", str(self.path))
        scaffold = subprocess.run((*command, "scaffold", "--http-port", "9500"),
                                  capture_output=True, text=True, check=True)
        self.assertIn("http://127.0.0.1:9500", scaffold.stdout)
        run = subprocess.run((*command, "run", "quick"), capture_output=True, text=True)
        self.assertEqual(run.returncode, 1, run.stderr)
        self.assertIn("0/3 checks passed", run.stdout)
        self.assertEqual(len(Workspace(self.path).data["history"]), 3)

    def test_load_summary_requires_nonzero_requests(self):
        prefix = self.path / "load"
        report = self.path / "load_stats.csv"
        columns = "Name,Request Count,Failure Count,Requests/s,Median Response Time,95%\n"
        report.write_text(columns + "Aggregated,24,0,4,3,6\n")
        self.assertIn("p95 6 ms", self.workspace.load_summary(prefix))
        report.write_text(columns + "Aggregated,0,0,0,0,0\n")
        with self.assertRaisesRegex(ValueError, "0 requests"):
            self.workspace.load_summary(prefix)


class CommandTests(unittest.TestCase):
    def test_streaming_cancellation_preserves_partial_output(self):
        cancel = Event()
        chunks = []

        def output(chunk):
            chunks.append(chunk)
            if "started" in "".join(chunks):
                cancel.set()

        with TemporaryDirectory() as folder:
            with self.assertRaisesRegex(RunCancelled, "started"):
                run_command((sys.executable, "-c", "import time; print('started', flush=True); time.sleep(20)"),
                            folder, timeout=5, output=output, cancel=cancel)
        self.assertIn("started", "".join(chunks))

    def test_timeout_preserves_output(self):
        with TemporaryDirectory() as folder:
            with self.assertRaises(subprocess.TimeoutExpired) as context:
                run_command((sys.executable, "-c", "import time; print('waiting', flush=True); time.sleep(20)"),
                            folder, timeout=0.8)
        self.assertIn("waiting", context.exception.output)


if __name__ == "__main__":
    unittest.main()
