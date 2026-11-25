---
name: push-jira
description: Skill internal PjM, dijalankan SPV sendiri. Membuat, mengubah, atau menutup tiket di tracker proyek (lokal, GitHub Issues, atau Jira) setelah persetujuan manusia. Dipanggil oleh ketiga skill pintu masuk setelah /request-approval.
user-invocable: false
---

# Mengirim tiket ke tracker

Dijalankan SPV sendiri, bukan oleh agen peran, supaya operator melihat setiap perubahan.

## Aturan keras: uji coba tidak memakai Jira

Proyek dengan `"pilot": true` di `project.json`, atau tanpa kunci `pilot`, tidak pernah menulis ke Jira. Skrip menolak membuat rencana untuk gabungan itu. Jika skrip menolak, jangan mengubah `project.json` sendiri dan jangan memanggil tool Atlassian dengan cara lain. Hanya operator yang boleh menyetel `"pilot": false`.

## 1. Pastikan persetujuan sah dan baca tujuan

```
python3 {{SDD_HOME}}/scripts/sdd.py pending-push <epic>
```

Perintah ini menolak jika persetujuan tidak ada, ada berkas yang berubah sesudahnya, atau proyek pilot diarahkan ke Jira. Jika menolak, berhenti dan laporkan. Jangan mengirim apa pun.

Baris pertama keluarannya adalah `tujuan`: `lokal`, `github`, atau `jira`. Baris berikutnya adalah rencana kerja, satu baris per tiket: `buat`, `ubah`, atau `tutup`. Kerjakan hanya baris itu, hanya ke tujuan itu. Tiket yang tidak muncul tidak disentuh.

## 2. Cara kerja per tujuan

Tiga tujuan memakai langkah yang sama di bagian 3. Yang berbeda hanya cara tiap tindakan diwujudkan.

| Tindakan | `lokal` | `github` | `jira` |
| --- | --- | --- | --- |
| Tempat | `projects/<proyek>/tracker-lokal/<slug-epic>/` | Issues di `tracker.github_repo` | Proyek di bagian `jira` |
| Epic | Berkas `EPIC.md`, kode `LOKAL-0` | Issue berlabel `epic` | Issue bertipe `epic_issue_type` |
| Buat tiket | Berkas `LOKAL-<n>.md`, n berurutan | Issue baru, menyebut epic di baris pertama | Issue dengan parent epic |
| Diblokir oleh | Baris `Diblokir oleh: LOKAL-<n>` di awal berkas | Baris `Diblokir oleh #<n>` di awal isi issue | Link `blocks_link_type` |
| Siap dikerjakan | Baris `Status: siap` | Label `siap` | Status `ready_status` |
| Selesai atau tutup | Baris `Status: tutup` beserta alasan | Tutup issue dengan komentar alasan | Status tutup yang berlaku, dengan komentar |

Catatan per tujuan:

- **lokal**: tidak ada layanan luar yang disentuh. Folder `tracker-lokal/` sengaja berada di luar folder epic supaya persetujuan tidak batal.
- **github**: pakai integrasi GitHub yang tersedia di alatmu (tool MCP GitHub atau CLI `gh`). Jika sesi tidak punya akses ke repo itu, berhenti dan laporkan. Jangan pindah ke repo lain.
- **jira**: sebelum membuat tiket pertama, ambil metadata issue type proyek untuk memastikan nama issue type, status, dan jenis link di `project.json` memang ada. Jika ada yang tidak cocok atau masih berisi "ISI", berhenti dan tanyakan operator.

Jika `epic.json` belum punya kode epic, buat epic dengan ringkasan dari `prd.md` (atau `intake.md` pada epic kecil), lalu catat:

```
python3 {{SDD_HOME}}/scripts/sdd.py set-jira <epic> <KODE-EPIC>
```

## 3. Kerjakan rencana

Urutan: tiket contract dulu, lalu tiket role, supaya ketergantungan bisa dibuat.

**buat**

1. Buat tiket. Judul dari baris `# ...` tanpa `[KODE-TIKET]`. Isi adalah isi berkas tiket tanpa front matter.
2. Catat segera: `python3 {{SDD_HOME}}/scripts/sdd.py record-push <epic> <nama-berkas-tanpa-.md> <KODE>`.
3. Untuk tiap `blocked_by`, catat ketergantungannya. Nama berkas diterjemahkan ke kode tracker lewat `jira-map.json`.
4. Tandai status:
   - Tiket contract: selesai, karena contract sudah disetujui pemiliknya di workflow ini. Sebut nama penyetuju.
   - Tiket role: siap dikerjakan, hanya jika semua pemblokirnya sudah selesai. Jika belum, biarkan di status awal dan laporkan.

**ubah**

Perbarui judul dan isi tiket yang ada, sesuaikan ketergantungan jika `blocked_by` berubah, lalu jalankan `record-push` lagi dengan kode yang sama. Tambahkan catatan singkat tentang apa yang berubah dan versi contract yang baru bila ada.

**tutup**

Berlaku untuk tiket yang berkasnya sudah dihapus dan tiket yang disetujui ditutup di `audit.md`. Tutup dengan alasan, lalu catat: `python3 {{SDD_HOME}}/scripts/sdd.py record-push <epic> <nama> <KODE> --closed`. Jangan menghapus tiket.

## 4. Laporkan

Jalankan `pending-push` sekali lagi. Hasilnya harus "tidak ada yang perlu dikirim". Laporkan kepada operator: tujuan, kode epic, tabel tiket (berkas, kode, tindakan, status), dan apa pun yang gagal atau dibiarkan.

Jika satu panggilan gagal, berhenti pada tiket itu, laporkan, dan jangan menebak perbaikannya. Tiket yang sudah tercatat tidak akan dibuat dua kali saat skill ini dijalankan ulang.
