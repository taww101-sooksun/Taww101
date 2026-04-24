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
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from streamlit_autorefresh import st_autorefresh
import hashlib

# ==========================================
# 1. INITIAL CONFIG (ตั้งค่าระบบพื้นฐาน)
# ==========================================
st.set_page_config(page_title="SYNAPSE ADVANCED HUB", layout="wide", initial_sidebar_state="expanded")

# --- ฟังก์ชันดึงข้อมูล Base64 (หัวใจของ Media) ---
def get_base64_data(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except Exception:
        return ""

# --- ตรวจสอบสถานะสีและหน้าจอ ---
if 'main_color' not in st.session_state:
    st.session_state.main_color = "#00f3ff"
if 'sub_color' not in st.session_state:
    st.session_state.sub_color = "#ff00de"
if 'page' not in st.session_state:
    st.session_state.page = "HOME"
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ==========================================
# 2. GLOBAL STYLING & LOGO (คุมทุกห้อง)
# ==========================================
logo_b64 = get_base64_data("logo1.png")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    :root {{
        --primary: {st.session_state.main_color};
        --secondary: {st.session_state.sub_color};
    }}

    /* พื้นหลังและตัวอักษรหลัก */
    .stApp {{
        background-color: #000000;
        color: #ffffff;
        font-family: 'Orbitron', sans-serif;
    }}

    /* โลโก้คงที่ทุกหน้า */
    .global-logo {{
        position: fixed;
        top: 15px;
        right: 25px;
        width: 70px;
        z-index: 10000;
        filter: drop-shadow(0 0 10px var(--primary));
        animation: pulse-glow 2s infinite alternate;
    }}
    @keyframes pulse-glow {{
        from {{ filter: drop-shadow(0 0 5px var(--primary)); transform: scale(1); }}
        to {{ filter: drop-shadow(0 0 20px var(--secondary)); transform: scale(1.05); }}
    }}

    /* สไตล์ตัวหนังสือวิ่งและนีออน */
    .neon-title {{
        text-align: center;
        color: #fff;
        text-shadow: 0 0 10px var(--primary), 0 0 20px var(--secondary);
        margin-bottom: 20px;
    }}
    
    /* ซ่อนแถบเดิมของ Streamlit */
    header, footer, #MainMenu {{visibility: hidden;}}
    
    /* ปุ่มกดย้อนกลับ */
    .back-btn {{
        background: none;
        border: 1px solid var(--primary);
        color: var(--primary);
        padding: 5px 15px;
        border-radius: 10px;
        cursor: pointer;
    }}
    </style>
    <img src="data:image/png;base64,{logo_b64}" class="global-logo">
""", unsafe_allow_html=True)

# ==========================================
# 3. SIDEBAR ENGINE (ตัวควบคุมเพลงต่อเนื่องและสี)
# ==========================================
with st.sidebar:
    st.markdown(f"<h2 class='neon-title'>SYSTEM CONTROL</h2>", unsafe_allow_html=True)
    
    # --- ส่วนที่ 1: เพลงพื้นหลัง (เล่นต่อเนื่องไม่ดับ) ---
    st.markdown("### 📻 CONTINUOUS AUDIO")
    all_files = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
    bg_selection = st.selectbox("เลือกเพลงหลัก (Global Music)", ["OFF"] + all_files)
    
    if bg_selection != "OFF":
        bg_audio_b64 = get_base64_data(bg_selection)
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); padding: 10px; border-radius: 15px; border: 1px solid var(--primary);">
                <small style="color: var(--primary);">Now Playing: {bg_selection}</small>
                <audio id="bgPlayer" autoplay loop controls style="width: 100%; height: 35px; margin-top: 5px;">
                    <source src="data:audio/mp3;base64,{bg_audio_b64}" type="audio/mp3">
                </audio>
            </div>
        """, unsafe_allow_html=True)

    # --- ส่วนที่ 2: ปรับแต่งธีมสี ---
    st.markdown("---")
    with st.expander("🎨 THEME CUSTOMIZER (GLOBAL)"):
        st.session_state.main_color = st.color_picker("Neon Color 1", st.session_state.main_color)
        st.session_state.sub_color = st.color_picker("Neon Color 2", st.session_state.sub_color)
        if st.button("SET DEFAULT"):
            st.session_state.main_color = "#00f3ff"
            st.session_state.sub_color = "#ff00de"
            st.rerun()

    # --- ส่วนที่ 3: Logout ---
    if st.session_state.logged_in:
        st.markdown("---")
        if st.button("🔴 TERMINATE SESSION"):
            st.session_state.logged_in = False
            st.rerun()

# ==========================================
# 4. LOGIN SYSTEM (หน้าลงทะเบียน)
# ==========================================
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h1 class='neon-title'>AGENT REGISTRATION</h1>", unsafe_allow_html=True)
        agent_name = st.text_input("ENTER CODE NAME", placeholder="เช่น ต๊ะ101").strip()
        
        if st.button("ACTIVATE SYSTEM", use_container_width=True):
            if agent_name:
                st.session_state.user = agent_name
                st.session_state.logged_in = True
                st.session_state.page = "HOME"
                st.balloons()
                st.rerun()
            else:
                st.error("กรุณาระบุรหัส AGENT")
    st.stop()

# ==========================================
# 5. NAVIGATION LOGIC (ปุ่มย้อนกลับ)
# ==========================================
if st.session_state.page != "HOME":
    if st.button("⬅️ RETURN TO HUB"):
        st.session_state.page = "HOME"
        st.rerun()

# ==========================================
# 6. MAIN CONTENT (ห้องการใช้งาน 1-10)
# ==========================================

# --- [ หน้าแรก: HUB ศูนย์รวม ] ---
if st.session_state.page == "HOME":
    st.markdown("<h1 class='neon-title'>SYNAPSE COMMAND CENTER</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>Welcome, Agent <b>{st.session_state.user}</b></p>", unsafe_allow_html=True)
    
    # การแบ่ง Grid ปุ่มกด
    colA, colB = st.columns(2)
    with colA:
        if st.button("🎵 1. DJ STATION (ADVANCED)", use_container_width=True): st.session_state.page = "1"; st.rerun()
        if st.button("💬 2. SECURE RADAR CHAT", use_container_width=True): st.session_state.page = "2"; st.rerun()
        if st.button("🧬 3. LUNAR DECODER", use_container_width=True): st.session_state.page = "3"; st.rerun()
        if st.button("🛰️ 4. PARALLEL SCANNER", use_container_width=True): st.session_state.page = "4"; st.rerun()
        if st.button("🔮 5. DESTINY TIMELINE", use_container_width=True): st.session_state.page = "5"; st.rerun()
    with colB:
        if st.button("⚡ 6. VIBRATION SENSOR", use_container_width=True): st.session_state.page = "6"; st.rerun()
        if st.button("💖 7. DESTINY CHECK", use_container_width=True): st.session_state.page = "7"; st.rerun()
        if st.button("🔢 8. DAILY SECURITY CODE", use_container_width=True): st.session_state.page = "8"; st.rerun()
        if st.button("📝 9. SYSTEM MEMORY LOG", use_container_width=True): st.session_state.page = "9"; st.rerun()
        if st.button("🎨 10. INTERFACE MASTER", use_container_width=True): st.session_state.page = "10"; st.rerun()

# --- [ ห้องที่ 1: DJ STATION (512Hz Visualizer) ] ---
elif st.session_state.page == "1":
    st.markdown("<h2 class='neon-title'>🎧 DUAL-DECK AUDIO UNIT</h2>", unsafe_allow_html=True)
    
    deck_a_col, deck_b_col = st.columns(2)
    with deck_a_col:
        sel_a = st.selectbox("DECK A TRACK", ["-- Select --"] + all_files, key="da")
    with deck_b_col:
        sel_b = st.selectbox("DECK B TRACK", ["-- Select --"] + all_files, key="db")

    b64_a = get_base64_data(sel_a) if sel_a != "-- Select --" else ""
    b64_b = get_base64_data(sel_b) if sel_b != "-- Select --" else ""

    mixer_html = f"""
    <div style="background: #000; border: 2px solid #333; border-radius: 20px; padding: 20px;">
        <marquee style="color: var(--primary); font-size: 12px; margin-bottom: 15px;"> 
            NOW MONITORING: DECK A [{sel_a}] --- DECK B [{sel_b}] --- UNIT: SYNAPSE-X1
        </marquee>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div style="border: 1px solid var(--primary); padding: 15px; border-radius: 15px; text-align: center;">
                <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--primary);">
                    <span id="curA">00:00</span><span id="remA">-00:00</span>
                </div>
                <canvas id="canvasA" style="width: 100%; height: 70px; background: #050505; margin: 10px 0; border-radius: 5px;"></canvas>
                <input type="range" id="volA" min="0" max="1" step="0.01" value="0.7" style="width: 100%; accent-color: var(--primary);">
                <div style="margin-top: 15px; display: flex; justify-content: center; gap: 10px;">
                    <button onclick="playDeck('A')" style="background: var(--primary); border:none; padding:8px 20px; border-radius:5px; font-weight:bold; cursor:pointer;">PLAY</button>
                    <button onclick="pauseDeck('A')" style="background:none; border:1px solid var(--primary); color:var(--primary); padding:8px 20px; border-radius:5px; cursor:pointer;">PAUSE</button>
                </div>
            </div>
            <div style="border: 1px solid var(--secondary); padding: 15px; border-radius: 15px; text-align: center;">
                <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--secondary);">
                    <span id="curB">00:00</span><span id="remB">-00:00</span>
                </div>
                <canvas id="canvasB" style="width: 100%; height: 70px; background: #050505; margin: 10px 0; border-radius: 5px;"></canvas>
                <input type="range" id="volB" min="0" max="1" step="0.01" value="0.7" style="width: 100%; accent-color: var(--secondary);">
                <div style="margin-top: 15px; display: flex; justify-content: center; gap: 10px;">
                    <button onclick="playDeck('B')" style="background: var(--secondary); border:none; padding:8px 20px; border-radius:5px; font-weight:bold; cursor:pointer; color: white;">PLAY</button>
                    <button onclick="pauseDeck('B')" style="background:none; border:1px solid var(--secondary); color:var(--secondary); padding:8px 20px; border-radius:5px; cursor:pointer;">PAUSE</button>
                </div>
            </div>
        </div>

        <button onclick="autoFade()" style="width:100%; margin-top:20px; background: linear-gradient(90deg, var(--primary), var(--secondary)); border:none; padding:15px; border-radius:15px; color:white; font-weight:bold; cursor:pointer; font-family:'Orbitron';">
            🔄 START 10s AUTO-CROSSFADE
        </button>

        <audio id="audioA" src="data:audio/mp3;base64,{b64_a}"></audio>
        <audio id="audioB" src="data:audio/mp3;base64,{b64_b}"></audio>

        <script>
            const audA = document.getElementById('audioA');
            const audB = document.getElementById('audioB');
            let ctx = null;

            function setupVisual(audio, canvasId, color) {{
                if(!ctx) ctx = new (window.AudioContext || window.webkitAudioContext)();
                const src = ctx.createMediaElementSource(audio);
                const analyzer = ctx.createAnalyser();
                const canvas = document.getElementById(canvasId);
                const cCtx = canvas.getContext("2d");

                src.connect(analyzer);
                analyzer.connect(ctx.destination);
                analyzer.fftSize = 512;

                const buffer = analyzer.frequencyBinCount;
                const data = new Uint8Array(buffer);

                function render() {{
                    requestAnimationFrame(render);
                    analyzer.getByteFrequencyData(data);
                    cCtx.clearRect(0, 0, canvas.width, canvas.height);
                    const barW = (canvas.width / buffer) * 2;
                    let x = 0;
                    for(let i=0; i<buffer; i++) {{
                        let h = data[i] / 2.5;
                        cCtx.fillStyle = color;
                        cCtx.fillRect(x, canvas.height - h, barW, h);
                        x += barW + 1;
                    }}
                }}
                render();
            }}

            let isSetA = false, isSetB = false;
            function playDeck(d) {{
                if(ctx && ctx.state === 'suspended') ctx.resume();
                if(d === 'A') {{ if(!isSetA){{setupVisual(audA, 'canvasA', '{st.session_state.main_color}'); isSetA=true;}} audA.play(); }}
                else {{ if(!isSetB){{setupVisual(audB, 'canvasB', '{st.session_state.sub_color}'); isSetB=true;}} audB.play(); }}
            }}
            function pauseDeck(d) {{ d === 'A' ? audA.pause() : audB.pause(); }}

            function updateTime(aud, curI, remI) {{
                aud.ontimeupdate = () => {{
                    let cM = Math.floor(aud.currentTime/60), cS = Math.floor(aud.currentTime%60);
                    document.getElementById(curI).innerText = (cM<10?'0'+cM:cM)+":"+(cS<10?'0'+cS:cS);
                    let r = aud.duration - aud.currentTime;
                    if(!isNaN(r)) {{
                        let rM = Math.floor(r/60), rS = Math.floor(r%60);
                        document.getElementById(remI).innerText = "-"+(rM<10?'0'+rM:rM)+":"+(rS<10?'0'+rS:rS);
                    }}
                }};
            }}
            updateTime(audA, 'curA', 'remA'); updateTime(audB, 'curB', 'remB');

            function autoFade() {{
                let steps = 100, volStep = 1/steps;
                audB.volume = 0; audB.play();
                let count = 0;
                let fade = setInterval(() => {{
                    if(count >= steps) {{ clearInterval(fade); audA.pause(); }}
                    else {{
                        if(audA.volume > volStep) audA.volume -= volStep;
                        if(audB.volume < 1-volStep) audB.volume += volStep;
                        count++;
                    }}
                }}, 100);
            }}
        </script>
    </div>
    """
    components.html(mixer_html, height=580)
    st.info("💡 หมายเหตุ: กราฟ Visualizer จะเริ่มทำงานเมื่อคุณเลือกเพลงและกด PLAY ครั้งแรก")

# --- [ ห้องอื่นๆ (ใส่ตรรกะเดิมของคุณต๊ะลงไปได้เลย) ] ---
elif st.session_state.page == "2":
    st.markdown("<h2 class='neon-title'>🛰️ TACTICAL RADAR CHAT</h2>", unsafe_allow_html=True)
    st.write("ระบบนี้กำลังเชื่อมต่อฐานข้อมูลความปลอดภัย...")
    # (วางโค้ดหน้า 2 เดิมที่นี่...)

# ... (ไปจนถึงห้อง 10) ...

# ==========================================
# 7. FOOTER (ปิดท้ายระบบ)
# ==========================================
st.markdown("---")
st.caption(f"SYNAPSE OS v.4.0 | Current Agent: {st.session_state.user} | Multi-Room Synchronization Enabled")
