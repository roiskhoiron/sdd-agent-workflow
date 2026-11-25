# sdd-agent-workflow

Tim agen AI di Claude Code yang mengubah **satu kebutuhan bisnis** menjadi **tiket yang siap dikerjakan**.

Kamu cukup menjelaskan kebutuhannya. Agen menulis PRD, flow layar, API contract, dan tiket. Setiap dokumen diuji reviewer independen, lalu kamu yang memutuskan sebelum tiket dikirim.

> Cakupan saat ini: tiket untuk role **Mobile**. Pekerjaan Backend, Frontend web, dan DevOps dicatat sebagai daftar, belum dibuatkan tiket.

---

## Daftar isi

1. [Gambaran singkat](#gambaran-singkat)
2. [Yang perlu disiapkan](#yang-perlu-disiapkan)
3. [Mulai dalam 5 langkah](#mulai-dalam-5-langkah)
4. [Tiga perintah utama](#tiga-perintah-utama)
5. [Apa yang terjadi saat perintah berjalan](#apa-yang-terjadi-saat-perintah-berjalan)
6. [Kapan kamu diminta memutuskan](#kapan-kamu-diminta-memutuskan)
7. [Ke mana tiket dikirim](#ke-mana-tiket-dikirim)
8. [Struktur folder](#struktur-folder)
9. [Masalah umum](#masalah-umum)
10. [Istilah](#istilah)
11. [Untuk pengembang workflow](#untuk-pengembang-workflow)

---

## Gambaran singkat

Bayangkan sebuah tim kecil: Product Manager, desainer, arsitek, dan project manager. Masing-masing menulis bagiannya, lalu ada satu orang yang membaca tanpa tahu konteks apa pun. Kalau orang itu bingung, dokumennya belum siap.

Repo ini menjalankan tim itu sebagai agen AI. Kamu berperan sebagai **operator**: menjawab pertanyaan, meninjau hasil, dan memberi persetujuan.

Tiga hal yang membuat workflow ini berbeda:

- **Tiket hanya berisi yang dibutuhkan pengerjanya.** Tiket Mobile tidak memuat detail database atau server.
- **Setiap tahap diuji reviewer yang tidak ikut menulis.** Reviewer selalu mulai dari nol, jadi ia membaca seperti pengerja tiket nanti.
- **Tidak ada tiket terkirim tanpa persetujuanmu.** Aturan ini dijaga oleh skrip, bukan hanya oleh instruksi ke agen.

Rancangan lengkapnya: [Draft: Agent Workflow Produksi Tiket (BMAD × EGM)](https://claude.ai/artifact/MmaafFo6XZrmLyJGm9ebkx).

---

## Yang perlu disiapkan

| Kebutuhan | Keterangan |
| --- | --- |
| [Claude Code](https://code.claude.com) | CLI, aplikasi desktop, web, atau ekstensi IDE |
| Python 3.8 atau lebih baru | Untuk skrip penjaga `scripts/sdd.py`. Tidak perlu `pip install` apa pun. |
| Git | Untuk mengunduh repo dan menyimpan hasil |
| Konektor Atlassian | **Hanya** jika tiket dikirim ke Jira. Untuk uji coba tidak perlu. |
| Akses GitHub ke repo tujuan | **Hanya** jika tiket dikirim ke GitHub Issues |

---

## Mulai dalam 5 langkah

### 1. Unduh repo dan buka di Claude Code

```bash
git clone https://github.com/roiskhoiron/sdd-agent-workflow.git
cd sdd-agent-workflow
claude
```

### 2. (Disarankan) Izinkan skrip penjaga berjalan tanpa ditanya

Skrip `sdd.py` dipanggil berkali-kali. Supaya kamu tidak diminta izin setiap kali, buat berkas `.claude/settings.json` berisi:

```json
{ "permissions": { "allow": ["Bash(python3 scripts/sdd.py:*)"] } }
```

### 3. Jalankan perintah pertama

Ketik di Claude Code, ganti `chefgenie` dengan nama proyekmu:

```
/initiate-epic-ticket chefgenie Pengguna bisa menyimpan resep favorit
```

Karena proyek ini belum ada, agen membuat folder `projects/chefgenie/` dari template **lalu berhenti**. Ini disengaja: agen butuh informasi proyek sebelum bisa menulis tiket yang benar.

### 4. Isi data proyek

Buka dan isi dua hal ini:

**a. `projects/<proyek>/project.json`.** Ganti setiap teks `ISI` dengan nilai sebenarnya. Yang paling penting:

| Kunci | Isi dengan |
| --- | --- |
| `name` | Nama proyek |
| `pilot` | Biarkan `true` selama uji coba |
| `tracker.type` | `lokal` untuk mulai. Lihat [Ke mana tiket dikirim](#ke-mana-tiket-dikirim). |
| `owners` | Nama orang yang menyetujui tiap jenis dokumen |
| `references` | Tautan ke konvensi kode mobile dan konfigurasi environment |

Bagian `jira` boleh dibiarkan selama `tracker.type` bukan `jira`.

**b. Enam dokumen di `projects/<proyek>/foundation/`.** Ini pengetahuan dasar proyek yang dirujuk oleh tiket.

| Berkas | Isi singkat | Wajib untuk tiket Mobile? |
| --- | --- | --- |
| `design-system.md` | Komponen UI, warna, tipografi, pola layar | **Ya** |
| `katalog-contract.md` | Daftar API contract yang berlaku dan versinya | **Ya** |
| `infrastruktur.md` | Server, environment, jalur deploy | Tidak |
| `stack-backend.md` | Bahasa, framework, konvensi backend | Tidak |
| `skema-database.md` | Tabel inti dan aturan migrasi | Tidak |
| `adr.md` | Catatan keputusan arsitektur | Tidak |

Tidak harus sempurna. Mulai dengan yang kamu tahu, lalu lengkapi seiring waktu.

### 5. Jalankan lagi perintah yang sama

```
/initiate-epic-ticket chefgenie Pengguna bisa menyimpan resep favorit
```

Sekarang agen akan bertanya tentang kebutuhanmu, lalu bekerja tahap demi tahap. Ikuti pertanyaannya sampai tiket terkirim.

---

## Tiga perintah utama

Kamu hanya perlu mengingat tiga perintah ini.

| Perintah | Kapan dipakai | Hasilnya |
| --- | --- | --- |
| `/initiate-epic-ticket <proyek> <kebutuhan>` | Ada kebutuhan baru | Epic dan tiket baru di tracker |
| `/modify-epic-ticket <proyek> <epic> <perubahan>` | Kebutuhan atau API berubah setelah tiket dibuat | Hanya dokumen dan tiket yang terdampak yang diperbarui |
| `/clean-epic-ticket <proyek> <epic> <selesai\|dibatalkan>` | Epic selesai atau dibatalkan | Tiket usang ditutup, epic diarsipkan, Foundation diperbarui |

Contoh:

```
/modify-epic-ticket chefgenie resep-favorit Batas favorit naik dari 50 menjadi 100
/clean-epic-ticket chefgenie resep-favorit selesai
```

`<epic>` boleh berupa nama folder epic (misalnya `resep-favorit`) atau kode tiket epic di tracker.

> ⚠️ **Jangan mengedit tiket langsung di tracker** setelah epic dibuat. Perubahan manual akan tertimpa oleh `/modify-epic-ticket` berikutnya. Selalu ubah lewat perintah.

---

## Apa yang terjadi saat perintah berjalan

### Alur `/initiate-epic-ticket`

```
Kamu menjelaskan kebutuhan
        │
        ▼
Agen mengusulkan ukuran ──► kamu memilih: kecil / sedang / besar
        │
        ├── kecil ─────────────────────────────────────┐
        │                                              │
        ▼ sedang / besar                               │
1. PdM menulis PRD ─────────────► gate review          │
2. Product Designer menulis flow ► gate review         │
3. HoE menulis API contract ────► gate review          │
   (jika API berubah: pemilik contract harus setuju)   │
        │                                              │
        ▼                                              │
4. PjM memecah menjadi tiket ◄─────────────────────────┘
        │
        ▼
   cek format otomatis ──► gate review
        │
        ▼
Kamu memutuskan setiap temuan, lalu menyetujui
        │
        ▼
Tiket dikirim ke tracker
```

### Peran agen

| Agen | Tugas |
| --- | --- |
| **SPV** (sesi utama) | Mengatur urutan, bertanya kepadamu, memanggil agen lain |
| **PdM** | Menulis PRD: masalah, scope, acceptance criteria |
| **Product Designer** | Menulis flow layar dan semua state-nya (kosong, memuat, berhasil, gagal, offline) |
| **HoE** | Menulis API contract dan catatan teknis server |
| **PjM** | Memecah epic menjadi tiket per role |
| **Reviewer EGM** | Membaca dokumen tanpa konteks dan mencatat yang tidak jelas, bertentangan, atau hilang |

### Cara kerja gate review

Setelah setiap penulis selesai, reviewer baru membaca dokumennya.

1. Reviewer mencatat **temuan**: hal yang membuat pembaca harus menebak.
2. Penulis menjawab setiap temuan dengan salah satu dari tiga jawaban:
   - **diperbaiki**: dokumen diubah, lalu direview ulang oleh reviewer baru.
   - **ditolak**: penulis tidak setuju dan menuliskan alasannya.
   - **diteruskan**: butuh keputusan manusia.
3. Gate lolos jika tidak ada temuan yang terbuka.
4. Jika masih gagal setelah **dua kali revisi**, alur berhenti dan kamu diminta memberi arahan.

Temuan yang **ditolak** atau **diteruskan** tidak hilang. Kamu akan diminta memutuskannya satu per satu sebelum persetujuan akhir.

### Ukuran pekerjaan

| Ukuran | Contoh | Tahap yang dijalankan |
| --- | --- | --- |
| Kecil | Ubah teks, perbaikan tampilan, bug kecil | Langsung ke tiket, satu gate |
| Sedang | Fitur di satu layar dengan API yang sudah ada | Semua tahap, PRD singkat |
| Besar | Fitur lintas role atau butuh API baru | Semua tahap, contract wajib disetujui pemiliknya |

---

## Kapan kamu diminta memutuskan

Agen akan berhenti dan bertanya di titik-titik ini. Tabel ini membantumu menjawab.

| Titik | Yang perlu kamu periksa | Jika ragu |
| --- | --- | --- |
| **Ukuran pekerjaan** | Apakah menyentuh lebih dari satu role? Butuh API baru? | Pilih ukuran yang lebih besar |
| **Review flow** | Apakah flow layar sesuai harapan pemilik desain? | Minta revisi |
| **Persetujuan contract** | Apakah API cocok dengan flow, dan pemilik contract sudah setuju? | Jangan lanjut tanpa pemilik contract |
| **Temuan terbawa** | Apakah alasan penulis menolak temuan itu masuk akal? | Pilih "revisi" |
| **Persetujuan akhir** | Bisakah tiket Mobile dikerjakan tanpa bertanya balik? | Tulis komentar, jangan setujui |

Setiap keputusan dicatat beserta namamu. Kamu tidak bisa menyetujui semuanya sekaligus, dan itu disengaja: persetujuan yang asal klik adalah risiko terbesar workflow ini.

---

## Ke mana tiket dikirim

Tujuan tiket diatur di `project.json`, kunci `tracker.type`.

| Nilai | Tiket masuk ke | Cocok untuk |
| --- | --- | --- |
| `lokal` | Berkas Markdown di `projects/<proyek>/tracker-lokal/` | Belajar dan uji coba. **Nilai awal.** |
| `github` | GitHub Issues di repo `tracker.github_repo` | Uji coba dengan tracker sungguhan |
| `jira` | Proyek Jira sesuai bagian `jira` | Pemakaian produksi |

> 🔒 **Aturan keras: uji coba tidak boleh memakai Jira.**
> Proyek baru selalu dibuat dengan `"pilot": true`. Selama nilainya `true` (atau kuncinya tidak ada), skrip **menolak** mengirim ke Jira. Hanya pemilik proyek yang boleh mengubahnya menjadi `false`, dan agen dilarang mengubahnya sendiri.

---

## Struktur folder

```
sdd-agent-workflow/
├── .claude/
│   ├── skills/          14 skill: 3 perintah utama + 11 langkah internal
│   └── agents/          5 agen peran
├── workflow/
│   ├── context-matrix.md      apa yang boleh masuk ke tiket tiap role
│   ├── menjalankan-gate.md    prosedur gate review
│   ├── menjawab-temuan.md     cara penulis menjawab temuan
│   ├── templates/             template PRD, flow, contract, tiket
│   └── project-template/      kerangka proyek baru
├── scripts/sdd.py       skrip penjaga aturan
├── tests/               uji untuk skrip penjaga
└── projects/            proyek kamu ada di sini
    └── <proyek>/
        ├── project.json
        ├── foundation/        6 dokumen dasar proyek
        ├── tracker-lokal/     tiket, jika tracker = lokal
        └── epics/<slug>/      satu folder per kebutuhan
```

Isi satu folder epic:

| Berkas | Ditulis oleh | Isi |
| --- | --- | --- |
| `intake.md` | SPV | Jawabanmu saat ditanya tentang kebutuhan |
| `prd.md` | PdM | Masalah, scope, acceptance criteria |
| `flow.md` | Product Designer | Layar, flow, dan state |
| `contract/` | HoE | API contract, dibaca semua role |
| `specs/` | HoE | Catatan teknis server, **tidak** dibaca role Mobile |
| `tickets/` | PjM | Satu berkas per tiket |
| `reviews/` | Reviewer dan penulis | Temuan dan jawabannya |
| `approval.md` | SPV | Ringkasan yang kamu baca sebelum menyetujui |
| `epic.json`, `approval.json`, `jira-map.json` | Skrip | Status. **Jangan diedit manual.** |

---

## Masalah umum

| Gejala | Penyebab | Solusi |
| --- | --- | --- |
| Perintah berhenti setelah membuat folder proyek | Proyek baru, `project.json` belum diisi | Isi `project.json` dan `foundation/`, lalu jalankan lagi |
| Agen bertanya tentang teks `ISI` | Ada bagian `project.json` yang belum diisi | Isi bagian yang disebut agen |
| "gate ... berstatus berhenti" | Dua kali revisi belum cukup | Baca temuannya, beri arahan ke agen |
| "gate ... berstatus usang" | Dokumen berubah setelah gate lolos | Biarkan agen menjalankan review ulang |
| "berkas berubah setelah disetujui" | Ada perubahan setelah kamu menyetujui | Setujui ulang lewat agen |
| "proyek ini pilot dan tracker-nya Jira" | Aturan keras pilot | Pakai tracker `lokal` atau `github` |
| Perintah terhenti di tengah | Sesi ditutup atau menunggu keputusan | Jalankan perintah yang sama lagi. Agen melanjutkan dari tahap terakhir yang belum lolos. |

Cek posisi sebuah epic kapan saja:

```bash
python3 scripts/sdd.py status projects/<proyek>/epics/<slug>
```

---

## Istilah

| Istilah | Arti |
| --- | --- |
| **Epic** | Satu kebutuhan bisnis utuh, berisi beberapa tiket |
| **PRD** | Product Requirements Document: masalah apa yang diselesaikan dan untuk siapa |
| **Flow** | Urutan layar dan apa yang dilihat pengguna di setiap keadaan |
| **API contract** | Kesepakatan bentuk data antara aplikasi dan server |
| **Foundation** | Dokumen dasar proyek yang ditulis sekali dan dirujuk oleh tiket |
| **Gate** | Titik pemeriksaan sebelum lanjut ke tahap berikutnya |
| **Temuan** | Catatan reviewer tentang hal yang tidak jelas, bertentangan, atau hilang |
| **BMAD** | Pola agen yang menulis dokumen per peran |
| **EGM** | Pola review "gajah menulis, ikan mas me-review": penulis yang tahu banyak, reviewer yang tidak membawa ingatan apa pun |
| **Pilot** | Uji coba. Proyek pilot tidak boleh memakai Jira. |

---

## Untuk pengembang workflow

Bagian ini untuk yang ingin mengubah workflow, bukan sekadar memakainya.

### Jalankan uji

```bash
python3 -m unittest discover tests
```

Wajib dijalankan setelah mengubah `scripts/sdd.py`. Jika template tiket Mobile berubah, sesuaikan juga `MOBILE_SECTIONS` di skrip dan skill `slice-tickets`.

### Aturan yang dijaga skrip

Aturan berikut sengaja tidak bergantung pada kepatuhan agen.

| Aturan | Perintah `sdd.py` |
| --- | --- |
| Gate lolos hanya jika tidak ada temuan terbuka, maksimal dua revisi | `gate` |
| Dokumen yang berubah setelah lolos harus direview ulang | `gate`, `reopen` |
| Tiket Mobile punya 9 bagian berurutan, tanpa placeholder, versi contract cocok | `lint` |
| Temuan ditolak atau diteruskan diputuskan manusia satu per satu | `decide` |
| Contract yang berubah disetujui pemiliknya dulu | `approve-contract` |
| Persetujuan mengunci isi epic | `approve`, `verify-approval` |
| Proyek pilot tidak boleh ke Jira | `pending-push` |
| Hanya tiket baru, berubah, atau dihapus yang dikirim | `pending-push`, `record-push` |

### Keputusan awal yang bisa diubah

| Hal | Pilihan saat ini | Tempat mengubah |
| --- | --- | --- |
| Format contract | OpenAPI 3.1 | `project.json`, skill `write-contract` |
| Mockup | Tautan bila ada, wireframe teks bila tidak | `mockup_tool` di `project.json` |
| Model AI tiap peran | Mengikuti model sesi | Tambahkan `model:` di `.claude/agents/*.md` |
| Temuan gate | Berkas JSON di `reviews/` | Skill `egm-review` |
| Pembaruan Foundation | Langsung setelah disetujui | Skill `clean-epic-ticket` |

### Belum dikerjakan

- Template tiket Backend, Frontend web, dan DevOps.
- Uji coba pada epic nyata. Skrip sudah diuji otomatis, tetapi alur agen belum pernah dijalankan dari awal sampai akhir.
- Hook yang memblokir tool Atlassian untuk proyek pilot. Saat ini larangannya dijaga skrip dan instruksi agen.
