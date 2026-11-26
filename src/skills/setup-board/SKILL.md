---
name: setup-board
description: Skill internal SPV. Memastikan platform papan kanban sudah dipilih, diuji, dan tercatat di memory project (sdd.json). Dipanggil di awal ketiga skill pintu masuk.
user-invocable: false
---

# Menyiapkan papan kanban

Memory project adalah berkas `sdd.json` di akar repo. Pilihan platform ditanya sekali, lalu disimpan di sana.

## 1. Baca memory

```
python3 {{SDD_HOME}}/scripts/sdd.py memory .
```

Jika `board.platform` sudah tercatat dan `board.capabilities` sudah terisi, skill ini selesai tanpa bertanya.

Jika `sdd.json` belum ada, salin `{{SDD_HOME}}/workflow/project-template/sdd.json` ke akar repo lebih dulu.

## 2. Tanyakan platform

Tanyakan sekali kepada operator. Tampilkan pilihan dengan urutan ini:

| Pilihan | Nilai | Keterangan |
| --- | --- | --- |
| GitHub Projects | `github-projects` | Default. Pakai jika operator tidak memilih yang lain. |
| Jira | `jira` | Tidak bisa dipilih selama `sdd.json` berisi `"pilot": true`. |
| Lokal | `lokal` | Berkas di repo, tanpa layanan luar. Untuk uji coba. |

Lalu tanyakan lokasi papan sesuai adapternya di `{{SDD_HOME}}/workflow/boards/<platform>.md`, misalnya repo dan nomor project untuk GitHub Projects.

Catat:

```
python3 {{SDD_HOME}}/scripts/sdd.py remember . board.platform <nilai>
python3 {{SDD_HOME}}/scripts/sdd.py remember . board.location '<json lokasi>'
```

Skrip menolak Jira untuk proyek pilot. Jangan mengubah `pilot` sendiri. Hanya operator yang boleh mengedit kunci itu.

## 3. Uji empat kemampuan

Jalankan operasi **uji** dari adapter: membuat epic, membuat tiket anak, membuat ketergantungan, dan membaca status. Laporkan hasilnya kepada operator, lalu catat:

```
python3 {{SDD_HOME}}/scripts/sdd.py remember . board.capabilities '{"epic": true, "child": true, "dependency": false, "status": true}'
```

Kemampuan yang tidak ada akan diganti teks oleh `push-board`. Sebutkan itu kepada operator sekarang, bukan saat tiket dikirim.

## 4. Pemetaan status dan label

Tunjukkan `board.status_map` dan `board.role_labels` di `sdd.json` kepada operator. Nilai awalnya mengikuti kolom Todo, Ready To Review, dan Done. Jika nama kolom di papan berbeda, catat yang benar dengan `remember`.

## Mengganti platform

Jika operator ingin pindah platform, jalankan ulang skill ini dari langkah 2. Tiket lama tidak dipindahkan. Epic yang sudah berjalan diselesaikan di platform lamanya, karena `board-map.json` tiap epic mencatat kode di platform tempat tiket itu dibuat.
