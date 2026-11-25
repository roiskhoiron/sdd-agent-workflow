---
name: write-contract
description: Skill internal HoE. Menulis API contract berversi, delta data, dan dampak infrastruktur. Dijalankan oleh subagent hoe.
user-invocable: false
---

# Menulis contract dan delta

Masukan: `prd.md`, `flow.md`, dan seluruh `foundation/` proyek. Keluaran ada di dua folder dengan pembaca yang berbeda:

| Berkas | Isi | Dibaca oleh |
| --- | --- | --- |
| `contract/contract.json` | Manifes: versi, apakah berubah, sumber | Semua, termasuk skrip lint |
| `contract/api.yaml` | API contract klien ke server, OpenAPI 3.1 | Semua role |
| `specs/data-delta.md` | Perubahan skema dan migrasi | Backend |
| `specs/server-logic.md` | Logika bisnis sisi server, jika ada | Backend |
| `specs/backend-events.md` | Contract antar-backend, jika ada | Backend |
| `specs/infra-impact.md` | Dampak infrastruktur | DevOps |

Template ada di `workflow/templates/`. Berkas `specs/` yang tidak relevan tidak perlu dibuat, kecuali `data-delta.md` dan `infra-impact.md` yang selalu ada dan diisi "Tidak ada perubahan" bila kosong.

## Dua keadaan

**Contract tidak berubah.** Semua endpoint yang dibutuhkan flow sudah ada di katalog. Tulis manifes dengan `"changed": false`, `version` sama dengan versi katalog, dan `source` menunjuk ke berkas di `foundation/contracts/`. Jangan membuat `api.yaml`.

**Contract berubah.** Salin contract dari katalog ke `contract/api.yaml`, terapkan perubahan, dan naikkan versi: angka tengah untuk penambahan yang tidak merusak klien lama, angka depan untuk perubahan yang merusak. Manifes berisi `"changed": true`, `previous_version`, dan `summary`. Versi di manifes dan di `info.version` harus sama.

## Yang membuat contract lolos gate

- Setiap data yang disebut `flow.md` berasal dari server punya endpoint dan field di contract.
- Setiap state gagal di flow punya kode error di contract, lengkap dengan pesan untuk pengguna.
- Aturan validasi, batas ukuran data, paginasi, dan rate limit tertulis di contract, bukan hanya di `specs/`.
- Contract tidak menyebut nama tabel, layanan internal, atau topologi server.
- Keputusan arsitektur baru dicatat sebagai draft ADR di `specs/adr-draft.md`, dengan alternatif yang ditolak.

Reviewer gate akan menguji satu hal: apakah contract cocok dengan mockup.
