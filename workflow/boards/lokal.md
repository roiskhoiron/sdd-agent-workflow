# Adapter: lokal (uji coba)

Tidak menyentuh layanan luar. Cocok untuk mencoba workflow tanpa akses papan sungguhan.

Tiket ditulis di `<board.location>/<slug-epic>/`, default `docs/papan-lokal/<slug-epic>/`. Folder ini sengaja berada di luar folder epic supaya persetujuan tidak batal.

| Operasi | Cara |
| --- | --- |
| uji | Pastikan folder bisa ditulis. Semua kemampuan tersedia. |
| buat-epic | Tulis `EPIC.md`. Kode epic `LOKAL-0`. |
| buat-tiket | Tulis `LOKAL-<n>.md`, n berurutan, dengan baris `Role: <role>` di awal. |
| hubungkan | Tambahkan baris `Diblokir oleh: LOKAL-<n>` di awal berkas. |
| ubah-status | Ganti baris `Status: <kolom>` di awal berkas. |
| baca | Baca semua berkas di folder epic. |
