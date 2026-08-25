import json
import sys
import tempfile
import unittest
from pathlib import Path

from install_skill_hooks import hook_command, install_one_hook, skill_is_installed


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = (
    ROOT
    / ".agents"
    / "skills"
    / "coding-agent-git-discipline"
    / "hooks"
    / "shared-checkout-guard"
    / "manifest.json"
)
RELEASE_MANIFEST_PATH = (
    ROOT
    / ".agents"
    / "skills"
    / "coding-agent-git-discipline"
    / "hooks"
    / "release-cut-reminder"
    / "manifest.json"
)
AUTH_MANIFEST_PATH = (
    ROOT
    / ".agents"
    / "skills"
    / "coding-agent-git-discipline"
    / "hooks"
    / "block-push-auth-loop"
    / "manifest.json"
)
RECORD_MANIFEST_PATH = (
    ROOT
    / ".agents"
    / "skills"
    / "coding-agent-git-discipline"
    / "hooks"
    / "record-push-outcome"
    / "manifest.json"
)
IDENTITY_MANIFEST_PATH = (
    ROOT
    / ".agents"
    / "skills"
    / "coding-agent-project-governance"
    / "hooks"
    / "identity-leak-backstop"
    / "manifest.json"
)
LIFECYCLE_MANIFEST_PATH = (
    ROOT
    / ".agents"
    / "skills"
    / "coding-agent-project-governance"
    / "hooks"
    / "lifecycle-evidence-reminder"
    / "manifest.json"
)
HTML_MANIFEST_PATH = (
    ROOT
    / ".agents"
    / "skills"
    / "document-governance"
    / "hooks"
    / "html-view-sync-reminder"
    / "manifest.json"
)
ART_MANIFEST_PATH = (
    ROOT
    / ".agents"
    / "skills"
    / "game-art-pipeline"
    / "hooks"
    / "art-draft-catalog"
    / "manifest.json"
)
VIKUNJA_MANIFEST_PATH = (
    ROOT
    / ".agents"
    / "skills"
    / "project-management-sync"
    / "hooks"
    / "vikunja-sync-reminder"
    / "manifest.json"
)


class InstallSkillHooksTests(unittest.TestCase):
    def load_manifest(self, manifest_path=MANIFEST_PATH):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["_hook_dir"] = manifest_path.parent
        return manifest

    def test_mac_style_command_remains_bash(self):
        self.assertEqual(
            hook_command(
                "codex", "coding-agent-git-discipline", "shared-checkout-guard", windows=False
            ),
            "bash .codex/hooks/coding-agent-git-discipline/shared-checkout-guard/script.sh",
        )

    def test_codex_plugin_cache_counts_as_installed_skill(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            home = root / "home"
            plugin_skill = (
                home
                / ".codex"
                / "plugins"
                / "cache"
                / "marketplace"
                / "plugin"
                / "7.6.39"
                / ".agents"
                / "skills"
                / "demo-skill"
            )
            plugin_skill.mkdir(parents=True)
            (plugin_skill / "SKILL.md").write_text("---\nname: demo-skill\n---\n", encoding="utf-8")

            self.assertTrue(skill_is_installed("demo-skill", root / "project", user_home=home))
            self.assertFalse(skill_is_installed("missing-skill", root / "project", user_home=home))

    def test_windows_install_migrates_legacy_bash_wiring(self):
        manifest = self.load_manifest()
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            config_path = project / ".codex" / "hooks.json"
            config_path.parent.mkdir(parents=True)
            config_path.write_text(
                json.dumps(
                    {
                        "hooks": {
                            "PreToolUse": [
                                {
                                    "matcher": "Bash",
                                    "hooks": [
                                        {
                                            "type": "command",
                                            "command": "bash .codex/hooks/coding-agent-git-discipline/shared-checkout-guard/script.sh",
                                            "timeout": 15,
                                        }
                                    ],
                                }
                            ]
                        }
                    }
                ),
                encoding="utf-8",
            )

            original_platform = sys.platform
            try:
                sys.platform = "win32"
                actions = install_one_hook(manifest, project, ["codex"], dry_run=False)
            finally:
                sys.platform = original_platform

            config = json.loads(config_path.read_text(encoding="utf-8"))
            installed_command = config["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
            self.assertEqual(
                installed_command,
                "powershell.exe -NoProfile -ExecutionPolicy Bypass -File "
                ".codex/hooks/coding-agent-git-discipline/shared-checkout-guard/script.ps1",
            )
            self.assertTrue(
                (
                    project
                    / ".codex"
                    / "hooks"
                    / "coding-agent-git-discipline"
                    / "shared-checkout-guard"
                    / "script.ps1"
                ).read_text(encoding="utf-8").startswith("param()")
            )
            self.assertTrue(any(action.startswith("installed codex:") for action in actions))

    def test_windows_release_reminder_copies_native_script(self):
        manifest = self.load_manifest(RELEASE_MANIFEST_PATH)
        with tempfile.TemporaryDirectory() as temp_dir:
            original_platform = sys.platform
            try:
                sys.platform = "win32"
                actions = install_one_hook(manifest, Path(temp_dir), ["codex"], dry_run=False)
            finally:
                sys.platform = original_platform

            installed = (
                Path(temp_dir)
                / ".codex"
                / "hooks"
                / "coding-agent-git-discipline"
                / "release-cut-reminder"
                / "script.ps1"
            )
            self.assertTrue(installed.read_text(encoding="utf-8").startswith("param()"))
            self.assertTrue(any(action.startswith("installed codex:") for action in actions))

    def test_windows_auth_loop_copies_native_script(self):
        manifest = self.load_manifest(AUTH_MANIFEST_PATH)
        with tempfile.TemporaryDirectory() as temp_dir:
            original_platform = sys.platform
            try:
                sys.platform = "win32"
                actions = install_one_hook(manifest, Path(temp_dir), ["codex"], dry_run=False)
            finally:
                sys.platform = original_platform

            installed = (
                Path(temp_dir)
                / ".codex"
                / "hooks"
                / "coding-agent-git-discipline"
                / "block-push-auth-loop"
                / "script.ps1"
            )
            content = installed.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("param()"))
            self.assertIn("exit 2", content)
            self.assertTrue(any(action.startswith("installed codex:") for action in actions))

    def test_windows_record_outcome_copies_native_script(self):
        manifest = self.load_manifest(RECORD_MANIFEST_PATH)
        with tempfile.TemporaryDirectory() as temp_dir:
            original_platform = sys.platform
            try:
                sys.platform = "win32"
                actions = install_one_hook(manifest, Path(temp_dir), ["codex"], dry_run=False)
            finally:
                sys.platform = original_platform

            installed = (
                Path(temp_dir)
                / ".codex"
                / "hooks"
                / "coding-agent-git-discipline"
                / "record-push-outcome"
                / "script.ps1"
            )
            content = installed.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("param()"))
            self.assertIn("exit 0", content)
            self.assertTrue(any(action.startswith("installed codex:") for action in actions))

    def test_windows_identity_backstop_copies_native_script(self):
        manifest = self.load_manifest(IDENTITY_MANIFEST_PATH)
        with tempfile.TemporaryDirectory() as temp_dir:
            original_platform = sys.platform
            try:
                sys.platform = "win32"
                actions = install_one_hook(manifest, Path(temp_dir), ["codex"], dry_run=False)
            finally:
                sys.platform = original_platform

            installed = (
                Path(temp_dir)
                / ".codex"
                / "hooks"
                / "coding-agent-project-governance"
                / "identity-leak-backstop"
                / "script.ps1"
            )
            content = installed.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("param()"))
            self.assertIn("exit 2", content)
            self.assertTrue(any(action.startswith("installed codex:") for action in actions))

    def test_windows_lifecycle_reminder_copies_native_script(self):
        manifest = self.load_manifest(LIFECYCLE_MANIFEST_PATH)
        with tempfile.TemporaryDirectory() as temp_dir:
            original_platform = sys.platform
            try:
                sys.platform = "win32"
                actions = install_one_hook(manifest, Path(temp_dir), ["codex"], dry_run=False)
            finally:
                sys.platform = original_platform

            installed = (
                Path(temp_dir)
                / ".codex"
                / "hooks"
                / "coding-agent-project-governance"
                / "lifecycle-evidence-reminder"
                / "script.ps1"
            )
            content = installed.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("param()"))
            self.assertIn("exit 0", content)
            self.assertTrue(any(action.startswith("installed codex:") for action in actions))

    def test_windows_html_view_reminder_copies_native_script(self):
        manifest = self.load_manifest(HTML_MANIFEST_PATH)
        with tempfile.TemporaryDirectory() as temp_dir:
            original_platform = sys.platform
            try:
                sys.platform = "win32"
                actions = install_one_hook(manifest, Path(temp_dir), ["codex"], dry_run=False)
            finally:
                sys.platform = original_platform

            installed = (
                Path(temp_dir)
                / ".codex"
                / "hooks"
                / "document-governance"
                / "html-view-sync-reminder"
                / "script.ps1"
            )
            content = installed.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("param()"))
            self.assertIn("exit 0", content)
            self.assertTrue(any(action.startswith("installed codex:") for action in actions))

    def test_windows_art_draft_catalog_copies_native_script(self):
        manifest = self.load_manifest(ART_MANIFEST_PATH)
        with tempfile.TemporaryDirectory() as temp_dir:
            original_platform = sys.platform
            try:
                sys.platform = "win32"
                actions = install_one_hook(manifest, Path(temp_dir), ["codex"], dry_run=False)
            finally:
                sys.platform = original_platform

            installed = (
                Path(temp_dir)
                / ".codex"
                / "hooks"
                / "game-art-pipeline"
                / "art-draft-catalog"
                / "script.ps1"
            )
            content = installed.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("param()"))
            self.assertIn("DRAFT-GOVERNANCE", content)
            self.assertIn("exit 2", content)
            self.assertTrue(any(action.startswith("installed codex:") for action in actions))

    def test_windows_vikunja_reminder_copies_native_script(self):
        manifest = self.load_manifest(VIKUNJA_MANIFEST_PATH)
        with tempfile.TemporaryDirectory() as temp_dir:
            original_platform = sys.platform
            try:
                sys.platform = "win32"
                actions = install_one_hook(manifest, Path(temp_dir), ["codex"], dry_run=False)
            finally:
                sys.platform = original_platform

            installed = (
                Path(temp_dir)
                / ".codex"
                / "hooks"
                / "project-management-sync"
                / "vikunja-sync-reminder"
                / "script.ps1"
            )
            content = installed.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("param()"))
            self.assertIn("stop_hook_active", content)
            self.assertIn("exit 2", content)
            self.assertTrue(any(action.startswith("installed codex:") for action in actions))


if __name__ == "__main__":
    unittest.main()
