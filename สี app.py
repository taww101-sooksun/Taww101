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
synapse_size = "120px"  # ขนาดคำว่า SYNAPSE
motto_size = "45px"     # ขนาดคำว่า อยู่นิ่งๆ ไม่เจ็บตัว
slogan_glow_speed = "3s" # ความเร็วการวิ่งของสี

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
        animation: logo-dance 3s ease-in-out infinite;
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

st.markdown('<div class="logo-container">', unsafe_allow_html=True)
try:
    st.image("logo1.png", width=220)
except:
    st.write("")
st.markdown('</div>', unsafe_allow_html=True)

# แสดงผลแบบแยกชั้น ความใหญ่สะใจแน่นอน
st.markdown(f'''
    <div class="neon-wrapper">
        <span class="synapse-title">SYNAPSE</span>
        <span class="motto-text">อยู่นิ่งๆ ไม่เจ็บตัว</span>
    </div>
''', unsafe_allow_html=True)

# =========================================================
# 📟 ZONE: NAVIGATION SYSTEM
# =========================================================

if 'page' not in st.session_state: st.session_state.page = "HOME"

if st.session_state.page == "HOME":
    cols = st.columns(4)
    colors = ["#FF3131", "#FF5E33", "#FFF01F", "#0FFF50", "#00F3FF", "#1F51FF", "#FF44CC"]
    
    for i in range(1, 21):
        with cols[(i-1)%4]:
            c = colors[(i-1)%7]
            # ปุ่ม 20 ห้อง
            st.markdown(f"""<style>div.stButton > button[key="u{i}"] {{ color: {c}; border: 1px solid {c}; box-shadow: 0 0 5px {c}; height: 60px; border-radius: 15px; font-weight: bold; }} div.stButton > button[key="u{i}"]:hover {{ background-color: {c}; color: #000; box-shadow: 0 0 20px {c}; }}</style>""", unsafe_allow_html=True)
            if st.button(f"UNIT {i:02d}", key=f"u{i}", use_container_width=True):
                st.session_state.page = str(i)
                st.rerun()

else:
    # --- ปุ่มกลับ (Back Button) แสดงเฉพาะตอนเข้าห้อง ---
    col_back, col_title = st.columns([1, 4])
    with col_back:
        if st.button("⬅️ HUB", key="back_home"):
            st.session_state.page = "HOME"
            st.rerun()
    with col_title:
        st.markdown(f"<h2 style='color:#0F26D3; text-shadow: 0 0 10px #FF0738;'>⚡ UNIT {st.session_state.page} ONLINE</h2>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # พื้นที่เขียนโค้ดแต่ละห้อง
    if st.session_state.page == "1":
        st.write("เขียนความจริงลงไปใน Unit 01...")

# =========================================================
