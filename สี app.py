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

# --- 2. CONFIG & STYLE ---
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")

st.markdown("""
    <style>
    @keyframes RainbowFlow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
    .stApp { 
        background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff); 
        background-size: 1200% 1200%; 
        animation: RainbowFlow 60s ease infinite; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGO (Size 300 & Check Lowercase) ---
logo_file = "logo2.jpg" if os.path.exists("logo2.jpg") else "Logo2.jpg"
if os.path.exists(logo_file):
    st.image(logo_file, width=300)
else:
    st.markdown("<h1 style='color: white;'>S Y N A P S E</h1>", unsafe_allow_html=True)

# --- 4. ACCESS CONTROL (Bilingual) ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h3 style='color: white;'>🔐 ACCESS CONTROL / ระบบควบคุมการเข้าถึง</h3>", unsafe_allow_html=True)
    with st.form("Login"):
        u_id = st.text_input("Enter ID / ใส่ไอดี")
        u_pw = st.text_input("Password / รหัสผ่าน", type="password")
        if st.form_submit_button("UNLOCK / ปลดล็อค"):
            if u_pw == "9999999" and u_id:
                st.session_state.authenticated = True
                st.session_state.my_id = u_id
                st.rerun()
    st.stop()

my_id = st.session_state.my_id
all_users = db.reference('/users').get() or {}

# --- 5. GPS & TACTICAL RADAR (English Included) ---
st.subheader("📡 RADAR SYSTEM / ระบบเรดาร์")
location = get_geolocation()

if location:
    coords = location.get('coords', {})
    lat, lon = coords.get('latitude'), coords.get('longitude')
    
    if lat and lon:
        # Timezone & Weather
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lng=lon, lat=lat)
        local_tz = pytz.timezone(tz_name)
        now_dt = datetime.now(local_tz)
        
        w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        try:
            temp = requests.get(w_url).json().get('current_weather', {}).get('temperature', '??')
        except:
            temp = "??"

        # Cloud Update
        db.reference(f'/users/{my_id}/location').update({
            'lat': lat, 'lon': lon,
            'temp': f"{temp}°C",
            'time_intl': now_dt.strftime('%Y-%m-%d %H:%M:%S %Z'),
            'tz': tz_name
        })

        # Folium Map
        m = folium.Map(location=[lat, lon], zoom_start=16, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')

        for user_id, user_data in all_users.items():
            loc = user_data.get('location', {})
            u_lat, u_lon = loc.get('lat'), loc.get('lon')
            if u_lat and u_lon:
                is_me = (user_id == my_id)
                color = 'red' if is_me else 'blue'
                
                # Popup Info in English/Thai
                info_html = f"""
                <div style="font-family: Arial; font-size: 10pt; width: 180px;">
                    <b>ID:</b> {user_id}<br>
                    <b>Temp/อากาศ:</b> {loc.get('temp', 'N/A')}<br>
                    <b>Time/เวลา:</b> {loc.get('time_intl', 'N/A')}<br>
                    <b>Zone:</b> {loc.get('tz', 'N/A')}
                </div>
                """
                
                folium.Marker(
                    [u_lat, u_lon],
                    popup=folium.Popup(info_html, max_width=250),
                    tooltip=f"{user_id}",
                    icon=folium.Icon(color=color, icon='user', prefix='fa')
                ).add_to(m)

                folium.map.Marker(
                    [u_lat, u_lon],
                    icon=folium.features.DivIcon(
                        icon_size=(150,36),
                        html=f'<div style="font-size: 11pt; color: {color}; font-weight: bold; text-shadow: 2px 2px black;">{user_id}</div>',
                    )
                ).add_to(m)

        st_folium(m, use_container_width=True, height=400, key="global_radar")
    else:
        st.warning("🛰️ Searching for Satellites... / กำลังค้นหาสัญญาณดาวเทียม...")
else:
    st.info("💡 Please Enable GPS / โปรดเปิด GPS เพื่อระบุตำแหน่ง")

# --- 6. MESSENGER (Bilingual) ---
st.write("---")
st.subheader("💬 MESSENGER / ระบบส่งข้อความ")

friend_options = [u for u in all_users.keys() if u != my_id]
chat_target = st.selectbox("Select Target / เลือกเพื่อน", ["-- Select --"] + friend_options)

if chat_target != "-- Select --":
    st.success(f"✅ LINK ACTIVE: {chat_target} / เชื่อมต่อสำเร็จ")
    ids = sorted([my_id, chat_target])
    chat_id = f"chat_{ids[0]}_{ids[1]}"
    
    raw_msgs = db.reference(f'/messages/{chat_id}').get()
    if raw_msgs:
        sorted_msgs = sorted(raw_msgs.values(), key=lambda x: x.get('timestamp', ''))
        for m in sorted_msgs[-5:]:
            sender_label = "ME" if m['sender'] == my_id else m['sender']
            st.write(f"**[{sender_label}]:** {m['text']}")
    
    with st.form("msg_form", clear_on_submit=True):
        m_text = st.text_input("Message / ข้อความ...")
        if st.form_submit_button("SEND / ส่ง"):
            if m_text:
                db.reference(f'/messages/{chat_id}').push({
                    'sender': my_id, 'text': m_text, 'timestamp': datetime.now().isoformat()
                })
                st.rerun()

# --- 7. YOUTUBE (Size 150) ---
st.write("---")
yt_url = "https://www.youtube.com/embed?listType=playlist&list=PL6S211I3urvpt47sv8mhbexif2YOzs2gO&autoplay=1&mute=1"
st.markdown(f'<iframe width="100%" height="150" src="{yt_url}" frameborder="0" allow="autoplay; encrypted-media"></iframe>', unsafe_allow_html=True)

st.caption("SYNAPSE V2.6 | BILINGUAL SYSTEM | REAL-TIME TRUTH")
