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
# 1. SETUP สูงสุด (ต้องอยู่บรรทัดแรก และมีที่เดียวเท่านั้น)
# =================================================================
st.set_page_config(
    page_title="SYNAPSE ULTIMATE", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- ลบติ่ง STREAMLIT แบบขุดรากถอนโคน ---
st.markdown("""
    <style>
    /* ซ่อน Header (แถบใสข้างบน) */
    header[data-testid="stHeader"] {
        visibility: hidden !important;
        height: 0px !important;
    }
    
    /* ซ่อน Footer (Made with Streamlit) */
    footer {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* ซ่อนปุ่ม MainMenu (จุด 3 จุด) */
    #MainMenu {
        visibility: hidden !important;
    }

    /* ซ่อนปุ่ม Deploy และสถานะต่างๆ */
    .stDeployButton {
        display: none !important;
    }
    
    /* ขยับเนื้อหาขึ้นไปให้สุดหน้าจอ */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        max-width: 100% !important;
    }

    /* ซ่อนแถบสถานะการโหลดรันโค้ดข้างบน */
    div[data-testid="stStatusWidget"] {
        visibility: hidden !important;
    }
    </style>
""", unsafe_allow_html=True)

# =================================================================
# 2. ฟังก์ชันดึงข้อมูล (Base64)
# =================================================================
def get_base64_data(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

# =================================================================
# 3. INITIAL STATE (เช็คค่าสีและหน้าจอ)
# =================================================================
if 'main_color' not in st.session_state: st.session_state.main_color = "#00f3ff"
if 'sub_color' not in st.session_state: st.session_state.sub_color = "#ff00de"
if 'bg_glow' not in st.session_state: st.session_state.bg_glow = "#0015ff"
if 'page' not in st.session_state: st.session_state.page = "HOME"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# =================================================================
# 4. GLOBAL THEME CSS (เปลี่ยนตามสีที่คุณต๊ะเลือก)
# =================================================================
logo_b64 = get_base64_data("logo1.png")

st.markdown(f"""
    <style>
    :root {{
        --primary: {st.session_state.main_color};
        --secondary: {st.session_state.sub_color};
    }}
    .stApp {{ 
        background-color: #000; 
        color: #fff; 
        border: 2px solid var(--primary);
    }}
    .global-logo {{
        position: fixed; top: 10px; right: 20px; width: 60px; z-index: 10000;
        filter: drop-shadow(0 0 8px var(--primary));
    }}
    </style>
    <img src="data:image/png;base64,{logo_b64}" class="global-logo">
""", unsafe_allow_html=True)
