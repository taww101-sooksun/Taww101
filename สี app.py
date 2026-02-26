import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
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
# 1. SETUP & COMPACT DESIGN
# ==========================================
st.set_page_config(page_title="SYNAPSE V2", layout="wide")
st_autorefresh(interval=5000, key="global_refresh")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #001 0%, #000 100%); color: #00f2fe; font-family: 'Courier New', Courier, monospace; }
    .neon-header { 
        font-size: 32px; font-weight: 900; text-align: center;
        color: #fff; text-shadow: 0 0 10px #00f2fe;
        border: 2px solid #00f2fe; padding: 10px; background: rgba(0,0,0,0.8);
        border-radius: 10px; margin-bottom: 10px; letter-spacing: 5px;
    }
    .terminal-container {
        border: 1px solid #00f2fe; padding: 12px; border-radius: 8px;
        background: rgba(0, 242, 254, 0.05); border-left: 5px solid #ff00de;
        margin-bottom: 10px;
    }
    .stTabs [data-baseweb="tab"] { font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. AUDIO (SIDEBAR)
# ==========================================
audio_file = "ฉันผิดเองที่เดินหนี้ความจริง.mp3"
with st.sidebar:
    if os.path.exists("logo3.jpg"):
        st.image("logo3.jpg", width=120)
    st.markdown("### 🛰️ NETWORK STATUS")
    st.success("ENCRYPTION: ACTIVE")
    if os.path.exists(audio_file):
        st.audio(audio_file, format="audio/mp3", loop=True)
    st.markdown("---")
    st.write(f"LAST SYNC: {datetime.datetime.now().strftime('%H:%M:%S')}")

# ==========================================
# 3. HEADER
# ==========================================
st.markdown('<div class="neon-header">SYNAPSE</div>', unsafe_allow_html=True)

# ==========================================
# 4. TABS (เติมของที่ใช้งานได้จริงให้ทุกช่อง)
# ==========================================
tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "📊 LOGS", "🔐 SEC", "📺 MEDIA", "🧹 SYS"])

# --- TAB 1: CORE (ระบบยืนยันตัวตน) ---
with tabs[0]:
    st.markdown('<div class="terminal-container">[ USER_PROTOCOL ]</div>', unsafe_allow_html=True)
    name = st.text_input("ENTER CODENAME:", value="Agent_X")
    status_col1, status_col2 = st.columns(2)
    with status_col1:
        if st.button("🚀 CONNECT SATELLITE"):
            st.info("กำลังเชื่อมต่อวงโคจร...")
            time.sleep(1)
            st.success("CONNECTED")
    with status_col2:
        st.metric("UPTIME", "99.99%", "+0.01%")

# --- TAB 2: RADAR (แผนที่จริง) ---
with tabs[1]:
    st.markdown('<div class="terminal-container">[ GLOBAL_RADAR ]</div>', unsafe_allow_html=True)
    m = folium.Map(location=[13.75, 100.5], zoom_start=5, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google")
    st_folium(m, width="100%", height=400)

# --- TAB 3: COMMS (วิดีโอคอลจริง) ---
with tabs[2]:
    st.markdown('<div class="terminal-container">[ ENCRYPTED_VIDEO_FEED ]</div>', unsafe_allow_html=True)
    webrtc_streamer(key="call", mode=WebRtcMode.SENDRECV)
    st.text_area("SECURE NOTES:", "บันทึกภารกิจลับที่นี่...")

# --- TAB 4: LOGS (ตารางข้อมูลจริง) ---
with tabs[3]:
    st.markdown('<div class="terminal-container">[ METADATA_ANALYSIS ]</div>', unsafe_allow_html=True)
    # สร้างตารางหลอกที่ดูเหมือนข้อมูลจริง
    log_data = pd.DataFrame({
        "TIMESTAMP": [datetime.datetime.now().strftime('%H:%M:%S') for _ in range(5)],
        "ID": ["S-101", "S-204", "S-009", "S-771", "S-102"],
        "STATUS": ["ENCRYPTED", "PASS", "PASS", "WARNING", "ENCRYPTED"]
    })
    st.table(log_data)

# --- TAB 5: SEC (เครื่องมือ Hacker) ---
with tabs[4]:
    st.markdown('<div class="terminal-container">[ SECURITY_TOOLKIT ]</div>', unsafe_allow_html=True)
    st.write("🔒 **QUANTUM KEY GENERATOR**")
    if st.button("🔑 GENERATE NEW KEY"):
        key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
        st.code(key)
    st.markdown("---")
    st.write("📡 **SIGNAL STRENGTH**")
    st.progress(random.randint(70, 95))

# --- TAB 6: MEDIA (หน้าโชว์เพลงและคลิป) ---
with tabs[5]:
    st.markdown('<div class="terminal-container">[ SATELLITE_BROADCAST ]</div>', unsafe_allow_html=True)
    if os.path.exists(audio_file):
        st.markdown(f"#### 🎵 {audio_file}")
        st.audio(audio_file)
    st.video("https://www.youtube.com/watch?v=F3zR5W0Bv0U") # ใส่ลิงก์วิดีโอเพลงร็อกของคุณ

# --- TAB 7: SYS (ระบบทำลายหลักฐาน) ---
with tabs[6]:
    st.markdown('<div class="terminal-container">[ DESTRUCTION_PROTOCOL ]</div>', unsafe_allow_html=True)
    st.warning("คำเตือน: การกดปุ่มด้านล่างจะล้างข้อมูลถาวร")
    if st.button("🧹 CLEAR CACHE & LOGS"):
        st.toast("กำลังล้างข้อมูล...")
        time.sleep(2)
        st.success("SYSTEM CLEANED")
