"""Uji pemasang: python3 -m unittest discover tests"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INSTALLER = ROOT / "scripts" / "install_agent.py"
ALL = ("claude", "codex", "gemini", "opencode", "cursor", "copilot", "generic")

sys.path.insert(0, str(ROOT / "scripts"))
import install_agent  # noqa: E402

try:
    import tomllib
except ImportError:  # Python < 3.11
    tomllib = None


class Installer(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.home, self.proj = base / "home", base / "proj"
        self.home.mkdir()
        self.proj.mkdir()
        self.env = dict(os.environ, HOME=str(self.home))
        self.env.pop("SDD_HOME", None)

    def tearDown(self):
        self.tmp.cleanup()

    def run_installer(self, *args, code=0):
        r = subprocess.run([sys.executable, str(INSTALLER), *args], capture_output=True, text=True, env=self.env)
        self.assertEqual(r.returncode, code, r.stdout + r.stderr)
        return r.stdout

    def install(self, agents, scope="project", code=0, *extra):
        args = ["--agent", agents, "--scope", scope]
        if scope == "project":
            args += ["--target", str(self.proj)]
        return self.run_installer(*args, *extra, code=code)

    def files(self, root):
        return {p for p in root.rglob("*") if p.is_file()}

    def test_every_tool_renders_cleanly_in_project_scope(self):
        self.install(",".join(ALL))
        for p in self.files(self.proj):
            text = p.read_text(encoding="utf-8")
            left = set(re.findall(r"\{\{[A-Z_]+\}\}", text))
            self.assertFalse(left, f"{p}: {left}")
            if p.name == "SKILL.md" or p.parent.name == "agents" and p.suffix == ".md":
                meta, _, _ = install_agent.split_front(text)
                self.assertIn("description", meta, p)
            if p.suffix == ".toml" and tomllib:
                tomllib.loads(text)
        for skills in (".claude", ".agents", ".gemini", ".opencode", ".cursor", ".github", ".sdd"):
            self.assertEqual(len(list((self.proj / skills / "skills").glob("*/SKILL.md"))), 17, skills)
        self.assertTrue((self.proj / ".sdd" / "scripts" / "sdd.py").exists())
        for board in ("github-projects", "jira", "lokal"):
            self.assertTrue((self.proj / ".sdd" / "workflow" / "boards" / f"{board}.md").exists())

    def test_non_claude_skills_drop_claude_only_fields_and_arguments(self):
        self.install("claude,codex")
        claude = (self.proj / ".claude/skills/initiate-epic-ticket/SKILL.md").read_text()
        codex = (self.proj / ".agents/skills/initiate-epic-ticket/SKILL.md").read_text()
        self.assertIn("disable-model-invocation: true", claude)
        self.assertIn("$ARGUMENTS", claude)
        self.assertNotIn("disable-model-invocation", codex)
        self.assertNotIn("$ARGUMENTS", codex)
        self.assertIn("python3 .sdd/scripts/sdd.py", codex)

    def test_shared_instruction_file_gets_one_block_for_all_tools(self):
        (self.proj / "AGENTS.md").write_text("# Aturan tim\n\nPakai bahasa Indonesia.\n")
        self.install("codex")
        self.install("opencode,cursor")
        text = (self.proj / "AGENTS.md").read_text()
        self.assertTrue(text.startswith("# Aturan tim\n\nPakai bahasa Indonesia.\n"))
        self.assertEqual(text.count(install_agent.MARK_START), 1)
        for label in ("OpenAI Codex CLI", "OpenCode", "Cursor"):
            self.assertIn(label, text)

    def test_reinstall_is_idempotent(self):
        self.install("claude,gemini")
        before = {p: p.read_bytes() for p in self.files(self.proj)}
        self.install("claude,gemini")
        after = {p: p.read_bytes() for p in self.files(self.proj)}
        self.assertEqual(before, after)

    def test_foreign_file_is_not_overwritten(self):
        mine = self.proj / ".claude/skills/write-prd/SKILL.md"
        mine.parent.mkdir(parents=True)
        mine.write_text("milik pengguna\n")
        out = self.install("claude", "project", 3)
        self.assertIn("Dilewati", out)
        self.assertEqual(mine.read_text(), "milik pengguna\n")
        self.install("claude", "project", 0, "--force")
        self.assertNotEqual(mine.read_text(), "milik pengguna\n")

    def test_uninstall_keeps_user_content_and_other_tools(self):
        (self.proj / "AGENTS.md").write_text("# Aturan tim\n")
        (self.proj / "sdd.json").write_text("{}\n")
        (self.proj / "docs/epics/x").mkdir(parents=True)
        (self.proj / "docs/epics/x/prd.md").write_text("prd\n")
        self.install("codex,opencode,claude")
        self.run_installer("--uninstall", "--agent", "codex", "--target", str(self.proj))
        agents_md = (self.proj / "AGENTS.md").read_text()
        self.assertIn("`/initiate-epic-ticket", agents_md, "blok OpenCode harus tetap ada")
        self.assertNotIn("$initiate-epic-ticket", agents_md, "petunjuk Codex harus hilang")
        self.assertFalse((self.proj / ".codex").exists())
        self.assertTrue((self.proj / ".opencode/agents/pdm.md").exists())
        self.run_installer("--uninstall", "--target", str(self.proj))
        self.assertEqual((self.proj / "AGENTS.md").read_text(), "# Aturan tim\n")
        self.assertFalse((self.proj / "CLAUDE.md").exists())
        self.assertFalse((self.proj / ".sdd").exists())
        self.assertFalse((self.proj / ".claude").exists())
        self.assertEqual((self.proj / "sdd.json").read_text(), "{}\n", "memory project tidak boleh dihapus")
        self.assertTrue((self.proj / "docs/epics/x/prd.md").exists(), "dokumen pengguna tidak boleh dihapus")

    def test_global_scope_writes_only_under_home(self):
        self.install("claude,codex,gemini,opencode,cursor,copilot", "global")
        self.assertEqual(self.files(self.proj), set())
        core = self.home / ".sdd-agent-workflow"
        self.assertTrue((core / "scripts/sdd.py").exists())
        self.assertTrue((self.home / ".claude/agents/pdm.md").exists())
        self.assertTrue((self.home / ".codex/agents/pdm.toml").exists())
        self.assertTrue((self.home / ".copilot/agents/pdm.agent.md").exists())
        claude_md = (self.home / ".claude/CLAUDE.md").read_text()
        self.assertIn(f"python3 {core}/scripts/sdd.py", claude_md)
        self.assertTrue((core / "instructions/cursor.md").exists(), "Cursor tidak punya berkas aturan global")

    def test_product_designer_is_not_tool_restricted(self):
        self.install("claude,copilot")
        claude = (self.proj / ".claude/agents/product-designer.md").read_text()
        copilot = (self.proj / ".github/agents/product-designer.agent.md").read_text()
        self.assertNotIn("tools:", claude.split("---")[1], "butuh tool MCP platform desain")
        self.assertNotIn("tools:", copilot.split("---")[1])
        self.assertIn("tools:", (self.proj / ".claude/agents/pdm.md").read_text())

    def test_invoke_hint_has_no_project_argument(self):
        self.install("codex")
        text = (self.proj / "AGENTS.md").read_text()
        self.assertIn("$initiate-epic-ticket <kebutuhan>", text)
        self.assertNotIn("<proyek>", text)

    def test_headless_mode_points_to_role_prompts(self):
        self.install("codex", "project", 0, "--role-mode", "headless")
        self.assertFalse((self.proj / ".codex/agents").exists())
        text = (self.proj / "AGENTS.md").read_text()
        self.assertIn("codex exec", text)
        self.assertIn(".sdd/roles/<peran>.md", text)
        role = (self.proj / ".sdd/roles/egm-reviewer.md").read_text()
        self.assertIn(".sdd/skills/egm-review/SKILL.md", role)

    def test_installed_guard_script_runs(self):
        self.install("generic")
        epic = self.proj / "docs/epics/satu"
        r = subprocess.run([sys.executable, str(self.proj / ".sdd/scripts/sdd.py"), "init", str(epic),
                            "--title", "Uji"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_install_sh_non_interactive(self):
        r = subprocess.run(["bash", str(ROOT / "install.sh"), "--agent", "claude,copilot", "--scope", "project",
                            "--target", str(self.proj), "--yes"], capture_output=True, text=True, env=self.env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Langkah berikutnya", r.stdout)
        self.assertTrue((self.proj / ".github/agents/hoe.agent.md").exists())
        r = subprocess.run(["bash", str(ROOT / "install.sh"), "--uninstall", "--scope", "project",
                            "--target", str(self.proj), "--yes"], capture_output=True, text=True, env=self.env)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertFalse((self.proj / ".sdd").exists())

    def test_install_sh_rejects_unknown_tool(self):
        r = subprocess.run(["bash", str(ROOT / "install.sh"), "--agent", "notepad", "--scope", "project",
                            "--target", str(self.proj), "--yes"], capture_output=True, text=True, env=self.env)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("tidak dikenal", r.stderr)


if __name__ == "__main__":
    unittest.main()
