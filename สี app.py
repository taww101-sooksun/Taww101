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
st.set_page_config(page_title="SYNAPSE PURITY", layout="wide")
st.markdown("""
    <style>
    @keyframes RainbowFlow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .stApp { background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff); background-size: 1200% 1200%; animation: RainbowFlow 180s ease infinite; }
    .status-box { background: rgba(0,0,0,0.8); padding: 15px; border-radius: 10px; border: 1px solid #00ff00; color: #00ff00; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGO (จาก GitHub ของนาย) ---
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

# --- 5. DATA CLEANING & FETCH (ล้างขยะพิกัดเก่า) ---
all_users = db.reference('/users').get() or {}
current_ts = time.time()

# กรองเฉพาะคนที่ Online จริง (พิกัดต้องไม่เก่าเกิน 5 นาที)
active_users = {}
for uid, udata in all_users.items():
    loc_data = udata.get('location', {})
    last_sync = loc_data.get('last_sync', 0)
    # ถ้าซิงค์ล่าสุดไม่เกิน 300 วินาที ให้ถือว่า Active
    if (current_ts - last_sync) < 300:
        active_users[uid] = udata

friend_list = [u for u in active_users.keys() if u != my_id]

# --- 6. LIVE RADAR FRAGMENT (เน้น GPS 2 ภาษา) ---
@st.fragment(run_every=10)
def purity_radar(users_to_show):
    location = get_geolocation()
    if location:
        coords = location.get('coords', {})
        lat, lon = coords.get('latitude'), coords.get('longitude')
        
        if lat and lon:
            # คำนวณเวลา 2 ภาษา (TH / UK-UTC)
            tf = TimezoneFinder()
            tz_name = tf.timezone_at(lng=lon, lat=lat)
            time_th = datetime.now(pytz.timezone(tz_name)).strftime('%H:%M:%S')
            time_uk = datetime.now(pytz.utc).strftime('%H:%M:%S UTC')
            
            # อัปเดตพิกัดสดใหม่ลง Cloud
            db.reference(f'/users/{my_id}/location').update({
                'lat': lat, 'lon': lon,
                'last_sync': time.time(),
                'time_th': time_th,
                'time_uk': time_uk
            })

            # แผนที่ (Zoom 17 ให้เห็นมุดชัดๆ)
            m = folium.Map(location=[lat, lon], zoom_start=17, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')
            
            for uid, udata in users_to_show.items():
                loc = udata.get('location', {})
                u_lat, u_lon = loc.get('lat'), loc.get('lon')
                if u_lat and u_lon:
                    color = 'red' if uid == my_id else 'blue'
                    folium.Marker([u_lat, u_lon], icon=folium.Icon(color=color, icon='screenshot', prefix='glyphicon')).add_to(m)
                    # ชื่อบ่งบอกมุด
                    folium.map.Marker([u_lat, u_lon], icon=folium.features.DivIcon(
                        icon_size=(150,36),
                        html=f'<div style="font-size: 11pt; color: {color}; font-weight: bold; text-shadow: 2px 2px black;">{uid}</div>'
                    )).add_to(m)

            st_folium(m, use_container_width=True, height=500, key="radar_purity")
            
            # แสดงเวลา 2 ภาษา
            st.markdown(f"""
            <div class="status-box">
                <b>🇹🇭 TIME (TH):</b> {time_th}<br>
                <b>🇬🇧 TIME (UK/UTC):</b> {time_uk}<br>
                <b>🛰️ GPS STATUS:</b> ACTIVE (REAL-TIME)
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("🛰️ Searching for GPS signal... / กำลังค้นหาสัญญาณ...")
    else:
        st.info("💡 Please enable GPS / โปรดเปิด GPS เพื่อระบุตัวตน")

purity_radar(active_users)

# --- 7. CLEAN CHAT ---
st.write("---")
chat_target = st.selectbox("💬 CHAT WITH (ONLINE ONLY):", ["-- Select Friend --"] + friend_list)

if chat_target != "-- Select Friend --":
    ids = sorted([my_id, chat_target])
    chat_id = f"chat_{ids[0]}_{ids[1]}"
    msgs = db.reference(f'/messages/{chat_id}').limit_to_last(5).get()
    if msgs:
        for m in sorted(msgs.values(), key=lambda x: x.get('timestamp', '')):
            st.write(f"**{m['sender']}:** {m['text']}")
    
    with st.form("send_msg", clear_on_submit=True):
        txt = st.text_input("Transmission... / พิมพ์ข้อความ")
        if st.form_submit_button("SEND / ส่ง"):
            if txt:
                db.reference(f'/messages/{chat_id}').push({
                    'sender': my_id, 'text': txt, 'timestamp': datetime.now().isoformat()
                })
                st.rerun()

st.caption("SYNAPSE V3.4 | PURITY SYSTEM | NO OLD DATA | REAL-TIME TRUTH")
