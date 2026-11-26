---
name: setup-docs
description: Skill internal SPV. Memastikan platform dokumentasi sudah dipilih dan tercatat di memory project (sdd.json). Dipanggil di awal ketiga skill pintu masuk, setelah setup-board.
user-invocable: false
---

# Menyiapkan platform dokumentasi

Jika `docs.platform` di `sdd.json` sudah tercatat, skill ini selesai tanpa bertanya.

Jika belum, tanyakan sekali kepada operator:

| Pilihan | Nilai | Keterangan |
| --- | --- | --- |
| Folder `docs/` di repo | `repo` | Default. Markdown di repo ini. |
| Claude Docs | `claude-docs` | Salinan untuk dibaca dan dikomentari |
| Confluence | `confluence` | Salinan untuk dibaca dan dikomentari |
| Notion | `notion` | Salinan untuk dibaca dan dikomentari |

```
python3 {{SDD_HOME}}/scripts/sdd.py remember . docs.platform <nilai>
```

Untuk pilihan selain `repo`, tanyakan juga lokasi induknya (ruang, halaman, atau folder) dan catat di `docs.location`.

## Tata letak dokumen

Apa pun pilihannya, dokumen ditulis lebih dulu di repo. Gate, persetujuan, dan skrip `sdd.py` bekerja dari berkas ini.

| Dokumen | Lokasi |
| --- | --- |
| PRD, flow, spec, tiket, dan catatan gate | `docs/epics/<slug>/` |
| API contract berversi dan katalognya | `docs/contracts/` |
| Catatan keputusan | `docs/adr/` |
| Foundation docs | `docs/foundation/` |

Jika folder ini belum ada, salin isi `{{SDD_HOME}}/workflow/project-template/docs/` ke `docs/`, beri tahu operator bahwa Foundation harus diisi pemiliknya, lalu berhenti.

Untuk platform selain `repo`, setelah persetujuan akhir SPV menyalin PRD, flow, dan contract ke platform itu dan mencatat tautannya di laporan akhir. Salinan itu untuk dibaca manusia. Sumber kebenarannya tetap berkas di repo.
