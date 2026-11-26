---
name: push-board
description: Skill internal PjM, dijalankan SPV sendiri. Membuat, mengubah, atau menutup tiket di papan kanban lewat adapter platform, setelah persetujuan manusia. Dipanggil oleh ketiga skill pintu masuk setelah request-approval.
user-invocable: false
---

# Mengirim tiket ke papan kanban

Dijalankan SPV sendiri, bukan oleh agen peran, supaya operator melihat setiap perubahan. Hanya skill ini dan `audit-epic` yang berbicara ke platform papan.

## Aturan keras: uji coba tidak memakai Jira

Proyek dengan `"pilot": true` di `sdd.json`, atau tanpa kunci `pilot`, tidak pernah menulis ke Jira. Skrip menolak membuat rencana untuk gabungan itu. Jika skrip menolak, jangan mengubah `sdd.json` sendiri dan jangan memanggil integrasi Atlassian dengan cara lain. Hanya operator yang boleh menyetel `"pilot": false`.

## 1. Pastikan persetujuan sah dan baca platform

```
python3 {{SDD_HOME}}/scripts/sdd.py pending-push <epic>
```

Perintah ini menolak jika persetujuan tidak ada, ada berkas yang berubah sesudahnya, platform belum dipilih, atau proyek pilot diarahkan ke Jira. Jika menolak, berhenti dan laporkan. Jangan mengirim apa pun.

Baris pertama keluarannya adalah `tujuan`: nama platform. Baris berikutnya adalah rencana kerja, satu baris per tiket: `buat`, `ubah`, atau `tutup`. Kerjakan hanya baris itu. Tiket yang tidak muncul tidak disentuh, dengan satu pengecualian: pada pembersihan epic (`clean-epic-ticket`), tiket di bagian "Tiket yang diusulkan ditutup" pada `audit.md` yang sudah disetujui juga ditutup, dan link di bagian "Link yang diusulkan dilepas" juga dilepas.

Buka adapter platform itu: `{{SDD_HOME}}/workflow/boards/<platform>.md`. Semua operasi di bawah memakai cara yang tertulis di sana. Lokasi papan, pemetaan status, label role, dan kemampuan yang tersedia ada di `sdd.json`.

## 2. Epic

Jika `epic.json` belum punya `board_epic`, jalankan operasi **buat-epic** dengan ringkasan dari `prd.md` (atau `intake.md` pada epic kecil), lalu catat:

```
python3 {{SDD_HOME}}/scripts/sdd.py set-board-epic <epic> <KODE-EPIC>
```

## 3. Kerjakan rencana

Urutan: tiket contract dan tiket desain dulu, lalu tiket role, supaya ketergantungan bisa dibuat.

**buat**

1. Jalankan **buat-tiket**. Judul dari baris `# ...` tanpa `[KODE-TIKET]`. Isi adalah isi berkas tiket tanpa front matter. Label dari `board.role_labels` sesuai `role` atau `kind` tiket.
2. Catat segera: `python3 {{SDD_HOME}}/scripts/sdd.py record-push <epic> <nama-berkas-tanpa-.md> <KODE>`.
3. Untuk tiap `blocked_by`, jalankan **hubungkan**. Nama berkas diterjemahkan ke kode lewat `board-map.json`. Jika `board.capabilities.dependency` bernilai false, tulis baris `Diblokir oleh: <kode>` di awal isi tiket.
4. Jalankan **ubah-status**:
   - Tiket contract: ke kolom `selesai`, karena contract sudah disetujui pemiliknya di workflow ini. Sebut nama penyetuju di komentar.
   - Tiket desain: ke kolom `siap`. Workflow UI/UX yang mengerjakannya.
   - Tiket role: ke kolom `siap`, hanya jika semua pemblokirnya sudah selesai. Jika belum, biarkan di status awal dan laporkan.

**ubah**

Perbarui judul dan isi tiket yang ada, sesuaikan ketergantungan jika `blocked_by` berubah, lalu jalankan `record-push` lagi dengan kode yang sama. Tambahkan komentar singkat tentang apa yang berubah dan versi contract yang baru bila ada.

**tutup**

Berlaku untuk tiket yang berkasnya sudah dihapus dan tiket yang disetujui ditutup di `audit.md`. Pindahkan ke kolom `selesai` atau tutup dengan alasan, lalu catat: `python3 {{SDD_HOME}}/scripts/sdd.py record-push <epic> <nama> <KODE> --closed`. Jangan menghapus tiket.

## 4. Laporkan

Jalankan `pending-push` sekali lagi. Hasilnya harus "tidak ada yang perlu dikirim". Laporkan kepada operator: platform, kode epic, tabel tiket (berkas, kode, tindakan, status), kemampuan yang diganti teks, dan apa pun yang gagal atau dibiarkan.

Jika satu panggilan gagal, berhenti pada tiket itu, laporkan, dan jangan menebak perbaikannya. Tiket yang sudah tercatat tidak akan dibuat dua kali saat skill ini dijalankan ulang.
