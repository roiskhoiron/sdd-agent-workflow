# Menjalankan satu gate EGM

Prosedur ini dijalankan SPV setelah setiap skill penulis. Skrip `{{SDD_HOME}}/scripts/sdd.py` yang menentukan status gate, bukan penilaianmu.

## Dokumen per gate

| Gate | Penulis | Dokumen yang diuji | Rujukan yang boleh dibaca reviewer |
| --- | --- | --- | --- |
| `prd` | `pdm` | `prd.md` | tidak ada |
| `flow` | `product-designer` | `flow.md` | `prd.md`, `docs/foundation/design-system.md` |
| `contract` | `hoe` | `contract/`, `specs/` | `prd.md`, `flow.md`, `docs/contracts/katalog.md` |
| `tickets` | `pjm` | `tickets/*.md` | `{{SDD_HOME}}/workflow/context-matrix.md`, dan untuk tiap tiket hanya berkas yang ditautkan tiket itu |

Pada gate `tickets`, reviewer tidak diberi `prd.md` atau `specs/`. Ia harus bisa memahami tiket dari tiket itu sendiri dan rujukannya, sama seperti agen delivery nanti.

## Langkah

1. Jalankan `python3 {{SDD_HOME}}/scripts/sdd.py gate <epic> <gate>` dan ikuti statusnya:

   | Status | Tindakan |
   | --- | --- |
   | `belum-direview` | Lanjut ke langkah 2 dengan N = 1. |
   | `perlu-jawaban` | Lanjut ke langkah 3. |
   | `perlu-review-ulang` | Lanjut ke langkah 2 dengan N = putaran terakhir + 1. |
   | `usang` | Dokumen berubah setelah gate lolos. Jalankan `reopen <epic> <gate>`, lalu mulai dari langkah 2. |
   | `lolos` | Gate selesai. Lanjut ke tahap berikutnya. |
   | `berhenti` | Dua revisi tidak cukup. Hentikan alur dan lanjut ke langkah 4. |

2. Jalankan agen peran `egm-reviewer` dalam konteks baru, dengan cara yang tertulis di bagian "Menjalankan agen peran" pada berkas instruksi proyek. Brief hanya berisi lima baris ini, tanpa ringkasan, tanpa latar belakang, tanpa pendapatmu:

   ```
   Gate: <gate>
   Akar proyek: .
   Dokumen yang diuji: <path>
   Rujukan yang boleh dibaca: <path, atau "tidak ada">
   Tulis hasil ke: <epic>/reviews/<gate>-r<N>.json
   ```

   Jangan melanjutkan percakapan reviewer sebelumnya dan jangan memberinya temuan putaran lalu. Reviewer yang mewarisi konteks bukan lagi ikan mas. Setelah selesai, kembali ke langkah 1.

3. Jalankan agen peran penulis gate itu dengan brief: folder epic, skill yang dijalankan, dan path berkas review yang harus dijawab. Setelah selesai, kembali ke langkah 1.

4. Saat status `berhenti`, tampilkan temuan putaran terakhir kepada operator dan minta arahan. Setelah operator memberi arahan, panggil penulis dengan arahan itu, jalankan `reopen <epic> <gate>`, lalu mulai lagi dari langkah 1.

## Larangan

- Jangan mengedit berkas di `reviews/` sendiri. Temuan milik reviewer, jawaban milik penulis.
- Jangan meloloskan gate dengan cara lain selain status `lolos` dari skrip.
- Jangan menjalankan `reopen` untuk menghindari batas revisi. Perintah itu hanya dipakai pada status `usang`, setelah arahan operator, atau saat `/modify-epic-ticket` mengubah dokumen.
