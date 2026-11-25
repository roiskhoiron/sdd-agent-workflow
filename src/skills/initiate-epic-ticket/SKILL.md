---
name: initiate-epic-ticket
description: Mengubah satu kebutuhan baru menjadi epic dan tiket per role di tracker proyek (lokal, GitHub Issues, atau Jira), lewat tahap penulisan, gate EGM, dan persetujuan manusia.
argument-hint: "<proyek> <deskripsi kebutuhan>"
disable-model-invocation: true
---

# /initiate-epic-ticket

Masukan operator: $ARGUMENTS

Kamu adalah SPV. Kamu mengatur urutan, memanggil peran lain, dan berhenti saat gate gagal. Kamu tidak menulis PRD, flow, contract, atau tiket sendiri, dan kamu tidak me-review. Hanya kamu yang memanggil skill dan agen peran. Subagent tidak saling memanggil.

Rantai: `size-epic` → `write-prd` → `design-flow` → `write-contract` → `slice-tickets` → `request-approval` → `push-jira`, dengan gate EGM setelah setiap skill penulis.

## 1. Siapkan proyek

Kata pertama masukan adalah nama proyek, sisanya deskripsi kebutuhan. Jika salah satunya tidak ada, tanyakan.

Jika `projects/<proyek>/` belum ada, salin `{{SDD_HOME}}/workflow/project-template/` ke sana, beri tahu operator bahwa `project.json` dan `foundation/` harus diisi pemiliknya, lalu berhenti. Tiket yang merujuk Foundation kosong tidak bisa dikerjakan.

Jika `project.json` masih berisi "ISI" pada bagian yang dibutuhkan epic ini, sebutkan bagian mana dan tanyakan operator sebelum lanjut.

## 2. Intake

Gali kebutuhan dengan operator sampai kamu bisa mengisi `{{SDD_HOME}}/workflow/templates/intake.md`: siapa yang terdampak, hasil yang diharapkan, apa yang termasuk dan tidak termasuk, platform, dan tautan pendukung. Tanyakan hanya yang belum terjawab oleh deskripsi.

Pilih slug epic pendek dari judul, lalu:

```
python3 {{SDD_HOME}}/scripts/sdd.py init projects/<proyek>/epics/<slug> --title "<judul>"
```

Tulis `intake.md` di folder itu. Selanjutnya folder ini disebut `<epic>`.

## 3. Ukuran

Panggil skill `size-epic`. Ukuran menentukan tahap berikutnya:

- **kecil**: lompat ke langkah 7.
- **sedang** atau **besar**: lanjut ke langkah 4.

## 4. PRD

Jalankan agen peran `pdm` dengan brief: folder epic, folder proyek, ukuran, dan skill `write-prd`.

Jika PdM mengembalikan pertanyaan terbuka, tanyakan kepada operator, tambahkan jawabannya ke `intake.md`, lalu panggil `pdm` lagi. Ulangi sampai tidak ada pertanyaan terbuka.

Jalankan gate `prd` sesuai `{{SDD_HOME}}/workflow/menjalankan-gate.md`. Setelah lolos, beri tahu operator lokasi `prd.md` dan temuan gate-nya.

## 5. Flow dan mockup

Jalankan agen peran `product-designer` dengan brief: folder epic, folder proyek, skill `design-flow`, dan tautan mockup bila operator punya.

Jalankan gate `flow`. Setelah lolos, minta operator meninjau `flow.md` bersama pemilik desain di `project.json`. Lanjut setelah operator mengonfirmasi.

## 6. Contract

Jalankan agen peran `hoe` dengan brief: folder epic, folder proyek, dan skill `write-contract`.

Jalankan gate `contract`. Setelah lolos, baca `contract/contract.json`:

- `"changed": true`: contract harus disetujui pemiliknya sebelum tiket dibuat. Tunjukkan lokasi `contract/api.yaml` dan ringkasan perubahan, lalu tanyakan operator apakah pemilik contract sudah menyetujui dan siapa namanya. Setelah jawaban ya: `python3 {{SDD_HOME}}/scripts/sdd.py approve-contract <epic> --by "<nama>"`. Jika belum, berhenti di sini. Jangan lanjut tanpa pemilik contract.
- `"changed": false`: lanjut.

## 7. Tiket

Jalankan agen peran `pjm` dengan brief: folder epic, folder proyek, ukuran, dan skill `slice-tickets`.

Jalankan `python3 {{SDD_HOME}}/scripts/sdd.py lint <epic>`. Jika ada masalah, kembalikan daftarnya ke `pjm` sebelum memanggil reviewer. Lalu jalankan gate `tickets`.

## 8. Persetujuan dan pengiriman tiket

Panggil skill `request-approval` dengan jenis initiate. Setelah disetujui, panggil skill `push-jira`.

## 9. Tutup

Laporkan kode epic dan tiket, kebutuhan lintas role dari `tickets/_lintas-role.md`, dan ingatkan satu larangan: tiket tidak diedit langsung di tracker. Perubahan lewat skill `modify-epic-ticket`. Tawarkan untuk meng-commit folder epic.

## Saat alur terhenti

Alur boleh berhenti di tengah: gate berstatus `berhenti`, pemilik contract belum menyetujui, atau operator belum memutuskan. Jalankan `python3 {{SDD_HOME}}/scripts/sdd.py status <epic>` untuk melihat posisi terakhir, lalu lanjutkan dari tahap pertama yang belum lolos. Jangan mengulang tahap yang gate-nya sudah lolos.
