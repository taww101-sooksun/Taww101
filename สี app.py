import streamlit as st
import os 
import time
import base64
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from folium.features import DivIcon
from streamlit_folium import st_folium
from math import radians, cos, sin, asin, sqrt
import pytz
from timezonefinder import TimezoneFinder
from datetime import datetime, date, timedelta
import math
import random
import hashlib
import pandas as pd
from streamlit_js_eval import get_geolocation 

# =================================================================
# 1. INITIAL SYSTEM SETUP (ตั้งค่าบนสุดครั้งเดียว)
# =================================================================
st.set_page_config(page_title="SYNAPSE ULTIMATE", layout="wide", initial_sidebar_state="expanded")

# ฟังก์ชันดึงรูปภาพ/เสียง
def get_base64_data(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

# --- ตรวจสอบสถานะสีและหน้าจอ ---
if 'main_color' not in st.session_state: st.session_state.main_color = "#00f3ff"
if 'sub_color' not in st.session_state: st.session_state.sub_color = "#ff00de"
if 'bg_glow' not in st.session_state: st.session_state.bg_glow = "#0015ff"
if 'page' not in st.session_state: st.session_state.page = "HOME"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# =================================================================
# 2. GLOBAL CSS & LOGO (คุมโทนสีทุกห้อง)
# =================================================================
logo_b64 = get_base64_data("logo1.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    :root {{
        --primary: {st.session_state.main_color};
        --secondary: {st.session_state.sub_color};
        --glow: {st.session_state.bg_glow};
    }}

    .stApp {{ 
        background-color: #000; 
        color: #fff; 
        font-family: 'Orbitron', sans-serif;
        border: 2px solid var(--primary);
        transition: all 0.5s ease;
    }}
    
    /* ลบติ่ง Streamlit */
    header, footer, #MainMenu {{visibility: hidden;}}
    .block-container {{ padding-top: 2rem; }}

    /* โลโก้ลอย */
    .global-logo {{
        position: fixed; top: 15px; right: 25px; width: 65px; z-index: 10000;
        filter: drop-shadow(0 0 10px var(--primary));
        animation: pulse 2s infinite alternate;
    }}
    @keyframes pulse {{ from {{ transform: scale(1); }} to {{ transform: scale(1.1); }} }}
    
    /* ปุ่มวิ้งๆ */
    .stButton>button {{
        border-radius: 12px; border: 1px solid var(--primary) !important;
        background: rgba(0,0,0,0.3) !important; color: #fff !important;
        box-shadow: 0 0 5px var(--primary); transition: 0.3s;
    }}
    .stButton>button:hover {{ 
        background: var(--primary) !important; 
        box-shadow: 0 0 20px var(--primary) !important; 
        color: #000 !important; 
    }}

    .neon-text {{
        color: var(--primary) !important;
        text-shadow: 0 0 10px var(--primary), 0 0 20px var(--secondary);
        text-align: center;
    }}
    </style>
    <img src="data:image/png;base64,{logo_b64}" class="global-logo">
""", unsafe_allow_html=True)

# =================================================================
# 3. SIDEBAR CONTROL (เพลงและธีม)
# =================================================================
with st.sidebar:
    st.markdown("<h2 class='neon-text'>AGENT CONTROL</h2>", unsafe_allow_html=True)
    
    # เพลงพื้นหลังเล่นต่อเนื่อง
    all_songs = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
    selected_bg = st.selectbox("🎵 Background Music", ["Off"] + all_songs)
    if selected_bg != "Off":
        bg_data = get_base64_data(selected_bg)
        st.markdown(f'<audio autoplay loop controls style="width:100%; height:32px;"><source src="data:audio/mp3;base64,{bg_data}"></audio>', unsafe_allow_html=True)

    if st.session_state.logged_in:
        st.write(f"📟 Agent: {st.session_state.user}")
        if st.button("LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()

# =================================================================
# 4. LOGIN SYSTEM
# =================================================================
if not st.session_state.logged_in:
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.markdown("<h1 class='neon-text'>IDENTITY CHECK</h1>", unsafe_allow_html=True)
        new_user = st.text_input("AGENT CODE NAME:", placeholder="ENTER NAME").strip()
        if st.button("ACTIVATE SYSTEM", use_container_width=True):
            if new_user:
                st.session_state.user = new_user
                st.session_state.logged_in = True
                st.session_state.page = "HOME"
                st.rerun()
    st.stop()

# =================================================================
# 5. MAIN LOGIC (Lunar Decoder)
# =================================================================
def get_detailed_logic(dt):
    if dt is None: return None
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    if pos <= 14.765:
        m_num = int(pos) + 1
        res = math.sqrt((day_val**2) + (m_num**2))
    else:
        m_num = int(pos - 14.765) + 1
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
    return {"res": round(res, 4), "m_num": m_num, "day_val": day_val}

# =================================================================
# 6. NAVIGATION CONTENT
# =================================================================
if st.session_state.page != "HOME":
    if st.button("⬅️ BACK TO HUB"):
        st.session_state.page = "HOME"; st.rerun()

# --- [ PAGE: HOME HUB ] ---
if st.session_state.page == "HOME":
    st.markdown("<h1 class='neon-text'>SYNAPSE HUB</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🎵 1. DJ STATION", use_container_width=True): st.session_state.page = "1"; st.rerun()
        if st.button("🛰️ 2. RADAR & CHAT", use_container_width=True): st.session_state.page = "2"; st.rerun()
        if st.button("🧬 3. DECODER", use_container_width=True): st.session_state.page = "3"; st.rerun()
        if st.button("🌍 4. WORLD CLOCK", use_container_width=True): st.session_state.page = "4"; st.rerun()
    with c2:
        if st.button("🔮 5. DESTINY TIMELINE", use_container_width=True): st.session_state.page = "5"; st.rerun()
        if st.button("📳 6. SENSOR UNIT", use_container_width=True): st.session_state.page = "6"; st.rerun()
        if st.button("🔢 8. DAILY CODE", use_container_width=True): st.session_state.page = "8"; st.rerun()
        if st.button("🎨 10. COLOR MASTER", use_container_width=True): st.session_state.page = "10"; st.rerun()

# --- [ PAGE 10: COLOR MASTER (หัวใจการเปลี่ยนสี) ] ---
elif st.session_state.page == "10":
    st.markdown("<h2 class='neon-text'>🎨 COLOR MASTER UNIT</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.main_color = st.color_picker("🔵 PRIMARY NEON (สีหลัก)", st.session_state.main_color)
        st.session_state.bg_glow = st.color_picker("✨ GLOW ACCENT (สีเรืองแสง)", st.session_state.bg_glow)
    with col2:
        st.session_state.sub_color = st.color_picker("🔴 SECONDARY NEON (สีรอง)", st.session_state.sub_color)
    
    if st.button("🔥 SYNCHRONIZE COLORS", use_container_width=True):
        st.balloons()
        st.rerun()
    
    st.markdown(f"""
        <div style="border: 2px dashed var(--primary); padding: 20px; text-align: center; border-radius: 15px;">
            <h3 style="color:var(--primary); text-shadow: 0 0 10px var(--glow);">ระบบปรับแต่งสีสำเร็จ</h3>
            <p style="color:var(--secondary);">สีเหล่านี้จะถูกใช้ใน DJ Visualizer, ปุ่ม และแผนที่ทั่วทั้งระบบ</p>
        </div>
    """, unsafe_allow_html=True)

# --- [ PAGE 1: DJ STATION (ปรับให้สีเปลี่ยนตามหน้า 10) ] ---
elif st.session_state.page == "1":
    st.markdown("<h2 class='neon-text'>🎧 DJ STATION V.3</h2>", unsafe_allow_html=True)
    # ใส่โค้ด DJ เดิมของคุณต๊ะตรงนี้ โดยในส่วน JavaScript 
    # ให้เปลี่ยน '#00f3ff' เป็น '{st.session_state.main_color}'
    # และเปลี่ยน '#ff00de' เป็น '{st.session_state.sub_color}'
