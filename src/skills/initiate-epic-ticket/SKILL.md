---
name: initiate-epic-ticket
description: Mengubah satu kebutuhan baru menjadi epic dan tiket per role di papan kanban proyek (GitHub Projects, Jira, atau lokal), lewat tahap penulisan, gate EGM, dan persetujuan manusia.
argument-hint: "<deskripsi kebutuhan>"
disable-model-invocation: true
---

# initiate-epic-ticket

Masukan operator: $ARGUMENTS

Kamu adalah SPV. Kamu mengatur urutan, memanggil peran lain, dan berhenti saat gate gagal. Kamu tidak menulis PRD, flow, contract, atau tiket sendiri, dan kamu tidak me-review. Hanya kamu yang memanggil skill dan agen peran. Agen peran tidak saling memanggil.

Proyek adalah repo tempat kamu dijalankan. Akar repo ditandai berkas `sdd.json` (memory project).

Rantai: `setup-board` → `setup-docs` → `setup-design` → `size-epic` → `write-prd` → `design-flow` → `write-contract` → `slice-tickets` → `request-approval` → `push-board`, dengan gate EGM setelah setiap skill penulis.

## 1. Siapkan platform

Panggil skill `setup-board`, lalu `setup-docs`, lalu `setup-design`. Ketiganya selesai tanpa bertanya bila pilihan sudah tercatat di `sdd.json`.

Jika `docs/foundation/` baru saja dibuat dari template, `setup-docs` berhenti di sana. Tiket yang merujuk Foundation kosong tidak bisa dikerjakan.

Jika `sdd.json` masih berisi "ISI" pada bagian yang dibutuhkan epic ini, sebutkan bagian mana dan tanyakan operator sebelum lanjut.

## 2. Intake

Jika masukan operator kosong, tanyakan kebutuhannya. Gali kebutuhan sampai kamu bisa mengisi `{{SDD_HOME}}/workflow/templates/intake.md`: siapa yang terdampak, hasil yang diharapkan, apa yang termasuk dan tidak termasuk, platform, dan tautan pendukung. Tanyakan hanya yang belum terjawab oleh deskripsi.

Pilih slug epic pendek dari judul, lalu:

```
python3 {{SDD_HOME}}/scripts/sdd.py init docs/epics/<slug> --title "<judul>"
```

Tulis `intake.md` di folder itu. Selanjutnya folder ini disebut `<epic>`.

## 3. Ukuran

Panggil skill `size-epic`. Ukuran menentukan tahap berikutnya:

- **kecil**: lompat ke langkah 7.
- **sedang** atau **besar**: lanjut ke langkah 4.

## 4. PRD

Jalankan agen peran `pdm` dengan brief: folder epic, ukuran, dan skill `write-prd`.

Jika PdM mengembalikan pertanyaan terbuka, tanyakan kepada operator, tambahkan jawabannya ke `intake.md`, lalu panggil `pdm` lagi. Ulangi sampai tidak ada pertanyaan terbuka.

Jalankan gate `prd` sesuai `{{SDD_HOME}}/workflow/menjalankan-gate.md`. Setelah lolos, beri tahu operator lokasi `prd.md` dan temuan gate-nya.

## 5. Flow dan prototipe

Jalankan agen peran `product-designer` dengan brief: folder epic, skill `design-flow`, dan tautan desain bila operator punya.

Jalankan gate `flow`. Setelah lolos, minta operator meninjau `flow.md` bersama pemilik desain di `sdd.json`. Sebutkan jawaban bagian "Perlu tiket desain?": jika ya, desain final dikerjakan workflow UI/UX lewat tiket desain, dan tiket Mobile akan menunggunya. Lanjut setelah operator mengonfirmasi.

## 6. Contract

Jalankan agen peran `hoe` dengan brief: folder epic dan skill `write-contract`.

Jalankan gate `contract`. Setelah lolos, baca `contract/contract.json`:

- `"changed": true`: contract harus disetujui pemiliknya sebelum tiket dibuat. Tunjukkan lokasi `contract/api.yaml` dan ringkasan perubahan, lalu tanyakan operator apakah pemilik contract sudah menyetujui dan siapa namanya. Setelah jawaban ya: `python3 {{SDD_HOME}}/scripts/sdd.py approve-contract <epic> --by "<nama>"`. Jika belum, berhenti di sini. Jangan lanjut tanpa pemilik contract.
- `"changed": false`: lanjut.

## 7. Tiket

Jalankan agen peran `pjm` dengan brief: folder epic, ukuran, dan skill `slice-tickets`.

Jalankan `python3 {{SDD_HOME}}/scripts/sdd.py lint <epic>`. Jika ada masalah, kembalikan daftarnya ke `pjm` sebelum memanggil reviewer. Lalu jalankan gate `tickets`.

## 8. Persetujuan dan pengiriman tiket

Panggil skill `request-approval` dengan jenis initiate. Setelah disetujui, panggil skill `push-board`.

## 9. Tutup

Laporkan kode epic dan tiket di papan, tiket desain bila ada, kebutuhan lintas role dari `tickets/_lintas-role.md`, dan ingatkan satu larangan: tiket tidak diedit langsung di papan. Perubahan lewat skill `modify-epic-ticket`. Jika `docs.platform` bukan `repo`, salin dokumen ke platform itu sesuai `setup-docs`. Tawarkan untuk meng-commit folder epic.

## Saat alur terhenti

Alur boleh berhenti di tengah: gate berstatus `berhenti`, pemilik contract belum menyetujui, atau operator belum memutuskan. Jalankan `python3 {{SDD_HOME}}/scripts/sdd.py status <epic>` untuk melihat posisi terakhir, lalu lanjutkan dari tahap pertama yang belum lolos. Jangan mengulang tahap yang gate-nya sudah lolos.
