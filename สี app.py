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
st.set_page_config(page_title="SYNAPSE PURITY", layout="wide")
st.markdown("""
    <style>
    @keyframes RainbowFlow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .stApp { background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff); background-size: 1200% 1200%; animation: RainbowFlow 180s ease infinite; }
    .status-box { background: rgba(0,0,0,0.8); padding: 15px; border-radius: 10px; border: 1px solid #00ff00; color: #00ff00; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGO ---
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

# --- 5. DATA FETCH & FILTER (ล้างขยะพิกัดเก่า) ---
all_users = db.reference('/users').get() or {}
current_ts = time.time()
active_users = {}

for uid, udata in all_users.items():
    last_sync = udata.get('location', {}).get('last_sync', 0)
    if (current_ts - last_sync) < 300: # กรองเฉพาะ 5 นาทีล่าสุด
        active_users[uid] = udata

friend_list = [u for u in active_users.keys() if u != my_id]

# --- 6. LIVE RADAR FRAGMENT ---
@st.fragment(run_every=10)
def purity_radar(users_to_show):
    location = get_geolocation()
    if location:
        coords = location.get('coords', {})
        lat, lon = coords.get('latitude'), coords.get('longitude')
        if lat and lon:
            tf = TimezoneFinder()
            tz_name = tf.timezone_at(lng=lon, lat=lat)
            # แสดงเวลาตามตำแหน่งจริงทั่วโลก
            time_here = datetime.now(pytz.timezone(tz_name)).strftime('%H:%M:%S')
            time_utc = datetime.now(pytz.utc).strftime('%H:%M:%S UTC')
            
            db.reference(f'/users/{my_id}/location').update({
                'lat': lat, 'lon': lon,
                'last_sync': time.time(),
                'time_local': time_here,
                'time_uk': time_utc
            })

            m = folium.Map(location=[lat, lon], zoom_start=17, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')
            for uid, udata in users_to_show.items():
                loc = udata.get('location', {})
                if loc.get('lat') and loc.get('lon'):
                    color = 'red' if uid == my_id else 'blue'
                    folium.Marker([loc['lat'], loc['lon']], icon=folium.Icon(color=color, icon='screenshot', prefix='glyphicon')).add_to(m)
                    folium.map.Marker([loc['lat'], loc['lon']], icon=folium.features.DivIcon(
                        icon_size=(150,36),
                        html=f'<div style="font-size: 11pt; color: {color}; font-weight: bold; text-shadow: 2px 2px black;">{uid}</div>'
                    )).add_to(m)

            st_folium(m, use_container_width=True, height=500, key="radar_v35")
            st.markdown(f"""
            <div class="status-box">
                <b>📍 YOUR LOCATION TIME:</b> {time_here}<br>
                <b>🇬🇧 GLOBAL TIME (UTC):</b> {time_utc}<br>
                <b>🛰️ STATUS:</b> ONLINE (TRUTH ONLY)
            </div>
            """, unsafe_allow_html=True)

purity_radar(active_users)

# --- 7. SECURE CHAT (Fixed AttributeError) ---
st.write("---")
chat_target = st.selectbox("💬 CHAT WITH:", ["-- Select Friend --"] + friend_list)

if chat_target != "-- Select Friend --":
    ids = sorted([my_id, chat_target])
    chat_id = f"chat_{ids[0]}_{ids[1]}"
    
    # แก้ไขจุดที่เกิด Error: ตรวจสอบการมีอยู่ของข้อมูลก่อนเรียกใช้
    chat_ref = db.reference(f'/messages/{chat_id}')
    try:
        msgs_data = chat_ref.limit_to_last(5).get()
        if msgs_data:
            for m in sorted(msgs_data.values(), key=lambda x: x.get('timestamp', '')):
                st.write(f"**{m['sender']}:** {m['text']}")
        else:
            st.info("No messages yet. / ยังไม่มีข้อความ")
    except Exception:
        st.info("Start a conversation! / เริ่มคุยกันเลย!")
    
    with st.form("msg_v35", clear_on_submit=True):
        txt = st.text_input("Type Message / พิมพ์ข้อความ")
        if st.form_submit_button("SEND / ส่ง"):
            if txt:
                chat_ref.push({
                    'sender': my_id, 'text': txt, 'timestamp': datetime.now().isoformat()
                })
                st.rerun()

st.caption("SYNAPSE V3.5 | GLOBAL POSITIONING | NO LIES")
