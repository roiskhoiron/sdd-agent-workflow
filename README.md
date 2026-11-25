# sdd-agent-workflow

Workflow agen untuk mengubah satu kebutuhan bisnis menjadi tiket Jira yang siap dikerjakan, dengan setiap tiket hanya memuat konteks yang dibutuhkan role pengerjanya. Penulisan dokumen mengikuti pola BMAD, dan setiap perpindahan tahap melewati gate EGM (gajah menulis, ikan mas me-review).

Sumber rancangan: [Draft: Agent Workflow Produksi Tiket (BMAD × EGM)](https://claude.ai/artifact/MmaafFo6XZrmLyJGm9ebkx).

Cakupan saat ini adalah tiket role Mobile. Pekerjaan role lain dicatat sebagai kebutuhan lintas role, belum dibuatkan tiket.

## Memulai

1. Buka repo ini di Claude Code dengan konektor Atlassian tersambung.
2. Jalankan `/initiate-epic-ticket <proyek> <deskripsi kebutuhan>`. Pada pemakaian pertama, perintah ini membuat `projects/<proyek>/` dari template lalu berhenti.
3. Isi `projects/<proyek>/project.json` dan enam dokumen di `projects/<proyek>/foundation/`.
4. Jalankan lagi perintah yang sama.

Supaya tidak diminta izin setiap kali skrip penjaga berjalan, tambahkan sendiri aturan ini ke `.claude/settings.json`:

```json
{ "permissions": { "allow": ["Bash(python3 scripts/sdd.py:*)"] } }
```

## Tiga perintah

| Perintah | Kapan | Hasil |
| --- | --- | --- |
| `/initiate-epic-ticket <proyek> <kebutuhan>` | Ada kebutuhan baru | Epic dan tiket di Jira |
| `/modify-epic-ticket <proyek> <epic> <perubahan>` | Kebutuhan atau contract berubah | Hanya dokumen dan tiket terdampak yang diperbarui |
| `/clean-epic-ticket <proyek> <epic> <selesai\|dibatalkan>` | Epic selesai atau dibatalkan | Tiket usang ditutup, epic diarsipkan, Foundation diperbarui |

Setelah epic dibuat, jangan mengedit tiket langsung di Jira. Perubahan manual akan tertimpa oleh `/modify-epic-ticket` berikutnya.

## Alur

```
/initiate-epic-ticket
  intake → size-epic
    kecil ──────────────────────────────────────────────┐
    sedang, besar:                                      │
      pdm: write-prd            → gate prd              │
      product-designer: design-flow → gate flow         │
      hoe: write-contract       → gate contract         │
        contract berubah → persetujuan pemilik contract │
  pjm: slice-tickets  ←─────────────────────────────────┘
    → lint → gate tickets
  request-approval (manusia memutuskan tiap temuan, lalu menyetujui)
  push-jira
```

Setiap gate dijalankan `egm-reviewer` sebagai sesi baru yang hanya menerima path dokumen. Penulis menjawab tiap temuan dengan diperbaiki, ditolak, atau diteruskan. Jika gate masih gagal setelah dua revisi, alur berhenti dan temuan diserahkan ke operator.

## Titik keputusan operator

| Titik | Yang diperiksa | Jika ragu |
| --- | --- | --- |
| Ukuran pekerjaan | Lebih dari satu role? Butuh endpoint baru? | Pilih yang lebih besar |
| Persetujuan contract | Cocok dengan mockup, dan pemilik contract setuju? | Jangan lanjut tanpa pemilik contract |
| Persetujuan akhir | Setiap temuan terjawab, tiket bisa dikerjakan tanpa bertanya? | Tulis komentar, jangan setujui |
| Kebutuhan berubah | Menyentuh contract atau hanya satu tiket? | Jalankan `/modify-epic-ticket` |

## Yang dijaga skrip, bukan agen

`scripts/sdd.py` memegang aturan yang tidak boleh bergantung pada kepatuhan agen terhadap instruksi.

| Aturan | Perintah |
| --- | --- |
| Gate lolos hanya jika tidak ada temuan terbuka, paling banyak dua revisi | `gate` |
| Dokumen yang berubah setelah gate lolos harus direview ulang | `gate` (status `usang`), `reopen` |
| Tiket Mobile punya sembilan bagian, tanpa placeholder, versi contract cocok | `lint` |
| Temuan yang ditolak atau diteruskan diputuskan manusia satu per satu | `decide` |
| Contract yang berubah disetujui pemiliknya sebelum tiket disetujui | `approve-contract` |
| Persetujuan mengunci isi epic, perubahan sesudahnya membatalkannya | `approve`, `verify-approval` |
| Hanya tiket baru, berubah, atau dihapus yang dikirim ke Jira | `pending-push`, `record-push` |

Uji: `python3 -m unittest discover tests`.

## Isi satu epic

```
projects/<proyek>/epics/<slug>/
  epic.json            status: ukuran, keputusan, segel gate
  intake.md            jawaban operator, masukan PdM
  prd.md               PdM
  flow.md              Product Designer
  contract/            HoE: contract.json dan api.yaml, dibaca semua role
  specs/               HoE: delta data, logika server, dampak infra
  tickets/             PjM: satu berkas per tiket
  reviews/             temuan reviewer dan jawaban penulis, per gate per putaran
  approval.md          paket persetujuan untuk manusia
  approval.json        segel persetujuan
  jira-map.json        berkas tiket ke kode Jira
```

Pemisahan `contract/` dan `specs/` adalah cara matriks konteks ditegakkan: tiket Mobile hanya boleh mengambil dari `contract/`. Lihat `workflow/context-matrix.md`.

## Keputusan implementasi yang tidak ada di draft

Draft meninggalkan beberapa hal terbuka. Implementasi ini memilih nilai awal berikut, dan semuanya bisa diubah.

| Hal | Pilihan | Tempat mengubah |
| --- | --- | --- |
| Tempat dokumen disimpan | Berkas Markdown di repo ini | Susunan `projects/` |
| Temuan gate | Berkas JSON di `reviews/`, bukan komentar di dokumen | Skill `egm-review` |
| Format contract | OpenAPI 3.1 | `project.json`, skill `write-contract` |
| Mockup | Tautan bila ada, wireframe teks bila tidak | `mockup_tool` di `project.json` |
| Model tiap peran | Mengikuti model sesi | Tambahkan `model:` di `.claude/agents/*.md` |
| Pemilik manusia | Belum diisi | `owners` di `project.json` |
| Ukuran sedang | Tetap menulis PRD, dibatasi setengah halaman | Skill `size-epic` dan `write-prd` |
| Pembaruan Foundation | Diterapkan langsung setelah disetujui, tanpa tiket tersendiri | Skill `clean-epic-ticket` |
| Akses Jira | Hanya sesi utama, subagent tidak menyentuh Jira | Skill `push-jira` |
| Konvensi kode mobile dan konfigurasi environment | Tautan di `references`, bukan dokumen Foundation ketujuh | `project.json` |

## Belum dikerjakan

- Template tiket Backend, Frontend web, dan DevOps (roadmap di draft).
- Uji coba pada epic nyata. Skrip sudah diuji, tetapi skill dan agen belum pernah dijalankan dari awal sampai Jira.
