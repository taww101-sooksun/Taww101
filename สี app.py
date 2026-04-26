# =========================================================
# 🛡️ SYNAPSE COMMAND CENTER - ALL-IN-ONE IMPORTS
# =========================================================

# --- 1. Standard Libraries (พื้นฐานที่ต้องมี) ---
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

# --- 2. Data & Math (การคำนวณและข้อมูล) ---
import pandas as pd
import numpy as np
import pytz
import matplotlib.pyplot as plt
import networkx as nx

# --- 3. Streamlit Core & Components (ระบบหน้าจอ) ---
import streamlit as st
import streamlit.components.v1 as components
from streamlit_player import st_player
from streamlit_js_eval import streamlit_js_eval
from streamlit_autorefresh import st_autorefresh

# --- 4. Firebase & Security (ฐานข้อมูลและความปลอดภัย) ---
import firebase_admin
from firebase_admin import credentials, firestore, storage, auth
# (ตัวนี้ผมเพิ่มให้สำหรับเรียกใช้ Realtime DB โดยตรง)
from firebase_admin import db as realtime_db 

# --- 5. AI & Generative (ปัญญาประดิษฐ์) ---
import google.generativeai as genai
import replicate

# --- 6. Multimedia & Audio (ระบบเสียงและวิดีโอ) ---
import librosa
import soundfile as sf
from pydub import AudioSegment
from gtts import gTTS
import moviepy.editor as mp
# (ตัวนี้ผมเพิ่มให้ เผื่อคุณต้องการจัดการไฟล์ภาพ/วิดีโอระดับสูง)
from PIL import Image 

# --- 7. Location & Maps (พิกัดและแผนที่) ---
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import osmnx as ox

# --- 8. Networking & Real-time (การสื่อสาร) ---
import requests
from streamlit_webrtc import streamlit_webrtc_streaming_video_handle

# =========================================================
# 🛠️ ZONE 1: FIREBASE INITIALIZATION (ดึงจาก Secrets)
# =========================================================

if not firebase_admin._apps:
    try:
        # ดึงค่าที่วางไว้ใน Secrets อัตโนมัติ
        cred_info = dict(st.secrets["firebase_service_account"])
        cred = credentials.Certificate(cred_info)
        firebase_admin.initialize_app(cred, {
            'storageBucket': st.secrets["firebase_config"]["storageBucket"],
            'databaseURL': st.secrets["firebase_config"].get("databaseURL", "")
        })
    except Exception as e:
        st.error(f"การเชื่อมต่อ Firebase ผิดพลาด: {e}")

# ตัวแปรกลางสำหรับใช้งานในทุก UNIT
db = firestore.client() if firebase_admin._apps else None
bucket = storage.bucket() if firebase_admin._apps else None

# =========================================================
# 🏠 ZONE 2: 20-UNIT STRUCTURE SETUP
# =========================================================

st.set_page_config(page_title="SYNAPSE COMMAND", layout="wide")
if 'page' not in st.session_state: st.session_state.page = "HOME"

# (ต่อด้วยระบบ Navigation และห้องต่างๆ 1-20 ของคุณ...)
