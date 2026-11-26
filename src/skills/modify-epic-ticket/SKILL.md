---
name: modify-epic-ticket
description: Memperbarui dokumen dan tiket yang terdampak saat kebutuhan atau contract berubah setelah epic dibuat. Yang tidak terdampak tidak disentuh.
argument-hint: "<epic> <perubahan yang diminta>"
disable-model-invocation: true
---

# modify-epic-ticket

Masukan operator: $ARGUMENTS

Kamu adalah SPV. Aturan pemanggilan sama dengan `/initiate-epic-ticket`: hanya kamu yang memanggil skill dan agen peran, dan kamu tidak menulis atau me-review dokumen sendiri.

Rantai: `setup-board` → `setup-docs` → `setup-design` → `impact-check` → skill penulis yang terdampak saja → `slice-tickets` → `request-approval` → `push-board`, dengan gate EGM setelah setiap skill penulis.

## 1. Siapkan platform dan temukan epic

Panggil skill `setup-board`, `setup-docs`, dan `setup-design`. Ketiganya selesai tanpa bertanya bila pilihan sudah tercatat.

Epic boleh disebut dengan slug folder atau kode epic di papan. Untuk kode papan, cari `board_epic` yang cocok di `docs/epics/*/epic.json`. Jika tidak ketemu, tanyakan. Jalankan `python3 {{SDD_HOME}}/scripts/sdd.py status <epic>` untuk melihat keadaannya.

## 2. Dampak

Panggil skill `impact-check`. Lanjut hanya setelah operator mengonfirmasi daftar dampaknya.

## 3. Tulis ulang yang terdampak

Kerjakan dari hulu ke hilir, hanya dokumen yang tercantum di `changes/NN-impact.md`:

| Dokumen terdampak | Subagent | Skill | Gate |
| --- | --- | --- | --- |
| `prd.md` | `pdm` | `write-prd` | `prd` |
| `flow.md` | `product-designer` | `design-flow` | `flow` |
| `contract/`, `specs/` | `hoe` | `write-contract` | `contract` |

Untuk tiap dokumen: jalankan `python3 {{SDD_HOME}}/scripts/sdd.py reopen <epic> <gate>`, panggil penulisnya dengan brief berisi folder epic, perubahan yang diminta, dan path `changes/NN-impact.md`, lalu jalankan gate sesuai `{{SDD_HOME}}/workflow/menjalankan-gate.md`.

Jika contract berubah, versinya naik dan persetujuan pemilik contract yang lama tidak berlaku lagi. Minta persetujuan baru seperti langkah 6 di `/initiate-epic-ticket`.

## 4. Tiket

Jalankan `reopen <epic> tickets`, lalu jalankan agen peran `pjm` dengan skill `slice-tickets` dan daftar tiket terdampak dari berkas dampak. Tegaskan di brief: tiket lain tidak disentuh.

Jalankan `lint`, lalu gate `tickets`.

## 5. Persetujuan dan pengiriman tiket

Panggil skill `request-approval` dengan jenis modify, lalu skill `push-board`. Skrip hanya akan mengirim tiket yang isinya berubah, tiket baru, dan tiket yang berkasnya dihapus.

## 6. Tutup

Laporkan tiket yang diubah, dibuat, dan ditutup beserta kodenya di papan, dan versi contract sekarang. Jika ada tiket terdampak yang sudah dikerjakan delivery, sebutkan secara khusus: operator perlu memberi tahu pengerjanya.
