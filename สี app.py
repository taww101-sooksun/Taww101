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

# --- 2. THEME & AUTO-LOGIN SETUP ---
st.set_page_config(page_title="SYNAPSE AUTO-PILOT", layout="wide")

# ระบบจดจำ User อัตโนมัติ (ถ้าเคยพิมพ์ชื่อไว้ครั้งหนึ่งแล้วจะไม่ถามอีก)
if 'my_id' not in st.session_state:
    st.session_state.my_id = None

st.markdown("""
    <style>
    @keyframes RainbowFlow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .stApp { background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff); background-size: 1200% 1200%; animation: RainbowFlow 180s ease infinite; }
    .status-box { background: rgba(0,0,0,0.85); padding: 15px; border-radius: 12px; border: 2px solid #00ff00; color: #00ff00; font-family: 'Courier New', monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGO ---
st.image("https://raw.githubusercontent.com/taww101/taww101/main/logo2.jpg", width=250)

# --- 4. AUTO-LOGIN LOGIC ---
if not st.session_state.my_id:
    st.subheader("🚀 INITIALIZE SYSTEM / เริ่มต้นระบบ")
    input_id = st.text_input("ENTER YOUR CALLSIGN (ชื่อเรียกของคุณ):", placeholder="เช่น Commander-1")
    if st.button("CONNECT SYSTEM"):
        if input_id:
            st.session_state.my_id = input_id
            st.rerun()
    st.stop()

my_id = st.session_state.my_id

# --- 5. GPS & DATA CORE ---
@st.fragment(run_every=5) # ปรับเหลือ 5 วินาทีเพื่อให้มุด "ติดตาม" ได้ลื่นขึ้น
def auto_pilot_radar():
    location = get_geolocation()
    all_users = db.reference('/users').get() or {}
    current_ts = time.time()
    
    # กรองคนออนไลน์ (3 นาทีล่าสุด)
    active_users = {uid: data for uid, data in all_users.items() 
                    if (current_ts - data.get('location', {}).get('last_sync', 0)) < 180}

    if location:
        coords = location.get('coords', {})
        lat, lon = coords.get('latitude'), coords.get('longitude')
        
        if lat and lon:
            # คำนวณเวลาอัตโนมัติตามพิกัด
            tf = TimezoneFinder()
            tz_name = tf.timezone_at(lng=lon, lat=lat)
            time_local = datetime.now(pytz.timezone(tz_name)).strftime('%H:%M:%S')
            time_utc = datetime.now(pytz.utc).strftime('%H:%M:%S UTC')

            # ⚡ บังคับเขียนข้อมูล (Force Write) ทุกครั้งที่ขยับ
            db.reference(f'/users/{my_id}/location').update({
                'lat': lat, 'lon': lon,
                'last_sync': time.time(),
                'time_local': time_local,
                'time_uk': time_utc
            })

            # แผนที่ (Fixed Zoom เพื่อความนิ่ง)
            m = folium.Map(location=[lat, lon], zoom_start=18, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')
            
            for uid, udata in active_users.items():
                loc = udata.get('location', {})
                u_lat, u_lon = loc.get('lat'), loc.get('lon')
                if u_lat and u_lon:
                    color = 'red' if uid == my_id else 'blue'
                    # หมุดเน้นความชัดเจน
                    folium.Marker([u_lat, u_lon], icon=folium.Icon(color=color, icon='screenshot', prefix='glyphicon')).add_to(m)
                    # ชื่อลอยบนหัวหมุด
                    folium.map.Marker([u_lat, u_lon], icon=folium.features.DivIcon(
                        icon_size=(150,36),
                        html=f'<div style="font-size: 12pt; color: {color}; font-weight: bold; text-shadow: 2px 2px black;">{uid}</div>'
                    )).add_to(m)

            st_folium(m, use_container_width=True, height=500, key=f"radar_sync_{time.time()}")
            
            st.markdown(f"""
            <div class="status-box">
                <b>🛰️ COMMANDER:</b> {my_id} | <b>STATUS:</b> ONLINE<br>
                <b>📍 LOCAL TIME:</b> {time_local}<br>
                <b>🌍 GLOBAL UTC:</b> {time_utc}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("🛰️ Searching for GPS Satellite...")
    else:
        st.info("💡 Please 'Allow' Location Access / โปรดกดยอมรับตำแหน่ง")

auto_pilot_radar()

# --- 6. SIMPLE CHAT ---
st.write("---")
friend_list = [u for u in all_users.keys() if u != my_id and (current_ts - all_users[u].get('location', {}).get('last_sync', 0)) < 300]
target = st.selectbox("💬 QUICK CHAT:", ["-- Online Friends --"] + friend_list)

if target != "-- Online Friends --":
    ids = sorted([my_id, target])
    chat_id = f"chat_{ids[0]}_{ids[1]}"
    chat_ref = db.reference(f'/messages/{chat_id}')
    
    msgs = chat_ref.limit_to_last(5).get()
    if msgs:
        for m in sorted(msgs.values(), key=lambda x: x.get('timestamp', '')):
            st.write(f"**{m['sender']}:** {m['text']}")
            
    with st.form("quick_send", clear_on_submit=True):
        msg_txt = st.text_input("Message...")
        if st.form_submit_button("SEND"):
            if msg_txt:
                chat_ref.push({'sender': my_id, 'text': msg_txt, 'timestamp': datetime.now().isoformat()})
                st.rerun()

st.caption("SYNAPSE V3.6 | AUTO-PILOT ENABLED | REAL-TIME TRUTH")
