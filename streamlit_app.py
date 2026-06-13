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