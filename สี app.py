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
# 1. SETUP & THEME (แก้ไข CSS ให้ถูกต้อง)
# ==========================================
st.set_page_config(page_title="SYNAPSE ULTIMATE", layout="wide")
st_autorefresh(interval=10000, key="global_refresh") # รีเฟรชทุก 10 วิ เพื่อไม่ให้หนักเครื่องเกินไป

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
        margin-bottom: 20px; /* แก้ไขจาก 'นั่ง' เป็น 20px */
    }
    .clock-box {
        background: rgba(0,0,0,0.6); border: 1px solid #00f2fe;
        padding: 10px; border-radius: 8px; text-align: center;
    }
    .clock-time { color: #ff00de; font-size: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FIREBASE CONNECTION (ปรับให้เสถียรขึ้น)
# ==========================================
if not firebase_admin._apps:
    try:
        # พยายามดึงจาก Secrets ถ้าไม่มีให้แจ้งเตือน
        if "firebase" in st.secrets:
            fb_dict = dict(st.secrets["firebase"])
            if "private_key" in fb_dict:
                fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            creds = credentials.Certificate(fb_dict)
            firebase_admin.initialize_app(creds, {
                'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
        else:
            st.warning("⚠️ ค้นหา Firebase Secrets ไม่เจอ กรุณาตั้งค่าใน .streamlit/secrets.toml")
    except Exception as e:
        st.error(f"DATABASE ERROR: {e}")

# ==========================================
# 3. HEADER & WORLD CLOCK
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
# 4. MAIN TABS
# ==========================================
tabs = st.tabs(["🚀 แกนหลัก", "🛰️ เรดาร์", "💬 การสื่อสาร", "🧹 ระบบ"])

# --- TAB 1: CORE (GPS) ---
with tabs[0]:
    st.markdown('<div class="terminal-container">[ GPS_INIT ]</div>', unsafe_allow_html=True)
    user_id = st.text_input("USER CODENAME:", value=st.session_state.get('user_id', 'Agent_001'), key="uid_input")
    st.session_state.user_id = user_id
    
    if st.button("🛰️ อัปเดตพิกัดปัจจุบัน"):
        loc = get_geolocation()
        if loc:
            lat = loc['coords']['latitude']
            lon = loc['coords']['longitude']
            db.reference(f'users/{user_id}').update({
                'lat': lat, 
                'lon': lon,
                'ts': time.time()
            })
            st.success(f"บันทึกพิกัดสำเร็จ: {lat}, {lon}")
        else:
            st.error("ไม่สามารถดึงพิกัดได้ โปรดอนุญาตการเข้าถึง GPS")

# --- TAB 2: RADAR ---
with tabs[1]:
    st.markdown('<div class="terminal-container">[ RADAR_LIVE ]</div>', unsafe_allow_html=True)
    # จุดเริ่มต้นแผนที่ (กลางกรุงเทพฯ)
    m = folium.Map(location=[13.75, 100.5], zoom_start=6, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
    
    try:
        users_data = db.reference('users').get()
        if users_data:
            for u, data in users_data.items():
                if isinstance(data, dict) and 'lat' in data and 'lon' in data:
                    folium.Marker(
                        location=[data['lat'], data['lon']], 
                        popup=f"Agent: {u}",
                        tooltip=u,
                        icon=folium.Icon(color='red' if u == user_id else 'blue', icon='user', prefix='fa')
                    ).add_to(m)
    except Exception as e:
        st.write("ยังไม่มีข้อมูลผู้ใช้ออนไลน์")

    st_folium(m, width="100%", height=500)

# --- TAB 3: COMMS ---
with tabs[2]:
    st.markdown('<div class="terminal-container">[ SECURE_CHAT ]</div>', unsafe_allow_html=True)
    webrtc_streamer(key="v-call", mode=WebRtcMode.SENDRECV)
    
    with st.form("chat_form", clear_on_submit=True):
        msg = st.text_input("พิมพ์ข้อความส่งเข้าเครือข่าย:")
        if st.form_submit_button("SEND") and msg:
            db.reference('global_chat').push({
                'user': st.session_state.user_id,
                'msg': msg,
                'ts': time.time()
            })
    
    # ดึงแชท 10 ข้อความล่าสุด
    chats = db.reference('global_chat').order_by_child('ts').limit_to_last(10).get()
    if chats:
        for c_id in reversed(list(chats.keys())):
            c = chats[c_id]
            st.markdown(f"📌 **{c['user']}**: {c['msg']}")

# --- TAB 4: SYSTEM ---
with tabs[3]:
    st.warning("⚠️ โซนอันตราย")
    confirm = st.text_input("พิมพ์ 'CONFIRM' เพื่อล้างข้อมูลพิกัดทั้งหมด")
    if st.button("🔥 WIPE ALL DATA"):
        if confirm == "CONFIRM":
            db.reference('users').delete()
            st.success("ข้อมูลทั้งหมดถูกทำลายแล้ว")
            st.rerun()
        else:
            st.error("รหัสยืนยันไม่ถูกต้อง")
