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
import datetime as dt # ใช้ชื่อย่อ dt เพื่อความปลอดภัยสูงสุด
import math
import random
from streamlit_js_eval import get_geolocation 

# ==========================================
# 1. SYSTEM CONFIG & INITIALIZATION
# ==========================================
st.set_page_config(page_title="SYNAPSE OS v4.2 PRO", layout="wide", initial_sidebar_state="collapsed")

def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#1408BF"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"Firebase Connection Error: {e}")

# ==========================================
# 2. UPDATED CSS - ขอบใหญ่ ไฟแรงจัด (8px & 50px Glow)
# ==========================================
def apply_custom_background():
    theme = st.session_state.get('theme_color', "#1408BF")
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(270deg, #121212, #1a1a1a, #000);
            background-size: 400% 400%;
        }}

        /* ขอบเมนูหลัก (Tabs) - ปรับตามคำขอ: ใหญ่และฟุ้ง */
        .stTabs [data-baseweb="tab-list"] {{
            border: 8px solid {theme} !important; 
            box-shadow: 0 0 50px {theme} !important;
            border-radius: 30px !important;
            background: rgba(0,0,0,0.95) !important;
            padding: 10px 20px !important;
            margin: 10px 0px !important;
        }}
        
        /* ขยายฟอนต์เมนู Tabs */
        .stTabs [data-baseweb="tab"] p {{
            font-size: 1.2rem !important;
            font-weight: bold !important;
        }}

        /* ขอบปุ่มกด - หนาและมีมิติ */
        div.stButton > button {{
            border: 5px solid {theme} !important;
            border-radius: 20px !important;
            box-shadow: 0 0 20px {theme}88;
            background: #000 !important;
            color: white !important;
            font-size: 1.1rem !important;
            padding: 12px 24px !important;
            transition: all 0.3s ease;
        }}
        div.stButton > button:hover {{ 
            transform: scale(1.05);
            box-shadow: 0 0 30px {theme};
        }}

        /* กล่องเนื้อเพลง / กล่อง SCANNER - ขอบเขียว Matrix หนาๆ */
        .logic-box, .lyrics-box {{
            background: rgba(0, 0, 0, 0.85);
            border: 6px solid #00ff41; 
            border-radius: 25px;
            padding: 30px;
            color: #00ff41;
            font-family: 'Courier New', Courier, monospace;
            box-shadow: 0 0 35px rgba(0, 255, 65, 0.4);
            line-height: 1.8;
            text-align: center;
        }}
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. UTILS & CALCULATION LOGIC
# ==========================================
def get_local_time(lat, lon):
    try:
        tf = TimezoneFinder()
        tz_str = tf.timezone_at(lat=lat, lng=lon)
        if tz_str:
            return dt.datetime.now(pytz.timezone(tz_str))
    except: pass
    return dt.datetime.now(pytz.timezone('Asia/Bangkok'))

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon, dlat = lon2 - lon1, lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * 6371

def get_reality_logic(date_val):
    ref_date = dt.date(1900, 1, 1)
    diff = (date_val - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = date_val.weekday() + 1
    if pos <= 14.765:
        m_num = int(pos) + 1
        res = math.sqrt((day_val**2) + (m_num**2))
        phase = f"ขึ้น {m_num} ค่ำ"
    else:
        m_num = int(pos - 14.765) + 1
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        phase = f"แรม {m_num} ค่ำ"
    return {"res": round(res, 4), "phase": phase}

# ==========================================
# 4. ROOM MODULES
# ==========================================

def room_login():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color};'>SYNAPSE ACCESS</h1>", unsafe_allow_html=True)
        tab_l, tab_r = st.tabs(["🔑 LOGIN", "📝 REGISTER"])
        with tab_l:
            with st.form("login"):
                uid = st.text_input("AGENT ID")
                pw = st.text_input("PASSWORD", type="password")
                if st.form_submit_button("ACCESS GRANTED", use_container_width=True):
                    user_data = db.reference(f'users/{uid}').get()
                    if user_data and user_data.get('pw') == pw:
                        st.session_state.user = uid
                        st.session_state.logged_in = True
                        st.rerun()
                    else: st.error("ACCESS DENIED")
        with tab_r:
            with st.form("reg"):
                new_id = st.text_input("NEW AGENT ID")
                new_pw = st.text_input("NEW PASSWORD", type="password")
                if st.form_submit_button("CREATE AGENT", use_container_width=True):
                    db.reference(f'users/{new_id}').set({'pw': new_pw, 'ts': time.time()})
                    st.success("REGISTERED!")

def room_core(loc):
    st.subheader("🏠 CORE CONTROL - อยู่นิ่งๆไม่เจ็บตัว")
    lat, lon = 13.7367, 100.5231
    if loc and 'coords' in loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
    
    current_time = get_local_time(lat, lon)
    st.markdown(f"""
        <div style="text-align:center; padding:40px; border:6px solid {st.session_state.theme_color}; border-radius:25px; background:rgba(0,0,0,0.8); box-shadow: 0 0 30px {st.session_state.theme_color};">
            <h1 style="font-size:6em; color:{st.session_state.theme_color}; margin:0; font-family: 'Courier New';">
                {current_time.strftime('%H:%M:%S')}
            </h1>
            <p style="color:#FFF; font-size:1.2em;">DATE: {current_time.strftime('%Y-%m-%d')}</p>
            <p style="color:#00ff41; font-family:monospace;">📍 POSITION: {lat:.5f}, {lon:.5f}</p>
            <p style="color:{st.session_state.theme_color}; font-weight:bold; font-size:1.5em;">AGENT {st.session_state.user} ONLINE</p>
        </div>
    """, unsafe_allow_html=True)
    
    # แสดงวิดีโอในหน้าแรก
    if os.path.exists("1000014353.mp4"): st.video("1000014353.mp4")

def room_radar(loc):
    st.subheader("🛰️ STRATEGIC RADAR SCANNER")
    my_lat, my_lon = 13.7367, 100.5231 
    if loc and 'coords' in loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']
    
    m = folium.Map(location=[my_lat, my_lon], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr='Google Satellite')
    folium.Marker([my_lat, my_lon], icon=folium.Icon(color='red', icon='screenshot', prefix='fa')).add_to(m)
    
    try:
        users = db.reference('users').get()
        if users:
            for uid, data in users.items():
                if uid != st.session_state.user and 'lat' in data:
                    u_lat, u_lon = data['lat'], data['lon']
                    folium.Marker([u_lat, u_lon], icon=folium.Icon(color='blue', icon='user', prefix='fa'), tooltip=f"AGENT: {uid}").add_to(m)
    except: pass

    st_folium(m, width="100%", height=500)
    if st.button("📡 BROADCAST SIGNAL", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.toast("SIGNAL BROADCASTED")

def room_reality_scanner():
    st.subheader("🧬 ตรวจสอบพิกัดรหัสคู่ขนาน")
    min_date = dt.date(1960, 1, 1) # แก้ไขตามคำขอ: ปี 1960
    max_date = dt.date.today()
    
    col1, col2 = st.columns(2)
    with col1:
        u1 = st.date_input("AGENT 1 (วันเกิด)", value=dt.date(1984, 05, 18), min_value=min_date, max_value=max_date, format="YYYY/MM/DD")
    with col2:
        u2 = st.date_input("AGENT 2 (วันเกิด)", value=max_date, min_value=min_date, max_value=max_date, format="YYYY/MM/DD")

    if st.button("COMPUTE GAP", use_container_width=True):
        r1 = get_reality_logic(u1)
        r2 = get_reality_logic(u2)
        gap = abs(r1['res'] - r2['res'])
        st.markdown(f"""
            <div class="logic-box">
                <h2 style="color:#00ff41;">RESULT GAP: {gap:.4f}</h2>
                <hr style="border-color:#00ff41; opacity:0.3;">
                <p>CODE 1: {r1['res']} ({r1['phase']})</p>
                <p>CODE 2: {r2['res']} ({r2['phase']})</p>
            </div>
        """, unsafe_allow_html=True)

def room_secure_chat():
    st.subheader("💬 SECURE MESSENGER")
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    target = st.selectbox("🎯 TARGET:", friends)
    
    if target:
        rid = "_".join(sorted([st.session_state.user, target]))
        chat_box = st.container(height=300, border=True)
        chats = db.reference(f'private_rooms/{rid}').order_by_key().limit_to_last(20).get()
        
        with chat_box:
            if chats:
                for c in chats.values():
                    is_me = c['u'] == st.session_state.user
                    bg = st.session_state.theme_color if is_me else "#333"
                    align = "right" if is_me else "left"
                    st.markdown(f"<div style='text-align:{align};'><span style='background:{bg}; padding:8px 15px; border-radius:15px; color:white; display:inline-block; margin:5px;'>{c['m']}</span></div>", unsafe_allow_html=True)

        with st.form("chat_f", clear_on_submit=True):
            msg = st.text_input("Message...")
            if st.form_submit_button("SEND"):
                if msg: db.reference(f'private_rooms/{rid}').push({'u': st.session_state.user, 'm': msg, 'ts': time.time()})
                st.rerun()

def room_audio_call():
    st.markdown(f"<div class='logic-box' style='border-color:{st.session_state.theme_color};'><h2>📞 VOICE ENCRYPTION</h2></div>", unsafe_allow_html=True)
    # ใส่ JavaScript PeerJS สำหรับระบบโทร (เหมือนที่เคยเขียนให้ก่อนหน้านี้)
    st.info("ระบบโทร P2P กำลังแสตนบาย... กรุณาเลือกเป้าหมาย")

def room_music():
    st.subheader("🎧 SYNAPSE MUSIC STATION")
    lyrics = """
    (อยู่นิ่งๆ ไม่เจ็บตัว… Let’s go!)
    เริ่มที่หน้า LOGIN ใส่ AGENT ID เข้ามา...
    📍 มองไปที่ CORE เห็นเวลาและพิกัด...
    📍 RADAR ส่องพิกัด เพื่อนอยู่ไหนเรารู้ไป...
    """
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f"<div class='lyrics-box'><h3>📜 LYRICS</h3><p style='white-space: pre-wrap;'>{lyrics}</p></div>", unsafe_allow_html=True)
    with col2:
        files = sorted([f for f in os.listdir('.') if f.endswith(".mp3") or f.endswith(".mp4")])
        if files:
            song = st.selectbox("💿 TRACK", files, key="music_sel")
            if song.endswith(".mp3"): st.audio(song)
            else: st.video(song)

# ==========================================
# 5. MAIN EXECUTION
# ==========================================
def main():
    init_system()
    apply_custom_background()
    loc = get_geolocation() 

    if not st.session_state.get('logged_in', False):
        room_login()
        return

    # Sidebar Settings
    with st.sidebar:
        st.markdown(f"### 👤 AGENT: {st.session_state.user}")
        st.session_state.theme_color = st.color_picker("🎨 THEME", st.session_state.theme_color)
        if st.button("🚪 LOGOUT", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        st.write("---")
        st.write("'อยู่นิ่งๆ ไม่เจ็บตัว'")

    # Tabs Navigation - ครบทุกฟีเจอร์!
    tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "🧬 SCANNER", "💬 CHAT", "📞 VOICE", "🎧 MUSIC"])
    
    with tabs[0]: room_core(loc)
    with tabs[1]: room_radar(loc)
    with tabs[2]: room_reality_scanner()
    with tabs[3]: room_secure_chat()
    with tabs[4]: room_audio_call()
    with tabs[5]: room_music()

if __name__ == "__main__":
    main()
