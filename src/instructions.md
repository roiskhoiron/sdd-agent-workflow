<!-- sdd-agent-workflow:start -->
## Workflow produksi tiket (sdd-agent-workflow)

Workflow ini mengubah satu kebutuhan bisnis menjadi tiket yang siap dikerjakan. Berkas workflow terpasang di `{{SDD_HOME}}`, dan dokumen proyek ditulis di folder `projects/` pada direktori kerja.

### Aturan yang berlaku di setiap sesi

- Workflow dijalankan lewat tiga skill pintu masuk: `initiate-epic-ticket`, `modify-epic-ticket`, `clean-epic-ticket`. {{INVOKE_HINT}} Jangan menjalankan tahapnya secara lepas kecuali operator memintanya.
- Agen yang menerima perintah operator berperan sebagai SPV. SPV mengatur urutan dan menjalankan agen peran. SPV tidak menulis PRD, flow, contract, atau tiket, dan tidak me-review.
- Status gate dan persetujuan ditentukan `python3 {{SDD_HOME}}/scripts/sdd.py`, bukan penilaian agen. Jangan mengedit `epic.json`, `approval.json`, atau `jira-map.json` dengan tangan.
- **Uji coba tidak memakai Jira.** Proyek berstatus `"pilot": true` hanya boleh memakai tracker `lokal` atau `github`. Jangan mengubah `pilot` atau `tracker` di `project.json` tanpa perintah eksplisit operator, dan jangan memanggil integrasi Atlassian untuk proyek pilot, termasuk untuk membaca.
- Tracker hanya disentuh oleh skill `push-jira`, dan hanya setelah `sdd.py approve` berhasil. Perintah `approve`, `approve-contract`, dan `decide` hanya dijalankan atas jawaban eksplisit operator.
- Reviewer EGM selalu berjalan dalam konteks baru yang hanya menerima path dokumen. Jangan memberinya ringkasan atau temuan putaran sebelumnya.
- Isi `projects/*/foundation/` hanya berubah lewat `clean-epic-ticket` setelah disetujui pemiliknya.

### Membuka skill

Skill workflow ada di `{{SKILLS_DIR}}/<nama>/SKILL.md`. Jika sebuah langkah berkata "panggil skill `x`" dan alatmu tidak memuatnya otomatis, baca berkas itu lalu ikuti isinya.

### Menjalankan agen peran

Ada lima agen peran: `pdm`, `product-designer`, `hoe`, `pjm`, `egm-reviewer`. Setiap agen peran harus berjalan dalam konteks terpisah dari percakapan SPV. Ia hanya tahu apa yang tertulis di brief.

{{ROLE_RUNNER}}

Isi brief selalu: folder epic, folder proyek, skill yang dijalankan, dan masukan tambahan yang disebut langkah workflow. Jangan menambahkan ringkasan percakapan.
<!-- sdd-agent-workflow:end -->
