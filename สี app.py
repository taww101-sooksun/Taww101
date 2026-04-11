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
from datetime import datetime, date
import math
import random
from streamlit_js_eval import get_geolocation 

# ==========================================
# 1. SYSTEM CONFIG & UI HIDING
# ==========================================
st.set_page_config(layout="wide", page_title="SYNAPSE", page_icon="⚡")

# ซ่อน UI ของ Streamlit ให้กริบที่สุด
st.markdown("""
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppToolbar {display: none;}
    #MainMenu {visibility: hidden;}
    button[title="Manage app"] {display: none;}
    .block-container { padding-top: 0rem; padding-bottom: 0rem; }
    
    /* ตกแต่ง Tabs ให้ดูเป็นไซเบอร์ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(0,0,0,0.3);
        padding: 10px;
        border-radius: 15px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #1A1D21;
        border-radius: 10px;
        color: white;
        border: 1px solid #333;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE & INITIALIZATION
# ==========================================
if 'main_color' not in st.session_state: st.session_state.main_color = '#620909'
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'song_index' not in st.session_state: st.session_state.song_index = 0
if 'user' not in st.session_state: st.session_state.user = "Unknown"

# เชื่อมต่อ Firebase
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_credentials"])
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
    except Exception as e:
        st.error(f"Firebase Error: {e}")

# ==========================================
# 3. CORE LOGIC (สูตรคำนวณทั้งหมด)
# ==========================================
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon, dlat = lon2 - lon1, lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * 6371

def get_reality_logic(dt):
    ref_date = date(1900, 1, 1)
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

def get_local_time(lat, lon):
    try:
        tf = TimezoneFinder()
        tz_str = tf.timezone_at(lat=lat, lng=lon)
        return datetime.now(pytz.timezone(tz_str)) if tz_str else datetime.now()
    except: return datetime.now()

# ==========================================
# 4. CUSTOM UI COMPONENTS
# ==========================================
def draw_agent_card():
    # หน้าต่าง AGENT Ta103 ที่คุณต้องการ
    agent_html = f"""
    <div style="background-color: #1A1D21; border-radius: 15px; padding: 20px; color: white; border: 1px solid #333; box-shadow: 0 10px 20px rgba(0,0,0,0.5);">
        <div style="display: flex; align-items: center; font-size: 18px; font-weight: bold; gap: 10px;">👤 AGENT: {st.session_state.user}</div>
        <div style="color: #8C959F; font-size: 13px; margin-left: 32px; margin-bottom: 15px;">Status: AUTHENTICATED</div>
        <div style="background-color: #262B30; border-radius: 10px; padding: 15px;">
            <div style="font-size:11px; margin-bottom: 8px;">🎨 SYSTEM THEME (Neon)</div>
            <div style="width: 40px; height: 40px; background-color: {st.session_state.main_color}; border-radius: 5px; margin-bottom: 10px;"></div>
            <div style="width: 100%; height: 80px; background: linear-gradient(to bottom, white, transparent, black), linear-gradient(to right, transparent, {st.session_state.main_color}); background-color: {st.session_state.main_color}; border-radius: 8px;"></div>
        </div>
        <div style="background-color: #0D1117; padding: 10px; border-radius: 5px; text-align: center; font-family: monospace; font-size: 20px; margin-top: 15px; border: 1px solid #444;">{st.session_state.main_color}</div>
    </div>
    """
    st.sidebar.markdown(agent_html, unsafe_allow_html=True)

def draw_neon_lights():
    st.markdown(f"""
        <style>
        .neon-strip {{
            width: 100%; height: 8px;
            background: linear-gradient(90deg, #ff0000, {st.session_state.main_color}, #00ff00, {st.session_state.main_color}, #0000ff);
            background-size: 300% 300%; border-radius: 10px; margin: 10px 0;
            animation: RGBFlow 3s ease infinite;
        }}
        @keyframes RGBFlow {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
        </style>
        <div class="neon-strip"></div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. ROOMS / APP MODULES
# ==========================================
def room_login():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown(f"<h1 style='text-align:center; color:{st.session_state.main_color};'>SYNAPSE ACCESS</h1>", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input("AGENT ID")
            p = st.text_input("PASSWORD", type="password")
            if st.form_submit_button("LOGIN", use_container_width=True):
                user_data = db.reference(f'users/{u}').get()
                if user_data and user_data.get('pw') == p:
                    st.session_state.user = u
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("ACCESS DENIED")

def room_core(loc):
    lat, lon = (loc['coords']['latitude'], loc['coords']['longitude']) if loc else (13.7367, 100.5231)
    t = get_local_time(lat, lon)
    st.markdown(f"""
        <div style="text-align:center; padding:40px; border:4px solid {st.session_state.main_color}; border-radius:25px; background:rgba(0,0,0,0.6); box-shadow: 0 0 30px {st.session_state.main_color}88;">
            <h1 style="font-size:6em; color:{st.session_state.main_color}; margin:0; font-family: 'Courier New';">{t.strftime('%H:%M:%S')}</h1>
            <p style="color:#FFF; font-size:1.2em; letter-spacing: 4px;">DATE: {t.strftime('%Y-%m-%d')}</p>
            <p style="color:#00ff41; font-family:monospace;">📍 POSITION: {lat:.5f}, {lon:.5f}</p>
        </div>
    """, unsafe_allow_html=True)

def room_radar(loc):
    st.subheader("🛰️ STRATEGIC RADAR SCANNER")
    my_lat, my_lon = (loc['coords']['latitude'], loc['coords']['longitude']) if loc else (13.7367, 100.5231)
    m = folium.Map(location=[my_lat, my_lon], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr='Google')
    folium.Marker([my_lat, my_lon], icon=folium.Icon(color='red', icon='screenshot', prefix='fa')).add_to(m)
    
    # ดึงพิกัดคนอื่นจาก Firebase
    try:
        users = db.reference('users').get()
        if users:
            for uid, data in users.items():
                if uid != st.session_state.user and 'lat' in data:
                    folium.Marker([data['lat'], data['lon']], tooltip=f"AGENT: {uid}", icon=folium.Icon(color='blue')).add_to(m)
    except: pass
    st_folium(m, width="100%", height=500)
    
    if st.button("📡 BROADCAST SIGNAL", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.success("SIGNAL SENT")

def room_chat():
    st.subheader("💬 SECURE MESSENGER")
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    target = st.selectbox("🎯 TARGET:", friends)
    if target:
        rid = "_".join(sorted([st.session_state.user, target]))
        chats = db.reference(f'private_rooms/{rid}').order_by_key().limit_to_last(20).get()
        container = st.container(height=300)
        with container:
            if chats:
                for c in chats.values():
                    align = "right" if c['u'] == st.session_state.user else "left"
                    st.markdown(f"<div style='text-align:{align};'><p style='background:#333; display:inline-block; padding:8px; border-radius:10px;'>{c['u']}: {c['m']}</p></div>", unsafe_allow_html=True)
        
        msg = st.chat_input("Enter Message...")
        if msg:
            db.reference(f'private_rooms/{rid}').push({'u': st.session_state.user, 'm': msg, 'ts': time.time()})
            st.rerun()

def room_voice(target):
    st.subheader("📞 VOICE ENCRYPTION")
    call_js = f"""
    <div id="call-ui" style="background:#222; padding:20px; border-radius:15px; border:2px solid {st.session_state.main_color}; text-align:center;">
        <h3 id="status">📡 SYSTEM READY</h3>
        <audio id="remoteAudio" autoplay></audio>
        <button id="btn-call" style="background:{st.session_state.main_color}; color:white; padding:10px 20px; border:none; border-radius:10px;">START CALL</button>
    </div>
    <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
    <script>
        const peer = new Peer('{st.session_state.user}');
        document.getElementById('btn-call').onclick = () => {{
            navigator.mediaDevices.getUserMedia({{audio: true}}).then(stream => {{
                const call = peer.call('{target}', stream);
                call.on('stream', rem => {{ document.getElementById('remoteAudio').srcObject = rem; }});
                document.getElementById('status').innerText = "🎙️ CONNECTED";
            }});
        }};
        peer.on('call', call => {{
            if(confirm("Incoming Call?")) {{
                navigator.mediaDevices.getUserMedia({{audio: true}}).then(stream => {{
                    call.answer(stream);
                    call.on('stream', rem => {{ document.getElementById('remoteAudio').srcObject = rem; }});
                }});
            }}
        }});
    </script>
    """
    components.html(call_js, height=250)

def room_music():
    st.subheader("🎧 MUSIC STATION")
    files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if files:
        song = files[st.session_state.song_index]
        st.info(f"Streaming: {song}")
        with open(song, "rb") as f:
            st.audio(f.read(), format="audio/mp3")
        c1, c2, c3 = st.columns(3)
        if c1.button("PREV"): st.session_state.song_index = (st.session_state.song_index - 1) % len(files); st.rerun()
        if c3.button("NEXT"): st.session_state.song_index = (st.session_state.song_index + 1) % len(files); st.rerun()

# ==========================================
# 6. MAIN CONTROLLER
# ==========================================
def main():
    # บังคับสีพื้นหลังทั้งแอป
    st.markdown(f"<style>.stApp {{background-color: {st.session_state.main_color} !important; color: white !important;}}</style>", unsafe_allow_html=True)

    if not st.session_state.logged_in:
        room_login()
        return

    loc = get_geolocation()

    # Sidebar: หน้าต่าง AGENT และ Color Picker
    with st.sidebar:
        draw_agent_card()
        st.write("---")
        # ตัวเลือกสีหลัก (ทำให้แอปเปลี่ยนสีได้อิสระ)
        new_color = st.color_picker("🎛️ ADJUST SYSTEM COLOR", st.session_state.main_color)
        if new_color != st.session_state.main_color:
            st.session_state.main_color = new_color
            st.rerun()
        
        if st.button("🚪 LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()

    draw_neon_lights()

    # Navigation Tabs
    tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "🧬 SCANNER", "💬 CHAT", "📞 VOICE", "🎧 MUSIC"])
    
    with tabs[0]: room_core(loc)
    with tabs[1]: room_radar(loc)
    with tabs[2]: 
        dob = st.date_input("REALITY SCAN", value=date.today())
        st.write(get_reality_logic(dob))
    with tabs[3]: room_chat()
    with tabs[4]: 
        users = db.reference('users').get()
        target = st.selectbox("CALL TO:", [u for u in users.keys() if u != st.session_state.user]) if users else None
        if target: room_voice(target)
    with tabs[5]: room_music()

if __name__ == "__main__":
    main()
