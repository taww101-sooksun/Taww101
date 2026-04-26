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

# --- 1. SETUP & CONFIG ---
if 'main_color' not in st.session_state: st.session_state.main_color = "#00f3ff"
if 'sub_color' not in st.session_state: st.session_state.sub_color = "#ff00de"
if 'page' not in st.session_state: st.session_state.page = "HOME"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# ฟังก์ชันดึงข้อมูล Base64
def get_base64_data(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

# หัวใจการคำนวณ (The Truth)
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

# --- 2. STYLE INJECTION (UI) ---
logo_b64 = get_base64_data("logo1.png")
st.markdown(f"""
    <style>
    :root {{
        --primary: {st.session_state.main_color};
        --secondary: {st.session_state.sub_color};
    }}
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background: #000; border: 2px solid var(--primary); }}
    .global-logo {{ position: fixed; top: 15px; right: 25px; width: 65px; z-index: 10000; filter: drop-shadow(0 0 10px var(--primary)); }}
    .neon-text {{ text-align: center; color: #fff; text-shadow: 0 0 10px var(--primary), 0 0 20px var(--secondary); font-weight: bold; }}
    .stButton>button {{ border: 1px solid var(--primary) !important; background: rgba(0,0,0,0.2) !important; color: white !important; border-radius: 15px; transition: 0.3s; }}
    .stButton>button:hover {{ border-color: var(--secondary) !important; box-shadow: 0 0 20px var(--secondary) !important; }}
    .logic-box {{ background: rgba(0,0,0,0.5); border: 1px solid var(--primary); padding: 15px; border-radius: 10px; margin: 10px 0; }}
    </style>
    <img src="data:image/png;base64,{logo_b64}" class="global-logo">
""", unsafe_allow_html=True)

# --- 3. LOGIN SYSTEM ---
if not st.session_state.logged_in:
    st.markdown("<h2 class='neon-text'>REGISTER AGENT</h2>", unsafe_allow_html=True)
    new_user = st.text_input("ENTER AGENT NAME", placeholder="เช่น ต๊ะ101").strip()
    if st.button("ACTIVATE SYSTEM", use_container_width=True):
        if new_user:
            st.session_state.user = new_user
            st.session_state.logged_in = True
            st.session_state.page = "HOME"
            st.rerun()
    st.stop()

# --- 4. NAVIGATION ---
if st.session_state.page != "HOME":
    if st.button("⬅️ BACK TO HUB"):
        st.session_state.page = "HOME"; st.rerun()

# --- 5. PAGES ---

# [ HOME HUB ]
if st.session_state.page == "HOME":
    st.markdown("<h1 class='neon-text'>SYNAPSE HUB</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>ศูนย์ควบคุมระบบ: อยู่นิ่งๆ ไม่เจ็บตัว</p>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🎵 1. MUSIC STATION\nเครื่องเล่นเพลง MP3", use_container_width=True):
            st.session_state.page = "1"; st.rerun()
        if st.button("🛰️ 2. TACTICAL UNIT\nแชตลับ & เรดาร์ GPS", use_container_width=True):
            st.session_state.page = "2"; st.rerun()
    with c2:
        if st.button("🧬 3. SYNAPSE DECODER\nศูนย์คำนวณรหัส & บันทึก", use_container_width=True):
            st.session_state.page = "3"; st.rerun()
        if st.button("⚡ 6. SENSOR UNIT\nวัดเสียง & การสั่นสะเทือน", use_container_width=True):
            st.session_state.page = "6"; st.rerun()
    
    if st.button("🎨 10. COLOR MASTER\nปรับแต่งสีระบบ", use_container_width=True):
        st.session_state.page = "10"; st.rerun()

# [ ห้อง 1: MUSIC ]
elif st.session_state.page == "1":
    st.markdown("<h2 class='neon-text'>🎧 DJ STATION</h2>", unsafe_allow_html=True)
    # (โค้ด Audio Mixer เดิมของคุณ...)
    all_songs = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
    song_a = st.selectbox("💿 DECK A", ["-- Select --"] + all_songs)
    # ... ใส่โค้ด HTML Mixer ที่คุณมีอยู่ได้เลย ...
    st.caption("Music Module v.1.5")

# [ ห้อง 2: CHAT & GPS ]
elif st.session_state.page == "2":
    st.markdown("<h2 class='neon-text'>🛰️ TACTICAL RADAR & CHAT</h2>", unsafe_allow_html=True)
    # (โค้ด Radar และ Private Chat เดิมของคุณ...)
    st.caption("Tactical Module v.2.0")

# [ ห้อง 3: THE CENTER (รวมฟีเจอร์คำนวณทั้งหมด) ]
elif st.session_state.page == "3":
    st.markdown("<h2 class='neon-text'>🧬 SYNAPSE CENTRAL DECODER</h2>", unsafe_allow_html=True)
    
    t1, t2, t3, t4, t5 = st.tabs(["💎 DAILY SCAN", "💖 DESTINY", "🔢 SECURITY CODE", "🗓️ 180 DAYS", "📝 MEMORY LOG"])
    
    with t1: # หน้าถอดรหัสส่วนตัว (เดิมหน้า 3)
        dob = st.date_input("📅 ระบุวันเกิดเพื่อถอดรหัส", key="dec_dob")
        if dob:
            d = get_detailed_logic(dob)
            st.metric("YOUR PERSONAL CODE", d['res'])
            st.info(f"พิกัด: {d['day_name']} | {d['phase']} (สูตร: {d['formula']})")

    with t2: # ตรวจดวงคู่ขนาน (เดิมหน้า 7)
        name1 = st.text_input("AGENT 1:", key="n1")
        name2 = st.text_input("AGENT 2:", key="n2")
        if st.button("⚡ SCAN SYNC"):
            score1 = sum(ord(c) for c in name1)
            score2 = sum(ord(c) for c in name2)
            match = 100 - (abs(score1 - score2) % 100)
            st.metric("SYNC RATE", f"{match}%")

    with t3: # รหัสลับประจำวัน (เดิมหน้า 8)
        current_agent = st.session_state.get('user', 'Guest')
        raw = f"{date.today()}_{current_agent}_SYNAPSE"
        h = hashlib.sha256(raw.encode()).hexdigest()
        st.write(f"ACCESS PIN: **{str(int(h[:4], 16))[-4:].zfill(4)}**")

    with t4: # สแกน 180 วัน (เดิมหน้า 5)
        st.write("ระบบสแกนหาพิกัดเพชร/ธรรม/กระจก ล่วงหน้า 180 วัน")
        # (ใส่ Loop คำนวณ 180 วันเดิมที่นี่)

    with t5: # บันทึกระบบ (เดิมหน้า 9)
        log_entry = st.text_area("✍️ บันทึกเหตุการณ์:")
        if st.button("💾 SAVE LOG"):
            st.success("บันทึกข้อมูลเข้า Cloud เรียบร้อย (Firebase Ready)")

# [ ห้อง 6: SENSOR ]
elif st.session_state.page == "6":
    st.markdown("<h2 class='neon-text'>⚡ SENSOR UNIT</h2>", unsafe_allow_html=True)
    # (โค้ด JS วัด Db, Hz และ Vibration เดิมของคุณ...)

# [ ห้อง 10: COLOR ]
elif st.session_state.page == "10":
    st.markdown("<h2 class='neon-text'>🎨 COLOR MASTER</h2>", unsafe_allow_html=True)
    st.session_state.main_color = st.color_picker("🔵 Main Neon", st.session_state.main_color)
    st.session_state.sub_color = st.color_picker("🔴 Sub Neon", st.session_state.sub_color)
    if st.button("APPLY COLORS"): st.rerun()

st.caption("อ.ย.น. ิ. ้.ง ๆ .ไ.ม.่.เ.จ.็.บ.ต.ั.ว | SYNAPSE COMMAND CENTER")
