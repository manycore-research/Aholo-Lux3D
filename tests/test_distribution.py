"""Offline integration checks against the shipped portable Common Skill.

Run with: python -B -m unittest discover -s tests -v
Requires only the shipped runtime's declared Python dependencies. No live API
requests, credential setup, dependency installation or paid tasks are performed.

Author: yinjie.
"""

import base64
import contextlib
import datetime
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile
import unittest
import warnings
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/common/aholo-lux3d"
RUNTIME = SKILL / "core/runtime"
SECRET = "offline-fixture-key-not-a-real-credential"
CONTEXT_ID = "ctx_" + "1" * 32
QUOTE_ID = "quote_" + "a" * 32
CREATE_PATH = "/lux3d/v1/generate/text-to-3d/task/create"
ITEMS = {"1": {"endpoint": {"method": "POST", "path": CREATE_PATH},
               "parameters": {"body": {"prompt": "chair", "version": "G1-Turbo"}}}}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    status_code = 200

    def __init__(self, data):
        self.data = data
        self.closed = False

    def json(self):
        return {"c": "0", "m": "success", "d": self.data}

    def close(self):
        self.closed = True


class FakeSession:
    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.calls = []
        self.closed = False

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        if not self.outcomes:
            raise AssertionError("Unexpected HTTP request in an offline test")
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome

    def close(self):
        self.closed = True


def quote_session(source):
    now = datetime.datetime.now(datetime.timezone.utc)
    return FakeSession(FakeResponse({
        "availableCredits": 100, "trialCountMap": {}, "member": False,
        "memberType": 0, "snapshotAt": now.isoformat(), "uniqueId": CONTEXT_ID,
        "uniqueIdExpiresAt": (now + datetime.timedelta(hours=24)).isoformat(),
    }), FakeResponse({
        "source": source, "uniqueId": CONTEXT_ID, "quoteId": QUOTE_ID,
        "pricingScope": "BEFORE_ACCOUNT_BENEFITS", "quotedAt": now.isoformat(),
        "expiresAt": (now + datetime.timedelta(hours=1)).isoformat(),
        "estimatedCreditsTotal": 12, "details": {"1": 12},
    }))


class DistributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cli = load_module("distribution_commerce", SKILL / "scripts/commerce.py")

    def setUp(self):
        output = ROOT / "output"
        output.mkdir(exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="distribution-test-", dir=output)
        self.addCleanup(temporary.cleanup)
        self.temp = Path(temporary.name)
        # Fail closed if an implementation starts using an unexpected HTTP path.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import requests
        self.requests = requests
        blocker = mock.patch("requests.sessions.Session.request",
                             side_effect=AssertionError("Live HTTP is forbidden in these tests"))
        blocker.start()
        self.addCleanup(blocker.stop)

    def invoke(self, args, session, environment=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, environment or {}, clear=True), \
                mock.patch("requests.Session", return_value=session), \
                contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = self.cli.main(args)
        self.assertNotIn(SECRET, stdout.getvalue() + stderr.getvalue())
        return code, stdout.getvalue(), stderr.getvalue()

    def success(self, args, session, environment=None):
        code, stdout, stderr = self.invoke(args, session, environment)
        self.assertEqual(0, code, stderr)
        self.assertEqual("", stderr)
        self.assertTrue(session.closed)
        return json.loads(stdout)

    def process(self, *args):
        environment = {key: value for key, value in os.environ.items()
                       if not key.startswith(("LUX3D_", "CODEX_", "CLAUDE", "PYTHON"))}
        return subprocess.run([sys.executable, "-I", "-B", *map(str, args)],
                              cwd=self.temp, env=environment, capture_output=True,
                              text=True, encoding="utf-8", errors="replace", timeout=30)

    def test_all_bundled_runtime_modules_import_from_the_installed_directory(self):
        # A separate interpreter cannot silently reuse modules from another checkout.
        program = (
            "import importlib,pathlib,sys; root=pathlib.Path(sys.argv[1]).resolve(); "
            "sys.path.insert(0,str(root)); "
            "modules=[importlib.import_module(p.stem) for p in sorted(root.glob('*.py'))]; "
            "assert all(pathlib.Path(m.__file__).resolve().parent == root for m in modules); "
            "print(len(modules))"
        )
        result = self.process("-c", program, RUNTIME)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(len(list(RUNTIME.glob("*.py"))), int(result.stdout))

    def test_commerce_and_generation_entrypoints_expose_their_commands(self):
        for script, commands in (
            (SKILL / "scripts/commerce.py", ("balance", "quote", "init", "report", "feedback", "retry")),
            (RUNTIME / "lux3d_client.py", ("image", "text", "material", "four-view", "export", "query", "list")),
        ):
            for command in commands:
                with self.subTest(script=script.name, command=command):
                    result = self.process(script, command, "--help")
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertIn("usage:", result.stdout)

    def test_common_adapter_is_portable_and_source_overrides_fail_before_http(self):
        self.assertEqual(SKILL, self.cli.find_skill_root())
        self.assertEqual(RUNTIME, self.cli.find_runtime())
        adapter = self.cli.identity_support.load_adapter(SKILL)
        self.assertEqual("common", adapter["ecosystem"])
        self.assertEqual("automatic-host", adapter["identityMode"])
        self.assertNotIn("source", adapter)
        self.assertNotIn("profileId", adapter)
        for extra in (("--source", "100"), ("--binding", "fixture.json")):
            session = FakeSession()
            code, stdout, stderr = self.invoke(["balance", "--region", "cn", *extra], session,
                                               {"CODEX_THREAD_ID": "offline-session"})
            self.assertEqual((1, ""), (code, stdout))
            self.assertEqual("CLI_ARGUMENT_INVALID", json.loads(stderr)["error"]["code"])
            self.assertEqual([], session.calls)

    def test_cn_and_international_quotes_use_current_host_and_account_context(self):
        items = self.temp / "items.json"
        items.write_text(json.dumps(ITEMS), encoding="utf-8")
        hosts = (
            ((), {"CODEX_THREAD_ID": "offline-session"}, 1, "codex"),
            ((), {"CLAUDECODE": "1"}, 2, "claude-code"),
            (("--host-name", "DeepSeek"), {}, 3, "deepseek"),
            (("--host-name", "WorkBuddy"), {}, 4, "workbuddy"),
            ((), {"LUX3D_HOST_NAME": "  Other Host  "}, 100, "Other Host"),
            (("--host-name", "  豆包  "), {}, 100, "豆包"),
        )
        for region, variable, base in (
            ("cn", "LUX3D_CN_API_KEY", "https://api.aholo3d.cn"),
            ("international", "LUX3D_GLOBAL_API_KEY", "https://api.aholo3d.com/global"),
        ):
            for flags, metadata, source, name in hosts:
                with self.subTest(region=region, host=name):
                    session = quote_session(source)
                    result = self.success(["quote", "--region", region, "--items", str(items), *flags],
                                          session, {variable: SECRET, "LUX3D_SOURCE": "999", **metadata})
                    account, quote = session.calls
                    self.assertEqual(("GET", base + "/lux3d/v1/account/balance"), account[:2])
                    identity = {"source": source}
                    if source == 100:
                        identity["agentName"] = name
                    self.assertEqual(identity, account[2]["params"])
                    self.assertTrue(quote[1].startswith(base + "/lux3d/v1/"))
                    body = quote[2]["json"]
                    self.assertEqual((source, name, CONTEXT_ID),
                                     (body["source"], body["agentName"], body["uniqueId"]))
                    self.assertEqual(CREATE_PATH, body["items"]["1"]["endpoint"]["path"])
                    self.assertEqual(12, result["quote"]["estimatedCreditsTotal"])
                    for call in session.calls:
                        self.assertFalse(call[2]["allow_redirects"])
                        self.assertEqual(SECRET, call[2]["headers"]["Authorization"])

    def test_installed_invite_code_reaches_quote_and_report_from_another_cwd(self):
        with mock.patch.object(sys, "path", [str(ROOT / "scripts"), *sys.path]):
            installer = load_module("distribution_installer", ROOT / "scripts/install_skill.py")
        installed = Path(installer.install(self.temp / "skills", invite_code="TEST-INVITE")["path"])
        installed_cli = load_module("installed_distribution_commerce", installed / "scripts/commerce.py")
        items = self.temp / "items.json"
        items.write_text(json.dumps(ITEMS), encoding="utf-8")
        elsewhere = self.temp / "unrelated-working-directory"
        elsewhere.mkdir()
        (elsewhere / ".aholo-lux3d-installation.json").write_text(
            '{"inviteCode":"WRONG-CWD"}', encoding="utf-8")
        environment = {"LUX3D_CN_API_KEY": SECRET, "LUX3D_HOST_NAME": "WorkBuddy"}
        previous_cwd = Path.cwd()
        try:
            os.chdir(elsewhere)
            with mock.patch.object(self, "cli", installed_cli):
                quoted = quote_session(4)
                self.success(["quote", "--region", "cn", "--items", str(items)], quoted, environment)
                account, quote = quoted.calls
                self.assertEqual({"source": 4}, account[2]["params"])
                quote_body = quote[2]["json"]
                self.assertIsInstance(quote_body["context"], str)
                self.assertEqual("TEST-INVITE", json.loads(quote_body["context"])["inviteCode"])

                base = ["--region", "cn", "--journal", str(self.temp / "collection.sqlite")]
                initialized = self.success(["init", *base], FakeSession(), environment)
                report_request = self.temp / "report.json"
                report_request.write_text(json.dumps({
                    "pluginTaskId": initialized["pluginTaskId"], "requestId": "installed-report-1",
                    "result": {"status": "SUCCEEDED"},
                }), encoding="utf-8")
                receipt = {"reportId": "report_" + "a" * 64,
                           "receiptStatus": "ACCEPTED", "checkResult": "OK"}
                reported = FakeSession(FakeResponse(receipt))
                self.assertEqual(receipt, self.success(
                    ["report", *base, "--request", str(report_request)], reported, environment))
                self.assertEqual(1, len(reported.calls))
                report_body = reported.calls[0][2]["json"]
                self.assertIsInstance(report_body["context"], str)
                self.assertEqual("TEST-INVITE", json.loads(report_body["context"])["inviteCode"])
        finally:
            os.chdir(previous_cwd)

    def test_registered_aliases_resolve_to_their_host(self):
        registry = json.loads((SKILL / "host-identity.json").read_text(encoding="utf-8"))
        for host in registry["knownHosts"].values():
            for alias in host["aliases"]:
                with self.subTest(alias=alias):
                    self.assertEqual({"source": host["source"], "agentName": host["agentName"]},
                                     self.cli.identity_support.resolve_host_identity({}, "  " + alias.upper() + "  "))

    def test_missing_host_is_not_inferred_from_keys_model_or_install_directory(self):
        session = FakeSession()
        code, stdout, stderr = self.invoke(["balance", "--region", "cn"], session, {
            "LUX3D_CN_API_KEY": SECRET, "OPENAI_API_KEY": SECRET, "MODEL": "codex",
            "CODEX_HOME": "codex", "CLAUDECODE": "0", "LUX3D_SOURCE": "1",
        })
        self.assertEqual((1, ""), (code, stdout))
        self.assertEqual("CLI_HOST_IDENTITY_REQUIRED", json.loads(stderr)["error"]["code"])
        self.assertEqual([], session.calls)

    def test_conflicting_host_metadata_fails_before_http(self):
        cases = (
            ({"CODEX_THREAD_ID": "offline-session", "CLAUDECODE": "1"}, ()),
            ({"CODEX_THREAD_ID": "offline-session"}, ("--host-name", "WorkBuddy")),
            ({"LUX3D_HOST_NAME": "Other Host"}, ("--host-name", "WorkBuddy")),
            ({"LUX3D_HOST_NAME": "Other Host", "CLAUDECODE": "1"}, ()),
        )
        for metadata, flags in cases:
            with self.subTest(metadata=metadata, flags=flags):
                session = FakeSession()
                code, stdout, stderr = self.invoke(["balance", "--region", "cn", *flags], session,
                                                   {"LUX3D_CN_API_KEY": SECRET, **metadata})
                self.assertEqual((1, ""), (code, stdout))
                self.assertEqual("CLI_HOST_IDENTITY_CONFLICT", json.loads(stderr)["error"]["code"])
                self.assertEqual([], session.calls)

    def test_invalid_host_metadata_fails_before_http(self):
        for name in ("", "   ", "x" * 129, "bad\x00host", "\nCodex\n"):
            with self.subTest(name=repr(name)):
                session = FakeSession()
                code, stdout, stderr = self.invoke(["balance", "--region", "cn", "--host-name", name],
                                                   session, {"LUX3D_CN_API_KEY": SECRET})
                self.assertEqual((1, ""), (code, stdout))
                self.assertEqual("CLI_HOST_IDENTITY_INVALID", json.loads(stderr)["error"]["code"])
                self.assertEqual([], session.calls)

    def test_host_detection_works_without_installed_dependencies(self):
        for name, source, canonical in (("Codex", 1, "codex"), ("WorkBuddy", 4, "workbuddy"),
                                        ("Other Host", 100, "Other Host")):
            with self.subTest(host=name):
                result = self.process("-S", SKILL / "scripts/host_identity.py", "detect", "--host-name", name)
                self.assertEqual(0, result.returncode, result.stderr)
                self.assertEqual({"status": "detected", "source": source, "agentName": canonical},
                                 json.loads(result.stdout))

    def test_explicit_region_never_falls_back_to_other_region_credentials(self):
        session = FakeSession()
        code, stdout, stderr = self.invoke(["balance", "--region", "international"],
                                          session, {"LUX3D_CN_API_KEY": SECRET, "LUX3D_HOST_NAME": "WorkBuddy"})
        self.assertEqual((1, ""), (code, stdout))
        self.assertEqual("API_KEY_REQUIRED", json.loads(stderr)["error"]["code"])
        self.assertEqual([], session.calls)

    def test_collection_retry_uses_frozen_request_after_input_file_is_gone(self):
        journal = self.temp / "collection.sqlite"
        environment = {"LUX3D_CN_API_KEY": SECRET, "LUX3D_HOST_NAME": "WorkBuddy"}
        base = ["--region", "cn", "--journal", str(journal)]
        initialized = self.success(["init", *base, "--model-name", "observed-model",
                                    "--client-region", "Shanghai, CN"], FakeSession(), environment)
        request = self.temp / "report.json"
        request.write_text(json.dumps({"pluginTaskId": initialized["pluginTaskId"],
                                      "requestId": "report-1", "result": {"status": "SUCCEEDED"}}),
                           encoding="utf-8")
        first = FakeSession(self.requests.Timeout())
        code, stdout, stderr = self.invoke(["report", *base, "--request", str(request)], first, environment)
        self.assertEqual((1, ""), (code, stdout))
        self.assertIn("error", json.loads(stderr))
        self.assertEqual(1, len(first.calls))
        request.unlink()
        # A later observed model must not replace the original frozen request.
        self.success(["init", *base, "--model-name", "later-model"], FakeSession(), environment)
        receipt = {"reportId": "report_" + "a" * 64, "receiptStatus": "ACCEPTED", "checkResult": "OK"}
        retry = FakeSession(FakeResponse(receipt))
        command = ["retry", *base, "--kind", "report", "--request-id", "report-1"]
        self.assertEqual(receipt, self.success(command, retry, environment))
        self.assertEqual(first.calls[0][2]["json"], retry.calls[0][2]["json"])
        self.assertEqual("observed-model", retry.calls[0][2]["json"]["modelName"])
        self.assertEqual((4, "workbuddy"), (retry.calls[0][2]["json"]["source"],
                                           retry.calls[0][2]["json"]["agentName"]))
        cached = FakeSession()
        self.assertEqual(receipt, self.success(command, cached, environment))
        self.assertEqual([], cached.calls, "An acknowledged retry must not resend a report")

    def test_feedback_requires_consent_to_its_specific_version(self):
        journal = self.temp / "collection.sqlite"
        environment = {"LUX3D_CN_API_KEY": SECRET, "LUX3D_HOST_NAME": "Other Host"}
        base = ["--region", "cn", "--journal", str(journal)]
        initialized = self.success(["init", *base], FakeSession(), environment)
        request = self.temp / "feedback.json"
        body = {"pluginTaskId": initialized["pluginTaskId"], "requestId": "feedback-1",
                "agentFeedback": "Offline fixture"}
        request.write_text(json.dumps(body), encoding="utf-8")
        session = FakeSession()
        code, _, stderr = self.invoke(["feedback", *base, "--request", str(request)], session, environment)
        self.assertEqual(1, code)
        self.assertEqual("COLLECTION_REQUEST_INVALID", json.loads(stderr)["error"]["code"])
        self.assertEqual([], session.calls)
        body["consent"] = {"granted": True, "feedbackVersion": "v1"}
        request.write_text(json.dumps(body), encoding="utf-8")
        receipt = {"feedbackId": "feedback_" + "b" * 64, "submissionStatus": "ACCEPTED"}
        session = FakeSession(FakeResponse(receipt))
        self.assertEqual(receipt, self.success(["feedback", *base, "--request", str(request)],
                                              session, environment))
        self.assertEqual(body["consent"], json.loads(session.calls[0][2]["json"]["consent"]))
        self.assertEqual((100, "Other Host"), (session.calls[0][2]["json"]["source"],
                                              session.calls[0][2]["json"]["agentName"]))

    def test_missing_dependencies_and_setup_check_do_not_install_or_call_api(self):
        result = self.process("-S", SKILL / "scripts/commerce.py", "balance", "--region", "cn",
                              "--host-name", "Other Host")
        self.assertEqual(1, result.returncode)
        self.assertEqual("CLI_DEPENDENCY_MISSING", json.loads(result.stderr)["error"]["code"])
        cache = self.temp / "absent environment"
        result = self.process("-S", SKILL / "scripts/setup_runtime.py", "--check", "--env-dir", cache)
        self.assertEqual(1, result.returncode)
        self.assertEqual("CLI_DEPENDENCY_SETUP_REQUIRED", json.loads(result.stderr)["error"]["code"])
        self.assertFalse(cache.exists())

    def test_delivery_preserves_fixture_glb_and_embeds_all_preview_resources(self):
        document = json.dumps({"asset": {"version": "2.0"}, "scenes": [], "nodes": [], "meshes": []}).encode()
        document += b" " * (-len(document) % 4)
        model = struct.pack("<4sII", b"glTF", 2, 20 + len(document))
        model += struct.pack("<II", len(document), 0x4E4F534A) + document
        asset = self.temp / "fixture.glb"
        asset.write_bytes(model)
        state = self.temp / "attempt.json"
        state.write_text(json.dumps({
            "schema": "lux3d.workflow-state/v1", "status": "succeeded",
            "createdAt": "2026-10-09T01:00:00+00:00", "updatedAt": "2026-10-09T01:01:00+00:00",
            "taskId": "9007199254740993", "lastKnownProviderStatus": 3, "expectedFormats": ["glb"],
            "request": {"operation": "text-to-3d", "region": "cn", "version": "G1-Turbo"},
            "downloadedArtifacts": [{"path": str(asset), "format": "glb"}],
        }), encoding="utf-8")
        spec = self.temp / "spec.json"
        spec.write_text(json.dumps({
            "schema": "lux3d.delivery-spec/v2", "title": "Offline fixture </script>",
            "items": [{"id": "fixture", "label": "Fixture", "selectedAttemptId": "fixture-attempt",
                       "attempts": [{"id": "fixture-attempt", "statePath": str(state)}]}],
        }), encoding="utf-8")
        target = self.temp / "delivery"
        program = ("import sys; sys.path.insert(0,sys.argv[1]); import delivery_bundle; "
                   "delivery_bundle.prepare_bundle(sys.argv[2],sys.argv[3],locale='zh-CN')")
        result = self.process("-c", program, RUNTIME, spec, target)
        self.assertEqual(0, result.returncode, result.stderr)
        manifest = json.loads((target / "lux3d-delivery.json").read_text(encoding="utf-8"))
        self.assertEqual("complete", manifest["assetStatus"])
        artifact = manifest["artifacts"][0]
        self.assertEqual(model, (target / artifact["path"]).read_bytes())
        html = (target / "preview.html").read_text(encoding="utf-8")
        embedded = re.search(r'<script id="lux3d-data" type="application/json">([^<]*)</script>', html)
        self.assertIsNotNone(embedded)
        payload = json.loads(embedded[1])
        self.assertEqual(manifest, payload["manifest"])
        self.assertEqual(model, base64.b64decode(payload["assets"][artifact["id"]]))
        self.assertEqual(4, len(payload["decoders"]))
        self.assertTrue(all(value.startswith("data:") for value in payload["decoders"].values()))
        self.assertNotRegex(html, r'<(?:script|link)\b[^>]*(?:src|href)=["\']https?://')


if __name__ == "__main__":
    unittest.main()
