---
name: impact-check
description: Skill internal SPV. Mencari dokumen dan tiket yang terdampak sebuah perubahan. Dipanggil oleh /modify-epic-ticket.
user-invocable: false
---

# Memeriksa dampak perubahan

Masukan: folder epic dan perubahan yang diminta operator. Keluaran: `changes/NN-impact.md` di folder epic, dengan NN nomor urut dua digit.

Telusuri dari hulu ke hilir. Dokumen hilir terdampak jika dokumen hulunya berubah pada bagian yang ia pakai.

```
prd.md -> flow.md -> contract/ dan specs/ -> tickets/
```

Untuk tiap dokumen, jawab: apakah perubahan ini mengubah isinya? Jika ya, bagian mana?

- Perubahan teks atau tampilan yang tidak menyentuh acceptance criteria biasanya hanya mengenai `flow.md` dan tiket layar itu.
- Perubahan field, endpoint, kode error, atau aturan validasi mengenai contract. Contract yang berubah menaikkan versi, dan semua tiket yang mencatat versi lama ikut terdampak.
- Perubahan scope mengenai `prd.md` dan hampir semua yang di bawahnya.

Untuk tiket, bandingkan dengan `jira-map.json` supaya jelas mana yang sudah ada di tracker.

Isi berkas keluaran:

```markdown
# Dampak perubahan NN

## Perubahan yang diminta
Kalimat operator apa adanya.

## Dokumen terdampak
| Dokumen | Bagian | Penulis | Gate yang dibuka ulang |
| --- | --- | --- | --- |

## Tiket terdampak
| Tiket | Kode Jira | Tindakan (ubah, buat, hapus) | Alasan |
| --- | --- | --- | --- |

## Tidak terdampak
Dokumen dan tiket yang sengaja tidak disentuh.

## Versi contract
Tetap di x.y.z, atau naik dari x.y.z ke a.b.c.
```

Jika perubahan membuat ukuran epic naik, misalnya epic kecil yang kini butuh endpoint baru, katakan itu kepada operator sebelum melanjutkan. Epic itu perlu tahap yang dulu dilewati.

Tampilkan ringkasan dampak kepada operator dan minta konfirmasi sebelum ada dokumen yang diubah.
