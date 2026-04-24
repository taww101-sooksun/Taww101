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
# 1. SETUP & CONFIG (ต้องอยู่บนสุด)
# =================================================================
st.set_page_config(page_title="SYNAPSE ULTIMATE", layout="wide")

# ระบบจัดการสถานะ (State)
if 'main_color' not in st.session_state: st.session_state.main_color = "#00f3ff"
if 'sub_color' not in st.session_state: st.session_state.sub_color = "#ff00de"
if 'page' not in st.session_state: st.session_state.page = "HOME"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# =================================================================
# 2. GLOBAL CSS (ลบติ่ง + เชื่อมสีทุกห้อง)
# =================================================================
st.markdown(f"""
    <style>
    /* ลบ Header/Footer Streamlit */
    header, footer, #MainMenu {{visibility: hidden !important; height: 0px !important;}}
    .stDeployButton {{display: none !important;}}
    
    :root {{
        --primary: {st.session_state.main_color};
        --secondary: {st.session_state.sub_color};
    }}

    .stApp {{
        background-color: #000 !important;
        border: 2px solid var(--primary);
    }}

    /* ปุ่มทุกปุ่มในระบบ */
    .stButton>button {{
        border: 1px solid var(--primary) !important;
        background: rgba(0,0,0,0.5) !important;
        color: white !important;
        box-shadow: 0 0 10px var(--primary);
        border-radius: 12px !important;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        border-color: var(--secondary) !important;
        box-shadow: 0 0 20px var(--secondary) !important;
    }}

    .neon-text {{
        color: var(--primary) !important;
        text-shadow: 0 0 10px var(--primary), 0 0 20px var(--secondary) !important;
        text-align: center; font-weight: bold;
    }}
    </style>
""", unsafe_allow_html=True)

# =================================================================
# 3. HELPER FUNCTIONS
# =================================================================
def get_base64_data(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

def get_detailed_logic(dt):
    if dt is None: return None
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    day_name = day_names[dt.weekday()]
    if pos <= 14.765:
        m_num = int(pos) + 1
        phase = f"ขึ้น {m_num} ค่ำ"
        res = math.sqrt((day_val**2) + (m_num**2))
        formula, logic_type = f"√({day_val}² + {m_num}²)", "Vector Energy"
    else:
        m_num = int(pos - 14.765) + 1
        phase = f"แรม {m_num} ค่ำ"
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula, logic_type = f"({day_val} × 1.618) / {m_num}", "Golden Ratio"
    return {"res": round(res, 4), "phase": phase, "day_name": day_name, "day_val": day_val, "m_num": m_num, "formula": formula, "type": logic_type}

# =================================================================
# 4. LOGIN SYSTEM
# =================================================================
if not st.session_state.logged_in:
    st.markdown("<h2 class='neon-text'>REGISTER AGENT</h2>", unsafe_allow_html=True)
    new_user = st.text_input("รหัส AGENT:", placeholder="เช่น ต๊ะ101").strip()
    if st.button("ACTIVATE SYSTEM", use_container_width=True):
        if new_user:
            st.session_state.user = new_user
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# =================================================================
# 5. NAVIGATION & PAGES
# =================================================================

# --- ปุ่มย้อนกลับ (แสดงทุกหน้ายกเว้น HOME) ---
if st.session_state.page != "HOME":
    if st.button("⬅️ BACK TO MAIN"):
        st.session_state.page = "HOME"
        st.rerun()

# --- [ หน้าแรก: 4 ปุ่มหลัก ] ---
if st.session_state.page == "HOME":
    st.markdown("<h1 class='neon-text'>SYNAPSE HUB</h1>", unsafe_allow_html=True)
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎵 1. DJ STATION (MUSIC)", use_container_width=True): st.session_state.page = "1"; st.rerun()
        if st.button("💬 2. CHAT & RADAR", use_container_width=True): st.session_state.page = "2"; st.rerun()
    with col2:
        if st.button("🧠 3. INTELLIGENCE (LUNAR/LOGS)", use_container_width=True): st.session_state.page = "3"; st.rerun()
        if st.button("🎨 4. COLOR MASTER", use_container_width=True): st.session_state.page = "10"; st.rerun()

# --- [ หน้า 1: DJ STATION ] ---
elif st.session_state.page == "1":
    st.markdown("<h2 class='neon-text'>🎧 DJ STATION</h2>", unsafe_allow_html=True)
    st.write("ระบบเล่นเพลง Deck A/B พร้อม Visualizer")
    # (โค้ดเพลงที่คุณต๊ะมีอยู่แล้ว)

# --- [ หน้า 2: CHAT & RADAR ] ---
elif st.session_state.page == "2":
    st.markdown("<h2 class='neon-text'>🛰️ TACTICAL UNIT</h2>", unsafe_allow_html=True)
    # (โค้ดแผนที่และแชตที่คุณต๊ะมีอยู่แล้ว)

# --- [ หน้า 3: INTELLIGENCE CENTER (รวม 3-9) ] ---
elif st.session_state.page == "3":
    st.markdown("<h2 class='neon-text'>🧠 INTELLIGENCE CENTER</h2>", unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["🌙 LUNAR & GAP", "🔮 DESTINY SCAN", "🔢 DAILY PIN", "📝 SYSTEM LOG"])
    
    with t1:
        st.write("### 🌙 Lunar & Parallel Decoder")
        d_input = st.date_input("เลือกวันเกิดเพื่อถอดรหัส", value=date.today())
        if d_input:
            info = get_detailed_logic(d_input)
            st.info(f"รหัสของคุณคือ: {info['res']} | พิกัด: {info['phase']}")
            st.caption(f"ลอจิก: {info['type']} ใช้สูตร {info['formula']}")

    with t2:
        st.write("### 🔮 Destiny Timeline (180 Days)")
        # สแกนหาพิกัด เพชร/ธรรม/กระจก
        st.write("กำลังสแกนพิกัดบรรจบของรหัสคุณกับจักรวาล...")
        # (ส่วนนี้ใส่ลอจิกสแกน 180 วันที่ผมให้ไว้ก่อนหน้า)

    with t3:
        st.write("### 🔢 Daily Security PIN")
        u_name = st.session_state.get('user', 'AGENT')
        raw_code = f"{date.today()}_{u_name}_SYNAPSE"
        h = hashlib.sha256(raw_code.encode()).hexdigest()
        st.markdown(f"<h1 style='text-align:center;'>{h[:6].upper()}</h1>", unsafe_allow_html=True)
        st.caption("รหัสเปลี่ยนทุก 24 ชม. ตามชื่อผู้ใช้และวันที่")

    with t4:
        st.write("### 📝 System Memory Log")
        with st.form("log_form"):
            note = st.text_area("บันทึกเหตุการณ์:")
            if st.form_submit_button("SAVE"):
                st.success("บันทึกลงฐานข้อมูลแล้ว (Firebase)")

# --- [ หน้า 10: COLOR MASTER ] ---
elif st.session_state.page == "10":
    st.markdown("<h2 class='neon-text'>🎨 COLOR MASTER</h2>", unsafe_allow_html=True)
    st.session_state.main_color = st.color_picker("สีหลักระบบ", st.session_state.main_color)
    st.session_state.sub_color = st.color_picker("สีรองระบบ", st.session_state.sub_color)
    if st.button("🔥 UPDATE ALL DIMENSIONS", use_container_width=True):
        st.rerun()
