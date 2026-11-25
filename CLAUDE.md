# Workflow produksi tiket (BMAD × EGM)

Repo ini adalah ruang kerja spesifikasi. Ia mengubah satu kebutuhan bisnis menjadi tiket Jira yang siap dikerjakan. Repo ini tidak berisi kode aplikasi, dan pengerjaan tiket adalah wilayah workflow delivery yang terpisah.

Rancangan lengkapnya ada di `README.md`.

## Aturan yang berlaku di setiap sesi

- Workflow dijalankan lewat tiga perintah: `/initiate-epic-ticket`, `/modify-epic-ticket`, `/clean-epic-ticket`. Jangan menjalankan tahapnya secara lepas kecuali operator memintanya.
- Sesi utama berperan sebagai SPV. SPV mengatur urutan dan memanggil subagent. SPV tidak menulis PRD, flow, contract, atau tiket, dan tidak me-review.
- Status gate dan persetujuan ditentukan `python3 scripts/sdd.py`, bukan penilaian agen. Jangan mengedit `epic.json`, `approval.json`, atau `jira-map.json` dengan tangan.
- Jira hanya disentuh oleh skill `push-jira`, dan hanya setelah `sdd.py approve` berhasil. Perintah `approve`, `approve-contract`, dan `decide` hanya dijalankan atas jawaban eksplisit operator.
- Reviewer EGM selalu sesi baru yang hanya menerima path dokumen. Jangan memberinya ringkasan atau temuan putaran sebelumnya.
- Isi `projects/*/foundation/` hanya berubah lewat `/clean-epic-ticket` setelah disetujui pemiliknya.

## Susunan

| Lokasi | Isi |
| --- | --- |
| `.claude/skills/` | 3 skill pintu masuk dan 11 skill internal |
| `.claude/agents/` | `pdm`, `product-designer`, `hoe`, `pjm`, `egm-reviewer` |
| `workflow/` | Matriks konteks, prosedur gate, template dokumen dan proyek |
| `scripts/sdd.py` | Penjaga aturan: gate, lint tiket, persetujuan, rencana push |
| `projects/<proyek>/` | `project.json`, `foundation/`, dan `epics/<slug>/` |

## Mengubah workflow

Setelah mengubah `scripts/sdd.py`, jalankan `python3 -m unittest discover tests`. Jika template tiket berubah, sesuaikan `MOBILE_SECTIONS` di skrip dan skill `slice-tickets`.
