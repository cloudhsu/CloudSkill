from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = (Path(__file__).parent.parent / "scripts" / "vikunja_sync.py").resolve()
SPEC = importlib.util.spec_from_file_location("vikunja_sync", SCRIPT)
assert SPEC and SPEC.loader
vikunja_sync = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = vikunja_sync
SPEC.loader.exec_module(vikunja_sync)


def plan() -> dict:
    return {
        "source_system": "test-backlog",
        "target_provider": "vikunja",
        "target_profile": "test",
        "agent": "Codex 5.6 Luna xhigh",
        "project": {"title": "test-project", "description": "test scope"},
        "tasks": [
            {
                "source_key": "TEST-1",
                "title": "test-task",
                "problem_background": "test background",
                "approach": "test approach",
                "acceptance_criteria": ["test evidence"],
                "source": "test source",
                "status": "planned",
            }
        ],
    }


class VikunjaSyncTests(unittest.TestCase):
    def test_service_preflight_fails_closed_when_unavailable(self) -> None:
        class UnavailableHTTP:
            def request(self, *args, **kwargs):
                raise vikunja_sync.SyncError("transport_unknown", unknown=True)

        with self.assertRaises(vikunja_sync.SyncError) as context:
            vikunja_sync.VikunjaAdapter(UnavailableHTTP()).discover()
        self.assertEqual(context.exception.code, "service_unavailable")

    def test_vikunja_version_prefix_is_supported(self) -> None:
        class DiscoveryHTTP:
            def request(self, method, path, **kwargs):
                if method == "GET" and path == "info":
                    return vikunja_sync.HttpResponse(200, {}, {"version": "v2.5.0"})
                return vikunja_sync.HttpResponse(204, {"allow": "OPTIONS, GET, PUT"}, None)

        capabilities = vikunja_sync.VikunjaAdapter(DiscoveryHTTP()).discover()
        self.assertTrue(capabilities.writable)
        self.assertEqual(capabilities.api_family, "vikunja-v2-api-v1-route")

    def test_description_has_fixed_sections_and_agent(self) -> None:
        description = vikunja_sync.render_description(plan()["tasks"][0], plan()["agent"], "2026-08-23")
        positions = [description.index(section) for section in vikunja_sync.DESCRIPTION_SECTIONS]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("### Progress 2026-08-23", description)
        self.assertIn("- Agent: Codex 5.6 Luna xhigh", description)

    def test_missing_agent_is_rejected(self) -> None:
        candidate = plan()
        del candidate["agent"]
        with self.assertRaises(vikunja_sync.SyncError):
            vikunja_sync.validate_plan(candidate)

    def test_future_provider_is_rejected_before_transport(self) -> None:
        candidate = plan()
        candidate["target_provider"] = "redmine"
        with self.assertRaises(vikunja_sync.SyncError):
            vikunja_sync.validate_plan(candidate)

    def test_dry_run_creates_project_and_task_without_mutation(self) -> None:
        adapter = vikunja_sync.FakeAdapter()
        candidate = vikunja_sync.validate_plan(plan())
        report, project_id, operations = vikunja_sync.plan_remote(adapter, candidate, "dry-run", "2026-08-23")
        self.assertIsNone(project_id)
        self.assertEqual(report["planned"]["create"], 2)
        self.assertEqual(len(adapter.projects), 0)
        self.assertEqual([operation["action"] for operation in operations], ["create", "create"])

    def test_existing_exact_task_is_noop(self) -> None:
        adapter = vikunja_sync.FakeAdapter(projects=[{"id": 1, "title": "test-project"}], tasks={1: [{"id": 2, "title": "test-task"}]})
        candidate = vikunja_sync.validate_plan(plan())
        report, project_id, operations = vikunja_sync.plan_remote(adapter, candidate, "dry-run", "2026-08-23")
        self.assertEqual(project_id, 1)
        self.assertEqual(report["planned"]["no-op"], 2)
        self.assertEqual(operations[-1]["reason"], "exact_title_match")

    def test_duplicate_exact_task_is_ambiguous(self) -> None:
        adapter = vikunja_sync.FakeAdapter(
            projects=[{"id": 1, "title": "test-project"}],
            tasks={1: [{"id": 2, "title": "test-task"}, {"id": 3, "title": "test-task"}]},
        )
        candidate = vikunja_sync.validate_plan(plan())
        report, _, _ = vikunja_sync.plan_remote(adapter, candidate, "dry-run", "2026-08-23")
        self.assertEqual(report["planned"]["ambiguous"], 1)

    def test_apply_readback_and_private_mapping(self) -> None:
        adapter = vikunja_sync.FakeAdapter()
        candidate = vikunja_sync.validate_plan(plan())
        with tempfile.TemporaryDirectory() as directory:
            journal = Path(directory) / "journal.json"
            mapping = Path(directory) / "mapping.json"
            report, project_id, operations = vikunja_sync.plan_remote(adapter, candidate, "apply", "2026-08-23")
            report = vikunja_sync.apply_plan(adapter, candidate, report, project_id, operations, journal, mapping, "2026-08-23")
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["executed"]["create"], 2)
            self.assertEqual(report["post_write_readback"], "PASS")
            self.assertEqual(json.loads(mapping.read_text())["records"]["TEST-1"]["target_record_id"], 9002)


if __name__ == "__main__":
    unittest.main()
