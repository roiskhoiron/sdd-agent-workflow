---
name: size-epic
description: Skill internal SPV. Mengusulkan ukuran epic (kecil, sedang, besar) dan tahap yang dijalankan. Dipanggil oleh /initiate-epic-ticket.
user-invocable: false
---

# Menentukan ukuran epic

Baca `intake.md` di folder epic, lalu usulkan satu ukuran dengan alasan satu kalimat.

| Ukuran | Tanda | Tahap yang dijalankan | Gate |
| --- | --- | --- | --- |
| kecil | Satu role, tanpa endpoint baru, tanpa layar baru: perbaikan tampilan, ubah teks, bug kecil | Langsung `slice-tickets` | `tickets` |
| sedang | Fitur di satu layar dengan endpoint yang sudah ada di katalog contract | PRD, flow, contract, tiket | keempatnya |
| besar | Lintas role, atau butuh endpoint baru, atau mengubah contract | PRD, flow, contract, tiket | keempatnya |

Dua pertanyaan yang memutuskan: apakah pekerjaan ini menyentuh lebih dari satu role, dan apakah butuh endpoint baru atau perubahan contract? Jika salah satu jawabannya ya, ukurannya besar. Jika kamu ragu di antara dua ukuran, usulkan yang lebih besar.

Untuk memeriksa endpoint, baca `foundation/katalog-contract.md`. Jangan membaca Foundation lain.

Ukuran adalah keputusan operator. Tanyakan kepada operator dengan usulanmu sebagai pilihan pertama (pakai fitur pertanyaan pilihan bila alatmu punya), lalu catat jawabannya:

```
python3 {{SDD_HOME}}/scripts/sdd.py set-size <epic> <kecil|sedang|besar>
```

Pada ukuran sedang, PRD ditulis pendek (paling banyak setengah halaman) dan contract biasanya tidak berubah, sehingga `write-contract` hanya mencatat versi katalog yang dipakai.
