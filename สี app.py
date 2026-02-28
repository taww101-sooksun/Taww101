import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import folium
from streamlit_folium import st_folium
import datetime
import time
import pandas as pd
import numpy as np

# ==========================================
# 1. SETTING & UI (ธีมไซไฟ สีสด)
# ==========================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #000; color: #00f2fe; }
    .neon-text { text-shadow: 0 0 10px #ff1744, 0 0 20px #ff1744; color: #fff; text-align: center; }
    .status-card { border: 1px solid #00f2fe; padding: 15px; border-radius: 10px; background: rgba(0, 242, 254, 0.05); }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. AUDIO SYSTEM (ยักษ์ในตัวฉัน)
# ==========================================
def play_system_audio():
    audio_link = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
    st.components.v1.html(f"""
        <audio id="bg-audio" loop autoplay><source src="{audio_link}" type="audio/mpeg"></audio>
        <script>document.addEventListener('click', function() {{ document.getElementById('bg-audio').play(); }}, {{once: true}});</script>
    """, height=0)

play_system_audio()

# ==========================================
# 3. FIREBASE INITIALIZATION
# ==========================================
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except: st.error("Firebase Connection Error")

if 'nav_level' not in st.session_state: st.session_state.nav_level = "HOME"
if 'my_name' not in st.session_state: st.session_state.my_name = "Agent_Unknown"

# ==========================================
# 4. LOGIC FUNCTIONS
# ==========================================
def get_marker_color(info, name):
    if name == st.session_state.my_name: return "cadetblue"
    battery = info.get('battery', 100)
    status = info.get('status', 'OFFLINE')
    if battery < 20: return "red"
    if status == "ACTIVE": return "green"
    return "gray"

# ==========================================
# 5. NAVIGATION & PAGES
# ==========================================

if st.session_state.nav_level != "HOME":
    if st.button("⬅️ BACK TO MENU"):
        st.session_state.nav_level = "GPS_MENU" if "FEATURE" in st.session_state.nav_level else "HOME"
        st.rerun()

# --- HOME PAGE ---
if st.session_state.nav_level == "HOME":
    st.markdown("<h1 class='neon-text'>SYNAPSE COMMAND v.2</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🛰️ 1. GPS SYSTEMS", use_container_width=True):
            st.session_state.nav_level = "GPS_MENU"
            st.rerun()
    with c2: st.button("💬 2. COMMUNICATIONS", use_container_width=True)

# --- GPS SUB-MENU (10 กรอบ) ---
elif st.session_state.nav_level == "GPS_MENU":
    st.markdown("### 🌐 GPS STRATEGIC UNITS")
    cols = st.columns(2)
    features = ["1.1 Signal Pulse", "1.2 Radar Tracking", "1.3 Tactical Ruler", "1.4 Velocity Monitor", "1.5 Geofence Alarm", "1.6 ETA Calculator", "1.7 Satellite Switch", "1.8 Breadcrumb Trail", "1.9 Elevation Profile", "1.10 Area Density"]
    for i, f_name in enumerate(features):
        with cols[i % 2]:
            if st.button(f_name, use_container_width=True):
                st.session_state.nav_level = f"FEATURE_{i+1}"
                st.rerun()

# ==========================================
# 6. FEATURE IMPLEMENTATIONS (ไส้ใน 10 อย่าง)
# ==========================================

elif st.session_state.nav_level == "FEATURE_1": # Signal Pulse
    st.subheader("📡 1.1 SIGNAL PULSE MONITOR")
    st.write("สถานะการส่งสัญญาณ: **STABLE**")
    st.info("จำลองการแผ่กระจายของคลื่นวิทยุจากตำแหน่งปัจจุบัน...")

elif st.session_state.nav_level == "FEATURE_2": # Radar Tracking
    st.subheader("🛰️ 1.2 REAL-TIME RADAR")
    users = db.reference('users').get()
    m = folium.Map(location=[13.75, 100.5], zoom_start=6, tiles="cartodbpositron")
    if users:
        for name, info in users.items():
            if isinstance(info, dict) and 'lat' in info:
                folium.Marker([info['lat'], info['lon']], icon=folium.Icon(color=get_marker_color(info, name))).add_to(m)
    st_folium(m, width="100%", height=500)

elif st.session_state.nav_level == "FEATURE_3": # Tactical Ruler
    st.subheader("📏 1.3 TACTICAL RULER")
    st.write("เลือกเป้าหมายเพื่อวัดระยะทางตรง (Air Distance)")
    st.metric("DISTANCE TO TARGET", "14.52 KM", "+0.2 KM")

elif st.session_state.nav_level == "FEATURE_4": # Velocity Monitor
    st.subheader("🌡️ 1.4 VELOCITY MONITOR")
    speed = 45 
    st.write(f"ความเร็วปัจจุบัน: **{speed} KM/H**")
    st.progress(speed/120)

elif st.session_state.nav_level == "FEATURE_5": # Geofence Alarm
    st.subheader("🚧 1.5 GEOFENCE SECURITY")
    st.error("⚠️ WARNING: TARGET APPROACHING BOUNDARY")
    m = folium.Map(location=[13.75, 100.5], zoom_start=13)
    folium.Circle([13.75, 100.5], radius=2000, color='red', fill=True).add_to(m)
    st_folium(m, width="100%", height=400)

elif st.session_state.nav_level == "FEATURE_6": # ETA Calculator
    st.subheader("🕒 1.6 ETA CALCULATOR")
    st.markdown("<div class='status-card'>ESTIMATED ARRIVAL: <b>14:30 (15 min)</b></div>", unsafe_allow_html=True)

elif st.session_state.nav_level == "FEATURE_7": # Satellite Switch
    st.subheader("🗺️ 1.7 SATELLITE VIEW")
    st_folium(folium.Map(location=[13.75, 100.5], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", attr="Google"), width="100%", height=500)

elif st.session_state.nav_level == "FEATURE_8": # Breadcrumb Trail
    st.subheader("👣 1.8 BREADCRUMB TRAIL")
    st.write("ประวัติการเคลื่อนที่ในช่วง 1 ชั่วโมงที่ผ่านมา")
    chart_data = pd.DataFrame(np.random.randn(20, 2), columns=['lat', 'lon'])
    st.line_chart(chart_data)

elif st.session_state.nav_level == "FEATURE_9": # Elevation Profile
    st.subheader("📉 1.9 ELEVATION PROFILE")
    st.area_chart(np.random.randn(10))
    st.write("ระดับความสูงปัจจุบัน: **45m ABOVE SEA LEVEL**")

elif st.session_state.nav_level == "FEATURE_10": # Area Density
    st.subheader("👥 1.10 AREA DENSITY")
    st.warning("DETECTION: 3 AGENTS IN 1KM RADIUS")
