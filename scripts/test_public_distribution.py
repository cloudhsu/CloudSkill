"""Mutation tests for the fail-closed public distribution contract."""

from __future__ import annotations

from pathlib import Path
import json
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from public_distribution_contract import (  # noqa: E402
    PUBLIC_SKILL_TABLE_BEGIN,
    PUBLIC_SKILL_TABLE_END,
    classify_public_export_path,
    render_public_skill_table,
    replace_marked_section,
)
from validate_public_distribution import validate  # noqa: E402


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


class PublicDistributionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        base = Path(self.temp.name)
        self.source = base / "source"
        self.artifact = base / "artifact"
        self.source.mkdir()
        self.artifact.mkdir()
        write_json(
            self.source / "config/skill-distribution.json",
            {"schema_version": 1, "skills": {"core-skill": "core", "private-skill": "non-core"}},
        )
        self._set_artifact_skills(["core-skill"])
        for relative, content in {
            "AGENTS.md": "Public agent guidance.\n",
            "INSTALL.md": "Public installation.\n",
        }.items():
            (self.artifact / relative).write_text(content, encoding="utf-8")
        self._render_readme()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _set_artifact_skills(self, skill_ids: list[str]) -> None:
        write_json(
            self.artifact / "config/skill-distribution.json",
            {"schema_version": 1, "skills": {skill_id: "core" for skill_id in skill_ids}},
        )
        manifest = []
        for skill_id in skill_ids:
            skill_file = self.artifact / ".agents/skills" / skill_id / "SKILL.md"
            skill_file.parent.mkdir(parents=True, exist_ok=True)
            skill_file.write_text(
                f"---\nname: {skill_id}\ndescription: Use when testing {skill_id}.\n---\n\n# {skill_id}\n",
                encoding="utf-8",
            )
            manifest.append({"name": skill_id, "description": f"Use when testing {skill_id}."})
        write_json(self.artifact / "SKILL_MANIFEST.json", {"version": "0.0.0", "skills": manifest})
        plugin = {"skills": [f"./.agents/skills/{skill_id}" for skill_id in skill_ids]}
        write_json(self.artifact / ".codex-plugin/plugin.json", plugin)
        write_json(self.artifact / ".claude-plugin/plugin.json", plugin)

    def _render_readme(self) -> None:
        path = self.artifact / "README.md"
        if not path.exists():
            path.write_text(
                f"# Public fixture\n\n{PUBLIC_SKILL_TABLE_BEGIN}\n{PUBLIC_SKILL_TABLE_END}\n",
                encoding="utf-8",
            )
        current = path.read_text(encoding="utf-8")
        path.write_text(
            replace_marked_section(
                current,
                PUBLIC_SKILL_TABLE_BEGIN,
                PUBLIC_SKILL_TABLE_END,
                render_public_skill_table(self.artifact),
            ),
            encoding="utf-8",
        )

    def _errors(self) -> list[str]:
        return validate(
            self.artifact,
            self.source,
            "WORKTREE",
            check_modes=False,
        )

    def test_closed_fixture_passes(self) -> None:
        self.assertEqual(self._errors(), [])

    def test_private_skill_reference_fails(self) -> None:
        (self.artifact / "AGENTS.md").write_text("Route to private-skill.\n", encoding="utf-8")
        self.assertTrue(any("absent/private Skill ID private-skill" in item for item in self._errors()))

    def test_plugin_manifest_drift_fails(self) -> None:
        write_json(
            self.artifact / ".codex-plugin/plugin.json",
            {"skills": ["./.agents/skills/core-skill", "./.agents/skills/private-skill"]},
        )
        self.assertTrue(any(".codex-plugin/plugin.json does not equal" in item for item in self._errors()))

    def test_missing_operational_file_reference_fails(self) -> None:
        (self.artifact / "INSTALL.md").write_text(
            "Run scripts/does-not-exist.py.\n", encoding="utf-8"
        )
        self.assertTrue(any("references missing file scripts/does-not-exist.py" in item for item in self._errors()))

    def test_runtime_tree_fails(self) -> None:
        runtime = self.artifact / "evals/runtime/case.json"
        runtime.parent.mkdir(parents=True)
        runtime.write_text("{}\n", encoding="utf-8")
        self.assertTrue(any("private-only public path is present: evals/runtime/" in item for item in self._errors()))

    def test_new_core_skill_propagates_through_generated_table(self) -> None:
        write_json(
            self.source / "config/skill-distribution.json",
            {
                "schema_version": 1,
                "skills": {
                    "core-skill": "core",
                    "new-core-skill": "core",
                    "private-skill": "non-core",
                },
            },
        )
        self._set_artifact_skills(["core-skill", "new-core-skill"])
        self._render_readme()
        self.assertEqual(self._errors(), [])
        self.assertIn("| `new-core-skill` |", (self.artifact / "README.md").read_text(encoding="utf-8"))

    def test_unclassified_source_path_is_fail_closed(self) -> None:
        policy = {"public_exact_files": [], "private_exact_files": [], "private_prefixes": []}
        self.assertEqual(
            classify_public_export_path(
                "unexpected/new-file.md", b"new", {"core-skill"}, {"private-skill"}, policy
            ),
            "unclassified",
        )


if __name__ == "__main__":
    unittest.main()
