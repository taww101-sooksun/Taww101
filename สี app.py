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
import uuid
import os
import time

# --- 1. INITIALIZE FIREBASE ---
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")

if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_service_account"])
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
    except Exception as e:
        st.error(f"Firebase Error: {e}")

# --- 2. SECURITY GATE ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    with st.form("Login"):
        u_id = st.text_input("Enter ID")
        u_pw = st.text_input("Password", type="password")
        if st.form_submit_button("UNLOCK"):
            if u_pw == "9999999" and u_id: 
                st.session_state.authenticated = True
                st.session_state.my_id = u_id
                st.rerun()
    st.stop()

my_id = st.session_state.my_id

# --- 3. TACTICAL BLACK STYLE (ปรับปุ่มดำ-ตัวหนังสือขาว) ---
st.markdown("""
    <style>
    @keyframes RainbowFlow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .stApp { background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff); background-size: 1200% 1200%; animation: RainbowFlow 180s ease infinite; }
    
    /* ปรับปุ่มทุกอย่างเป็นสีดำ ตัวหนังสือขาว */
    button, .stButton>button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
        border-radius: 10px !important;
        font-weight: bold !important;
    }
    
    /* ปรับช่อง Input และ Expander เป็นสีดำ */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #000000 !important;
        color: #ffffff !important;
    }
    
    /* แถบข้อมูล Metric สีดำเข้ม */
    [data-testid="stMetric"] {
        background-color: rgba(0, 0, 0, 0.9) !important;
        border: 1px solid #ffffff !important;
        padding: 10px !important;
        border-radius: 10px !important;
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. HEADER ---
if os.path.exists("logo2.jpg"):
    st.image("logo2.jpg", width=250)
else:
    st.markdown("<h1 style='text-align: center; color: white;'>S Y N A P S E</h1>", unsafe_allow_html=True)

# --- 5. GPS & TIME SYNC CORE ---
@st.fragment(run_every=10)
def tactical_core():
    location = get_geolocation()
    if location:
        coords = location.get('coords', {})
        lat, lon = coords.get('latitude'), coords.get('longitude')
        if lat and lon:
            # ⏰ คำนวณเวลาจากพิกัด GPS ทั่วโลก
            tf = TimezoneFinder()
            tz_name = tf.timezone_at(lng=lon, lat=lat)
            tz = pytz.timezone(tz_name)
            local_time = datetime.now(tz).strftime('%H:%M:%S')
            
            # อัปเดต Firebase
            db.reference(f'/users/{my_id}/location').update({
                'lat': lat, 'lon': lon, 
                'time_gps': local_time,
                'last_seen': time.time()
            })
            
            # ข้อมูลสภาพอากาศ & เวลา (Black Cards)
            w_res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()['current_weather']
            c1, c2, c3 = st.columns(3)
            c1.metric("🌡️ TEMP", f"{w_res['temperature']}°C")
            c2.metric("🛰️ TIME (GPS)", local_time)
            c3.metric("🌍 ZONE", tz_name.split('/')[-1])

            # --- แผนที่พร้อมเวลาบนหัวหมุด ---
            m = folium.Map(location=[lat, lon], zoom_start=17, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')
            
            # หมุดของเราเอง
            folium.Marker([lat, lon], icon=folium.Icon(color='red', icon='screenshot', prefix='glyphicon')).add_to(m)
            folium.map.Marker([lat, lon], icon=folium.features.DivIcon(
                html=f'<div style="font-size: 10pt; color: white; font-weight: bold; background: black; padding: 2px 5px; border-radius: 5px; border: 1px solid red; width: 120px;">{my_id} [{local_time}]</div>'
            )).add_to(m)

            st_folium(m, use_container_width=True, height=450, key="tactical_map")
    else:
        st.info("💡 GPS INITIALIZING...")

tactical_core()

# --- 6. CALL SYSTEM (ปุ่มดำตัวหนังสือขาวตาม Style) ---
with st.expander("🔍 SEARCH & CALL / ค้นหาเพื่อน", expanded=False):
    all_users = db.reference('/users').get() or {}
    friend_options = [u for u in all_users.keys() if u != my_id]
    target = st.selectbox("SELECT TARGET", ["-- Select --"] + friend_options)
    if st.button("📞 INITIATE CALL"):
        if target != "-- Select --":
            room_id = f"SYNAPSE-{uuid.uuid4().hex[:6]}"
            db.reference(f'/calls/{target}').set({'from': my_id, 'room': room_id, 'status': 'calling'})
            st.session_state.active_room = room_id

# --- 7. FOOTER & MUSIC ---
st.write("---")
playlist_id = "PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
st.markdown(f'<iframe width="100%" height="80" src="https://www.youtube.com/embed?listType=playlist&list={playlist_id}&autoplay=1&mute=1" frameborder="0" allow="autoplay"></iframe>', unsafe_allow_html=True)
st.caption("SYNAPSE V2.0 | TACTICAL BLACK | GPS PRECISION")
