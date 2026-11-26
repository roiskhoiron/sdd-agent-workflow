---
name: setup-design
description: Skill internal SPV. Memastikan platform desain sudah dipilih dan tercatat di memory project (sdd.json). Dipanggil di awal ketiga skill pintu masuk, setelah setup-docs.
user-invocable: false
---

# Menyiapkan platform desain

Jika `design.platform` di `sdd.json` sudah tercatat, skill ini selesai tanpa bertanya.

Jika belum, tanyakan sekali kepada operator:

| Pilihan | Nilai | Keterangan |
| --- | --- | --- |
| FigCraft MCP | `figcraft` | Default |
| Figma MCP resmi | `figma` | |
| Claude Design | `claude-design` | |

Tanyakan juga lokasi berkas desain tim (tautan berkas atau project), lalu catat:

```
python3 {{SDD_HOME}}/scripts/sdd.py remember . design.platform <nilai>
python3 {{SDD_HOME}}/scripts/sdd.py remember . design.location "<tautan>"
```

Periksa apakah integrasi platform itu tersedia di alatmu, misalnya tool MCP-nya terdaftar. Jika tidak tersedia, beri tahu operator: Product Designer akan menulis wireframe teks dan merujuk tautan desain yang diberikan operator, tanpa membaca berkas desain langsung.
