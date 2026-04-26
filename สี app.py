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
        st.markdown("<h2 class='neon-wrapper'>🛰️ UNIT 02: RADAR MONITOR</h2>", unsafe_allow_html=True)

        # --- [1] ดึงพิกัดปัจจุบัน (GPS Detection) ---
        loc_data = get_geolocation() 
        my_lat, my_lon = 13.7367, 100.5231 # พิกัดสำรอง
        if loc_data and 'coords' in loc_data:
            my_lat = loc_data['coords'].get('latitude', my_lat)
            my_lon = loc_data['coords'].get('longitude', my_lon)

        # --- [2] อัปเดตพิกัดตัวเองขึ้น Firebase (Broadcast) ---
        if st.button("📡 BROADCAST MY LOCATION", use_container_width=True):
            my_id = st.session_state.get('user', 'ADMIN')
            realtime_db.reference(f'users/{my_id}').update({
                'lat': my_lat,
                'lon': my_lon,
                'ts': time.time()
            })
            st.toast("ส่งพิกัดเข้าศูนย์บัญชาการแล้ว", icon="📍")

        # --- [3] ส่วนแสดงแผนที่ดาวเทียม (Google Satellite) ---
        st.markdown("### 🗺️ LIVE TACTICAL MAP")
        
        # สร้างแผนที่ Folium
        m = folium.Map(
            location=[my_lat, my_lon], 
            zoom_start=15, 
            tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
            attr='Google Satellite'
        )
        
        # ปักหมุดตัวเรา (สีแดง)
        folium.Marker(
            [my_lat, my_lon], 
            icon=folium.Icon(color='red', icon='star'), 
            tooltip="YOU (COMMANDER)"
        ).add_to(m)

        # --- [4] สแกนหา Agent อื่นๆ ในฐานข้อมูล ---
        try:
            all_users = realtime_db.reference('users').get()
            if all_users:
                agent_stats = []
                for uid, data in all_users.items():
                    if uid != st.session_state.get('user', 'ADMIN') and 'lat' in data:
                        u_lat, u_lon = data['lat'], data['lon']
                        
                        # คำนวณระยะห่างด้วยสูตร Haversine ที่พี่มี
                        dist = haversine(my_lat, my_lon, u_lat, u_lon)
                        
                        # ปักหมุด Agent อื่นๆ (สีเขียว)
                        folium.Marker(
                            [u_lat, u_lon], 
                            icon=folium.Icon(color='green', icon='info-sign'), 
                            tooltip=f"AGENT: {uid}"
                        ).add_to(m)
                        
                        # วาดเส้นเชื่อมโยง (Tactical Line)
                        folium.PolyLine(
                            [[my_lat, my_lon], [u_lat, u_lon]], 
                            color=primary_neon, 
                            weight=2, 
                            dash_array='10', 
                            opacity=0.6
                        ).add_to(m)
                        
                        agent_stats.append({"Agent": uid, "Distance (km)": round(dist, 2)})

                # แสดงแผนที่
                st_folium(m, width="100%", height=400)

                # --- [5] ตารางสรุปพิกัดระยะห่าง ---
                if agent_stats:
                    st.markdown("### 📊 PROXIMITY REPORT")
                    st.table(pd.DataFrame(agent_stats))
        except Exception as e:
            st.error(f"🛰️ ระบบสแกนขัดข้อง: {e}")
            st_folium(m, width="100%", height=400) # แสดงแค่แผนที่ตัวเองถ้าดึงเพื่อนไม่ได้


    elif st.session_state.page == "3":
        # --- [ วางโค้ดเปลี่ยนสี UNIT 03 ตรงนี้ ] ---
        st.write("🎨 ระบบปรับแต่ง Interface...")

    elif st.session_state.page == "4":
        # --- [ วางโค้ดวัดเสียง/สั่น UNIT 04 ตรงนี้ ] ---
        st.write("⚡ กำลังเตรียมเซนเซอร์...")
    elif st.session_state.page == "5":
        st.markdown("<h2 class='neon-wrapper'>🔮 UNIT 05: THE TRUTH SCANNER</h2>", unsafe_allow_html=True)

        # ---------------------------------------------------------
        # หัวข้อที่ 1: ตรวจสอบพิกัดวันเดี่ยว (Single Day Decoder)
        # ---------------------------------------------------------
        st.markdown("### 1️⃣ ตรวจสอบรหัสความจริงรายวัน (1960-2026)")
        target_date = st.date_input("เลือกวันที่ที่อยากรู้", value=date.today(), 
                                    min_value=date(1960,1,1), max_value=date(2026,12,31), key="single_d")
        
        if target_date:
            d = get_detailed_logic(target_date)
            st.markdown(f"""
                <div class="logic-box">
                    <b>วันที่:</b> {target_date.strftime('%d/%m/%Y')} (วัน{d['day_name']}) <br>
                    <b>สภาวะดาราศาสตร์:</b> {d['phase']} (รอบดวงจันทร์ 29.53)<br>
                    <b>รหัสที่คำนวณได้:</b> <span style="color:#00ff41; font-size:20px;">{d['res']}</span>
                </div>
            """, unsafe_allow_html=True)

        st.divider()

        # ---------------------------------------------------------
        # หัวข้อที่ 2: สแกนคู่ขนาน & หาค่า GAP (Double Agent Scan)
        # ---------------------------------------------------------
        st.markdown("### 2️⃣ วิเคราะห์รหัสคู่ขนาน & สัญญาณ GAP")
        c1, c2 = st.columns(2)
        with c1:
            dob1 = st.date_input("👤 AGENT 1 (ตัวตั้งต้น)", value=None, min_value=date(1960,1,1), key="u1_p2")
        with c2:
            dob2 = st.date_input("👤 AGENT 2 (คู่สแกน)", value=None, min_value=date(1960,1,1), key="u2_p2")

        if dob1 and dob2:
            d1 = get_detailed_logic(dob1)
            d2 = get_detailed_logic(dob2)
            gap = abs(d1['res'] - d2['res'])

            # อธิบายที่มา (แฉความจริง)
            st.write("🛠️ **ขั้นตอนการถอดรหัส:**")
            col_ex1, col_ex2 = st.columns(2)
            with col_ex1:
                st.info(f"AGENT 1: วัน{d1['day_name']}({d1['day_val']}) {d1['phase']}({d1['m_num']}) \n\n สูตร: {d1['formula']} = {d1['res']}")
            with col_ex2:
                st.info(f"AGENT 2: วัน{d2['day_name']}({d2['day_val']}) {d2['phase']}({d2['m_num']}) \n\n สูตร: {d2['formula']} = {d2['res']}")

            # สรุปค่า GAP และความสำคัญ
            st.markdown(f"<h1 style='text-align:center; color:#00ff41;'>GAP: {gap:.4f}</h1>", unsafe_allow_html=True)
            
            # ระบบจัดลำดับความสำคัญ (ธร-เพชร-กงจักร)
            if gap <= 1.0:
                st.error("💎 **ระดับ: เพชร (Diamond)** - รหัสแฝด พลังงานสูงสุด")
            elif 3.8 <= gap <= 4.2:
                st.warning("🌀 **ระดับ: ธร (Tor)** - รหัสคู่ขนาน สัญญาณสะท้อนรุนแรง")
            elif gap >= 10.0:
                st.success("⚙️ **ระดับ: กงจักร (Chakra)** - รหัสตัดขาด พลังงานแยกตัวอิสระ")
            else:
                st.write("💡 ระดับ: ปกติ - พลังงานสมดุลทั่วไป")

        st.divider()

        # ---------------------------------------------------------
        # หัวข้อที่ 3: แผนที่พิกัดเวลา (Past & Future Timeline)
        # ---------------------------------------------------------
        st.markdown("### 3️⃣ แผนที่พิกัดกาลเวลา (Past & Future)")
        if dob1:
            st.write(f"วิเคราะห์รอบเวลาสำหรับรหัส: **{d1['res']}**")
            
            tab_back, tab_next = st.tabs(["⏪ สแกนอดีต (365 วัน)", "🔮 สแกนอนาคต (365 วัน)"])
            
            with tab_back:
                past_df = run_scanner(d1['res'], date.today(), 365, mode="past")
                st.dataframe(past_df, use_container_width=True, hide_index=True)
            
            with tab_next:
                future_df = run_scanner(d1['res'], date.today(), 365, mode="future")
                st.dataframe(future_df, use_container_width=True, hide_index=True)
        else:
            st.info("กรุณากรอกวันเกิด AGENT 1 เพื่อสร้างแผนที่กาลเวลา")


                
            
        # ---------------------------------------------------------
        # หัวข้อที่ 3: แผนที่พิกัดเวลา (Past & Future Timeline)
        # ---------------------------------------------------------
        st.markdown("### 3️⃣ แผนที่พิกัดกาลเวลา (Past & Future)")
        if dob1:
            st.write(f"วิเคราะห์รอบเวลาสำหรับรหัส: **{d1['res']}**")
            
            tab_back, tab_next = st.tabs(["⏪ สแกนอดีต (365 วัน)", "🔮 สแกนอนาคต (365 วัน)"])
            
            with tab_back:
                past_df = run_scanner(d1['res'], date.today(), 365, mode="past")
                st.dataframe(past_df, use_container_width=True, hide_index=True)
            
            with tab_next:
                future_df = run_scanner(d1['res'], date.today(), 365, mode="future")
                st.dataframe(future_df, use_container_width=True, hide_index=True)
        else:
            st.info("กรุณากรอกวันเกิด AGENT 1 เพื่อสร้างแผนที่กาลเวลา")

 elif page == "6":
        st.markdown("<h2 class='neon-wrapper'>💬 UNIT 06: TACTICAL COMMS</h2>", unsafe_allow_html=True)
        
        # --- [1] ดึงข้อมูลพิกัดเราก่อน ---
        loc = get_geolocation()
        my_lat, my_lon = 13.7367, 100.5231
        if loc and 'coords' in loc:
            my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']

        # --- [2] ส่วนเลือก Agent ที่จะคุยด้วย ---
        st.markdown("### 🛰️ SCANNING FOR AGENTS...")
        try:
            all_users = realtime_db.reference('users').get()
            if all_users:
                # กรองรายชื่อ Agent อื่นๆ
                agent_list = [uid for uid in all_users.keys() if uid != "ADMIN"]
                
                if not agent_list:
                    st.info("🌑 ยังไม่มี Agent อื่นออนไลน์ในขณะนี้")
                else:
                    target_agent = st.selectbox("เลือก Agent ที่ต้องการติดต่อ:", agent_list)
                    
                    # คำนวณระยะห่างความจริง
                    target_data = all_users[target_agent]
                    if 'lat' in target_data:
                        dist = haversine(my_lat, my_lon, target_data['lat'], target_data['lon'])
                        
                        # แสดงผลสถานะความปลอดภัย
                        col_stat1, col_stat2 = st.columns(2)
                        with col_stat1:
                            st.metric("DISTANCE", f"{dist:.2f} KM")
                        with col_stat2:
                            status = "🟢 SECURE" if dist < 5 else "🟡 REMOTE"
                            st.metric("STATUS", status)
                        
                        st.divider()
                        
                        # --- [3] ระบบแชทความจริง (Real-time Chat) ---
                        st.markdown(f"### ✉️ SECURE CHANNEL: {target_agent}")
                        
                        # ดึงข้อความ
                        chat_ref = realtime_db.reference(f'chats/ADMIN_{target_agent}')
                        messages = chat_ref.order_by_child('ts').limit_to_last(10).get()
                        
                        # แสดงกล่องข้อความ
                        chat_container = st.container(height=300)
                        if messages:
                            for msg_id, msg_data in messages.items():
                                align = "right" if msg_data['sender'] == "ADMIN" else "left"
                                color = primary_neon if msg_data['sender'] == "ADMIN" else "#FF44CC"
                                chat_container.markdown(f"""
                                    <div style="text-align: {align}; margin-bottom: 10px;">
                                        <div style="display: inline-block; padding: 8px 15px; border-radius: 15px; 
                                                    background: #111; border: 1px solid {color}; color: white;">
                                            <small style="color: {color};">{msg_data['sender']}:</small><br>{msg_data['text']}
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)

                        # ส่งข้อความ
                        new_msg = st.chat_input("พิมพ์ข้อความแจ้งศูนย์บัญชาการ...")
                        if new_msg:
                            chat_ref.push({
                                'sender': "ADMIN",
                                'text': new_msg,
                                'ts': time.time()
                            })
                            st.rerun()
            else:
                st.warning("⚠️ ไม่พบข้อมูลในฐานระบบ")
        except Exception as e:
            st.error(f"❌ ระบบ Comms ขัดข้อง: {e}")

        st.caption("🔒 การเชื่อมต่อเข้ารหัสแบบ 256-bit | อยู่นิ่งๆ ไม่เจ็บตัว")



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
