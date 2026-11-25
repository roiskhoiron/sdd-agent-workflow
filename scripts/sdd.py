#!/usr/bin/env python3
"""Penjaga aturan workflow produksi tiket.

Skrip ini memegang aturan yang tidak boleh bergantung pada ingatan agen:
status gate EGM, batas revisi, keputusan manusia atas temuan, persetujuan
akhir, dan daftar tiket yang boleh dikirim ke Jira. Hanya pustaka standar.

Pemakaian: python3 scripts/sdd.py <perintah> <folder-epic> [opsi]
"""
import argparse
import datetime
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

SIZES = ("kecil", "sedang", "besar")
GATES = ("prd", "flow", "contract", "tickets")
GATES_BY_SIZE = {"kecil": ("tickets",), "sedang": GATES, "besar": GATES}
GATE_FILES = {
    "prd": ("prd.md",),
    "flow": ("flow.md",),
    "contract": ("contract", "specs"),
    "tickets": ("tickets",),
}
MAX_ROUNDS = 3  # satu review awal ditambah dua revisi
RESPONSES = ("diperbaiki", "ditolak", "diteruskan")
FINDING_TYPES = ("tidak-jelas", "bertentangan", "hilang")
# Berkas status tidak ikut di-hash: isinya berubah justru karena persetujuan dan push.
UNHASHED = {"epic.json", "approval.json", "jira-map.json", "jira-snapshot.json"}
MOBILE_SECTIONS = (
    "Tujuan", "Ruang lingkup", "Layar dan flow", "API contract", "Aturan sisi klien",
    "Keamanan sisi klien", "Acceptance criteria", "Rujukan Foundation", "Ketergantungan",
)
ALWAYS_FILLED = {1, 2, 7}  # bagian lain boleh 'Tidak ada', tetapi tidak boleh kosong
JIRA_KEY = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")


class Fail(Exception):
    pass


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def load(path, default=None):
    if not path.exists():
        if default is not None:
            return default
        raise Fail(f"berkas tidak ditemukan: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise Fail(f"JSON rusak di {path}: {e}")


def save(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def epic_state(epic):
    return load(epic / "epic.json")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hash_tree(epic, roots=None):
    """Hash setiap berkas isi epic. `roots` membatasi ke berkas atau folder tertentu."""
    out = {}
    for p in sorted(epic.rglob("*")):
        rel = p.relative_to(epic)
        if not p.is_file() or rel.parts[0] == "_history" or rel.as_posix() in UNHASHED:
            continue
        if roots is not None and rel.parts[0] not in roots:
            continue
        out[rel.as_posix()] = sha(p)
    return out


# ---------- gate ----------

def rounds(epic, gate):
    found = []
    for p in (epic / "reviews").glob(f"{gate}-r*.json"):
        m = re.fullmatch(rf"{gate}-r(\d+)\.json", p.name)
        if m:
            found.append((int(m.group(1)), p))
    return sorted(found)


def findings_of(path, gate, n):
    data = load(path)
    items = data.get("findings")
    if not isinstance(items, list):
        raise Fail(f"{path}: 'findings' harus berupa daftar")
    for i, f in enumerate(items, 1):
        f.setdefault("id", f"{gate}-r{n}-{i}")
        if f.get("type") not in FINDING_TYPES:
            raise Fail(f"{path}: temuan {f['id']} butuh 'type' salah satu dari {FINDING_TYPES}")
        if not str(f.get("text", "")).strip():
            raise Fail(f"{path}: temuan {f['id']} tidak punya 'text'")
        r = f.get("response")
        if r is not None:
            if r.get("status") not in RESPONSES:
                raise Fail(f"{path}: jawaban {f['id']} butuh 'status' salah satu dari {RESPONSES}")
            if r["status"] != "diperbaiki" and not str(r.get("note", "")).strip():
                raise Fail(f"{path}: jawaban {f['id']} berstatus {r['status']} wajib punya 'note'")
    return items


def gate_status(epic, gate, state=None):
    """Kembalikan (status, temuan putaran terakhir).

    belum-direview  belum ada putaran review
    perlu-jawaban   ada temuan yang belum dijawab penulis
    perlu-review-ulang  ada temuan berstatus diperbaiki, butuh putaran baru
    berhenti        masih ada temuan setelah dua revisi, serahkan ke manusia
    usang           dokumen berubah sejak gate lolos
    lolos           tidak ada temuan, atau sisanya ditolak/diteruskan untuk diputuskan manusia
    """
    state = state or epic_state(epic)
    rs = rounds(epic, gate)
    if not rs:
        return "belum-direview", []
    n, path = rs[-1]
    items = findings_of(path, gate, n)
    if items and n >= MAX_ROUNDS:
        return "berhenti", items
    if any(f.get("response") is None for f in items):
        return "perlu-jawaban", items
    if any(f["response"]["status"] == "diperbaiki" for f in items):
        return "perlu-review-ulang", items
    seal = state.get("gate_seals", {}).get(gate)
    if seal is not None and seal != hash_tree(epic, GATE_FILES[gate]):
        return "usang", items
    return "lolos", items


def required_gates(state):
    size = state.get("size")
    if size not in SIZES:
        raise Fail("ukuran epic belum ditetapkan, jalankan set-size")
    return GATES_BY_SIZE[size]


def carried_findings(epic, state):
    """Temuan yang tidak diperbaiki (ditolak atau diteruskan): wajib diputuskan manusia."""
    out = []
    for gate in required_gates(state):
        status, items = gate_status(epic, gate, state)
        if status == "lolos":
            out += [f for f in items if f["response"]["status"] != "diperbaiki"]
    return out


def cmd_gate(epic, args):
    state = epic_state(epic)
    status, items = gate_status(epic, args.gate, state)
    if status == "lolos" and args.gate not in state.get("gate_seals", {}):
        state.setdefault("gate_seals", {})[args.gate] = hash_tree(epic, GATE_FILES[args.gate])
        save(epic / "epic.json", state)
    n = len(rounds(epic, args.gate))
    print(f"gate {args.gate}: {status} (putaran {n} dari maksimal {MAX_ROUNDS})")
    for f in items:
        r = f.get("response")
        print(f"  {f['id']} [{f['type']}] {r['status'] if r else 'BELUM DIJAWAB'}: {f['text']}")
    return 0 if status == "lolos" else 1


def cmd_reopen(epic, args):
    """Arsipkan putaran review sebuah gate supaya dokumen yang berubah direview dari awal."""
    state = epic_state(epic)
    rs = rounds(epic, args.gate)
    dest = epic / "_history" / "reviews" / now().replace(":", "")
    for _, p in rs:
        dest.mkdir(parents=True, exist_ok=True)
        shutil.move(str(p), str(dest / p.name))
    state.get("gate_seals", {}).pop(args.gate, None)
    for f in [k for k in state.get("decisions", {}) if k.startswith(args.gate + "-r")]:
        del state["decisions"][f]
    save(epic / "epic.json", state)
    print(f"gate {args.gate} dibuka ulang, {len(rs)} putaran diarsipkan")
    return 0


# ---------- tiket ----------

def parse_ticket(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        raise Fail(f"{path.name}: tidak punya front matter '---'")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.split("#")[0].strip()
    return meta, m.group(2)


def is_none(value):
    return value.strip().strip(".").lower() in ("", "tidak ada")


def blockers(meta):
    raw = meta.get("blocked_by", "")
    return [] if is_none(raw) else [b.strip() for b in raw.strip("[]").split(",") if b.strip()]


def lint_ticket(path, tickets, manifest, errors):
    meta, body = parse_ticket(path)
    err = lambda msg: errors.append(f"{path.name}: {msg}")
    kind, size = meta.get("kind"), meta.get("size")
    if kind not in ("role", "contract"):
        err("'kind' harus role atau contract")
    if size not in SIZES:
        err(f"'size' harus salah satu dari {SIZES}")
    for b in blockers(meta):
        if b not in tickets and not JIRA_KEY.match(b):
            err(f"blocked_by '{b}' bukan berkas tiket di epic ini dan bukan kode Jira")
    if not re.search(r"^# \S", body, re.M):
        err("tidak punya judul '# ...'")
    if kind != "role":
        return
    version = meta.get("contract_version", "")
    if not is_none(version):
        if manifest is None:
            err("mencatat contract_version tetapi contract/contract.json tidak ada")
        elif version != manifest.get("version"):
            err(f"contract_version {version} tidak cocok dengan contract {manifest.get('version')}")
        elif manifest.get("changed") and not any(
            parse_ticket(tickets[b])[0].get("kind") == "contract" for b in blockers(meta) if b in tickets
        ):
            err("contract berubah di epic ini, tiket wajib blocked_by tiket contract")
    if meta.get("role") != "mobile":
        err("baru role mobile yang punya template, role lain ditulis sebagai catatan lintas role")
        return
    parts = re.split(r"^## (\d+)\. (.+)$", body, flags=re.M)
    heads = [(int(parts[i]), parts[i + 1].strip(), parts[i + 2].strip()) for i in range(1, len(parts), 3)]
    if [h[1] for h in heads] != list(MOBILE_SECTIONS):
        err("bagian harus persis sembilan dan berurutan: " + ", ".join(MOBILE_SECTIONS))
        return
    for num, title, content in heads:
        if not content or re.search(r"(^|\s)\.\.\.($|\s)|\[(tautan|KODE)", content):
            err(f"bagian {num} ({title}) kosong atau masih berisi placeholder template")
        elif is_none(content) and num in ALWAYS_FILLED:
            err(f"bagian {num} ({title}) tidak boleh 'Tidak ada'")
    if not re.search(r"^- \[ \] .*\S", heads[6][2], re.M):
        err("bagian 7 butuh minimal satu acceptance criteria berbentuk '- [ ] Given ... When ... Then ...'")
    if is_none(version) and not is_none(heads[3][2]):
        err("bagian 4 menyebut contract tetapi contract_version kosong")


def ticket_files(epic):
    return {p.stem: p for p in sorted((epic / "tickets").glob("*.md")) if not p.name.startswith("_")}


def lint(epic):
    tickets = ticket_files(epic)
    errors = []
    if not tickets:
        errors.append("folder tickets/ belum berisi tiket")
    manifest_path = epic / "contract" / "contract.json"
    manifest = load(manifest_path) if manifest_path.exists() else None
    for path in tickets.values():
        try:
            lint_ticket(path, tickets, manifest, errors)
        except Fail as e:
            errors.append(str(e))
    return errors


def cmd_lint(epic, args):
    errors = lint(epic)
    for e in errors:
        print("  " + e)
    print("lint: " + ("bersih" if not errors else f"{len(errors)} masalah"))
    return 1 if errors else 0


# ---------- persetujuan ----------

def contract_changed(epic):
    path = epic / "contract" / "contract.json"
    return path.exists() and bool(load(path).get("changed"))


def contract_approved(epic, state):
    seal = state.get("contract_approval")
    return bool(seal) and seal["hashes"] == hash_tree(epic, ("contract",))


def blocking_reasons(epic, state):
    reasons = []
    for gate in required_gates(state):
        status, _ = gate_status(epic, gate, state)
        if status != "lolos":
            reasons.append(f"gate {gate} berstatus {status}")
    if reasons:
        return reasons
    decisions = state.get("decisions", {})
    for f in carried_findings(epic, state):
        d = decisions.get(f["id"])
        if d is None:
            reasons.append(f"temuan {f['id']} belum diputuskan manusia")
        elif d["decision"] != "terima":
            reasons.append(f"temuan {f['id']} diputuskan '{d['decision']}', harus direvisi dulu")
    if contract_changed(epic) and not contract_approved(epic, state):
        reasons.append("contract berubah dan belum disetujui pemilik contract (approve-contract)")
    return reasons + lint(epic)


def cmd_decide(epic, args):
    state = epic_state(epic)
    ids = {f["id"] for f in carried_findings(epic, state)}
    if args.finding not in ids:
        raise Fail(f"{args.finding} bukan temuan terbawa. Yang ada: {sorted(ids) or 'tidak ada'}")
    state.setdefault("decisions", {})[args.finding] = {
        "decision": args.decision, "by": args.by, "note": args.note, "at": now()}
    save(epic / "epic.json", state)
    print(f"{args.finding}: {args.decision} oleh {args.by}")
    return 0


def cmd_approve_contract(epic, args):
    state = epic_state(epic)
    status, _ = gate_status(epic, "contract", state)
    if status != "lolos":
        raise Fail(f"gate contract berstatus {status}, belum bisa disetujui")
    state["contract_approval"] = {"by": args.by, "at": now(), "hashes": hash_tree(epic, ("contract",))}
    save(epic / "epic.json", state)
    print(f"contract disetujui oleh {args.by}")
    return 0


def cmd_approve(epic, args):
    state = epic_state(epic)
    # Pembersihan epic tidak mensyaratkan gate: epic yang dibatalkan bisa saja belum pernah lolos.
    reasons = [] if args.clean else blocking_reasons(epic, state)
    if reasons:
        print("belum bisa disetujui:")
        for r in reasons:
            print("  " + r)
        return 1
    kind = "clean" if args.clean else "tiket"
    save(epic / "approval.json", {"by": args.by, "at": now(), "kind": kind, "hashes": hash_tree(epic)})
    print(f"epic disetujui oleh {args.by}")
    return 0


def approval_problem(epic):
    path = epic / "approval.json"
    if not path.exists():
        return "belum ada persetujuan"
    approved, current = load(path)["hashes"], hash_tree(epic)
    changed = sorted(k for k in set(approved) | set(current) if approved.get(k) != current.get(k))
    return f"berkas berubah setelah disetujui: {', '.join(changed)}" if changed else None


def cmd_verify_approval(epic, args):
    problem = approval_problem(epic)
    print("persetujuan: " + (problem or "sah"))
    return 1 if problem else 0


# ---------- push ke tracker ----------

TRACKERS = ("lokal", "github", "jira")


def tracker_of(epic):
    """Baca tujuan tiket dari project.json. Proyek pilot tidak pernah boleh menulis ke Jira."""
    path = epic.resolve().parent.parent / "project.json"
    if not path.exists():
        raise Fail(f"project.json tidak ditemukan di {path.parent}, tujuan tiket tidak diketahui")
    cfg = load(path)
    kind = cfg.get("tracker", {}).get("type")
    if kind not in TRACKERS:
        raise Fail(f"tracker.type di project.json harus salah satu dari {TRACKERS}")
    # Tanpa keterangan, proyek dianggap pilot: lebih aman salah menolak daripada salah menulis ke Jira.
    if cfg.get("pilot", True) and kind == "jira":
        raise Fail("proyek ini pilot dan tracker-nya Jira. Uji coba dilarang memakai Jira: "
                   "pakai tracker 'lokal' atau 'github', atau minta pemilik proyek menyetel \"pilot\": false")
    return kind


def cmd_pending_push(epic, args):
    kind = tracker_of(epic)
    problem = approval_problem(epic)
    if problem:
        raise Fail(f"tidak boleh push, {problem}")
    pushed = load(epic / "jira-map.json", {})
    tickets = ticket_files(epic)
    plan = []
    for name, path in tickets.items():
        entry = pushed.get(name)
        if entry is None:
            plan.append(("buat", name, "-"))
        elif entry["hash"] != sha(path):
            plan.append(("ubah", name, entry["key"]))
    plan += [("tutup", name, e["key"]) for name, e in pushed.items() if name not in tickets and not e.get("closed")]
    print(f"tujuan\t{kind}")
    for action, name, key in plan:
        print(f"{action}\t{name}\t{key}")
    if not plan:
        print("tidak ada yang perlu dikirim")
    return 0


def cmd_record_push(epic, args):
    pushed = load(epic / "jira-map.json", {})
    path = epic / "tickets" / f"{args.ticket}.md"
    if args.closed:
        if args.ticket not in pushed:
            raise Fail(f"{args.ticket} belum pernah dikirim")
        pushed[args.ticket]["closed"] = True
    else:
        if not path.exists():
            raise Fail(f"tiket tidak ditemukan: {path}")
        pushed[args.ticket] = {"key": args.key, "hash": sha(path), "at": now()}
    save(epic / "jira-map.json", pushed)
    print(f"tercatat: {args.ticket} -> {args.key}")
    return 0


# ---------- siklus hidup ----------

def cmd_init(epic, args):
    if (epic / "epic.json").exists():
        raise Fail(f"epic sudah ada: {epic}")
    for sub in ("contract", "specs", "tickets", "reviews"):
        (epic / sub).mkdir(parents=True, exist_ok=True)
    save(epic / "epic.json", {"title": args.title, "created": now(), "size": None})
    print(f"epic dibuat: {epic}")
    return 0


def cmd_set_size(epic, args):
    state = epic_state(epic)
    state["size"] = args.size
    save(epic / "epic.json", state)
    print(f"ukuran {args.size}, gate yang dijalankan: {', '.join(GATES_BY_SIZE[args.size])}")
    return 0


def cmd_set_jira(epic, args):
    state = epic_state(epic)
    state["jira_epic"] = args.key
    save(epic / "epic.json", state)
    print(f"epic Jira: {args.key}")
    return 0


def cmd_status(epic, args):
    state = epic_state(epic)
    print(f"{state['title']} | ukuran: {state.get('size') or 'belum ditetapkan'} | Jira: {state.get('jira_epic', '-')}")
    if state.get("size") in SIZES:
        for gate in required_gates(state):
            print(f"  gate {gate}: {gate_status(epic, gate, state)[0]}")
        if contract_changed(epic):
            print("  contract: " + ("disetujui" if contract_approved(epic, state) else "BELUM disetujui pemilik"))
    print("  persetujuan akhir: " + (approval_problem(epic) or "sah"))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn, *opts):
        p = sub.add_parser(name, help=fn.__doc__)
        p.add_argument("epic", type=Path)
        for flags, kw in opts:
            p.add_argument(*flags, **kw)
        p.set_defaults(fn=fn)

    gate = (("gate",), {"choices": GATES})
    by = (("--by",), {"required": True, "help": "nama manusia yang memutuskan"})
    add("init", cmd_init, (("--title",), {"required": True}))
    add("set-size", cmd_set_size, (("size",), {"choices": SIZES}))
    add("set-jira", cmd_set_jira, (("key",), {}))
    add("status", cmd_status)
    add("gate", cmd_gate, gate)
    add("reopen", cmd_reopen, gate)
    add("lint", cmd_lint)
    add("decide", cmd_decide, (("finding",), {}), (("decision",), {"choices": ("terima", "revisi")}),
        by, (("--note",), {"default": ""}))
    add("approve-contract", cmd_approve_contract, by)
    add("approve", cmd_approve, by, (("--clean",), {"action": "store_true",
        "help": "persetujuan untuk /clean-epic-ticket, tanpa syarat gate"}))
    add("verify-approval", cmd_verify_approval)
    add("pending-push", cmd_pending_push)
    add("record-push", cmd_record_push, (("ticket",), {}), (("key",), {}),
        (("--closed",), {"action": "store_true"}))
    args = ap.parse_args(argv)
    try:
        return args.fn(args.epic, args)
    except Fail as e:
        print(f"gagal: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
