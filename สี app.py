import streamlit as st
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

# --- 2. THEME (Slow Rainbow 180s) ---
st.set_page_config(page_title="SYNAPSE ZERO", layout="wide")
st.markdown("""
    <style>
    @keyframes RainbowFlow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .stApp { background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff); background-size: 1200% 1200%; animation: RainbowFlow 180s ease infinite; }
    .status-box { background: rgba(0,0,0,0.85); padding: 15px; border-radius: 12px; border: 2px solid #00ff00; color: #00ff00; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. AUTO-LOGIN (Session State) ---
if 'my_id' not in st.session_state:
    st.session_state.my_id = None

if not st.session_state.my_id:
    st.image("https://raw.githubusercontent.com/taww101/taww101/main/logo2.jpg", width=250)
    input_id = st.text_input("Enter ID / ชื่อเรียก:")
    if st.button("CONNECT"):
        if input_id:
            st.session_state.my_id = input_id
            st.rerun()
    st.stop()

my_id = st.session_state.my_id

# --- 4. CORE ENGINE (Fragment for Data & Map) ---
@st.fragment(run_every=10) # ปรับเป็น 10 วินาที เพื่อให้นิ่งที่สุด
def tactical_radar():
    # ดึงพิกัด (ดึงใหม่ทุก 10 วิ)
    location = get_geolocation()
    all_users = db.reference('/users').get() or {}
    current_ts = time.time()
    
    # กรองเฉพาะคนที่ Online (5 นาทีล่าสุด)
    active_users = {uid: data for uid, data in all_users.items() 
                    if (current_ts - data.get('location', {}).get('last_sync', 0)) < 300}

    if location:
        coords = location.get('coords', {})
        lat, lon = coords.get('latitude'), coords.get('longitude')
        
        if lat and lon:
            # คำนวณเวลา (Global Sync)
            tf = TimezoneFinder()
            tz_name = tf.timezone_at(lng=lon, lat=lat)
            time_local = datetime.now(pytz.timezone(tz_name)).strftime('%H:%M:%S')
            time_utc = datetime.now(pytz.utc).strftime('%H:%M:%S UTC')

            # อัปเดตข้อมูลขึ้น Firebase
            db.reference(f'/users/{my_id}/location').update({
                'lat': lat, 'lon': lon,
                'last_sync': time.time(),
                'time_local': time_local,
                'time_uk': time_utc
            })

            # สร้างแผนที่ (จุดตาย: ใส่ key แบบคงที่ ไม่เปลี่ยนตามเวลา)
            m = folium.Map(location=[lat, lon], zoom_start=17, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')
            
            for uid, udata in active_users.items():
                loc = udata.get('location', {})
                u_lat, u_lon = loc.get('lat'), loc.get('lon')
                if u_lat and u_lon:
                    color = 'red' if uid == my_id else 'blue'
                    folium.Marker([u_lat, u_lon], icon=folium.Icon(color=color, icon='screenshot', prefix='glyphicon')).add_to(m)
                    folium.map.Marker([u_lat, u_lon], icon=folium.features.DivIcon(
                        icon_size=(150,36),
                        html=f'<div style="font-size: 11pt; color: {color}; font-weight: bold; text-shadow: 2px 2px black;">{uid}</div>'
                    )).add_to(m)

            # --- จุดสำคัญ: key="fixed_radar" จะทำให้แผนที่ไม่อันตรธานหายไปตอนอัปเดต ---
            st_folium(m, use_container_width=True, height=500, key="fixed_radar")
            
            st.markdown(f"""
            <div class="status-box">
                <b>COMMANDER:</b> {my_id} | <b>STATUS:</b> ACTIVE<br>
                <b>📍 LOCAL TIME:</b> {time_local}<br>
                <b>🌍 GLOBAL UTC:</b> {time_utc}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("🛰️ Searching for GPS signal...")
    else:
        st.info("💡 Please Allow GPS Access")

# --- 5. RUN SYSTEM ---
st.image("https://raw.githubusercontent.com/taww101/taww101/main/logo2.jpg", width=200)
tactical_radar()

st.write("---")
# (ส่วนแชทถ้าเพื่อนยังต้องการใช้ ให้เปิดแอปหน้าใหม่จะนิ่งกว่า หรือใส่ไว้ล่างสุด)
st.caption("SYNAPSE V3.7 | NO FLICKER | REAL-TIME TRUTH")
