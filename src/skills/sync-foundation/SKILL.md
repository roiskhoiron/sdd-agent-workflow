---
name: sync-foundation
description: Skill internal HoE. Menyusun usulan pembaruan Foundation dari epic yang selesai. Dijalankan oleh agen peran hoe.
user-invocable: false
---

# Menyusun usulan pembaruan Foundation

Masukan: folder epic, `docs/foundation/`, `docs/contracts/`, dan `docs/adr/`. Keluaran: `foundation-proposal.md` di folder epic. Jangan mengubah isi ketiga folder itu.

Jika epic dibatalkan, tidak ada yang dibawa ke Foundation. Tulis usulan kosong dengan alasan itu.

Jika epic selesai, bandingkan hasilnya dengan tiap dokumen Foundation:

| Sumber di epic | Dokumen Foundation | Yang diusulkan |
| --- | --- | --- |
| `contract/api.yaml` dengan `changed: true` | `docs/contracts/katalog.md` dan berkas `docs/contracts/<nama>-<versi>.yaml` | Versi baru menggantikan versi lama di katalog |
| `specs/data-delta.md` | `docs/foundation/skema-database.md` | Tabel dan kolom baru masuk skema dasar |
| `specs/infra-impact.md` | `docs/foundation/infrastruktur.md` | Layanan, variabel, atau aturan baru |
| `specs/adr-draft.md` | `docs/adr/NNNN-judul.md` | Berkas keputusan baru |
| Komponen baru di `flow.md` | `docs/foundation/design-system.md` | Komponen yang perlu ditambahkan. Jika epic punya tiket desain, ambil dari hasil tiket itu. |

Untuk tiap usulan, tulis teks persis yang akan ditambahkan atau diganti, supaya pemilik dokumen menyetujui isinya dan bukan niatnya.

```markdown
# Usulan pembaruan Foundation: [judul epic]

## docs/contracts/katalog.md
Pemilik: [dari sdd.json]
Ganti baris: ...
Menjadi: ...

## Tidak ada perubahan
Dokumen Foundation yang tidak tersentuh epic ini.
```

Hanya usulkan hal yang benar-benar dikerjakan. Jika `board-snapshot.json` menunjukkan tiket yang membawa suatu perubahan tidak selesai, perubahan itu tidak masuk Foundation.
