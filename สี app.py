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

# --- 2. CONFIG & THEME (Slow Rainbow 180s) ---
st.set_page_config(page_title="SYNAPSE CORE", layout="wide")
st.markdown("""
    <style>
    @keyframes RainbowFlow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .stApp { background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff); background-size: 1200% 1200%; animation: RainbowFlow 180s ease infinite; }
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
        if st.form_submit_button("UNLOCK"):
            if u_pw == "synapse2026" and u_id:
                st.session_state.authenticated = True
                st.session_state.my_id = u_id
                st.rerun()
    st.stop()

my_id = st.session_state.my_id

# --- 5. DATA PREP (Fix NameError) ---
all_users = db.reference('/users').get() or {}
friend_list = [u for u in all_users.keys() if u != my_id]

# --- 6. LIVE RADAR (Fix Flicker) ---
@st.fragment(run_every=10)
def core_radar(users_data):
    location = get_geolocation()
    if location:
        coords = location.get('coords', {})
        lat, lon = coords.get('latitude'), coords.get('longitude')
        if lat and lon:
            now_utc = datetime.now(pytz.utc).strftime('%H:%M:%S UTC')
            # Sync to Cloud
            db.reference(f'/users/{my_id}/location').update({
                'lat': lat, 'lon': lon,
                'last_sync': time.time(),
                'time_intl': now_utc
            })
            # Map Design
            m = folium.Map(location=[lat, lon], zoom_start=17, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')
            for uid, udata in users_data.items():
                loc = udata.get('location', {})
                if loc.get('lat') and loc.get('lon'):
                    color = 'red' if uid == my_id else 'blue'
                    folium.Marker([loc['lat'], loc['lon']], icon=folium.Icon(color=color, icon='user', prefix='fa')).add_to(m)
                    folium.map.Marker([loc['lat'], loc['lon']], icon=folium.features.DivIcon(
                        icon_size=(150,36),
                        html=f'<div style="font-size: 12pt; color: {color}; font-weight: bold; text-shadow: 2px 2px black;">{uid}</div>'
                    )).add_to(m)
            # สำคัญ: key ต้องนิ่ง ไม่เปลี่ยนตามเวลา เพื่อลดการกะพริบ
            st_folium(m, use_container_width=True, height=500, key="radar_v33")
            st.write(f"🌍 **GLOBAL TIME (UTC):** {now_utc}")

core_radar(all_users)

# --- 7. CHAT SYSTEM (Fixed Syntax) ---
st.write("---")
chat_target = st.selectbox("💬 CHAT WITH:", ["-- Select Friend --"] + friend_list)

if chat_target != "-- Select Friend --":
    ids = sorted([my_id, chat_target])
    chat_id = f"chat_{ids[0]}_{ids[1]}"
    msgs = db.reference(f'/messages/{chat_id}').limit_to_last(5).get()
    if msgs:
        for m in sorted(msgs.values(), key=lambda x: x.get('timestamp', '')):
            st.write(f"**{m['sender']}:** {m['text']}")
    
    with st.form("send_msg", clear_on_submit=True):
        txt = st.text_input("Message...")
        # แก้ไขจุดที่ลืมปิดฟันหนูตรงคำว่า "SEND" เรียบร้อย
        if st.form_submit_button("SEND"):
            if txt:
                db.reference(f'/messages/{chat_id}').push({
                    'sender': my_id, 'text': txt, 'timestamp': datetime.now().isoformat()
                })
                st.rerun()

st.caption("SYNAPSE V3.3 | CORE STABLE | REAL-TIME TRUTH")
