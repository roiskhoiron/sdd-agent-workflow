---
name: slice-tickets
description: Skill internal PjM. Memecah epic menjadi tiket per role sesuai matriks konteks, dengan ketergantungan. Dijalankan oleh agen peran pjm.
user-invocable: false
---

# Memecah epic menjadi tiket

Masukan: seluruh folder epic, `sdd.json`, dan `{{SDD_HOME}}/workflow/context-matrix.md`. Keluaran: berkas di `tickets/`.

| Berkas | Kapan dibuat | Template |
| --- | --- | --- |
| `tickets/contract-01.md` | Hanya jika `contract/contract.json` berisi `"changed": true` | `{{SDD_HOME}}/workflow/templates/ticket-contract.md` |
| `tickets/design-01.md` | Hanya jika `flow.md` menjawab "Perlu tiket desain?" dengan ya | `{{SDD_HOME}}/workflow/templates/ticket-design.md` |
| `tickets/mobile-NN.md` | Satu per potongan kerja Mobile | `{{SDD_HOME}}/workflow/templates/ticket-mobile.md` |
| `tickets/_lintas-role.md` | Jika epic butuh pekerjaan Backend, Frontend web, atau DevOps | Daftar bebas |

Workflow ini menghasilkan tiket Mobile, tiket contract, dan tiket desain untuk workflow UI/UX. Pekerjaan role lain dicatat di `_lintas-role.md` supaya operator membuat tiketnya dengan cara yang berlaku sekarang. Berkas berawalan garis bawah tidak dikirim ke papan.

## Memotong

Satu tiket adalah satu hasil yang bisa diuji sendiri, biasanya satu layar atau satu alur. Jika sebuah tiket butuh lebih dari sekitar tujuh acceptance criteria, pecah lagi. Epic kecil hampir selalu menjadi satu tiket.

## Mengisi tiket Mobile

Tiket harus bisa dikerjakan agen delivery tanpa bertanya balik dan tanpa membaca PRD.

- Pertahankan sembilan bagian dan urutannya. Bagian yang tidak relevan diisi "Tidak ada", bukan dihapus, supaya reviewer tahu itu keputusan dan bukan kelupaan. Bagian 1, 2, dan 7 tidak boleh "Tidak ada".
- Salin dari sumber yang ditandai Penuh di matriks: tujuan dan acceptance criteria dari `prd.md`, layar dan state dari `flow.md`, endpoint dan kode error dari contract.
- Jangan menyalin apa pun dari `specs/`. Jika tiket butuh informasi yang hanya ada di sana, laporkan sebagai contract yang belum lengkap.
- Bagian 8 berisi tautan ke `docs/foundation/design-system.md` dan ke `references` di `sdd.json`. Jangan menyalin isinya.
- Front matter: `size` mengikuti ukuran epic, `contract_version` sama dengan manifes contract, `blocked_by` berisi `contract-01` jika tiket contract ada dan `design-01` jika tiket desain ada.
- Bagian 3 merujuk prototipe dan halaman handover. Jika ada tiket desain, tulis bahwa tautannya diisi dari hasil tiket desain itu, dan rujuk `flow.md` untuk daftar state. Tiket yang tidak memakai contract menulis `contract_version: tidak ada`.
- Judul memakai `[KODE-TIKET]` apa adanya. Kode asli diisi saat tiket masuk papan.
- Hapus semua placeholder template: `...` dan `[tautan]`.

Pada epic kecil tidak ada `prd.md` atau `flow.md`. Sumbernya `intake.md`, dan bagian 3 sampai 6 diisi seperlunya atau "Tidak ada".

## Mengisi tiket desain

Isi dari `flow.md`: daftar layar, state, komponen baru, dan rujukan berkas desain tim. Tiket desain tidak memuat contract atau detail server. Bagian "Tiket yang menunggu" berisi semua tiket Mobile di epic ini.

## Saat dipanggil untuk perubahan

Jika brief menyertakan daftar tiket terdampak, ubah hanya tiket itu. Tiket lain jangan disentuh, termasuk untuk merapikan kalimat. Tiket yang tidak lagi dibutuhkan dihapus berkasnya.

Reviewer gate akan menguji satu hal: apakah tiket bisa dikerjakan tanpa bertanya.
