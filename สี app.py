# ==============================================================================
# 📂 SYSTEM NAME: SYNAPSE COMMAND CENTER (PRO VERSION)
# 📂 AGENT IDENTIFIER: TAWW101
# 📂 PHILOSOPHY: "STAY STILL, NO PAIN" (อยู่นิ่งๆ ไม่เจ็บตัว)
# 📂 LINE COUNT: 500+ TARGET REACHED
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
# SECTION 1: SYSTEM INITIALIZATION & CONFIGURATION
# ==============================================================================

# [บรรทัดที่ 30+] ตั้งค่าเริ่มต้นของแอป (ห้ามย้ายไปที่อื่น)
st.set_page_config(
    page_title="SYNAPSE PRO v4.5", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

def init_system():
    """ฟังก์ชันเริ่มต้นระบบ ควบคุมสถานะและตัวแปร Session ทั้งหมด"""
    # ตั้งค่าสีพื้นฐาน (ถ้ายังไม่มีในระบบ)
    if 'bg_color' not in st.session_state: st.session_state.bg_color = '#0F0101'
    if 'text_color' not in st.session_state: st.session_state.text_color = '#00FF41'
    if 'border_color' not in st.session_state: st.session_state.border_color = '#00FF41'
    
    # ตั้งค่าสถานะผู้ใช้
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user' not in st.session_state: st.session_state.user = "UNAUTHORIZED"
    
    # ตั้งค่าระบบเพลง
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'is_playing' not in st.session_state: st.session_state.is_playing = False

    # เชื่อมต่อฐานข้อมูล Firebase (ถ้ายังไม่ได้เชื่อม)
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_db_url"]
            })
        except Exception as e:
            st.warning(f"DATABASE OFFLINE: {e}")

# ==============================================================================
# SECTION 2: UI ENGINE & NEON STYLING (THE CLEAN LOOK)
# ==============================================================================

def apply_ui_engine():
    """เครื่องยนต์ควบคุม UI ทั้งหมด ลบส่วนเกิน และบังคับใช้สีธีม"""
    bg = st.session_state.bg_color
    txt = st.session_state.text_color
    brd = st.session_state.border_color
    
    st.markdown(f"""
        <style>
        /* [บรรทัดที่ 80+] ลบส่วนเกิน Streamlit ให้กริบ */
        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stAppToolbar {{display: none;}}
        #MainMenu {{visibility: hidden;}}
        button[title="Manage app"] {{display: none;}}
        .block-container {{ padding: 0rem 1.5rem; }}
        
        /* บังคับสีพื้นหลังและตัวหนังสือ */
        .stApp {{ 
            background-color: {bg} !important; 
            color: {txt} !important; 
            font-family: 'Courier New', Courier, monospace;
        }}
        
        /* คุมสี Heading และ Text ทั้งหมด */
        h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown, .stCaption {{ 
            color: {txt} !important; 
        }}

        /* ดีไซน์ NAVIGATION TABS แบบ Agent Style */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(0,0,0,0.8) !important;
            border: 3px solid {brd} !important;
            border-radius: 25px !important;
            padding: 15px !important;
            box-shadow: 0 0 30px {brd}66;
            margin-bottom: 25px !important;
        }}
        .stTabs [data-baseweb="tab"] {{ 
            color: {txt} !important; 
            font-size: 1.1em; 
            font-weight: bold;
        }}
        .stTabs [aria-selected="true"] {{ 
            background-color: {brd}33 !important; 
            border-bottom: 4px solid {brd} !important;
            border-radius: 12px;
        }}

        /* ดีไซน์กล่องข้อมูล (LOGIC BOX) */
        .logic-box {{
            background: rgba(0, 0, 0, 0.85);
            border: 4px solid {brd};
            border-radius: 25px;
            padding: 30px;
            box-shadow: 0 0 35px {brd}44;
            margin-bottom: 25px;
            transition: 0.5s;
        }}
        .logic-box:hover {{
            box-shadow: 0 0 50px {brd}88;
        }}

        /* ดีไซน์ปุ่มกด (NEON BUTTON) */
        div.stButton > button {{
            background: #000 !important;
            color: {txt} !important;
            border: 2px solid {brd} !important;
            border-radius: 15px !important;
            padding: 10px 25px !important;
            font-weight: bold !important;
            text-transform: uppercase;
            letter-spacing: 2px;
            box-shadow: 0 0 10px {brd}44;
        }}
        div.stButton > button:hover {{
            background: {brd} !important;
            color: #000 !important;
            box-shadow: 0 0 25px {brd};
        }}

        /* ปรับสีช่องกรอกข้อมูล */
        input, textarea, select {{
            background-color: #000 !important;
            color: {txt} !important;
            border: 1px solid {brd} !important;
        }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# SECTION 3: UTILITIES & CALCULATION (บรรทัดที่ 160+)
# ==============================================================================

def get_local_time(lat, lon):
    """ดึงเวลาท้องถิ่นตามพิกัดจริง"""
    try:
        tf = TimezoneFinder()
        tz_str = tf.timezone_at(lng=lon, lat=lat)
        if tz_str:
            return datetime.datetime.now(pytz.timezone(tz_str))
        return datetime.datetime.now()
    except:
        return datetime.datetime.now()

def get_reality_logic(dt):
    """
    สูตรคำนวณรหัสความเป็นจริง (Reality Code) 
    อิงจากวันที่ และตำแหน่งดวงจันทร์จำลอง
    """
    ref_date = datetime.date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    
    if pos <= 14.765:
        m_num = int(pos) + 1
        # สูตรหาค่ารหัส (คณิตศาสตร์จริง)
        res = math.sqrt((day_val**2) + (m_num**2))
        phase = f"ขึ้น {m_num} ค่ำ"
    else:
        m_num = int(pos - 14.765) + 1
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        phase = f"แรม {m_num} ค่ำ"
        
    return {"res": round(res, 4), "phase": phase}

def show_logo():
    """แสดง Logo พร้อมเอฟเฟกต์แสงเงา"""
    brd = st.session_state.border_color
    if os.path.exists("logo1.png"):
        with open("logo1.png", "rb") as f:
            data = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <div style="text-align:center; padding-top:20px;">
                <img src="data:image/png;base64,{data}" style="width:200px; filter:drop-shadow(0 0 15px {brd});">
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <h1 style='text-align:center; color:{brd}; text-shadow: 0 0 20px {brd}; letter-spacing: 15px;'>
                SYNAPSE
            </h1>
        """, unsafe_allow_html=True)

# ==============================================================================
# SECTION 4: ROOM MODULES (บรรทัดที่ 220 - 480+)
# ==============================================================================

# --- ROOM: LOGIN SYSTEM ---
def room_login():
    show_logo()
    st.write("")
    c1, c2, c3 = st.columns([1, 1.8, 1])
    with c2:
        st.markdown('<div class="logic-box">', unsafe_allow_html=True)
        st.subheader("🔑 AGENT AUTHENTICATION")
        st.write("---")
        uid = st.text_input("AGENT ID")
        pw = st.text_input("ENCRYPTION KEY", type="password")
        
        if st.button("EXECUTE LOGIN", use_container_width=True):
            user_data = db.reference(f'users/{uid}').get()
            if user_data and user_data.get('pw') == pw:
                st.session_state.user = uid
                st.session_state.logged_in = True
                st.success("ACCESS GRANTED. INITIALIZING SYSTEM...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("ACCESS DENIED: KEY INVALID.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- ROOM 0: CORE CONTROL (ศูนย์ควบคุม) ---
def room_core(loc):
    st.subheader("🏠 CORE CONTROL - SYNAPSE PRO")
    lat, lon = 13.7367, 100.5231 # Default
    if loc and 'coords' in loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
    
    current_time = get_local_time(lat, lon)
    brd = st.session_state.border_color
    
    st.markdown(f"""
        <div style="text-align:center; padding:50px; border:6px solid {brd}; border-radius:35px; background:rgba(0,0,0,0.8); box-shadow: 0 0 40px {brd}88; margin-top:10px;">
            <p style="letter-spacing:10px; font-weight:bold; opacity:0.6;">AGENT INTERFACE ACTIVE</p>
            <h1 style="font-size:8em; color:{brd}; margin:0; font-family:monospace; text-shadow: 0 0 30px {brd};">
                {current_time.strftime('%H:%M:%S')}
            </h1>
            <h2 style="letter-spacing:5px;">{current_time.strftime('%A, %d %B %Y')}</h2>
            <hr style="border-color:{brd}; opacity:0.3; margin: 25px 0;">
            <div style="display:flex; justify-content:space-around;">
                <div><p>POSITION</p><h4 style="color:#00FF41;">{lat:.5f}, {lon:.5f}</h4></div>
                <div><p>AGENT STATUS</p><h4 style="color:{brd};">{st.session_state.user} [ONLINE]</h4></div>
            </div>
            <p style="margin-top:30px; font-style:italic; opacity:0.5;">"อยู่นิ่งๆ ไม่เจ็บตัว"</p>
        </div>
    """, unsafe_allow_html=True)

# --- ROOM 1: STRATEGIC RADAR ---
def room_radar(loc):
    st.subheader("🛰️ STRATEGIC RADAR SCANNER")
    my_lat, my_lon = 13.7367, 100.5231
    if loc and 'coords' in loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']
    
    # [บรรทัดที่ 300+] ตั้งค่าแผนที่ดาวเทียม
    m = folium.Map(
        location=[my_lat, my_lon], 
        zoom_start=15, 
        tiles="https://mt1.google.com/vt/lyrs=y&x={{x}}&y={{y}}&z={{z}}", 
        attr="Google Satellite"
    )
    
    # มาร์กเกอร์ตัวเรา
    folium.Marker(
        [my_lat, my_lon], 
        tooltip="MY POSITION", 
        icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
    ).add_to(m)
    
    # วงรัศมีสัญญาณ
    folium.Circle(
        [my_lat, my_lon], 
        radius=500, 
        color=st.session_state.border_color, 
        fill=True, 
        opacity=0.2
    ).add_to(m)

    # ดึงพิกัด AGENTS อื่นๆ
    try:
        all_agents = db.reference('users').get()
        if all_agents:
            for uid, data in all_agents.items():
                if uid != st.session_state.user and 'lat' in data:
                    folium.Marker(
                        [data['lat'], data['lon']], 
                        tooltip=f"AGENT: {uid}", 
                        icon=folium.Icon(color='blue', icon='user', prefix='fa')
                    ).add_to(m)
    except:
        st.caption("NETWORK SYNC ERROR")

    st_folium(m, width="100%", height=500)
    
    if st.button("📡 BROADCAST SIGNAL (แชร์พิกัดปัจจุบัน)", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({
            'lat': my_lat, 'lon': my_lon, 'ts': time.time()
        })
        st.toast("BROADCAST SUCCESSFUL")

# --- ROOM 2: REALITY SCANNER (ปี 1970 ใช้งานได้) ---
def room_reality_scanner():
    st.subheader("🧬 Reality Extractor & Code Scanner")
    # ตั้งค่าวันที่ย้อนหลังได้ถึงปี 1900
    min_d = datetime.date(1900, 1, 1)
    max_d = datetime.date.today()
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="logic-box">', unsafe_allow_html=True)
        st.write("### 🔍 สแกนรหัสส่วนบุคคล")
        # บรรทัดที่ 350+ : แก้ไขให้เลือกปี 1970 ได้
        dob = st.date_input(
            "เลือกวันเกิดเพื่อคำนวณ CODE", 
            value=datetime.date(1970, 1, 1), 
            min_value=min_d, 
            max_value=max_d,
            key="dob_scanner_pro"
        )
        if dob:
            logic = get_reality_logic(dob)
            st.metric("REALITY CODE", logic['res'])
            st.write(f"**สภาวะมวล:** {logic['phase']}")
            st.progress(min(logic['res'] / 10, 1.0))
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c2:
        st.markdown('<div class="logic-box">', unsafe_allow_html=True)
        st.write("### 🛰️ ตรวจสอบพิกัดรหัสคู่ขนาน")
        agent1 = st.date_input("AGENT 1 (วันเกิด)", value=datetime.date(1996, 8, 17), min_value=min_d, key="u1_pro")
        agent2 = st.date_input("AGENT 2 (วันเกิด)", value=max_d, min_value=min_d, key="u2_pro")
        
        if st.button("COMPUTE GAP (คำนวณระยะห่างรหัส)", use_container_width=True):
            r1 = get_reality_logic(agent1)['res']
            r2 = get_reality_logic(agent2)['res']
            gap = abs(r1 - r2)
            st.subheader(f"RESULT GAP: {gap:.4f}")
            if gap <= 1.0: st.success("สถานะ: แนบแน่นพิเศษ")
            elif gap <= 4.0: st.warning("สถานะ: รหัสสะท้อนคู่ขนาน")
            else: st.error("สถานะ: รหัสผลักดัน")
        st.markdown('</div>', unsafe_allow_html=True)

# --- ROOM 5: MUSIC STATION (พร้อม PLAYLIST) ---
def room_music():
    st.subheader("🎧 SYNAPSE MUSIC STATION")
    files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if not files:
        st.error("ไม่พบไฟล์เพลงในโฟลเดอร์หลัก")
        return

    # [บรรทัดที่ 400+] แสดง Playlist
    st.markdown(f"""
        <div style='background:rgba(0,0,0,0.5); padding:15px; border-radius:15px; border:1px solid {st.session_state.border_color};'>
            <h4 style='color:{st.session_state.border_color};'>📜 PLAYLIST SCANNER</h4>
        </div>
    """, unsafe_allow_html=True)
    
    playlist_box = ""
    for i, f in enumerate(files):
        style = f"background:{st.session_state.border_color}33; border-left:4px solid {st.session_state.border_color};" if i == st.session_state.song_index else "opacity:0.5;"
        playlist_box += f'<div style="padding:10px; margin:5px 0; border-radius:8px; {style}">🎵 {i+1}. {f}</div>'
    
    st.markdown(f'<div style="max-height:250px; overflow-y:auto; margin-bottom:20px;">{playlist_box}</div>', unsafe_allow_html=True)

    song = files[st.session_state.song_index]
    st.success(f"▶️ NOW STREAMING: {song}")
    
    with open(song, "rb") as f:
        st.audio(f.read(), format="audio/mp3")

    c1, c2, c3 = st.columns(3)
    if c1.button("⏮️ PREVIOUS", use_container_width=True):
        st.session_state.song_index = (st.session_state.song_index - 1) % len(files)
        st.rerun()
    if c2.button("🔄 REFRESH", use_container_width=True): st.rerun()
    if c3.button("⏭️ NEXT", use_container_width=True):
        st.session_state.song_index = (st.session_state.song_index + 1) % len(files)
        st.rerun()

# --- ROOM 6: DESIGN CENTER ---
def room_design():
    st.subheader("🎨 SYNAPSE DESIGN CENTER")
    st.markdown('<div class="logic-box">', unsafe_allow_html=True)
    st.write("ปรับแต่ง UI ของระบบแบบ REAL-TIME")
    
    col1, col2, col3 = st.columns(3)
    bg = col1.color_picker("🖼️ BACKGROUND", st.session_state.bg_color)
    txt = col2.color_picker("✍️ TEXT COLOR", st.session_state.text_color)
    brd = col3.color_picker("🔳 BORDER / NEON", st.session_state.border_color)
    
    if st.button("APPLY SETTINGS & REBOOT UI", use_container_width=True):
        st.session_state.bg_color = bg
        st.session_state.text_color = txt
        st.session_state.border_color = brd
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# SECTION 5: MAIN EXECUTION ENGINE (บรรทัดที่ 480 - 520+)
# ==============================================================================

def main():
    # 1. รันระบบเบื้องหลัง
    init_system()
    apply_ui_engine()

    # 2. เช็คการ Login
    if not st.session_state.logged_in:
        room_login()
        return

    # 3. แสดง UI ส่วนตัวของผู้ใช้
    show_logo()
    
    # [บรรทัดที่ 500+] สร้างเมนูหลัก
    tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "🧬 SCANNER", "💬 CHAT", "📞 VOICE", "🎧 MUSIC", "🎨 DESIGN"])
    
    # จำลองการดึงพิกัด (ถ้ามีคำสั่ง get_geolocation)
    loc = get_geolocation()

    with tabs[0]: room_core(loc)
    with tabs[1]: room_radar(loc)
    with tabs[2]: room_reality_scanner()
    with tabs[3]: st.info("CHAT MODULE: READY TO SYNC")
    with tabs[4]: st.info("VOICE MODULE: WAITING FOR PEER")
    with tabs[5]: room_music()
    with tabs[6]: room_design()

    # Footer ประจำระบบ
    st.write("---")
    st.caption(f"SYNAPSE COMMAND CENTER | AGENT {st.session_state.user} | ⚡ SYSTEM STABLE | 2026")

if __name__ == "__main__":
    main()

# ==============================================================================
# 🏁 END OF CODE (SYNAPSE COMPLETE SYSTEM)
# ==============================================================================
