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
            if u_pw == "synapse2026" and u_id: 
                st.session_state.authenticated = True
                st.session_state.my_id = u_id
                st.rerun()
    st.stop()

my_id = st.session_state.my_id

# --- 3. STYLE & RAINBOW ---
st.markdown("""
    <style>
    @keyframes RainbowFlow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .stApp { background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff); background-size: 1200% 1200%; animation: RainbowFlow 15s ease infinite; }
    .stMetric { background-color: rgba(0, 0, 0, 0.8) !important; padding: 5px !important; border-radius: 10px; border: 1px solid white; }
    </style>
    """, unsafe_allow_html=True)

if os.path.exists("logo2.jpg"):
    st.image("logo2.jpg", width=300)
else:
    st.markdown("<h1 style='text-align: center; color: white;'>S Y N A P S E</h1>", unsafe_allow_html=True)

st.write(f"👤 **ID:** {my_id} | **Status:** 'อยู่นิ่งๆ ไม่เจ็บตัว'")

# --- 4. CALL & SEARCH SYSTEM (ของเดิมคงไว้) ---
with st.expander("🔍 ค้นหาและโทรหาเพื่อน", expanded=False):
    all_users = db.reference('/users').get()
    friend_options = [u for u in all_users.keys() if u != my_id] if all_users else []
    target = st.selectbox("เลือกเพื่อนที่จะโทรหา", ["-- Select --"] + friend_options)
    if st.button("📞 CALL NOW"):
        if target != "-- Select --":
            room_id = f"SYNAPSE-{uuid.uuid4().hex[:6]}"
            db.reference(f'/calls/{target}').set({'from': my_id, 'room': room_id, 'status': 'calling'})
            st.session_state.active_room = room_id
            st.session_state.call_target = target

# --- 5. CHAT SYSTEM (เพิ่มเข้าไปใหม่ตามสั่ง) ---
with st.expander("💬 แชทกับเพื่อน (Real-time)", expanded=True):
    chat_target = st.selectbox("เลือกเพื่อนที่จะแชทด้วย", ["-- Select --"] + friend_options, key="chat_select")
    if chat_target != "-- Select --":
        ids = sorted([my_id, chat_target])
        chat_id = f"chat_{ids[0]}_{ids[1]}"
        
        # แสดงข้อความ
        msgs = db.reference(f'/messages/{chat_id}').order_by_child('timestamp').limit_to_last(15).get()
        chat_box = st.container(height=250)
        if msgs:
            for m_id, m_data in msgs.items():
                with chat_box:
                    st.chat_message("user" if m_data['sender'] == my_id else "assistant").write(f"**{m_data['sender']}**: {m_data['text']}")
        
        # ส่งข้อความ
        with st.form("send_chat", clear_on_submit=True):
            m_text = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("SEND"):
                if m_text:
                    db.reference(f'/messages/{chat_id}').push({
                        'sender': my_id, 'text': m_text, 'timestamp': datetime.now().isoformat()
                    })
                    st.rerun()

# --- 6. CORE GPS & TIMEZONE (ปรับปรุงนาฬิกาตามที่นายบอก) ---
location = get_geolocation()
if location:
    coords = location.get('coords', {})
    lat, lon = coords.get('latitude'), coords.get('longitude')
    if lat and lon:
        # ระบบนาฬิกาตามพิกัดจริง
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lng=lon, lat=lat)
        local_tz = pytz.timezone(tz_name)
        time_at_location = datetime.now(local_tz)

        db.reference(f'/users/{my_id}/location').update({'lat': lat, 'lon': lon, 'time': time_at_location.isoformat()})
        
        w_res = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true").json()['current_weather']
        c1, c2, c3 = st.columns(3)
        c1.metric("🌡️ Temp", f"{w_res['temperature']}°C")
        c2.metric("⏰ Local Time", time_at_location.strftime('%H:%M:%S'))
        c3.metric("🌍 Zone", tz_name)
        
        # แผนที่ Hybrid (ของเดิม)
        m = folium.Map(location=[lat, lon], zoom_start=17, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')
        folium.Marker([lat, lon], icon=folium.Icon(color='blue', icon='user', prefix='fa')).add_to(m)
        st_folium(m, use_container_width=True, height=500)
    else: st.warning("🛰️ กำลังรับสัญญาณดาวเทียม...")
else: st.info("💡 โปรดอนุญาต GPS")

# --- 7. VIDEO CALL & YOUTUBE (ของเดิมคงไว้ทั้งหมด) ---
if "active_room" in st.session_state:
    st.markdown(f'<iframe src="https://meet.jit.si/{st.session_state.active_room}" allow="camera; microphone; fullscreen" width="100%" height="500" style="border: 2px solid white; border-radius: 15px;"></iframe>', unsafe_allow_html=True)
    if st.button("❌ END CALL"):
        db.reference(f'/calls/{st.session_state.call_target}').delete()
        del st.session_state.active_room
        st.rerun()

st.write("---")
playlist_id = "PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
st.markdown(f'''<iframe width="100%" height="150" src="https://www.youtube.com/embed?listType=playlist&list={playlist_id}&autoplay=1&loop=1&mute=1&playlist={playlist_id}" frameborder="0" allow="autoplay; encrypted-media"></iframe>''', unsafe_allow_html=True)

st.caption("SYNAPSE V2.1 | NO DATA REMOVED | REAL-TIME TRUTH")
