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
from streamlit_autorefresh import st_autorefresh


# ==========================================
# 1. วางระบบ INITIALIZATION ไว้บนสุด (ตรงนี้แหล่ะ!)
# ==========================================
def init_system():
    # --- ดักเรื่อง Session State (กัน Error: has no attribute 'user') ---
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if 'user' not in st.session_state:
        st.session_state.user = "Guest_Agent" # ชื่อสำรองกันแอปเด้ง
        
    if 'page' not in st.session_state:
        st.session_state.page = "login" # หน้าเริ่มต้น

    # --- ดักเรื่อง Firebase (กัน Error: default app does not exist) ---
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            # แก้ปัญหาเรื่องขึ้นบรรทัดใหม่ใน Private Key
            if "\\n" in fb_creds["private_key"]:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
                
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_db_url"]
            })
        except Exception as e:
            st.error(f"🛰️ ระบบเชื่อมต่อฐานข้อมูลขัดข้อง: {e}")

# เรียกใช้งานทันทีที่รันไฟล์
init_system()

# ==========================================
# 2. ต่อด้วยระบบ LOGIN (ตัวอย่าง)
# ==========================================
if not st.session_state.logged_in:
    # ใส่โค้ดหน้า Login ของแกตรงนี้ 
    # พอ Login สำเร็จ อย่าลืมตั้งค่า:
    # st.session_state.logged_in = True
    # st.session_state.user = uid
    # st.session_state.page = "1" (หรือหน้าอื่น)
    pass
# --- ส่วนหน้าจอลงชื่อเข้าใช้ (Login / Register) ---
if not st.session_state.get('logged_in', False):
    st.markdown("<h2 style='text-align:center; color:#00f3ff; font-family:Orbitron;'>REGISTER AGENT</h2>", unsafe_allow_html=True)
    
    with st.container():
        # ช่องให้คนใหม่ตั้งชื่อ (ID)
        new_user = st.text_input("ENTER AGENT NAME", placeholder="เช่น ต๊ะ101, บาส, ฯลฯ").strip()
        
        if st.button("ACTIVATE SYSTEM", use_container_width=True):
            if new_user:
                # 1. เช็คใน Firebase ว่าชื่อนี้มีคนใช้หรือยัง
                user_check = db.reference(f'users/{new_user}').get()
                
                if user_check:
                    # ถ้ามีชื่อนี้แล้ว ให้ถือว่าเป็นการ Login (หรือจะใส่รหัสผ่านเพิ่มก็ได้)
                    st.session_state.user = new_user
                    st.session_state.logged_in = True
                    st.success(f"ยินดีต้อนรับกลับ AGENT: {new_user}")
                    time.sleep(1)
                    st.rerun()
                else:
                    # 2. ถ้ายังไม่มีชื่อนี้ ให้ลงทะเบียนใหม่
                    db.reference(f'users/{new_user}').set({
                        'created_at': time.time(),
                        'lat': 13.7367, # พิกัดเริ่มต้น
                        'lon': 100.5231
                    })
                    st.session_state.user = new_user
                    st.session_state.logged_in = True
                    st.balloons() # ฉลอง Agent ใหม่
                    st.success(f"ลงทะเบียน AGENT: {new_user} สำเร็จ!")
                    time.sleep(2)
                    st.rerun()
            else:
                st.warning("กรุณาใส่ชื่อ AGENT ของคุณก่อน!")
    st.stop() # หยุดการทำงานหน้าอื่นไว้จนกว่าจะ Login สำเร็จ

# ==========================================
# 3. ส่วนควบคุมหน้าเพจ (Navigation)
# ==========================================
# ใช้ st.session_state.page ในการสลับหน้า
if st.session_state.page == "1":
    # โค้ดห้องที่ 1 (OMNI-MIXER)
    pass

elif st.session_state.page == "2":
    # โค้ดห้องที่ 2 (TACTICAL RADAR & CHAT)
    pass


def init_system():
    # เช็คว่ามีการเปิดแอป Firebase ไว้หรือยัง
    if not firebase_admin._apps:
        try:
            # ดึงข้อมูลจาก secrets.toml
            fb_creds = dict(st.secrets["firebase_credentials"])
            
            # ตรวจสอบเรื่อง Private Key (ต้องจัดการเรื่องเว้นวรรค \n ให้ถูกต้อง)
            if "\\n" in fb_creds["private_key"]:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
                
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_db_url"]
            })
            # st.success("🛰️ เชื่อมต่อศูนย์บัญชาการสำเร็จ") # เปิดไว้เช็คตอน Test ได้
        except Exception as e:
            st.error(f"🛰️ ระบบเชื่อมต่อฐานข้อมูลขัดข้อง: {e}")
            return False
    return True

# --- ตรงนี้สำคัญ ---
# เรียกใช้ฟังก์ชันก่อนจะเริ่มรันเนื้อหาในหน้าเพจ
if init_system():
    # รันเนื้อหาแอปของแกต่อที่นี่ (เช่น main() หรือการเช็ค page)
    pass

# สั่งให้รีเฟรชตัวเองทุกๆ 5 วินาที (5000 มิลลิวินาที)
# เพื่อไปดึงพิกัดใหม่และแชตใหม่จาก Firebase
count = st_autorefresh(interval=5000, key="datarefresh")

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
elif st.session_state.page == "2":
    from streamlit_autorefresh import st_autorefresh
    
    # --- [ จุดสำคัญ: ระบบ AUTO REFRESH ] ---
    # สั่งให้หน้านี้รีเฟรชตัวเองทุก 8 วินาที เพื่อดึงแชตและพิกัดใหม่
    # (ไม่ตั้งให้เร็วเกินไป เพื่อป้องกันหน้าจอกะพริบจนใช้งานลำบาก)
    st_autorefresh(interval=8000, key="synapse_update")

    st.markdown("<h2 style='text-align:center; color:#00f3ff; font-family:Orbitron;'>🛰️ TACTICAL RADAR & PRIVATE CHAT</h2>", unsafe_allow_html=True)

    # --- ส่วนที่ 1: RADAR (GPS) ---
    from streamlit_js_eval import get_geolocation
    from streamlit_folium import st_folium
    import folium

    loc = get_geolocation()
    my_lat, my_lon = 13.7367, 100.5231 # Default BKK
    if loc and 'coords' in loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']

    # แสดงแผนที่ Satellite
    m = folium.Map(location=[my_lat, my_lon], zoom_start=15, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                   attr='Google Satellite')
    
    folium.Marker([my_lat, my_lon], icon=folium.Icon(color='red', icon='star'), tooltip="YOU").add_to(m)

    # ดึงพิกัดเพื่อนๆ จาก Firebase
    try:
        users_ref = db.reference('users').get()
        if users_ref:
            for uid, data in users_ref.items():
                if uid != st.session_state.user and 'lat' in data:
                    folium.Marker([data['lat'], data['lon']], 
                                 icon=folium.Icon(color='blue'), 
                                 tooltip=f"AGENT: {uid}").add_to(m)
    except: pass

    st_folium(m, width="100%", height=300)

    # ปุ่ม Broadcast พิกัดตัวเอง
    if st.button("📡 BROADCAST POSITION", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.toast("พิกัดถูกส่งแล้ว!")

    st.write("---")

    # --- ส่วนที่ 2: PRIVATE CHAT ---
    st.markdown("<h4 style='color:#ff00de; font-family:Orbitron;'>🔐 PRIVATE SECURE CHAT</h4>", unsafe_allow_html=True)

    try:
        all_users = db.reference('users').get()
        if all_users:
            friends = [u for u in all_users.keys() if u != st.session_state.user]
            target_agent = st.selectbox("🎯 เลือก AGENT ที่ต้องการติดต่อ:", friends)

            if target_agent:
                # สร้าง ID ห้องแบบคู่ (เช่น user1_user2)
                room_id = "_".join(sorted([st.session_state.user, target_agent]))
                chat_ref = db.reference(f'private_messages/{room_id}')

                # ฟอร์มส่งข้อความ
                with st.form("private_chat_form", clear_on_submit=True):
                    msg = st.text_input(f"TO: {target_agent}", placeholder="พิมพ์ข้อความที่นี่...")
                    if st.form_submit_button("SEND SIGNAL"):
                        if msg:
                            chat_ref.push({
                                'sender': st.session_state.user,
                                'text': msg,
                                'ts': time.time()
                            })
                            st.rerun()

                # แสดงผลข้อความล่าสุด 10 ข้อความ
                messages = chat_ref.order_by_child('ts').limit_to_last(10).get()
                if messages:
                    for mid in reversed(list(messages.keys())):
                        m_data = messages[mid]
                        is_me = m_data['sender'] == st.session_state.user
                        align = "right" if is_me else "left"
                        color = "#00f3ff" if is_me else "#ff00de"
                        bg = "rgba(0, 243, 255, 0.15)" if is_me else "rgba(255, 0, 222, 0.15)"
                        
                        st.markdown(f"""
                            <div style="text-align:{align}; margin-bottom:10px;">
                                <div style="display:inline-block; background:{bg}; padding:8px 15px; border-radius:15px; border:1px solid {color};">
                                    <b style="color:{color}; font-size:0.75rem;">{m_data['sender']}</b><br>
                                    <span style="color:white;">{m_data['text']}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("ระบบพร้อมสำหรับการสื่อสารลับ...")
    except Exception as e:
        st.error(f"ระบบขัดข้อง: {e}")

    st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | Tactical Module v.2 (Auto-Update)")


# (เพิ่ม elif ไปจนครบหน้า 10 ตามโครงเดิมได้เลยครับ...)
