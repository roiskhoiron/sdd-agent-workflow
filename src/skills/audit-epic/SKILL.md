---
name: audit-epic
description: Skill internal PjM, dijalankan SPV sendiri. Membaca papan kanban lewat adapter, lalu mencari tiket usang, link yatim, dan versi contract yang tidak cocok pada epic yang selesai atau dibatalkan.
user-invocable: false
---

# Mengaudit epic

Dijalankan SPV sendiri, karena skill ini membaca papan. Selain `push-board`, hanya skill ini yang berbicara ke platform, dan ia hanya membaca. Keluaran: `audit.md` di folder epic.

## 1. Ambil keadaan papan

Baca `board.platform` di `sdd.json`. Pada proyek pilot dengan platform Jira, berhenti: skrip akan menolak, dan integrasi Atlassian tidak boleh dipanggil.

Jalankan operasi **baca** dari `{{SDD_HOME}}/workflow/boards/<platform>.md` untuk semua tiket di bawah `board_epic` pada `epic.json`. Simpan ke `<epic>/board-snapshot.json` sebagai daftar objek `{ "key", "summary", "status", "links" }`.

## 2. Periksa empat hal

| Pemeriksaan | Cara | Tindakan yang diusulkan |
| --- | --- | --- |
| Tiket usang | Tiket di snapshot yang belum selesai padahal epic selesai atau dibatalkan | Tutup, dengan alasan |
| Tiket tanpa sumber | Tiket di snapshot yang tidak ada di `board-map.json` | Tanyakan operator, jangan usulkan tutup |
| Link yatim | `blocked_by` yang menunjuk tiket yang sudah tidak ada | Lepas link |
| Versi contract tidak cocok | `contract_version` di tiket berbeda dari manifes contract | Catat. Jika tiket sudah selesai dengan versi lama, tandai untuk pemilik contract |

## 3. Tulis `audit.md`

```markdown
# Audit epic: [judul]

Alasan pembersihan: selesai / dibatalkan
Platform: [board.platform]

## Tiket yang diusulkan ditutup
| Kode | Berkas | Status sekarang | Alasan |
| --- | --- | --- | --- |

## Link yang diusulkan dilepas

## Perlu keputusan operator
Tiket tanpa sumber dan versi contract yang tidak cocok.

## Tidak ada tindakan
Tiket yang sudah selesai dan bersih.
```

Jangan mengubah tiket di papan dan jangan mengubah berkas tiket. Skill ini hanya mengusulkan. Menutup tiket baru terjadi lewat `push-board` setelah manusia menyetujui.
