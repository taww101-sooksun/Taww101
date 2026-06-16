import streamlit as st
import os 
import time
import base64
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from folium.features import DivIcon
from streamlit_folium import st_folium
from math import radians, cos, sin, asin, sqrt
import pytz
from timezonefinder import TimezoneFinder
from datetime import datetime, date, timedelta
import math
import random
import hashlib
import pandas as pd
from streamlit_js_eval import get_geolocation 

# --- [ จุดแก้บั๊ก 1: ตั้งค่าหน้าจอต้องอยู่บนสุด ห้ามซ้ำซ้อน ] ---
st.set_page_config(page_title="SYNAPSE HUB", layout="wide")

# --- [ จุดแก้บั๊ก 2: ตัวเชื่อมต่อ Firebase ดึงจาก Streamlit Secrets ] ---
if not firebase_admin._apps:
    try:
        import json
        key_dict = json.loads(st.secrets["textkey"])
        cred = credentials.Certificate(key_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': st.secrets["databaseURL"]
        })
    except Exception as e:
        st.error(f"❌ ระบบเชื่อมต่อฐานข้อมูลขัดข้อง: {e}")
        st.stop()

# 1. ฟังก์ชั่นดึงข้อมูล (สีแดงบนสุด)
def get_base64_data(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except Exception:
        return ""

# 2. ตั้งค่าสีและสถานะเริ่มต้น
if 'main_color' not in st.session_state:
    st.session_state.main_color = "#00f3ff"

if 'sub_color' not in st.session_state:
    st.session_state.sub_color = "#ff00de"

if 'page' not in st.session_state:
    st.session_state.page = "HOME"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ส่วนควบคุมโลโก้
logo_b64 = get_base64_data("logo1.png")

st.markdown(f"""
    <style>
    .global-logo {{
        position: fixed; 
        top: 15px;      
        right: 25px;    
        width: 65px;    
        z-index: 10000; 
        filter: drop-shadow(0 0 10px var(--primary)); 
        animation: pulse 2s infinite alternate; 
    }}
    @keyframes pulse {{ 
        from {{ transform: scale(1); }} 
        to {{ transform: scale(1.1); }} 
    }}
    </style>
    <img src="data:image/png;base64,{logo_b64}" class="global-logo">
""", unsafe_allow_html=True)

# ปรับปรุงโครงสร้าง CSS :root ให้ยืดหยุ่นตามตัวแปร
st.markdown(f"""
    <style>
    :root {{
        --primary: {st.session_state.main_color};
        --secondary: {st.session_state.sub_color};
        --glow: {st.session_state.get('bg_glow', '#00f3ff')};
    }}
    .stButton>button {{
        border: 1px solid var(--primary) !important;
        background: rgba(0,0,0,0.2) !important;
        color: white !important;
        box-shadow: 0 0 5px var(--primary);
    }}
    .stButton>button:hover {{
        border-color: var(--secondary) !important;
        box-shadow: 0 0 20px var(--secondary) !important;
    }}
    .neon-text {{
        color: var(--primary) !important;
        text-shadow: 0 0 10px var(--primary), 0 0 20px var(--secondary) !important;
    }}
    .stApp {{
        border: 2px solid var(--primary);
        transition: all 0.8s ease;
        background: #000;
        color: #00f2fe;
    }}
    header, footer, #MainMenu {{visibility: hidden;}}
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 0rem;
    }}
    </style>
""", unsafe_allow_html=True)

# 4. SIDEBAR: ระบบเปลี่ยนสีและเพลงพื้นหลัง
with st.sidebar:
    st.markdown("<h2 class='neon-text'>CONTROL PANEL</h2>", unsafe_allow_html=True)
    with st.expander("🎨 THEME COLORS"):
        st.session_state.main_color = st.color_picker("Main Neon", st.session_state.main_color)
        st.session_state.sub_color = st.color_picker("Sub Neon", st.session_state.sub_color)
    
    all_songs = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
    selected_bg = st.selectbox("🎵 Background Music", ["Off"] + all_songs)
    
    if selected_bg != "Off":
        bg_audio_data = get_base64_data(selected_bg)
        st.markdown(f"""
            <audio id="bgAudio" autoplay loop controls style="width: 100%; height: 40px; margin-top:10px;">
                <source src="data:audio/mp3;base64,{bg_audio_data}" type="audio/mp3">
            </audio>
        """, unsafe_allow_html=True)

# --- 5. หัวใจคำนวณ: ระบบถอดรหัส Lunar ---
def get_detailed_logic(dt):
    if dt is None: return None
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    day_name = day_names[dt.weekday()]

    if pos <= 14.765:
        m_num = int(pos) + 1
        phase = f"ขึ้น {m_num} ค่ำ"
        res = math.sqrt((day_val**2) + (m_num**2))
        formula, logic_type = f"√({day_val}² + {m_num}²)", "Vector Energy"
    else:
        m_num = int(pos - 14.765) + 1
        phase = f"แรม {m_num} ค่ำ"
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula, logic_type = f"({day_val} × 1.618) / {m_num}", "Golden Ratio"

    return {"res": round(res, 4), "phase": phase, "day_name": day_name, "day_val": day_val, "m_num": m_num, "formula": formula, "type": logic_type}

# --- ส่วนหน้าจอลงชื่อเข้าใช้ (Login / Register) ---
if not st.session_state.get('logged_in', False):
    st.markdown("<h2 style='text-align:center; color:#00f3ff; font-family:Orbitron;'>REGISTER AGENT</h2>", unsafe_allow_html=True)
    with st.container():
        new_user = st.text_input("ENTER AGENT NAME", placeholder="เช่น ต๊ะ101, บาส").strip()
        if st.button("ACTIVATE SYSTEM", use_container_width=True):
            if new_user:
                user_check = db.reference(f'users/{new_user}').get()
                if not user_check:
                    db.reference(f'users/{new_user}').set({
                        'created_at': time.time(),
                        'lat': 13.7367,
                        'lon': 100.5231
                    })
                st.session_state.user = new_user        
                st.session_state.logged_in = True     
                st.session_state.page = "HOME"         
                st.success(f"WELCOME AGENT: {new_user}")
                st.balloons()
                time.sleep(1.5)
                st.rerun()
            else:
                st.warning("กรุณาใส่ชื่อ AGENT ของคุณก่อน!")
    st.stop() 

# ปุ่มย้อนกลับหน้าหลัก
if st.session_state.page != "HOME":
    if st.button("⬅️ กลับหน้าหลัก"):
        st.session_state.page = "HOME"
        st.rerun()

# --- [ หน้าแรก: ศูนย์รวมเมนู ] ---
if st.session_state.page == "HOME":
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        if os.path.exists("logo1.png"):
            st.image("logo1.png", use_container_width=True)
        else:
            st.markdown("<h1 class='neon-text'>SYNAPSE</h1>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center;'>ศูนย์ควบคุมระบบ: เลือกฟังก์ชันการใช้งาน</h3>", unsafe_allow_html=True)
    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🎵 1. MUSIC PLAYER\nฟังเพลง MP3 จากคลังข้อมูล", use_container_width=True):
            st.session_state.page = "1"; st.rerun()
        if st.button("💬 2. CHAT & RADAR\nระบบสื่อสารและพิกัดดาวเทียม", use_container_width=True):
            st.session_state.page = "2"; st.rerun()
        if st.button("🧬 3. QUANTUM ANALYZER\nรวมระบบคำนวณพิกัดดวงชะตา", use_container_width=True):
            st.session_state.page = "3"; st.rerun()
        if st.button("📝 4. SYSTEM LOG\nบันทึกข้อมูลคลาวด์", use_container_width=True):
            st.session_state.page = "9"; st.rerun()
    with c2:
        if st.button("🔊 5. VIBRATION UNIT\nตรวจวัดคลื่นเสียงและแรงสั่น", use_container_width=True):
            st.session_state.page = "6"; st.rerun()
        if st.button("💖 6. DESTINY CHECK\nตรวจดวงชะตาคู่ขนานตัวอักษร", use_container_width=True):
            st.session_state.page = "7"; st.rerun()
        if st.button("🔢 7. DAILY CODE\nถอดรหัสความปลอดภัยประจำวัน", use_container_width=True):
            st.session_state.page = "8"; st.rerun()
        if st.button("🎨 8. COLOR MASTER\nปรับแต่งธีมสีออร่าระบบ", use_container_width=True):
            st.session_state.page = "10"; st.rerun()

# --- ห้องที่ 1: MUSIC PLAYER ---
elif st.session_state.page == "1":
    st.markdown("<h2 class='neon-text'>🎧 SYNAPSE DJ STATION V.3</h2>", unsafe_allow_html=True)
    all_songs = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
    col_sel_a, col_sel_b = st.columns(2)
    with col_sel_a: song_a = st.selectbox("💿 DECK A", ["-- Select --"] + all_songs, key="sa")
    with col_sel_b: song_b = st.selectbox("💿 DECK B", ["-- Select --"] + all_songs, key="sb")
    data_a = get_base64_data(song_a) if song_a != "-- Select --" else ""
    data_b = get_base64_data(song_b) if song_b != "-- Select --" else ""

    mixer_html = f"""
    <div style="background: #000; border: 2px solid #333; border-radius: 20px; padding: 15px; font-family: 'Orbitron';">
        <marquee style="color: #00f3ff; margin-bottom: 10px;"> Now Playing Deck A: {song_a} | Deck B: {song_b} </marquee>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <div style="border: 1px solid #00f3ff; padding: 10px; border-radius: 15px; text-align: center;">
                <div style="display: flex; justify-content: space-between; font-size: 10px; color: #00f3ff;"><span id="curA">00:00</span><span id="remA">-00:00</span></div>
                <canvas id="canvasA" style="width: 100%; height: 50px; background: #111; margin: 5px 0;"></canvas>
                <input type="range" id="volA" min="0" max="1" step="0.01" value="0.7" style="width: 100%; accent-color: #00f3ff;">
                <div style="margin-top: 10px;"><button onclick="play('A')" style="background:#00f3ff; border:none; padding:5px 15px; border-radius:5px;">PLAY</button><button onclick="pause('A')" style="background:none; border:1px solid #00f3ff; color:#00f3ff; padding:5px 15px; border-radius:5px;">PAUSE</button></div>
            </div>
            <div style="border: 1px solid #ff00de; padding: 10px; border-radius: 15px; text-align: center;">
                <div style="display: flex; justify-content: space-between; font-size: 10px; color: #ff00de;"><span id="curB">00:00</span><span id="remB">-00:00</span></div>
                <canvas id="canvasB" style="width: 100%; height: 50px; background: #111; margin: 5px 0;"></canvas>
                <input type="range" id="volB" min="0" max="1" step="0.01" value="0.7" style="width: 100%; accent-color: #ff00de;">
                <div style="margin-top: 10px;"><button onclick="play('B')" style="background:#ff00de; border:none; padding:5px 15px; border-radius:5px; color:white;">PLAY</button><button onclick="pause('B')" style="background:none; border:1px solid #ff00de; color:#ff00de; padding:5px 15px; border-radius:5px;">PAUSE</button></div>
            </div>
        </div>
        <button onclick="autoFade()" style="width:100%; margin-top:15px; background: linear-gradient(90deg, #00f3ff, #ff00de); border:none; padding:10px; border-radius:10px; color:white; font-weight:bold;">🔄 10s AUTO CROSSFADE</button>
        <audio id="audioA" src="data:audio/mp3;base64,{data_a}" crossorigin="anonymous"></audio>
        <audio id="audioB" src="data:audio/mp3;base64,{data_b}" crossorigin="anonymous"></audio>
        <script>
            const audA = document.getElementById('audioA'); const audB = document.getElementById('audioB'); const ctx = new (window.AudioContext || window.webkitAudioContext)();
            function setupVisualizer(audioElem, canvasID, color) {{
                const src = ctx.createMediaElementSource(audioElem); const analyzer = ctx.createAnalyser(); const canvas = document.getElementById(canvasID); const canvasCtx = canvas.getContext("2d");
                src.connect(analyzer); analyzer.connect(ctx.destination); analyzer.fftSize = 512;
                const bufferLength = analyzer.frequencyBinCount; const dataArray = new Uint8Array(bufferLength);
                function draw() {{ requestAnimationFrame(draw); analyzer.getByteFrequencyData(dataArray); canvasCtx.fillStyle = "#111"; canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
                    const barWidth = (canvas.width / bufferLength) * 2.5; let barHeight; let x = 0;
                    for(let i = 0; i < bufferLength; i++) {{ barHeight = dataArray[i] / 2; canvasCtx.fillStyle = color; canvasCtx.fillRect(x, canvas.height - barHeight, barWidth, barHeight); x += barWidth + 1; }}
                }} draw();
            }}
            let setupA = false, setupB = false;
            function play(deck) {{ if (ctx.state === 'suspended') ctx.resume(); if (deck === 'A') {{ if(!setupA) {{ setupVisualizer(audA, 'canvasA', '#00f3ff'); setupA = true; }} audA.play(); }} else {{ if(!setupB) {{ setupVisualizer(audB, 'canvasB', '#ff00de'); setupB = true; }} audB.play(); }} }}
            function pause(deck) {{ deck === 'A' ? audA.pause() : audB.pause(); }}
            function updateTime(aud, curID, remID) {{ aud.ontimeupdate = () => {{ let cM = Math.floor(aud.currentTime/60), cS = Math.floor(aud.currentTime%60); document.getElementById(curID).innerText = (cM<10?'0'+cM:cM)+":"+(cS<10?'0'+cS:cS); let r = aud.duration - aud.currentTime; if(!isNaN(r)) {{ let rM = Math.floor(r/60), rS = Math.floor(r%60); document.getElementById(remID).innerText = "-"+(rM<10?'0'+rM:rM)+":"+(rS<10?'0'+rS:rS); }} }}; }}
            updateTime(audA, 'curA', 'remA'); updateTime(audB, 'curB', 'remB');
            function autoFade() {{ let steps = 100, interval = 100, volStep = 1/steps; audB.volume = 0; audB.play(); if(!setupB) {{ setupVisualizer(audB, 'canvasB', '#ff00de'); setupB = true; }} let count = 0; let fade = setInterval(() => {{ if (count >= steps) {{ clearInterval(fade); audA.pause(); }} else {{ if (audA.volume > volStep) audA.volume -= volStep; if (audB.volume < 1-volStep) audB.volume += volStep; count++; }} }}, interval); }}
        </script>
    </div>
    """
    components.html(mixer_html, height=550)

# --- ห้องที่ 2: CHAT & RADAR ---
elif st.session_state.page == "2":
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=8000, key="synapse_update")
    st.markdown("<h2 style='text-align:center; color:#00f3ff; font-family:Orbitron;'>🛰️ TACTICAL RADAR & PRIVATE CHAT</h2>", unsafe_allow_html=True)
    
    loc = get_geolocation()
    my_lat, my_lon = 13.7367, 100.5231
    if loc and 'coords' in loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']

    m = folium.Map(location=[my_lat, my_lon], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr='Google Satellite')
    folium.Marker([my_lat, my_lon], icon=folium.Icon(color='red', icon='star'), tooltip="YOU").add_to(m)

    try:
        users_ref = db.reference('users').get()
        if users_ref:
            for uid, data in users_ref.items():
                if uid != st.session_state.user and 'lat' in data:
                    folium.Marker([data['lat'], data['lon']], icon=folium.Icon(color='blue'), tooltip=f"AGENT: {uid}").add_to(m)
    except: pass

    st_folium(m, width="100%", height=300)

    if st.button("📡 BROADCAST POSITION", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.toast("พิกัดถูกส่งแล้ว!")

    st.write("---")
    st.markdown("<h4 style='color:#ff00de; font-family:Orbitron;'>🔐 PRIVATE SECURE CHAT</h4>", unsafe_allow_html=True)

    try:
        all_users = db.reference('users').get()
        if all_users:
            friends = [u for u in all_users.keys() if u != st.session_state.user]
            target_agent = st.selectbox("🎯 เลือก AGENT ที่ต้องการติดต่อ:", friends)
            if target_agent:
                room_id = "_".join(sorted([st.session_state.user, target_agent]))
                chat_ref = db.reference(f'private_messages/{room_id}')

                with st.form("private_chat_form", clear_on_submit=True):
                    msg = st.text_input(f"TO: {target_agent}", placeholder="พิมพ์ข้อความที่นี่...")
                    if st.form_submit_button("SEND SIGNAL"):
                        if msg:
                            chat_ref.push({'sender': st.session_state.user, 'text': msg, 'ts': time.time()})
                            st.rerun()

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
                                    <b style="color:{color}; font-size:0.75rem;">{m_data['sender']}</b><br><span style="color:white;">{m_data['text']}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
    except Exception as e: st.error(f"ระบบขัดข้อง: {e}")

# --- [ จุดสำคัญ: รวมห้องคำนวณทั้งหมดไว้ที่นี่ (แอปหมายเลข 3) ] ---
elif st.session_state.page == "3":
    st.markdown("<h2 class='neon-text' style='text-align:center;'>🧬 QUANTUM ANALYZER UNIT</h2>", unsafe_allow_html=True)
    
    # แยกส่วนการทำงานออกเป็น 3 หัวข้อย่อยในหน้าเดียวผ่านสัญชาตญาณความจริง
    t1, t2, t3 = st.tabs(["💎 สแกนรหัสส่วนตัว", "🤝 ตรวจค่าความต่าง (Gap)", "📅 ตารางพิกัดอนาคต 180 วัน"])

    with t1:
        st.subheader("พิกัดประจำตัว (Individual Scan)")
        dob = st.date_input("📅 ระบุวันเกิดเพื่อถอดรหัส", min_value=date(1960, 1, 1), max_value=date(2026, 12, 31), key="dob_solo")
        if dob:
            d = get_detailed_logic(dob)
            col1, col2 = st.columns([1, 2])
            with col1: st.metric("YOUR CODE", d['res'])
            with col2: st.info(f"พิกัด: วัน{d['day_name']} | {d['phase']}")
            
            st.markdown(f"""
            <div style="background: rgba(0,243,255,0.05); padding:15px; border-left:3px solid #00f3ff; border-radius:5px;">
                <h4>📝 ที่มาของรหัสประจำตัว (The Truth)</h4>
                <ul>
                    <li><b>เลขฐานวัน ({d['day_val']}):</b> ลำดับวันในสัปดาห์</li>
                    <li><b>เลขจันทรคติ ({d['m_num']}):</b> ระยะห่างจริงทางดาราศาสตร์จากจุดเดือนดับ</li>
                    <li><b>สมการคณิตศาสตร์ที่คำนวณจริง:</b> <code>{d['formula']}</code> ({d['type']})</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    with t2:
        st.subheader("พิกัดคู่ขนาน (Gap Analysis)")
        c1, c2 = st.columns(2)
        with c1: dob1 = st.date_input("วันเกิด AGENT 1", min_value=date(1960,1,1), max_value=date(2026,12,31), key="g1")
        with c2: dob2 = st.date_input("วันเกิด AGENT 2", min_value=date(1960,1,1), max_value=date(2026,12,31), key="g2")
        
        if dob1 and dob2:
            d1 = get_detailed_logic(dob1)
            d2 = get_detailed_logic(dob2)
            gap = abs(d1['res'] - d2['res'])
            st.write(f"### ค่าความต่างพิกัด (Gap): `{gap:.4f}`")
            
            if gap < 0.5: st.success("💎 สถานะ: พิกัดเพชร (รหัสแฝดบรรจบ/โอกาสร่วม)")
            elif 3.8 <= gap <= 4.2: st.warning("🌀 สถานะ: พิกัดธรรม (แรงสะท้อนดึงดูดพลังงานภายนอก)")
            elif gap > 10.0: st.info("🪞 สถานะ: พิกัดกระจก (พลังงานเป็นอิสระต่อกันอย่างสมบูรณ์)")

            st.markdown(f"""
            <div style="background: rgba(255,0,222,0.05); padding:10px; border-radius:5px; font-size:0.85rem; color:#ccc;">
                <b>สูตรการคำนวณทางกายภาพ:</b> <code>|รหัส {d1['res']} - รหัส {d2['res']}| = {gap:.4f}</code> ไม่มีการสุ่มตัวเลขมั่วเดาใจ
            </div>
            """, unsafe_allow_html=True)

    with t3:
        st.subheader("พิกัดอนาคต (180 Days Timeline)")
        user_dob = st.date_input("กรอกวันเกิดเพื่อสแกนไทม์ไลน์", min_value=date(1960,1,1), max_value=date(2026,12,31), key="dob_timeline")
        if user_dob:
            my_code = get_detailed_logic(user_dob)['res']
            st.write(f"🧬 กำลังตรวจสอบการกระทบความถี่ของรหัสคุณ **{my_code}** กับคลื่นพลังงานดาราศาสตร์ล่วงหน้า 180 วัน")
            
            future_results = []
            for i in range(180):
                target_date = date.today() + timedelta(days=i)
                d = get_detailed_logic(target_date)
                gap = abs(d['res'] - my_code)
                
                status, symbol = "อิสระ", "⚪"
                if gap < 0.5: status, symbol = "💎 พิกัดเพชร (บรรจบ/เริ่มสิ่งใหม่)", "💎"
                elif 3.8 <= gap <= 4.2: status, symbol = "🌀 พิกัดธรรม (สะท้อน/เรื่องไม่คาดฝัน)", "🌀"
                elif gap > 10.0: status, symbol = "🪞 พิกัดกระจก (แยกตัว/อิสระ)", "🪞"
                
                if status != "อิสระ":
                    future_results.append({
                        "วันที่": target_date.strftime('%d/%m/%Y'),
                        "วันประจำสัปดาห์": d['day_name'],
                        "ประเภทพิกัด": status,
                        "ค่า Gap": round(gap, 4),
                        "สัญลักษณ์": symbol
                    })
            if future_results:
                st.dataframe(pd.DataFrame(future_results), use_container_width=True, hide_index=True)
            else:
                st.info("ไม่พบจุดตัดพิกัดพิเศษในช่วง 180 วันนี้ (กระแสพลังงานไหลเวียนปกติ)")

# --- ห้องที่ 5: VIBRATION UNIT ---
elif st.session_state.page == "6":
    st.markdown("<h2 style='text-align:center; color:#FFD700; font-family:Orbitron;'>⚡ SYNAPSE VIBRATION & BIO UNIT</h2>", unsafe_allow_html=True)
    tab_sonic, tab_motion, tab_bio = st.tabs(["🎙️ SONIC SCAN", "📳 MOTION SCAN", "🩸 BIO-SCAN"])
    
    with tab_sonic:
        st.subheader("🎙️ REAL-TIME SONIC ANALYZER")
        audio_js = """
        <div style="background-color: #111; color: #FFD700; padding: 20px; border: 2px solid #FFD700; border-radius: 15px; text-align: center; font-family: monospace;">
            <div style="display: flex; justify-content: space-around;">
                <div><small>ความดัง</small><h1 id="db_val" style="font-size: 40px; color:#0f0;">0</h1><small>เดซิเบล (dB)</small></div>
                <div><small>ความถี่</small><h1 id="hz_val" style="font-size: 40px; color:#00ffff;">0</h1><small>เฮิรตซ์ (Hz)</small></div>
            </div>
            <p id="audio_status" style="margin-top:10px; color:#888;">🔴 รอสัญญาณเสียง...</p>
        </div>
        <script>
            async function startAudio() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    const analyser = audioCtx.createAnalyser();
                    const source = audioCtx.createMediaStreamSource(stream); source.connect(analyser); analyser.fftSize = 2048;
                    const dataArray = new Uint8Array(analyser.frequencyBinCount);
                    function update() { analyser.getByteFrequencyData(dataArray); let sum = 0, maxVal = 0, maxIdx = 0;
                        for (let i = 0; i < dataArray.length; i++) { sum += dataArray[i]; if (dataArray[i] > maxVal) { maxVal = dataArray[i]; maxIdx = i; } }
                        let db = Math.round(sum / dataArray.length * 2); let hz = Math.round(maxIdx * audioCtx.sampleRate / analyser.fftSize);
                        document.getElementById('db_val').innerText = db; document.getElementById('hz_val').innerText = hz;
                        document.getElementById('audio_status').innerText = "🟢 ตรวจจับคลื่นเสียงจริง"; requestAnimationFrame(update);
                    } update();
                } catch (e) { document.getElementById('audio_status').innerText = "❌ เข้าถึงไมค์ไม่ได้"; }
            } startAudio();
        </script>
        """
        components.html(audio_js, height=250)

    with tab_motion:
        st.subheader("📳 MOTION & VIBRATION SENSOR")
        motion_js = """
        <div style="background-color: #111; color: #FFD700; padding: 20px; border: 2px solid #FFD700; border-radius: 15px; text-align: center; font-family: monospace;">
            <small>แรงสั่นสะเทือนรวม (Magnitude)</small><h1 id="mag_val" style="font-size: 50px; color: #0f0;">1.000</h1><p>G-Force</p>
        </div>
        <script>
            window.addEventListener('devicemotion', (e) => { const acc = e.accelerationIncludingGravity; if (!acc) return;
                let magnitude = Math.sqrt(acc.x**2 + acc.y**2 + acc.z**2) / 9.80665;
                document.getElementById('mag_val').innerText = magnitude.toFixed(3);
            });
        </script>
        """
        components.html(motion_js, height=250)
        
    with tab_bio:
        st.subheader("🩸 REAL-TIME BIO-DATA SCANNER")
        bio_js = """
        <div style="background-color: #111; color: #FFD700; padding: 15px; border: 2px solid #FFD700; border-radius: 15px; font-family: monospace; text-align:center;">
            <h3>Fingerprint Bio-Scanner Simulated Terminal</h3>
            <p style='color:#f00;'>[ ระบบพร้อมรับสัญญาณปลายนิ้วผ่านหน้าเลนส์กล้อง ]</p>
        </div>
        """
        components.html(bio_js, height=200)

# --- ห้องที่ 6: DESTINY CHECK ---
elif st.session_state.page == "7":
    st.markdown("<h2 style='text-align:center; color:#ff00de; font-family:Orbitron;'>💖 DESTINY CHECK (DIMENSION 4)</h2>", unsafe_allow_html=True)
    name1 = st.text_input("ชื่อ AGENT 1:", placeholder="ระบุชื่อคนที่ 1")
    name2 = st.text_input("ชื่อ AGENT 2:", placeholder="ระบุชื่อคนที่ 2")
    if st.button("⚡ เดินเครื่องสแกนความถี่", use_container_width=True):
        if name1 and name2:
            score1 = sum(ord(char) for char in name1)
            score2 = sum(ord(char) for char in name2)
            gap = abs(score1 - score2)
            match_percent = 100 - (gap % 100)
            st.divider()
            st.metric("ระดับความสอดคล้องของคลื่นความถี่ (Synchronization)", f"{match_percent} %")

# --- ห้องที่ 7: DAILY CODE ---
elif st.session_state.page == "8":
    st.markdown("<h2 style='text-align:center; color:#00f3ff; font-family:Orbitron;'>🔢 DAILY SECURITY CODE</h2>", unsafe_allow_html=True)
    today_str = date.today().strftime("%Y-%m-%d")
    current_agent = st.session_state.get('user', 'Guest_Agent')
    raw_data = f"{today_str}_{current_agent}_SYNAPSE"
    
    try:
        hash_object = hashlib.sha256(raw_data.encode('utf-8')).hexdigest()
        daily_4_digit = str(int(hash_object[:4], 16))[-4:].zfill(4)
        daily_6_digit = str(int(hash_object[4:10], 16))[-6:].zfill(6)
        
        col1, col2 = st.columns(2)
        with col1: st.markdown(f"<div style='text-align:center; border: 2px solid #00f3ff; padding: 20px; border-radius: 15px;'><small style='color:#00f3ff;'>ACCESS PIN</small><h1>{daily_4_digit}</h1></div>", unsafe_allow_html=True)
        with col2: st.markdown(f"<div style='text-align:center; border: 2px solid #ff00de; padding: 20px; border-radius: 15px;'><small style='color:#ff00de;'>MASTER KEY</small><h1>{daily_6_digit}</h1></div>", unsafe_allow_html=True)
    except Exception as e: st.error(f"การถอดรหัสผิดพลาด: {e}")

# --- ห้องที่ 4 เดิม: SYSTEM LOG ---
elif st.session_state.page == "9":
    st.markdown("<h2 style='text-align:center; color:#50C878; font-family:Orbitron;'>📝 SYNAPSE MEMORY LOG</h2>", unsafe_allow_html=True)
    with st.form("log_form", clear_on_submit=True):
        log_entry = st.text_area("✍️ ข้อความบันทึก:", placeholder="พิมพ์สิ่งที่คุณต้องการจดจำ...")
        if st.form_submit_button("💾 SAVE TO CLOUD") and log_entry:
            try:
                db.reference(f'system_logs/{st.session_state.user}').push({'text': log_entry, 'timestamp': time.time(), 'datetime': str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))})
                st.success("บันทึกข้อมูลเรียบร้อย!")
            except Exception as e: st.error(f"ฐานข้อมูลขัดข้อง: {e}")

# --- ห้องที่ 8 เดิม: COLOR MASTER ---
elif st.session_state.page == "10":
    st.markdown("<h2 class='neon-text'>🎨 MULTI-COLOR INTERFACE</h2>", unsafe_allow_html=True)
    st.session_state.main_color = st.color_picker("🔵 สีหลัก (Primary Neon)", st.session_state.main_color)
    st.session_state.sub_color = st.color_picker("🔴 สีรอง (Secondary Neon)", st.session_state.sub_color)
    if st.button("🔥 APPLY ALL DIMENSIONS", use_container_width=True): st.rerun()

st.write("---")
st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | Synapse Command Center Engine v3.0")
