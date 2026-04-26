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

# --- ปรับแต่ง UI & Animation ---
st.set_page_config(page_title="SYNAPSE", layout="wide")

# >>> [จุดปรับขนาดตัวหนังสือ] <<< 
synapse_size = "30px"  # ขนาดคำว่า SYNAPSE
motto_size = "30px"     # ขนาดคำว่า อยู่นิ่งๆไม่เจ็บตัว
slogan_glow_speed = "2s" # ความเร็วการวิ่งของสี

st.markdown(f"""
    <style>
    /* ลบส่วนเกิน Streamlit */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header {{ visibility: hidden; }}
    .stApp {{ background-color: #000000; }}

    /* โลโก้เต้น */
    .logo-container {{
        display: flex;
        justify-content: center;
        animation: logo-dance 2s ease-in-out infinite;
    }}
    @keyframes logo-dance {{
        0% {{ transform: translateY(0px) rotate(0deg); }}
        50% {{ transform: translateY(-15px) rotate(2deg); }}
        100% {{ transform: translateY(0px) rotate(0deg); }}
    }}

    /* สโลแกน 7 สีสะท้อนแสง */
    .neon-wrapper {{
        text-align: center;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
        background: linear-gradient(to right, #FF3131, #FF5E33, #FFF01F, #0FFF50, #00F3FF, #1F51FF, #FF44CC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: rainbow-glow {slogan_glow_speed} linear infinite;
        line-height: 1.1;
        margin-bottom: 40px;
    }}

    .synapse-title {{
        font-size: {synapse_size};
        letter-spacing: 15px;
        display: block;
    }}

    .motto-text {{
        font-size: {motto_size};
        letter-spacing: 5px;
        display: block;
    }}

    @keyframes rainbow-glow {{
        0% {{ filter: hue-rotate(0deg) drop-shadow(0 0 10px #00F3FF); }}
        100% {{ filter: hue-rotate(360deg) drop-shadow(0 0 10px #00F3FF); }}
    }}

    /* ปุ่มย้อนกลับ */
    .stButton > button[key="back_home"] {{
        border: 3px solid #FF3131 !important;
        color: #FF3131 !important;
        background-color: transparent !important;
        border-radius: 50px !important;
        font-weight: bold !important;
        box-shadow: 0 0 15px #FF3131;
    }}
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 🏠 ZONE: HEADER (LOGO DANCE + SLOGAN)
# =========================================================

# ส่วนหัว: โลโก้เรืองแสง + เต้น + สโลแกน
st.markdown(f"""
    <div class="logo-container">
        <div class="neon-wrapper">
            <img src="data:image/png;base64,{base64.b64encode(open('logo1.png', 'rb').read()).decode()}" 
                 style="width:180px; filter: drop-shadow(0 0 20px {primary_neon});">
            
            <span class="synapse-title" style="font-size: 80px;">SYNAPSE</span>
            <span class="motto-text" style="font-size: 40px;">อยู่นิ่งๆ ไม่เจ็บตัว</span>
        </div>
    </div>
""", unsafe_allow_html=True)


# =========================================================
# 📟 ZONE: NAVIGATION SYSTEM
# =========================================================

if 'page' not in st.session_state: st.session_state.page = "HOME"

if st.session_state.page == "HOME":
    # 1. รหัสสีทองนีออน
    gold_neon = "#FF0738" 
    
    # 2. CSS แบบล็อคเป้า (ใช้แบคสแลชคลุมปีกกาเพื่อกัน Python Error)
    st.markdown(f"""
        <style>
        /* ล็อคเป้าทุกปุ่มที่มีคำว่า UNIT */
        button[kind="secondary"] {{
            background-color: transparent !important;
            color: {gold_neon} !important;
            border: 2px solid {gold_neon} !important; /* ความหนา 2px */
            border-radius: 15px !important;
            height: 65px !important;
            font-weight: bold !important;
            font-size: 20px !important;
            text-transform: uppercase !important;
            /* เพิ่มแสงฟุ้งสีทอง */
            box-shadow: 0 0 15px {gold_neon}, inset 0 0 10px {gold_neon} !important;
            transition: all 0.3s ease-in-out !important;
            margin-bottom: 10px !important;
        }}

        /* เอฟเฟกต์ตอนเอาเมาส์วาง/กด */
        button[kind="secondary"]:hover {{
            background-color: {gold_neon} !important;
            color: #000000 !important;
            box-shadow: 0 0 30px {gold_neon}, 0 0 60px {gold_neon} !important;
            transform: translateY(-3px) !important;
        }}
        
        /* แก้ไขระยะห่างระหว่างคอลัมน์ให้ดูเต็มจอ */
        [data-testid="column"] {{
            padding: 5px !important;
        }}
        </style>
    """, unsafe_allow_html=True)

    # 3. สร้างปุ่ม 20 ห้อง (เรียงลำดับ 01-20 ให้สวยๆ)
    cols = st.columns(4)
    for i in range(1, 21):
        with cols[(i-1)%4]:
            if st.button(f"UNIT {i:02d}", key=f"u{i}", use_container_width=True):
                st.session_state.page = str(i)
                st.rerun()


else:
    # --- ปุ่มกลับ (Back Button) และเนื้อหาในหน้า UNIT ---
    col_back, col_title = st.columns([1, 4])
    with col_back:
        # ใช้ CSS class 'back-btn' ที่เราเขียนไว้ในส่วนหัว
        if st.button("⬅️ HUB", key="back_home"):
            st.session_state.page = "HOME"
            st.rerun()
    with col_title:
        st.markdown(f"<h2 style='color:#0F26D3; text-shadow: 0 0 10px #FF0738;'>⚡ UNIT {st.session_state.page} ONLINE</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # พื้นที่เขียนโค้ดแต่ละห้อง
    if st.session_state.page == "1":
        st.write("ระบบ Unit 01 กำลังทำงาน...")


