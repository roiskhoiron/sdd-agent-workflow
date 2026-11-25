# Matriks konteks

Matriks ini menentukan apa yang masuk ke tiket tiap role. PjM memakainya saat memecah epic, dan Reviewer EGM memakainya saat menguji tiket.

| Jenis spesifikasi | Sumber di folder epic | Mobile | Backend | Frontend web | DevOps |
| --- | --- | --- | --- | --- | --- |
| Tujuan bisnis dan acceptance criteria | `prd.md` | Penuh | Penuh | Penuh | Ringkas |
| Mockup dan flow layar | `flow.md` | Penuh (layar mobile) | Tidak | Penuh (layar web) | Tidak |
| API contract klien ke server | `contract/` | Penuh | Penuh | Penuh | Rujukan |
| Contract antar-backend (event, integrasi) | `specs/backend-events.md` | Tidak | Penuh | Tidak | Rujukan |
| Delta database dan migrasi | `specs/data-delta.md` | Tidak | Penuh | Tidak | Rujukan |
| Logika bisnis sisi server | `specs/server-logic.md` | Tidak | Penuh | Tidak | Tidak |
| Infrastruktur dan keamanan infra | `specs/infra-impact.md` | Tidak | Rujukan | Tidak | Penuh |
| Konfigurasi environment (base URL, feature flag) | `project.json` bagian `references` | Penuh | Penuh | Penuh | Penuh |

Arti nilai:

- **Penuh**: isi yang relevan disalin ke tiket.
- **Ringkas**: satu sampai dua kalimat ditambah tautan.
- **Rujukan**: tiket hanya berisi tautan.
- **Tidak**: tidak disebut sama sekali, termasuk sebagai tautan.

Untuk API contract, "Penuh" berarti tiket mencantumkan endpoint yang dipakai, kode error yang harus ditangani, dan versi contract. Skema lengkapnya tetap di berkas contract dan dirujuk, tidak disalin.

## Dua aturan pelengkap

1. Yang dibutuhkan klien dari server harus sudah ada di contract. Jika tiket Mobile butuh informasi yang hanya ada di `specs/`, itu tanda contract belum lengkap. Kembalikan ke HoE, jangan menyalin dari `specs/`.
2. Keamanan sisi klien tetap urusan Mobile: penyimpanan token, certificate pinning, izin perangkat. Yang dikeluarkan dari tiket Mobile hanya keamanan infrastruktur server.

## Urutan ketergantungan

Tiket role tidak boleh berstatus siap sebelum contract yang dirujuknya disetujui. Jika contract berubah di epic ini, ada satu tiket contract, dan setiap tiket role yang memakai contract itu mencatat `blocked_by` ke tiket tersebut.

## Foundation yang boleh dimuat tiap peran

| Dokumen Foundation | Dimuat oleh |
| --- | --- |
| `infrastruktur.md` | HoE, tiket DevOps |
| `stack-backend.md` | HoE, tiket Backend |
| `skema-database.md` | HoE, tiket Backend |
| `katalog-contract.md` | semua |
| `design-system.md` | Product Designer, tiket Mobile, tiket Frontend web |
| `adr.md` | HoE, SPV |

Tiket merujuk Foundation dengan tautan dan tidak menyalin isinya.
