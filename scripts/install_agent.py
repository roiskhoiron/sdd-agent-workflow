#!/usr/bin/env python3
"""Pemasang sdd-agent-workflow untuk berbagai AI coding agent.

Biasanya dipanggil lewat install.sh. Hanya pustaka standar.

Contoh:
  python3 scripts/install_agent.py --agent claude,codex --scope project --target ~/kerja/spesifikasi
  python3 scripts/install_agent.py --agent gemini --scope global
  python3 scripts/install_agent.py --scope project --target . --uninstall
"""
import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MARK_START = "<!-- sdd-agent-workflow:start -->"
MARK_END = "<!-- sdd-agent-workflow:end -->"
MANIFEST = "install-manifest.json"
ROLES = ("pdm", "product-designer", "hoe", "pjm", "egm-reviewer")
ENTRY_SKILLS = ("initiate-epic-ticket", "modify-epic-ticket", "clean-epic-ticket")
INVOKE = "{p}initiate-epic-ticket <kebutuhan>`, `{p}modify-epic-ticket <epic> <perubahan>`, `{p}clean-epic-ticket <epic> <selesai|dibatalkan>"

# ---------------------------------------------------------------------------
# Profil alat. Path diawali "~/" berarti relatif ke HOME, selain itu relatif ke
# folder proyek. None berarti alat tidak punya lokasi itu pada scope tersebut.
#
#   skills      folder Agent Skills (SKILL.md)
#   agents      folder subagent native, beserta format berkasnya
#   instr       berkas instruksi tempat blok aturan disisipkan
#   headless    perintah sekali jalan untuk menjalankan agen peran di proses baru
#   invoke      cara operator memanggil skill pintu masuk
#   skill_meta  kunci frontmatter skill yang boleh dipertahankan
# ---------------------------------------------------------------------------
def _command_files(fmt, folder):
    """Perintah slash yang membuka skill pintu masuk, untuk alat yang skill-nya tidak bisa dipanggil dengan slash."""
    def build(scope, target, ctx):
        out = {}
        for name in ENTRY_SKILLS:
            path = f"{ctx['SKILLS_DIR']}/{name}/SKILL.md"
            desc = _skill_meta(name)["description"]
            if fmt == "gemini-toml":
                body = (f"description = {json.dumps(desc, ensure_ascii=False)}\n"
                        f'prompt = """Baca {path} lalu jalankan isinya sebagai SPV.\n\nMasukan operator: {{{{args}}}}"""\n')
                out[expand(f"{folder[scope]}/{name}.toml", scope, target)] = body
            else:
                body = (front({"description": desc}, ["description"]) +
                        f"\nBaca {path} lalu jalankan isinya sebagai SPV.\n\nMasukan operator: $ARGUMENTS\n")
                out[expand(f"{folder[scope]}/{name}.md", scope, target)] = body
        return out
    return build


TOOLS = {
    "claude": {
        "label": "Claude Code",
        "bin": "claude",
        "skills": {"project": ".claude/skills", "global": "~/.claude/skills"},
        "agents": {"project": ".claude/agents", "global": "~/.claude/agents"},
        "agent_format": "claude",
        "instr": {"project": "CLAUDE.md", "global": "~/.claude/CLAUDE.md"},
        "headless": 'claude -p --permission-mode acceptEdits "<prompt>"',
        "invoke": "Panggil dengan `" + INVOKE.format(p="/") + "`.",
        "skill_meta": ("name", "description", "argument-hint", "disable-model-invocation", "user-invocable"),
        "keeps_arguments": True,
    },
    "codex": {
        "label": "OpenAI Codex CLI",
        "bin": "codex",
        "skills": {"project": ".agents/skills", "global": "~/.agents/skills"},
        "agents": {"project": ".codex/agents", "global": "~/.codex/agents"},
        "agent_format": "codex-toml",
        "instr": {"project": "AGENTS.md", "global": "~/.codex/AGENTS.md"},
        "headless": 'codex exec --sandbox workspace-write "<prompt>"',
        "invoke": "Panggil dengan `" + INVOKE.format(p="$") + "`.",
        "skill_meta": ("name", "description"),
    },
    "gemini": {
        "label": "Gemini CLI",
        "bin": "gemini",
        "skills": {"project": ".gemini/skills", "global": "~/.gemini/skills"},
        "agents": {"project": ".gemini/agents", "global": "~/.gemini/agents"},
        "agent_format": "gemini",
        "instr": {"project": "GEMINI.md", "global": "~/.gemini/GEMINI.md"},
        "headless": 'gemini --approval-mode=auto_edit -p "<prompt>"',
        "invoke": "Panggil dengan `" + INVOKE.format(p="/") + "`.",
        "skill_meta": ("name", "description"),
        "extras": _command_files("gemini-toml", {"project": ".gemini/commands", "global": "~/.gemini/commands"}),
    },
    "opencode": {
        "label": "OpenCode",
        "bin": "opencode",
        "skills": {"project": ".opencode/skills", "global": "~/.config/opencode/skills"},
        "agents": {"project": ".opencode/agents", "global": "~/.config/opencode/agents"},
        "agent_format": "opencode",
        "instr": {"project": "AGENTS.md", "global": "~/.config/opencode/AGENTS.md"},
        "headless": 'opencode run "<prompt>"',
        "invoke": "Panggil dengan `" + INVOKE.format(p="/") + "`.",
        "skill_meta": ("name", "description"),
        "extras": _command_files("md", {"project": ".opencode/commands", "global": "~/.config/opencode/commands"}),
    },
    "cursor": {
        "label": "Cursor (editor dan CLI)",
        "bin": "agent",
        "skills": {"project": ".cursor/skills", "global": "~/.cursor/skills"},
        "agents": {"project": ".cursor/agents", "global": "~/.cursor/agents"},
        "agent_format": "cursor",
        # Aturan global Cursor diatur di UI (User Rules), tidak ada berkas yang terdokumentasi.
        "instr": {"project": "AGENTS.md", "global": None},
        "headless": 'agent -p --force "<prompt>"',
        "invoke": "Panggil dengan `" + INVOKE.format(p="/") + "`.",
        "skill_meta": ("name", "description", "disable-model-invocation"),
    },
    "copilot": {
        "label": "GitHub Copilot (VS Code dan CLI)",
        "bin": "copilot",
        "skills": {"project": ".github/skills", "global": "~/.copilot/skills"},
        "agents": {"project": ".github/agents", "global": "~/.copilot/agents"},
        "agent_format": "copilot",
        "instr": {"project": ".github/copilot-instructions.md", "global": "~/.copilot/copilot-instructions.md"},
        "headless": 'copilot -p "<prompt>" --allow-tool=write --no-ask-user',
        "invoke": "Panggil dengan `" + INVOKE.format(p="/") + "`.",
        "skill_meta": ("name", "description", "argument-hint", "disable-model-invocation", "user-invocable"),
    },
    "generic": {
        "label": "Agen lain (AGENTS.md + .agents/skills)",
        "bin": "",
        "skills": {"project": ".agents/skills", "global": "~/.agents/skills"},
        "agents": {},
        "instr": {"project": "AGENTS.md", "global": "~/.agents/AGENTS.md"},
        "headless": "<perintah sekali jalan alatmu> \"<prompt>\"",
        "invoke": "Minta agen menjalankan skill `initiate-epic-ticket` dengan deskripsi kebutuhan, atau suruh ia membaca berkas SKILL.md-nya.",
        "skill_meta": ("name", "description"),
    },
}

SCOPES = ("project", "global")


class Fail(Exception):
    pass


# ---------- utilitas ----------

def expand(path, scope, target):
    if path.startswith("~/"):
        return Path.home() / path[2:]
    if scope == "global":
        raise Fail(f"path proyek '{path}' dipakai pada scope global")
    return target / path


def split_front(text):
    m = re.match(r"---\n(.*?)\n---\n?(.*)", text, re.S)
    if not m:
        raise Fail("berkas tidak punya front matter")
    meta, order, key = {}, [], None
    for line in m.group(1).splitlines():
        if re.match(r"^\s+- ", line) and key:
            meta[key] = (meta[key] if isinstance(meta[key], list) else []) + [line.split("- ", 1)[1].strip()]
            continue
        k, _, v = line.partition(":")
        key = k.strip()
        v = v.split("  #")[0].strip()
        if len(v) > 1 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        meta[key] = v if v else []
        order.append(key)
    return meta, order, m.group(2)


def yaml_value(v):
    if isinstance(v, list):
        return "\n" + "\n".join(f"  - {x}" for x in v)
    if v in ("true", "false") or v.startswith("[") or re.fullmatch(r"[\w./ -]+", v) and not v.startswith(("-", " ")) and ":" not in v:
        return " " + v
    return " " + json.dumps(v, ensure_ascii=False)


def front(meta, keys):
    lines = ["---"]
    for k in keys:
        if k in meta and meta[k] not in ([], ""):
            lines.append(f"{k}:{yaml_value(meta[k])}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def render(text, ctx):
    for k, v in ctx.items():
        text = text.replace("{{" + k + "}}", v)
    left = re.findall(r"\{\{[A-Z_]+\}\}", text)
    if left:
        raise Fail(f"placeholder tidak terisi: {sorted(set(left))}")
    return text


class Writer:
    """Menulis berkas sambil mencatatnya ke manifest, dan menolak menimpa milik orang lain."""

    def __init__(self, owned, force, dry):
        self.owned, self.force, self.dry = set(owned), force, dry
        self.written, self.skipped = [], []

    def write(self, path, content):
        path = Path(path)
        key = str(path)
        if path.exists() and key not in self.owned and not self.force:
            if path.read_text(encoding="utf-8") != content:
                self.skipped.append(key)
                return
        if not self.dry:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        self.written.append(key)

    def upsert_block(self, path, block):
        """Sisipkan atau ganti blok bertanda di berkas instruksi, tanpa menyentuh isi lain."""
        path = Path(path)
        old = path.read_text(encoding="utf-8") if path.exists() else ""
        pattern = re.compile(re.escape(MARK_START) + r".*?" + re.escape(MARK_END) + r"\n?", re.S)
        if pattern.search(old):
            new = pattern.sub(lambda _: block.rstrip("\n") + "\n", old)
        else:
            new = (old.rstrip("\n") + "\n\n" if old.strip() else "") + block.rstrip("\n") + "\n"
        if not self.dry:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(new, encoding="utf-8")
        self.written.append("block:" + str(path))


def remove_block(path):
    path = Path(path)
    if not path.exists():
        return False
    old = path.read_text(encoding="utf-8")
    pattern = re.compile(r"\n*" + re.escape(MARK_START) + r".*?" + re.escape(MARK_END) + r"\n?", re.S)
    new = pattern.sub("\n", old).strip("\n")
    if new:
        path.write_text(new + "\n", encoding="utf-8")
    else:
        path.unlink()
    return True


# ---------- render per alat ----------

def _skill_meta(name):
    return split_front((REPO / "src" / "skills" / name / "SKILL.md").read_text(encoding="utf-8"))[0]


def skill_text(name, ctx, tool):
    meta, order, body = split_front((REPO / "src" / "skills" / name / "SKILL.md").read_text(encoding="utf-8"))
    keys = [k for k in order if k in tool["skill_meta"]]
    body = render(body.lstrip("\n"), ctx)
    if not tool.get("keeps_arguments"):
        body = body.replace("$ARGUMENTS", "teks yang diberikan operator saat memanggil skill ini")
    return front(meta, keys) + "\n" + body


def role_prompt(role, ctx):
    """Prompt lengkap agen peran untuk mode headless: isi agen ditambah daftar skill yang ia jalankan."""
    meta, _, body = split_front((REPO / "src" / "agents" / f"{role}.md").read_text(encoding="utf-8"))
    skills = meta.get("skills") or []
    lines = [f"# Peran: {role}", "", render(body.strip(), ctx), "", "## Skill yang kamu jalankan", "",
             "Brief menyebut skill mana yang dijalankan. Baca berkasnya sebelum mulai:", ""]
    lines += [f"- `{s}`: `{ctx['SKILLS_DIR']}/{s}/SKILL.md`" for s in skills]
    return "\n".join(lines) + "\n"


def agent_files(tool, ctx):
    """Kembalikan {nama_berkas: isi} untuk subagent native, sesuai format alat."""
    fmt = tool.get("agent_format")
    out = {}
    for role in ROLES:
        meta, order, body = split_front((REPO / "src" / "agents" / f"{role}.md").read_text(encoding="utf-8"))
        body = render(body.strip(), ctx)
        skills = meta.get("skills") or []
        tools = [t.strip() for t in meta["tools"].split(",")]
        unrestricted = tools == ["all"]
        skill_note = "\n\nSkill yang kamu jalankan disebut di brief. Baca berkasnya sebelum mulai:\n" + \
            "\n".join(f"- `{s}`: `{ctx['SKILLS_DIR']}/{s}/SKILL.md`" for s in skills)
        if fmt == "claude":
            names = {"read": "Read", "search": "Glob, Grep", "write": "Write", "edit": "Edit"}
            m = {"name": role, "description": meta["description"], "skills": skills}
            if not unrestricted:
                m["tools"] = ", ".join(names[t] for t in tools)
            if meta.get("isolated") == "true":
                m["omitClaudeMd"] = "true"
            out[f"{role}.md"] = front(m, ["name", "description", "tools", "omitClaudeMd", "skills"]) + "\n" + body + "\n"
        elif fmt == "codex-toml":
            # Codex tidak punya daftar tool per agen. Batasan ditulis di instruksi.
            text = (f"name = {json.dumps(role)}\n"
                    f"description = {json.dumps(meta['description'], ensure_ascii=False)}\n"
                    "developer_instructions = \'\'\'\n" + (body + skill_note).replace("\'\'\'", "") + "\n\'\'\'\n")
            out[f"{role}.toml"] = text
        elif fmt == "gemini":
            # Tanpa kunci tools: agen memakai tool induk. Nama tool Gemini tidak ditebak di sini.
            out[f"{role}.md"] = front({"name": role, "description": meta["description"]},
                                      ["name", "description"]) + "\n" + body + skill_note + "\n"
        elif fmt == "cursor":
            # Cursor tidak punya daftar tool per agen. Reviewer tetap butuh menulis berkas hasil review.
            out[f"{role}.md"] = front({"name": role, "description": meta["description"]},
                                      ["name", "description"]) + "\n" + body + skill_note + "\n"
        elif fmt == "copilot":
            names = {"read": "read", "search": "search", "write": "edit", "edit": "edit"}
            m = {"name": role, "description": meta["description"]}
            if not unrestricted:
                m["tools"] = "[" + ", ".join(json.dumps(t) for t in dict.fromkeys(names[t] for t in tools)) + "]"
            out[f"{role}.agent.md"] = front(m, ["name", "description", "tools"]) + "\n" + body + skill_note + "\n"
        elif fmt == "opencode":
            out[f"{role}.md"] = front({"description": meta["description"], "mode": "subagent"},
                                      ["description", "mode"]) + "\n" + body + skill_note + "\n"
        else:
            raise Fail(f"format agen tidak dikenal: {fmt}")
    return out


def role_runner(tool, mode, ctx):
    if mode == "native":
        return (
            "Jalankan agen peran sebagai subagent native dengan nama yang sama, dan berikan brief sebagai "
            "tugasnya. Selalu mulai subagent baru: jangan melanjutkan percakapan subagent sebelumnya, "
            "terutama untuk `egm-reviewer`."
        )
    return (
        "Jalankan agen peran sebagai proses baru supaya konteksnya terpisah:\n\n"
        "1. Tulis brief ke `<epic>/_briefs/<peran>-<NN>.md`, NN nomor urut dua digit.\n"
        f"2. Jalankan di terminal dan tunggu sampai selesai: `{tool['headless']}`, dengan `<prompt>` berisi "
        f"`Baca {ctx['SDD_HOME']}/roles/<peran>.md lalu kerjakan brief di <epic>/_briefs/<peran>-<NN>.md`.\n"
        "3. Baca keluarannya, lalu periksa berkas yang seharusnya ditulis peran itu.\n\n"
        "Jika perintah itu tidak bisa dijalankan dari alatmu, minta operator menjalankannya di terminal lain."
    )


def instruction_block(names, modes, ctx):
    """Satu blok untuk satu berkas instruksi, memuat petunjuk semua alat yang membaca berkas itu."""
    if len(names) == 1:
        tool = TOOLS[names[0]]
        invoke, runner = tool["invoke"], role_runner(tool, modes[names[0]], ctx)
    else:
        invoke = "Cara memanggilnya tergantung alat:\n\n" + "\n".join(
            f"  - {TOOLS[n]['label']}: {TOOLS[n]['invoke']}" for n in names) + "\n\n "
        runner = "\n\n".join(f"**{TOOLS[n]['label']}.** {role_runner(TOOLS[n], modes[n], ctx)}" for n in names)
    return render((REPO / "src" / "instructions.md").read_text(encoding="utf-8"),
                  dict(ctx, INVOKE_HINT=invoke, ROLE_RUNNER=runner))


def instruction_path(name, scope, target, home):
    path = TOOLS[name]["instr"].get(scope)
    if path is None:
        return home / "instructions" / f"{name}.md"
    return expand(path, scope, target)


def write_blocks(manifest, w, ctx):
    groups = {}
    for name, info in manifest["tools"].items():
        groups.setdefault(info["instructions"], []).append(name)
    for path, names in groups.items():
        modes = {n: manifest["tools"][n]["mode"] for n in names}
        w.upsert_block(path, instruction_block(sorted(names, key=list(TOOLS).index), modes, ctx))


# ---------- pasang dan copot ----------

def sdd_home(scope, target, override):
    if override:
        return Path(override).expanduser().resolve()
    if scope == "project":
        return target / ".sdd"
    return Path(os.environ.get("SDD_HOME", "~/.sdd-agent-workflow")).expanduser()


def home_ref(scope, home, target):
    """Path SDD_HOME seperti yang ditulis di dokumen: relatif untuk proyek supaya bisa di-commit."""
    if scope == "project":
        try:
            return home.relative_to(target).as_posix()
        except ValueError:
            return str(home)
    return str(home)


def load_manifest(home):
    path = home / MANIFEST
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"tools": {}, "core": []}


def install(args):
    target = Path(args.target).expanduser().resolve()
    home = sdd_home(args.scope, target, args.sdd_home)
    ref = home_ref(args.scope, home, target)
    manifest = load_manifest(home)
    owned = set(manifest["core"]) | {f for t in manifest["tools"].values() for f in t["files"]}
    w = Writer(owned, args.force, args.dry_run)
    ctx = {"SDD_HOME": ref, "SKILLS_DIR": f"{ref}/skills"}

    # 1. Inti workflow: skrip, dokumen workflow, salinan skill, prompt peran.
    w.write(home / "scripts" / "sdd.py", (REPO / "scripts" / "sdd.py").read_text(encoding="utf-8"))
    for src in sorted((REPO / "workflow").rglob("*")):
        if src.is_file():
            text = src.read_text(encoding="utf-8")
            w.write(home / "workflow" / src.relative_to(REPO / "workflow"),
                    render(text, ctx) if src.suffix == ".md" else text)
    neutral = {"skill_meta": ("name", "description")}
    for skill in sorted(p.name for p in (REPO / "src" / "skills").iterdir()):
        w.write(home / "skills" / skill / "SKILL.md", skill_text(skill, ctx, neutral))
    for role in ROLES:
        w.write(home / "roles" / f"{role}.md", role_prompt(role, ctx))
    core = list(w.written)
    manifest["core"] = sorted(set(manifest["core"]) | set(core))

    # 2. Adapter per alat.
    for name in args.agent:
        tool = TOOLS[name]
        before = len(w.written)
        skills_dir = tool["skills"].get(args.scope)
        if skills_dir:
            base = expand(skills_dir, args.scope, target)
            tctx = dict(ctx, SKILLS_DIR=str(base) if args.scope == "global" else skills_dir)
            for skill in sorted(p.name for p in (REPO / "src" / "skills").iterdir()):
                w.write(base / skill / "SKILL.md", skill_text(skill, tctx, tool))
        else:
            tctx = ctx
        mode = args.role_mode or ("native" if tool.get("agents", {}).get(args.scope) else "headless")
        if args.headless_cmd:
            tool["headless"] = args.headless_cmd
        if mode == "native":
            if not tool.get("agents", {}).get(args.scope):
                raise Fail(f"{tool['label']} tidak punya subagent native pada scope {args.scope}")
            base = expand(tool["agents"][args.scope], args.scope, target)
            for fname, content in agent_files(tool, tctx).items():
                w.write(base / fname, content)
        for extra in tool.get("extras", lambda *_: {})(args.scope, target, tctx).items():
            w.write(*extra)
        instr = instruction_path(name, args.scope, target, home)
        files = [f for f in w.written[before:] if not f.startswith("block:")]
        prev = manifest["tools"].get(name, {})
        manifest["tools"][name] = {
            "scope": args.scope, "mode": mode, "instructions": str(instr),
            "files": sorted(set(prev.get("files", [])) | set(files)),
        }

    manifest["scope"] = args.scope
    manifest["target"] = str(target)
    write_blocks(manifest, w, ctx)
    if not args.dry_run:
        home.mkdir(parents=True, exist_ok=True)
        (home / MANIFEST).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    report(args, home, w, manifest)
    return 0 if not w.skipped else 3


def uninstall(args):
    target = Path(args.target).expanduser().resolve()
    home = sdd_home(args.scope, target, args.sdd_home)
    manifest = load_manifest(home)
    names = args.agent or list(manifest["tools"])
    removed = 0
    for name in names:
        info = manifest["tools"].pop(name, None)
        if not info:
            print(f"  {name}: tidak terpasang di {home}")
            continue
        for f in info["files"]:
            p = Path(f)
            if p.exists():
                p.unlink()
                removed += 1
                for parent in p.parents:
                    if parent == Path.home() or parent == target or not parent.exists() or any(parent.iterdir()):
                        break
                    parent.rmdir()
        if not any(t["instructions"] == info["instructions"] for t in manifest["tools"].values()):
            remove_block(info["instructions"])
        print(f"  {TOOLS.get(name, {}).get('label', name)}: dicopot")
    if manifest["tools"]:
        ref = home_ref(args.scope, home, target)
        write_blocks(manifest, Writer((), True, False), {"SDD_HOME": ref, "SKILLS_DIR": f"{ref}/skills"})
    if not manifest["tools"]:
        shutil.rmtree(home, ignore_errors=True)
        print(f"  inti workflow di {home} dihapus")
    else:
        (home / MANIFEST).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"selesai, {removed} berkas adapter dihapus. sdd.json dan docs/ tidak disentuh.")
    return 0


def report(args, home, w, manifest):
    verb = "akan ditulis" if args.dry_run else "ditulis"
    print(f"\nInti workflow: {home}")
    for name in args.agent:
        info = manifest["tools"][name]
        print(f"  {TOOLS[name]['label']}: {len(info['files'])} berkas, agen peran mode {info['mode']}, "
              f"instruksi di {info['instructions']}")
    print(f"{len(w.written)} berkas {verb}.")
    for name in args.agent:
        if TOOLS[name]["instr"].get(args.scope) is None:
            print(f"\nCatatan {TOOLS[name]['label']}: alat ini tidak punya berkas instruksi global. Salin isi "
                  f"{manifest['tools'][name]['instructions']} ke pengaturan aturan pengguna di alat itu.")
    if w.skipped:
        print("\nDilewati karena sudah ada dan bukan milik pemasang ini (pakai --force untuk menimpa):")
        for f in w.skipped:
            print("  " + f)


def parse(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--agent", default="", help="satu atau lebih, dipisah koma: " + ", ".join(TOOLS))
    ap.add_argument("--scope", choices=SCOPES, default="project")
    ap.add_argument("--target", default=".", help="folder proyek untuk scope project (default: folder sekarang)")
    ap.add_argument("--sdd-home", help="lokasi inti workflow (default: <target>/.sdd atau ~/.sdd-agent-workflow)")
    ap.add_argument("--role-mode", choices=("native", "headless"),
                    help="cara menjalankan agen peran (default: native bila alat mendukung)")
    ap.add_argument("--headless-cmd", help="perintah sekali jalan alatmu, dengan <prompt> sebagai tempat prompt")
    ap.add_argument("--force", action="store_true", help="timpa berkas yang sudah ada")
    ap.add_argument("--dry-run", action="store_true", help="tampilkan rencana tanpa menulis")
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--list-agents", action="store_true", help="cetak daftar alat yang didukung")
    args = ap.parse_args(argv)
    args.agent = [a.strip() for a in args.agent.split(",") if a.strip()]
    unknown = [a for a in args.agent if a not in TOOLS]
    if unknown:
        ap.error(f"alat tidak dikenal: {', '.join(unknown)}. Pilihan: {', '.join(TOOLS)}")
    return args


def main(argv=None):
    args = parse(argv)
    if args.list_agents:
        for key, tool in TOOLS.items():
            print(f"{key}\t{tool['label']}\t{tool.get('bin', '')}")
        return 0
    try:
        if args.uninstall:
            return uninstall(args)
        if not args.agent:
            raise Fail("pilih minimal satu alat dengan --agent")
        return install(args)
    except Fail as e:
        print(f"gagal: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
