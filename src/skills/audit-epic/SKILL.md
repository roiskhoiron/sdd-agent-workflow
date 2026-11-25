---
name: audit-epic
description: Skill internal PjM. Mencari tiket usang, link yatim, dan versi contract yang tidak cocok pada epic yang selesai atau dibatalkan. Dijalankan oleh agen peran pjm.
user-invocable: false
---

# Mengaudit epic

Masukan: folder epic, termasuk `jira-map.json` dan `jira-snapshot.json` yang disiapkan SPV. Kamu tidak mengakses Jira. Keluaran: `audit.md` di folder epic.

Periksa empat hal:

| Pemeriksaan | Cara | Tindakan yang diusulkan |
| --- | --- | --- |
| Tiket usang | Tiket di snapshot yang belum selesai padahal epic selesai atau dibatalkan | Tutup, dengan alasan |
| Tiket tanpa sumber | Tiket di snapshot yang tidak ada di `jira-map.json` | Tanyakan operator, jangan usulkan tutup |
| Link yatim | `blocked_by` yang menunjuk tiket yang sudah tidak ada | Lepas link |
| Versi contract tidak cocok | `contract_version` di tiket berbeda dari manifes contract | Catat. Jika tiket sudah selesai dengan versi lama, tandai untuk pemilik contract |

Isi `audit.md`:

```markdown
# Audit epic: [judul]

Alasan pembersihan: selesai / dibatalkan

## Tiket yang diusulkan ditutup
| Kode Jira | Berkas | Status sekarang | Alasan |
| --- | --- | --- | --- |

## Link yang diusulkan dilepas

## Perlu keputusan operator
Tiket tanpa sumber dan versi contract yang tidak cocok.

## Tidak ada tindakan
Tiket yang sudah selesai dan bersih.
```

Jangan mengubah atau menghapus berkas tiket. Kamu hanya mengusulkan, dan menutup tiket baru terjadi setelah manusia menyetujui.
