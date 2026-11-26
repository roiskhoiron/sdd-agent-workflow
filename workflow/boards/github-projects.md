# Adapter: GitHub Projects

Lokasi papan di `sdd.json`:

```json
"board": { "platform": "github-projects", "location": { "repo": "pemilik/repo", "project_owner": "pemilik", "project_number": 3 } }
```

Pakai GitHub CLI (`gh`) bila tersedia, atau tool MCP GitHub yang setara. Perintah di bawah memakai `gh`. Sebelum mulai, pastikan `gh auth status` berhasil dan token punya scope `project`.

## uji

Jalankan sekali saat `setup-board`, pada repo yang sama:

1. Buat issue uji berjudul `[sdd] uji papan`, lalu satu issue anak, lalu jadikan sub-issue.
2. Tandai issue anak diblokir oleh issue uji.
3. Tambahkan keduanya ke project dan baca nilai field Status.
4. Tutup kedua issue dengan komentar "uji setup-board selesai".

Catat hasil tiap langkah di `board.capabilities`. Jika langkah 2 gagal, ketergantungan ditulis sebagai teks.

## buat-epic

```bash
gh issue create --repo <repo> --title "<judul epic>" --body-file <berkas> --label epic
```

Kode epic adalah `#<nomor>`.

## buat-tiket

```bash
gh issue create --repo <repo> --title "<judul>" --body-file <isi-tanpa-front-matter> --label "<board.role_labels[role]>"
# jadikan sub-issue: butuh id numerik issue anak, bukan nomornya
id=$(gh api repos/<repo>/issues/<nomor-anak> --jq .id)
gh api -X POST repos/<repo>/issues/<nomor-epic>/sub_issues -F sub_issue_id="$id"
gh project item-add <project_number> --owner <project_owner> --url <url-issue>
```

## hubungkan

```bash
id=$(gh api repos/<repo>/issues/<nomor-pemblokir> --jq .id)
gh api -X POST repos/<repo>/issues/<nomor-tiket>/dependencies/blocked_by -F issue_id="$id"
```

## ubah-status

Ambil id field Status dan id opsi kolomnya dengan `gh project field-list <project_number> --owner <project_owner> --format json`, lalu:

```bash
gh project item-edit --id <item-id> --project-id <project-id> --field-id <status-field-id> --single-select-option-id <option-id>
```

Menutup tiket: `gh issue close <nomor> --repo <repo> --comment "<alasan>"`.

## baca

```bash
gh api repos/<repo>/issues/<nomor-epic>/sub_issues --paginate
gh project item-list <project_number> --owner <project_owner> --format json --limit 500
```

Gabungkan keduanya menjadi `board-snapshot.json`: `{ "key": "#12", "summary", "status", "links": ["#10"] }`.
