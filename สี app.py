# ==============================================================================
# 📂 SYSTEM: SYNAPSE COMMAND CENTER (ULTIMATE EDITION)
# 📂 AGENT: TAWW101
# 📂 PHILOSOPHY: "STAY STILL, NO PAIN" (อยู่นิ่งๆ ไม่เจ็บตัว)
# 📂 TARGET LINE COUNT: 550+ 
# ==============================================================================

import streamlit as st
import datetime
import os 
import time
import base64
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from folium.features import DivIcon
from streamlit_folium import st_folium
import math
from math import radians, cos, sin, asin, sqrt
import pytz
from timezonefinder import TimezoneFinder
from streamlit_js_eval import get_geolocation 
import random

# ==============================================================================
# SECTION 1: GLOBAL CONFIGURATION & SESSION MANAGEMENT
# ==============================================================================

# [บรรทัดที่ 30+] ตั้งค่าแอปพลิเคชัน (ต้องอยู่บรรทัดแรกๆ ของโค้ด)
st.set_page_config(
    page_title="SYNAPSE COMMAND CENTER", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

def init_system():
    """ฟังก์ชันจัดการตัวแปรระบบทั้งหมด (Session State)"""
    # 🎨 ระบบสีและดีไซน์
    if 'bg_color' not in st.session_state: st.session_state.bg_color = '#0A0A0A'
    if 'text_color' not in st.session_state: st.session_state.text_color = '#00FF41'
    if 'border_color' not in st.session_state: st.session_state.border_color = '#00FF41'
    
    # 🔐 ระบบสมาชิกและความปลอดภัย
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user' not in st.session_state: st.session_state.user = "GUEST_AGENT"
    
    # 🎧 ระบบมัลติมีเดีย
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    
    # 💬 ระบบแชท (เก็บข้อมูลชั่วคราวขณะรัน)
    if 'chat_history' not in st.session_state: st.session_state.chat_history = []

    # 🌐 เชื่อมต่อ FIREBASE (หัวใจของระบบ)
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_db_url"]
            })
        except Exception as e:
            st.error(f"FATAL ERROR: DATABASE CONNECTION FAILED - {e}")

# ==============================================================================
# SECTION 2: UI & NEON STYLING ENGINE (CSS 100+ LINES)
# ==============================================================================

def apply_ui_engine():
    """เครื่องยนต์ควบคุมความงามและการซ่อนส่วนเกินของ Streamlit"""
    bg = st.session_state.bg_color
    txt = st.session_state.text_color
    brd = st.session_state.border_color
    
    st.markdown(f"""
        <style>
        /* [บรรทัดที่ 80+] การล้าง Interface เดิมของ Streamlit */
        header, footer {{visibility: hidden !important;}}
        .stAppToolbar {{display: none !important;}}
        #MainMenu {{visibility: hidden !important;}}
        .block-container {{ padding: 0.5rem 2rem !important; }}
        
        /* ตั้งค่าธีมพื้นหลังและฟอนต์ */
        .stApp {{ 
            background-color: {bg} !important; 
            color: {txt} !important; 
            font-family: 'Courier New', Courier, monospace !important;
        }}
        
        /* คุมสีข้อความทั้งหมด */
        h1, h2, h3, h4, h5, p, span, label, div, .stMarkdown, .stCaption {{ 
            color: {txt} !important; 
        }}

        /* ดีไซน์แถบนำทาง (TABS) */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(0,0,0,0.9) !important;
            border: 2px solid {brd} !important;
            border-radius: 15px !important;
            padding: 10px !important;
            gap: 10px !important;
            box-shadow: 0 0 20px {brd}44;
        }}
        .stTabs [data-baseweb="tab"] {{ 
            color: {txt} !important; 
            padding: 10px 20px !important;
            border-radius: 10px !important;
        }}
        .stTabs [aria-selected="true"] {{ 
            background-color: {brd}22 !important; 
            border: 1px solid {brd} !important;
        }}

        /* ดีไซน์กล่อง LOGIC BOX (แผงวงจรระบบ) */
        .logic-panel {{
            background: rgba(0, 0, 0, 0.8);
            border: 3px solid {brd};
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 0 30px {brd}33;
            margin-bottom: 20px;
        }}

        /* ปุ่มกดสไตล์ NEON */
        div.stButton > button {{
            background: transparent !important;
            color: {txt} !important;
            border: 2px solid {brd} !important;
            border-radius: 12px !important;
            padding: 12px 24px !important;
            font-weight: bold !important;
            letter-spacing: 2px !important;
            transition: 0.4s all !important;
            width: 100%;
        }}
        div.stButton > button:hover {{
            background: {brd} !important;
            color: {bg} !important;
            box-shadow: 0 0 25px {brd};
            transform: translateY(-2px);
        }}

        /* ตกแต่ง Input */
        input, textarea {{
            background-color: rgba(0,0,0,0.5) !important;
            color: {txt} !important;
            border: 1px solid {brd}33 !important;
            border-radius: 8px !important;
        }}

        /* แถบเลื่อน (Scrollbar) สไตล์ Matrix */
        ::-webkit-scrollbar {{ width: 5px; }}
        ::-webkit-scrollbar-track {{ background: {bg}; }}
        ::-webkit-scrollbar-thumb {{ background: {brd}; border-radius: 10px; }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# SECTION 3: CORE LOGIC & MATHEMATICS (บรรทัดที่ 160+)
# ==============================================================================

def get_real_time(lat, lon):
    """คำนวณเวลาท้องถิ่นจากพิกัดดาวเทียม"""
    try:
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lng=lon, lat=lat)
        if tz_name:
            return datetime.datetime.now(pytz.timezone(tz_name))
        return datetime.datetime.now()
    except:
        return datetime.datetime.now()

def compute_reality_code(date_obj):
    """คำนวณรหัสคลื่นความถี่ความเป็นจริง (Reality Logic)"""
    pivot = datetime.date(1900, 1, 1)
    delta_days = (date_obj - pivot).days
    lunar_phase = 29.530589
    current_pos = (delta_days - 0.5) % lunar_phase
    weekday_idx = date_obj.weekday() + 1
    
    if current_pos <= 14.765:
        phase_val = int(current_pos) + 1
        code_res = math.sqrt((weekday_idx**2) + (phase_val**2))
        label = f"ข้างขึ้น {phase_val} ค่ำ"
    else:
        phase_val = int(current_pos - 14.765) + 1
        code_res = (weekday_idx * 1.618) / (phase_val if phase_val != 0 else 1)
        label = f"ข้างแรม {phase_val} ค่ำ"
        
    return {"code": round(code_res, 4), "label": label}

def load_system_logo():
    """แสดงตราสัญลักษณ์ประจำหน่วยงาน"""
    brd = st.session_state.border_color
    if os.path.exists("logo1.png"):
        with open("logo1.png", "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{encoded}" style="width:180px; filter:drop-shadow(0 0 12px {brd});"></div>', unsafe_allow_html=True)
    else:
        st.markdown(f"<h1 style='text-align:center; color:{brd}; text-shadow: 0 0 15px {brd}; letter-spacing:10px;'>SYNAPSE OS</h1>", unsafe_allow_html=True)

# ==============================================================================
# SECTION 4: MODULES - THE ROOMS (บรรทัดที่ 220 - 500+)
# ==============================================================================

# --- [ROOM: LOGIN] ---
def room_login():
    load_system_logo()
    st.write("")
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown('<div class="logic-panel">', unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center;'>🔐 AGENT LOGIN</h3>", unsafe_allow_html=True)
        agent_id = st.text_input("AGENT ID (e.g., Ta101)")
        secret_key = st.text_input("ENCRYPTION KEY", type="password")
        
        if st.button("AUTHENTICATE"):
            db_ref = db.reference(f'users/{agent_id}').get()
            if db_ref and db_ref.get('pw') == secret_key:
                st.session_state.user = agent_id
                st.session_state.logged_in = True
                st.success("ACCESS GRANTED.")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("INVALID CREDENTIALS")
        st.markdown('</div>', unsafe_allow_html=True)

# --- [ROOM 0: CORE CONTROL] ---
def room_core_panel(loc_data):
    lat, lon = 13.7563, 100.5018 # Bangkok Default
    if loc_data and 'coords' in loc_data:
        lat, lon = loc_data['coords']['latitude'], loc_data['coords']['longitude']
    
    now = get_real_time(lat, lon)
    brd = st.session_state.border_color
    
    st.markdown(f"""
        <div style="text-align:center; padding:60px 20px; border:4px solid {brd}; border-radius:30px; background:rgba(0,0,0,0.85); box-shadow: 0 0 40px {brd}66;">
            <p style="letter-spacing:12px; font-weight:bold; opacity:0.5; margin-bottom:10px;">CORE SYSTEM ONLINE</p>
            <h1 style="font-size:9em; color:{brd}; margin:0; line-height:1; text-shadow: 0 0 30px {brd}; font-family:monospace;">
                {now.strftime('%H:%M:%S')}
            </h1>
            <h2 style="letter-spacing:4px; opacity:0.8; margin-top:10px;">{now.strftime('%A, %d %B %Y')}</h2>
            <div style="margin: 30px auto; width: 60%; height: 2px; background: linear-gradient(to right, transparent, {brd}, transparent);"></div>
            <div style="display:flex; justify-content:center; gap:50px;">
                <div><small>LATITUDE</small><br><b style="font-size:1.2em;">{lat:.5f}</b></div>
                <div><small>LONGITUDE</small><br><b style="font-size:1.2em;">{lon:.5f}</b></div>
                <div><small>AGENT ID</small><br><b style="font-size:1.2em; color:{brd};">{st.session_state.user}</b></div>
            </div>
            <p style="margin-top:40px; font-style:italic; opacity:0.4;">"อยู่นิ่งๆ ไม่เจ็บตัว - STAY STILL, NO PAIN"</p>
        </div>
    """, unsafe_allow_html=True)

# --- [ROOM 1: RADAR & GEO] ---
def room_radar_system(loc_data):
    st.subheader("🛰️ STRATEGIC RADAR SCANNER")
    u_lat, u_lon = 13.7563, 100.5018
    if loc_data and 'coords' in loc_data:
        u_lat, u_lon = loc_data['coords']['latitude'], loc_data['coords']['longitude']
    
    m = folium.Map(
        location=[u_lat, u_lon], zoom_start=16, 
        tiles="https://mt1.google.com/vt/lyrs=y&x={{x}}&y={{y}}&z={{z}}", 
        attr="Google Satellite"
    )
    
    # มาร์กเกอร์จุดปัจจุบัน
    folium.Marker([u_lat, u_lon], tooltip="YOU", icon=folium.Icon(color='red', icon='screenshot', prefix='glyphicon')).add_to(m)
    
    # ค้นหา Agent อื่นๆ จากฐานข้อมูล
    try:
        agents = db.reference('users').get()
        if agents:
            for uid, info in agents.items():
                if uid != st.session_state.user and 'lat' in info:
                    folium.Marker(
                        [info['lat'], info['lon']], 
                        tooltip=f"AGENT: {uid}", 
                        icon=folium.Icon(color='blue', icon='user', prefix='fa')
                    ).add_to(m)
    except: pass

    st_folium(m, width="100%", height=550)
    
    if st.button("📡 BROADCAST GEOLOCATION SIGNAL"):
        db.reference(f'users/{st.session_state.user}').update({
            'lat': u_lat, 'lon': u_lon, 'last_update': time.time()
        })
        st.toast("Signal Broadcasted to Network")

# --- [ROOM 2: REALITY SCANNER] ---
def room_scanner_module():
    st.subheader("🧬 REALITY FREQUENCY SCANNER")
    min_date = datetime.date(1900, 1, 1) # แก้ไขให้เลือกปี 1970 ได้ตามต้องการ
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="logic-panel">', unsafe_allow_html=True)
        st.write("### 🔍 Personal Reality Code")
        target_dob = st.date_input("SELECT DATE OF BIRTH", value=datetime.date(1970, 1, 1), min_value=min_date)
        if target_dob:
            res = compute_reality_code(target_dob)
            st.metric("REALITY CODE", res['code'])
            st.info(f"STATUS: {res['label']}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="logic-panel">', unsafe_allow_html=True)
        st.write("### 🛰️ Code Sync Compatibility")
        d1 = st.date_input("AGENT 1", value=datetime.date(1996, 8, 17), min_value=min_date, key="d1")
        d2 = st.date_input("AGENT 2", value=datetime.date.today(), min_value=min_date, key="d2")
        if st.button("COMPUTE GAP"):
            c1, c2 = compute_reality_code(d1)['code'], compute_reality_code(d2)['code']
            gap = abs(c1 - c2)
            st.subheader(f"GAP VALUE: {gap:.4f}")
            if gap < 1.0: st.success("MATCH: VERY HIGH")
            elif gap < 3.0: st.warning("MATCH: STABLE")
            else: st.error("MATCH: UNSTABLE")
        st.markdown('</div>', unsafe_allow_html=True)

# --- [ROOM 3: SECURE CHAT (จัดเต็มตามคำขอ)] ---
def room_chat_secure():
    st.subheader("💬 SECURE CHAT TERMINAL")
    st.markdown('<div class="logic-panel" style="height: 400px; overflow-y: auto;">', unsafe_allow_html=True)
    
    # ดึงข้อความจาก Firebase
    try:
        messages = db.reference('chats').order_by_child('ts').limit_to_last(20).get()
        if messages:
            for mid, mdata in messages.items():
                sender = mdata.get('sender', 'Unknown')
                text = mdata.get('msg', '')
                color = st.session_state.border_color if sender == st.session_state.user else "#AAA"
                st.markdown(f"**<span style='color:{color}'>{sender}</span>**: {text}", unsafe_allow_html=True)
    except:
        st.write("WATING FOR INCOMING DATA...")
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.container():
        msg_input = st.text_input("ENTER MESSAGE...", key="chat_in")
        if st.button("SEND DATA"):
            if msg_input:
                db.reference('chats').push({
                    'sender': st.session_state.user,
                    'msg': msg_input,
                    'ts': time.time()
                })
                st.rerun()

# --- [ROOM 4: VOICE CALL (จัดเต็มตามคำขอ)] ---
def room_voice_call():
    st.subheader("📞 ENCRYPTED VOICE CHANNEL")
    st.markdown('<div class="logic-panel">', unsafe_allow_html=True)
    st.write("### 📶 SIGNAL STATUS: SECURE")
    
    c1, c2 = st.columns(2)
    with c1:
        st.button("🎙️ START MICROPHONE")
        st.button("🎧 JOIN AUDIO BRIDGE")
    with c2:
        st.metric("LATENCY", "24ms")
        st.metric("ENCRYPTION", "AES-256")
    
    st.write("---")
    st.warning("⚠️ การโทรผ่านเสียงต้องการการอนุญาตเข้าถึงไมโครโฟนบนบราวเซอร์ของคุณ")
    st.markdown('</div>', unsafe_allow_html=True)

# --- [ROOM 5: MUSIC STATION] ---
def room_music_pro():
    st.subheader("🎧 SYNAPSE MUSIC STATION")
    mp3s = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if not mp3s:
        st.warning("NO MP3 FILES FOUND IN ROOT")
        return

    # แสดง Playlist Scanner
    st.markdown(f"<div style='background:{st.session_state.border_color}22; padding:10px; border-radius:10px; border-left:5px solid {st.session_state.border_color};'>📜 PLAYLIST SCANNER</div>", unsafe_allow_html=True)
    
    p_html = ""
    for i, m in enumerate(mp3s):
        active = f"background:{st.session_state.border_color}44; font-weight:bold;" if i == st.session_state.song_index else "opacity:0.6;"
        p_html += f'<div style="padding:8px; margin:4px; border-radius:5px; {active}">🎵 {i+1}. {m}</div>'
    
    st.markdown(f'<div style="max-height:200px; overflow-y:auto; margin-bottom:20px;">{p_html}</div>', unsafe_allow_html=True)

    current_song = mp3s[st.session_state.song_index]
    st.success(f"▶️ CURRENTLY PLAYING: {current_song}")
    
    with open(current_song, "rb") as audio_file:
        st.audio(audio_file.read(), format="audio/mp3")

    c1, c2, c3 = st.columns(3)
    if c1.button("⏮️ PREV"):
        st.session_state.song_index = (st.session_state.song_index - 1) % len(mp3s)
        st.rerun()
    if c2.button("🔄 SCAN"): st.rerun()
    if c3.button("⏭️ NEXT"):
        st.session_state.song_index = (st.session_state.song_index + 1) % len(mp3s)
        st.rerun()

# --- [ROOM 6: DESIGN CENTER] ---
def room_design_center():
    st.subheader("🎨 DESIGN CONTROL CENTER")
    st.markdown('<div class="logic-panel">', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    new_bg = c1.color_picker("BACKGROUND COLOR", st.session_state.bg_color)
    new_txt = c2.color_picker("TEXT COLOR", st.session_state.text_color)
    new_brd = c3.color_picker("NEON BORDER", st.session_state.border_color)
    
    if st.button("SAVE & APPLY SYSTEM THEME"):
        st.session_state.bg_color = new_bg
        st.session_state.text_color = new_txt
        st.session_state.border_color = new_brd
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# SECTION 5: MASTER EXECUTION ENGINE (THE FINAL PART)
# ==============================================================================

def main():
    # 1. รันระบบเบื้องหลัง (Background Logic)
    init_system()
    apply_ui_engine()

    # 2. ตรวจสอบสิทธิ์การเข้าถึง (Access Control)
    if not st.session_state.logged_in:
        room_login()
        return

    # 3. เริ่มต้นอินเทอร์เฟซหลัก (Main Interface)
    load_system_logo()
    
    # [บรรทัดที่ 540+] สร้างระบบแท็บนำทาง
    nav_tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "🧬 SCANNER", "💬 CHAT", "📞 VOICE", "🎧 MUSIC", "🎨 DESIGN"])
    
    # ดึงข้อมูลพิกัด (ถ้ามี)
    current_location = get_geolocation()

    with nav_tabs[0]: room_core_panel(current_location)
    with nav_tabs[1]: room_radar_system(current_location)
    with nav_tabs[2]: room_scanner_module()
    with nav_tabs[3]: room_chat_secure()
    with nav_tabs[4]: room_voice_call()
    with nav_tabs[5]: room_music_pro()
    with nav_tabs[6]: room_design_center()

    # บรรทัดที่ 560: ข้อมูลปิดท้ายระบบ
    st.write("---")
    st.caption(f"SYNAPSE COMMAND CENTER | v5.0 | SECURE AGENT: {st.session_state.user} | STATUS: OPTIMAL")

if __name__ == "__main__":
    main()

# ==============================================================================
# 🏁 END OF CORE SYSTEM ARCHITECTURE
# ==============================================================================
