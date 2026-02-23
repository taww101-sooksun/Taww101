import streamlit as st
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import pytz
import time

# --- 1. FIREBASE SETUP ---
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_service_account"])
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
    except Exception as e:
        st.error(f"Error: {e}")

# --- 2. UI & RAINBOW ---
st.set_page_config(page_title="SYNAPSE ALWAYS-ON", layout="wide")
st.markdown("""
    <style>
    @keyframes Rainbow { 0% {background-position:0% 50%} 50% {background-position:100% 50%} 100% {background-position:0% 50%} }
    .stApp { background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff); background-size: 1000% 1000%; animation: Rainbow 180s ease infinite; }
    .status-card { background: rgba(0,0,0,0.8); padding: 10px; border-radius: 10px; border: 1px solid #00ff00; color: #00ff00; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. AUTO-ID (ไม่ต้องล็อกอินบ่อย) ---
# ระบบจะจำ ID ไว้ใน Session ถ้าปิดแท็บแล้วเปิดใหม่ในวันเดียวกันจะยังจำได้
if 'my_id' not in st.session_state:
    st.session_state.my_id = st.query_params.get("id", None) # ลองดึงจาก URL เผื่อส่งลิงก์แบบระบุตัวตน

if not st.session_state.my_id:
    st.image("https://raw.githubusercontent.com/taww101/taww101/main/logo2.jpg", width=200)
    name_input = st.text_input("SET CALLSIGN / ตั้งชื่อเรียก (ครั้งแรกครั้งเดียว):")
    if st.button("START SYSTEM"):
        if name_input:
            st.session_state.my_id = name_input
            st.rerun()
    st.stop()

my_id = st.session_state.my_id

# --- 4. DATA CORE (อัปเดตพิกัดแบบเงียบๆ) ---
@st.fragment(run_every=15) # ปรับเป็น 15 วิ เพื่อความเสถียรและไม่กินทรัพยากรเครื่องจนโดนตัด
def update_system():
    loc = get_geolocation()
    all_users = db.reference('/users').get() or {}
    now_ts = time.time()
    
    if loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        # ซิงค์ข้อมูลขึ้น Cloud
        db.reference(f'/users/{my_id}/location').update({
            'lat': lat, 'lon': lon, 'last_sync': now_ts,
            'time_utc': datetime.now(pytz.utc).strftime('%H:%M:%S UTC')
        })

        # กรองเฉพาะคนที่ซิงค์ล่าสุดไม่เกิน 10 นาที (เผื่อเน็ตเพื่อนช้า)
        active = {u: d for u, d in all_users.items() if (now_ts - d.get('location', {}).get('last_sync', 0)) < 600}

        # แผนที่ (ใช้ Static Key เพื่อไม่ให้กะพริบ)
        m = folium.Map(location=[lat, lon], zoom_start=17, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')
        
        for uid, udata in active.items():
            u_loc = udata.get('location', {})
            if u_loc.get('lat'):
                color = 'red' if uid == my_id else 'blue'
                folium.Marker([u_loc['lat'], u_loc['lon']], icon=folium.Icon(color=color, icon='user', prefix='fa')).add_to(m)
                folium.map.Marker([u_loc['lat'], u_loc['lon']], icon=folium.features.DivIcon(
                    html=f'<div style="font-size: 10pt; color: {color}; font-weight: bold; text-shadow: 1px 1px black; width: 100px;">{uid}</div>'
                )).add_to(m)

        st_folium(m, use_container_width=True, height=450, key="main_radar")
        st.markdown(f'<div class="status-card">COMMANDER: {my_id} | STATUS: BROADCASTING...</div>', unsafe_allow_html=True)

# --- 5. EXECUTE ---
st.image("https://raw.githubusercontent.com/taww101/taww101/main/logo2.jpg", width=150)
update_system()

st.caption("SYNAPSE V3.8 | PERSISTENT CONNECTION | REAL-TIME TRUTH")
