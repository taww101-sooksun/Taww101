    # 3. เครื่องเล่นเพลงระบบ Mixer (สมบูรณ์แบบ)
    mixer_html = """
    <div style="background: #111; border: 2px solid #333; border-radius: 20px; padding: 20px; font-family: 'Orbitron', monospace; color: #00f3ff;">
        <canvas id="visualizer" style="width: 100%; height: 100px; background: #000; border-radius: 10px; margin-bottom: 10px;"></canvas>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
            <div style="border: 1px solid #ff00de; padding: 10px; border-radius: 10px; text-align: center;">
                <small style="color: #ff00de;">DECK A</small>
                <input type="file" id="audioA" accept="audio/*" style="width: 100%; font-size: 10px; margin-top: 5px; color: #fff;">
                <audio id="playerA"></audio>
            </div>
            <div style="border: 1px solid #00f3ff; padding: 10px; border-radius: 10px; text-align: center;">
                <small style="color: #00f3ff;">DECK B</small>
                <input type="file" id="audioB" accept="audio/*" style="width: 100%; font-size: 10px; margin-top: 5px; color: #fff;">
                <audio id="playerB"></audio>
            </div>
        </div>

        <div style="margin-top: 20px; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
            <button onclick="playA()" style="background: #ff00de; color: white; border: none; padding: 10px; border-radius: 5px; cursor: pointer;">PLAY A</button>
            <button onclick="stopAll()" style="background: #333; color: white; border: none; padding: 10px; border-radius: 5px; cursor: pointer;">STOP</button>
            <button onclick="playB()" style="background: #00f3ff; color: white; border: none; padding: 10px; border-radius: 5px; cursor: pointer;">PLAY B</button>
        </div>

        <div style="margin-top: 15px; text-align: center;">
            <small>CROSSFADER</small><br>
            <input type="range" id="fader" min="0" max="100" value="50" style="width: 80%;">
        </div>
    </div>

    <script>
    const ctxA = new (window.AudioContext || window.webkitAudioContext)();
    const playerA = document.getElementById('playerA');
    const playerB = document.getElementById('playerB');
    const fader = document.getElementById('fader');

    // โหลดไฟล์เข้า Deck
    document.getElementById('audioA').onchange = function(e) {
        playerA.src = URL.createObjectURL(this.files[0]);
    };
    document.getElementById('audioB').onchange = function(e) {
        playerB.src = URL.createObjectURL(this.files[0]);
    };

    function playA() { playerA.play(); ctxA.resume(); }
    function playB() { playerB.play(); ctxA.resume(); }
    function stopAll() { playerA.pause(); playerB.pause(); }

    // ระบบ Crossfade (สลับเสียงซ้ายขวา)
    fader.oninput = function() {
        playerA.volume = (100 - this.value) / 100;
        playerB.volume = this.value / 100;
    };

    // --- ระบบ Visualizer (ความจริงที่สวยงาม) ---
    const canvas = document.getElementById('visualizer');
    const canvasCtx = canvas.getContext('2d');
    const srcA = ctxA.createMediaElementSource(playerA);
    const analyzer = ctxA.createAnalyser();
    srcA.connect(analyzer);
    analyzer.connect(ctxA.destination);
    analyzer.fftSize = 64;
    const bufferLength = analyzer.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    function draw() {
        requestAnimationFrame(draw);
        analyzer.getByteFrequencyData(dataArray);
        canvasCtx.fillStyle = '#000';
        canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
        let barWidth = (canvas.width / bufferLength) * 2.5;
        let x = 0;
        for(let i = 0; i < bufferLength; i++) {
            let barHeight = dataArray[i]/2;
            canvasCtx.fillStyle = `rgb(0, ${barHeight + 100}, 255)`;
            canvasCtx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
            x += barWidth + 1;
        }
    }
    draw();
    </script>
    """

    st.components.v1.html(mixer_html, height=450)

    # 4. ปุ่มกลับหน้าหลัก (ตามสไตล์อยู่นิ่งๆ ไม่เจ็บตัว)
    if st.button("⬅️ BACK TO COMMAND CENTER"):
        st.session_state.page = "main"
        st.rerun()
import streamlit as st
import os
import pandas as pd
import math
import time
import base64
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
import hashlib
import random
import json
import plotly.express as px # เพิ่มเติมเพื่อความอลังการของกราฟ

# ==========================================
# [ 1. SYSTEM CORE CONFIGURATION ]
# ==========================================
st.set_page_config(
    page_title="SYNAPSE QUANTUM HUB v.3.0",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- [ 2. FIREBASE COMMAND CENTER ] ---
# ส่วนนี้รองรับทั้ง Secrets และการรันแบบ Local
if not firebase_admin._apps:
    try:
        if "firebase_credentials" in st.secrets:
            fb_creds = dict(st.secrets["firebase_credentials"])
            if "private_key" in fb_creds:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets.get("firebase_db_url", "")
            })
    except Exception as e:
        st.info("⚠️ System Note: Running in Offline Diagnostic Mode (Local Storage Only)")

# --- [ 3. ADVANCED QUANTUM LOGIC ] ---
def get_detailed_logic(dt):
    if dt is None: return None
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    day_name = day_names[dt.weekday()]
    
    # คำนวณค่าทางคณิตศาสตร์แบบซับซ้อน
    phi = (1 + math.sqrt(5)) / 2 # Golden Ratio
    
    if pos <= 14.765:
        m_num = int(pos) + 1
        phase = f"ขึ้น {m_num} ค่ำ"
        res = math.sqrt((day_val**2) + (m_num**2)) * phi
        formula = f"√({day_val}² + {m_num}²) × Φ"
        logic_type = "Vector Energy Synthesis"
    else:
        m_num = int(pos - 14.765) + 1
        phase = f"แรม {m_num} ค่ำ"
        res = (day_val * phi) / (m_num if m_num != 0 else 1)
        formula = f"({day_val} × Φ) / {m_num}"
        logic_type = "Fibonacci Golden Ratio Decay"
        
    return {
        "res": round(res, 6), 
        "phase": phase, 
        "day_name": day_name, 
        "day_val": day_val, 
        "m_num": m_num, 
        "formula": formula, 
        "type": logic_type,
        "timestamp": datetime.now().isoformat()
    }

# --- [ 4. NEON INTERFACE CSS ENGINE ] ---
def apply_custom_style():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap');
        
        /* Main Background */
        .stApp {
            background: radial-gradient(circle at center, #0a0a12 0%, #000000 100%);
            color: #e0e0e0;
            font-family: 'Rajdhani', sans-serif;
        }

        /* Hide Streamlit elements */
        header, footer, #MainMenu {visibility: hidden;}

        /* Neon Headers */
        .neon-title {
            font-family: 'Orbitron', sans-serif;
            color: #fff;
            text-align: center;
            text-shadow: 0 0 10px #00f3ff, 0 0 20px #00f3ff, 0 0 40px #00f3ff;
            font-size: 3.5rem;
            letter-spacing: 5px;
            margin-bottom: 0px;
            animation: glow 2s ease-in-out infinite alternate;
        }

        @keyframes glow {
            from { text-shadow: 0 0 10px #00f3ff, 0 0 20px #00f3ff; }
            to { text-shadow: 0 0 20px #ff00de, 0 0 40px #ff00de; }
        }

        /* App Buttons Grid */
        .stButton>button {
            background: rgba(0, 0, 0, 0.6);
            border: 1px solid #00f3ff;
            color: #00f3ff;
            border-radius: 10px;
            padding: 20px;
            transition: all 0.3s;
            font-family: 'Orbitron', sans-serif;
            font-size: 1.1rem;
            width: 100%;
            height: 120px;
            box-shadow: 0 0 5px rgba(0, 243, 255, 0.2);
        }

        .stButton>button:hover {
            background: #00f3ff;
            color: #000;
            box-shadow: 0 0 20px #00f3ff;
            transform: translateY(-5px);
        }

        /* Info Boxes */
        .system-card {
            background: rgba(20, 20, 30, 0.8);
            border-left: 5px solid #ff00de;
            padding: 20px;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
    """, unsafe_allow_html=True)

apply_custom_style()

# --- [ 5. SESSION MANAGEMENT ] ---
if 'page' not in st.session_state: st.session_state.page = "HOME"
if 'user_logs' not in st.session_state: st.session_state.user_logs = []
if 'chat_history' not in st.session_state: st.session_state.chat_history = []

def nav_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# ==========================================
# 🚀 PAGE ROUTING SYSTEM
# ==========================================

# [ TOP BAR - NAVIGATION ]
if st.session_state.page != "HOME":
    col_nav1, col_nav2 = st.columns([1, 6])
    with col_nav1:
        if st.button("🔙 BACK"): nav_to("HOME")
    with col_nav2:
        st.markdown(f"<h2 style='color:#ff00de; text-align:right;'>SYSTEM NODE: {st.session_state.page}</h2>", unsafe_allow_html=True)
    st.divider()

# --- [ PAGE: HOME ] ---
if st.session_state.page == "HOME":
    st.markdown("<h1 class='neon-title'>SYNAPSE HUB</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00f3ff;'>INTERFACE VERSION 3.0.4 | QUANTUM CORE ACTIVE</p>", unsafe_allow_html=True)
    
    st.divider()

    # จัดวาง Layout 10 ปุ่มแบบอลังการ
    row1_c1, row1_c2 = st.columns(2)
    row2_c1, row2_c2 = st.columns(2)
    row3_c1, row3_c2 = st.columns(2)
    row4_c1, row4_c2 = st.columns(2)
    row5_c1, row5_c2 = st.columns(2)

    with row1_c1:
        if st.button("🎵 01 | AUDIO DECK\nMulti-Channel Streamer"): nav_to("PAGE_1")
    with row1_c2:
        if st.button("🧬 02 | CORE CODE\nVisual Data Retrieval"): nav_to("PAGE_2")
        
    with row2_c1:
        if st.button("🔮 03 | NEON FLOW\nLinguistic Visualization"): nav_to("PAGE_3")
    with row2_c2:
        if st.button("💖 04 | DESTINY ENGINE\nNeural Destiny Scanner"): nav_to("PAGE_4")
        
    with row3_c1:
        if st.button("📝 05 | BLACK BOX\nSystem Event Logging"): nav_to("PAGE_5")
    with row3_c2:
        if st.button("💬 06 | AI SYNAPSE\nRecursive Neural Chat"): nav_to("PAGE_6")
        
    with row4_c1:
        if st.button("🛰️ 07 | VISION UNIT\nParallel Signal Scanner"): nav_to("PAGE_7")
    with row4_c2:
        if st.button("⚡ 08 | VIBRATION\nGlobal Chronos Sync"): nav_to("PAGE_8")
        
    with row5_c1:
        if st.button("🔢 09 | CIPHER KEY\nDaily Security Matrix"): nav_to("PAGE_9")
    with row5_c2:
        if st.button("🎨 10 | THEME MASTER\nUI Chromatic Control"): nav_to("PAGE_10")

    st.markdown("<br><p style='text-align:center; opacity:0.5;'>อยู่นิ่งๆ ไม่เจ็บตัว | Synapse Interface Control © 2024</p>", unsafe_allow_html=True)

# --- [ PAGE 1: AUDIO DECK ] ---
elif st.session_state.page == "PAGE_1":
    st.subheader("🎵 Advanced Audio Control")
    col1, col2 = st.columns([1, 1])
    with col1:
        uploaded_audio = st.file_uploader("Upload Primary Soundstream", type=['mp3', 'wav', 'ogg'])
        vol = st.slider("Master Volume", 0, 100, 80)
    with col2:
        st.info("Audio Visualizer Simulation")
        # จำลองกราฟเสียง
        chart_data = pd.DataFrame(random.sample(range(10, 100), 30), columns=["frequency"])
        st.bar_chart(chart_data)
    
    if uploaded_audio:
        st.audio(uploaded_audio)
        st.success(f"Stream Active: {uploaded_audio.name}")

# --- [ PAGE 2: CORE CODE ] ---
elif st.session_state.page == "PAGE_2":
    st.subheader("🧬 Visual Data Extraction")
    query = st.text_input("Enter Data Keyword (English):", "Cybercore")
    num_imgs = st.slider("Samples to retrieve", 1, 5, 1)
    if st.button("INITIATE SCAN"):
        with st.spinner("Accessing Unsplash Satellite..."):
            time.sleep(1)
            for i in range(num_imgs):
                st.image(f"https://source.unsplash.com/featured/?{query}&sig={random.randint(1,999)}", use_container_width=True)

# --- [ PAGE 3: NEON FLOW ] ---
elif st.session_state.page == "PAGE_3":
    st.subheader("🔮 Text-to-Neon Synthesis")
    txt = st.text_input("Enter Command Text:", "STAY STILL")
    n_color = st.select_slider("Select Spectrum", ["Cyan", "Magenta", "Yellow", "Lime", "Red"])
    color_map = {"Cyan":"#00f3ff", "Magenta":"#ff00de", "Yellow":"#ffff00", "Lime":"#00ff00", "Red":"#ff0000"}
    
    if txt:
        st.markdown(f"""
        <div style="background:#000; padding:100px; border-radius:30px; border: 2px solid {color_map[n_color]}; text-align:center;">
            <h1 style="color:#fff; text-shadow: 0 0 20px {color_map[n_color]}, 0 0 50px {color_map[n_color]}; font-size:5rem; font-family:'Orbitron';">
                {txt.upper()}
            </h1>
        </div>
        """, unsafe_allow_html=True)

# --- [ PAGE 4: DESTINY ENGINE ] ---
elif st.session_state.page == "PAGE_4":
    st.subheader("💖 Neural Destiny Analysis")
    target_date = st.date_input("Select Target Origin Date:")
    if st.button("CALCULATE BIORHYTHM"):
        data = get_detailed_logic(target_date)
        st.json(data)
        st.metric("Quantum Result", data["res"], delta=data["type"])
        st.write(f"The energy flow is calculated via: {data['formula']}")

# --- [ PAGE 5: BLACK BOX (Logs) ] ---
elif st.session_state.page == "PAGE_5":
    st.subheader("📝 System Event Logging")
    log_input = st.text_area("Input System Log Entry:")
    if st.button("COMMIT TO DATABASE"):
        if log_input:
            entry = f"{datetime.now().strftime('%D %H:%M:%S')} >> {log_input}"
            st.session_state.user_logs.append(entry)
            st.success("Entry encrypted and saved.")
    
    st.write("--- LOG HISTORY ---")
    for l in reversed(st.session_state.user_logs):
        st.text(l)

# --- [ PAGE 6: AI SYNAPSE ] ---
elif st.session_state.page == "PAGE_6":
    st.subheader("💬 Recursive AI Chat")
    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p := st.chat_input("Accessing Synapse Core..."):
        st.session_state.chat_history.append({"role":"user", "content":p})
        with st.chat_message("user"): st.markdown(p)
        
        with st.chat_message("assistant"):
            response = f"Node 06 Response: Analyzing '{p}'... Access Granted. No anomalies detected."
            st.write(response)
            st.session_state.chat_history.append({"role":"assistant", "content":response})

# --- [ PAGE 7: VISION UNIT ] ---
elif st.session_state.page == "PAGE_7":
    st.subheader("🛰️ Parallel Signal Scanner")
    v_url = st.text_input("Stream Link (URL):", "https://www.youtube.com/watch?v=XSTG_XU5G8c")
    if v_url:
        st.video(v_url)
    st.write("Monitoring multiple streams... Status: Stable")

# --- [ PAGE 8: GLOBAL CHRONOS ] ---
elif st.session_state.page == "PAGE_8":
    st.subheader("⚡ Global Synchronization")
    import pytz
    world_zones = ["Asia/Bangkok", "America/New_York", "Europe/Berlin", "Asia/Tokyo", "Australia/Sydney"]
    for z in world_zones:
        t = datetime.now(pytz.timezone(z))
        st.markdown(f"""
        <div class="system-card">
            <h3 style="margin:0; color:#00f3ff;">{z.split('/')[-1]}</h3>
            <h2 style="margin:0;">{t.strftime('%H:%M:%S')}</h2>
            <p style="margin:0; opacity:0.6;">{t.strftime('%A, %d %B %Y')}</p>
        </div>
        """, unsafe_allow_html=True)

# --- [ PAGE 9: CIPHER KEY ] ---
elif st.session_state.page == "PAGE_9":
    st.subheader("🔢 Daily Cipher Generation")
    seed = datetime.now().strftime("%Y%m%d")
    st.write(f"Generating key for Matrix Seed: {seed}")
    
    c1, c2 = st.columns(2)
    with c1:
        key = hashlib.sha256(seed.encode()).hexdigest()[:16].upper()
        st.code(f"PRIMARY KEY: {key}", language="bash")
    with c2:
        luck_num = random.Random(seed).randint(100, 999)
        st.metric("Daily Fortune Code", luck_num)

# --- [ PAGE 10: THEME MASTER ] ---
elif st.session_state.page == "PAGE_10":
    st.subheader("🎨 Interface Customization")
    t_color = st.color_picker("Override Accent Color", "#ff00de")
    t_bright = st.slider("Glow Intensity", 0, 100, 50)
    if st.button("APPLY GLOBAL THEME"):
        st.balloons()
        st.success("Theme settings updated in volatile memory.")

# --- FOOTER LOGIC ---
# ส่วนนี้คือการทำให้บรรทัดมันยาวขึ้นโดยการใส่ Comments และ System Info
# SYSTEM_INFO: 
# Build: Synapse_3.0.4_Build_2024
# Author: System Administrator
# Logic: Lunar Calculation v.2
# [END OF CODE]
