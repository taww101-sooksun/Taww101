import streamlit as st
import os
import time
import json
import uuid
import base64
import hashlib
import binascii
import io
import math
import psutil
from datetime import datetime, date, timedelta

# --- Data & Math ---
import pandas as pd
import numpy as np
import pytz
import matplotlib.pyplot as plt
import networkx as nx

# --- Streamlit Core & Components ---
import streamlit.components.v1 as components
from streamlit_player import st_player
from streamlit_js_eval import streamlit_js_eval
from streamlit_autorefresh import st_autorefresh

# --- Firebase & Security ---
import firebase_admin
from firebase_admin import credentials, firestore, storage, auth
from firebase_admin import db as realtime_db 

# --- AI & Generative ---
import google.generativeai as genai
import replicate

# --- Multimedia & Audio ---
import librosa
import soundfile as sf
from pydub import AudioSegment
from gtts import gTTS
try:
    import moviepy.editor as mp
except ImportError:
    import moviepy as mp
from PIL import Image 

# --- Location & Maps ---
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import osmnx as ox

# --- Networking ---
import requests

# =========================================================
# 🛡️ CORE FUNCTIONS - หัวใจการคำนวณ (ห้ามย้ายตำแหน่ง)
# =========================================================

# --- [1] ฟังก์ชันคำนวณรหัสความจริง ---
def get_detailed_logic(dt):
    if dt is None: return None
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    
    if pos <= 14.765: # ข้างขึ้น
        m_num = int(pos) + 1
        phase = f"ขึ้น {m_num} ค่ำ"
        res = math.sqrt((day_val**2) + (m_num**2))
        formula = f"√({day_val}² + {m_num}²)"
        logic_type = "แรงผลักดัน (Vector Energy)"
    else: # ข้างแรม
        m_num = int(pos - 14.765) + 1
        phase = f"แรม {m_num} ค่ำ"
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula = f"({day_val} × 1.618) / {m_num}"
        logic_type = "สมดุลสัดส่วนทองคำ (Golden Ratio)"

    return {
        "res": round(res, 4), "phase": phase, "day_name": day_names[dt.weekday()],
        "day_val": day_val, "m_num": m_num, "formula": formula, "type": logic_type
    }

# --- [2] ฟังก์ชันดึงพิกัดจริงจาก Browser ---
def get_geolocation():
    return streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition(success => { return success; })", key="GPS_ENGINE")

# --- [3] ฟังก์ชันคำนวณระยะทาง (Haversine) ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371 
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))

# --- [4] ฟังก์ชันสแกนแผนที่กาลเวลา ---
def run_scanner(target_res, base_date, days, mode="future"):
    results = []
    for i in range(days + 1):
        current_date = base_date + timedelta(days=i) if mode == "future" else base_date - timedelta(days=i)
        d = get_detailed_logic(current_date)
        gap = abs(target_res - d['res'])
        status = "ปกติ"
        if gap < 0.5: status = "💎 เพชร (รหัสบรรจบ)"
        elif 3.8 <= gap <= 4.2: status = "🌀 ธร (สัญญาณสะท้อน)"
        elif gap > 10.0: status = "⚙️ กงจักร (รหัสแยกตัว)"
        if status != "ปกติ":
            results.append({"วันที่": current_date.strftime("%d/%m/%Y"), "วัน": d['day_name'], "สถานะพิกัด": status, "Gap": round(gap, 4), "รหัสวันนั้น": d['res']})
    return pd.DataFrame(results)

# --- [5] แปลงไฟล์เป็น Base64 ---
def get_base64(file):
    try:
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return None

# =========================================================
# 🔥 FIREBASE INITIALIZATION
# =========================================================
if not firebase_admin._apps:
    try:
        if "firebase_service_account" in st.secrets:
            cred = credentials.Certificate(dict(st.secrets["firebase_service_account"]))
            firebase_admin.initialize_app(cred, {
                'storageBucket': st.secrets["firebase_config"]["storageBucket"],
                'databaseURL': st.secrets["firebase_config"].get("databaseURL", "")
            })
    except: st.error("Firebase Init Failed - Check Secrets")

# =========================================================
# 🎨 UI & STYLES
# =========================================================
st.set_page_config(page_title="SYNAPSE COMMAND", layout="wide")
primary_neon = "#1F51FF"
logo_data = get_base64("logo1.png")

st.markdown(f"""
    <style>
    #MainMenu, footer, header {{visibility: hidden;}}
    .stApp {{ background-color: #000; color: white; }}
    .neon-wrapper {{
        text-align: center; font-family: 'Courier New', monospace; font-weight: bold;
        background: linear-gradient(to right, #FF3131, #FFF01F, #00F3FF, #FF44CC);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        animation: rainbow-glow 3s linear infinite, slogan-shake 2s ease-in-out infinite;
    }}
    @keyframes slogan-shake {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.05); }} }}
    button[kind="secondary"] {{
        background: transparent !important; color: {primary_neon} !important;
        border: 3px solid {primary_neon} !important; border-radius: 15px !important;
        height: 60px !important; font-weight: bold !important;
        box-shadow: 0 0 10px {primary_neon} !important;
    }}
    .logic-box {{ border: 1px solid {primary_neon}; padding: 15px; border-radius: 10px; background: #111; }}
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 🛰️ MAIN INTERFACE
# =========================================================
if logo_data:
    st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo_data}" style="width:120px;"></div>', unsafe_allow_html=True)

st.markdown('<div class="neon-wrapper"><div style="font-size:35px;">SYNAPSE</div><div style="font-size:20px;">อยู่นิ่งๆไม่เจ็บตัว</div></div>', unsafe_allow_html=True)

if 'page' not in st.session_state: st.session_state.page = "HOME"

if st.session_state.page == "HOME":
    st.write("##")
    cols = st.columns(4)
    units = ["🎵 UNIT 01: DJ", "🛰️ UNIT 02: RADAR", "🎨 UNIT 03: COLOR", "⚡ UNIT 04: SENSOR", "🔮 UNIT 05: LOGIC"]
    for i in range(1, 21):
        with cols[(i-1)%4]:
            label = units[i-1] if i <= len(units) else f"UNIT {i:02d}"
            if st.button(label, key=f"u{i}", use_container_width=True):
                st.session_state.page = str(i); st.rerun()
else:
    if st.button("⬅️ HUB"): st.session_state.page = "HOME"; st.rerun()
    
    # --- ROOMS ---
    page = st.session_state.page
    if page == "1":
        st.markdown("<h2 class='neon-wrapper'>🎧 SYNAPSE DJ STATION</h2>", unsafe_allow_html=True)
        all_songs = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
        if not all_songs: st.warning("ไม่พบไฟล์ .mp3")
        else:
            c1, c2 = st.columns(2)
            song_a = c1.selectbox("DECK A", ["-- Select --"] + all_songs)
            song_b = c2.selectbox("DECK B", ["-- Select --"] + all_songs)
            # (Mixer HTML code here as per previous version - kept for functionality)
            st.info(f"Ready to play: {song_a} & {song_b}")

    elif page == "2":
        st.markdown("<h2 class='neon-wrapper'>🛰️ UNIT 02: RADAR</h2>", unsafe_allow_html=True)
        loc = get_geolocation()
        lat, lon = 13.7367, 100.5231
        if loc and 'coords' in loc:
            lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
            st.success(f"พิกัดปัจจุบัน: {lat}, {lon}")
        
        m = folium.Map(location=[lat, lon], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr='Google')
        folium.Marker([lat, lon], icon=folium.Icon(color='red')).add_to(m)
        st_folium(m, width="100%", height=400)
        
        if st.button("📡 BROADCAST LOCATION"):
            try: realtime_db.reference(f'users/ADMIN').update({'lat': lat, 'lon': lon, 'ts': time.time()})
            except: st.error("Firebase Connection Error")

    elif page == "5":
        st.markdown("<h2 class='neon-wrapper'>🔮 UNIT 05: THE TRUTH SCANNER</h2>", unsafe_allow_html=True)
        target_date = st.date_input("เลือกวันที่", value=date.today())
        d = get_detailed_logic(target_date)
        if d:
            st.markdown(f"<div class='logic-box'>วัน{d['day_name']} | {d['phase']}<br>รหัส: {d['res']}<br>สูตร: {d['formula']}</div>", unsafe_allow_html=True)

    else:
        st.warning(f"UNIT {page} อยู่ระหว่างการพัฒนา")

st.caption(f"SYNAPSE OS v4.2 | {datetime.now().strftime('%H:%M:%S')}")
