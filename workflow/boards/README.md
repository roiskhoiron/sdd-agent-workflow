# Adapter papan kanban

Workflow memakai lima konsep netral. Setiap adapter menerjemahkannya ke satu platform. Hanya skill `setup-board`, `push-board`, dan `audit-epic` yang membaca folder ini. Skill lain tidak tahu platform mana yang dipakai.

| Konsep netral | GitHub Projects (default) | Jira | Lokal (uji coba) |
| --- | --- | --- | --- |
| Epic | Issue induk | Epic | `EPIC.md` |
| Tiket per role | Sub-issue di bawah issue induk | Issue anak di bawah epic | `LOKAL-<n>.md` |
| Ketergantungan | Issue dependencies: blocked by dan blocking | Link is blocked by | Baris `Diblokir oleh` |
| Status | Field Status pada project (kolom papan) | Status workflow | Baris `Status` |
| Role pengerja | Label, misalnya `role:mobile` | Label atau komponen | Baris `Role` |
| Alat yang dipakai agen | GitHub CLI (`gh`) atau GitHub MCP | Atlassian MCP | Berkas di repo |

Setiap adapter menjawab enam operasi:

1. **uji**: memeriksa empat kemampuan yang dibutuhkan, yaitu membuat epic, membuat tiket anak, membuat ketergantungan, dan membaca status.
2. **buat-epic**
3. **buat-tiket**: tiket anak di bawah epic, dengan label role.
4. **hubungkan**: tiket A diblokir oleh tiket B.
5. **ubah-status**: memindahkan tiket ke kolom yang dipetakan di `board.status_map` pada `sdd.json`.
6. **baca**: mengambil semua tiket di bawah epic beserta status dan ketergantungannya.

Jika sebuah kemampuan tidak ada di platform, gantikan dengan teks: tulis baris `Diblokir oleh: <kode>` di awal isi tiket, dan catat kekurangan itu di `board.capabilities` saat setup.

Menambah platform baru (Linear, Trello, dan lainnya) cukup dengan menulis satu berkas adapter di folder ini dan menambahkan namanya ke `BOARDS` di `scripts/sdd.py`.
