import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import pytz
import os
import time
import random
import string
import pandas as pd
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. SETUP & THEME
# ==========================================
st.set_page_config(page_title="SYNAPSE V2", layout="wide")
st_autorefresh(interval=5000, key="global_refresh")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #001 0%, #000 100%); color: #00f2fe; font-family: 'Courier New', Courier, monospace; }
    .neon-header { 
        font-size: 35px; font-weight: 900; text-align: center;
        color: #fff; text-shadow: 0 0 10px #00f2fe, 0 0 20px #ff00de;
        border: 2px solid #00f2fe; padding: 10px; background: rgba(0,0,0,0.8);
        border-radius: 10px; margin-bottom: 20px; letter-spacing: 10px;
    }
    .terminal-container {
        border: 1px solid #00f2fe; padding: 15px; border-radius: 8px;
        background: rgba(0, 242, 254, 0.05); border-left: 5px solid #ff00de;
        margin-bottom: 15px;
    }
    .clock-box {
        background: rgba(0,0,0,0.5); border: 1px solid #00f2fe;
        padding: 5px; border-radius: 5px; text-align: center; font-size: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FIREBASE & LOGO
# ==========================================
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_dict = dict(st.secrets["firebase"])
            if "private_key" in fb_dict:
                fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            creds = credentials.Certificate(fb_dict)
            firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except: pass

col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    if os.path.exists("logo3.jpg"):
        st.image("logo3.jpg", width=400)
    st.markdown('<div class="neon-header">SYNAPSE</div>', unsafe_allow_html=True)

# ==========================================
# 3. WORLD CLOCK (นาฬิกาทั่วโลก)
# ==========================================
st.markdown("### 🌐 GLOBAL WORLD TIME")
c1, c2, c3, c4 = st.columns(4)
zones = {'BANGKOK': 'Asia/Bangkok', 'NEW YORK': 'America/New_York', 'LONDON': 'Europe/London', 'TOKYO': 'Asia/Tokyo'}
cols = [c1, c2, c3, c4]
for col, (city, zone) in zip(cols, zones.items()):
    now = datetime.datetime.now(pytz.timezone(zone)).strftime('%H:%M:%S')
    col.markdown(f"<div class='clock-box'><b>{city}</b><br><span style='color:#ff00de;'>{now}</span></div>", unsafe_allow_html=True)

# ==========================================
# 4. SIDEBAR & AUDIO
# ==========================================
audio_file = "ฉันผิดเองที่เดินหนี้ความจริง.mp3"
with st.sidebar:
    st.markdown("### 🛰️ NETWORK")
    if os.path.exists(audio_file): st.audio(audio_file, format="audio/mp3", loop=True)
    st.markdown("---")
    st.write(f"SYSTEM SYNC: {datetime.datetime.now().strftime('%H:%M:%S')}")

# ==========================================
# 5. MAIN TABS
# ==========================================
tabs = st.tabs(["🚀 แกนหลัก", "🛰️ เรดาร์", "💬 การสื่อสาร", "📊 บันทึก", "🔐 SEC", "📺 สื่อมวลชน", "🧹 ระบบ"])

# --- TAB 1: CORE (GPS กลับมาแล้ว) ---
with tabs[0]:
    st.markdown('<div class="terminal-container">[ SATELLITE_LINK_PROTOCOL ]</div>', unsafe_allow_html=True)
    name = st.text_input("ระบุชื่อรหัสของคุณ:", value=st.session_state.get('my_name', 'Agent_X'))
    st.session_state.my_name = name
    
    if st.button("🚀 INITIATE GPS TRACKING"):
        loc = get_geolocation()
        if loc:
            lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
            db.reference(f'users/{name}').set({
                'lat': lat, 'lon': lon,
                'time': datetime.datetime.now().strftime('%H:%M:%S'),
                'status': 'ONLINE'
            })
            st.success(f"พิกัดถูกส่งเข้าดาวเทียม: {lat}, {lon}")
        else:
            st.warning("กรุณากดอนุญาตให้เข้าถึงพิกัด (GPS)")

# --- TAB 2: RADAR (โชว์มุดบนแผนที่) ---
with tabs[1]:
    st.markdown('<div class="terminal-container">[ GLOBAL_LIVE_RADAR ]</div>', unsafe_allow_html=True)
    users = db.reference('users').get()
    m = folium.Map(location=[13.75, 100.5], zoom_start=2, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google")
    if users:
        for u_name, info in users.items():
            if isinstance(info, dict) and 'lat' in info:
                folium.Marker([info['lat'], info['lon']], popup=u_name, icon=folium.Icon(color='red', icon='info-sign')).add_to(m)
    st_folium(m, width="100%", height=500)

# --- TAB 3: COMMS (แชทใช้งานได้) ---
with tabs[2]:
    st.markdown('<div class="terminal-container">[ SECURE_CHAT ]</div>', unsafe_allow_html=True)
    with st.form("chat_form", clear_on_submit=True):
        msg = st.text_input("พิมพ์ข้อความลับ...")
        if st.form_submit_button("TRANSMIT") and msg:
            db.reference('global_chat').push({'user': st.session_state.my_name, 'msg': msg, 'ts': time.time()})
    
    chats = db.reference('global_chat').order_by_child('ts').limit_to_last(8).get()
    if chats:
        for v in reversed(chats.values()):
            st.write(f"**{v.get('user')}**: {v.get('msg')}")

# --- TAB 5: SEC ---
with tabs[4]:
    if st.button("🔑 GENERATE KEY"):
        st.code(''.join(random.choices(string.ascii_uppercase + string.digits, k=16)))

# --- TAB 6: MEDIA ---
with tabs[5]:
    st.video("https://www.youtube.com/watch?v=F3zR5W0Bv0U")

# --- TAB 7: SYS ---
with tabs[6]:
    if st.button("💣 WIPE SYSTEM"):
        db.reference('users').delete()
        st.success("ข้อมูลพิกัดถูกล้างแล้ว")
