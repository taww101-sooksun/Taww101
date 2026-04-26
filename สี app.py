# =========================================================
# 🛡️ SYNAPSE COMMAND CENTER - FULL POWER IMPORTS
# =========================================================

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

# --- 1. FIREBASE INITIALIZATION ---
if not firebase_admin._apps:
    try:
        cred_info = dict(st.secrets["firebase_service_account"])
        cred = credentials.Certificate(cred_info)
        firebase_admin.initialize_app(cred, {
            'storageBucket': st.secrets["firebase_config"]["storageBucket"],
            'databaseURL': st.secrets["firebase_config"].get("databaseURL", "")
        })
    except: pass
# --- [1] ฟังก์ชันคำนวณรหัสความจริง (หัวใจหลัก) ---
def get_detailed_logic(dt):
    if dt is None: return None
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
# --- [3] ฟังก์ชันดึงพิกัดจริงจาก Browser ---
def get_geolocation():
    # เรียกใช้ streamlit_js_eval ที่พี่ import ไว้แล้ว
    return streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition(success => { return success; })", key="GPS_ENGINE")

# --- [4] ฟังก์ชันคำนวณระยะทางระหว่างจุด (Haversine Formula) ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # รัศมีโลก (กม.)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

    
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

# --- [2] ฟังก์ชันสแกนแผนที่กาลเวลา (อดีต/อนาคต) ---
def run_scanner(target_res, base_date, days, mode="future"):
    results = []
    for i in range(days + 1):
        current_date = base_date + timedelta(days=i) if mode == "future" else base_date - timedelta(days=i)
        d = get_detailed_logic(current_date)
        gap = abs(target_res - d['res'])
        
        # จัดลำดับความสำคัญตามที่ลูกพี่สั่ง
        status = "ปกติ"
        if gap < 0.5: status = "💎 เพชร (รหัสบรรจบ)"
        elif 3.8 <= gap <= 4.2: status = "🌀 ธร (สัญญาณสะท้อน)"
        elif gap > 10.0: status = "⚙️ กงจักร (รหัสแยกตัว)"
        
        if status != "ปกติ":
            results.append({
                "วันที่": current_date.strftime("%d/%m/%Y"),
                "วัน": d['day_name'],
                "สถานะพิกัด": status,
                "Gap": round(gap, 4),
                "รหัสวันนั้น": d['res']
            })
    return pd.DataFrame(results)

# --- 2. CONFIG & THEME ---
st.set_page_config(page_title="SYNAPSE COMMAND", layout="wide")
primary_neon = "#1F51FF"  # สีทองที่ลูกพี่ชอบ

# ฟังก์ชันแปลงรูปโลโก้
def get_base64(file):
    try:
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return None

logo_data = get_base64("logo1.png")

# --- 3. CUSTOM CSS (หนา 2px + โยกสะบัด) ---
st.markdown(f"""
    <style>
    #MainMenu, footer, header {{visibility: hidden;}}
    .stApp {{ background-color: #000; }}

    /* โลโก้เต้น */
    .logo-container {{
        display: flex; justify-content: center;
        animation: logo-dance 3s ease-in-out infinite;
        margin-bottom: 10px;
    }}
    @keyframes logo-dance {{
        0%, 100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-5px); }}
    }}

    /* สโลแกนนีออนโยกสะบัด */
    .neon-wrapper {{
        text-align: center;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        background: linear-gradient(to right, #FF3131, #FFF01F, #00F3FF, #FF44CC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: rainbow-glow 3s linear infinite, slogan-shake 2s ease-in-out infinite;
    }}
    @keyframes slogan-shake {{
        0%, 100% {{ transform: scale(1) rotate(0); }}
        50% {{ transform: scale(1.1) rotate(2deg); }}
    }}
    @keyframes rainbow-glow {{
        0% {{ filter: hue-rotate(0deg) drop-shadow(0 0 10px {primary_neon}); }}
        100% {{ filter: hue-rotate(360deg) drop-shadow(0 0 10px {primary_neon}); }}
    }}

    /* ปุ่ม UNIT หนา 2px สีทอง */
    button[kind="secondary"] {{
        background-color: transparent !important;
        color: {primary_neon} !important;
        border: 4px solid {primary_neon} !important;
        border-radius: 15px !important;
        height: 70px !important;
        font-weight: bold !important;
        box-shadow: 0 0 15px {primary_neon}, inset 0 0 10px {primary_neon} !important;
        transition: 0.3s;
    }}
    button[kind="secondary"]:hover {{
        background-color: {primary_neon} !important;
        color: #000 !important;
        box-shadow: 0 0 30px {primary_neon} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 4. HEADER ---
if logo_data:
    st.markdown(f'''
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_data}" style="width:150px; filter: drop-shadow(0 0 20px {primary_neon});">
        </div>''', unsafe_allow_html=True)

st.markdown(f'''
    <div class="neon-wrapper">
        <div style="font-size:30px; letter-spacing:4px;">SYNAPSE</div>
        <div style="font-size:30px; letter-spacing:6px;">อยู่นิ่งๆไม่เจ็บตัว</div>
    </div>''', unsafe_allow_html=True)

# --- 5. NAVIGATION HUB (11 UNITS SYSTEM) ---
if 'page' not in st.session_state: st.session_state.page = "HOME"

if st.session_state.page == "HOME":
    st.write("##")
    # สร้างปุ่ม 11 ปุ่ม (จัดวางแบบ 3 หรือ 4 คอลัมน์ให้สมดุล)
    cols = st.columns(3) 
    
    # กำหนดชื่อและไอคอนทั้ง 11 UNIT
    unit_names = {
        1: "🎵 01: DJ STATION",
        2: "🛰️ 02: TACTICAL RADAR",
        3: "🔮 03: TRUTH LOGIC",
        4: "⚡ 04: SENSOR SCAN",
        5: "🎨 05: UI DESIGNER",
        6: "💬 06: COMMS CENTER",
        7: "🛠️ 07: DIY MASTER",
        8: "🧬 08: SYNAPSE CORE",
        9: "📹 09: MEDIA STUDIO",
        10: "💾 10: FIREBASE DB",
        11: "🏴 11: COMMAND POST"
    }

    for i in range(1, 12):
        with cols[(i-1)%3]:
            btn_label = unit_names.get(i, f"UNIT {i:02d}")
            if st.button(btn_label, key=f"u{i}", use_container_width=True):
                st.session_state.page = str(i)
                st.rerun()
else:
    # --- [ปุ่มกลับหน้าหลัก] แถบควบคุมด้านบนในทุกห้อง ---
    c_back, c_title = st.columns([1, 4])
    with c_back:
        if st.button("⬅️ HUB", use_container_width=True):
            st.session_state.page = "HOME"
            st.rerun()
    

    # =========================================================
    # 📥 โซนจัดการห้องรบ (เพิ่มเติมต่อจากเดิม)
    # =========================================================
    
    elif st.session_state.page == "2":
        st.markdown("<h2 class='neon-wrapper'>🛰️ UNIT 02: TACTICAL RADAR</h2>", unsafe_allow_html=True)
        
        # ส่วนแสดงพิกัดจริง
        col_gps, col_dist = st.columns([2, 1])
        with col_gps:
            st.write("### 📍 Live Coordinates")
            # ดึงข้อมูลจากคำสั่งที่พี่เขียนไว้ (streamlit_js_eval)
            loc = get_geolocation()
            if loc:
                lat = loc['coords']['latitude']
                lon = loc['coords']['longitude']
                st.success(f"พบพิกัดปัจจุบัน: {lat}, {lon}")
                
                # สร้างแผนที่จริงด้วย Folium
                m = folium.Map(location=[lat, lon], zoom_start=15, tiles="CartoDB dark_matter")
                folium.Marker([lat, lon], popup="CURRENT AGENT", icon=folium.Icon(color='red', icon='info-sign')).add_to(m)
                st_folium(m, width=700, height=400)
            else:
                st.warning("📡 กำลังรอสัญญาณ GPS... (กรุณากด Allow Location ใน Browser)")

        with col_dist:
            st.write("### 📏 Proximity Check")
            target_lat = st.number_input("Target Lat", value=13.7563) # Default BKK
            target_lon = st.number_input("Target Lon", value=100.5018)
            
            if loc:
                dist = haversine(lat, lon, target_lat, target_lon)
                st.metric("ระยะห่างจากเป้าหมาย", f"{dist:.2f} KM")
                if dist < 1.0: st.error("🚨 ALERT: NEAR TARGET!")
            else:
                st.info("ระบุพิกัดเป้าหมายเพื่อคำนวณระยะทางจริง")

    elif st.session_state.page == "3":
        st.markdown("<h2 class='neon-wrapper'>🔮 UNIT 03: TRUTH LOGIC</h2>", unsafe_allow_html=True)
        
        c1, c2 = st.columns([1, 2])
        with c1:
            target_date = st.date_input("เลือกวันที่ตรวจสอบ", date.today())
            scan_days = st.slider("ขอบเขตการสแกน (วัน)", 7, 90, 30)
            
            logic = get_detailed_logic(target_date)
            st.write("---")
            st.subheader(f"รหัสวันนี้: {logic['res']}")
            st.code(f"สูตร: {logic['formula']}\nประเภท: {logic['type']}\nข้างขึ้น/แรม: {logic['phase']}")
        
        with c2:
            st.write("### 📊 วิเคราะห์แนวโน้มรหัสบรรจบ")
            scan_data = run_scanner(logic['res'], target_date, scan_days)
            
            if not scan_data.empty:
                # แสดงกราฟความผันผวนของรหัส
                fig, ax = plt.subplots(figsize=(10, 4))
                plt.style.use('dark_background')
                ax.plot(scan_data['วันที่'], scan_data['รหัสวันนั้น'], color=primary_neon, marker='o', markersize=4)
                ax.set_title("Truth Code Fluctuations", color=primary_neon)
                plt.xticks(rotation=45)
                st.pyplot(fig)
                
                st.dataframe(scan_data, use_container_width=True)
            else:
                st.success("✅ ไม่พบรหัสผิดปกติในระยะที่กำหนด (สถานะ: อยู่นิ่งๆ ไม่เจ็บตัว)")

