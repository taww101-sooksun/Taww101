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

# --- 2. THEME & SLOW RAINBOW (180s) ---
st.set_page_config(page_title="SYNAPSE CORE", layout="wide")
st.markdown("""
    <style>
    @keyframes RainbowFlow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .stApp { background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff); background-size: 1200% 1200%; animation: RainbowFlow 180s ease infinite; }
    .chat-container { background: rgba(0,0,0,0.7); padding: 10px; border-radius: 10px; border: 1px solid #00ff00; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGO (Size 300) ---
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
        if st.form_submit_button("SYSTEM UNLOCK"):
            if u_pw == "synapse2026" and u_id:
                st.session_state.authenticated = True
                st.session_state.my_id = u_id
                st.rerun()
    st.stop()

my_id = st.session_state.my_id

# --- 5. CORE SYSTEM: RADAR & TIME ---
# ใช้ Fragment เพื่อให้แผนที่อัปเดตตัวเองทุก 5 วินาที (มุดจะได้วิ่ง)
@st.fragment(run_every=5)
def core_radar():
    location = get_geolocation()
    all_users = db.reference('/users').get() or {}
    
    if location:
        coords = location.get('coords', {})
        lat, lon = coords.get('latitude'), coords.get('longitude')
        
        if lat and lon:
            # คำนวณเวลา (Local & Global)
            tf = TimezoneFinder()
            tz_name = tf.timezone_at(lng=lon, lat=lat)
            now_local = datetime.now(pytz.timezone(tz_name)).strftime('%H:%M:%S')
            now_utc = datetime.now(pytz.utc).strftime('%H:%M:%S UTC')
            
            # ⚡ FORCE UPDATE: บังคับเขียนพิกัดลง Cloud ทันทีที่ขยับ
            db.reference(f'/users/{my_id}/location').update({
                'lat': lat, 'lon': lon,
                'time_th': now_local,
                'time_uk': now_utc,
                'last_sync': time.time() # ใช้ timestamp ตัวเลขเพื่อความแม่นยำ
            })

            # สร้างแผนที่แบบ Minimal ชัดเจน
            m = folium.Map(location=[lat, lon], zoom_start=17, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')
            
            for user_id, user_data in all_users.items():
                loc = user_data.get('location', {})
                u_lat, u_lon = loc.get('lat'), loc.get('lon')
                
                if u_lat and u_lon:
                    # เช็คว่าเพื่อนยังออนไลน์อยู่ไหม (ถ้าซิงค์ล่าสุดเกิน 1 นาที ให้ถือว่า Offline)
                    is_online = (time.time() - loc.get('last_sync', 0)) < 60
                    marker_color = 'red' if user_id == my_id else ('blue' if is_online else 'gray')
                    
                    # ปักหมุด
                    folium.Marker(
                        [u_lat, u_lon],
                        icon=folium.Icon(color=marker_color, icon='user', prefix='fa')
                    ).add_to(m)

                    # ชื่อบนหมุด (ชัดเจนที่สุด)
                    folium.map.Marker(
                        [u_lat, u_lon],
                        icon=folium.features.DivIcon(
                            icon_size=(150,36),
                            html=f'<div style="font-size: 11pt; color: {marker_color}; font-weight: bold; text-shadow: 2px 2px black;">{user_id}</div>',
                        )
                    ).add_to(m)

            # แสดงแผนที่ขนาด 500
            st_folium(m, use_container_width=True, height=500, key=f"radar_{time.time()}")
            st.markdown(f"**TIME (TH):** {now_local} | **TIME (UK/UTC):** {now_utc}")
        else:
            st.warning("🛰️ Searching for GPS... / กำลังค้นหาตำแหน่ง...")
    else:
        st.info("💡 Please Allow GPS Access / โปรดอนุญาต GPS")

# เรียกใช้งานแผนที่
core_radar()

# --- 6. CORE CHAT ---
st.write("---")
friend_list = [u for u in all_users.keys() if u != my_id]
chat_target = st.selectbox("💬 CHAT WITH:", ["-- Select Friend --"] + friend_list)

if chat_target != "-- Select Friend --":
    st.success(f"Connected to: {chat_target}")
    ids = sorted([my_id, chat_target])
    chat_id = f"chat_{ids[0]}_{ids[1]}"
    
    # ดึงแชท
    msgs = db.reference(f'/messages/{chat_id}').get()
    if msgs:
        sorted_m = sorted(msgs.values(), key=lambda x: x.get('timestamp', ''))
        for m in sorted_m[-5:]:
            st.write(f"**{m['sender']}:** {m['text']}")
    
    with st.form("send_chat", clear_on_submit=True):
        txt = st.text_input("Type Message...")
        if st.form_submit_button("SEND"):
            if txt:
                db.reference(f'/messages/{chat_id}').push({
                    'sender': my_id, 'text': txt, 'timestamp': datetime.now().isoformat()
                })
                st.rerun()

st.caption("SYNAPSE V3.1 | CORE CONNECTION | NO LIES")
