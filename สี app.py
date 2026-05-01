import streamlit as st
import os 
import base64
import math
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation 

# ==========================================
# 0. CONFIG & INVISIBLE UI
# ==========================================
st.set_page_config(page_title="SYNAPSE OS V4", layout="wide", initial_sidebar_state="expanded")

def apply_ui_logic():
    primary = st.session_state.get('theme_color', "#39FF14")
    bg = st.session_state.get('bg_color', "#000000")
    st.markdown(f"""
        <style>
        #MainMenu, footer, header {{visibility: hidden;}}
        .stApp {{ background: {bg}; color: white; font-family: 'Orbitron', sans-serif; }}
        .neon-card {{
            border: 1px solid {primary}55;
            padding: 20px;
            border-radius: 15px;
            background: rgba(0,0,0,0.4);
            box-shadow: 0 0 15px {primary}22;
            margin-bottom: 20px;
        }}
        .stTabs [data-baseweb="tab-list"] {{ background: #0a0a0a; border-radius: 10px; border: 1px solid {primary}33; }}
        .stTabs [data-baseweb="tab"] {{ color: #888; }}
        .stTabs [aria-selected="true"] {{ color: {primary} !important; border-bottom: 2px solid {primary} !important; }}
        </style>
    """, unsafe_allow_html=True)

def branding():
    if os.path.exists("logo1.png"):
        st.sidebar.image("logo1.png", width=100)
    st.sidebar.title("SYNAPSE")
    st.sidebar.caption("'อยู่นิ่งๆ ไม่เจ็บตัว'")

# ==========================================
# 1. LOGIC ENGINE (หัวใจของความจริง)
# ==========================================
def calculate_logic(dt):
    ref = date(1900, 1, 1)
    diff = (dt - ref).days
    lunar = (diff - 0.5) % 29.530589
    day_val = dt.weekday() + 1
    is_waxing = lunar <= 14.765
    m_num = int(lunar) + 1 if is_waxing else int(lunar - 14.765) + 1
    
    if is_waxing:
        res = math.sqrt((day_val**2) + (m_num**2))
        formula, tech_desc = f"√({day_val}² + {m_num}²)", "Vector Force (พลังงานผลักดัน)"
    else:
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula, tech_desc = f"({day_val} × 1.618) / {m_num}", "Golden Ratio (พลังงานสมดุล)"
    return {"res": round(res, 4), "phase": f"{'ขึ้น' if is_waxing else 'แรม'} {m_num} ค่ำ", "formula": formula, "tech": tech_desc, "diff": diff}

# ==========================================
# 2. ROOMS (MODULAR)
# ==========================================

def room_music():
    st.markdown("### 🎧 MUSIC STATION")
    st.info("💡 **คำอธิบาย:** ห้องนี้ใช้สำหรับการปรับจูนสภาวะจิตใจผ่านคลื่นความถี่ (Sound Frequency)")
    t1, t2 = st.tabs(["🎵 HOLOGRAPHIC PLAYER", "💿 DECK B"])
    songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    
    with t1:
        if songs:
            s = st.selectbox("เลือกสัญญาณเสียง (Signal Source)", songs)
            with open(s, "rb") as f:
                st.audio(f.read())
            st.markdown(f"<div class='neon-card'>กำลังประมวลผล: {s} <br> <small>สถานะ: เข้ารหัสผ่านคลื่นความถี่ปลอดภัย</small></div>", unsafe_allow_html=True)
        else:
            st.error("ไม่พบไฟล์ .mp3 ในระบบ")
    with t2:
        st.write("โหมด Deck B กำลังรอการซิงค์ข้อมูลไฟล์ลำดับที่สอง...")

def room_comms():
    st.markdown("### 💬 COMM CENTER & GPS")
    st.info("💡 **คำอธิบาย:** ระบบระบุพิกัดตัวตนและช่องทางสื่อสารในเครือข่าย SYNAPSE")
    t1, t2, t3 = st.tabs(["🌐 แชทรวม", "📞 ส่วนตัว", "🛰️ SATELLITE GPS"])
    
    with t3:
        loc = get_geolocation()
        lat, lon = (loc['coords']['latitude'], loc['coords']['longitude']) if loc else (13.75, 100.5)
        m = folium.Map(location=[lat, lon], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google")
        folium.Marker([lat, lon], tooltip="ตำแหน่งของคุณ").add_to(m)
        st_folium(m, width="100%", height=400)
        st.caption(f"พิกัดปัจจุบัน: {lat}, {lon} (อ้างอิงจากดาวเทียม)")

def room_logic():
    st.markdown("### 🧬 LOGIC CALCULATOR")
    st.info("💡 **คำอธิบาย:** ถอดรหัสพิกัดชีวิตจากสถิติจันทรคติและเลขศาสตร์ความจริง (1950-2026)")
    t1, t2, t3 = st.tabs(["🔍 ตรวจรหัสรายวัน", "⚖️ วิเคราะห์คู่ขนาน", "🔮 ไทม์ไลน์ 365 วัน"])
    
    with t1:
        d_input = st.date_input("เลือกวันที่", value=date.today(), min_value=date(1950,1,1), max_value=date(2026,12,31))
        res = calculate_logic(d_input)
        st.markdown(f"""
            <div class='neon-card' style='text-align:center;'>
                <h1 style='color:{st.session_state.theme_color};'>{res['res']}</h1>
                <p>{res['tech']}</p>
                <code style='color:#888;'>ที่มา: {res['formula']}</code>
                <p style='font-size:12px; margin-top:10px;'>คำอธิบาย: ตัวเลขนี้เกิดจากการนำค่าคงที่ของวัน (1-7) มาประมวลผลร่วมกับรอบการโคจรของดวงจันทร์ เพื่อหาค่าแรงดึงดูดที่มีผลต่อสภาวะจิตใจในวันนั้นๆ</p>
            </div>
        """, unsafe_allow_html=True)

def room_sensor():
    st.markdown("### 📟 SENSOR ARRAY")
    st.info("💡 **คำอธิบาย:** ใช้เซนเซอร์จากมือถือของคุณเพื่อวัดค่าความจริงทางกายภาพ (เสียงและการสั่นสะเทือน)")
    
    sensor_js = f"""
    <div style="background:#000; border:1px solid {st.session_state.theme_color}; border-radius:15px; padding:20px; color:white; font-family:monospace;">
        <div id="status" style="color:{st.session_state.theme_color};">READY TO SCAN...</div>
        <hr>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px; text-align:center;">
            <div><small>SONIC LEVEL</small><h2 id="vol">0</h2></div>
            <div><small>MOTION (G)</small><h2 id="acc">1.00</h2></div>
        </div>
        <button id="btn" style="width:100%; padding:10px; background:none; border:1px solid {st.session_state.theme_color}; color:{st.session_state.theme_color}; cursor:pointer; margin-top:10px;">INITIALIZE SENSORS</button>
    </div>
    <script>
        const btn = document.getElementById('btn');
        btn.onclick = async () => {{
            btn.style.display = 'none';
            document.getElementById('status').innerText = 'SCANNING ACTIVE...';
            
            // Audio Sensor
            const stream = await navigator.mediaDevices.getUserMedia({{audio:true}});
            const aCtx = new AudioContext();
            const analyser = aCtx.createAnalyser();
            const source = aCtx.createMediaStreamSource(stream);
            source.connect(analyser);
            const data = new Uint8Array(analyser.frequencyBinCount);
            
            // Motion Sensor
            if(window.DeviceMotionEvent && typeof DeviceMotionEvent.requestPermission === 'function') {{
                await DeviceMotionEvent.requestPermission();
            }}
            
            function update() {{
                requestAnimationFrame(update);
                analyser.getByteFrequencyData(data);
                let sum = data.reduce((a,b)=>a+b, 0);
                document.getElementById('vol').innerText = Math.round(sum/data.length);
            }}
            window.addEventListener('devicemotion', (e) => {{
                let a = e.accelerationIncludingGravity;
                let g = Math.sqrt(a.x**2 + a.y**2 + a.z**2) / 9.8;
                document.getElementById('acc').innerText = g.toFixed(2);
            }});
            update();
        }};
    </script>
    """
    components.html(sensor_js, height=250)
    st.warning("⚠️ โปรดอนุญาตให้แอปเข้าถึงไมโครโฟนและเซนเซอร์ความเคลื่อนไหว")

def room_settings():
    st.markdown("### ⚙️ SYSTEM SETTINGS")
    st.info("💡 **คำอธิบาย:** ปรับแต่งอินเตอร์เฟซให้เข้ากับตัวตนของคุณ (Agent Identity)")
    c1, c2, c3 = st.columns(3)
    st.session_state.theme_color = c1.color_picker("สีนีออนหลัก", st.session_state.theme_color)
    st.session_state.bg_color = c2.color_picker("สีพื้นหลังระบบ", st.session_state.bg_color)
    if st.button("บันทึกการตั้งค่า"): st.rerun()

# ==========================================
# 3. MAIN RUNNER
# ==========================================
def main():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    
    apply_ui_logic()
    branding()
    
    # Sidebar Navigation
    st.sidebar.markdown("---")
    menu = st.sidebar.radio("COMMAND ROOM", ["🎧 MUSIC", "💬 COMMS", "🧬 LOGIC", "📟 SENSOR", "⚙️ SETTINGS"])
    
    if menu == "🎧 MUSIC": room_music()
    elif menu == "💬 COMMS": room_comms()
    elif menu == "🧬 LOGIC": room_logic()
    elif menu == "📟 SENSOR": room_sensor()
    elif menu == "⚙️ SETTINGS": room_settings()

if __name__ == "__main__":
    main()
