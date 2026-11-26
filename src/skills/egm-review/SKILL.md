---
name: egm-review
description: Skill internal Reviewer EGM. Menguji satu dokumen di sesi baru tanpa konteks dan menulis daftar temuan. Dijalankan oleh agen peran egm-reviewer.
user-invocable: false
---

# Review gate EGM

Brief memberimu lima hal: nama gate, akar proyek, dokumen yang diuji, rujukan yang boleh dibaca, dan lokasi berkas hasil. Baca dokumen yang diuji sampai habis sebelum membuka rujukan.

## Pertanyaan per gate

Setiap gate punya satu pertanyaan utama. Daftar di bawahnya adalah cara mengujinya.

**Gate `prd`: masalah dan scope jelas?**

- Bisakah kamu menyebut siapa yang punya masalah dan apa akibatnya, hanya dari dokumen ini?
- Apakah batas "tidak termasuk" cukup tegas untuk menolak permintaan tambahan?
- Bisakah setiap acceptance criteria diuji lulus atau gagal oleh orang lain?
- Adakah jalur gagal yang tidak punya acceptance criteria?
- Adakah istilah yang dipakai tanpa dijelaskan?

**Gate `flow`: setiap state layar tergambar?**

- Apakah setiap layar punya state kosong, memuat, berhasil, gagal, dan offline, atau alasan tertulis mengapa tidak berlaku?
- Pada state gagal, apakah jelas apa yang dilihat pengguna dan apa langkah berikutnya?
- Apakah setiap acceptance criteria di PRD bisa ditelusuri ke layar atau langkah flow?
- Adakah layar yang tidak bisa dicapai atau tidak punya jalan keluar?
- Adakah komponen yang tidak ada di design system dan tidak dicatat sebagai komponen baru?
- Apakah jawaban "Perlu tiket desain?" punya alasan, dan konsisten dengan jumlah komponen dan layar baru?

**Gate `contract`: contract cocok dengan mockup?**

- Apakah setiap data dari server yang disebut flow punya endpoint dan field?
- Apakah setiap state gagal di flow punya kode error dan pesan untuk pengguna?
- Apakah aturan validasi, batas ukuran, paginasi, dan rate limit tertulis di contract?
- Apakah versi di manifes sama dengan versi di berkas contract?
- Apakah contract membocorkan detail server: nama tabel, layanan internal, topologi?
- Adakah yang tertulis di `specs/` padahal klien membutuhkannya?

**Gate `tickets`: bisa dikerjakan tanpa bertanya?**

Uji tiap tiket seolah kamu yang harus mengerjakannya besok, hanya dengan tiket itu dan berkas yang ditautkannya.

- Apakah kamu tahu layar mana yang dibangun dan state apa saja yang ditangani?
- Apakah kamu tahu endpoint mana yang dipanggil, versi contract-nya, dan apa yang ditampilkan untuk tiap kode error?
- Bisakah setiap acceptance criteria diuji?
- Apakah tautan di tiket menunjuk ke berkas yang ada dan memuat hal yang dijanjikan?
- Menurut `{{SDD_HOME}}/workflow/context-matrix.md`, adakah isi yang bukan urusan role tiket ini, misalnya detail infrastruktur atau skema database di tiket Mobile?
- Adakah bagian yang kosong tanpa tulisan "Tidak ada"?
- Jika ada tiket desain, apakah ia memuat semua layar dan state yang dibutuhkan tiket Mobile?
- Apakah ketergantungan antar-tiket masuk akal dan tidak melingkar?

## Apa yang termasuk temuan

Temuan adalah sesuatu yang membuat pembaca berikutnya harus menebak, bertanya, atau memilih di antara dua tafsir. Tiga jenis:

| `type` | Arti |
| --- | --- |
| `tidak-jelas` | Ada, tetapi bisa ditafsirkan lebih dari satu cara |
| `bertentangan` | Dua bagian dokumen, atau dokumen dan rujukannya, saling menyangkal |
| `hilang` | Dibutuhkan untuk mengerjakan, tetapi tidak tertulis |

Yang bukan temuan: selera gaya bahasa, saran fitur tambahan, dan hal yang sudah dijawab dokumen dengan alasan tertulis. Jika dokumen menyatakan sesuatu sengaja tidak dicakup dan menyebut alasannya, jangan melaporkannya sebagai hilang.

Dokumen yang baik boleh menghasilkan nol temuan. Jangan mencari-cari supaya daftar terisi.

## Format hasil

Tulis satu berkas JSON di lokasi yang disebut brief. Jangan menulis berkas lain.

```json
{
  "gate": "tickets",
  "reviewed": ["tickets/mobile-01.md"],
  "findings": [
    {
      "type": "hilang",
      "where": "tickets/mobile-01.md, bagian 4",
      "text": "Kode error 413 ada di contract tetapi tiket tidak menyebut pesan untuk pengguna."
    }
  ]
}
```

Setiap `text` berdiri sendiri: sebut apa masalahnya dan apa akibatnya bagi pengerja, dalam satu atau dua kalimat. Jangan menulis cara memperbaikinya. Jika tidak ada temuan, `findings` berisi daftar kosong.
