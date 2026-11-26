---
name: clean-epic-ticket
description: Membersihkan epic yang selesai atau dibatalkan. Menutup tiket usang di papan kanban, mengarsipkan draft, dan memperbarui Foundation setelah disetujui.
argument-hint: "<epic> <selesai|dibatalkan>"
disable-model-invocation: true
---

# clean-epic-ticket

Masukan operator: $ARGUMENTS

Kamu adalah SPV. Hanya kamu yang memanggil skill dan agen peran.

Rantai: `setup-board` → `setup-docs` → `setup-design` → `audit-epic` → `sync-foundation` → `request-approval` → `push-board`. Tidak ada gate EGM di sini, tetapi persetujuan manusia tetap wajib karena menutup tiket sulit dibatalkan.

## 1. Siapkan platform dan temukan epic

Panggil skill `setup-board`, `setup-docs`, dan `setup-design`. Ketiganya selesai tanpa bertanya bila pilihan sudah tercatat.

Epic boleh disebut dengan slug folder atau kode epic di papan. Untuk kode papan, cari `board_epic` yang cocok di `docs/epics/*/epic.json`. Jika operator tidak menyebut alasannya, tanyakan: selesai atau dibatalkan.

Jika epic dibuat sebelum platform papan diganti, tiketnya tetap di platform lama. Tanyakan operator platform mana yang dipakai epic ini sebelum lanjut, dan jangan mengubah `sdd.json`.

## 2. Audit

Panggil skill `audit-epic`. Skill ini membaca papan lewat adapter dan menghasilkan `audit.md`.

Jika audit berisi "perlu keputusan operator", tanyakan sekarang dan catat jawabannya di `audit.md` sebelum lanjut.

## 3. Usulan Foundation

Jalankan agen peran `hoe` dengan brief: folder epic, alasan pembersihan, dan skill `sync-foundation`. Hasilnya `foundation-proposal.md`.

## 4. Persetujuan

Panggil skill `request-approval` dengan jenis clean. Paketnya memuat tiket yang akan ditutup dan teks persis yang akan masuk Foundation. Tiap usulan Foundation disetujui pemilik dokumennya menurut `owners` di `sdd.json`. Tanyakan operator apakah pemilik itu sudah menyetujui.

## 5. Jalankan

Setelah disetujui:

1. Panggil skill `push-board` untuk menutup tiket yang disetujui di `audit.md` dan melepas link yatim.
2. Terapkan `foundation-proposal.md` persis seperti yang disetujui, ke `docs/foundation/`, `docs/contracts/`, dan `docs/adr/`. Jika contract berubah, salin `contract/api.yaml` ke `docs/contracts/<nama>-<versi>.yaml` dan perbarui barisnya di `docs/contracts/katalog.md`.
3. Pindahkan folder epic ke `docs/epics/_arsip/<slug>/`.

Kerjakan dalam urutan itu. Folder epic dipindahkan terakhir karena `push-board` membaca persetujuan dari sana.

## 6. Tutup

Laporkan tiket yang ditutup, dokumen Foundation yang berubah, dan lokasi arsip. Jika `docs.platform` bukan `repo`, perbarui salinan Foundation di platform itu. Tawarkan untuk meng-commit hasilnya.
