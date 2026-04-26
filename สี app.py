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

# --- 5. NAVIGATION HUB (20 UNITS SYSTEM) ---
if 'page' not in st.session_state: st.session_state.page = "HOME"

if st.session_state.page == "HOME":
    st.write("##")
    # สร้างปุ่ม 20 ปุ่มแบบอัตโนมัติ (4 คอลัมน์)
    cols = st.columns(4)
    for i in range(1, 21):
        with cols[(i-1)%4]:
            # ปรับแต่งชื่อปุ่มตามฟังก์ชันหลักที่เราตกลงกัน
            btn_label = f"UNIT {i:02d}"
            if i == 1: btn_label = "🎵 UNIT 01: DJ"
            elif i == 2: btn_label = "🛰️ UNIT 02: RADAR"
            elif i == 3: btn_label = "🎨 UNIT 03: COLOR"
            elif i == 4: btn_label = "⚡ UNIT 04: SENSOR"
            elif i == 5: btn_label = "🔮 UNIT 05: LOGIC"

            if st.button(btn_label, key=f"u{i}", use_container_width=True):
                st.session_state.page = str(i)
                st.rerun()
else:
    # --- แถบควบคุมด้านบนในทุกห้อง ---
    c_back, c_title = st.columns([1, 4])
    with c_back:
        if st.button("⬅️ HUB"):
            st.session_state.page = "HOME"
            st.rerun()
    
    # =========================================================
    # 📥 โซนก๊อปวางโค้ดใหม่ (แยกตามเลขห้อง)
    # =========================================================

    if st.session_state.page == "1":
    # ==========================================
    # 🎵 UNIT 01: DJ STATION (MUSIC PLAYER)
    # ==========================================
    
        st.markdown("<h2 class='neon-wrapper' style='font-size:30px;'>🎧 SYNAPSE DJ STATION V.3</h2>", unsafe_allow_html=True)
        
        # 1. ดึงรายชื่อไฟล์เพลงในโฟลเดอร์
        all_songs = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
        
        if not all_songs:
            st.warning("⚠️ ไม่พบไฟล์ .mp3 ในระบบ กรุณาอัปโหลดไฟล์เพลงไว้ในโฟลเดอร์เดียวกับโค้ด")
        else:
            # 2. ส่วนเลือกเพลงแยก 2 ฝั่ง
            col_sel_a, col_sel_b = st.columns(2)
            with col_sel_a:
                song_a = st.selectbox("💿 DECK A (LEFT)", ["-- Select --"] + all_songs, key="sa")
            with col_sel_b:
                song_b = st.selectbox("💿 DECK B (RIGHT)", ["-- Select --"] + all_songs, key="sb")

            # แปลงไฟล์เป็น Base64
            data_a = get_base64(song_a) if song_a != "-- Select --" else ""
            data_b = get_base64(song_b) if song_b != "-- Select --" else ""

            # 3. HTML & JS Mixer Engine (Visualizer + Control)
            mixer_html = f"""
            <div style="background: #000; border: 2px solid {primary_neon}; border-radius: 20px; padding: 15px; font-family: monospace;">
                
                <marquee style="color: {primary_neon}; margin-bottom: 10px;"> 
                    Now Playing Deck A: {song_a} | Deck B: {song_b} --- Synapse High-Res Audio System --- 
                </marquee>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div style="border: 1px solid {primary_neon}; padding: 10px; border-radius: 15px; text-align: center;">
                        <div style="display: flex; justify-content: space-between; font-size: 10px; color: {primary_neon};">
                            <span id="curA">00:00</span><span id="remA">-00:00</span>
                        </div>
                        <canvas id="canvasA" style="width: 100%; height: 60px; background: #111; margin: 5px 0; border-radius:5px;"></canvas>
                        <input type="range" id="volA" min="0" max="1" step="0.01" value="0.7" style="width: 100%; accent-color: {primary_neon};">
                        <div style="margin-top: 10px;">
                            <button onclick="play('A')" style="background:{primary_neon}; border:none; padding:5px 15px; border-radius:5px; color:#000; font-weight:bold; cursor:pointer;">PLAY A</button>
                            <button onclick="pause('A')" style="background:none; border:1px solid {primary_neon}; color:{primary_neon}; padding:5px 15px; border-radius:5px; cursor:pointer;">PAUSE</button>
                        </div>
                    </div>

                    <div style="border: 1px solid #FF44CC; padding: 10px; border-radius: 15px; text-align: center;">
                        <div style="display: flex; justify-content: space-between; font-size: 10px; color: #FF44CC;">
                            <span id="curB">00:00</span><span id="remB">-00:00</span>
                        </div>
                        <canvas id="canvasB" style="width: 100%; height: 60px; background: #111; margin: 5px 0; border-radius:5px;"></canvas>
                        <input type="range" id="volB" min="0" max="1" step="0.01" value="0.7" style="width: 100%; accent-color: #FF44CC;">
                        <div style="margin-top: 10px;">
                            <button onclick="play('B')" style="background:#FF44CC; border:none; padding:5px 15px; border-radius:5px; color:#fff; font-weight:bold; cursor:pointer;">PLAY B</button>
                            <button onclick="pause('B')" style="background:none; border:1px solid #FF44CC; color:#FF44CC; padding:5px 15px; border-radius:5px; cursor:pointer;">PAUSE</button>
                        </div>
                    </div>
                </div>

                <div style="margin-top:20px; text-align:center;">
                    <small style="color:#888;">CROSSFADER (A <-> B)</small><br>
                    <input type="range" id="fader" min="0" max="1" step="0.01" value="0.5" style="width: 80%; accent-color: white;">
                </div>

                <audio id="audioA" src="data:audio/mp3;base64,{data_a}" crossorigin="anonymous"></audio>
                <audio id="audioB" src="data:audio/mp3;base64,{data_b}" crossorigin="anonymous"></audio>

                <script>
                    const audA = document.getElementById('audioA');
                    const audB = document.getElementById('audioB');
                    const ctx = new (window.AudioContext || window.webkitAudioContext)();
                    const fader = document.getElementById('fader');
                    
                    function setupVisualizer(audioElem, canvasID, color) {{
                        const src = ctx.createMediaElementSource(audioElem);
                        const analyser = ctx.createAnalyser();
                        const canvas = document.getElementById(canvasID);
                        const canvasCtx = canvas.getContext("2d");

                        src.connect(analyser);
                        analyser.connect(ctx.destination);
                        analyser.fftSize = 256;

                        const bufferLength = analyser.frequencyBinCount;
                        const dataArray = new Uint8Array(bufferLength);

                        function draw() {{
                            requestAnimationFrame(draw);
                            analyser.getByteFrequencyData(dataArray);
                            canvasCtx.fillStyle = "#111";
                            canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
                            
                            const barWidth = (canvas.width / bufferLength) * 2;
                            let x = 0;
                            for(let i = 0; i < bufferLength; i++) {{
                                let barHeight = dataArray[i] / 4;
                                canvasCtx.fillStyle = color;
                                canvasCtx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
                                x += barWidth + 1;
                            }}
                        }}
                        draw();
                    }}

                    let setupA = false, setupB = false;
                    function play(deck) {{
                        if (ctx.state === 'suspended') ctx.resume();
                        if (deck === 'A') {{
                            if(!setupA) {{ setupVisualizer(audA, 'canvasA', '{primary_neon}'); setupA = true; }}
                            audA.play();
                        }} else {{
                            if(!setupB) {{ setupVisualizer(audB, 'canvasB', '#FF44CC'); setupB = true; }}
                            audB.play();
                        }}
                    }}
                    function pause(deck) {{ deck === 'A' ? audA.pause() : audB.pause(); }}

                    // Link fader to volumes
                    fader.oninput = () => {{
                        audA.volume = (1 - fader.value) * document.getElementById('volA').value;
                        audB.volume = fader.value * document.getElementById('volB').value;
                    }};

                    function updateTime(aud, curID, remID) {{
                        aud.ontimeupdate = () => {{
                            let cM = Math.floor(aud.currentTime/60), cS = Math.floor(aud.currentTime%60);
                            document.getElementById(curID).innerText = (cM<10?'0'+cM:cM)+":"+(cS<10?'0'+cS:cS);
                            let r = aud.duration - aud.currentTime;
                            if(!isNaN(r)) {{
                                let rM = Math.floor(r/60), rS = Math.floor(r%60);
                                document.getElementById(remID).innerText = "-"+(rM<10?'0'+rM:rM)+":"+(rS<10?'0'+rS:rS);
                            }}
                        }};
                    }}
                    updateTime(audA, 'curA', 'remA');
                    updateTime(audB, 'curB', 'remB');
                </script>
            </div>
            """
            components.html(mixer_html, height=450)
            st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | Tactical Sound Module v4.2")

    elif st.session_state.page == "2":
        # --- [ วางโค้ด Radar/Chat UNIT 02 ตรงนี้ ] ---
        st.write("🛰️ กำลังสแกนหา AGENT...")

    elif st.session_state.page == "3":
        # --- [ วางโค้ดเปลี่ยนสี UNIT 03 ตรงนี้ ] ---
        st.write("🎨 ระบบปรับแต่ง Interface...")

    elif st.session_state.page == "4":
        # --- [ วางโค้ดวัดเสียง/สั่น UNIT 04 ตรงนี้ ] ---
        st.write("⚡ กำลังเตรียมเซนเซอร์...")

    elif st.session_state.page == "5":
        # --- [ วางโค้ด Quantum Logic HUB UNIT 05 ตรงนี้ ] ---
        st.write("🔮 กำลังประมวลผลฐานข้อมูล...")

    # --- ห้องที่ 6-20 เตรียมไว้ให้แล้ว พี่แค่ก๊อปโค้ดมาใส่แทนที่ st.info ---
    elif st.session_state.page == "6":
        st.info("⌛ UNIT 06: พร้อมสำหรับการติดตั้งโมดูลใหม่")
        
    elif st.session_state.page == "7":
        st.info("⌛ UNIT 07: พร้อมสำหรับการติดตั้งโมดูลใหม่")

    elif st.session_state.page == "8":
        st.info("⌛ UNIT 08: พร้อมสำหรับการติดตั้งโมดูลใหม่")
    
    # ... พี่สามารถเพิ่ม elif ไปเรื่อยๆ จนถึง 20 ได้เลยครับ ...
    
    else:
        st.warning(f"UNIT {st.session_state.page} อยู่ระหว่างการพัฒนาโดย AGENT TA")

# =========================================================
st.caption(f"SYNAPSE OS v4.2 | {datetime.now().strftime('%H:%M:%S')}")

