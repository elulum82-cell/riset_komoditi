"""Pencari Riset & Inovasi Pengembangan Produk Komoditas.

Jalankan:  streamlit run app.py
"""
import html
import io
import os
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from core.gambar import gambar_produk  # noqa: E402
from core.produk import ringkas_produk  # noqa: E402
from core.search import cari  # noqa: E402
from core.sources import SUMBER  # noqa: E402

st.set_page_config(page_title="Riset & Inovasi Komoditas", page_icon="🌱", layout="wide")

st.markdown("""
<style>
.hero h1 {font-size: 1.9rem; margin-bottom: .2rem;}
.hero p {color: #5b6b62; margin-top: 0;}
.grid {display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 18px;}
.card {border: 1px solid rgba(120,140,128,.28); border-radius: 14px; overflow: hidden;
       background: rgba(250,252,250,.6); display: flex; flex-direction: column;}
.card img {width: 100%; height: 170px; object-fit: cover; display: block; background: #e9efe9;}
.noimg {height: 170px; display: flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg,#dfeee2,#f4efe1); color: #4d6b55;
        font-weight: 600; font-size: 1.05rem; padding: 0 12px; text-align: center;}
.body {padding: 12px 14px 14px; display: flex; flex-direction: column; gap: 6px; flex: 1;}
.nama {font-weight: 700; font-size: 1.05rem;}
.badge {display: inline-block; font-size: .72rem; padding: 2px 8px; border-radius: 999px;
        background: #e3f0e6; color: #2f5e3b; margin-right: 6px;}
.jml {font-size: .78rem; color: #6b7a70;}
.card ul {margin: 4px 0 0 1rem; padding: 0; font-size: .8rem;}
.card li {margin-bottom: 3px;}
.atrib {font-size: .66rem; color: #8a968e; margin-top: auto; padding-top: 6px;}
@media (prefers-color-scheme: dark) {
  .card {background: rgba(30,36,32,.6);} .badge {background:#2c4433; color:#cfe8d5;}
  .noimg {background: linear-gradient(135deg,#27392c,#3a3527); color:#cfe8d5;}
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="hero"><h1>🌱 Pencari Riset & Inovasi Pengembangan Produk</h1>'
    "<p>Masukkan komoditas dan/atau tema. Aplikasi menelusuri jurnal ilmiah, "
    "prosiding, dan paten, lalu merangkum bentuk-bentuk produk yang sudah dikembangkan.</p></div>",
    unsafe_allow_html=True,
)

# ---------------- Input (satu kolom) ----------------
ada_lens = bool(os.getenv("LENS_TOKEN"))
ada_s2 = bool(os.getenv("S2_API_KEY"))
pilihan_sumber = [s for s in SUMBER if s != "Lens (paten)" or ada_lens]
default_sumber = [s for s in pilihan_sumber if s != "Semantic Scholar" or ada_s2]

with st.form("cari"):
    k1, k2 = st.columns([5, 1])
    teks = k1.text_input("Komoditas atau tema", label_visibility="collapsed",
                         placeholder="Ketik komoditas atau tema, mis. kulit jagung, rumput laut, bioplastik")
    tombol = k2.form_submit_button("🔎 Cari", type="primary")
    with st.expander("Pengaturan lanjutan"):
        a1, a2 = st.columns(2)
        tahun_mulai = a1.number_input("Tahun terbit mulai", 1980, 2100, 2015, step=1)
        limit = a2.slider("Maks. hasil per kueri per sumber", 10, 100, 25, step=5)
        sumber = st.multiselect("Sumber data", pilihan_sumber, default=default_sumber,
                                help="Semantic Scholar lebih stabil bila S2_API_KEY diisi. "
                                     "Paten Lens.org muncul bila LENS_TOKEN diisi di file .env.")
        b1, b2 = st.columns(2)
        filter_rel = b1.checkbox("Hanya hasil yang relevan dengan kata kunci", value=True)
        tampil_gambar = b2.checkbox("Tampilkan gambar contoh produk", value=True)

@st.cache_data(ttl=3600, show_spinner=False)
def _cari(teks, tahun_mulai, sumber, limit, filter_rel):
    hasil, galat, kueri, info = cari(teks, tahun_mulai, list(sumber), limit, filter_rel)
    info = {**info, "grup": [sorted(g) for g in info["grup"]]}
    return [asdict(r) for r in hasil], galat, kueri, info


@st.cache_data(ttl=86400, show_spinner=False)
def _gambar_banyak(pasangan):
    with ThreadPoolExecutor(max_workers=6) as ex:
        return list(ex.map(lambda p: gambar_produk(p[0], p[1]), pasangan))


def _e(teks):
    return html.escape(str(teks or ""))


def kartu_produk(p, gbr):
    if gbr:
        gambar = f'<img src="{_e(gbr["url"])}" alt="{_e(p["nama"])}" loading="lazy">'
        atrib = (f'Gambar ilustrasi: <a href="{_e(gbr["halaman"])}" target="_blank">'
                 f'{_e(gbr["sumber"])}</a>'
                 + (f' · {_e(gbr["pembuat"])}' if gbr.get("pembuat") else "")
                 + (f' · {_e(gbr["lisensi"])}' if gbr.get("lisensi") else ""))
    else:
        gambar = f'<div class="noimg">{_e(p["nama"])}</div>'
        atrib = "Gambar tidak ditemukan"
    daftar = "".join(
        f'<li><a href="{_e(r.get("url"))}" target="_blank">{_e((r.get("judul") or "")[:90])}'
        f'{"…" if len(r.get("judul") or "") > 90 else ""}</a>'
        f' ({_e(r.get("tahun") or "-")})</li>'
        for r in p["riset"][:3]
    )
    return (
        f'<div class="card">{gambar}<div class="body">'
        f'<div class="nama">{_e(p["nama"])}</div>'
        f'<div><span class="badge">{_e(p["kategori"])}</span>'
        f'<span class="jml">{p["jumlah"]} riset</span></div>'
        f'<ul>{daftar}</ul><div class="atrib">{atrib}</div></div></div>'
    )


if tombol:
    st.session_state["param"] = (teks.strip(), int(tahun_mulai), tuple(sumber), limit, filter_rel)
    st.session_state["gambar"] = tampil_gambar

param = st.session_state.get("param")
if not param:
    st.info("Ketik **satu** komoditas atau tema di kolom atas, lalu klik **Cari**. "
            "Boleh bahasa Indonesia atau Inggris.\n\n"
            "Contoh: `kelapa` · `kulit jagung` · `limbah tulang ikan` · `rumput laut` · "
            "`bioplastik` · `edible film`")
    st.stop()
if not param[0]:
    st.warning("Isi komoditas atau tema terlebih dulu.")
    st.stop()
if not param[2]:
    st.warning("Pilih minimal satu sumber data di Pengaturan lanjutan.")
    st.stop()

with st.spinner("Menelusuri sumber riset… (biasanya 10–60 detik)"):
    data, galat, kueri, info = _cari(*param)

if info["inti_en"]:
    st.caption(f"Dicari sebagai: **{_e(info['inti_id'])}** (Indonesia) dan "
               f"**{_e(info['inti_en'])}** (Inggris)")

for n, e in galat.items():
    st.warning(f"**{n}** {e}")

if not data:
    st.info("Tidak ada hasil. Coba ketik dalam bahasa Inggris (mis. *corn husk*), "
            "mundurkan tahun mulai, atau matikan filter relevansi di Pengaturan lanjutan.")
    st.stop()

df = pd.DataFrame(data)
df["kategori_str"] = df["kategori"].apply("; ".join)
df["produk_str"] = df["produk"].apply("; ".join)
judul_subjek = info["inti_id"] or param[0]

with st.expander(f"Kueri yang dipakai ({len(kueri)})"):
    st.write(", ".join(f"`{q}`" for q in kueri))

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total hasil", f"{len(df):,}".replace(",", "."))
c2.metric("Bentuk produk terdeteksi", int(df["produk"].explode().dropna().nunique()))
c3.metric("Paten", int((df["jenis"] == "paten").sum()))
tahun_ok = df["tahun"].dropna()
c4.metric("Rentang tahun", f"{int(tahun_ok.min())}–{int(tahun_ok.max())}" if len(tahun_ok) else "-")

tab1, tab2, tab3 = st.tabs(["🧺 Contoh produk", "📊 Ringkasan", "📄 Daftar riset"])

# ---------------- Tab 1: galeri produk ----------------
with tab1:
    produk = ringkas_produk(data, info["inti_id"], info["inti_en"] or info["inti_id"], maks=16)
    if not produk:
        st.info("Belum ada nama produk yang terdeteksi dari judul riset. "
                "Lihat tab Daftar riset, atau tambahkan istilah produk di core/produk.py.")
    else:
        st.caption(f"Bentuk produk dari **{_e(judul_subjek)}** yang paling banyak diteliti. "
                   "Gambar adalah ilustrasi berlisensi terbuka dan mungkin tidak persis sama "
                   "dengan produk dalam riset.")
        if st.session_state.get("gambar", True):
            with st.spinner("Mengambil gambar contoh produk…"):
                gbr = _gambar_banyak(tuple(
                    (p["nama_en"], p["kunci"]) for p in produk))
        else:
            gbr = [None] * len(produk)
        st.markdown('<div class="grid">' + "".join(
            kartu_produk(p, g) for p, g in zip(produk, gbr)) + "</div>",
            unsafe_allow_html=True)

# ---------------- Tab 2: ringkasan ----------------
with tab2:
    kat = df.explode("kategori")
    g1, g2 = st.columns(2)
    g1.subheader("Bentuk pengembangan produk")
    g1.bar_chart(kat["kategori"].value_counts(), horizontal=True)
    g2.subheader("Tren publikasi per tahun")
    g2.line_chart(df.dropna(subset=["tahun"]).astype({"tahun": int}).groupby("tahun").size())
    g3, g4 = st.columns(2)
    g3.subheader("Sumber data")
    g3.bar_chart(df["sumber"].value_counts())
    g4.subheader("Produk paling sering diteliti")
    prod = df.explode("produk").dropna(subset=["produk"])
    if len(prod):
        g4.bar_chart(prod["produk"].value_counts().head(15), horizontal=True)
    else:
        g4.write("Belum ada produk terdeteksi.")

# ---------------- Tab 3: tabel ----------------
with tab3:
    f1, f2, f3 = st.columns([2, 2, 1])
    pilih_kat = f1.multiselect("Saring kategori", sorted(kat["kategori"].unique()))
    semua_prod = sorted(df["produk"].explode().dropna().unique())
    pilih_prod = f2.multiselect("Saring produk", semua_prod)
    hanya_oa = f3.checkbox("Open access saja")
    kata = st.text_input("Cari kata dalam judul/abstrak")

    t = df
    if pilih_kat:
        t = t[t["kategori"].apply(lambda ks: any(k in ks for k in pilih_kat))]
    if pilih_prod:
        t = t[t["produk"].apply(lambda ps: any(p in ps for p in pilih_prod))]
    if hanya_oa:
        t = t[t["open_access"] == True]  # noqa: E712
    if kata:
        m = (t["judul"].str.contains(kata, case=False, na=False, regex=False)
             | t["abstrak"].str.contains(kata, case=False, na=False, regex=False))
        t = t[m]

    st.caption(f"{len(t)} hasil ditampilkan")
    kolom = ["tahun", "judul", "produk_str", "kategori_str", "jenis", "venue",
             "penulis", "sitasi", "sumber", "url"]
    st.dataframe(
        t[kolom].sort_values(["tahun", "sitasi"], ascending=False, na_position="last"),
        hide_index=True,
        column_config={
            "tahun": st.column_config.NumberColumn("Tahun", format="%d"),
            "judul": "Judul", "produk_str": "Produk", "kategori_str": "Kategori",
            "jenis": "Jenis", "venue": "Jurnal/Penerbit", "penulis": "Penulis",
            "sitasi": "Sitasi", "sumber": "Sumber",
            "url": st.column_config.LinkColumn("Tautan"),
        },
    )

    ekspor = t.drop(columns=["kategori", "produk"]).rename(
        columns={"kategori_str": "kategori", "produk_str": "produk"})
    nama_file = "riset_" + "".join(ch if ch.isalnum() else "_" for ch in judul_subjek.lower())[:40]
    d1, d2 = st.columns(2)
    d1.download_button("⬇️ Unduh CSV", ekspor.to_csv(index=False).encode("utf-8-sig"),
                       f"{nama_file}.csv", "text/csv")
    buf = io.BytesIO()
    ekspor.to_excel(buf, index=False, sheet_name="Riset")
    d2.download_button("⬇️ Unduh Excel", buf.getvalue(), f"{nama_file}.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.caption("Sumber data: OpenAlex, Crossref, Semantic Scholar, Europe PMC, Lens.org (opsional). "
           "Gambar: Wikimedia Commons / Openverse (lisensi terbuka).")
