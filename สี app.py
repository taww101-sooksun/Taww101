import streamlit as st
import os 
import time
import base64
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from math import radians, cos, sin, asin, sqrt
from folium.features import DivIcon

# ==========================================
# 0. ระบบพื้นฐาน & ชุดสีรุ้ง 3 เลเยอร์
# ==========================================
def init_system():
    if 'user' not in st.session_state: st.session_state.user = "Ta101"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    
    # CSS ชุดสีรุ้ง 3 รูปแบบ (ข้อความ, กรอบไฟวิ่ง, พื้นหลัง)
    rainbow_style = """
    <style>
    @keyframes rainbow_text { 0% {color: #ff0000;} 20% {color: #ffff00;} 40% {color: #00ff00;} 60% {color: #00ffff;} 80% {color: #0000ff;} 100% {color: #ff00ff;} }
    @keyframes rainbow_border { 0% {border-color: #ff0000; box-shadow: 0 0 10px #ff0000;} 33% {border-color: #00ff00; box-shadow: 0 0 10px #00ff00;} 66% {border-color: #0000ff; box-shadow: 0 0 10px #0000ff;} 100% {border-color: #ff0000; box-shadow: 0 0 10px #ff0000;} }
    @keyframes rainbow_bg { 0% {background-color: #050505;} 50% {background-color: #0a0010;} 100% {background-color: #050505;} }

    .rainbow-text { animation: rainbow_text 3s linear infinite; font-weight: bold; }
    .rainbow-box { border: 3px solid; padding: 20px; border-radius: 15px; animation: rainbow_border 4s linear infinite; background: rgba(0,0,0,0.8); }
    .stApp { animation: rainbow_bg 10s ease infinite; color: #FFFFFF !important; }
    
    /* ปรับแต่งปุ่มให้เข้ากับธีม */
    .stButton>button { border: 2px solid white !important; background: transparent !important; color: white !important; border-radius: 10px; }
    .stButton>button:hover { animation: rainbow_border 1s linear infinite; }
    </style>
    """
    st.markdown(rainbow_style, unsafe_allow_html=True)
    
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except: pass

def show_logo():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        try:
            # ใช้รูปโลโก้ที่นายส่งมา
            st.image("1000014112.jpg", use_container_width=True)
        except:
            st.markdown("<h1 class='rainbow-text' style='text-align:center;'>SYNAPSE PRO</h1>", unsafe_allow_html=True)

# ==========================================
# 1. ฟังก์ชันช่วยคำนวณ (Helper)
# ==========================================
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    d = 2 * asin(sqrt(sin((lat2-lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2-lon1)/2)**2)) 
    return d * 6371

# ==========================================
# 2. พื้นที่การทำงาน (Modules)
# ==========================================

def room_core():
    st.markdown("<h2 class='rainbow-text'>🚀 COMMAND CENTER</h2>", unsafe_allow_html=True)
    now = datetime.utcnow() + timedelta(hours=7)
    st.markdown(f"""
        <div class="rainbow-box" style="text-align: center;">
            <h1 style="font-size: 3.5em; margin:0;">{now.strftime('%H:%M:%S')}</h1>
            <p class="rainbow-text" style="letter-spacing: 5px;">SYSTEM ONLINE</p>
        </div>
    """, unsafe_allow_html=True)
    st.write(f"👤 AGENT ID: **{st.session_state.user}**")
    st.markdown("🚩 SLOGAN: **'อยู่นิ่งๆ ไม่เจ็บตัว'**")

def room_radar():
    st.subheader("🛰️ SAT RADAR (Hybrid View)")
    loc = get_geolocation()
    my_lat, my_lon = (loc['coords']['latitude'], loc['coords']['longitude']) if loc else (13.7367, 100.5231)
    
    # ใช้ Google Hybrid Map เห็นทั้งภาพจริงและชื่อซอย
    m = folium.Map(location=[my_lat, my_lon], zoom_start=17, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google")
    
    # หมุดเรา
    folium.Marker([my_lat, my_lon], icon=folium.Icon(color='red', icon='user', prefix='fa')).add_to(m)
    folium.Marker([my_lat - 0.0001, my_lon], icon=DivIcon(html=f'<div style="font-size:10pt; color:red; font-weight:bold; background:rgba(255,255,255,0.8); padding:2px;">📍 YOU</div>')).add_to(m)

    # ดึงพิกัดเพื่อน
    users = db.reference('users').get()
    if users:
        for uid, d in users.items():
            if uid != st.session_state.user and 'lat' in d:
                dist = haversine(my_lat, my_lon, d['lat'], d['lon'])
                folium.Marker([d['lat'], d['lon']], icon=folium.Icon(color='green')).add_to(m)
                folium.Marker([d['lat'] - 0.0001, d['lon']], icon=DivIcon(html=f'<div style="font-size:9pt; color:green; font-weight:bold; background:rgba(255,255,255,0.8); padding:2px;">👤 {uid} ({dist:.2f}km)</div>')).add_to(m)

    st_folium(m, width="100%", height=450)
    if st.button("📡 แชร์พิกัดของฉันลงกลุ่ม", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.success("อัปเดตตำแหน่งแล้ว!")

def room_music():
    st.markdown("<h2 class='rainbow-text'>🎧 MUSIC STATION</h2>", unsafe_allow_html=True)
    music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if not music_files:
        st.warning(" ไม่พบไฟล์เพลง .mp3")
        return

    # แสดงปกเพลง (ใช้รูปที่นายส่งมา)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("1000014112.jpg", use_container_width=True)
    with col2:
        current_song = music_files[st.session_state.song_index]
        st.write(f"🎵 Now Playing:")
        st.markdown(f"<h3 class='rainbow-text'>{current_song}</h3>", unsafe_allow_html=True)
        with open(current_song, "rb") as f:
            st.audio(f.read(), format="audio/mp3")

    with st.expander("📂 รายชื่อเพลงทั้งหมด"):
        for i, s in enumerate(music_files):
            if st.button(f"{'▶️' if i==st.session_state.song_index else '🎵'} {s}", key=f"s_{i}", use_container_width=True):
                st.session_state.song_index = i
                st.rerun()

# ==========================================
# 3. ส่วนควบคุมหลัก (Main)
# ==========================================
def main():
    st.set_page_config(page_title="SYNAPSE RAINBOW", layout="wide")
    init_system()
    
    # ส่วน Sidebar
    with st.sidebar:
        show_logo()
        st.markdown("<h2 class='rainbow-text' style='text-align:center;'>SETTINGS</h2>", unsafe_allow_html=True)
        st.write(f"AGENT: **{st.session_state.user}**")
        st.write("---")
        st.markdown('สโลแกน: **"อยู่นิ่งๆ ไม่เจ็บตัว"**')

    # ส่วน Tab ต่างๆ
    tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "🎧 MUSIC", "📟 SENSOR"])
    
    with tabs[0]: room_core()
    with tabs[1]: room_radar()
    with tabs[2]: room_music()
    with tabs[3]: 
        from room_sensor_module import room_sensor # สมมติว่าแยกโมดูลไว้
        try: room_sensor()
        except: st.info("กำลังเตรียมระบบวัดคลื่นเสียง...")

if __name__ == "__main__":
    main()
