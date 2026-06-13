import subprocess
import time

def run_streamlit(filename, port=8501):
    # Kill SEMUA proses streamlit, bukan hanya yang kita spawn
    subprocess.run(["pkill", "-f", "streamlit"], capture_output=True)

    # Force-free port kalau masih ada yang nempel
    subprocess.run(["fuser", "-k", f"{port}/tcp"], capture_output=True)

    # Tutup semua tunnel ngrok
    ngrok.kill()

    # Tunggu port benar-benar bebas
    time.sleep(3)

    proc = subprocess.Popen(
        [
            "streamlit", "run", filename,
            "--server.headless=true",
            "--server.port", str(port),
            "--server.enableCORS=false",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    time.sleep(3)

    public_url = ngrok.connect(port)
    print(f"Streamlit berjalan: {public_url}")

    return proc
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

import subprocess
import time

# tools.py

# from data import PACKAGES, FAQS, PROMOS, SYARAT_PEMASANGAN, ALUR_PENDAFTARAN

lead_database = []

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
            except:
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
    data = {
        "nama": nama,
        "whatsapp": whatsapp,
        "lokasi": lokasi,
        "paket_diminati": paket_diminati
    }
    lead_database.append(data)
    return f"Lead untuk {nama} berhasil disimpan dan siap diteruskan ke admin sales."

def get_saved_leads() -> list:
    return lead_database

saved_leads = []

def get_all_packages() -> list:
    """Mengambil semua paket IndiHome yang tersedia."""
    return [
        {
            "nama": "EZnet 20 Mbps",
            "jenis": "Internet rumah saja",
            "tagihan_bulanan": 194250,
            "biaya_awal": 99000,
            "catatan": "Bayar tagihan pertama bulan depan tanggal 5."
        },
        {
            "nama": "One Dynamic 20 Mbps 30 GB",
            "jenis": "Internet rumah + paket data mobile",
            "tagihan_bulanan": 227550,
            "biaya_awal": 99000,
            "catatan": "Kuota keluarga 30 GB per bulan untuk 3 nomor, bonus 2 perdana Telkomsel gratis."
        },
        {
            "nama": "IndiHome 50 Mbps Internet Only",
            "jenis": "Internet rumah saja",
            "tagihan_bulanan": 230000,
            "biaya_awal": 0,
            "catatan": "Ada skema PDD kontrak khusus, setelah lewat masa kontrak bisa jadi tarif reguler."
        }
    ]


def recommend_package(jumlah_pengguna: int, aktivitas: str, budget: int) -> str:
    """Memberikan rekomendasi paket IndiHome berdasarkan jumlah pengguna, aktivitas internet, dan budget."""
    aktivitas = aktivitas.lower()

    if budget <= 200000:
        return "Budget Anda paling cocok ke EZnet 20 Mbps dengan tagihan sekitar Rp194.250 per bulan."
    elif budget <= 230000:
        if "mobile" in aktivitas or "kuota" in aktivitas:
            return "Saya rekomendasikan One Dynamic 20 Mbps 30 GB karena ada Wi-Fi rumah plus kuota keluarga."
        return "Saya rekomendasikan IndiHome 50 Mbps Internet Only atau One Dynamic 20 Mbps, tergantung Anda butuh kuota mobile atau tidak."
    else:
        if jumlah_pengguna >= 4 or "gaming" in aktivitas or "streaming" in aktivitas:
            return "Saya rekomendasikan IndiHome 50 Mbps Internet Only karena lebih nyaman untuk pemakaian ramai, streaming, atau gaming."
        return "Untuk kebutuhan umum keluarga, One Dynamic 20 Mbps atau IndiHome 50 Mbps sama-sama layak dipertimbangkan."


def get_promos() -> list:
    """Mengambil daftar promo IndiHome yang sedang tersedia."""
    return [
        "Promo hemat EZnet: biaya instalasi hanya Rp99.000, tagihan bulanan Rp194.250.",
        "Promo One Dynamic: Wi-Fi rumah 20 Mbps, kuota keluarga 30 GB per bulan, dan 2 perdana Telkomsel gratis.",
        "Promo awal pasang: saat layanan aktif, pelanggan hanya bayar biaya instalasi Rp99.000."
    ]


def answer_faq(question: str) -> str:
    """Menjawab pertanyaan umum pelanggan berdasarkan FAQ IndiHome yang tersedia."""
    q = question.lower()

    faq = {
        "20 mbps cukup untuk berapa perangkat": "20 Mbps dinilai aman untuk sekitar 3 HP, bahkan bisa dipakai untuk TikTok dan game ringan.",
        "apakah pelanggan harus ada saat pemasangan": "Tidak harus, asalkan data, share lokasi, foto rumah, dan komunikasi dengan teknisi sudah lengkap.",
        "kapan pemasangan dilakukan": "Bisa one day service, tetapi tetap tergantung antrean dan kondisi teknisi.",
        "bagaimana pembayaran setelah terpasang": "Biaya instalasi dibayar saat layanan aktif, sedangkan tagihan bulanan mengikuti paket dan periode tagihan.",
        "bagaimana jika email tidak bisa dipakai": "Bisa ganti atau buat email baru, dan sebaiknya sesuai nama di KTP."
    }

    for key, value in faq.items():
        if key in q:
            return value

    return "Maaf, FAQ itu belum ada di data. Nanti bisa saya teruskan ke admin."


def get_installation_requirements() -> list:
    """Mengambil syarat pemasangan IndiHome."""
    return [
        "Nama sesuai KTP.",
        "Nomor HP/WhatsApp aktif.",
        "Email aktif dan sebaiknya sesuai nama KTP.",
        "Alamat pemasangan lengkap.",
        "Pilihan paket dan jenis pemasangan.",
        "Foto KTP wajib.",
        "Foto rumah tampak depan wajib.",
        "Share lokasi akurat.",
        "Bersedia menerima konfirmasi dari teknisi."
    ]


def get_registration_flow() -> list:
    """Mengambil alur pendaftaran IndiHome dari awal sampai pemasangan aktif."""
    return [
        "Konsultasi paket dan cek kebutuhan pemakaian.",
        "Isi form pendaftaran.",
        "Kirim data dan lampiran foto KTP serta foto rumah.",
        "Verifikasi email dan WhatsApp.",
        "Buka link registrasi dari WhatsApp atau email.",
        "Pilih jadwal pemasangan terdekat.",
        "Order diproses dan masuk antrean.",
        "Teknisi menghubungi pelanggan.",
        "Pemasangan dilakukan.",
        "Setelah aktif, pembayaran instalasi dan tagihan mengikuti ketentuan paket."
    ]


def save_lead(nama: str, lokasi: str, whatsapp: str) -> str:
    """Menyimpan data lead calon pelanggan IndiHome ke memori sederhana."""
    lead = {
        "nama": nama,
        "lokasi": lokasi,
        "whatsapp": whatsapp
    }
    saved_leads.append(lead)
    return f"Lead berhasil disimpan untuk {nama} di {lokasi} dengan WhatsApp {whatsapp}."


def get_saved_leads() -> list:
    """Mengambil daftar lead calon pelanggan yang sudah tersimpan."""
    return saved_leads

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
- Fokus pada penjualan dan informasi layanan IndiHome, hindari topik di luar itu.
"""

# app.py

import os
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

# Jika di Google Colab


# =========================================================
# Pastikan fungsi-fungsi ini SUDAH didefinisikan di cell sebelumnya:
# - get_all_packages
# - recommend_package
# - get_promos
# - answer_faq
# - get_installation_requirements
# - get_registration_flow
# - save_lead
# - get_saved_leads
# Dan SYSTEM_PROMPT juga sudah ada.
# =========================================================

# Ambil API key dari Colab Secrets
try:
    GOOGLE_API_KEY = userdata.get("GEMINI_API_KEY")
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
except Exception:
    raise ValueError(
        "Secret GEMINI_API_KEY belum ditemukan. "
        "Tambahkan dulu di Colab > Secrets."
    )

# Inisialisasi model
model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.2,
    google_api_key=os.environ["GOOGLE_API_KEY"]
)

# Memory percakapan
checkpointer = InMemorySaver()

# Daftar tools
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

# Buat agent
agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
    checkpointer=checkpointer
)

# Fungsi chat interaktif
def chat_with_bot(thread_id: str = "indihome-sales-1"):
    """Menjalankan chatbot sales IndiHome dengan memory per thread."""
    config = {"configurable": {"thread_id": thread_id}}
    print("Chatbot IndiHome siap. Ketik 'q' untuk keluar.\n")

    while True:
        user_input = input("User: ").strip()

        if user_input.lower() in ["q", "quit", "exit"]:
            print("Bot: Terima kasih, semoga saya bisa bantu lagi.")
            break

        if not user_input:
            print("Bot: Silakan tulis pertanyaan atau kebutuhan Anda ya.")
            continue

        response = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config
        )

        print("Bot:", response["messages"][-1].content)

# Jalankan chatbot
chat_with_bot()

#CODE UI STREAMLIT

import os
import uuid
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

# =========================
# PASTE tools & SYSTEM_PROMPT di atas file ini
# atau import dari file lain
# =========================

st.set_page_config(
    page_title="Chatbot Sales IndiHome",
    page_icon="💬",
    layout="wide"
)

# =========================
# Inisialisasi state
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"indihome-{uuid.uuid4()}"

if "agent" not in st.session_state:
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.2,
        google_api_key=os.environ["GOOGLE_API_KEY"]
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

# =========================
# Sidebar
# =========================
with st.sidebar:
    st.title("IndiHome Sales Bot")
    st.caption("Bantu pelanggan pilih paket, cek promo, dan daftar pemasangan.")

    st.subheader("Paket Tersedia")
    for paket in get_all_packages():
        st.markdown(
            f"""
            **{paket['nama']}**  
            Jenis: {paket['jenis']}  
            Tagihan: Rp{paket['tagihan_bulanan']:,}  
            Biaya awal: Rp{paket['biaya_awal']:,}
            """
        )
        st.divider()

    st.subheader("Promo Aktif")
    for promo in get_promos():
        st.write(f"- {promo}")

# =========================
# Main layout
# =========================
col1, col2 = st.columns([2, 1])

with col1:
    st.title("💬 Chatbot Sales IndiHome")
    st.write("Tanyakan paket, promo, syarat pemasangan, atau langsung daftar.")

    # Tombol cepat
    quick_col1, quick_col2, quick_col3 = st.columns(3)
    with quick_col1:
        if st.button("Lihat Paket"):
            st.session_state.messages.append(
                {"role": "user", "content": "Paket IndiHome apa saja yang tersedia?"}
            )
    with quick_col2:
        if st.button("Lihat Promo"):
            st.session_state.messages.append(
                {"role": "user", "content": "Promo IndiHome yang tersedia apa saja?"}
            )
    with quick_col3:
        if st.button("Syarat Pasang"):
            st.session_state.messages.append(
                {"role": "user", "content": "Apa syarat pemasangan IndiHome?"}
            )

    # Tampilkan chat history
    for msg in st.session_state.messages:
        with st.chat_message("user" if msg["role"] == "user" else "assistant"):
            st.markdown(msg["content"])

    # Input chat
    prompt = st.chat_input("Tulis pertanyaan Anda...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})

        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        response = agent.invoke(
            {"messages": [{"role": "user", "content": prompt}]},
            config=config
        )

        bot_reply = response["messages"][-1].content
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        st.rerun()

with col2:
    st.subheader("Form Lead")
    with st.form("lead_form"):
        nama = st.text_input("Nama")
        lokasi = st.text_input("Lokasi pemasangan")
        whatsapp = st.text_input("Nomor WhatsApp")
        submitted = st.form_submit_button("Simpan Lead")

        if submitted:
            if nama and lokasi and whatsapp:
                hasil = save_lead(nama, lokasi, whatsapp)
                st.success(hasil)
            else:
                st.warning("Lengkapi nama, lokasi, dan WhatsApp dulu.")

    with st.expander("FAQ"):
        st.write("- 20 Mbps cukup untuk sekitar 3 HP.")
        st.write("- Pemasangan bisa one day service tergantung antrean.")
        st.write("- Pelanggan tidak harus ada saat pemasangan jika data lengkap.")

    with st.expander("Syarat Pemasangan"):
        for item in get_installation_requirements():
            st.write(f"- {item}")

    with st.expander("Alur Pendaftaran"):
        for i, step in enumerate(get_registration_flow(), start=1):
            st.write(f"{i}. {step}")

    with st.expander("Lead Tersimpan"):
        leads = get_saved_leads()
        if leads:
            st.json(leads)
        else:
            st.info("Belum ada lead tersimpan.")
