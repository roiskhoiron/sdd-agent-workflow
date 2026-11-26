---
name: design-flow
description: Skill internal Product Designer. Menyusun flow layar, prototipe atau mockup, dan daftar state dari PRD, lalu memutuskan apakah epic butuh tiket desain. Dijalankan oleh agen peran product-designer.
user-invocable: false
---

# Menyusun flow dan prototipe

Masukan: `prd.md` di folder epic, `docs/foundation/design-system.md`, dan bagian `design` di `sdd.json`. Keluaran: `flow.md`, mengikuti `{{SDD_HOME}}/workflow/templates/flow.md`.

## Platform desain

Baca `design.platform` dan `design.location` di `sdd.json`:

| Platform | Cara kerja |
| --- | --- |
| `figcraft` (default) atau `figma` | Baca berkas desain tim lewat tool MCP platform itu: komponen yang ada, layar serupa, token. Rujuk layar yang relevan dengan tautannya. |
| `claude-design` | Rujuk tautan desain yang diberikan operator dan uraikan tiap layar dalam teks. |
| Integrasi tidak tersedia di alatmu | Tulis wireframe teks dan catat di laporan akhir bahwa berkas desain tidak terbaca langsung. |

Kamu tidak membuat desain final di berkas desain tim.

## Perlu tiket desain?

Jawab di bagian "Perlu tiket desain?" pada `flow.md`:

- **Ya**, jika epic butuh komponen baru di design system atau banyak layar baru. `flow.md` menjadi brief untuk workflow UI/UX, dan `slice-tickets` membuat tiket desain yang memblokir tiket Mobile dan Frontend web.
- **Tidak**, jika layar bisa disusun dari komponen dan pola yang sudah ada. Flow dan rujukan desain di `flow.md` cukup untuk tiket Mobile.

Tulis alasannya dalam satu kalimat. Jika ragu, jawab ya.

Yang membuat flow lolos gate:

- Setiap layar punya tabel lima state: kosong, memuat, berhasil, gagal, offline. State yang tidak berlaku tetap ditulis dengan keterangan "tidak berlaku" dan alasannya di "Keputusan desain".
- State gagal menyebut apa yang dilihat pengguna dan apa yang bisa ia lakukan selanjutnya.
- Setiap acceptance criteria di PRD bisa ditelusuri ke minimal satu layar atau satu langkah flow.
- Komponen yang dipakai disebut dengan nama dari design system. Komponen yang belum ada dicatat sebagai komponen baru.
- Data yang ditampilkan disebut asalnya: masukan pengguna, penyimpanan lokal, atau server. Bagian ini yang nanti dicocokkan HoE dengan contract.

Jangan merancang endpoint atau bentuk data server. Cukup sebut data apa yang dibutuhkan layar.

Reviewer gate akan menguji satu hal: apakah setiap state layar tergambar, dan apakah keputusan tiket desain punya alasan.
