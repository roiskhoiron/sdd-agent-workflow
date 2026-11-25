---
name: request-approval
description: Skill internal SPV. Merangkum hasil dan temuan gate menjadi paket persetujuan, lalu mencatat keputusan pemilik manusia. Dipanggil oleh ketiga skill pintu masuk sebelum /push-jira.
user-invocable: false
---

# Meminta persetujuan manusia

Tidak ada jalur ke tracker yang melewati langkah ini. Skrip menolak persetujuan selama masih ada gate yang belum lolos, temuan yang belum diputuskan, contract berubah yang belum disetujui pemiliknya, atau tiket yang gagal lint.

## 1. Periksa kesiapan

```
python3 {{SDD_HOME}}/scripts/sdd.py status <epic>
python3 {{SDD_HOME}}/scripts/sdd.py lint <epic>
```

Jika lint gagal, kembalikan ke `pjm` dengan daftar masalahnya, lalu jalankan ulang gate `tickets`.

## 2. Tulis paket persetujuan

Tulis `approval.md` di folder epic mengikuti `{{SDD_HOME}}/workflow/templates/approval.md`. Ambil temuan dari berkas `reviews/` putaran terakhir tiap gate. Untuk jenis modify, daftar "yang kamu setujui" hanya memuat dokumen dan tiket yang berubah menurut `changes/NN-impact.md`. Untuk jenis clean, isinya `audit.md` dan `foundation-proposal.md`, dan langkah 1 serta 3 dilewati.

Paket ini untuk manusia yang akan memutuskan, jadi tulis apa adanya. Jangan melunakkan temuan dan jangan menyimpulkan bahwa semuanya sudah baik.

## 3. Minta keputusan atas tiap temuan terbawa

Setiap temuan berstatus `ditolak` atau `diteruskan` diputuskan operator satu per satu. Tampilkan temuan dan jawaban penulis, tanyakan kepada operator, lalu catat:

```
python3 {{SDD_HOME}}/scripts/sdd.py decide <epic> <id-temuan> <terima|revisi> --by "<nama>" --note "<alasan>"
```

`terima` berarti operator setuju dengan jawaban penulis. `revisi` berarti dokumen harus diubah: panggil penulis gate itu dengan catatan operator, jalankan `reopen <epic> <gate>`, ulangi gate sesuai `{{SDD_HOME}}/workflow/menjalankan-gate.md`, lalu mulai lagi dari langkah 1.

Jangan mengelompokkan temuan menjadi satu pertanyaan "setujui semua". Persetujuan yang menjadi formalitas adalah risiko terbesar workflow ini.

## 4. Minta persetujuan akhir

Tunjukkan lokasi `approval.md` dan daftar tiket, lalu tanyakan apakah operator setuju. Tanyakan juga nama yang dicatat sebagai penyetuju.

- **Setuju**: jalankan `python3 {{SDD_HOME}}/scripts/sdd.py approve <epic> --by "<nama>"`. Untuk jenis clean tambahkan `--clean`, karena epic yang dibatalkan bisa saja belum pernah lolos gate. Jika skrip menolak, tampilkan alasannya dan selesaikan dulu.
- **Belum**: minta komentarnya, panggil penulis yang relevan dengan komentar itu, buka ulang gate dokumen yang berubah, lalu mulai lagi dari langkah 1.

Persetujuan mengunci isi folder epic. Setiap perubahan berkas sesudahnya membatalkan persetujuan, dan `/push-jira` akan menolak berjalan.

Jangan pernah menjalankan `approve` atau `decide` tanpa jawaban eksplisit operator di percakapan ini.
