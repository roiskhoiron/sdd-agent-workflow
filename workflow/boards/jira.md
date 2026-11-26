# Adapter: Jira

Proyek berstatus pilot tidak boleh memakai adapter ini. Skrip `sdd.py` menolak, dan agen dilarang memanggil integrasi Atlassian untuk proyek pilot, termasuk untuk membaca.

Lokasi papan di `sdd.json`:

```json
"board": { "platform": "jira", "location": { "site": "nama.atlassian.net", "project_key": "BC",
  "epic_issue_type": "Epic", "ticket_issue_type": "Story", "blocks_link_type": "Blocks" } }
```

Pakai tool Atlassian MCP yang tersedia di alatmu.

## uji

Ambil metadata issue type proyek dan daftar transisi. Pastikan issue type, jenis link, dan setiap kolom di `board.status_map` memang ada. Jangan membuat issue uji di Jira. Catat hasilnya di `board.capabilities`.

## buat-epic

Buat issue bertipe `epic_issue_type`. Kode epic adalah kunci issue, misalnya `BC-120`.

## buat-tiket

Buat issue bertipe `ticket_issue_type` dengan parent epic, label dari `board.role_labels`, dan deskripsi berisi isi tiket tanpa front matter.

## hubungkan

Buat link `blocks_link_type` sehingga tiket "is blocked by" pemblokirnya.

## ubah-status

Pindahkan lewat transisi ke status yang dipetakan di `board.status_map`. Menutup tiket memakai transisi ke status `selesai` beserta komentar alasan. Jangan menghapus issue.

## baca

Cari dengan JQL `parent = <KODE-EPIC>`, ambil kunci, ringkasan, status, dan link.
