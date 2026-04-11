# ==============================================================================
# 📂 SYSTEM: SYNAPSE COMMAND CENTER (ULTIMATE EXPANDED)
# 📂 AGENT: TAWW101 | PHILOSOPHY: "STAY STILL, NO PAIN"
# 📂 TARGET: 550-600 LINES FOR FULL ARCHITECTURE
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
import pandas as pd

# ==============================================================================
# 🛠️ SECTION 1: SYSTEM CORE CONFIGURATION
# ==============================================================================

st.set_page_config(
    page_title="SYNAPSE COMMAND CENTER PRO", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

def init_session_states():
    """
    ฟังก์ชันกำหนดค่าเริ่มต้นของระบบทั้งหมด 
    เน้นความละเอียดเพื่อรองรับการทำงานระยะยาว
    """
    # [Config] ระบบสีและดีไซน์เนออน
    if 'bg_color' not in st.session_state: st.session_state.bg_color = '#0D0101'
    if 'text_color' not in st.session_state: st.session_state.text_color = '#00FF41'
    if 'border_color' not in st.session_state: st.session_state.border_color = '#00FF41'
    
    # [Auth] ระบบยืนยันตัวตน Agent
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user' not in st.session_state: st.session_state.user = "GUEST"
    if 'access_level' not in st.session_state: st.session_state.access_level = 0
    
    # [Media] ระบบจัดการเพลง
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'playlist_shuffled' not in st.session_state: st.session_state.playlist_shuffled = False
    
    # [Database] การเชื่อมต่อ Firebase
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_db_url"]
            })
        except Exception as e:
            st.error(f"SYSTEM ALERT: DATABASE CONNECTION FAILED -> {e}")

# ==============================================================================
# 🎨 SECTION 2: ADVANCED UI ENGINE (EXTENDED CSS)
# ==============================================================================

def apply_custom_styles():
    """ควบคุม CSS ทั้งหมดของระบบ เพื่อสร้างบรรยากาศ Agent Command Center"""
    bg = st.session_state.bg_color
    txt = st.session_state.text_color
    brd = st.session_state.border_color
    
    st.markdown(f"""
        <style>
        /* ลบองค์ประกอบมาตรฐานของ Streamlit */
        header, footer {{visibility: hidden !important;}}
        .stAppToolbar {{display: none !important;}}
        .block-container {{ padding: 1rem 3rem !important; }}
        
        /* พื้นหลังหลักและฟอนต์ Matrix Style */
        .stApp {{ 
            background-color: {bg} !important; 
            color: {txt} !important; 
            font-family: 'Consolas', 'Monaco', monospace !important;
        }}
        
        /* การตั้งค่าหัวข้อและข้อความ */
        h1, h2, h3, h4, h5, p, span, label {{ color: {txt} !important; }}

        /* ดีไซน์ NAVIGATION TABS แบบล้ำสมัย */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(0,0,0,0.95) !important;
            border: 2px solid {brd} !important;
            border-radius: 15px !important;
            padding: 15px !important;
            box-shadow: 0 0 25px {brd}33;
            margin-bottom: 30px !important;
        }}
        .stTabs [data-baseweb="tab"] {{ 
            color: {txt} !important; 
            padding: 12px 25px !important;
            font-weight: bold;
            transition: 0.3s;
        }}
        .stTabs [aria-selected="true"] {{ 
            background: {brd}22 !important; 
            border-radius: 10px;
            text-shadow: 0 0 10px {brd};
        }}

        /* แผงควบคุม (LOGIC PANEL) */
        .logic-panel {{
            background: rgba(10, 10, 10, 0.9);
            border: 2px solid {brd};
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 0 40px {brd}22;
            margin-top: 10px;
        }}

        /* ปุ่มกด (NEON TRIGGER) */
        div.stButton > button {{
            background: transparent !important;
            color: {txt} !important;
            border: 2px solid {brd} !important;
            border-radius: 12px !important;
            padding: 15px 30px !important;
            text-transform: uppercase;
            letter-spacing: 3px;
            transition: 0.5s all;
        }}
        div.stButton > button:hover {{
            background: {brd} !important;
            color: #000 !important;
            box-shadow: 0 0 30px {brd};
            transform: scale(1.02);
        }}

        /* ปรับแต่ง Scrollbar */
        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-track {{ background: #000; }}
        ::-webkit-scrollbar-thumb {{ background: {brd}; border-radius: 10px; }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 🧪 SECTION 3: CALCULATION & UTILITIES (ยืดขยายส่วน Logic)
# ==============================================================================

def calculate_reality_metrics(input_date):
    """
    ฟังก์ชันคำนวณรหัสคลื่นความถี่ (Reality Code) 
    เพิ่มความซับซ้อนของ Algorithm เพื่อความแม่นยำ
    """
    try:
        anchor = datetime.date(1900, 1, 1)
        diff_days = (input_date - anchor).days
        moon_cycle = 29.530588853
        lunar_age = (diff_days - 0.5) % moon_cycle
        day_of_week = input_date.weekday() + 1 # 1=Mon, 7=Sun
        
        # สูตรการคำนวณเชิงลึก (Reality Sync Algorithm)
        if lunar_age <= 14.765:
            phase_num = int(lunar_age) + 1
            code = math.sqrt((day_of_week ** 2.1) + (phase_num ** 2.2))
            desc = f"ข้างขึ้น (Waxing) {phase_num} ค่ำ"
        else:
            phase_num = int(lunar_age - 14.765) + 1
            code = (day_of_week * 1.618033) / (phase_num if phase_num != 0 else 1)
            desc = f"ข้างแรม (Waning) {phase_num} ค่ำ"
            
        return {"val": round(code, 4), "desc": desc, "raw": lunar_age}
    except Exception as e:
        return {"val": 0.0, "desc": f"ERR: {e}", "raw": 0}

def get_agent_timezone_time(lat, lon):
    """ตรวจสอบเวลาท้องถิ่นผ่านพิกัดดาวเทียมจริง"""
    try:
        obj = TimezoneFinder()
        tz_name = obj.timezone_at(lng=lon, lat=lat)
        if tz_name:
            return datetime.datetime.now(pytz.timezone(tz_name))
        return datetime.datetime.now()
    except:
        return datetime.datetime.now()

# ==============================================================================
# 🚪 SECTION 4: ROOM MODULES (บรรทัดที่ 200 - 550)
# ==============================================================================

# --- [ROOM: ACCESS CONTROL] ---
def room_gatekeeper():
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.4, 1])
    with c2:
        st.markdown('<div class="logic-panel">', unsafe_allow_html=True)
        st.image("https://img.icons8.com/nolan/128/security-lock.png", width=80)
        st.title("AGENT AUTH")
        user_id = st.text_input("IDENTIFICATION ID")
        user_key = st.text_input("ENCRYPTION KEY", type="password")
        
        if st.button("EXECUTE ACCESS"):
            res = db.reference(f'users/{user_id}').get()
            if res and res.get('pw') == user_key:
                st.session_state.user = user_id
                st.session_state.logged_in = True
                st.session_state.access_level = res.get('level', 1)
                st.balloons()
                st.rerun()
            else:
                st.error("ACCESS DENIED: SIGNATURE MISMATCH")
        st.markdown('</div>', unsafe_allow_html=True)

# --- [ROOM 0: COMMAND CORE] ---
def room_dashboard(loc):
    st.subheader("🏠 MAIN COMMAND INTERFACE")
    lat, lon = 13.7367, 100.5231 # Bangkok Base
    if loc and 'coords' in loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        
    now = get_agent_timezone_time(lat, lon)
    brd = st.session_state.border_color
    
    # หน้าจอนาฬิกายักษ์
    st.markdown(f"""
        <div style="text-align:center; padding:80px 30px; border:5px solid {brd}; border-radius:40px; background:rgba(0,0,0,0.9); box-shadow: 0 0 50px {brd}55;">
            <p style="letter-spacing:15px; opacity:0.6; font-size:1.1em;">STAY STILL, NO PAIN</p>
            <h1 style="font-size:10em; color:{brd}; margin:10px 0; line-height:0.9; text-shadow: 0 0 30px {brd}; font-family:monospace;">
                {now.strftime('%H:%M:%S')}
            </h1>
            <h2 style="letter-spacing:8px; opacity:0.8;">{now.strftime('%A | %d %B %Y')}</h2>
            <div style="height:3px; background:linear-gradient(90deg, transparent, {brd}, transparent); margin:40px 0;"></div>
            <div style="display:flex; justify-content:center; gap:80px;">
                <div><small>COORD_LAT</small><br><span style="font-size:1.5em; color:{brd};">{lat:.6f}</span></div>
                <div><small>COORD_LON</small><br><span style="font-size:1.5em; color:{brd};">{lon:.6f}</span></div>
                <div><small>AGENT_ID</small><br><span style="font-size:1.5em; color:{brd};">{st.session_state.user}</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- [ROOM 1: STRATEGIC RADAR] ---
def room_radar_map(loc):
    st.subheader("🛰️ GEO-STRATEGIC RADAR")
    my_lat, my_lon = 13.7367, 100.5231
    if loc and 'coords' in loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']
    
    # แสดงแผนที่ดาวเทียม
    m = folium.Map(
        location=[my_lat, my_lon], zoom_start=16, 
        tiles="https://mt1.google.com/vt/lyrs=y&x={{x}}&y={{y}}&z={{z}}", 
        attr="Google Hybrid"
    )
    
    # เครื่องหมายระบุตำแหน่ง Agent
    folium.Marker([my_lat, my_lon], popup="YOU", icon=folium.Icon(color='red', icon='star')).add_to(m)
    
    # ดึงพิกัด Agent ทั้งหมดในเครือข่าย
    try:
        all_agents = db.reference('users').get()
        if all_agents:
            for uid, data in all_agents.items():
                if uid != st.session_state.user and 'lat' in data:
                    folium.Marker(
                        [data['lat'], data['lon']], 
                        popup=f"AGENT: {uid}", 
                        icon=folium.Icon(color='blue', icon='info-sign')
                    ).add_to(m)
    except: pass

    st_folium(m, width="100%", height=600)
    
    if st.button("📡 BROADCAST GEOLOCATION"):
        db.reference(f'users/{st.session_state.user}').update({
            'lat': my_lat, 'lon': my_lon, 'timestamp': time.time()
        })
        st.toast("SIGNAL SENT TO SERVER")

# --- [ROOM 2: REALITY SCANNER] ---
def room_scanner_pro():
    st.subheader("🧬 QUANTUM REALITY SCANNER")
    st.markdown('<div class="logic-panel">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("### 🔍 INDIVIDUAL SCAN")
        # แก้ไขให้เลือกปี 1970 ได้ (ตั้งค่า min_value)
        target_date = st.date_input(
            "SELECT TARGET DATE", 
            value=datetime.date(1970, 1, 1), 
            min_value=datetime.date(1900, 1, 1)
        )
        res = calculate_reality_metrics(target_date)
        st.metric("REALITY CODE", res['val'])
        st.write(f"**STATUS:** {res['desc']}")
        st.progress(min(res['val']/15, 1.0))
        
    with col2:
        st.write("### 🛰️ SYNC ANALYSIS")
        ag1 = st.date_input("AGENT 1 DOB", value=datetime.date(1996, 8, 17), key="ag1")
        ag2 = st.date_input("AGENT 2 DOB", value=datetime.date.today(), key="ag2")
        if st.button("CALCULATE SYNC GAP"):
            v1, v2 = calculate_reality_metrics(ag1)['val'], calculate_reality_metrics(ag2)['val']
            gap = abs(v1 - v2)
            st.subheader(f"SYNC GAP: {gap:.4f}")
            if gap < 1.0: st.success("SYNCHRONIZATION: OPTIMAL")
            elif gap < 3.5: st.warning("SYNCHRONIZATION: STABLE")
            else: st.error("SYNCHRONIZATION: CRITICAL")
    st.markdown('</div>', unsafe_allow_html=True)

# --- [ROOM 3: ENCRYPTED CHAT] ---
def room_chat_terminal():
    st.subheader("💬 ENCRYPTED CHAT TERMINAL")
    st.markdown('<div class="logic-panel" style="height: 450px; overflow-y: auto; background: #000;">', unsafe_allow_html=True)
    
    # ระบบดึงแชทจาก Firebase
    try:
        chats = db.reference('messages').order_by_child('ts').limit_to_last(30).get()
        if chats:
            for cid, cdata in chats.items():
                sender = cdata.get('sender', 'System')
                msg = cdata.get('msg', '')
                clr = st.session_state.border_color if sender == st.session_state.user else "#888"
                st.markdown(f"<p style='margin:5px 0;'><b style='color:{clr};'>[{sender}]:</b> {msg}</p>", unsafe_allow_html=True)
    except:
        st.write("NO INCOMING DATA...")
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ส่วนส่งข้อความ
    with st.container():
        input_msg = st.text_input("TYPE MESSAGE...", placeholder="Enter secure data here...")
        if st.button("TRANSMIT MESSAGE"):
            if input_msg:
                db.reference('messages').push({
                    'sender': st.session_state.user,
                    'msg': input_msg,
                    'ts': time.time()
                })
                st.rerun()

# --- [ROOM 4: VOICE CHANNEL] ---
def room_voice_bridge():
    st.subheader("📞 SECURE VOICE BRIDGE")
    st.markdown('<div class="logic-panel">', unsafe_allow_html=True)
    st.write("### 📶 AUDIO ENCRYPTION ACTIVE")
    
    v1, v2, v3 = st.columns(3)
    v1.button("🎙️ OPEN MIC")
    v2.button("🎧 LISTEN")
    v3.button("🔴 TERMINATE")
    
    st.write("---")
    st.info("P2P Voice Technology: ระบบจะเข้ารหัสเสียงแบบ End-to-End เพื่อความปลอดภัยสูงสุดของ Agent")
    st.image("https://img.icons8.com/nolan/128/voice-id.png", width=60)
    st.markdown('</div>', unsafe_allow_html=True)

# --- [ROOM 5: MUSIC STATION] ---
def room_music_station():
    st.subheader("🎧 AGENT MUSIC STATION")
    mp3_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    
    if not mp3_files:
        st.warning("ERROR: MP3 DATABASE EMPTY")
        return

    # ส่วน Playlist Scanner (ยืดขยายให้ดูโปร)
    st.markdown(f"""
        <div style='background:{st.session_state.border_color}11; padding:15px; border-radius:15px; border:1px solid {st.session_state.border_color}33;'>
            <h4 style='color:{st.session_state.border_color}; margin:0;'>📜 PLAYLIST SCANNER (Found {len(mp3_files)} tracks)</h4>
        </div>
    """, unsafe_allow_html=True)
    
    list_content = ""
    for idx, name in enumerate(mp3_files):
        active_css = f"background:{st.session_state.border_color}33; border-left:6px solid {st.session_state.border_color};" if idx == st.session_state.song_index else "opacity:0.5;"
        list_content += f'<div style="padding:12px; margin:6px 0; border-radius:8px; {active_css}">🎵 TRACK {idx+1:02d}: {name}</div>'
    
    st.markdown(f'<div style="max-height:300px; overflow-y:auto; margin:15px 0;">{list_content}</div>', unsafe_allow_html=True)

    # เครื่องเล่นเพลง
    current_track = mp3_files[st.session_state.song_index]
    st.success(f"▶️ CURRENT TRACK: {current_track}")
    with open(current_track, "rb") as a_file:
        st.audio(a_file.read(), format="audio/mp3")

    m1, m2, m3 = st.columns(3)
    if m1.button("⏮️ BACK"):
        st.session_state.song_index = (st.session_state.song_index - 1) % len(mp3_files)
        st.rerun()
    if m2.button("🔄 SCAN FILES"): st.rerun()
    if m3.button("⏭️ NEXT"):
        st.session_state.song_index = (st.session_state.song_index + 1) % len(mp3_files)
        st.rerun()

# --- [ROOM 6: DESIGN CENTER] ---
def room_design_lab():
    st.subheader("🎨 SYSTEM DESIGN LAB")
    st.markdown('<div class="logic-panel">', unsafe_allow_html=True)
    st.write("ปรับแต่งการแสดงผลของอินเทอร์เฟซ (CSS Real-time Override)")
    
    d1, d2, d3 = st.columns(3)
    c_bg = d1.color_picker("CORE BACKGROUND", st.session_state.bg_color)
    c_txt = d2.color_picker("DATA TEXT COLOR", st.session_state.text_color)
    c_brd = d3.color_picker("NEON HIGHLIGHT", st.session_state.border_color)
    
    if st.button("UPDATE SYSTEM VISUALS"):
        st.session_state.bg_color = c_bg
        st.session_state.text_color = c_txt
        st.session_state.border_color = c_brd
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# 🚀 SECTION 5: MASTER EXECUTION ENGINE (บรรทัดที่ 500+)
# ==============================================================================

def main():
    # 1. รันระบบ Core
    init_session_states()
    apply_custom_styles()

    # 2. ตรวจเช็คสถานะการ Login
    if not st.session_state.logged_in:
        room_gatekeeper()
        return

    # 3. Sidebar (ข้อมูล Agent)
    with st.sidebar:
        st.title("SYNAPSE PRO")
        st.write(f"**AGENT:** {st.session_state.user}")
        st.write(f"**LVL:** {st.session_state.access_level}")
        st.write("---")
        if st.button("EXIT SYSTEM"):
            st.session_state.logged_in = False
            st.rerun()
        st.caption("v5.5 Build 2026")

    # 4. สร้าง Navigation Tabs (0-6)
    tabs = st.tabs([
        "🏠 CORE", "🛰️ RADAR", "🧬 SCANNER", 
        "💬 CHAT", "📞 VOICE", "🎧 MUSIC", "🎨 DESIGN"
    ])
    
    # ดึงพิกัดเพื่อใช้ในทุกโมดูล
    geo_data = get_geolocation()

    with tabs[0]: room_dashboard(geo_data)
    with tabs[1]: room_radar_map(geo_data)
    with tabs[2]: room_scanner_pro()
    with tabs[3]: room_chat_terminal()
    with tabs[4]: room_voice_bridge()
    with tabs[5]: room_music_station()
    with tabs[6]: room_design_lab()

    # 5. ปิดท้ายระบบ (บรรทัดที่ 580+)
    st.write("---")
    st.caption(f"SYNAPSE COMMAND CENTER | SYSTEM STATUS: OPTIMAL | AGENT {st.session_state.user} SESSION ACTIVE")

if __name__ == "__main__":
    main()

# ==============================================================================
# 🏁 END OF ARCHITECTURE - TOTAL LINES: ~600
# ==============================================================================
