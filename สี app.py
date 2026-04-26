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

# =========================================================
# 🛠️ ZONE 1: FIREBASE INITIALIZATION
# =========================================================

if not firebase_admin._apps:
    try:
        cred_info = dict(st.secrets["firebase_service_account"])
        cred = credentials.Certificate(cred_info)
        firebase_admin.initialize_app(cred, {
            'storageBucket': st.secrets["firebase_config"]["storageBucket"],
            'databaseURL': st.secrets["firebase_config"].get("databaseURL", "")
        })
    except:
        pass

db = firestore.client() if firebase_admin._apps else None
bucket = storage.bucket() if firebase_admin._apps else None

# =========================================================
# 🎨 ZONE 2: CUSTOM UI (ลบติ่ง + NEON GLOW)
# =========================================================

st.set_page_config(page_title="SYNAPSE COMMAND", layout="wide")

st.markdown("""
    <style>
    /* ลบ Header, Footer และแถบเมนู Streamlit ออกให้หมด */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #000; }

    /* เอฟเฟกต์สโลแกนนีออนเรืองแสง */
    .neon-text {
        font-family: 'Courier New', Courier, monospace;
        color: #fff;
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 3px;
        text-shadow: 
            0 0 5px #fff,
            0 0 10px #fff,
            0 0 20px #00f3ff,
            0 0 40px #00f3ff,
            0 0 80px #00f3ff;
        margin-top: 5px;
        margin-bottom: 20px;
    }
    
    .stButton>button {
        background-color: transparent;
        color: #00f3ff;
        border: 1px solid #00f3ff;
        border-radius: 10px;
        transition: 0.3s;
        height: 50px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #00f3ff;
        color: #000;
        box-shadow: 0 0 20px #00f3ff;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 🏠 ZONE 3: HEADER (LOGO + SLOGAN)
# =========================================================

col_logo, col_empty = st.columns([1, 4])
with col_logo:
    try:
        st.image("logo1.png", width=150)
    except:
        st.markdown("<p style='color: #333;'>[ NO LOGO FOUND ]</p>", unsafe_allow_html=True)

st.markdown('<p class="neon-text">SYNAPSE : อยู่นิ่งๆ ไม่เจ็บตัว</p>', unsafe_allow_html=True)

# =========================================================
# 📟 ZONE 4: 20-UNIT HUB
# =========================================================

if 'page' not in st.session_state: st.session_state.page = "HOME"

if st.session_state.page == "HOME":
    cols = st.columns(4)
    for i in range(1, 21):
        col_idx = (i-1) % 4
        with cols[col_idx]:
            if st.button(f"UNIT {i:02d}", key=f"u{i}", use_container_width=True):
                st.session_state.page = str(i)
                st.rerun()
else:
    if st.sidebar.button("⬅️ BACK TO HUB"):
        st.session_state.page = "HOME"
        st.rerun()
    
    st.markdown(f"### ⚡ SYSTEM ONLINE : UNIT {st.session_state.page}")
    st.markdown("---")
    
    # ตัวอย่างการเรียกใช้ Library ในห้องที่ 1
    if st.session_state.page == "1":
        st.write("ห้องนี้พร้อมใช้ librosa และ moviepy แล้วครับ")

# =========================================================
st.caption(f"SYNAPSE OS v4.2 | {datetime.now().strftime('%H:%M:%S')}")
