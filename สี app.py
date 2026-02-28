import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import pytz
import os
import time
import pandas as pd
import random
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. CORE SYSTEM CONFIGURATION (NEON THEME)
# ==========================================
st.set_page_config(page_title="SYNAPSE QUANTUM CONTROL", layout="wide")
st_autorefresh(interval=5000, key="global_refresh")

# ลิงก์เพลงหลัก (ยักษ์ในตัวฉัน)
direct_link = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"

# ตกแต่ง UI แบบฉบับกองบัญชาการ สีสด แสงหายใจ (ตามคลิปที่เพื่อนส่งมา)
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #001 0%, #000 100%); color: #00f2fe; font-family: 'Courier New', Courier, monospace; }
    
    .neon-header { 
        font-size: 40px; font-weight: 900; text-align: center;
        color: #fff; text-shadow: 0 0 15px #ff1744, 0 0 20px #00f2fe;
        border: 10px double #ff1744; padding: 20px; background: rgba(0,0,0,0.85);
        border-radius: 20px; margin-bottom: 30px;
    }
    
    @keyframes breathing {
        0% { box-shadow: 0 0 5px #ff1744; }
        50% { box-shadow: 0 0 25px #ff1744; }
        100% { box-shadow: 0 0 5px #ff1744; }
    }

    div.stButton > button {
        background: linear-gradient(135deg, #ff1744 0%, #000 50%, #ff00de 100%);
        color: white !important; border: 2px solid #fff; border-radius: 10px;
        height: 50px; font-weight: bold; width: 100%; transition: 0.5s;
        animation: breathing 3s infinite ease-in-out;
    }
    
    .clock-box {
        background: rgba(0, 242, 254, 0.1); border: 1px solid #00f2fe;
        padding: 10px; border-radius: 10px; text-align: center; box-shadow: 0 0 10px #00f2fe;
    }
    .clock-time { font-size: 20px; font-weight: bold; color: #ff1744; }
    
    .bubble-me { background: rgba(0, 242, 254, 0.15); border: 2px solid #00f2fe; padding: 12px; border-radius: 15px 15px 0 15px; margin-bottom: 10px; color: #fff; }
    .bubble-others { background: rgba(255, 23, 68, 0.15); border: 2px solid #ff1744; padding: 12px; border-radius: 15px 15px 15px 0; margin-bottom: 10px; color: #fff; }
    
    .terminal-container {
        border: 1px solid rgba(0, 242, 254, 0.5); padding: 20px; border-radius: 10px;
        background: rgba(0, 5, 15, 0.9); border-left: 8px solid #00f2fe;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 🔊 ระบบเพลงแอบเล่น (Auto-play) ---
st.components.v1.html(f"""
    <audio id="synapse-audio" loop autoplay style="display:none;"><source src="{direct_link}" type="audio/mpeg"></audio>
    <script>
        var audio = document.getElementById("synapse-audio");
        window.parent.document.addEventListener('click', function() {{ audio.play(); }}, {{ once: true }});
    </script>
""", height=0)

# ==========================================
# 2. FIREBASE INITIALIZATION
# ==========================================
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_dict = dict(st.secrets["firebase"])
            if "private_key" in fb_dict: fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            creds = credentials.Certificate(fb_dict)
            firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except Exception as e: st.error(f"SYSTEM_ERROR: {e}")

# ==========================================
# 3. TOP UI (LOGO & CLOCKS)
# ==========================================
col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    if os.path.exists("logo3.jpg"): st.image("logo3.jpg", width=500)
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
    if os.path.exists("logo3.jpg"): st.image("logo3.jpg", use_container_width=True)
    st.markdown("---")
    st.markdown("### 🎵 AUDIO FREQUENCY")
    st.audio(direct_link, format="audio/mpeg", loop=True)
    st.markdown("---")
    if st.button("🔍 SCAN NETWORK"): st.toast("กำลังวิเคราะห์โหนดโครงข่าย...")
    st.write(f"UPTIME: {datetime.datetime.now().strftime('%H:%M:%S')}")

# ==========================================
# 5. MAIN INTERFACE (FULL TABS)
# ==========================================
st.markdown('<div class="neon-header" style="font-size:20px; border:none; background:none;">S Y N A P S E _ O V E R L O R D</div>', unsafe_allow_html=True)
tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "📊 DATA LOG", "🔐 SECURITY", "📺 MEDIA", "🧹 SYSTEM"])

# --- TAB 1: CORE ---
with tabs[0]:
    st.markdown('<div class="terminal-container"><h3>[ PROTOCOL_IDENTIFICATION ]</h3></div>', unsafe_allow_html=True)
    st.session_state.my_name = st.text_input("ระบุชื่อรหัสของคุณ:", value=st.session_state.get('my_name', 'Guest'))
    if st.button("🚀 INITIATE QUANTUM LINK"):
        loc = get_geolocation()
        if loc:
            raw_time = loc.get('timestamp', datetime.datetime.now().timestamp())
            local_time = datetime.datetime.fromtimestamp(raw_time/1000).strftime('%Y-%m-%d %H:%M:%S')
            db.reference(f'users/{st.session_state.my_name}').set({'lat': loc['coords']['latitude'], 'lon': loc['coords']['longitude'], 'gps_time': local_time, 'status': 'ACTIVE'})
            st.success("GLOBAL POSITIONING SYNCHRONIZED.")

# --- TAB 2: RADAR ---
with tabs[1]:
    st.markdown('<div class="terminal-container"><h3>[ GLOBAL_SURVEILLANCE_RADAR ]</h3></div>', unsafe_allow_html=True)
    users = db.reference('users').get()
    m = folium.Map(location=[13.75, 100.5], zoom_start=2, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
    if users:
        for name, info in users.items():
            if isinstance(info, dict) and 'lat' in info:
                f_color = 'cadetblue' if name == st.session_state.my_name else 'red'
                folium.Marker([info['lat'], info['lon']], tooltip=f"Agent: {name}", icon=
