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

# ==============================================================================
# 1. INITIAL SYSTEM CONFIGURATION (บรรทัดที่ 20+)
# ==============================================================================
st.set_page_config(
    page_title="SYNAPSE COMMAND CENTER", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

def init_system():
    """ควบคุมสถานะระบบทั้งหมด"""
    if 'bg_color' not in st.session_state: st.session_state.bg_color = '#120202'
    if 'text_color' not in st.session_state: st.session_state.text_color = '#FFFFFF'
    if 'border_color' not in st.session_state: st.session_state.border_color = '#00FF41'
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user' not in st.session_state: st.session_state.user = "GUEST"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except:
            pass

# ==============================================================================
# 2. UI & CSS ENGINE (ลบติ่ง + คุมธีม) (บรรทัดที่ 50+)
# ==============================================================================
def apply_ui_engine():
    bg = st.session_state.bg_color
    txt = st.session_state.text_color
    brd = st.session_state.border_color
    
    st.markdown(f"""
        <style>
        /* ลบส่วนเกิน Streamlit */
        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stAppToolbar {{display: none;}}
        #MainMenu {{visibility: hidden;}}
        button[title="Manage app"] {{display: none;}}
        .block-container {{ padding: 0rem 1rem; }}
        
        /* คุมโทนสีระบบ */
        .stApp {{ background-color: {bg} !important; color: {txt} !important; }}
        h1, h2, h3, h4, p, span, label, .stMarkdown, .stCaption {{ color: {txt} !important; }}

        /* ดีไซน์ NAVIGATION TABS */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(0,0,0,0.7) !important;
            border: 3px solid {brd} !important;
            border-radius: 20px !important;
            box-shadow: 0 0 20px {brd}55;
            padding: 10px !important;
            margin-top: 10px !important;
        }}
        .stTabs [data-baseweb="tab"] {{ color: {txt} !important; font-weight: bold; }}
        .stTabs [aria-selected="true"] {{ background-color: {brd}33 !important; border-radius: 10px; }}

        /* กล่อง LOGIC BOX (รหัสคู่ขนาน) */
        .logic-box {{
            background: rgba(0, 0, 0, 0.8);
            border: 4px solid {brd};
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 0 25px {brd}66;
            margin-bottom: 20px;
        }}

        /* ดีไซน์ปุ่ม */
        div.stButton > button {{
            background: linear-gradient(145deg, #000, #222) !important;
            color: {txt} !important;
            border: 2px solid {brd} !important;
            border-radius: 12px !important;
            transition: 0.3s;
        }}
        div.stButton > button:hover {{
            box-shadow: 0 0 15px {brd};
            transform: scale(1.02);
        }}
        </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 3. UTILITY FUNCTIONS (บรรทัดที่ 100+)
# ==============================================================================
def get_local_time(lat, lon):
    try:
        tf = TimezoneFinder()
        tz_str = tf.timezone_at(lng=lon, lat=lat)
        if tz_str:
            return datetime.datetime.now(pytz.timezone(tz_str))
        return datetime.datetime.now()
    except:
        return datetime.datetime.now()

def get_reality_logic(dt):
    """สูตรคำนวณรหัสคู่ขนาน"""
    ref_date = datetime.date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    if pos <= 14.765:
        m_num = int(pos) + 1
        res = math.sqrt((day_val**2) + (m_num**2))
        phase = f"ขึ้น {m_num} ค่ำ"
    else:
        m_num = int(pos - 14.765) + 1
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        phase = f"แรม {m_num} ค่ำ"
    return {"res": round(res, 4), "phase": phase}

def show_logo():
    brd = st.session_state.border_color
    if os.path.exists("logo1.png"):
        with open("logo1.png", "rb") as f:
            data = base64.b64encode(f.read()).decode()
        st.markdown(f'<div style="text-align:center; padding-top:10px;"><img src="data:image/png;base64,{data}" style="width:180px; filter:drop-shadow(0 0 10px {brd});"></div>', unsafe_allow_html=True)
    else:
        st.markdown(f"<h1 style='text-align:center; color:{brd}; text-shadow: 0 0 10px {brd};'>SYNAPSE OS</h1>", unsafe_allow_html=True)

# ==============================================================================
# 4. ROOM MODULES (บรรทัดที่ 150 - 450)
# ==============================================================================

# --- ROOM: LOGIN ---
def room_login():
    show_logo()
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown('<div class="logic-box">', unsafe_allow_html=True)
        st.subheader("🔐 AGENT ACCESS")
        uid = st.text_input("AGENT ID (เช่น Ta101)")
        pw = st.text_input("PASSWORD", type="password")
        if st.button("AUTHENTICATE", use_container_width=True):
            user_ref = db.reference(f'users/{uid}').get()
            if user_ref and user_ref.get('pw') == pw:
                st.session_state.user = uid
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("ACCESS DENIED")
        st.markdown('</div>', unsafe_allow_html=True)

# --- ROOM 0: CORE CONTROL ---
def room_core(loc):
    lat, lon = 13.7367, 100.5231
    if loc and 'coords' in loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
    
    current_time = get_local_time(lat, lon)
    brd = st.session_state.border_color
    st.markdown(f"""
        <div style="text-align:center; padding:40px; border:5px solid {brd}; border-radius:30px; background:rgba(0,0,0,0.7); box-shadow: 0 0 30px {brd}88; margin-top:20px;">
            <p style="letter-spacing:5px; opacity:0.7;">STAY STILL, NO PAIN</p>
            <h1 style="font-size:7em; color:{brd}; margin:0; font-family:monospace; text-shadow: 0 0 20px {brd};">
                {current_time.strftime('%H:%M:%S')}
            </h1>
            <h2 style="opacity:0.8;">{current_time.strftime('%A, %d %B %Y')}</h2>
            <hr style="border-color:{brd}; opacity:0.2;">
            <p style="color:#00FF41; font-family:monospace; font-size:1.2em;">📍 {lat:.6f}, {lon:.6f}</p>
            <h3 style="color:{brd};">AGENT: {st.session_state.user} [ONLINE]</h3>
        </div>
    """, unsafe_allow_html=True)

# --- ROOM 1: RADAR ---
def room_radar(loc):
    st.subheader("🛰️ STRATEGIC RADAR SCANNER")
    my_lat, my_lon = 13.7367, 100.5231
    if loc and 'coords' in loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']
    
    m = folium.Map(location=[my_lat, my_lon], zoom_start=14, tiles="https://mt1.google.com/vt/lyrs=y&x={{x}}&y={{y}}&z={{z}}", attr="Google")
    folium.Marker([my_lat, my_lon], tooltip="YOU", icon=folium.Icon(color='red')).add_to(m)
    
    # ดึงพิกัดเพื่อนๆ จาก Firebase
    try:
        all_users = db.reference('users').get()
        if all_users:
            for uid, data in all_users.items():
                if uid != st.session_state.user and 'lat' in data:
                    folium.Marker([data['lat'], data['lon']], tooltip=f"AGENT: {uid}", icon=folium.Icon(color='blue')).add_to(m)
    except: pass

    st_folium(m, width="100%", height=500)
    if st.button("📡 BROADCAST MY SIGNAL"):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.toast("Signal Sent!")

# --- ROOM 2: SCANNER (เลือกปี 1970 ได้) ---
def room_reality_scanner():
    min_d, max_d = datetime.date(1900, 1, 1), datetime.date.today()
    st.subheader("🧬 Reality & Code Scanner")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="logic-box">', unsafe_allow_html=True)
        st.write("### 🔍 สแกนรหัสส่วนบุคคล")
        dob = st.date_input("เลือกวันเกิด", value=datetime.date(1970, 1, 1), min_value=min_d, max_value=max_d, key="dob_scan")
        if dob:
            logic = get_reality_logic(dob)
            st.metric("REALITY CODE", logic['res'])
            st.write(f"**สภาวะ:** {logic['phase']}")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="logic-box">', unsafe_allow_html=True)
        st.write("### 🛰️ ตรวจสอบพิกัดรหัสคู่ขนาน")
        u1 = st.date_input("AGENT 1", value=datetime.date(1996, 8, 17), min_value=min_d, key="u1_scan")
        u2 = st.date_input("AGENT 2", value=max_d, min_value=min_d, key="u2_scan")
        if st.button("COMPUTE GAP"):
            r1, r2 = get_reality_logic(u1)['res'], get_reality_logic(u2)['res']
            gap = abs(r1 - r2)
            st.subheader(f"GAP RESULT: {gap:.4f}")
            if gap < 1.0: st.success("ระดับความสัมพันธ์: แนบแน่น")
        st.markdown('</div>', unsafe_allow_html=True)

# --- ROOM 3 & 4: CHAT & VOICE (ย่อส่วน) ---
def room_secure_chat():
    st.subheader("💬 SECURE CHAT")
    st.info("ระบบแชทเข้ารหัสเชื่อมต่อ Firebase พร้อมใช้งาน")
    # (โค้ดแชทเดิมของคุณทำงานได้ดีอยู่แล้ว สามารถใส่ตัวเต็มได้เลย)

def room_audio_call():
    st.subheader("📞 VOICE ENCRYPTION")
    st.warning("P2P Voice Channel: กรุณาเปิดไมโครโฟน")

# --- ROOM 5: MUSIC (พร้อม PLAYLIST) ---
def room_music():
    st.subheader("🎧 MUSIC STATION")
    files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if not files:
        st.error("ไม่พบไฟล์ MP3 ในโฟลเดอร์")
        return

    # แสดง Playlist
    with st.expander("📜 SHOW PLAYLIST SCANNER", expanded=True):
        playlist_html = ""
        for i, f in enumerate(files):
            active = f"border-left:5px solid {st.session_state.border_color}; background:rgba(255,255,255,0.1);" if i == st.session_state.song_index else ""
            playlist_html += f'<div style="padding:10px; margin:5px; border-radius:5px; {active}">🎵 {f}</div>'
        st.markdown(f'<div style="max-height:200px; overflow-y:auto;">{playlist_html}</div>', unsafe_allow_html=True)

    song = files[st.session_state.song_index]
    st.success(f"▶️ PLAYING: {song}")
    with open(song, "rb") as f:
        st.audio(f.read(), format="audio/mp3")

    c1, c2, c3 = st.columns(3)
    if c1.button("⏮️ PREV"):
        st.session_state.song_index = (st.session_state.song_index - 1) % len(files)
        st.rerun()
    if c3.button("⏭️ NEXT"):
        st.session_state.song_index = (st.session_state.song_index + 1) % len(files)
        st.rerun()

# --- ROOM 6: DESIGN CENTER ---
def room_design():
    st.markdown('<div class="logic-box">', unsafe_allow_html=True)
    st.subheader("🎨 DESIGN CONTROL CENTER")
    c1, c2, c3 = st.columns(3)
    bg = c1.color_picker("Background", st.session_state.bg_color)
    txt = c2.color_picker("Text Color", st.session_state.text_color)
    brd = c3.color_picker("Border/Neon", st.session_state.border_color)
    
    if st.button("APPLY VISUAL SETTINGS", use_container_width=True):
        st.session_state.bg_color, st.session_state.text_color, st.session_state.border_color = bg, txt, brd
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ==============================================================================
# 5. MAIN EXECUTION (บรรทัดที่ 450 - 500+)
# ==============================================================================
def main():
    init_system()
    apply_ui_engine()

    if not st.session_state.logged_in:
        room_login()
        return

    show_logo()
    
    # Sidebar สำหรับ Logout และข้อมูลเบื้องต้น
    with st.sidebar:
        st.markdown(f"### 👤 AGENT: {st.session_state.user}")
        st.write("---")
        if st.button("🚪 LOGOUT", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        st.write("'อยู่นิ่งๆ ไม่เจ็บตัว'")

    # แท็บนำทางหลัก (0-6)
    tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "🧬 SCANNER", "💬 CHAT", "📞 VOICE", "🎧 MUSIC", "🎨 DESIGN"])
    
    with tabs[0]: room_core(None) # ใส่ loc จริงถ้าได้พิกัด
    with tabs[1]: room_radar(None)
    with tabs[2]: room_reality_scanner()
    with tabs[3]: room_secure_chat()
    with tabs[4]: room_audio_call()
    with tabs[5]: room_music()
    with tabs[6]: room_design()

    # บรรทัดที่ 500: ปิดท้ายระบบ
    st.caption(f"SYNAPSE OS v4.5 Pro | System Status: Secure | {datetime.datetime.now().year}")

if __name__ == "__main__":
    main()
