---
name: design-flow
description: Skill internal Product Designer. Menyusun flow layar, mockup, dan daftar state dari PRD. Dijalankan oleh subagent product-designer.
user-invocable: false
---

# Menyusun flow dan mockup

Masukan: `prd.md` di folder epic, `foundation/design-system.md`, dan `mockup_tool` di `project.json`. Keluaran: `flow.md`, mengikuti `workflow/templates/flow.md`.

Cara kerja mengikuti `mockup_tool`:

- `figma` atau `claude-design`: jika PRD atau brief memberi tautan mockup, rujuk tautan itu dan uraikan tiap layar dalam teks. Jika belum ada mockup, tulis wireframe teks dan catat di laporan akhir bahwa mockup visual masih harus dibuat Lead UI/UX.
- `teks`: wireframe teks adalah mockup-nya. Uraikan susunan layar dari atas ke bawah.

Yang membuat flow lolos gate:

- Setiap layar punya tabel lima state: kosong, memuat, berhasil, gagal, offline. State yang tidak berlaku tetap ditulis dengan keterangan "tidak berlaku" dan alasannya di "Keputusan desain".
- State gagal menyebut apa yang dilihat pengguna dan apa yang bisa ia lakukan selanjutnya.
- Setiap acceptance criteria di PRD bisa ditelusuri ke minimal satu layar atau satu langkah flow.
- Komponen yang dipakai disebut dengan nama dari design system. Komponen yang belum ada dicatat sebagai komponen baru.
- Data yang ditampilkan disebut asalnya: masukan pengguna, penyimpanan lokal, atau server. Bagian ini yang nanti dicocokkan HoE dengan contract.

Jangan merancang endpoint atau bentuk data server. Cukup sebut data apa yang dibutuhkan layar.

Reviewer gate akan menguji satu hal: apakah setiap state layar tergambar.
