import streamlit as st
import os
import time
import base64
import hashlib
import math
import pandas as pd
from datetime import date, datetime, timedelta
import streamlit.components.v1 as components

# --- 1. การตั้งค่าระบบพื้นฐาน (Core Engine) ---
if 'main_color' not in st.session_state:
    st.session_state.main_color = "#00f3ff"
if 'sub_color' not in st.session_state:
    st.session_state.sub_color = "#ff00de"
if 'page' not in st.session_state:
    st.session_state.page = "HOME"
if 'user' not in st.session_state:
    st.session_state.user = "Agent_Guest"

# ฟังก์ชันดึงไฟล์ Base64
def get_base64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

# --- 2. การตกแต่ง UI นีออน (CSS) ---
st.set_page_config(page_title="SYNAPSE COMMAND", layout="wide")

st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background-color: #000; border: 2px solid {st.session_state.main_color}; }}
    
    .neon-text {{
        font-family: 'Courier New', monospace;
        color: #fff;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        text-shadow: 0 0 10px {st.session_state.main_color}, 0 0 20px {st.session_state.sub_color};
        margin: 20px 0;
    }}
    
    .stButton>button {{
        background: rgba(0,0,0,0.3);
        color: {st.session_state.main_color};
        border: 1px solid {st.session_state.main_color};
        border-radius: 10px;
        height: 60px;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        box-shadow: 0 0 15px {st.session_state.main_color};
        background: {st.session_state.main_color};
        color: #000;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. ส่วนหัวแอป (Logo & Slogan) ---
col_l, col_r = st.columns([1, 4])
with col_l:
    logo_data = get_base64("logo1.png")
    if logo_data:
        st.image(f"data:image/png;base64,{logo_data}", width=80)
with col_r:
    st.markdown(f'<p class="neon-text">SYNAPSE : อ.ย.น. ิ. ้.ง ๆ .ไ.ม.่.เ.จ.็.บ.ต.ั.ว</p>', unsafe_allow_html=True)

# --- 4. การจัดการหน้าจอ (Navigation) ---
if st.session_state.page != "HOME":
    if st.sidebar.button("⬅️ BACK TO HUB"):
        st.session_state.page = "HOME"
        st.rerun()

# --- 5. เนื้อหาแต่ละ UNIT ---

# [ หน้าหลัก: HUB ]
if st.session_state.page == "HOME":
    st.session_state.user = st.text_input("AGENT NAME", value=st.session_state.user)
    cols = st.columns(2)
    with cols[0]:
        if st.button("🎵 UNIT 01: DJ STATION", use_container_width=True):
            st.session_state.page = "1"; st.rerun()
        if st.button("📡 UNIT 02: RADAR & CHAT", use_container_width=True):
            st.session_state.page = "2"; st.rerun()
    with cols[1]:
        if st.button("📳 UNIT 03: VIBRATION SENSOR", use_container_width=True):
            st.session_state.page = "3"; st.rerun()
        if st.button("🎨 UNIT 04: SYSTEM COLORS", use_container_width=True):
            st.session_state.page = "4"; st.rerun()

# [ UNIT 01: DJ STATION ]
elif st.session_state.page == "1":
    st.subheader("🎧 SYNAPSE DJ STATION")
    all_songs = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
    if not all_songs:
        st.warning("No MP3 files found.")
    else:
        c1, c2 = st.columns(2)
        with c1: s_a = st.selectbox("DECK A", ["--"] + all_songs, key="sa")
        with c2: s_b = st.selectbox("DECK B", ["--"] + all_songs, key="sb")
        
        d_a = get_base64(s_a) if s_a != "--" else ""
        d_b = get_base64(s_b) if s_b != "--" else ""
        
        mixer_html = f"""
        <div style="background:#111; padding:20px; border-radius:15px; border:1px solid {st.session_state.main_color};">
            <canvas id="vA" style="width:100%; height:50px; background:#000;"></canvas>
            <audio id="audA" src="data:audio/mp3;base64,{d_a}" controls style="width:100%;"></audio>
            <hr style="border:0.5px solid #333;">
            <canvas id="vB" style="width:100%; height:50px; background:#000;"></canvas>
            <audio id="audB" src="data:audio/mp3;base64,{d_b}" controls style="width:100%;"></audio>
        </div>
        """
        components.html(mixer_html, height=350)

# [ UNIT 02: RADAR & CHAT (GPS ลำลอง) ]
elif st.session_state.page == "2":
    st.subheader("🛰️ TACTICAL RADAR")
    st.info("ระบบจำลองการสื่อสารและพิกัดดาวเทียม")
    with st.container(border=True):
        chat_msg = st.text_input("SEND SIGNAL")
        if st.button("BROADCAST"):
            st.toast(f"Signal sent by {st.session_state.user}")
    st.write("---")
    st.caption("📡 พิกัดปัจจุบัน: 13.7367, 100.5231 (BKK Static Hub)")

# [ UNIT 03: VIBRATION & SONIC ]
elif st.session_state.page == "3":
    st.subheader("⚡ VIBRATION & SONIC UNIT")
    sensor_js = f"""
    <div style="background:#000; color:{st.session_state.main_color}; padding:20px; border:2px solid {st.session_state.main_color}; border-radius:15px; text-align:center;">
        <small>แรงสั่นสะเทือน (G-Force)</small>
        <h1 id="v_val">1.000</h1>
        <small>ความดังเสียง (dB)</small>
        <h1 id="db_val">0</h1>
    </div>
    <script>
        window.addEventListener('devicemotion', (e) => {{
            let acc = e.accelerationIncludingGravity;
            if(acc) {{
                let g = Math.sqrt(acc.x**2 + acc.y**2 + acc.z**2) / 9.8;
                document.getElementById('v_val').innerText = g.toFixed(3);
            }}
        }});
        // Simple Audio Detection
        navigator.mediaDevices.getUserMedia({{audio:true}}).then(stream => {{
            const ctx = new AudioContext();
            const src = ctx.createMediaStreamSource(stream);
            const ana = ctx.createAnalyser();
            src.connect(ana);
            const data = new Uint8Array(ana.frequencyBinCount);
            function up() {{
                ana.getByteFrequencyData(data);
                let avg = data.reduce((a,b) => a+b)/data.length;
                document.getElementById('db_val').innerText = Math.round(avg);
                requestAnimationFrame(up);
            }}
            up();
        }});
    </script>
    """
    components.html(sensor_js, height=300)
    st.info("**ความเป็นจริง:** ข้อมูลดึงจาก Accelerometer และ Microphone ของอุปกรณ์จริง 100%")

# [ UNIT 04: SYSTEM COLORS ]
elif st.session_state.page == "4":
    st.subheader("🎨 INTERFACE CONTROL")
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.main_color = st.color_picker("MAIN NEON", st.session_state.main_color)
    with c2:
        st.session_state.sub_color = st.color_picker("SUB NEON", st.session_state.sub_color)
    
    if st.button("🔥 APPLY SETTINGS", use_container_width=True):
        st.rerun()

st.sidebar.caption(f"SYNAPSE OS v4.5 | {st.session_state.user}")
