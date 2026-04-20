import streamlit as st
import os
import datetime
import pandas as pd
import math
import time
import base64
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
import hashlib
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import base64
# --- ส่วนบนสุดของไฟล์ (Initial State) ---
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#39FF14"  # กำหนดสีเริ่มต้นเป็นสีเขียว Matrix

def get_base64(file_path):
    """ฟังก์ชันสำหรับแปลงไฟล์เพลงเป็น Base64 เพื่อให้เล่นบน HTML5 Player ได้"""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    except Exception as e:
        st.error(f"❌ ไม่สามารถอ่านไฟล์ได้: {e}")
        return None

# --- 1. SETUP & ลบติ่ง (อยู่นิ่งๆ ไม่เจ็บตัว) ---
st.set_page_config(page_title="SYNAPSE HUB", layout="wide")

def setup_ui():
    st.markdown("""
        <style>
        /* ลบ Header, Footer และเมนูเดิมของ Streamlit */
        header, footer, #MainMenu {visibility: hidden;}
        .stApp { background: #000; color: #00f2fe; }
        
        /* สไตล์ปุ่มเมนู */
        .stButton>button {
            border-radius: 15px;
            border: 1px solid #00f2fe;
            background: rgba(0, 242, 254, 0.1);
            color: white;
            height: 100px;
            font-size: 18px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background: #00f2fe;
            color: #000;
            box-shadow: 0 0 20px #00f2fe;
        }
        
        /* ตัวหนังสือวิ้ง */
        .neon-text {
            text-align: center;
            color: #fff;
            text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

setup_ui()

# --- 2. การจัดการหน้าจอ (Navigation) ---
if 'page' not in st.session_state:
    st.session_state.page = "HOME"

# ฟังก์ชันย้อนกลับ
if st.session_state.page != "HOME":
    if st.button("⬅️ กลับหน้าหลัก"):
        st.session_state.page = "HOME"
        st.rerun()

# --- 3. เนื้อหาแต่ละหน้า ---

# [ หน้าแรก: ศูนย์รวม 10 แอป ]
if st.session_state.page == "HOME":
    # วาง LOGO แทนที่ติ่ง
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        if os.path.exists("logo1.png"):
            st.image("logo1.png", use_container_width=True)
        else:
            st.markdown("<h1 class='neon-text'>SYNAPSE</h1>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center;'>ศูนย์ควบคุมระบบ: เลือกฟังก์ชันการใช้งาน</h3>", unsafe_allow_html=True)
    st.divider()

    # สร้าง Grid 10 แอป (แบ่งเป็น 2 คอลัมน์)
    c1, c2 = st.columns(2)

    with c1:
        if st.button("🎵 1. MUSIC PLAYER\nฟังเพลง MP3 จากคลังข้อมูล", use_container_width=True):
            st.session_state.page = "1"; st.rerun()
        st.caption("ความสามารถ: เล่นไฟล์เสียง 1.mp3 และระบบควบคุมเสียงผ่านหน้าเว็บ")

        if st.button("🖼️ 3. IMAGE SEARCH\nค้นหาภาพจากดาวเทียม", use_container_width=True):
            st.session_state.page = "3"; st.rerun()
        st.caption("ความสามารถ: ดึงรูปภาพจากคลัง Unsplash ตามคำค้นหาที่ต้องการ")

        if st.button("✨ 5. NEON GENERATOR\nสร้างตัวอักษรเรืองแสง", use_container_width=True):
            st.session_state.page = "5"; st.rerun()
        st.caption("ความสามารถ: แปลงข้อความธรรมดาให้เป็นศิลปะนีออนวิ้งๆ")

        if st.button("💖 7. DESTINY CHECK\nตรวจดวงชะตาคู่ขนาน", use_container_width=True):
            st.session_state.page = "7"; st.rerun()
        st.caption("ความสามารถ: วิเคราะห์ดวงชะตาในมิติที่ 4 ผ่านระบบฐานข้อมูลชื่อ")

        if st.button("📝 9. SYSTEM LOG\nบันทึกข้อมูลการใช้งาน", use_container_width=True):
            st.session_state.page = "9"; st.rerun()
        st.caption("ความสามารถ: จดบันทึกข้อความและเหตุการณ์สำคัญลงในหน่วยความจำ")

    with c2:
        if st.button("💬 2. CHAT SYSTEM\nระบบสื่อสารอัจฉริยะ", use_container_width=True):
            st.session_state.page = "2"; st.rerun()
        st.caption("ความสามารถ: โต้ตอบผ่านข้อความกับระบบจัดการ AI")

        if st.button("🎬 4. VIDEO HUB\nศูนย์รวมวิดีโอวงจรปิด", use_container_width=True):
            st.session_state.page = "4"; st.rerun()
        st.caption("ความสามารถ: เชื่อมต่อและฉายภาพวิดีโอจาก YouTube หรือ Link ตรง")

        if st.button("🌍 6. WORLD CLOCK\nเวลาโลกแบบเรียลไทม์", use_container_width=True):
            st.session_state.page = "6"; st.rerun()
        st.caption("ความสามารถ: ตรวจสอบเวลาปัจจุบันในโซนต่างๆ ทั่วโลก")

        if st.button("🔢 8. DAILY CODE\nรหัสลับประจำวัน", use_container_width=True):
            st.session_state.page = "8"; st.rerun()
        st.caption("ความสามารถ: เจนรหัสตัวเลขนำโชคและรหัสรักษาความปลอดภัยรายวัน")

        if st.button("🎨 10. COLOR MASTER\nปรับแต่งธีมสีระบบ", use_container_width=True):
            st.session_state.page = "10"; st.rerun()
        st.caption("ความสามารถ: เปลี่ยนสีสันของ Interface เพื่อความสวยงามตามใจชอบ")

# --- ส่วนนี้คือที่วางโค้ดของแต่ละแอปย่อย (ทำเหมือนเดิม) ---
# --- [ ห้องที่ 1: SYNAPSE OMNI-MIXER (COMMAND CENTER) ] ---
elif st.session_state.page == "1":
    import base64
    import os

    # 1. ฟังก์ชันช่วยสำหรับการแสดงผล
    def get_base64_img(file_path):
        try:
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except: return ""

    logo_b64 = get_base64_img("logo1.png")

    # 2. CSS ปรับแต่งหน้าจอ (Logo ตรงกลาง + สไตล์ Neon)
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
        
        header, footer, #MainMenu {{visibility: hidden;}}
        .stApp {{ background-color: #000000; }}

        /* สร้าง Logo กระพริบตรงกลางหน้า */
        .logo-center {{
            display: block;
            margin: 0 auto;
            width: 100px; height: 100px;
            background-image: url("data:image/png;base64,{logo_b64}");
            background-size: contain; background-repeat: no-repeat;
            filter: drop-shadow(0 0 10px #ff00de);
            animation: logo-pulsing 2s infinite alternate;
            z-index: 99;
        }}
        @keyframes logo-pulsing {{
            from {{ filter: drop-shadow(0 0 5px #ff00de); transform: scale(1); }}
            to {{ filter: drop-shadow(0 0 20px #00f3ff); transform: scale(1.1); }}
        }}

        .neon-title-main {{
            font-family: 'Orbitron', sans-serif;
            color: #fff; text-align: center;
            text-shadow: 0 0 10px #ff00de, 0 0 20px #00f3ff;
            font-size: 1.8rem; margin: 15px 0;
        }}
        </style>
        <div class="logo-center"></div>
        <h1 class="neon-title-main">SYNAPSE COMMAND CENTER</h1>
    """, unsafe_allow_html=True)

    # 3. ส่วนของ Mixer HTML/JS (Deck A & B)
    # ผมรวมโค้ด Mixer ที่มี Visualizer และ Crossfade มาไว้ตรงนี้
    mixer_html = f"""
    <div id="mixer-container" style="background: rgba(10,10,10,0.9); border: 2px solid #333; border-radius: 25px; padding: 20px; font-family: sans-serif;">
        <canvas id="v-main" style="width: 100%; height: 120px; background: #000; border-radius: 15px; border: 1px solid #ff00de;"></canvas>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px;">
            <div style="padding: 15px; border-left: 4px solid #ff00de; background: rgba(255,0,222,0.05); border-radius: 10px;">
                <small style="color: #ff00de; font-weight: bold;">DECK A</small>
                <div id="nameA" style="color: #fff; font-size: 12px; margin: 5px 0; overflow: hidden;">ยังไม่ได้เลือกเพลง...</div>
                <input type="file" id="inA" accept="audio/*" style="display:none" onchange="loadA(this.files[0])">
                <button onclick="document.getElementById('inA').click()" style="background: #ff00de; color: white; border: none; padding: 5px 10px; border-radius: 5px; font-size: 10px; cursor: pointer;">SELECT A</button>
                <div style="height: 4px; background: #222; margin-top: 10px; border-radius: 2px;"><div id="barA" style="height: 100%; width: 0%; background: #ff00de;"></div></div>
            </div>

            <div style="padding: 15px; border-left: 4px solid #00f3ff; background: rgba(0,243,255,0.05); border-radius: 10px;">
                <small style="color: #00f3ff; font-weight: bold;">DECK B</small>
                <div id="nameB" style="color: #fff; font-size: 12px; margin: 5px 0; overflow: hidden;">ยังไม่ได้เลือกเพลง...</div>
                <input type="file" id="inB" accept="audio/*" style="display:none" onchange="loadB(this.files[0])">
                <button onclick="document.getElementById('inB').click()" style="background: #00f3ff; color: black; border: none; padding: 5px 10px; border-radius: 5px; font-size: 10px; cursor: pointer;">SELECT B</button>
                <div style="height: 4px; background: #222; margin-top: 10px; border-radius: 2px;"><div id="barB" style="height: 100%; width: 0%; background: #00f3ff;"></div></div>
            </div>
        </div>

        <div style="display: grid; grid-cols: 2; gap: 10px; margin-top: 20px;">
            <button onclick="playAll()" style="width: 100%; padding: 12px; background: none; border: 2px solid #ff0055; color: #ff0055; font-weight: bold; border-radius: 15px; cursor: pointer;">⚡ START MIX</button>
            <button onclick="fade()" style="width: 100%; padding: 12px; background: none; border: 2px solid #00ffcc; color: #00ffcc; font-weight: bold; border-radius: 15px; cursor: pointer; margin-top: 10px;">🔄 CROSSFADE (5s)</button>
        </div>
    </div>

    <script>
        let ctx, ana, sA, sB, gA, gB, isP = false, cur = 'A', data;
        function init() {{ if(!ctx) {{ ctx = new (window.AudioContext || window.webkitAudioContext)(); ana = ctx.createAnalyser(); ana.fftSize = 128; data = new Uint8Array(ana.frequencyBinCount); loop(); }} }}
        function loop() {{
            requestAnimationFrame(loop); if(!ana) return; ana.getByteFrequencyData(data);
            const can = document.getElementById('v-main'); const c = can.getContext('2d');
            c.fillStyle = 'rgba(0,0,0,0.2)'; c.fillRect(0,0,can.width,can.height);
            let x = 0; let w = (can.width/data.length)*2;
            for(let i=0; i<data.length; i++) {{
                let h = (data[i]/255)*can.height;
                c.fillStyle = 'hsl('+(180+i*5)+', 100%, 50%)';
                c.fillRect(x, can.height-h, w-1, h); x += w;
            }}
            updateProgress();
        }}
        async function loadA(f) {{ init(); document.getElementById('nameA').innerText = f.name; sA = await ctx.decodeAudioData(await f.arrayBuffer()); }}
        async function loadB(f) {{ init(); document.getElementById('nameB').innerText = f.name; sB = await ctx.decodeAudioData(await f.arrayBuffer()); }}
        function playAll() {{
            if(!sA || !sB || isP) return;
            srcA = ctx.createBufferSource(); srcA.buffer = sA; gA = ctx.createGain();
            srcA.connect(gA).connect(ana).connect(ctx.destination);
            srcB = ctx.createBufferSource(); srcB.buffer = sB; gB = ctx.createGain(); gB.gain.value = 0;
            srcB.connect(gB).connect(ana).connect(ctx.destination);
            srcA.start(0); srcB.start(0); isP = true;
        }}
        function fade() {{
            let now = ctx.currentTime;
            if(cur === 'A') {{ gA.gain.linearRampToValueAtTime(0, now+5); gB.gain.linearRampToValueAtTime(1, now+5); cur = 'B'; }}
            else {{ gB.gain.linearRampToValueAtTime(0, now+5); gA.gain.linearRampToValueAtTime(1, now+5); cur = 'A'; }}
        }}
        function updateProgress() {{
             // อัปเดต Progress Bar แบบง่าย (จำลอง)
             if(isP) {{
                document.getElementById('barA').style.width = cur === 'A' ? '100%' : '0%';
                document.getElementById('barB').style.width = cur === 'B' ? '100%' : '0%';
             }}
        }}
    </script>
    """
    st.components.v1.html(mixer_html, height=520)

    # 4. ส่วนคลังเพลง (Global Playlist)
    st.write("---")
    st.markdown("<h4 style='color:#00f3ff; font-family:Orbitron; text-align:center;'>📂 GLOBAL DATABASE</h4>", unsafe_allow_html=True)
    all_songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if all_songs:
        with st.expander("คลิกเพื่อเลือกเล่นเพลงในคลัง (52+ เพลง)"):
            for s in all_songs:
                if st.button(f"🎵 {s}", use_container_width=True):
                    # ฟังเพลงเดี่ยวๆ ผ่าน Streamlit Audio
                    st.audio(s)
    
    st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | Synapse Studio v.1")


# (เพิ่ม elif ไปจนครบหน้า 10 ตามโครงเดิมได้เลยครับ...)
