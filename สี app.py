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
    # 📥 โซนจัดการห้องรบ (UNIT 01 - 11)
    # =========================================================

    if st.session_state.page == "1":
        st.markdown("<h1 class='neon-title-unit'>🎵 : MP3</h1>", unsafe_allow_html=True)
        
        # --- 1. สแกนไฟล์เพลง (.mp3) จากหน้าหลัก ---
        music_files = [f for f in os.listdir(".") if f.endswith(".mp3")]

        if music_files:
            col_sel1, col_sel2 = st.columns(2)
            with col_sel1:
                song_a = st.selectbox("💿 DECK A", music_files, key="select_a")
                with open(song_a, "rb") as f:
                    b64_a = base64.b64encode(f.read()).decode()
            with col_sel2:
                default_idx = 1 if len(music_files) > 1 else 0
                song_b = st.selectbox("💿 DECK B", music_files, index=default_idx, key="select_b")
                with open(song_b, "rb") as f:
                    b64_b = base64.b64encode(f.read()).decode()

            # --- 2. เครื่องเล่นเพลง + กราฟเสียงเต้นตามจังหวะ ---
            html_code = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://cdn.tailwindcss.com"></script>
                <style>
                    body {{ background: transparent; color: white; font-family: 'Courier New', monospace; }}
                    .deck-box {{ border: 2px solid #333; background: #310000; border-radius: 15px; padding: 12px; }}
                    .active-a {{ border-color: #ff00de; box-shadow: 0 0 30px #ff00de; }}
                    .active-b {{ border-color: #00f3ff; box-shadow: 0 0 30px #00f3ff; }}
                    
                    /* ตัวหนังสือวิ่ง */
                    .marquee {{ background: #000; border: 1px solid #222; padding: 4px; overflow: hidden; border-radius: 10px; margin-bottom: 10px; }}
                    .marquee p {{ display: inline-block; white-space: nowrap; animation: move 12s linear infinite; color: #00f3ff; font-size: 11px; }}
                    @keyframes move {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
                    
                    canvas {{ width: 100%; height: 80px; background: #000; border-radius: 8px; margin-bottom: 10px; border: 1px solid #1a1a1a; }}
                    .btn-ctrl {{ border: 1px solid #444; background: #111; padding: 6px; border-radius: 6px; font-size: 10px; width: 48%; }}
                    .vol-bar {{ width: 100%; accent-color: #ff00de; }}
                </style>
            </head>
            <body>
                <div class="grid grid-cols-2 gap-4">
                    <div id="boxA" class="deck-box">
                        <div class="marquee"><p>{song_a}</p></div>
                        <canvas id="vizA"></canvas>
                        <div class="flex justify-between mb-2">
                            <button onclick="play('A')" class="btn-ctrl text-green-400">PLAY A</button>
                            <button onclick="stop('A')" class="btn-ctrl text-red-400">STOP</button>
                        </div>
                        <input type="range" class="vol-bar" oninput="setVol('A', this.value)" value="80">
                    </div>

                    <div id="boxB" class="deck-box">
                        <div class="marquee"><p>{song_b}</p></div>
                        <canvas id="vizB"></canvas>
                        <div class="flex justify-between mb-2">
                            <button onclick="play('B')" class="btn-ctrl text-green-400">PLAY B</button>
                            <button onclick="stop('B')" class="btn-ctrl text-red-400">STOP</button>
                        </div>
                        <input type="range" class="vol-bar" style="accent-color: #00f3ff;" oninput="setVol('B', this.value)" value="150">
                    </div>
                </div>

                <script>
                    let ctx, songA, songB, gA, gB, srcA, srcB, anaA, anaB;
                    let dataA, dataB;

                    async function init() {{
                        if (!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)();
                        if (!songA) songA = await decode("{b64_a}");
                        if (!songB) songB = await decode("{b64_b}");
                        
                        if (!anaA) {{
                            anaA = ctx.createAnalyser(); anaA.fftSize = 64;
                            dataA = new Uint8Array(anaA.frequencyBinCount);
                            gA = ctx.createGain(); gA.connect(ctx.destination);
                        }}
                        if (!anaB) {{
                            anaB = ctx.createAnalyser(); anaB.fftSize = 64;
                            dataB = new Uint8Array(anaB.frequencyBinCount);
                            gB = ctx.createGain(); gB.connect(ctx.destination);
                        }}
                        draw();
                    }}

                    async function decode(b64) {{
                        const r = await fetch("data:audio/mp3;base64," + b64);
                        return await ctx.decodeAudioData(await r.arrayBuffer());
                    }}

                    function draw() {{
                        requestAnimationFrame(draw);
                        if(anaA) {{
                            anaA.getByteFrequencyData(dataA);
                            renderViz('vizA', dataA, '#FF3131');
                        }}
                        if(anaB) {{
                            anaB.getByteFrequencyData(dataB);
                            renderViz('vizB', dataB, '#7B00FF');
                        }}
                    }}

                    function renderViz(id, data, color) {{
                        const can = document.getElementById(id);
                        const c = can.getContext('2d');
                        c.clearRect(0, 0, can.width, can.height);
                        let bw = (can.width / data.length) * 2;
                        for(let i=0; i<data.length; i++) {{
                            let h = (data[i]/255) * can.height;
                            c.fillStyle = color;
                            c.fillRect(i*bw, can.height - h, bw-2, h);
                        }}
                    }}

                    function play(side) {{
                        init().then(() => {{
                            if(side === 'A') {{
                                if(srcA) srcA.stop();
                                srcA = ctx.createBufferSource(); srcA.buffer = songA;
                                srcA.connect(anaA).connect(gA); srcA.start(0);
                                document.getElementById('boxA').classList.add('active-a');
                            }} else {{
                                if(srcB) srcB.stop();
                                srcB = ctx.createBufferSource(); srcB.buffer = songB;
                                srcB.connect(anaB).connect(gB); srcB.start(0);
                                document.getElementById('boxB').classList.add('active-b');
                            }}
                        }});
                    }}

                    function stop(side) {{
                        if(side === 'A' && srcA) {{ srcA.stop(); document.getElementById('boxA').classList.remove('active-a'); }}
                        if(side === 'B' && srcB) {{ srcB.stop(); document.getElementById('boxB').classList.remove('active-b'); }}
                    }}

                    function setVol(side, val) {{
                        init();
                        if(side === 'A') gA.gain.value = val/100;
                        if(side === 'B') gB.gain.value = val/100;
                    }}
                </script>
            </body>
            </html>
            """
            st.components.v1.html(html_code, height=500)
        else:
            st.warning("ไม่พบไฟล์ .mp3 ในหน้าหลักครับ")



                
    
    
    elif st.session_state.page == "2":
        st.markdown("<h2 class='neon-wrapper'>🛰️ UNIT 02: TACTICAL RADAR</h2>", unsafe_allow_html=True)
        st.info("📡 กำลังสแกนพิกัดดาวเทียมและคำนวณระยะห่าง AGENTS...")

    elif st.session_state.page == "3":
        st.markdown("<h2 class='neon-wrapper'>🔮 UNIT 03: TRUTH LOGIC</h2>", unsafe_allow_html=True)
        st.info("🧬 ระบบถอดรหัสรหัสความจริงและแผนที่พิกัดกาลเวลา...")

    elif st.session_state.page == "4":
        st.markdown("<h2 class='neon-wrapper'>⚡ UNIT 04: SENSOR SCAN</h2>", unsafe_allow_html=True)
        st.info("📶 กำลังเตรียมการเชื่อมต่อเซนเซอร์ตรวจจับความเคลื่อนไหวและเสียง...")

    elif st.session_state.page == "5":
        st.markdown("<h2 class='neon-wrapper'>🎨 UNIT 05: UI DESIGNER</h2>", unsafe_allow_html=True)
        st.info("🌈 ระบบปรับแต่งโทนสีนีออนและ CSS Interface ขั้นสูง...")

    elif st.session_state.page == "6":
        st.markdown("<h2 class='neon-wrapper'>💬 UNIT 06: COMMS CENTER</h2>", unsafe_allow_html=True)
        st.info("🛰️ ระบบสื่อสารเข้ารหัสพร้อมส่งสัญญาณหาศูนย์บัญชาการ...")

    elif st.session_state.page == "7":
        st.markdown("<h2 class='neon-wrapper'>🛠️ UNIT 07: DIY MASTER</h2>", unsafe_allow_html=True)
        st.info("🔧 บันทึกงานช่างและการซ่อมบำรุงเชิงกล (PE Pipe / Blower Maintenance)...")

    elif st.session_state.page == "8":
        st.markdown("<h2 class='neon-wrapper'>🧬 UNIT 08: SYNAPSE CORE</h2>", unsafe_allow_html=True)
        st.info("🧠 ระบบประมวลผลกลาง AI และการเขียนโค้ดเชิงลึก...")

    elif st.session_state.page == "9":
        st.markdown("<h2 class='neon-wrapper'>📹 UNIT 09: MEDIA STUDIO</h2>", unsafe_allow_html=True)
        st.info("🎬 พื้นที่จัดการ Content และวิดีโอ AI ของ AGENT TA...")

    elif st.session_state.page == "10":
        st.markdown("<h2 class='neon-wrapper'>💾 UNIT 10: FIREBASE DB</h2>", unsafe_allow_html=True)
        st.info("📂 ตรวจสอบความปลอดภัยฐานข้อมูล Cloud และไฟล์ในระบบ...")

    elif st.session_state.page == "11":
        st.markdown("<h2 class='neon-wrapper'>🏴 11: COMMAND POST</h2>", unsafe_allow_html=True)
        st.info("🏁 หน้าสรุปสถานะภารกิจทั้งหมดในศูนย์บัญชาการ...")

# =========================================================
# 🛰️ FOOTER STATS
# =========================================================
st.write("---")
st.caption(f"SYNAPSE OS v4.2 | AGENT STATUS: ONLINE | {datetime.now().strftime('%H:%M:%S')}")
