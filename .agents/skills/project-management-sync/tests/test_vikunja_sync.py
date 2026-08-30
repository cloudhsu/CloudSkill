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

    def test_missing_update_capability_does_not_disable_create(self) -> None:
        class CreateOnlyHTTP:
            def request(self, method, path, **kwargs):
                if method == "GET" and path == "info":
                    return vikunja_sync.HttpResponse(200, {}, {"version": "v2.5.0"})
                if method == "OPTIONS" and path == "tasks/0":
                    raise vikunja_sync.SyncError("http_405")
                return vikunja_sync.HttpResponse(204, {"allow": "OPTIONS, GET, PUT"}, None)

        capabilities = vikunja_sync.VikunjaAdapter(CreateOnlyHTTP()).discover()
        self.assertTrue(capabilities.writable)
        self.assertFalse(capabilities.task_update_writable)

    def test_missing_create_capability_does_not_disable_update(self) -> None:
        class UpdateOnlyHTTP:
            def request(self, method, path, **kwargs):
                if method == "GET" and path == "info":
                    return vikunja_sync.HttpResponse(200, {}, {"version": "v2.5.0"})
                if method == "OPTIONS" and path == "tasks/0":
                    return vikunja_sync.HttpResponse(204, {"allow": "OPTIONS, GET, PATCH"}, None)
                raise vikunja_sync.SyncError("http_405")

        capabilities = vikunja_sync.VikunjaAdapter(UpdateOnlyHTTP()).discover()
        self.assertFalse(capabilities.writable)
        self.assertTrue(capabilities.task_update_writable)

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

    def test_completed_source_owned_status_plans_update(self) -> None:
        candidate = plan()
        candidate["source_owned_fields"] = ["status"]
        candidate["tasks"][0]["status"] = "completed"
        adapter = vikunja_sync.FakeAdapter(
            projects=[{"id": 1, "title": "test-project"}],
            tasks={1: [{"id": 2, "title": "test-task", "done": False}]},
        )
        report, _, operations = vikunja_sync.plan_remote(
            adapter, vikunja_sync.validate_plan(candidate), "dry-run", "2026-08-29"
        )
        self.assertEqual(report["planned"]["update"], 1)
        self.assertEqual(operations[-1]["reason"], "source_owned_status_differs")

    def test_status_is_read_only_without_explicit_ownership(self) -> None:
        candidate = plan()
        candidate["tasks"][0]["status"] = "completed"
        adapter = vikunja_sync.FakeAdapter(
            projects=[{"id": 1, "title": "test-project"}],
            tasks={1: [{"id": 2, "title": "test-task", "done": False}]},
        )
        report, _, _ = vikunja_sync.plan_remote(
            adapter, vikunja_sync.validate_plan(candidate), "dry-run", "2026-08-29"
        )
        self.assertEqual(report["planned"]["no-op"], 2)

    def test_unknown_owned_field_and_status_are_rejected(self) -> None:
        candidate = plan()
        candidate["source_owned_fields"] = ["description"]
        candidate["tasks"][0]["status"] = "closed-ish"
        with self.assertRaises(vikunja_sync.SyncError):
            vikunja_sync.validate_plan(candidate)

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

    def test_apply_updates_only_source_owned_status_and_verifies_completion(self) -> None:
        candidate = plan()
        candidate["source_owned_fields"] = ["status"]
        candidate["tasks"][0]["status"] = "completed"
        remote = {
            "id": 2,
            "title": "test-task",
            "description": "provider-owned narrative",
            "done": False,
            "done_at": None,
            "updated": "2026-08-28T00:00:00Z",
        }
        adapter = vikunja_sync.FakeAdapter(
            projects=[{"id": 1, "title": "test-project"}], tasks={1: [remote]}
        )
        with tempfile.TemporaryDirectory() as directory:
            journal = Path(directory) / "journal.json"
            report, project_id, operations = vikunja_sync.plan_remote(
                adapter, vikunja_sync.validate_plan(candidate), "apply", "2026-08-29"
            )
            report = vikunja_sync.apply_plan(
                adapter, candidate, report, project_id, operations, journal, None, "2026-08-29"
            )
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["executed"]["update"], 1)
        self.assertEqual(report["post_write_readback"], "PASS")
        self.assertTrue(remote["done"])
        self.assertTrue(remote["done_at"])
        self.assertEqual(remote["description"], "provider-owned narrative")

    def test_update_timeout_is_unknown_and_not_retried(self) -> None:
        class TimeoutAdapter(vikunja_sync.FakeAdapter):
            calls = 0

            def update_task(self, task_id, payload):
                self.calls += 1
                raise vikunja_sync.SyncError("transport_unknown", unknown=True)

        candidate = plan()
        candidate["source_owned_fields"] = ["status"]
        candidate["tasks"][0]["status"] = "completed"
        adapter = TimeoutAdapter(
            projects=[{"id": 1, "title": "test-project"}],
            tasks={1: [{"id": 2, "title": "test-task", "done": False}]},
        )
        with tempfile.TemporaryDirectory() as directory:
            journal = Path(directory) / "journal.json"
            report, project_id, operations = vikunja_sync.plan_remote(
                adapter, vikunja_sync.validate_plan(candidate), "apply", "2026-08-29"
            )
            report = vikunja_sync.apply_plan(
                adapter, candidate, report, project_id, operations, journal, None, "2026-08-29"
            )
            retry_report, retry_project_id, retry_operations = vikunja_sync.plan_remote(
                adapter, vikunja_sync.validate_plan(candidate), "apply", "2026-08-29"
            )
            retry_report = vikunja_sync.apply_plan(
                adapter,
                candidate,
                retry_report,
                retry_project_id,
                retry_operations,
                journal,
                None,
                "2026-08-29",
            )
            entry = json.loads(journal.read_text())["operations"][0]
        self.assertEqual(report["status"], "UNKNOWN")
        self.assertEqual(retry_report["status"], "UNKNOWN")
        self.assertEqual(report["reconciliation"], "run_reconcile_before_retry")
        self.assertEqual(entry["status"], "unknown")
        self.assertEqual(adapter.calls, 1)

    def test_update_readback_requires_updated_marker(self) -> None:
        class MissingUpdatedAdapter(vikunja_sync.FakeAdapter):
            def update_task(self, task_id, payload):
                task = super().update_task(task_id, payload)
                task.pop("updated", None)
                return task

        candidate = plan()
        candidate["source_owned_fields"] = ["status"]
        candidate["tasks"][0]["status"] = "completed"
        adapter = MissingUpdatedAdapter(
            projects=[{"id": 1, "title": "test-project"}],
            tasks={1: [{"id": 2, "title": "test-task", "done": False, "done_at": None}]},
        )
        with tempfile.TemporaryDirectory() as directory:
            journal = Path(directory) / "journal.json"
            report, project_id, operations = vikunja_sync.plan_remote(
                adapter, vikunja_sync.validate_plan(candidate), "apply", "2026-08-29"
            )
            report = vikunja_sync.apply_plan(
                adapter, candidate, report, project_id, operations, journal, None, "2026-08-29"
            )
        self.assertEqual(report["status"], "UNKNOWN")

    def test_reconcile_status_update_distinguishes_committed_from_not_committed(self) -> None:
        class TimeoutAfterCommit(vikunja_sync.FakeAdapter):
            def update_task(self, task_id, payload):
                super().update_task(task_id, payload)
                raise vikunja_sync.SyncError("transport_unknown", unknown=True)

        candidate = plan()
        candidate["source_owned_fields"] = ["status"]
        candidate["tasks"][0]["status"] = "completed"
        for adapter_type, expected_key in (
            (TimeoutAfterCommit, "reconciled"),
            (None, "safe_to_retry"),
        ):
            adapter = (
                adapter_type(
                    projects=[{"id": 1, "title": "test-project"}],
                    tasks={1: [{"id": 2, "title": "test-task", "done": False, "done_at": None, "updated": "before"}]},
                )
                if adapter_type
                else vikunja_sync.FakeAdapter(
                    projects=[{"id": 1, "title": "test-project"}],
                    tasks={1: [{"id": 2, "title": "test-task", "done": False, "done_at": None, "updated": "before"}]},
                )
            )
            with tempfile.TemporaryDirectory() as directory:
                journal = Path(directory) / "journal.json"
                report, project_id, operations = vikunja_sync.plan_remote(
                    adapter, vikunja_sync.validate_plan(candidate), "apply", "2026-08-29"
                )
                if adapter_type:
                    vikunja_sync.apply_plan(
                        adapter, candidate, report, project_id, operations, journal, None, "2026-08-29"
                    )
                else:
                    vikunja_sync._journal_save(
                        journal,
                        {
                            "schema_version": 1,
                            "operations": [{
                                "operation_id": "task:TEST-1",
                                "kind": "task",
                                "operation": "update_status",
                                "title": "test-task",
                                "remote_id": 2,
                                "desired_done": True,
                                "before_updated": "before",
                                "status": "unknown",
                            }],
                        },
                    )
                reconciled = vikunja_sync.reconcile_unknowns(adapter, journal)
            self.assertEqual(reconciled[expected_key], 1)

    def test_timeout_after_commit_still_requires_reconcile_before_second_apply(self) -> None:
        class TimeoutAfterCommit(vikunja_sync.FakeAdapter):
            calls = 0

            def update_task(self, task_id, payload):
                self.calls += 1
                super().update_task(task_id, payload)
                raise vikunja_sync.SyncError("transport_unknown", unknown=True)

        candidate = plan()
        candidate["source_owned_fields"] = ["status"]
        candidate["tasks"][0]["status"] = "completed"
        adapter = TimeoutAfterCommit(
            projects=[{"id": 1, "title": "test-project"}],
            tasks={1: [{"id": 2, "title": "test-task", "done": False, "done_at": None, "updated": "before"}]},
        )
        with tempfile.TemporaryDirectory() as directory:
            journal = Path(directory) / "journal.json"
            first, project_id, operations = vikunja_sync.plan_remote(
                adapter, vikunja_sync.validate_plan(candidate), "apply", "2026-08-29"
            )
            vikunja_sync.apply_plan(adapter, candidate, first, project_id, operations, journal, None, "2026-08-29")
            second, project_id, operations = vikunja_sync.plan_remote(
                adapter, vikunja_sync.validate_plan(candidate), "apply", "2026-08-29"
            )
            second = vikunja_sync.apply_plan(
                adapter, candidate, second, project_id, operations, journal, None, "2026-08-29"
            )
        self.assertEqual(second["status"], "UNKNOWN")
        self.assertEqual(adapter.calls, 1)

    def test_status_update_preserves_description_against_whole_object_write(self) -> None:
        """Vikunja resets any field absent from an update body. The status-only
        path must round-trip the whole task so the description survives."""

        class ClobberingVikunjaFake(vikunja_sync.FakeAdapter):
            # Models the real provider: only fields present in the payload are
            # kept; every other writable field is reset to its zero value.
            _WRITABLE = ("title", "description", "due_date", "priority", "done", "percent_done")

            def update_task(self, task_id, payload):
                task = self.read_task(task_id)
                for field in self._WRITABLE:
                    task[field] = payload.get(field, "" if isinstance(task.get(field), str) else None)
                task["updated"] = "2026-08-29T00:00:01Z"
                if task.get("done"):
                    task["done_at"] = "2026-08-29T00:00:00Z"
                return task

        candidate = plan()
        candidate["source_owned_fields"] = ["status"]
        candidate["tasks"][0]["status"] = "completed"
        adapter = ClobberingVikunjaFake(
            projects=[{"id": 1, "title": "test-project"}],
            tasks={
                1: [{
                    "id": 2,
                    "title": "test-task",
                    "description": "load-bearing narrative that must not be lost",
                    "done": False,
                    "done_at": None,
                    "updated": "before",
                }],
            },
        )
        with tempfile.TemporaryDirectory() as directory:
            journal = Path(directory) / "journal.json"
            report, project_id, operations = vikunja_sync.plan_remote(
                adapter, vikunja_sync.validate_plan(candidate), "apply", "2026-08-29"
            )
            report = vikunja_sync.apply_plan(
                adapter, candidate, report, project_id, operations, journal, None, "2026-08-29"
            )
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["executed"]["update"], 1)
        remote = adapter.read_task(2)
        self.assertTrue(remote["done"])
        self.assertEqual(remote["description"], "load-bearing narrative that must not be lost")

    def test_status_update_fails_closed_if_a_preserved_field_is_clobbered(self) -> None:
        """If the provider still drops a preserved field, the readback must fail
        as UNKNOWN (so reconcile runs) rather than silently reporting success."""

        class DescriptionDroppingFake(vikunja_sync.FakeAdapter):
            def update_task(self, task_id, payload):
                # Simulate a provider that ignores the description on update.
                return super().update_task(task_id, {**payload, "description": ""})

        candidate = plan()
        candidate["source_owned_fields"] = ["status"]
        candidate["tasks"][0]["status"] = "completed"
        adapter = DescriptionDroppingFake(
            projects=[{"id": 1, "title": "test-project"}],
            tasks={1: [{"id": 2, "title": "test-task", "description": "keep me", "done": False, "done_at": None, "updated": "before"}]},
        )
        with tempfile.TemporaryDirectory() as directory:
            journal = Path(directory) / "journal.json"
            report, project_id, operations = vikunja_sync.plan_remote(
                adapter, vikunja_sync.validate_plan(candidate), "apply", "2026-08-29"
            )
            report = vikunja_sync.apply_plan(
                adapter, candidate, report, project_id, operations, journal, None, "2026-08-29"
            )
        self.assertEqual(report["status"], "UNKNOWN")
        self.assertEqual(report["reconciliation"], "run_reconcile_before_retry")

    def test_reconcile_rejects_malformed_remote_id_without_transport(self) -> None:
        adapter = vikunja_sync.FakeAdapter()
        with tempfile.TemporaryDirectory() as directory:
            journal = Path(directory) / "journal.json"
            vikunja_sync._journal_save(
                journal,
                {
                    "schema_version": 1,
                    "operations": [{
                        "operation_id": "task:TEST-1",
                        "kind": "task",
                        "operation": "update_status",
                        "remote_id": "not-an-id",
                        "desired_done": True,
                        "status": "unknown",
                    }],
                },
            )
            report = vikunja_sync.reconcile_unknowns(adapter, journal)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(report["blocked"], 1)


if __name__ == "__main__":
    unittest.main()
