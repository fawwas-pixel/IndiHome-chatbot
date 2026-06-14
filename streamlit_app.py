# =========================
# data.py
# =========================

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

# =========================
# tools.py
# =========================

import os
import uuid
import json
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

lead_database = []

def format_rupiah(angka: int) -> str:
    return f"Rp{angka:,}".replace(",", ".")

@tool
def get_all_packages() -> str:
    """Mengambil semua paket IndiHome yang tersedia."""
    hasil = []
    for paket in PACKAGES:
        biaya_awal = paket.get("biaya_awal", 0)
        hasil.append(
            f"{paket['nama']} | jenis: {paket['jenis']} | tagihan: {format_rupiah(paket['tagihan_bulanan'])} | biaya awal: {format_rupiah(biaya_awal)} | catatan: {paket.get('catatan', '-')}"
        )
    return "\n".join(hasil)

@tool
def recommend_package(jumlah_pengguna: str = "", aktivitas: str = "", budget: str = "") -> str:
    """Memberikan rekomendasi paket IndiHome berdasarkan jumlah pengguna, aktivitas internet, dan budget."""
    hasil = []
    budget_int = None

    if budget:
        try:
            budget_int = int("".join(filter(str.isdigit, str(budget))))
        except Exception:
            budget_int = None

    for paket in PACKAGES:
        harga = paket.get("tagihan_bulanan", 0)
        if budget_int and harga > budget_int:
            continue
        hasil.append(f"{paket['nama']} - {paket['jenis']} - {format_rupiah(harga)}")

    if not hasil:
        return "Belum ada paket yang benar-benar cocok dengan budget tersebut. Saya bisa bantu teruskan ke admin."

    if aktivitas:
        aktivitas = aktivitas.lower()
        if "kuota" in aktivitas or "mobile" in aktivitas:
            for item in hasil:
                if "One Dynamic" in item:
                    return f"Rekomendasi utama: {item}"

    return "Rekomendasi paket:\n" + "\n".join(hasil[:3])

@tool
def get_promos() -> str:
    """Mengambil daftar promo IndiHome yang tersedia."""
    hasil = []
    for promo in PROMOS:
        hasil.append(f"{promo['nama']}: {promo['detail']}")
    return "\n".join(hasil)

@tool
def answer_faq(user_question: str) -> str:
    """Menjawab pertanyaan umum pelanggan berdasarkan FAQ IndiHome yang tersedia."""
    q = user_question.lower()
    for item in FAQS:
        pertanyaan = item["pertanyaan"].lower()
        if pertanyaan in q or any(k in q for k in pertanyaan.split()):
            return item["jawaban"]
    return "Jawaban belum tersedia di data. Nanti saya bantu teruskan ke admin ya."

@tool
def get_installation_requirements() -> str:
    """Mengambil syarat pemasangan IndiHome."""
    return "\n".join([f"- {item}" for item in SYARAT_PEMASANGAN])

@tool
def get_registration_flow() -> str:
    """Mengambil alur pendaftaran IndiHome dari awal sampai pemasangan aktif."""
    return "\n".join([f"{i+1}. {step}" for i, step in enumerate(ALUR_PENDAFTARAN)])

@tool
def save_lead(nama: str, lokasi: str, whatsapp: str, paket_diminati: str = "") -> str:
    """Menyimpan data lead calon pelanggan IndiHome ke memori sederhana."""
    data = {
        "nama": nama,
        "whatsapp": whatsapp,
        "lokasi": lokasi,
        "paket_diminati": paket_diminati
    }
    lead_database.append(data)
    return f"Lead untuk {nama} berhasil disimpan dan siap diteruskan ke admin sales."

@tool
def get_saved_leads() -> str:
    """Mengambil daftar lead calon pelanggan yang sudah tersimpan."""
    if not lead_database:
        return "Belum ada lead tersimpan."
    return json.dumps(lead_database, ensure_ascii=False, indent=2)

# =========================
# prompt.py
# =========================

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
- Fokus pada penjualan dan informasi layanan IndiHome, hindari topik di luar itu.
"""

# =========================
# CODE UI STREAMLIT
# =========================

st.set_page_config(
    page_title="Chatbot Sales IndiHome",
    page_icon="💬",
    layout="wide"
)

GOOGLE_API_KEY = st.secrets.get("GOOGLE_API_KEY", os.environ.get("GOOGLE_API_KEY"))

if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY belum diatur di Streamlit Secrets.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"indihome-{uuid.uuid4()}"

if "agent" not in st.session_state:
    model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.2,
    google_api_key=GOOGLE_API_KEY,
    max_retries=2
)
    checkpointer = InMemorySaver()

    tools = [
        get_all_packages,
        recommend_package,
        get_promos,
        answer_faq,
        get_installation_requirements,
        get_registration_flow,
        save_lead,
        get_saved_leads,
    ]

    st.session_state.agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer
    )

agent = st.session_state.agent

def local_fallback_answer(user_text: str) -> str:
    q = user_text.lower()

    if "paket" in q:
        hasil = []
        for paket in PACKAGES:
            hasil.append(
                f"{paket['nama']} - {paket['jenis']} - {format_rupiah(paket['tagihan_bulanan'])}/bulan"
            )
        return "Berikut paket yang tersedia:\n\n" + "\n".join(hasil)

    if "promo" in q:
        hasil = [f"{item['nama']}: {item['detail']}" for item in PROMOS]
        return "Promo saat ini:\n\n" + "\n".join(hasil)

    if "syarat" in q or "pemasangan" in q:
        return "Syarat pemasangan:\n\n" + "\n".join([f"- {x}" for x in SYARAT_PEMASANGAN])

    for item in FAQS:
        pertanyaan = item["pertanyaan"].lower()
        if pertanyaan in q or any(k in q for k in pertanyaan.split()):
            return item["jawaban"]

    return (
        "Maaf, sistem sedang sibuk atau jawaban belum tersedia. "
        "Saya bisa bantu info paket, promo, syarat pemasangan, atau simpan data lead Anda."
    )

with st.sidebar:
    st.title("IndiHome Sales Bot")
    st.caption("Bantu pelanggan pilih paket, cek promo, dan daftar pemasangan.")

    st.subheader("Paket Tersedia")
    for paket in PACKAGES:
        biaya_awal = paket.get("biaya_awal", 0)
        st.markdown(
            f"""
            **{paket['nama']}**  
            Jenis: {paket['jenis']}  
            Tagihan: {format_rupiah(paket['tagihan_bulanan'])}  
            Biaya awal: {format_rupiah(biaya_awal)}
            """
        )
        st.divider()

    st.subheader("Promo Aktif")
    for promo in PROMOS:
        st.write(f"- {promo['nama']}: {promo['detail']}")

col1, col2 = st.columns([2, 1])

with col1:
    st.title("💬 Chatbot Sales IndiHome")
    st.write("Tanyakan paket, promo, syarat pemasangan, atau langsung daftar.")

    for msg in st.session_state.messages:
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.markdown(msg["content"])

    prompt = st.chat_input("Tulis pertanyaan Anda...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Sedang memproses jawaban..."):
                try:
                    config = {"configurable": {"thread_id": st.session_state.thread_id}}
                    response = agent.invoke(
                        {"messages": [{"role": "user", "content": prompt}]},
                        config=config
                    )
                    bot_reply = response["messages"][-1].content

                    if not bot_reply or str(bot_reply).strip() == "":
                        bot_reply = local_fallback_answer(prompt)

                except Exception:
                    bot_reply = local_fallback_answer(prompt)

                st.markdown(bot_reply)

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
with col2:
    st.subheader("Form Lead")
    with st.form("lead_form"):
        nama = st.text_input("Nama")
        lokasi = st.text_input("Lokasi pemasangan")
        whatsapp = st.text_input("Nomor WhatsApp")
        paket_diminati = st.text_input("Paket diminati (opsional)")
        submitted = st.form_submit_button("Simpan Lead")

        if submitted:
            if nama and lokasi and whatsapp:
                hasil = save_lead.invoke({
                    "nama": nama,
                    "lokasi": lokasi,
                    "whatsapp": whatsapp,
                    "paket_diminati": paket_diminati
                })
                st.success(hasil)
            else:
                st.warning("Lengkapi nama, lokasi, dan WhatsApp dulu.")

    with st.expander("FAQ"):
        for item in FAQS:
            st.write(f"- {item['pertanyaan']}")
            st.caption(item["jawaban"])

    with st.expander("Syarat Pemasangan"):
        for item in SYARAT_PEMASANGAN:
            st.write(f"- {item}")

    with st.expander("Alur Pendaftaran"):
        for i, step in enumerate(ALUR_PENDAFTARAN, start=1):
            st.write(f"{i}. {step}")

    with st.expander("Lead Tersimpan"):
        if lead_database:
            st.json(lead_database)
        else:
            st.info("Belum ada lead tersimpan.")

