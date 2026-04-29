import streamlit as st
import streamlit.components.v1 as components
import math
from datetime import datetime, date

# --- [ 1. INITIAL SETUP ] ---
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00ff41"
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = "MAIN MENU"

st.set_page_config(page_title="SYNAPSE X", layout="wide")

# CSS: ซ่อนทุกอย่างของ Streamlit และแต่ง UI ใหม่ให้เหมือนแอปมือถือ
st.markdown(f"""
    <style>
    header, footer, .stDeployButton {{visibility: hidden; display: none !important;}}
    [data-testid="stSidebar"] {{display: none;}} /* ปิด Sidebar ไปเลย */
    
    .stApp {{ background-color: #000; color: #ffffff; }}
    
    .neon-btn {{
        background-color: #111;
        border: 2px solid {st.session_state.theme_color};
        color: {st.session_state.theme_color};
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 10px;
        cursor: pointer;
        font-family: 'Orbitron', sans-serif;
        box-shadow: 0 0 10px {st.session_state.theme_color};
    }}
    
    .neon-title {{
        color: {st.session_state.theme_color};
        text-shadow: 0 0 15px {st.session_state.theme_color};
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        margin-bottom: 30px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- [ 2. NAVIGATION LOGIC ] ---
def go_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- [ 3. PAGE CONTENT ] ---

# หน้าเมนูหลัก (ใช้แทน Sidebar)
if st.session_state.current_page == "MAIN MENU":
    st.markdown("<h1 class='neon-title'>SYNAPSE X</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 SETTINGS", use_container_width=True): go_to("SETTINGS")
        if st.button("🛰️ GPS & CHAT", use_container_width=True): go_to("GPS")
    with col2:
        if st.button("🎧 MUSIC", use_container_width=True): go_to("MUSIC")
        if st.button("🧬 DECODER", use_container_width=True): go_to("DECODER")
    
    if st.button("🎙️ SENSOR LAB", use_container_width=True): go_to("SENSOR")
    
    st.divider()
    st.caption(f"AGENT: {st.session_state.user_name} | 'อยู่นิ่งๆ ไม่เจ็บตัว'")

# หน้าลูก (Sub-pages)
else:
    # ปุ่มกดกลับเมนูหลัก (Home Button)
    if st.button("⬅️ BACK TO MENU"):
        go_to("MAIN MENU")
    st.write("---")

    if st.session_state.current_page == "SETTINGS":
        st.markdown("<h2 class='neon-title'>SETTINGS</h2>", unsafe_allow_html=True)
        st.session_state.user_name = st.text_input("AGENT NAME", value=st.session_state.user_name)
        color = st.color_picker("NEON COLOR", st.session_state.theme_color)
        if st.button("SAVE THEME"):
            st.session_state.theme_color = color
            st.rerun()

    elif st.session_state.current_page == "DECODER":
        st.markdown("<h2 class='neon-title'>COSMIC DECODER</h2>", unsafe_allow_html=True)
        # ฟังก์ชันคำนวณ 3 หัวข้อ (เดิม)
        st.write("1. รหัสฐานวัน:", round(date.today().isoweekday() * 1.618, 4))
        st.write("2. รหัสจันทรคติ: 29.53")
        st.write("3. รหัสสมดุล: ALPHA-01")

    elif st.session_state.current_page == "MUSIC":
        st.markdown("<h2 class='neon-title'>NEON MUSIC</h2>", unsafe_allow_html=True)
        st.info("ระบบเครื่องเล่นเพลงพร้อมทำงาน...")
        # ใส่โค้ด Mixer ของคุณที่นี่

    elif st.session_state.current_page == "GPS":
        st.markdown("<h2 class='neon-title'>GPS RADAR</h2>", unsafe_allow_html=True)
        # ใส่โค้ด GPS ของคุณที่นี่

    elif st.session_state.current_page == "SENSOR":
        st.markdown("<h2 class='neon-title'>SENSOR LAB</h2>", unsafe_allow_html=True)
        # ใส่โค้ด Sensor ของคุณที่นี่
