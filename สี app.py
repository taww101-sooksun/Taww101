import streamlit as st
import requests
from streamlit_js_eval import get_geolocation
from datetime import datetime
import pytz
from timezonefinder import TimezoneFinder
import folium
from streamlit_folium import st_folium
import firebase_admin
from firebase_admin import credentials, db
import os
import time

# --- 1. INITIALIZE FIREBASE ---
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_service_account"])
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
    except Exception as e:
        st.error(f"Firebase Error: {e}")

# --- 2. CONFIG & SLOW RAINBOW (180s) ---
st.set_page_config(page_title="SYNAPSE CORE", layout="wide")
st.markdown("""
    <style>
    @keyframes RainbowFlow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .stApp { background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff); background-size: 1200% 1200%; animation: RainbowFlow 180s ease infinite; }
    .stMetric { background-color: rgba(0,0,0,0.5); padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGO ---
logo_path = "logo2.jpg"
if os.path.exists(logo_path):
    st.image(logo_path, width=300)
else:
    st.image("https://raw.githubusercontent.com/taww101/taww101/main/logo2.jpg", width=300)

# --- 4. ACCESS CONTROL ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    with st.form("Login"):
        u_id = st.text_input("ID / ไอดี")
        u_pw = st.text_input("Password", type="password")
        if st.form_submit_button("UNLOCK"):
            if u_pw == "synapse2026" and u_id:
                st.session_state.authenticated = True
                st.session_state.my_id = u_id
                st.rerun()
    st.stop()

my_id = st.session_state.my_id

# --- 5. DATA FETCH (ย้ายออกมาข้างนอกเพื่อแก้ NameError) ---
# ดึงข้อมูลผู้ใช้ทั้งหมดมาเตรียมไว้ก่อน
all_users = db.reference('/users').get() or {}
friend_list = [u for u in all_users.keys() if u != my_id]

# --- 6. LIVE RADAR (ปรับให้นิ่งขึ้น) ---
@st.fragment(run_every=10) # เพิ่มเวลาเป็น 10 วินาทีเพื่อลดการกะพริบที่ไวเกินไป
def core_radar(users_data):
    location = get_geolocation()
    
    if location:
        coords = location.get('coords', {})
        lat, lon = coords.get('latitude'), coords.get('longitude')
        
        if lat and lon:
            # เวลา (Global Time)
            now_utc = datetime.now(pytz.utc).strftime('%H:%M:%S UTC')
            
            # บังคับซิงค์พิกัด
            db.reference(f'/users/{my_id}/location').update({
                'lat': lat, 'lon': lon,
                'last_sync': time.time(),
                'time_intl': now_utc
            })

            # สร้างแผนที่
            m = folium.Map(location=[lat, lon], zoom_start=17, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')
            
            for u_id, u_data in users_data.items():
                loc = u_data.get('location', {})
                u_lat, u_lon = loc.get('lat'), loc.get('lon')
                
                if u_lat and u_lon:
                    is_me = (u_id == my_id)
                    color = 'red' if is_me else 'blue'
                    
                    folium.Marker(
                        [u_lat, u_lon],
                        tooltip=u_id,
                        icon=folium.Icon(color=color, icon='user', prefix='fa')
                    ).add_to(m)

                    folium.map.Marker(
                        [u_lat, u_lon],
                        icon=folium.features.DivIcon(
                            icon_size=(150,36),
                            html=f'<div style="font-size: 12pt; color: {color}; font-weight: bold; text-shadow: 2px 2px black;">{u_id}</div>',
                        )
                    ).add_to(m)

            st_folium(m, use_container_width=True, height=500, key="radar_v32")
            st.write(f"🌍 **GLOBAL TIME (UTC):** {now_utc}")
        else:
            st.warning("🛰️ Waiting for GPS...")
    else:
        st.info("💡 Please Allow GPS Access")

# เรียกฟังก์ชันแผนที่พร้อมส่งข้อมูลผู้ใช้เข้าไป
core_radar(all_users)

# --- 7. SIMPLE CHAT ---
st.write("---")
chat_target = st.selectbox("💬 CHAT WITH:", ["-- Select Friend --"] + friend_list)

if chat_target != "-- Select Friend --":
    ids = sorted([my_id, chat_target])
    chat_id = f"chat_{ids[0]}_{ids[1]}"
    
    # แสดงแชทแบบง่าย
    msgs = db.reference(f'/messages/{chat_id}').limit_to_last(5).get()
    if msgs:
        for m in sorted(msgs.values(), key=lambda x: x.get('timestamp', '')):
            st.write(f"**{m['sender']}:** {m['text']}")
    
    with st.form("send_msg", clear_on_submit=True):
        txt = st.text_input("Message...")
        if st.form_submit_button("SEND
