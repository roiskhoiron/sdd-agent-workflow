# sdd-agent-workflow

Tim agen AI yang mengubah **satu kebutuhan bisnis** menjadi **tiket yang siap dikerjakan**. Bisa dipasang di Claude Code, OpenAI Codex CLI, Gemini CLI, OpenCode, Cursor, GitHub Copilot, dan agen lain yang membaca `AGENTS.md`.

Kamu cukup menjelaskan kebutuhannya. Agen menulis PRD, flow layar, API contract, dan tiket. Setiap dokumen diuji reviewer independen, lalu kamu yang memutuskan sebelum tiket dikirim.

> Cakupan saat ini: tiket untuk role **Mobile**. Pekerjaan Backend, Frontend web, dan DevOps dicatat sebagai daftar, belum dibuatkan tiket.

---

## Daftar isi

1. [Gambaran singkat](#gambaran-singkat)
2. [Yang perlu disiapkan](#yang-perlu-disiapkan)
3. [Mulai dalam 5 langkah](#mulai-dalam-5-langkah)
4. [Alat yang didukung](#alat-yang-didukung)
5. [Tiga perintah utama](#tiga-perintah-utama)
6. [Apa yang terjadi saat perintah berjalan](#apa-yang-terjadi-saat-perintah-berjalan)
7. [Kapan kamu diminta memutuskan](#kapan-kamu-diminta-memutuskan)
8. [Ke mana tiket dikirim](#ke-mana-tiket-dikirim)
9. [Struktur folder](#struktur-folder)
10. [Masalah umum](#masalah-umum)
11. [Istilah](#istilah)
12. [Untuk pengembang workflow](#untuk-pengembang-workflow)

---

## Gambaran singkat

Bayangkan sebuah tim kecil: Product Manager, desainer, arsitek, dan project manager. Masing-masing menulis bagiannya, lalu ada satu orang yang membaca tanpa tahu konteks apa pun. Kalau orang itu bingung, dokumennya belum siap.

Workflow ini menjalankan tim itu sebagai agen AI di coding agent pilihanmu. Kamu berperan sebagai **operator**: menjawab pertanyaan, meninjau hasil, dan memberi persetujuan.

Tiga hal yang membuat workflow ini berbeda:

- **Tiket hanya berisi yang dibutuhkan pengerjanya.** Tiket Mobile tidak memuat detail database atau server.
- **Setiap tahap diuji reviewer yang tidak ikut menulis.** Reviewer selalu mulai dari nol, jadi ia membaca seperti pengerja tiket nanti.
- **Tidak ada tiket terkirim tanpa persetujuanmu.** Aturan ini dijaga oleh skrip, bukan hanya oleh instruksi ke agen.

Rancangan lengkapnya: [Draft: Agent Workflow Produksi Tiket (BMAD × EGM)](https://claude.ai/artifact/MmaafFo6XZrmLyJGm9ebkx).

---

## Yang perlu disiapkan

| Kebutuhan | Keterangan |
| --- | --- |
| Satu AI coding agent | Lihat [Alat yang didukung](#alat-yang-didukung) |
| Python 3.8 atau lebih baru | Untuk pemasang dan skrip penjaga. Tidak perlu `pip install` apa pun. |
| Bash dan Git | Untuk menjalankan `install.sh`. Di Windows, pakai WSL atau Git Bash. |
| Konektor Atlassian | **Hanya** jika tiket dikirim ke Jira. Untuk uji coba tidak perlu. |
| Akses GitHub ke repo tujuan | **Hanya** jika tiket dikirim ke GitHub Issues |

---

## Mulai dalam 5 langkah

### 1. Jalankan pemasang

Cara termudah, tanpa perlu meng-clone repo (butuh repo ini bisa diakses publik; jika privat, pakai cara clone):

```bash
curl -fsSL https://raw.githubusercontent.com/roiskhoiron/sdd-agent-workflow/master/install.sh | bash
```

Atau dari hasil clone:

```bash
git clone https://github.com/roiskhoiron/sdd-agent-workflow.git
cd sdd-agent-workflow
./install.sh
```

### 2. Jawab tiga pertanyaan pemasang

```
1. Pilih AI coding agent
  1) * Claude Code
  2) * OpenAI Codex CLI
  3)   Gemini CLI
  ...
  * terdeteksi di komputer ini
Nomor [1 2]: 1

2. Pilih scope
  1) project  hanya untuk satu folder proyek, bisa di-commit dan dipakai bersama tim
  2) global   untuk semua proyek di komputer ini, hanya untuk kamu
Nomor [1]: 1

3. Folder proyek
Folder [/home/kamu]: ~/kerja/spesifikasi-chefgenie
```

Boleh memilih lebih dari satu alat sekaligus, misalnya `1 2 6`. Alat yang ditandai `*` terdeteksi di komputermu, dan itulah pilihan awalnya.

**Project atau global?**

| Scope | Dipasang di | Pilih jika |
| --- | --- | --- |
| `project` | Folder proyek yang kamu pilih. Inti workflow di `<folder>/.sdd/`. | Kamu ingin tim memakai workflow yang sama lewat Git. **Disarankan untuk mulai.** |
| `global` | Folder konfigurasi alat di `~`. Inti workflow di `~/.sdd-agent-workflow/`. | Kamu ingin workflow tersedia di semua folder, hanya untuk dirimu. |

Dokumen spesifikasi selalu ditulis di folder `projects/` pada folder tempat coding agent dibuka, apa pun scope-nya.

### 3. Jalankan perintah pertama

Buka folder proyek dengan coding agent-mu, lalu jalankan `initiate-epic-ticket`. Di Claude Code, misalnya:

```
/initiate-epic-ticket chefgenie Pengguna bisa menyimpan resep favorit
```

Cara memanggil di alat lain ada di [Alat yang didukung](#alat-yang-didukung).

Karena proyek `chefgenie` belum ada, agen membuat folder `projects/chefgenie/` dari template **lalu berhenti**. Ini disengaja: agen butuh informasi proyek sebelum bisa menulis tiket yang benar.

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

### Memasang tanpa pertanyaan, menambah alat, dan mencopot

```bash
# Tanpa pertanyaan
./install.sh --agent claude,codex --scope project --target ~/kerja/spesifikasi --yes

# Menambah alat nanti: jalankan lagi dengan alat baru. Yang sudah ada tidak terganggu.
./install.sh --agent copilot --scope project --target ~/kerja/spesifikasi --yes

# Lihat rencana tanpa menulis apa pun
./install.sh --agent gemini --scope global --dry-run --yes

# Copot satu alat, atau semuanya bila --agent tidak diberikan
./install.sh --uninstall --agent codex --scope project --target ~/kerja/spesifikasi
./install.sh --uninstall --scope project --target ~/kerja/spesifikasi
```

Pemasang aman dijalankan berulang kali:

- Isi berkas instruksimu (`AGENTS.md`, `CLAUDE.md`, dan lainnya) tidak disentuh. Pemasang hanya menambah atau mengganti satu blok bertanda `sdd-agent-workflow`.
- Berkas yang sudah ada dan bukan buatan pemasang tidak ditimpa, kecuali kamu menambahkan `--force`.
- Mencopot tidak pernah menghapus folder `projects/` berisi pekerjaanmu.

---

## Alat yang didukung

| Alat | `--agent` | Cara memanggil perintah | Agen peran |
| --- | --- | --- | --- |
| Claude Code | `claude` | `/initiate-epic-ticket chefgenie ...` | Subagent native |
| OpenAI Codex CLI | `codex` | `$initiate-epic-ticket chefgenie ...` | Subagent native (TOML) |
| Gemini CLI | `gemini` | `/initiate-epic-ticket chefgenie ...` (perintah kustom) | Subagent native |
| OpenCode | `opencode` | `/initiate-epic-ticket chefgenie ...` (perintah kustom) | Subagent native |
| Cursor (editor dan CLI) | `cursor` | `/initiate-epic-ticket chefgenie ...` | Subagent native |
| GitHub Copilot (VS Code dan CLI) | `copilot` | `/initiate-epic-ticket chefgenie ...` | Custom agent |
| Agen lain | `generic` | Minta agen menjalankan skill `initiate-epic-ticket` | Proses baru lewat perintah headless |

Lokasi berkas yang dipasang per alat:

| Alat | Skill | Agen peran | Berkas instruksi (project / global) |
| --- | --- | --- | --- |
| `claude` | `.claude/skills/` | `.claude/agents/` | `CLAUDE.md` / `~/.claude/CLAUDE.md` |
| `codex` | `.agents/skills/` | `.codex/agents/*.toml` | `AGENTS.md` / `~/.codex/AGENTS.md` |
| `gemini` | `.gemini/skills/` | `.gemini/agents/` | `GEMINI.md` / `~/.gemini/GEMINI.md` |
| `opencode` | `.opencode/skills/` | `.opencode/agents/` | `AGENTS.md` / `~/.config/opencode/AGENTS.md` |
| `cursor` | `.cursor/skills/` | `.cursor/agents/` | `AGENTS.md` / tidak ada berkas, lihat catatan |
| `copilot` | `.github/skills/` | `.github/agents/*.agent.md` | `.github/copilot-instructions.md` / `~/.copilot/copilot-instructions.md` |
| `generic` | `.agents/skills/` | tidak ada, memakai `.sdd/roles/` | `AGENTS.md` / `~/.agents/AGENTS.md` |

Pada scope global, folder di kolom skill dan agen berada di bawah `~` (misalnya `~/.claude/skills/`, `~/.config/opencode/skills/`, `~/.copilot/skills/`).

### Agen peran: native atau headless

Workflow ini butuh reviewer yang **tidak membawa ingatan** dari percakapan. Ada dua cara mewujudkannya:

- **native**: memakai fitur subagent bawaan alat. Ini pilihan awal untuk semua alat yang mendukungnya.
- **headless**: agen utama menjalankan alat itu sebagai proses baru di terminal, misalnya `codex exec "..."`. Konteksnya pasti bersih, tetapi lebih lambat.

Pilih dengan `--role-mode native` atau `--role-mode headless`. Untuk `generic`, beri tahu perintah alatmu, misalnya:

```bash
./install.sh --agent generic --role-mode headless --headless-cmd 'aider --yes --message "<prompt>"' --yes
```

### Catatan per alat

Konvensi tiap alat diambil dari dokumentasi resminya per November 2026. Beberapa perilaku belum diuji langsung, jadi coba dulu di proyek pilot.

| Alat | Catatan |
| --- | --- |
| Codex | Subagent Codex tidak bisa dibatasi tool-nya, jadi batasan peran hanya ditulis di instruksi. Dokumentasinya tidak menyatakan isolasi konteks penuh. Jika reviewer terasa "ingat" konteks, pasang ulang dengan `--role-mode headless`. |
| Gemini CLI | Agen peran memakai semua tool induk, karena nama tool Gemini tidak ditebak oleh pemasang. Untuk pengguna tanpa langganan, Gemini CLI sudah digantikan Antigravity CLI sejak Juni 2026. |
| Cursor | Agen peran Cursor tidak punya daftar tool. Pada scope global, Cursor tidak punya berkas aturan, jadi salin isi `~/.sdd-agent-workflow/instructions/cursor.md` ke **Settings → Rules → User Rules**. |
| Copilot | Copilot CLI juga membaca `CLAUDE.md` dan `GEMINI.md`. Jika memasang Copilot bersama Claude atau Gemini, aturan workflow akan terbaca lebih dari sekali, dan itu tidak merusak. |
| Beberapa alat sekaligus | Cursor, Copilot, dan OpenCode juga membaca folder skill alat lain (`.claude/skills`, `.agents/skills`). Jika beberapa alat dipasang di satu folder, skill yang sama bisa terbaca dua kali dari lokasi berbeda. Isinya identik, jadi tidak berbahaya. |

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

Contoh di atas memakai gaya Claude Code. Di Codex ganti `/` dengan `$`. Di alat tanpa perintah slash, tulis saja permintaannya, misalnya "jalankan skill modify-epic-ticket untuk proyek chefgenie, epic resep-favorit, ...".

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

Setelah dipasang dengan scope `project`, folder proyekmu berisi:

```
<folder proyek>/
├── .sdd/                  inti workflow (jangan diedit, dipasang ulang oleh pemasang)
│   ├── scripts/sdd.py     skrip penjaga aturan
│   ├── workflow/          matriks konteks, prosedur gate, template
│   ├── skills/            salinan netral semua skill
│   └── roles/             prompt agen peran untuk mode headless
├── .claude/ .codex/ ...   adapter untuk alat yang kamu pilih
├── AGENTS.md / CLAUDE.md  blok aturan workflow ditambahkan di sini
└── projects/              pekerjaanmu
    └── <proyek>/
        ├── project.json
        ├── foundation/        6 dokumen dasar proyek
        ├── tracker-lokal/     tiket, jika tracker = lokal
        └── epics/<slug>/      satu folder per kebutuhan
```

Commit semuanya ke Git supaya tim memakai versi workflow yang sama.

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
| `python3 tidak ditemukan` saat memasang | Python belum terpasang | Pasang Python 3.8 atau lebih baru |
| "Dilewati karena sudah ada" saat memasang | Ada berkas dengan nama sama yang bukan buatan pemasang | Periksa berkasnya. Jika aman ditimpa, ulangi dengan `--force`. |
| Perintah `/initiate-epic-ticket` tidak dikenal | Alat belum memuat ulang skill, atau dipanggil dengan gaya alat lain | Mulai ulang sesi alat. Lihat kolom "Cara memanggil" di [Alat yang didukung](#alat-yang-didukung). |
| Perintah berhenti setelah membuat folder proyek | Proyek baru, `project.json` belum diisi | Isi `project.json` dan `foundation/`, lalu jalankan lagi |
| Agen bertanya tentang teks `ISI` | Ada bagian `project.json` yang belum diisi | Isi bagian yang disebut agen |
| "gate ... berstatus berhenti" | Dua kali revisi belum cukup | Baca temuannya, beri arahan ke agen |
| "gate ... berstatus usang" | Dokumen berubah setelah gate lolos | Biarkan agen menjalankan review ulang |
| "berkas berubah setelah disetujui" | Ada perubahan setelah kamu menyetujui | Setujui ulang lewat agen |
| "proyek ini pilot dan tracker-nya Jira" | Aturan keras pilot | Pakai tracker `lokal` atau `github` |
| Perintah terhenti di tengah | Sesi ditutup atau menunggu keputusan | Jalankan perintah yang sama lagi. Agen melanjutkan dari tahap terakhir yang belum lolos. |

Cek posisi sebuah epic kapan saja:

```bash
python3 .sdd/scripts/sdd.py status projects/<proyek>/epics/<slug>
# scope global: python3 ~/.sdd-agent-workflow/scripts/sdd.py status ...
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

### Susunan repo ini

| Lokasi | Isi |
| --- | --- |
| `src/skills/` | Sumber 14 skill, netral alat. Path ditulis dengan `{{SDD_HOME}}`. |
| `src/agents/` | Sumber 5 agen peran dengan frontmatter netral (`tools: read, search, write, edit`) |
| `src/instructions.md` | Blok aturan yang disisipkan ke berkas instruksi tiap alat |
| `workflow/` | Matriks konteks, prosedur gate, template dokumen dan proyek |
| `scripts/sdd.py` | Skrip penjaga aturan |
| `scripts/install_agent.py` | Pemasang: profil alat di `TOOLS`, render skill, agen, dan blok instruksi |
| `install.sh` | Antarmuka interaktif yang memanggil `install_agent.py` |

Repo ini sendiri tidak memasang workflow-nya. Untuk mencobanya, pasang ke folder lain dengan `./install.sh`.

### Menambah alat baru

Tambahkan satu entri di `TOOLS` dalam `scripts/install_agent.py`: folder skill, folder agen dan formatnya, berkas instruksi, perintah headless, dan cara memanggil. Jika format agennya baru, tambahkan cabang di `agent_files`. Tambahkan juga deteksinya di `install.sh`, lalu jalankan uji.

### Jalankan uji

```bash
python3 -m unittest discover tests
```

Wajib dijalankan setelah mengubah `scripts/`, `src/`, atau `install.sh`. Jika template tiket Mobile berubah, sesuaikan juga `MOBILE_SECTIONS` di `sdd.py` dan skill `slice-tickets`.

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
| Model AI tiap peran | Mengikuti model sesi | Frontmatter agen hasil pasang |
| Temuan gate | Berkas JSON di `reviews/` | Skill `egm-review` |
| Pembaruan Foundation | Langsung setelah disetujui | Skill `clean-epic-ticket` |

### Belum dikerjakan

- Template tiket Backend, Frontend web, dan DevOps.
- Uji coba pada epic nyata. Skrip dan pemasang sudah diuji otomatis, tetapi alur agen belum pernah dijalankan dari awal sampai akhir di alat mana pun.
- Hook yang memblokir integrasi Atlassian untuk proyek pilot. Saat ini larangannya dijaga skrip dan instruksi agen.
