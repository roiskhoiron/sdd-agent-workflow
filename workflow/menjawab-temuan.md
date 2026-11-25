# Menjawab temuan gate

Berlaku untuk semua peran penulis saat brief menyertakan berkas review `reviews/<gate>-r<N>.json`.

Setiap temuan wajib dijawab dengan mengisi `response` di berkas review itu. Jangan mengubah `id`, `type`, `where`, atau `text` milik reviewer.

```json
"response": { "status": "diperbaiki", "note": "Batas ukuran file ditambahkan di bagian Scope." }
```

Pilih satu status:

| Status | Kapan dipakai | Yang harus kamu lakukan |
| --- | --- | --- |
| `diperbaiki` | Temuan benar dan kamu bisa memperbaikinya | Ubah dokumen. `note` menyebut apa yang berubah. |
| `ditolak` | Temuan keliru, atau yang diminta memang sengaja tidak dicakup | `note` wajib berisi alasan. Tulis juga alasan itu di dokumen. |
| `diteruskan` | Jawabannya butuh keputusan manusia | `note` wajib berisi pertanyaan yang harus dijawab dan siapa pemiliknya. |

Tiga hal yang perlu diingat:

- Reviewer berikutnya adalah sesi baru yang tidak melihat temuan ini maupun jawabanmu. Jika kamu menolak temuan tanpa menuliskan alasannya di dokumen, reviewer berikutnya akan menemukan hal yang sama.
- Temuan berstatus `ditolak` dan `diteruskan` tidak hilang. Keduanya masuk paket persetujuan dan diputuskan manusia satu per satu.
- Jangan menandai `diperbaiki` untuk temuan yang sebenarnya kamu jawab dengan tebakan. Gunakan `diteruskan`.
