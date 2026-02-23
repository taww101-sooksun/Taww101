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
st.set_page_config(page_title="SYNAPSE STABLE", layout="wide")

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

# --- 3. TACTICAL BLACK STYLE ---
st.markdown("""
    <style>
    @keyframes RainbowFlow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .stApp { background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff); background-size: 1200% 1200%; animation: RainbowFlow 180s ease infinite; }
    
    /* ปุ่มดำ-ตัวหนังสือขาว */
    button, .stButton>button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
        border-radius: 10px !important;
    }
    
    /* กล่องข้อมูลสีดำ */
    [data-testid="stMetric"] {
        background-color: rgba(0, 0, 0, 0.9) !important;
        border: 1px solid #ffffff !important;
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. GPS & MAP ENGINE (แยกส่วนเพื่อไม่ให้กะพริบ) ---
@st.fragment(run_every=30) # อัปเดตพิกัดทุก 30 วินาทีเพื่อความนิ่งสูงสุด
def map_engine():
    location = get_geolocation()
    if location:
        coords = location.get('coords', {})
        lat, lon = coords.get('latitude'), coords.get('longitude')
        if lat and lon:
            # เก็บพิกัดลง Firebase
            db.reference(f'/users/{my_id}/location').update({
                'lat': lat, 'lon': lon, 'last_sync': time.time()
            })
            
            # วาดแผนที่ (ใช้ Key คงที่เพื่อไม่ให้กะพริบ)
            m = folium.Map(location=[lat, lon], zoom_start=17, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')
            folium.Marker([lat, lon], icon=folium.Icon(color='red', icon='screenshot', prefix='glyphicon')).add_to(m)
            
            # แสดงแผนที่
            st_folium(m, use_container_width=True, height=450, key="fixed_tactical_map")
    else:
        st.info("📡 WAITING FOR GPS...")

# --- 5. GPS TIME CLOCK (แยกส่วนทำงานต่างหาก) ---
@st.fragment(run_every=1) # อัปเดตเฉพาะตัวเลขนาฬิกาทุก 1 วินาที
def clock_engine():
    # ดึงพิกัดล่าสุดจาก session หรือดึงใหม่แบบเร็วๆ
    loc = get_geolocation()
    if loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lng=lon, lat=lat)
        local_time = datetime.now(pytz.timezone(tz_name)).strftime('%H:%M:%S')
        
        c1, c2 = st.columns(2)
        c1.metric("🛰️ GPS TIME (LOCAL)", local_time)
        c2.metric("🌍 TIMEZONE", tz_name.split('/')[-1])

# --- 6. UI LAYOUT ---
if os.path.exists("logo2.jpg"):
    st.image("logo2.jpg", width=200)

clock_engine() # นาฬิกาทำงานอิสระ ไม่กวนแผนที่
map_engine()   # แผนที่ทำงานอิสระ ไม่กวนนาฬิกา

# --- 7. CALL SYSTEM ---
with st.expander("🔍 CALL TARGET", expanded=False):
    all_users = db.reference('/users').get() or {}
    target = st.selectbox("SELECT FRIEND", ["-- Select --"] + [u for u in all_users.keys() if u != my_id])
    if st.button("📞 INITIATE"):
        if target != "-- Select --":
            room = f"SYNAPSE-{uuid.uuid4().hex[:6]}"
            db.reference(f'/calls/{target}').set({'from': my_id, 'room': room, 'status': 'calling'})

st.write("---")
st.caption("SYNAPSE V2.1 | ZERO-FLICKER | GPS TIME SYNC")
