# Pencari Riset & Inovasi Pengembangan Produk Komoditas

Aplikasi web (Python + Streamlit) untuk menelusuri hasil penelitian, inovasi, dan paten
tentang bentuk-bentuk pengembangan produk dari **komoditas apa pun** atau **tema apa pun**
yang Anda masukkan. Hasilnya ditampilkan sebagai:

- **Galeri contoh produk** dengan gambar, misalnya untuk kelapa: tepung kelapa, gula kelapa,
  minyak kelapa murni, sabun, briket, karbon aktif, sabut, dan seterusnya. Setiap kartu
  memuat jumlah riset dan tautan ke 3 riset paling banyak disitasi.
- **Ringkasan grafik**: kategori pengembangan produk, tren publikasi per tahun, sumber data,
  dan produk yang paling sering diteliti.
- **Daftar riset** yang bisa disaring (kategori, produk, open access, kata kunci) dan
  diunduh sebagai CSV atau Excel.

## Cara menjalankan

Butuh Python 3.10 atau lebih baru, dan koneksi internet.

**Windows:** klik dua kali `run.bat`.
**macOS/Linux:** jalankan `bash run.sh`.

Atau secara manual:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # Windows: copy .env.example .env
streamlit run app.py
```

Browser akan terbuka di `http://localhost:8501`.

Isi `CONTACT_EMAIL` di file `.env` dengan email Anda. Ini dianjurkan oleh OpenAlex dan
Crossref agar akses lebih stabil.

## Cara memakai

Ketik **satu** komoditas atau tema di kolom pencarian, lalu tekan **Cari** atau Enter.
Bahasa Indonesia dan Inggris sama-sama bisa dipakai.

| Contoh input | Dicari sebagai |
|---|---|
| `kelapa` | kelapa / coconut |
| `olahan kulit jagung` | kulit jagung / corn husk |
| `limbah tulang ikan` | limbah tulang ikan / fish bone waste |
| `bioplastik` | bioplastik / bioplastic |
| `edible film` | edible film |

Aplikasi menerjemahkan input ke bahasa Inggris memakai glosarium bawaan (`core/bahasa.py`).
Untuk kata yang belum ada di glosarium, aplikasi memakai layanan terjemahan gratis
MyMemory. Kata seperti "olahan", "produk", dan "pemanfaatan" diabaikan saat menentukan
relevansi. Jadi `olahan kulit jagung` tetap menemukan riset berjudul *Corn husk nanocellulose…*.

Tahun mulai, jumlah hasil, sumber data, dan opsi gambar ada di **Pengaturan lanjutan**.

## Sumber data

| Sumber | Isi | Kunci API |
|---|---|---|
| OpenAlex | 250 juta+ karya ilmiah, termasuk banyak jurnal Indonesia | Tidak wajib (`OPENALEX_API_KEY` opsional) |
| Crossref | Metadata semua artikel ber-DOI, termasuk jurnal Sinta | Tidak |
| Semantic Scholar | Artikel lintas bidang | Opsional (`S2_API_KEY`); tanpa kunci sering kena batas laju |
| Europe PMC | Pangan, kesehatan, farmasi, bioteknologi | Tidak |
| Lens.org (paten) | Paten dunia | Wajib `LENS_TOKEN` (daftar gratis di lens.org) |
| Wikimedia Commons, Openverse | Gambar ilustrasi produk (lisensi terbuka) | Tidak |

Setiap sumber dihubungi berurutan dengan jeda, dan permintaan diulang otomatis (hingga 4 kali)
bila sumber membalas "terlalu banyak permintaan" (429). Peringatan hanya muncul bila satu
sumber gagal total. Sumber lain tetap dipakai.

Semantic Scholar tidak dicentang secara bawaan karena tanpa `S2_API_KEY` hampir selalu
membalas 429. Pilihan Lens.org (paten) baru muncul setelah `LENS_TOKEN` diisi.

Google Scholar, Garuda, dan Sinta tidak dipakai karena tidak menyediakan API publik resmi.
Artikel jurnal Indonesia tetap tertangkap lewat Crossref dan OpenAlex.

## Menyesuaikan

- **Kategori pengembangan produk:** edit `KATEGORI` di `core/config.py`.
- **Daftar produk yang dikenali (untuk galeri):** tambah baris di `LEKSIKON` dalam
  `core/produk.py`, formatnya `("istilah inggris", "istilah indonesia|varian", "Kategori")`.
- **Sinonim komoditas:** edit `SINONIM_KOMODITAS` di `core/config.py`.
- **Terjemahan kata (bagian tanaman, limbah, tema):** edit `GLOSARIUM` di `core/bahasa.py`.

## Uji cepat

```bash
pip install pytest
python -m pytest -q tests
python -c "from core.sources import openalex; print(len(openalex('coconut value-added products', 2020, 5)))"
```

Perintah kedua menguji koneksi ke OpenAlex. Bila hasilnya 5, koneksi berjalan.

## Batasan

- Deteksi produk dan kategori berbasis kata kunci, bukan AI. Bisa ada produk yang terlewat
  atau salah kelompok. Lengkapi leksikonnya sesuai bidang Anda.
- Gambar adalah ilustrasi berlisensi terbuka hasil pencarian otomatis. Gambar bisa tidak
  persis sama dengan produk dalam riset. Atribusi pembuat dan lisensi ditampilkan di tiap kartu.
- Hasil di-cache 1 jam dan gambar di-cache 24 jam. Untuk memuat ulang, pakai menu ⋮ →
  *Clear cache* di aplikasi.
