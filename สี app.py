import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import pytz
import os
import time
import pandas as pd
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. SETUP & THEME
# ==========================================
st.set_page_config(page_title="SYNAPSE ULTIMATE", layout="wide")
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
        background: rgba(0,0,0,0.6); border: 1px solid #00f2fe;
        padding: 10px; border-radius: 8px; text-align: center;
    }
    .clock-time { color: #ff00de; font-size: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FIREBASE CONNECTION
# ==========================================
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_dict = dict(st.secrets["firebase"])
            if "private_key" in fb_dict:
                fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            creds = credentials.Certificate(fb_dict)
            firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except Exception as e:
        st.error(f"DATABASE ERROR: {e}")

# ==========================================
# 3. LOGO & WORLD CLOCK
# ==========================================
col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    if os.path.exists("logo3.jpg"):
        st.image("logo3.jpg", width=400)
    st.markdown('<div class="neon-header">SYNAPSE</div>', unsafe_allow_html=True)

st.markdown("### 🌐 GLOBAL REAL-TIME MONITOR")
c1, c2, c3, c4 = st.columns(4)
zones = {'BANGKOK': 'Asia/Bangkok', 'NEW YORK': 'America/New_York', 'LONDON': 'Europe/London', 'TOKYO': 'Asia/Tokyo'}
for col, (city, zone) in zip([c1, c2, c3, c4], zones.items()):
    now = datetime.datetime.now(pytz.timezone(zone)).strftime('%H:%M:%S')
    col.markdown(f"<div class='clock-box'><small>{city}</small><br><span class='clock-time'>{now}</span></div>", unsafe_allow_html=True)

# ==========================================
# 4. SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("### 🛰️ NETWORK CENTER")
    audio_file = "ฉันผิดเองที่เดินหนี้ความจริง.mp3"
    if os.path.exists(audio_file):
        st.audio(audio_file, format="audio/mp3", loop=True)
    st.write(f"UPTIME: {datetime.datetime.now().strftime('%H:%M:%S')}")

# ==========================================
# 5. MAIN NAVIGATION
# ==========================================
tabs = st.tabs(["🚀 แกนหลัก", "🛰️ เรดาร์", "💬 การสื่อสาร", "📊 บันทึก", "🔐 SEC", "📺 สื่อ", "🧹 ระบบ"])

# --- TAB 1: CORE (GPS) ---
with tabs[0]:
    st.markdown('<div class="terminal-container">[ GPS_INIT ]</div>', unsafe_allow_html=True)
    user_id = st.text_input("USER CODENAME:", value=st.session_state.get('user_id', 'Agent_001'))
    st.session_state.user_id = user_id
    if st.button("🛰️ ดึงพิกัด GPS"):
        loc = get_geolocation()
        if loc:
            db.reference(f'users/{user_id}').set({
                'lat': loc['coords']['latitude'], 
                'lon': loc['coords']['longitude'],
                'ts': time.time()
            })
            st.success("POSITION UPDATED")

# --- TAB 2: RADAR (FIXED SYNTAX) ---
with tabs[1]:
    st.markdown('<div class="terminal-container">[ RADAR_LIVE ]</div>', unsafe_allow_html=True)
    m = folium.Map(location=[13.75, 100.5], zoom_start=4, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
    try:
        users = db.reference('users').get()
        if users:
            for u, data in users.items():
                if isinstance(data, dict) and 'lat' in data and 'lon' in data:
                    folium.Marker(
                        location=[data['lat'], data['lon']], 
                        popup=u,
                        icon=folium.Icon(color='red', icon='info-sign')
                    ).add_to(m)
    except: pass
    st_folium(m, width="100%", height=500)

# --- TAB 3: COMMS ---
with tabs[2]:
    st.markdown('<div class="terminal-container">[ SECURE_CHAT ]</div>', unsafe_allow_html=True)
    webrtc_streamer(key="v-call", mode=WebRtcMode.SENDRECV)
    with st.form("chat_system", clear_on_submit=True):
        input_msg = st.text_input("TRANSMIT MESSAGE:")
        if st.form_submit_button("SEND") and input_msg:
            db.reference('global_chat').push({'user': st.session_state.user_id, 'msg': input_msg, 'ts': time.time()})
    raw_chat = db.reference('global_chat').get()
    if raw_chat:
        msg_list = sorted([v for v in raw_chat.values()], key=lambda x: x.get('ts', 0), reverse=True)
        for m in msg_list[:8]:
            st.write(f"📌 **{m.get('user')}**: {m.get('msg')}")

# --- TAB 7: SYS ---
with tabs[6]:
    if st.button("🔥 WIPE ALL"):
        db.reference('users').delete()
        st.success("CLEARED")
