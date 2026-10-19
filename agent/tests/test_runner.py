import contextlib
import importlib
import io
import json
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock

from site_agent import runner
from site_agent.schemas import RequestError, load_request, validate_request
from site_agent.tools import request_build

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "site-request.json"


class StarterTests(unittest.TestCase):
    def setUp(self):
        self.request = json.loads(EXAMPLE.read_text())
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / "report.json"

    def run_cli(self, *args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return runner.main(["--request", str(EXAMPLE), "--output", str(self.output), *args])

    def test_offline_never_opens_a_socket_even_with_credentials_present(self):
        with mock.patch("socket.socket.connect", side_effect=AssertionError("network")), \
                mock.patch.dict(os.environ, {"OPENAI_API_KEY": "synthetic-unused"}):
            self.assertEqual(self.run_cli(), 0)
        report = json.loads(self.output.read_text())
        self.assertEqual(report["status"], "BLOCKED_NOT_IMPLEMENTED")
        self.assertEqual(report["artifacts"], [])
        self.assertFalse(report["native_validation_performed"])
        self.assertFalse(report["production_actions_performed"])
        self.assertIsNone(report["model_advice"])

    def test_missing_facts_are_preserved_not_invented(self):
        self.request["plc_address"] = None
        report = runner.make_report(validate_request(self.request), "offline")
        self.assertEqual(report["missing_fields"], ["plc_address"])
        self.assertEqual(report["status"], "NEEDS_INPUT")

    def test_live_without_key_writes_awaiting_auth_without_network(self):
        with mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch("socket.socket.connect", side_effect=AssertionError("network")):
            self.assertEqual(self.run_cli("--mode", "live"), 2)
        self.assertEqual(json.loads(self.output.read_text())["status"], "AWAITING_AUTH")

    def test_live_without_model_is_explicit_configuration_failure(self):
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "synthetic-unused"}, clear=True):
            self.assertEqual(self.run_cli("--mode", "live"), 2)
        self.assertEqual(json.loads(self.output.read_text())["status"], "CONFIGURATION_REQUIRED")

    def test_existing_report_is_not_overwritten(self):
        self.output.write_text("keep this")
        self.assertEqual(self.run_cli(), 2)
        self.assertEqual(self.output.read_text(), "keep this")

    def test_live_provider_error_does_not_leak_exception_details(self):
        fake_adapter = types.ModuleType("site_agent.sdk_adapter")

        async def fail(*args):
            raise RuntimeError("synthetic-private-request-detail")

        fake_adapter.get_live_advice = fail
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": "synthetic-unused", "OPENAI_MODEL": "test-model"}), \
                mock.patch.dict("sys.modules", {"site_agent.sdk_adapter": fake_adapter}):
            self.assertEqual(self.run_cli("--mode", "live"), 3)
        text = self.output.read_text()
        self.assertEqual(json.loads(text)["status"], "MODEL_FAILED")
        self.assertNotIn("synthetic-private-request-detail", text)
        self.assertNotIn("synthetic-unused", text)

    def test_duplicate_fields_rejected(self):
        path = Path(self.temp.name) / "duplicate.json"
        path.write_text('{"schema_version":1,"schema_version":2}')
        with self.assertRaises(RequestError):
            load_request(path)

    def test_invalid_scope_and_fields_rejected(self):
        mutations = [
            {"job_type": "commission_site"}, {"schema_version": True},
            {"target_site": "exampledonor"}, {"donor_backup_ref": "../backup.gwbk"},
            {"plc_address": "invent-this"}, {"changes": "not-a-list"},
            {"api_key": "synthetic-unused"},
        ]
        for change in mutations:
            with self.subTest(change=change), self.assertRaises(RequestError):
                validate_request({**self.request, **change})

    def test_oversized_request_rejected(self):
        path = Path(self.temp.name) / "large.json"
        path.write_bytes(b" " * 65537)
        with self.assertRaises(RequestError):
            load_request(path)

    def test_stub_never_reports_success(self):
        self.assertEqual(request_build("build_artifacts")["status"], "NOT_IMPLEMENTED")
        with self.assertRaises(ValueError):
            request_build("deploy")

    def test_import_has_no_file_or_network_side_effects(self):
        with mock.patch("builtins.open", side_effect=AssertionError("write")), \
                mock.patch("socket.socket.connect", side_effect=AssertionError("network")):
            importlib.reload(runner)


if __name__ == "__main__":
    unittest.main()
