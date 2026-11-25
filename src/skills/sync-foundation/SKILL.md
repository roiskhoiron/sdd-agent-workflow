---
name: sync-foundation
description: Skill internal HoE. Menyusun usulan pembaruan Foundation dari epic yang selesai. Dijalankan oleh agen peran hoe.
user-invocable: false
---

# Menyusun usulan pembaruan Foundation

Masukan: folder epic dan `foundation/` proyek. Keluaran: `foundation-proposal.md` di folder epic. Jangan mengubah isi `foundation/`.

Jika epic dibatalkan, tidak ada yang dibawa ke Foundation. Tulis usulan kosong dengan alasan itu.

Jika epic selesai, bandingkan hasilnya dengan tiap dokumen Foundation:

| Sumber di epic | Dokumen Foundation | Yang diusulkan |
| --- | --- | --- |
| `contract/api.yaml` dengan `changed: true` | `katalog-contract.md`, `contracts/` | Versi baru menggantikan versi lama di katalog |
| `specs/data-delta.md` | `skema-database.md` | Tabel dan kolom baru masuk skema dasar |
| `specs/infra-impact.md` | `infrastruktur.md` | Layanan, variabel, atau aturan baru |
| `specs/adr-draft.md` | `adr.md` | Entri keputusan baru |
| Komponen baru di `flow.md` | `design-system.md` | Komponen yang perlu ditambahkan |

Untuk tiap usulan, tulis teks persis yang akan ditambahkan atau diganti, supaya pemilik dokumen menyetujui isinya dan bukan niatnya.

```markdown
# Usulan pembaruan Foundation: [judul epic]

## foundation/katalog-contract.md
Pemilik: [dari project.json]
Ganti baris: ...
Menjadi: ...

## Tidak ada perubahan
Dokumen Foundation yang tidak tersentuh epic ini.
```

Hanya usulkan hal yang benar-benar dikerjakan. Jika `jira-snapshot.json` menunjukkan tiket yang membawa suatu perubahan tidak selesai, perubahan itu tidak masuk Foundation.
