"""Uji aturan workflow: python3 -m unittest discover tests"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SDD = ROOT / "scripts" / "sdd.py"
TEMPLATE = (ROOT / "workflow" / "templates" / "ticket-mobile.md").read_text(encoding="utf-8")

GOOD_TICKET = """---
kind: role
role: mobile
size: {size}
contract_version: {version}
blocked_by: {blocked}
---
# [KODE-TIKET] Pengguna bisa mengirim foto di chat

## 1. Tujuan
Pengguna bisa mengirim foto dari galeri.

## 2. Ruang lingkup
- Termasuk: pilih satu foto
- Tidak termasuk: video

## 3. Layar dan flow
Layar chat, state gagal menampilkan tombol coba lagi.

## 4. API contract
{api}

## 5. Aturan sisi klien
Kompres foto sampai di bawah 2 MB.

## 6. Keamanan sisi klien
Tidak ada

## 7. Acceptance criteria
- [ ] Given foto 1 MB When dikirim Then muncul di chat

## 8. Rujukan Foundation
foundation/design-system.md

## 9. Ketergantungan
- Diblokir oleh: {blocked}
"""


class Workflow(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name) / "repo"
        self.epic = self.project / "docs" / "epics" / "epic"
        self.epic.parent.mkdir(parents=True)
        self.set_board("lokal", pilot=True)
        self.run_ok("init", "--title", "Kirim foto")

    def tearDown(self):
        self.tmp.cleanup()

    def set_board(self, kind, pilot):
        (self.project / "sdd.json").write_text(json.dumps({"pilot": pilot, "board": {"platform": kind}}))

    def memory_cmd(self, *args):
        return subprocess.run([sys.executable, str(SDD), *args], capture_output=True, text=True)

    def sdd(self, cmd, *args):
        return subprocess.run([sys.executable, str(SDD), cmd, str(self.epic), *args],
                              capture_output=True, text=True)

    def run_ok(self, cmd, *args):
        r = self.sdd(cmd, *args)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout

    def review(self, gate, n, findings):
        (self.epic / "reviews" / f"{gate}-r{n}.json").write_text(json.dumps({"gate": gate, "findings": findings}))

    def finding(self, status=None, note="alasan"):
        f = {"type": "hilang", "where": "bagian 4", "text": "Pesan error 413 tidak ada."}
        if status:
            f["response"] = {"status": status, "note": note}
        return f

    def ticket(self, name="mobile-01", size="kecil", version="tidak ada", blocked="tidak ada", api="Tidak ada"):
        (self.epic / "tickets" / f"{name}.md").write_text(
            GOOD_TICKET.format(size=size, version=version, blocked=blocked, api=api))

    def small_epic_ready(self):
        self.run_ok("set-size", "kecil")
        self.ticket()
        self.review("tickets", 1, [])
        self.run_ok("gate", "tickets")

    # ---- gate ----

    def test_gate_follows_review_rounds(self):
        self.run_ok("set-size", "kecil")
        self.ticket()
        self.assertIn("belum-direview", self.sdd("gate", "tickets").stdout)
        self.review("tickets", 1, [self.finding()])
        self.assertIn("perlu-jawaban", self.sdd("gate", "tickets").stdout)
        self.review("tickets", 1, [self.finding("diperbaiki")])
        self.assertIn("perlu-review-ulang", self.sdd("gate", "tickets").stdout)
        self.review("tickets", 2, [])
        self.assertIn("lolos", self.run_ok("gate", "tickets"))

    def test_gate_stops_after_two_revisions(self):
        self.run_ok("set-size", "kecil")
        self.review("tickets", 1, [self.finding("diperbaiki")])
        self.review("tickets", 2, [self.finding("diperbaiki")])
        self.review("tickets", 3, [self.finding("ditolak")])
        self.assertIn("berhenti", self.sdd("gate", "tickets").stdout)

    def test_rejection_needs_a_reason(self):
        self.run_ok("set-size", "kecil")
        self.review("tickets", 1, [self.finding("ditolak", note="")])
        r = self.sdd("gate", "tickets")
        self.assertEqual(r.returncode, 2)
        self.assertIn("wajib punya 'note'", r.stderr)

    def test_passed_gate_goes_stale_when_document_changes(self):
        self.small_epic_ready()
        self.ticket(api="Tidak ada.")
        self.assertIn("usang", self.sdd("gate", "tickets").stdout)
        self.run_ok("reopen", "tickets")
        self.assertIn("belum-direview", self.sdd("gate", "tickets").stdout)

    # ---- persetujuan ----

    def test_approval_requires_passed_gates(self):
        self.run_ok("set-size", "kecil")
        self.ticket()
        r = self.sdd("approve", "--by", "Rois")
        self.assertEqual(r.returncode, 1)
        self.assertIn("gate tickets berstatus belum-direview", r.stdout)

    def test_carried_findings_need_a_human_decision_each(self):
        self.run_ok("set-size", "kecil")
        self.ticket()
        self.review("tickets", 1, [self.finding("ditolak"), self.finding("diteruskan")])
        self.run_ok("gate", "tickets")
        self.assertIn("tickets-r1-1 belum diputuskan", self.sdd("approve", "--by", "Rois").stdout)
        self.run_ok("decide", "tickets-r1-1", "terima", "--by", "Rois")
        self.run_ok("decide", "tickets-r1-2", "revisi", "--by", "Rois")
        out = self.sdd("approve", "--by", "Rois").stdout
        self.assertNotIn("tickets-r1-1", out)
        self.assertIn("tickets-r1-2 diputuskan 'revisi'", out)
        self.run_ok("decide", "tickets-r1-2", "terima", "--by", "Rois")
        self.run_ok("approve", "--by", "Rois")

    def test_edit_after_approval_blocks_push(self):
        self.small_epic_ready()
        self.run_ok("approve", "--by", "Rois")
        self.assertIn("buat\tmobile-01", self.run_ok("pending-push"))
        self.ticket(api="Tidak ada.")
        r = self.sdd("pending-push")
        self.assertEqual(r.returncode, 2)
        self.assertIn("tickets/mobile-01.md", r.stderr)

    def test_push_without_approval_is_refused(self):
        self.small_epic_ready()
        self.assertEqual(self.sdd("pending-push").returncode, 2)

    def test_changed_contract_needs_owner_approval(self):
        self.run_ok("set-size", "besar")
        (self.epic / "prd.md").write_text("prd")
        (self.epic / "flow.md").write_text("flow")
        (self.epic / "contract" / "contract.json").write_text(json.dumps({"version": "1.1.0", "changed": True}))
        (self.epic / "tickets" / "contract-01.md").write_text(
            "---\nkind: contract\nsize: besar\nblocked_by: tidak ada\n---\n# [KODE-TIKET] Contract chat 1.1.0\n")
        self.ticket(size="besar", version="1.1.0", blocked="contract-01", api="POST /messages, contract 1.1.0")
        for gate in ("prd", "flow", "contract", "tickets"):
            self.review(gate, 1, [])
            self.run_ok("gate", gate)
        self.assertIn("belum disetujui pemilik contract", self.sdd("approve", "--by", "Rois").stdout)
        self.run_ok("approve-contract", "--by", "Lead Backend")
        self.run_ok("approve", "--by", "Rois")

    def test_clean_approval_skips_gates(self):
        self.run_ok("set-size", "besar")
        (self.epic / "audit.md").write_text("audit")
        self.run_ok("approve", "--by", "Rois", "--clean")
        self.run_ok("verify-approval")

    # ---- push ----

    def test_pilot_project_can_never_push_to_jira(self):
        self.small_epic_ready()
        self.run_ok("approve", "--by", "Rois")
        self.set_board("jira", pilot=True)
        r = self.sdd("pending-push")
        self.assertEqual(r.returncode, 2)
        self.assertIn("dilarang memakai Jira", r.stderr)
        (self.project / "sdd.json").write_text(json.dumps({"board": {"platform": "jira"}}))
        self.assertEqual(self.sdd("pending-push").returncode, 2, "tanpa kunci pilot harus dianggap pilot")
        self.set_board("jira", pilot=False)
        self.assertIn("tujuan\tjira", self.run_ok("pending-push"))
        self.set_board("github-projects", pilot=True)
        self.assertIn("tujuan\tgithub-projects", self.run_ok("pending-push"))

    def test_unchosen_board_blocks_push(self):
        self.small_epic_ready()
        self.run_ok("approve", "--by", "Rois")
        (self.project / "sdd.json").write_text(json.dumps({"pilot": True, "board": {"platform": None}}))
        r = self.sdd("pending-push")
        self.assertEqual(r.returncode, 2)
        self.assertIn("setup-board", r.stderr)

    # ---- memory project ----

    def test_remember_records_choices_and_guards_pilot(self):
        root = str(self.project)
        (self.project / "sdd.json").unlink()
        self.assertIn("board.platform: BELUM DIPILIH", self.memory_cmd("memory", root).stdout)
        r = self.memory_cmd("remember", root, "board.platform", "github-projects")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.memory_cmd("remember", root, "board.status_map", '{"siap": "Todo", "selesai": "Done"}')
        cfg = json.loads((self.project / "sdd.json").read_text())
        self.assertEqual(cfg["board"], {"platform": "github-projects", "status_map": {"siap": "Todo", "selesai": "Done"}})
        self.assertIn("harus salah satu", self.memory_cmd("remember", root, "board.platform", "trello").stderr)
        self.assertIn("hanya boleh diubah manusia", self.memory_cmd("remember", root, "pilot", "false").stderr)
        r = self.memory_cmd("remember", root, "board.platform", "jira")
        self.assertEqual(r.returncode, 2)
        self.assertIn("dilarang memakai Jira", r.stderr)
        self.assertEqual(json.loads((self.project / "sdd.json").read_text())["board"]["platform"], "github-projects")

    def test_only_changed_tickets_are_pushed_again(self):
        self.small_epic_ready()
        self.ticket(name="mobile-02")
        self.run_ok("reopen", "tickets")
        self.review("tickets", 1, [])
        self.run_ok("gate", "tickets")
        self.run_ok("approve", "--by", "Rois")
        self.run_ok("record-push", "mobile-01", "BC-1")
        self.run_ok("record-push", "mobile-02", "BC-2")
        self.assertIn("tidak ada yang perlu dikirim", self.run_ok("pending-push"))
        self.ticket(name="mobile-02", api="Tidak ada.")
        (self.epic / "tickets" / "mobile-01.md").unlink()
        self.run_ok("reopen", "tickets")
        self.review("tickets", 1, [])
        self.run_ok("gate", "tickets")
        self.run_ok("approve", "--by", "Rois")
        plan = self.run_ok("pending-push")
        self.assertIn("ubah\tmobile-02\tBC-2", plan)
        self.assertIn("tutup\tmobile-01\tBC-1", plan)

    # ---- lint ----

    def lint_errors(self):
        return self.sdd("lint").stdout

    def test_untouched_template_fails_lint(self):
        (self.epic / "tickets" / "mobile-01.md").write_text(TEMPLATE)
        out = self.lint_errors()
        self.assertIn("placeholder", out)
        self.assertIn("contract/contract.json tidak ada", out)

    def test_missing_section_fails_lint(self):
        self.ticket()
        p = self.epic / "tickets" / "mobile-01.md"
        p.write_text(p.read_text().replace("## 6. Keamanan sisi klien\nTidak ada\n\n", ""))
        self.assertIn("persis sembilan", self.lint_errors())

    def test_goal_cannot_be_tidak_ada(self):
        self.ticket()
        p = self.epic / "tickets" / "mobile-01.md"
        p.write_text(p.read_text().replace("Pengguna bisa mengirim foto dari galeri.", "Tidak ada"))
        self.assertIn("bagian 1 (Tujuan) tidak boleh 'Tidak ada'", self.lint_errors())

    def test_contract_version_must_match_manifest(self):
        (self.epic / "contract" / "contract.json").write_text(json.dumps({"version": "1.1.0", "changed": False}))
        self.ticket(version="1.0.0", api="GET /messages")
        self.assertIn("tidak cocok dengan contract 1.1.0", self.lint_errors())

    def test_changed_contract_requires_blocking_contract_ticket(self):
        (self.epic / "contract" / "contract.json").write_text(json.dumps({"version": "1.1.0", "changed": True}))
        self.ticket(version="1.1.0", api="GET /messages")
        self.assertIn("wajib blocked_by tiket contract", self.lint_errors())

    def test_design_ticket_must_block_role_tickets(self):
        (self.epic / "tickets" / "design-01.md").write_text(
            "---\nkind: design\nrole: ui-ux\nsize: besar\nblocked_by: tidak ada\n---\n# [KODE-TIKET] Prototipe layar favorit\n")
        self.ticket()
        self.assertIn("wajib blocked_by tiket desain", self.lint_errors())
        self.ticket(blocked="design-01")
        self.assertIn("lint: bersih", self.lint_errors())

    def test_unknown_blocker_fails_lint(self):
        self.ticket(blocked="backend-07")
        self.assertIn("blocked_by 'backend-07'", self.lint_errors())
        for key in ("BC-120", "#45", "codingskuy/chefgenie#45"):
            self.ticket(blocked=key)
            self.assertIn("lint: bersih", self.lint_errors(), key)


if __name__ == "__main__":
    unittest.main()
