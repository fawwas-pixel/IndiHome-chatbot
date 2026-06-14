# streamlit_app.py

import streamlit as st
from prompt import SYSTEM_PROMPT
from tools import (
    format_rupiah,
    get_all_packages,
    recommend_package,
    get_promos,
    answer_faq,
    get_installation_requirements,
    get_registration_flow,
    save_lead,
    get_saved_leads
)

st.set_page_config(
    page_title="Admin Jualan IndiHome",
    page_icon="📶",
    layout="wide"
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Halo, saya admin IndiHome. Saya bisa bantu info paket, promo, syarat pemasangan, dan pendaftaran."
        }
    ]


def simple_chatbot_reply(user_text: str) -> str:
    text = user_text.lower().strip()

    if any(k in text for k in ["paket", "harga", "internet", "wifi"]):
        paket_list = get_all_packages()
        hasil = []
        for paket in paket_list:
            hasil.append(
                f"- {paket['nama']} | {paket['jenis']} | {format_rupiah(paket['tagihan_bulanan'])}/bulan"
            )
        return "Berikut paket yang tersedia:\n" + "\n".join(hasil)

    if any(k in text for k in ["promo", "diskon", "penawaran"]):
        promo_list = get_promos()
        hasil = [f"- {item['nama']}: {item['detail']}" for item in promo_list]
        return "Berikut promo yang tersedia:\n" + "\n".join(hasil)

    if any(k in text for k in ["syarat", "dokumen", "ktp", "pemasangan"]):
        syarat = get_installation_requirements()
        return "Syarat pemasangan:\n" + "\n".join([f"- {s}" for s in syarat])

    if any(k in text for k in ["alur", "daftar", "pendaftaran", "proses"]):
        alur = get_registration_flow()
        return "Alur pendaftaran:\n" + "\n".join([f"{i+1}. {v}" for i, v in enumerate(alur)])

    faq_reply = answer_faq(user_text)
    if "belum ada di data" not in faq_reply.lower():
        return faq_reply

    if any(k in text for k in ["bingung", "rekomendasi", "pilih paket"]):
        return (
            "Boleh, saya bantu rekomendasi paket. "
            "Tolong kirim 3 hal ini: jumlah pengguna, aktivitas internet, dan budget per bulan."
        )

    if any(k in text for k in ["minat", "pasang", "daftar sekarang", "lanjut"]):
        return (
            "Siap. Untuk saya teruskan, kirim nama, lokasi pemasangan, dan nomor WhatsApp."
        )

    return "Saya siap bantu soal paket, promo, syarat pemasangan, dan pendaftaran. Kalau ada info yang belum tersedia, nanti saya teruskan ke admin."


st.title("📶 Admin Jualan IndiHome")
st.caption("Asisten informasi paket, promo, pendaftaran, dan penyimpanan lead")
st.write(SYSTEM_PROMPT)

with st.sidebar:
    st.header("Menu")
    menu = st.radio(
        "Pilih halaman",
        ["Paket", "Rekomendasi", "Promo", "FAQ", "Syarat", "Alur", "Lead", "Chat"]
    )

if menu == "Paket":
    st.header("Daftar Paket")
    for paket in get_all_packages():
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.subheader(paket["nama"])
                st.write(f"**Jenis:** {paket['jenis']}")
                st.write(f"**Catatan:** {paket['catatan']}")

            with col2:
                st.metric("Tagihan", format_rupiah(paket["tagihan_bulanan"]))
                if "biaya_awal" in paket:
                    st.metric("Biaya Awal", format_rupiah(paket["biaya_awal"]))
                elif "biaya_psb" in paket:
                    st.metric("Biaya PSB", str(paket["biaya_psb"]).capitalize())

            if "rincian" in paket:
                with st.expander("Lihat rincian"):
                    for key, value in paket["rincian"].items():
                        label = key.replace("_", " ").title()
                        if isinstance(value, (int, float)):
                            st.write(f"- {label}: {format_rupiah(value)}")
                        else:
                            st.write(f"- {label}: {value}")

elif menu == "Rekomendasi":
    st.header("Rekomendasi Paket")
    with st.form("form_rekomendasi"):
        jumlah_pengguna = st.number_input("Jumlah pengguna", min_value=1, value=1, step=1)
        aktivitas = st.text_input("Aktivitas internet", placeholder="mis. streaming, meeting, game, belajar")
        budget = st.number_input("Budget per bulan", min_value=0, value=200000, step=10000)
        submit_rekomendasi = st.form_submit_button("Lihat rekomendasi")

    if submit_rekomendasi:
        hasil = recommend_package(jumlah_pengguna, aktivitas, budget)
        st.success(hasil)

elif menu == "Promo":
    st.header("Promo Tersedia")
    tab1, tab2 = st.tabs(["Daftar Promo", "Ringkasan"])

    with tab1:
        for promo in get_promos():
            with st.container(border=True):
                st.subheader(promo["nama"])
                st.write(promo["detail"])

    with tab2:
        st.write(f"Total promo tersedia: {len(get_promos())}")

elif menu == "FAQ":
    st.header("FAQ")
    pertanyaan = st.text_input("Tulis pertanyaan Anda")
    if pertanyaan:
        st.info(answer_faq(pertanyaan))

    st.subheader("FAQ Umum")
    contoh_faq = [
        "20 Mbps cukup untuk berapa perangkat?",
        "Apakah pelanggan harus ada saat pemasangan?",
        "Kapan pemasangan dilakukan?",
        "Bagaimana pembayaran setelah terpasang?",
        "Bagaimana jika email tidak bisa dipakai?"
    ]
    for item in contoh_faq:
        with st.expander(item):
            st.write(answer_faq(item))

elif menu == "Syarat":
    st.header("Syarat Pemasangan")
    for i, item in enumerate(get_installation_requirements(), start=1):
        st.write(f"{i}. {item}")

elif menu == "Alur":
    st.header("Alur Pendaftaran")
    for i, item in enumerate(get_registration_flow(), start=1):
        st.write(f"{i}. {item}")

elif menu == "Lead":
    st.header("Simpan Lead")
    with st.form("form_lead"):
        nama = st.text_input("Nama calon pelanggan")
        lokasi = st.text_input("Lokasi pemasangan")
        whatsapp = st.text_input("Nomor WhatsApp")
        paket_diminati = st.text_input("Paket diminati", placeholder="Opsional")
        submit_lead = st.form_submit_button("Simpan lead")

    if submit_lead:
        if nama and lokasi and whatsapp:
            st.success(save_lead(nama, lokasi, whatsapp, paket_diminati))
        else:
            st.error("Nama, lokasi, dan WhatsApp wajib diisi.")

    st.subheader("Daftar Lead Tersimpan")
    leads = get_saved_leads()
    if leads:
        st.dataframe(leads, use_container_width=True)
    else:
        st.info("Belum ada lead tersimpan.")

elif menu == "Chat":
    st.header("Chat Admin")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_prompt = st.chat_input("Tulis pertanyaan Anda di sini...")
    if user_prompt:
        st.session_state.messages.append({"role": "user", "content": user_prompt})

        with st.chat_message("user"):
            st.markdown(user_prompt)

        reply = simple_chatbot_reply(user_prompt)
        st.session_state.messages.append({"role": "assistant", "content": reply})

        with st.chat_message("assistant"):
            st.markdown(reply)

# data.py

PACKAGES = [
    {
        "nama": "EZnet 20 Mbps",
        "jenis": "internet rumah saja",
        "tagihan_bulanan": 194250,
        "rincian": {
            "harga_paket": 170000,
            "biaya_layanan": 5000,
            "ppn": "sudah termasuk dalam total"
        },
        "biaya_awal": 99000,
        "catatan": "Bayar tagihan pertama bulan depan tanggal 5 bulan depan"
    },
    {
        "nama": "One Dynamic 20 Mbps 30 GB",
        "jenis": "internet rumah + paket data mobile",
        "tagihan_bulanan": 227550,
        "rincian": {
            "wifi_rumah": "20 Mbps unlimited",
            "kuota_keluarga": "30 GB per bulan untuk 3 nomor",
            "bonus": "2 perdana Telkomsel gratis"
        },
        "biaya_awal": 99000,
        "catatan": "Kuota keluarga dipakai bersama anggota yang didaftarkan"
    },
    {
        "nama": "IndiHome 50 Mbps Internet Only",
        "jenis": "internet rumah saja",
        "tagihan_bulanan": 230000,
        "biaya_psb": "gratis",
        "catatan": "Ada skema PDD/kontrak khusus, jika lewat masa kontrak bisa jadi tarif reguler"
    }
]

FAQS = [
    {
        "pertanyaan": "20 Mbps cukup untuk berapa perangkat?",
        "jawaban": "20 Mbps dinilai aman untuk sekitar 3 HP, bahkan dipakai untuk TikTok dan game."
    },
    {
        "pertanyaan": "Apakah pelanggan harus ada saat pemasangan?",
        "jawaban": "Tidak harus, asalkan data, share lokasi, foto rumah, dan komunikasi dengan teknisi sudah lengkap."
    },
    {
        "pertanyaan": "Kapan pemasangan dilakukan?",
        "jawaban": "Bisa one day service, tapi tergantung antrian dan kondisi teknisi."
    },
    {
        "pertanyaan": "Bagaimana pembayaran setelah terpasang?",
        "jawaban": "Biaya instalasi dibayar dulu saat layanan aktif, sedangkan tagihan bulanan mengikuti paket dan periode tagihan."
    },
    {
        "pertanyaan": "Bagaimana jika email tidak bisa dipakai?",
        "jawaban": "Bisa ganti atau buat email baru, disarankan sesuai nama di KTP."
    }
]

PROMOS = [
    {
        "nama": "Promo hemat EZnet",
        "detail": "Biaya instalasi hanya Rp99.000, tagihan bulanan Rp194.250."
    },
    {
        "nama": "Promo One Dynamic",
        "detail": "Dapat Wi-Fi rumah 20 Mbps, kuota keluarga 30 GB per bulan, dan 2 perdana Telkomsel gratis."
    },
    {
        "nama": "Promo awal pasang",
        "detail": "Saat layanan terpasang dan aktif, pelanggan hanya bayar biaya instalasi Rp99.000."
    }
]

SYARAT_PEMASANGAN = [
    "Nama sesuai KTP",
    "Nomor HP/WA aktif",
    "Email aktif dan sebaiknya sesuai nama KTP",
    "Alamat pemasangan lengkap",
    "Pilihan paket dan jenis pemasangan",
    "Foto KTP wajib",
    "Foto rumah tampak depan wajib",
    "Share lokasi akurat",
    "Bersedia menerima konfirmasi dari teknisi"
]

ALUR_PENDAFTARAN = [
    "Konsultasi paket dan cek kebutuhan pemakaian",
    "Isi form pendaftaran",
    "Kirim data dan lampiran foto KTP serta foto rumah",
    "Verifikasi email dan WA",
    "Buka link registrasi dari WA atau email",
    "Pilih jadwal pemasangan terdekat",
    "Order diproses dan masuk antrian",
    "Teknisi menghubungi pelanggan",
    "Pemasangan dilakukan",
    "Setelah aktif, pembayaran instalasi dan tagihan mengikuti ketentuan paket"
]
# tools.py

import streamlit as st
from data import PACKAGES, FAQS, PROMOS, SYARAT_PEMASANGAN, ALUR_PENDAFTARAN


def _init_saved_leads():
    if "saved_leads" not in st.session_state:
        st.session_state.saved_leads = []


def format_rupiah(angka: int) -> str:
    return f"Rp{angka:,}".replace(",", ".")


def get_all_packages() -> list:
    return PACKAGES


def recommend_package(jumlah_pengguna, aktivitas: str, budget) -> str:
    aktivitas = str(aktivitas).lower()
    hasil = []

    try:
        budget_int = int(budget)
    except Exception:
        budget_int = 0

    for paket in PACKAGES:
        harga = paket.get("tagihan_bulanan", 0)
        if budget_int and harga > budget_int:
            continue
        hasil.append(paket)

    if budget_int <= 200000:
        return "Budget Anda paling cocok ke EZnet 20 Mbps dengan tagihan sekitar Rp194.250 per bulan."

    if budget_int <= 230000:
        if "mobile" in aktivitas or "kuota" in aktivitas:
            return "Saya rekomendasikan One Dynamic 20 Mbps 30 GB karena ada Wi-Fi rumah plus kuota keluarga."
        return "Saya rekomendasikan IndiHome 50 Mbps Internet Only atau One Dynamic 20 Mbps, tergantung Anda butuh kuota mobile atau tidak."

    if int(jumlah_pengguna) >= 4 or "gaming" in aktivitas or "streaming" in aktivitas:
        return "Saya rekomendasikan IndiHome 50 Mbps Internet Only karena lebih nyaman untuk pemakaian ramai, streaming, atau gaming."

    if hasil:
        ringkas = []
        for paket in hasil[:3]:
            ringkas.append(
                f"{paket['nama']} - {paket['jenis']} - tagihan {format_rupiah(paket['tagihan_bulanan'])}"
            )
        return "Pilihan yang bisa dipertimbangkan:\n" + "\n".join(ringkas)

    return "Belum ada paket yang benar-benar cocok dengan budget tersebut. Saya bisa bantu teruskan ke admin."


def get_promos() -> list:
    return PROMOS


def answer_faq(question: str) -> str:
    q = question.lower()

    for item in FAQS:
        p = item["pertanyaan"].lower()
        if p in q or any(k in q for k in p.split()):
            return item["jawaban"]

    return "Maaf, FAQ itu belum ada di data. Nanti bisa saya teruskan ke admin."


def get_installation_requirements() -> list:
    return SYARAT_PEMASANGAN


def get_registration_flow() -> list:
    return ALUR_PENDAFTARAN


def save_lead(nama: str, lokasi: str, whatsapp: str, paket_diminati: str = "") -> str:
    _init_saved_leads()

    lead = {
        "nama": nama,
        "lokasi": lokasi,
        "whatsapp": whatsapp,
        "paket_diminati": paket_diminati
    }
    st.session_state.saved_leads.append(lead)
    return f"Lead berhasil disimpan untuk {nama} di {lokasi}."


def get_saved_leads() -> list:
    _init_saved_leads()
    return st.session_state.saved_leads

# prompt.py

SYSTEM_PROMPT = """
Kamu adalah admin jualan IndiHome yang ramah, singkat, dan persuasif.

Tugas:
- Membantu calon pelanggan memahami paket, harga, promo, syarat pemasangan, dan proses pendaftaran.
- Menjawab hanya berdasarkan data dan tools yang tersedia.
- Jika user bingung memilih paket, tanyakan:
  1. jumlah pengguna
  2. aktivitas internet (streaming, meeting, game, belajar, dll)
  3. budget per bulan

Aturan:
- Gunakan bahasa Indonesia yang sopan, singkat, dan mudah dipahami.
- Jangan mengarang harga, promo, atau ketentuan jika data tidak tersedia.
- Jika informasi tidak ada, katakan bahwa info akan diteruskan ke admin.
- Jika user menunjukkan minat, arahkan untuk mengirim nama, lokasi pemasangan, dan nomor WhatsApp.
- Jika data calon pelanggan sudah lengkap, bantu simpan lead.
"""
