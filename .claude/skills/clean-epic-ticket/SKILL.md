---
name: clean-epic-ticket
description: Membersihkan epic yang selesai atau dibatalkan. Menutup tiket usang, mengarsipkan draft, dan memperbarui Foundation setelah disetujui.
argument-hint: "<proyek> <epic> <selesai|dibatalkan>"
disable-model-invocation: true
---

# /clean-epic-ticket

Masukan operator: $ARGUMENTS

Kamu adalah SPV. Hanya kamu yang memanggil skill dan subagent.

Rantai: `audit-epic` → `sync-foundation` → `request-approval` → `push-jira`. Tidak ada gate EGM di sini, tetapi persetujuan manusia tetap wajib karena menutup tiket sulit dibatalkan.

## 1. Temukan epic

Cari epic seperti di `/modify-epic-ticket`. Jika operator tidak menyebut alasannya, tanyakan: selesai atau dibatalkan.

## 2. Ambil keadaan Jira

Dengan tool Atlassian, ambil semua issue di bawah epic Jira: kode, judul, status, dan link. Simpan ke `<epic>/jira-snapshot.json` sebagai daftar objek `{ "key", "summary", "status", "links" }`. Langkah ini hanya membaca Jira.

## 3. Audit

Panggil subagent `pjm` dengan brief: folder epic, alasan pembersihan, dan skill `audit-epic`. Hasilnya `audit.md`.

Jika audit berisi "perlu keputusan operator", tanyakan sekarang dan catat jawabannya di `audit.md` sebelum lanjut.

## 4. Usulan Foundation

Panggil subagent `hoe` dengan brief: folder epic, folder proyek, alasan pembersihan, dan skill `sync-foundation`. Hasilnya `foundation-proposal.md`.

## 5. Persetujuan

Panggil skill `request-approval` dengan jenis clean. Paketnya memuat tiket yang akan ditutup dan teks persis yang akan masuk Foundation. Tiap usulan Foundation disetujui pemilik dokumennya menurut `project.json`. Tanyakan operator apakah pemilik itu sudah menyetujui.

## 6. Jalankan

Setelah disetujui:

1. Panggil skill `push-jira` untuk menutup tiket yang disetujui di `audit.md` dan melepas link yatim.
2. Terapkan `foundation-proposal.md` ke `projects/<proyek>/foundation/` persis seperti yang disetujui. Jika contract berubah, salin `contract/api.yaml` ke `foundation/contracts/` dan perbarui barisnya di `katalog-contract.md`.
3. Pindahkan folder epic ke `projects/<proyek>/epics/_arsip/<slug>/`.

Kerjakan dalam urutan itu. Folder epic dipindahkan terakhir karena `push-jira` membaca persetujuan dari sana.

## 7. Tutup

Laporkan tiket yang ditutup, dokumen Foundation yang berubah, dan lokasi arsip. Tawarkan untuk meng-commit hasilnya.
