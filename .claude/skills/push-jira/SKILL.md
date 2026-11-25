---
name: push-jira
description: Skill internal PjM, dijalankan SPV di sesi utama. Membuat, mengubah, atau menutup tiket di Jira setelah persetujuan manusia. Dipanggil oleh ketiga skill pintu masuk setelah /request-approval.
user-invocable: false
---

# Mengirim tiket ke Jira

Dijalankan di sesi utama, bukan di subagent, supaya operator melihat setiap perubahan Jira.

## 1. Pastikan persetujuan sah

```
python3 scripts/sdd.py pending-push <epic>
```

Perintah ini menolak jika persetujuan tidak ada atau ada berkas yang berubah sesudahnya. Jika menolak, berhenti dan kembali ke `/request-approval`. Jangan mengirim apa pun.

Keluarannya adalah rencana kerja, satu baris per tiket: `buat`, `ubah`, atau `tutup`. Kerjakan hanya baris itu. Tiket yang tidak muncul tidak disentuh.

## 2. Siapkan Jira

Baca bagian `jira` di `project.json`. Pakai tool Atlassian yang tersedia di sesi ini. Sebelum membuat tiket pertama, ambil metadata issue type proyek untuk memastikan nama issue type, status, dan jenis link di `project.json` memang ada. Jika ada yang tidak cocok atau masih berisi "ISI", berhenti dan tanyakan operator.

Jika `epic.json` belum punya `jira_epic`, buat epic di Jira dengan ringkasan dari `prd.md` (atau `intake.md` pada epic kecil), lalu catat:

```
python3 scripts/sdd.py set-jira <epic> <KODE-EPIC>
```

## 3. Kerjakan rencana

Urutan: tiket contract dulu, lalu tiket role, supaya link ketergantungan bisa dibuat.

**buat**

1. Buat issue dengan parent epic. Judul dari baris `# ...` tanpa `[KODE-TIKET]`. Deskripsi adalah isi tiket tanpa front matter.
2. Catat segera: `python3 scripts/sdd.py record-push <epic> <nama-berkas-tanpa-.md> <KODE>`.
3. Untuk tiap `blocked_by`, buat link sehingga tiket ini "is blocked by" tiket itu. Nama berkas diterjemahkan ke kode Jira lewat `jira-map.json`.
4. Pindahkan status:
   - Tiket contract: ke `done_status`, karena contract sudah disetujui pemiliknya di workflow ini. Sebut nama penyetuju di komentar.
   - Tiket role: ke `ready_status`, hanya jika semua pemblokirnya sudah selesai. Jika belum, biarkan di status awal dan laporkan.

**ubah**

Perbarui judul dan deskripsi issue yang ada, sesuaikan link jika `blocked_by` berubah, lalu jalankan `record-push` lagi dengan kode yang sama. Tambahkan komentar singkat yang menyebut apa yang berubah dan versi contract yang baru bila ada.

**tutup**

Berlaku untuk tiket yang berkasnya sudah dihapus dan tiket yang disetujui ditutup di `audit.md`. Pindahkan ke status tutup yang berlaku di proyek, beri komentar alasan, lalu catat: `python3 scripts/sdd.py record-push <epic> <nama> <KODE> --closed`. Jangan menghapus issue.

## 4. Laporkan

Jalankan `pending-push` sekali lagi. Hasilnya harus "tidak ada yang perlu dikirim". Laporkan kepada operator: kode epic, tabel tiket (berkas, kode Jira, tindakan, status), dan apa pun yang gagal atau dibiarkan.

Jika satu panggilan Jira gagal, berhenti pada tiket itu, laporkan, dan jangan menebak perbaikannya. Tiket yang sudah tercatat tidak akan dibuat dua kali saat skill ini dijalankan ulang.
