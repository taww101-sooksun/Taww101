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
        st.error(f"Firebase Connection Error: {e}")

# --- 2. SECURITY GATE ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>🔐 ACCESS CONTROL</h2>", unsafe_allow_html=True)
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

# --- 3. STYLE & RAINBOW (Compact Mode) ---
st.markdown("""
    <style>
    @keyframes RainbowFlow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .stApp { background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff); background-size: 1200% 1200%; animation: RainbowFlow 180s ease infinite; }
    .stMetric { background-color: rgba(0, 0, 0, 0.8) !important; padding: 5px !important; border-radius: 10px; border: 1px solid white; }
    div[data-testid="stMetricValue"] > div { font-size: 1.5rem !important; } /* ย่อขนาดตัวเลขให้เล็กลงหน่อยไม่กินที่ */
    </style>
    """, unsafe_allow_html=True)

# --- 4. HEADER & LOGO CHECK ---
# ตรวจสอบไฟล์โลโก้ ถ้าไม่มีให้ใช้ Text Header แทน
if os.path.exists("logo2.jpg"):
    st.image("logo2.jpg", width=500)
else:
    st.markdown("<h1 style='text-align: center; color: white;'>S Y N A P S E</h1>", unsafe_allow_html=True)

st.write(f"👤 **ID:** {my_id} | **Status:** 'อยู่นิ่งๆ ไม่เจ็บตัว'")

# --- 5. CALL & SEARCH SYSTEM ---
with st.expander("🔍 ค้นหาและโทรหาเพื่อน", expanded=False):
    all_users = db.reference('/users').get()
    friend_options = [u for u in all_users.keys() if u != my_id] if all_users else []
    target = st.selectbox("เลือกเพื่อน", ["-- Select --"] + friend_options)
    if st.button("📞 CALL NOW📞"):
        if target != "-- Select --":
            room_id = f"SYNAPSE-{uuid.uuid4().hex[:6]}"
            db.reference(f'/calls/{target}').set({'from': my_id, 'room': room_id, 'status': 'calling'})
            st.session_state.active_room = room_id
            st.session_state.call_target = target

# --- 6. INCOMING CALL LISTENER ---
try:
    call_data = db.reference(f'/calls/{my_id}').get()
    if call_data and call_data.get('status') == 'calling':
        st.warning(f"🚨 📢สายเรียกเข้าจาก: {call_data.get('from')}")
        col_a, col_r = st.columns(2)
        if col_a.button("✅ รับสาย✅"):
            st.session_state.active_room = call_data.get('room')
            st.session_state.call_target = call_data.get('from')
            db.reference(f'/calls/{my_id}').update({'status': 'connected'})
            st.rerun()
        if col_r.button("❌ ไม่รับ📵"):
            db.reference(f'/calls/{my_id}').delete()
            st.rerun()
except: pass

# --- 7. CORE DATA (COMPACT REALITY) ---
location = get_geolocation()
if location:
    coords = location.get('coords', {})
    lat, lon = coords.get('latitude'), coords.get('longitude')
    if lat and lon:
        db.reference(f'/users/{my_id}/location').update({'lat': lat, 'lon': lon, 'time': datetime.now().isoformat()})
        
        # ยุบแถบข้อมูลให้ประหยัดพื้นที่
        w_res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()['current_weather']
        c1, c2, c3 = st.columns(3)
        c1.metric("🌡️ Temp", f"{w_res['temperature']}°C")
        c2.metric("💨 Wind", f"{w_res['windspeed']}k/h")
        c3.metric("⏰ Time", datetime.now().strftime('%H:%M'))
        
        st.caption(f"📍 พิกัดจริงของคุณ: {lat:.5f}, {lon:.5f}")

        # --- แผนที่ HYBRID (ใหญ่สะใจ) ---
        m = folium.Map(location=[lat, lon], zoom_start=17, 
                       tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
                       attr='Google Hybrid')
        folium.Marker([lat, lon], icon=folium.Icon(color='blue', icon='user', prefix='fa')).add_to(m)
        
        # แสดงพิกัดเพื่อนถ้าเชื่อมต่ออยู่
        if "call_target" in st.session_state:
            f_data = db.reference(f'/users/{st.session_state.call_target}/location').get()
            if f_data:
                folium.Marker([f_data['lat'], f_data['lon']], icon=folium.Icon(color='red', icon='eye', prefix='fa')).add_to(m)
        
        st_folium(m, use_container_width=True, height=300)
    else: st.warning("🛰️ กำลังรับสัญญาณดาวเทียม...")
else: st.info("💡 โปรดอนุญาต GPS")

# --- 8. ACTIVE CALL ---
if "active_room" in st.session_state:
    st.markdown(f'<iframe src="https://meet.jit.si/{st.session_state.active_room}" allow="camera; microphone; fullscreen" width="100%" height="300" style="border: 2px solid white; border-radius: 15px;"></iframe>', unsafe_allow_html=True)
    if st.button("❌ END CALL❌"):
        db.reference(f'/calls/{st.session_state.call_target}').delete()
        del st.session_state.active_room
        st.rerun()

# --- 9. YOUTUBE AUTOPLAY (บังคับเปิดตลอด) ---
st.write("---")
# ใส่ &autoplay=1&mute=1 เพื่อให้เล่นอัตโนมัติบน Browser ส่วนใหญ่ (ต้องติด Mute ไว้ตามนโยบาย Chrome/Safari)
# เพิ่ม loop=1 และ playlist ID เพื่อให้วนลูป
playlist_id = "PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
st.markdown(f'''
    <iframe width="100%" height="300" 
    src="https://www.youtube.com/embed?listType=playlist&list={playlist_id}&autoplay=1&loop=1&mute=1&playlist={playlist_id}" 
    frameborder="0" allow="autoplay; encrypted-media"></iframe>
    ''', unsafe_allow_html=True)

st.caption("SYNAPSE V1.9 | REAL DATA | NO LIES")
