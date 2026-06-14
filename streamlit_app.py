import streamlit as st
from data import (
    PACKAGES,
    FAQS,
    PROMOS,
    SYARAT_PEMASANGAN,
    ALUR_PENDAFTARAN
)


def format_rupiah(angka):
    if isinstance(angka, (int, float)):
        return f"Rp{angka:,.0f}".replace(",", ".")
    return str(angka)


st.set_page_config(
    page_title="Promo IndiHome",
    page_icon="📶",
    layout="wide"
)

st.title("📶 Informasi Paket Internet")
st.caption("Data paket, promo, FAQ, syarat pemasangan, dan alur pendaftaran")

with st.sidebar:
    st.header("Navigasi")
    menu = st.radio(
        "Pilih halaman",
        ["Paket", "Promo", "FAQ", "Syarat Pemasangan", "Alur Pendaftaran", "Data Mentah"]
    )

if menu == "Paket":
    st.header("Daftar Paket")

    for paket in PACKAGES:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.subheader(paket["nama"])
                st.write(f"**Jenis:** {paket['jenis']}")
                st.write(f"**Catatan:** {paket['catatan']}")

            with col2:
                st.metric("Tagihan Bulanan", format_rupiah(paket["tagihan_bulanan"]))
                if "biaya_awal" in paket:
                    st.metric("Biaya Awal", format_rupiah(paket["biaya_awal"]))
                elif "biaya_psb" in paket:
                    st.metric("Biaya PSB", str(paket["biaya_psb"]).capitalize())

            if "rincian" in paket:
                with st.expander("Lihat rincian paket"):
                    for key, value in paket["rincian"].items():
                        label = key.replace("_", " ").title()
                        if isinstance(value, (int, float)):
                            st.write(f"- {label}: {format_rupiah(value)}")
                        else:
                            st.write(f"- {label}: {value}")

elif menu == "Promo":
    st.header("Daftar Promo")

    tab1, tab2 = st.tabs(["Promo Aktif", "Ringkasan"])  
    with tab1:
        for promo in PROMOS:
            with st.container(border=True):
                st.subheader(promo["nama"])
                st.write(promo["detail"])

    with tab2:
        st.write(f"Total promo tersedia: **{len(PROMOS)}**")
        st.write("Promo dapat berubah mengikuti kebijakan wilayah dan ketersediaan.")

elif menu == "FAQ":
    st.header("Pertanyaan yang Sering Ditanyakan")

    for item in FAQS:
        with st.expander(item["pertanyaan"]):
            st.write(item["jawaban"])

elif menu == "Syarat Pemasangan":
    st.header("Syarat Pemasangan")
    for i, syarat in enumerate(SYARAT_PEMASANGAN, start=1):
        st.write(f"{i}. {syarat}")

elif menu == "Alur Pendaftaran":
    st.header("Alur Pendaftaran")
    for i, langkah in enumerate(ALUR_PENDAFTARAN, start=1):
        st.write(f"{i}. {langkah}")

elif menu == "Data Mentah":
    st.header("Data Mentah")
    data_tab1, data_tab2, data_tab3 = st.tabs(["Packages", "FAQs", "Promos"])

    with data_tab1:
        st.json(PACKAGES)

    with data_tab2:
        st.json(FAQS)

    with data_tab3:
        st.json(PROMOS)
        # tools.py

import streamlit as st
from data import PACKAGES, FAQS, PROMOS, SYARAT_PEMASANGAN, ALUR_PENDAFTARAN


def _init_lead_db():
    if "lead_database" not in st.session_state:
        st.session_state.lead_database = []


def format_rupiah(angka: int) -> str:
    return f"Rp{angka:,}".replace(",", ".")


def get_all_packages() -> list:
    return PACKAGES


def recommend_package(jumlah_pengguna: str, aktivitas: str, budget: str) -> str:
    hasil = []

    for paket in PACKAGES:
        nama = paket["nama"]
        harga = paket.get("tagihan_bulanan", 0)

        if budget:
            try:
                budget_int = int("".join(filter(str.isdigit, budget)))
                if harga > budget_int:
                    continue
            except Exception:
                pass

        hasil.append(
            f"{nama} - {paket['jenis']} - tagihan bulanan {format_rupiah(harga)}"
        )

    if not hasil:
        return "Belum ada paket yang benar-benar cocok dengan budget tersebut. Saya bisa bantu teruskan ke admin."

    return "\n".join(hasil[:3])


def get_promos() -> list:
    return PROMOS


def answer_faq(user_question: str) -> str:
    q = user_question.lower()
    for item in FAQS:
        if item["pertanyaan"].lower() in q or any(k in q for k in item["pertanyaan"].lower().split()):
            return item["jawaban"]
    return "Jawaban belum tersedia di data. Nanti saya bantu teruskan ke admin ya."


def get_installation_requirements() -> list:
    return SYARAT_PEMASANGAN


def get_registration_flow() -> list:
    return ALUR_PENDAFTARAN


def save_lead(nama: str, whatsapp: str, lokasi: str, paket_diminati: str = "") -> str:
    _init_lead_db()

    data = {
        "nama": nama,
        "whatsapp": whatsapp,
        "lokasi": lokasi,
        "paket_diminati": paket_diminati
    }
    st.session_state.lead_database.append(data)
    return f"Lead untuk {nama} berhasil disimpan dan siap diteruskan ke admin sales."


def get_saved_leads() -> list:
    _init_lead_db()
    return st.session_state.lead_database