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
import math
from math import radians, cos, sin, asin, sqrt
import pytz
from timezonefinder import TimezoneFinder
from datetime import datetime, date, timedelta
import random
import pandas as pd
import json
from streamlit_js_eval import get_geolocation 

# ==============================================================================
# 🎨 SECTION 1: GLOBAL STYLING & DESIGN ENGINE
# ==============================================================================

def apply_global_styles():
    """
    ระบบควบคุม Visual Identity ของ SYNAPSE OS
    เน้นขอบหนา ไฟฟุ้ง และความเป็น Matrix Neon
    """
    theme = st.session_state.get('theme_color', "#1408BF")
    secondary = "#00FF41" # Matrix Green
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

        /* ปรับแต่งโครงสร้างพื้นฐาน */
        .stApp {{
            background-color: #000000 !important;
            color: white !important;
            font-family: 'JetBrains Mono', monospace !important;
        }}

        /* ซ่อนส่วนเกินที่ไม่จำเป็น */
        header, footer, .stAppToolbar {{ visibility: hidden !important; }}
        .block-container {{ padding: 2rem 5rem !important; }}

        /* ระบบ TABS - ขอบหนาพิเศษและไฟเรืองแสง */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(5, 5, 5, 0.9) !important;
            border-radius: 30px !important;
            padding: 15px !important;
            border: 8px solid {theme} !important;
            box-shadow: 0 0 50px {theme}66, inset 0 0 20px {theme}33;
            margin: 20px 0px 40px 0px !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            color: #AAAAAA !important;
            font-size: 1.1em !important;
            font-weight: 700 !important;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            padding: 10px 25px !important;
        }}
        .stTabs [aria-selected="true"] {{
            color: white !important;
            background-color: {theme}33 !important;
            border-radius: 15px;
            text-shadow: 0 0 15px white;
            transform: translateY(-2px);
        }}

        /* ปุ่มกด - NEON TRIGGER PRO */
        div.stButton > button {{
            background: linear-gradient(135deg, #000000 0%, #111111 100%) !important;
            color: {theme} !important;
            border: 6px solid {theme} !important;
            border-radius: 25px !important;
            font-weight: 900 !important;
            letter-spacing: 3px !important;
            text-transform: uppercase !important;
            padding: 20px !important;
            box-shadow: 0 0 20px {theme}44;
            transition: 0.3s all ease-in-out;
            margin-top: 10px;
        }}
        div.stButton > button:hover {{
            background: {theme} !important;
            color: white !important;
            box-shadow: 0 0 40px {theme};
            transform: scale(1.03) translateY(-3px);
        }}

        /* LOGIC BOX - ขอบหนาสีเขียว Matrix */
        .logic-box {{
            background: rgba(0, 15, 0, 0.92);
            border: 6px solid {secondary} !important;
            border-radius: 25px;
            padding: 35px;
            box-shadow: 0 0 35px rgba(0, 255, 65, 0.4);
            margin-bottom: 30px;
            position: relative;
            overflow: hidden;
        }}
        .logic-box::after {{
            content: "SECURE DATA";
            position: absolute;
            top: 10px; right: 20px;
            font-size: 0.6em; color: {secondary};
            opacity: 0.5; letter-spacing: 2px;
        }}

        /* ปรับแต่ง INPUT / DATE INPUT */
        .stDateInput input, .stTextInput input {{
            background-color: #000 !important;
            color: {secondary} !important;
            border: 2px solid {secondary}55 !important;
            border-radius: 10px !important;
        }}

        /* Scrollbar Style */
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: #000; }}
        ::-webkit-scrollbar-thumb {{ background: {theme}; border-radius: 10px; }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# ⚙️ SECTION 2: SYSTEM KERNEL & INITIALIZATION
# ==============================================================================

def init_synapse_core():
    """ตั้งค่าตัวแปรระบบเริ่มต้น (Session States)"""
    if 'system_ready' not in st.session_state: st.session_state.system_ready = True
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#1408BF"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user' not in st.session_state: st.session_state.user = "GUEST"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'logs' not in st.session_state: st.session_state.logs = []
    
    # เชื่อมต่อ Database
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
            add_system_log("DATABASE CONNECTION: ESTABLISHED")
        except Exception as e:
            st.error(f"FATAL ERROR: FIREBASE FAIL -> {e}")

def add_system_log(msg):
    """ฟังก์ชันบันทึกกิจกรรมเข้าระบบ"""
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{ts}] {msg}")
    if len(st.session_state.logs) > 50: st.session_state.logs.pop(0)

# ==============================================================================
# 🧠 SECTION 3: CORE CALCULATIONS (REALITY & GEODESY)
# ==============================================================================

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """คำนวณระยะห่างระหว่างจุด 2 จุดบนผิวโลก"""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon, dlat = lon2 - lon1, lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return c * 6371 # กิโลเมตร

def get_reality_fingerprint(target_date):
    """
    สูตรคำนวณรหัสคลื่นความถี่ (Reality Code)
    ขยายความซับซ้อนเพื่อให้ข้อมูลมีความลึกขึ้น
    """
    anchor = date(1900, 1, 1)
    delta = (target_date - anchor).days
    lunar_cycle = 29.530588853
    position = (delta - 0.5) % lunar_cycle
    day_idx = target_date.weekday() + 1 # 1=Mon...7=Sun
    
    # Advanced Reality Formula
    if position <= 14.765:
        age = int(position) + 1
        code = math.sqrt((day_idx ** 2.5) + (age ** 2.2)) / 1.618
        status = f"ข้างขึ้น {age} ค่ำ (Waxing)"
    else:
        age = int(position - 14.765) + 1
        code = (day_idx * 3.14159) / (age if age != 0 else 1)
        status = f"ข้างแรม {age} ค่ำ (Waning)"
        
    return {
        "code": round(code, 4),
        "status": status,
        "lunar_pos": round(position, 2),
        "entropy": round(math.sin
