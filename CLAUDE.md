# Pengembangan sdd-agent-workflow

Repo ini adalah **sumber** workflow produksi tiket, bukan tempat workflow dijalankan. Pengguna memasangnya ke folder lain lewat `install.sh`. Panduan pemakai ada di `README.md`.

## Susunan

| Lokasi | Isi |
| --- | --- |
| `src/skills/` | Sumber 14 skill, netral alat |
| `src/agents/` | Sumber 5 agen peran, frontmatter netral |
| `src/instructions.md` | Blok aturan untuk berkas instruksi tiap alat |
| `workflow/` | Matriks konteks, prosedur gate, template |
| `scripts/sdd.py` | Skrip penjaga aturan, disalin apa adanya ke `<SDD_HOME>/scripts/` |
| `scripts/install_agent.py` | Pemasang. Profil tiap alat ada di `TOOLS`. |
| `install.sh` | Antarmuka interaktif pemasang |

## Aturan saat mengubah repo ini

- Tulis path workflow di `src/` dan `workflow/*.md` dengan placeholder `{{SDD_HOME}}`, bukan path tetap. Pemasang menolak berkas yang masih menyisakan placeholder.
- Jangan menulis istilah khusus satu alat di `src/` (misalnya nama tool Claude Code). Perbedaan antar-alat diurus di `TOOLS` dan `agent_files` pada pemasang.
- Aturan "uji coba tidak memakai Jira" dijaga `sdd.py pending-push`. Jangan melemahkannya.
- Setelah mengubah `scripts/`, `src/`, `workflow/`, atau `install.sh`, jalankan `python3 -m unittest discover tests`.
- Jika template tiket Mobile berubah, sesuaikan `MOBILE_SECTIONS` di `sdd.py` dan skill `slice-tickets`.
