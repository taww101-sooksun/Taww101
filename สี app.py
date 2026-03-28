import streamlit as st
import os
import random
import time
import requests
import pytz
import folium
import firebase_admin
import streamlit.components.v1 as components
from datetime import datetime
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from firebase_admin import credentials, db

# --- 1. SET UP & THEME ---
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")

# ระบบจำค่าสีและสถานะ Login
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14" 
if 'bg_color' not in st.session_state: st.session_state.bg_color = "#121212" 
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'lang' not in st.session_state: st.session_state.lang = "TH"

# --- 2. INITIALIZE FIREBASE (ใช้ Secrets จาก sooksun1) ---
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_service_account"]) # หรือ "firebase" ตามที่พี่ตั้งใน Secrets
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {'databaseURL': 'https://sooksun1-default-rtdb.firebaseio.com/'})
    except: pass

# --- 3. SECURITY GATE (ด่านล็อกอิน) ---
if not st.session_state.authenticated:
    st.markdown("""<style>.stApp { background: #000; }</style>""", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<div style='padding:20px; border:2px solid #39FF14; border-radius:15px; background:rgba(0,0,0,0.8);'>", unsafe_allow_html=True)
        st.subheader("🔐 SYNAPSE ACCESS")
        u_id = st.text_input("ID")
        u_pw = st.text_input("Password", type="password")
        if st.button("UNLOCK"):
            if u_pw == "99999999" and u_id:
                st.session_state.authenticated = True
                st.session_state.my_id = u_id
                st.rerun()
            else: st.error("Unauthorized!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 4. DYNAMIC CSS (สไตล์นีออนผสมรุ้งเงา) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    .stApp {{ background-color: {st.session_state.bg_color} !important; color: {st.session_state.theme_color} !important; }}
    .glossy-card {{ background: rgba(0, 0, 0, 0.85); border: 2px solid {st.session_state.theme_color}; border-radius: 15px; padding: 20px; box-shadow: 0 0 15px {st.session_state.theme_color}; margin-bottom: 15px; }}
    .marquee {{
        width: 100%; overflow: hidden; white-space: nowrap; background: rgba(0,0,0,0.6);
        padding: 15px 0; border-radius: 12px; margin-bottom: 15px; border: 2px solid {st.session_state.theme_color};
    }}
    .marquee p {{
        display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite;
        font-family: 'Orbitron', sans-serif; font-size: 22px; color: {st.session_state.theme_color};
    }}
    @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
    h1, h2, h3, p, span {{ font-family: 'Orbitron', sans-serif; color: {st.session_state.theme_color} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR CONTROL ---
with st.sidebar:
    # แก้ปัญหา NameError: เช็คไฟล์ก่อนโชว์
    logo_file = "logo2.jpg" if os.path.exists("logo2.jpg") else "logo3.jpg" if os.path.exists("logo3.jpg") else None
    if logo_file: st.image(logo_file, use_container_width=True)
    
    st.markdown("### 🎨 SYSTEM CONTROL")
    st.session_state.theme_color = st.color_picker("นีออน", st.session_state.theme_color)
    if st.button("🌐 Switch TH/EN"):
        st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"
        st.rerun()
    st.write("---")
    st.write('**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

# --- 6. REALITY CORE (GPS & WEATHER) ---
location = get_geolocation()
if location and location.get('coords'):
    lat, lon = location['coords']['latitude'], location['coords']['longitude']
    
    # ดึงเวลาและสภาพอากาศจริง
    try:
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lng=lon, lat=lat)
        now = datetime.now(pytz.timezone(tz_name)).strftime('%H:%M:%S')
        w = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()['current_weather']
        temp = w['temperature']
    except: now, temp = "--:--:--", "--"

    st.markdown(f"""
    <div class="glossy-card">
        <div style='display: flex; justify-content: space-around; font-size: 1.2rem;'>
            <span>📍 LAT: {lat:.4f} | LON: {lon:.4f}</span>
            <span style='color: yellow;'>⏰ TIME: {now}</span>
            <span style='color: #00ffff;'>🌡️ TEMP: {temp}°C</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 7. MAIN INTERFACE (MUSIC + MAP) ---
col_main, col_sub = st.columns([2, 1])

with col_main:
    # --- MUSIC SYSTEM ---
    music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if music_files:
        if 'song_index' not in st.session_state: st.session_state.song_index = 0
        current_song = music_files[st.session_state.song_index]
        st.markdown(f'<div class="marquee"><p>NOW PLAYING: {current_song} •--• NEXT TRACK UP SOON </p></div>', unsafe_allow_html=True)
        
        # ภาพ/วิดีโอประกอบ
        base_name = os.path.splitext(current_song)[0]
        if os.path.exists(base_name + ".mp4"): st.video(base_name + ".mp4", loop=True, autoplay=True, muted=True)
        elif os.path.exists(base_name + ".jpg"): st.image(base_name + ".jpg", use_container_width=True)
        
        st.audio(current_song)
        
        c1, c2 = st.columns(2)
        with c1: 
            if st.button("⏭️ เพลงถัดไป"): 
                st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
                st.rerun()
        with c2:
            if st.button("🎲 สุ่มเพลง"):
                st.session_state.song_index = random.randint(0, len(music_files)-1)
                st.rerun()
    
with col_sub:
    # --- RADAR MAP ---
    if location:
        m = folium.Map(location=[lat, lon], zoom_start=17, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')
        folium.Marker([lat, lon], icon=folium.Icon(color='red', icon='info-sign')).add_to(m)
        st_folium(m, height=400, use_container_width=True, key="synapse_map")

# --- 8. COMMUNICATION (JITSI) ---
with st.expander("📞 COMMUNICATION SYSTEM (JITSI)"):
    call_room = st.text_input("Room ID", "synapse_secure")
    if st.button("🚀 START CONNECTION"):
        components.html(f"""
            <iframe src="https://meet.jit.si/SYNAPSE_{call_room}" allow="camera; microphone; fullscreen" width="100%" height="500"></iframe>
        """, height=520)

# --- 9. FIREBASE LOGS ---
st.markdown("---")
with st.form("status_update"):
    status_msg = st.text_input("ส่งสถานะเข้าฐานข้อมูล:", value="System Online")
    if st.form_submit_button("🚀 UPDATE DATABASE"):
        try:
            db.reference('logs').push({'id': st.session_state.my_id, 'msg': status_msg, 'ts': time.time()})
            st.success("บันทึกข้อมูลเรียบร้อย!")
        except: st.error("Firebase Sync Failed!")

# Footer YouTube
pid = "PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
st.markdown(f'<iframe width="100%" height="150" src="https://www.youtube.com/embed/videoseries?list={pid}" frameborder="0"></iframe>', unsafe_allow_html=True)
