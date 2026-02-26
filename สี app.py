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
# 1. SETUP & THEME (เน้นความจริงและสวยงาม)
# ==========================================
st.set_page_config(page_title="SYNAPSE ULTIMATE", layout="wide")
st_autorefresh(interval=5000, key="global_refresh") # รีเฟรชหน้าจอทุก 5 วินาทีเพื่ออัปเดตเวลา/แชท

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
        st.error(f"ระบบฐานข้อมูลขัดข้อง: {e}")

# ==========================================
# 3. LOGO & WORLD CLOCK (ไฮไลต์หน้าจอ)
# ==========================================
col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    if os.path.exists("logo3.jpg"):
        st.image("logo3.jpg", width=400) # โลโก้ 400px ตามสั่ง
    else:
        st.markdown('<div style="text-align:center;">[ Missing logo3.jpg ]</div>', unsafe_allow_html=True)
    st.markdown('<div class="neon-header">SYNAPSE</div>', unsafe_allow_html=True)

# แถบนาฬิกาโลก
st.markdown("### 🌐 GLOBAL REAL-TIME MONITOR")
c1, c2, c3, c4 = st.columns(4)
zones = {'BANGKOK': 'Asia/Bangkok', 'NEW YORK': 'America/New_York', 'LONDON': 'Europe/London', 'TOKYO': 'Asia/Tokyo'}
for col, (city, zone) in zip([c1, c2, c3, c4], zones.items()):
    now = datetime.datetime.now(pytz.timezone(zone)).strftime('%H:%M:%S')
    col.markdown(f"""
        <div class='clock-box'>
            <small>{city}</small><br>
            <span class='clock-time'>{now}</span>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. SIDEBAR (เพลงและการควบคุม)
# ==========================================
with st.sidebar:
    st.markdown("### 🛰️ NETWORK CENTER")
    audio_file = "ฉันผิดเองที่เดินหนี้ความจริง.mp3"
    if os.path.exists(audio_file):
        st.audio(audio_file, format="audio/mp3", loop=True)
    st.markdown("---")
    st.write(f"SYSTEM UPTIME: {datetime.datetime.now().strftime('%H:%M:%S')}")

# ==========================================
# 5. MAIN NAVIGATION (TABS)
# ==========================================
tabs = st.tabs(["🚀 แกนหลัก", "🛰️ เรดาร์", "💬 การสื่อสาร", "📊 บันทึก", "🔐 ปลอดภัย", "📺 สื่อ", "🧹 ระบบ"])

# --- TAB 1: แกนหลัก (GPS & Login) ---
with tabs[0]:
    st.markdown('<div class="terminal-container">[ SATELLITE_LINK_INITIATED ]</div>', unsafe_allow_html=True)
    user_id = st.text_input("รหัสประจำตัว (User ID):", value=st.session_state.get('user_id', 'Agent_001'))
    st.session_state.user_id = user_id
    
    if st.button("🛰️ ดึงพิกัด GPS ปัจจุบัน"):
        loc = get_geolocation()
        if loc:
            lat = loc['coords']['latitude']
            lon = loc['coords']['longitude']
            db.reference(f'users/{user_id}').set({
                'lat': lat, 'lon': lon,
                'last_seen': datetime.datetime.now().strftime('%H:%M:%S'),
                'status': 'ONLINE'
            })
            st.success(f"บันทึกพิกัดสำเร็จ: {lat}, {lon}")
        else:
            st.warning("โปรดอนุญาตให้เข้าถึงตำแหน่งที่ตั้งในเบราว์เซอร์ของคุณ")

# --- TAB 2: เรดาร์ (แผนที่มุด GPS) ---
with tabs[1]:
    st.markdown('<div class="terminal-container">[ RADAR_LIVE_FEED ]</div>', unsafe_allow_html=True)
    m = folium.Map(location=[13.75, 100.5], zoom_start=4, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
    
    try:
        all_users = db.reference('users').get()
        if all_users:
            for u, data in all_users.items():
                if isinstance(data, dict) and 'lat' in data:
                    folium.Marker(
                        [data['lat'], data
