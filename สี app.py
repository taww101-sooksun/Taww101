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

# --- 2. CONFIG & STYLE ---
st.set_page_config(page_title="SYNAPSE COMMAND", layout="wide")

# ปรับพื้นหลัง 60 วินาที (60s) ตามสั่ง ลดการกระตุกสายตา
st.markdown("""
    <style>
    @keyframes RainbowFlow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .stApp { 
        background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff); 
        background-size: 1200% 1200%; 
        animation: RainbowFlow 60s ease infinite; 
    }
    .stChatFloating { border: 2px solid #00ff00; border-radius: 10px; padding: 10px; background: rgba(0,0,0,0.7); }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGO (Size 300) ---
if os.path.exists("Logo2.jpg"):
    st.image("Logo2.jpg", width=300)
else:
    st.markdown("<h1 style='color: white;'>S Y N A P S E</h1>", unsafe_allow_html=True)

# --- 4. ACCESS CONTROL ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    with st.form("Login"):
        u_id = st.text_input("ID / ไอดี")
        u_pw = st.text_input("Password / รหัสผ่าน", type="password")
        if st.form_submit_button("UNLOCK / ปลดล็อค"):
            if u_pw == "synapse2026" and u_id:
                st.session_state.authenticated = True
                st.session_state.my_id = u_id
                st.rerun()
    st.stop()

my_id = st.session_state.my_id

# --- 5. DATA FETCH (Real-time) ---
all_users = db.reference('/users').get() or {}
friend_options = [u for u in all_users.keys() if u != my_id]

# --- 6. TACTICAL RADAR (Map 500px) ---
st.subheader("📡 RADAR SYSTEM / ระบบเรดาร์")
location = get_geolocation()

if location:
    coords = location.get('coords', {})
    lat, lon = coords.get('latitude'), coords.get('longitude')
    
    if lat and lon:
        # อัปเดตตำแหน่ง (Update Location)
        db.reference(f'/users/{my_id}/location').update({
            'lat': lat, 'lon': lon, 'last_update': datetime.now().strftime('%H:%M:%S')
        })

        m = folium.Map(location=[lat, lon], zoom_start=16, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')

        for user_id, user_data in all_users.items():
            if 'location' in user_data:
                u_lat, u_lon = user_data['location'].get('lat'), user_data['location'].get('lon')
                if u_lat and u_lon:
                    is_me = (user_id == my_id)
                    color = 'red' if is_me else 'blue'
                    # ปักมุด (Marker)
                    folium.Marker(
                        [u_lat, u_lon],
                        tooltip=f"{user_id}",
                        icon=folium.Icon(color=color, icon='user', prefix='fa')
                    ).add_to(m)
                    # ชื่อลอย (Floating Name)
                    folium.map.Marker(
                        [u_lat, u_lon],
                        icon=folium.features.DivIcon(
                            icon_size=(150,36),
                            html=f'<div style="font-size: 12pt; color: {color}; font-weight: bold; text-shadow: 2px 2px black;">{user_id}</div>',
                        )
                    ).add_to(m)

        # แผนที่ขนาด 500 ตามสั่ง (Height 500)
        st_folium(m, use_container_width=True, height=500, key="synapse_map")
    else:
        st.warning("🛰️ Waiting for GPS... / รอสัญญาณดาวเทียม...")

# --- 7. MESSENGER & NOTIFICATION ---
st.write("---")
st.subheader("💬 MESSENGER / แชท")

col1, col2 = st.columns([1, 2])

with col1:
    chat_target = st.selectbox("Select Friend / เลือกเพื่อน", ["-- Select --"] + friend_options)
    # ปุ่มเชื่อมต่อระบุชัดเจน (Connection Status)
    if chat_target != "-- Select --":
        st.success(f"✅ CONNECTED TO: {chat_target} / เชื่อมต่อแล้ว")
    else:
        st.info("📡 STANDBY / รอการเชื่อมต่อ")

with col2:
    if chat_target != "-- Select --":
        ids = sorted([my_id, chat_target])
        chat_id = f"chat_{ids[0]}_{ids[1]}"
        
        # ดึงข้อความมาแสดง
        raw_msgs = db.reference(f'/messages/{chat_id}').get()
        if raw_msgs:
            sorted_msgs = sorted(raw_msgs.values(), key=lambda x: x.get('timestamp', ''))
            for m in sorted_msgs[-5:]:
                align = "right" if m['sender'] == my_id else "left"
                st.markdown(f"<div style='text-align: {align};'><b>{m['sender']}:</b> {m['text']}</div>", unsafe_allow_html=True)
        
        with st.form("send", clear_on_submit=True):
            m_text = st.text_input("Type here... / พิมพ์ที่นี่")
            if st.form_submit_button("SEND / ส่ง"):
                if m_text:
                    db.reference(f'/messages/{chat_id}').push({
                        'sender': my_id, 'text': m_text, 'timestamp': datetime.now().isoformat()
                    })
                    st.rerun()

# --- 8. YOUTUBE (Height 150) ---
st.write("---")
yt_url = "https://www.youtube.com/embed?listType=playlist&list=PL6S211I3urvpt47sv8mhbexif2YOzs2gO&autoplay=1&mute=1"
st.markdown(f'<iframe width="100%" height="150" src="{yt_url}" frameborder="0" allow="autoplay; encrypted-media"></iframe>', unsafe_allow_html=True)

st.caption("SYNAPSE V2.4 | STABLE RADAR | NO LIES")
