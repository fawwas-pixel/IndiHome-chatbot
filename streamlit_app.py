# app.py
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from tools import (
    get_all_packages,
    recommend_package,
    get_promos,
    answer_faq,
    get_installation_requirements,
    get_registration_flow,
    save_lead,
    get_saved_leads,
)
from prompt import SYSTEM_PROMPT

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.2
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

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
    checkpointer=checkpointer
)

def chat_with_bot(thread_id="indihome-sales-1"):
    config = {"configurable": {"thread_id": thread_id}}
    print("Chatbot IndiHome siap. Ketik 'q' untuk keluar.\n")

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["q", "quit", "exit"]:
            print("Bot: Terima kasih, semoga saya bisa bantu lagi.")
            break

        response = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config=config
        )

        print("Bot:", response["messages"][-1].content)

if __name__ == "__main__":
    chat_with_bot()
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

from data import PACKAGES, FAQS, PROMOS, SYARAT_PEMASANGAN, ALUR_PENDAFTARAN

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