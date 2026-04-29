import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import math
from datetime import datetime, date

# --- [ 1. INITIAL SETUP & THEME ] ---
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00ff41"
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

st.set_page_config(page_title="SYNAPSE X", layout="wide")

# CSS แบบจัดเต็ม: ซ่อน Streamlit Elements แต่เหลือทางออกไว้ให้
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    /* ซ่อนของเดิมของ Streamlit */
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stDeployButton {{display:none;}}
    
    /* ปรับแต่งหน้าตาแอป */
    .stApp {{ background-color: #000; color: #ffffff; }}
    
    [data-testid="stSidebar"] {{
        background-color: #050505;
        border-right: 2px solid {st.session_state.theme_color};
        min-width: 250px !important;
    }}
    
    /* ปุ่มพิเศษสำหรับเปิด Sidebar ในมือถือ (เผื่อปุ่มเดิมหาย) */
    .menu-hint {{
        position: fixed;
        top: 10px;
        left: 10px;
        background: {st.session_state.theme_color};
        color: black;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 10px;
        font-weight: bold;
        z-index: 999999;
    }}

    .neon-text {{ 
        color: {st.session_state.theme_color}; 
        text-shadow: 0 0 10px {st.session_state.theme_color}; 
        font-family: 'Orbitron', sans-serif; 
    }}
    </style>
    <div class="menu-hint">SWIPE FROM LEFT TO OPEN MENU</div>
    """, unsafe_allow_html=True)

# --- [ 2. NAVIGATION SIDEBAR ] ---
st.sidebar.markdown(f"<h1 class='neon-text'>SYNAPSE X</h1>", unsafe_allow_html=True)
if st.session_state.user_name:
    st.sidebar.success(f"AGENT: {st.session_state.user_name}")

# ใช้ Radio แบบธรรมดาเพื่อให้กดง่ายในมือถือ
menu = st.sidebar.radio("MAIN NAVIGATION", 
    ["🔐 LOGIN & SETTINGS", "🎧 ROOM 1: NEON MUSIC", "🛰️ ROOM 2: GPS & CHAT", "🧬 ROOM 3: COSMIC DECODER", "🎙️ ROOM 4: SENSOR LAB"])

st.sidebar.divider()
st.sidebar.write(f"Slogan: 'อยู่นิ่งๆ ไม่เจ็บตัว'")

# --- [ 3. LOGIC แต่ละห้อง ] ---

# ตัวอย่างการเช็กหน้าจอ: ถ้าหน้าจอยังว่าง ให้แสดงคำแนะนำ
if menu == "🔐 LOGIN & SETTINGS":
    st.markdown("<h2 class='neon-text'>SETTINGS</h2>", unsafe_allow_html=True)
    u_name = st.text_input("NAME/ID", value=st.session_state.user_name)
    if st.button("CONFIRM AGENT"):
        st.session_state.user_name = u_name
        st.success("AGENT SAVED")
    
    color = st.color_picker("NEON COLOR", st.session_state.theme_color)
    if st.button("SAVE THEME"):
        st.session_state.theme_color = color
        st.rerun()

elif menu == "🎧 ROOM 1: NEON MUSIC":
    st.markdown("<h2 class='neon-text'>MUSIC ROOM</h2>", unsafe_allow_html=True)
    # ใส่โค้ด Mixer เดิมของคุณตรงนี้

elif menu == "🛰️ ROOM 2: GPS & CHAT":
    st.markdown("<h2 class='neon-text'>GPS & CHAT</h2>", unsafe_allow_html=True)
    # ใส่โค้ด GPS เดิมของคุณตรงนี้

elif menu == "🧬 ROOM 3: COSMIC DECODER":
    st.markdown("<h2 class='neon-text'>DECODER</h2>", unsafe_allow_html=True)
    # ส่วนคำนวณ 3 หัวข้อ
    c1, c2, c3 = st.columns(3)
    c1.metric("รหัสฐานวัน", round(date.today().isoweekday() * 1.618, 4))
    c2.metric("รหัสจันทรคติ", "29.53")
    c3.metric("รหัสสมดุล", "ALPHA-01")

elif menu == "🎙️ ROOM 4: SENSOR LAB":
    st.markdown("<h2 class='neon-text'>SENSOR</h2>", unsafe_allow_html=True)
    # ใส่โค้ด Sensor เดิมของคุณตรงนี้

# --- FOOTER ---
st.divider()
st.caption(f"SYNAPSE X | VERSION 7.6 | AGENT: {st.session_state.user_name}")
