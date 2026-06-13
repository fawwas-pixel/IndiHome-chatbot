import streamlit as st

st.set_page_config(page_title="My App", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1rem; padding-bottom: 1rem;}
.card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 16px;
}
.chatbox {
    background: #2563eb;
    color: white;
    padding: 12px 16px;
    border-radius: 12px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.write("Dashboard")
    st.write("History")
    st.write("Settings")

main, right = st.columns([4, 1.3])

with main:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.title("Task Bot")
    st.markdown("<div class='chatbox'>Halo, saya siap membantu.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='card'>Info panel kanan</div>", unsafe_allow_html=True)