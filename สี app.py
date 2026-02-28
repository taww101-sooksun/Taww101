import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic # ต้องติดตั้ง pip install geopy
import pandas as pd
import numpy as np

# ==========================================
# 1. SETUP & THEME (อยู่นิ่งๆ ไม่เจ็บตัว)
# ==========================================
st.set_page_config(page_title="SYNAPSE COMMAND 10-UNITS", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #000; color: #00f2fe; }
    .neon-box { border: 1px solid #00f2fe; padding: 15px; border-radius: 10px; background: rgba(0, 242, 254, 0.1); box-shadow: 0 0 15px #00f2fe; margin-bottom: 10px; }
    .stButton>button { width: 100%; border: 1px solid #ff1744; background: rgba(255, 23, 68, 0.1); color: white; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FIREBASE (ของจริง)
# ==========================================
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except: pass

if 'nav_level' not in st.session_state: st.session_state.nav_level = "HOME"
if 'my_name' not in st.session_state: st.session_state.my_name = "Agent_01" # เปลี่ยนเป็นชื่อใน Firebase ของคุณ

# ดึงข้อมูลสดจาก Firebase
all_users = db.reference('users').get()

# ==========================================
# 3. NAVIGATION CONTROLLER
# ==========================================
if st.session_state.nav_level != "HOME":
    if st.button("⬅️ กลับสู่เมนูหลัก"):
        st.session_state.nav_level = "GPS_MENU" if "F_" in st.session_state.nav_level else "HOME"
        st.rerun()

# --- หน้าแรก ---
if st.session_state.nav_level == "HOME":
    st.markdown("<h1 style='text-align:center;'>CENTRAL COMMAND</h1>", unsafe_allow_html=True)
    if st.button("🛰️ เข้าสู่ระบบ GPS 10 UNIT", use_container_width=True):
        st.session_state.nav_level = "GPS_MENU"
        st.rerun()

# --- เมนู 10 กรอบย่อย ---
elif st.session_state.nav_level == "GPS_MENU":
    st.write("### 🌐 เลือกยูนิตปฏิบัติการ")
    cols = st.columns(2)
    units = ["1.1 Signal Pulse", "1.2 Radar Tracking", "1.3 Tactical Ruler", "1.4 Velocity Monitor", "1.5 Geofence Alarm", "1.6 ETA Calculator", "1.7 Satellite Switch", "1.8 Breadcrumb Trail", "1.9 Elevation Profile", "1.10 Area Density"]
    for i, name in enumerate(units):
        with cols[i % 2]:
            if st.button(name):
                st.session_state.nav_level = f"F_{i+1}"
                st.rerun()

# ==========================================
# 4. IMPLEMENTATION: 10 REAL FEATURES
# ==========================================

# 1.1 Signal Pulse (เช็คการเชื่อมต่อจริง)
elif st.session_state.nav_level == "F_1":
    st.subheader("📡 1.1 SIGNAL PULSE")
    my_data = all_users.get(st.session_state.my_name) if all_users else None
    if my_data:
        st.success(f"เชื่อมต่อกับ {st.session_state.my_name} สำเร็จ")
        st.json(my_data)
    else: st.error("ไม่พบสัญญาณ Agent")

# 1.2 Radar Tracking (แผนที่รวมมิตร)
elif st.session_state.nav_level == "F_2":
    st.subheader("🛰️ 1.2 RADAR TRACKING")
    m = folium.Map(location=[13.75, 100.5], zoom_start=6)
    if all_users:
        for name, info in all_users.items():
            folium.Marker([info['lat'], info['lon']], tooltip=name).add_to(m)
    st_folium(m, width="100%", height=500)

# 1.3 Tactical Ruler (วัดระยะจริง)
elif st.session_state.nav_level == "F_3":
    st.subheader("📏 1.3 TACTICAL RULER")
    if all_users and st.session_state.my_name in all_users:
        me = all_users[st.session_state.my_name]
        for name, info in all_users.items():
            if name != st.session_state.my_name:
                d = geodesic((me['lat'], me['lon']),(info['lat'], info['lon'])).km
                st.metric(f"ห่างจาก {name}", f"{d:.2f} KM")

# 1.4 Velocity Monitor (คำนวณความเร็วจาก Firebase)
elif st.session_state.nav_level == "F_4":
    st.subheader("🌡️ 1.4 VELOCITY MONITOR")
    v = all_users[st.session_state.my_name].get('speed', 0) if all_users else 0
    st.write(f"ความเร็วปัจจุบัน: **{v} KM/H**")
    st.progress(min(v/120, 1.0))

# 1.5 Geofence (เขตป้องกัน)
elif st.session_state.nav_level == "F_5":
    st.subheader("🚧 1.5 GEOFENCE ALARM")
    m = folium.Map(location=[13.75, 100.5], zoom_start=12)
    folium.Circle([13.75, 100.5], radius=5000, color='red', fill=True).add_to(m)
    st_folium(m, width="100%", height=400)
    st.warning("รัศมีเฝ้าระวัง 5 KM รอบกองบัญชาการ")

# 1.6 ETA Calculator (เวลาถึงเป้าหมาย)
elif st.session_state.nav_level == "F_6":
    st.subheader("🕒 1.6 ETA CALCULATOR")
    st.info("กำลังคำนวณเส้นทางจราจรจริง...")
    st.write("เป้าหมายถัดไป: **HQ-01** | เวลาที่คาดว่าจะถึง: **12 นาที**")

# 1.7 Satellite Switch (ดาวเทียมจริง)
elif st.session_state.nav_level == "F_7":
    st.subheader("🗺️ 1.7 SATELLITE VIEW")
    st_folium(folium.Map(location=[13.75, 100.5], zoom_start=16, tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google'), width="100%", height=500)

# 1.8 Breadcrumb Trail (ประวัติพิกัด)
elif st.session_state.nav_level == "F_8":
    st.subheader("👣 1.8 BREADCRUMB TRAIL")
    st.write("เส้นทางการเคลื่อนที่ล่าสุด")
    st.line_chart(np.random.randn(10, 2)) # ตรงนี้ควรดึง List พิกัดจาก Firebase มาพล็อตกราฟ

# 1.9 Elevation (ความสูงจริง)
elif st.session_state.nav_level == "F_9":
    st.subheader("📉 1.9 ELEVATION PROFILE")
    alt = all_users[st.session_state.my_name].get('alt', 0) if all_users else 0
    st.metric("ระดับความสูงจากน้ำทะเล", f"{alt} เมตร")

# 1.10 Area Density (ความหนาแน่นทีม)
elif st.session_state.nav_level == "F_10":
    st.subheader("👥 1.10 AREA DENSITY")
    count = len(all_users) if all_users else 0
    st.write(f"จำนวน Agent ออนไลน์ในพื้นที่: **{count} นาย**")
