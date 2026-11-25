---
name: write-prd
description: Skill internal PdM. Menulis PRD ringkas dan acceptance criteria dari intake. Dijalankan oleh subagent pdm.
user-invocable: false
---

# Menulis PRD ringkas

Masukan: `intake.md` di folder epic. Keluaran: `prd.md` di folder yang sama, mengikuti `workflow/templates/prd.md`.

Pembaca PRD ini adalah Product Designer, HoE, PjM, dan seorang reviewer yang tidak tahu apa-apa tentang percakapan sebelumnya. Mereka tidak membaca intake. Semua yang mereka butuhkan harus ada di PRD.

Yang membuat PRD lolos gate:

- **Masalah** menyebut siapa yang mengalaminya dan apa akibatnya sekarang, bukan sekadar fitur yang diminta.
- **Scope** punya daftar "tidak termasuk" yang nyata. Hal yang wajar diduga termasuk tetapi sebenarnya tidak, harus disebut di sana.
- **Acceptance criteria** berbentuk Given/When/Then, bisa diuji, dan mencakup jalur gagal, bukan hanya jalur berhasil.
- **Batasan dan keputusan** mencatat alasan atas hal yang sengaja tidak dicakup. Tanpa itu, reviewer akan melaporkannya sebagai hal yang hilang.
- Tidak ada istilah internal yang dipakai tanpa dijelaskan saat pertama muncul.

PRD tidak memuat rancangan teknis: nama tabel, bentuk endpoint, pilihan pustaka. Itu wilayah HoE.

Panjang: ukuran besar paling banyak dua halaman, ukuran sedang paling banyak setengah halaman.

Jika intake tidak cukup untuk menulis satu bagian, tulis pertanyaannya di "Pertanyaan terbuka" dan jangan menebak. Reviewer gate akan menguji satu hal: apakah masalah dan scope jelas.
