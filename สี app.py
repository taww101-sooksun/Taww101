import streamlit as st
import os 
import time
import base64
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from math import radians, cos, sin, asin, sqrt
from folium.features import DivIcon

# ==========================================
# 0. ฟังก์ชันสนับสนุน (Helper Functions)
# ==========================================

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    d = 2 * asin(sqrt(sin((lat2-lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2-lon1)/2)**2)) 
    return d * 6371

def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'user' not in st.session_state: st.session_state.user = "Guest"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
        
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ Firebase Connection Error: {e}")

# ==========================================
# 1. ระบบจัดการ User (Login / Register)
# ==========================================

def room_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("logo1.jpg", use_container_width=True)
        except:
            st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color};'>SYNAPSE</h1>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align:center;'>🔐 เข้ารหัสการเข้าถึงระบบ</h3>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 เข้าสู่ระบบ", "📝 ลงทะเบียน AGENT"])
    
    with tab1:
        with st.form("login_form"):
            user_id = st.text_input("AGENT ID")
            password = st.text_input("PASSWORD", type="password")
            if st.form_submit_button("UNLOCK SYSTEM", use_container_width=True):
                user_data = db.reference(f'users/{user_id}').get()
                if user_data and user_data.get('pw') == password:
                    st.session_state.user = user_id
                    st.session_state.logged_in = True
                    st.success("Access Granted")
                    st.rerun()
                else:
                    st.error("❌ ข้อมูลไม่ถูกต้อง")
                    
    with tab2:
        with st.form("reg_form"):
            new_id = st.text_input("ตั้งชื่อ AGENT ID")
            new_pw = st.text_input("ตั้งรหัสผ่าน", type="password")
            if st.form_submit_button("REGISTER AGENT", use_container_width=True):
                if new_id and new_pw:
                    db.reference(f'users/{new_id}').set({'pw': new_pw, 'created_at': time.time()})
                    st.success("ลงทะเบียนสำเร็จ!")

# ==========================================
# 2. ฟังก์ชันห้องต่างๆ (Modules)
# ==========================================

def room_core():
    st.subheader("🚀 SYNAPSE COMMAND CENTER")
    now = datetime.utcnow() + timedelta(hours=7)
    st.markdown(f"""
        <div style="border: 2px solid {st.session_state.theme_color}; padding: 20px; border-radius: 15px; text-align: center; background: rgba(0,0,0,0.3);">
            <h1 style="color: {st.session_state.theme_color}; font-size: 3.5em; margin:0;">{now.strftime('%H:%M:%S')}</h1>
            <p style="letter-spacing: 5px; color: {st.session_state.theme_color};">SYSTEM ONLINE</p>
        </div>
    """, unsafe_allow_html=True)
    st.write(f"👤 AGENT ID: **{st.session_state.user}**")

def room_radar():
    st.subheader("🛰️ ระบบเรดาร์ (Satellite View)")
    loc = get_geolocation()
    my_lat, my_lon = (loc['coords']['latitude'], loc['coords']['longitude']) if loc else (13.7367, 100.5231)
    
    google_hybrid = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"
    m = folium.Map(location=[my_lat, my_lon], zoom_start=18, tiles=google_hybrid, attr='Google')
    
    # หมุดเรา
    folium.Marker([my_lat, my_lon], icon=folium.Icon(color='red', icon='user', prefix='fa')).add_to(m)
    
    # หมุดเพื่อน
    users = db.reference('users').get()
    if users:
        for uid, data in users.items():
            if uid != st.session_state.user and data.get('lat'):
                u_lat, u_lon = data['lat'], data['lon']
                dist = haversine(my_lat, my_lon, u_lat, u_lon)
                folium.Marker([u_lat, u_lon], icon=folium.Icon(color='green')).add_to(m)
                folium.Marker([u_lat-0.0001, u_lon], icon=DivIcon(html=f'<div style="color:white; background:green; padding:2px; border-radius:3px;">{uid} ({dist:.2f}km)</div>')).add_to(m)

    st_folium(m, width="100%", height=500)
    if st.button("📡 แชร์ตำแหน่งปัจจุบัน", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})

def room_public():
    st.subheader("🌐 แชตรวมระบบส่งไฟล์")
    with st.form("pub_chat", clear_on_submit=True):
        msg = st.text_input("ข้อความ")
        file = st.file_uploader("แนบไฟล์", type=['jpg', 'png', 'mp4'])
        if st.form_submit_button("ส่ง"):
            f_data = base64.b64encode(file.getvalue()).decode() if file else None
            db.reference('public_chat').push({'u': st.session_state.user, 'm': msg, 'file': f_data, 'ft': file.type if file else None, 'ts': time.time()})
            st.rerun()

def room_private():
    st.subheader("🔐 แชตส่วนตัวสายลับ")
    users = db.reference('users').get()
    target = st.selectbox("เลือกคู่สาย:", [u for u in users.keys() if u != st.session_state.user] if users else [])
    if target:
        rid = "_".join(sorted([st.session_state.user, target]))
        with st.form("p_form", clear_on_submit=True):
            msg = st.text_input("ข้อความลับ")
            if st.form_submit_button("ส่ง") and msg:
                db.reference(f'private_rooms/{rid}').push({'u': st.session_state.user, 'm': msg, 'ts': time.time()})
                st.rerun()

def room_music():
    st.subheader("🎧 ระบบสถานีเพลง")
    music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if music_files:
        song = music_files[st.session_state.song_index]
        with open(song, "rb") as f:
            st.audio(f.read(), format="audio/mp3")
        if st.button("⏭️ เพลงถัดไป"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()

def room_bio():
    # ... (คงโค้ด JavaScript Bio Sensor เดิมของคุณไว้) ...
    st.subheader("🩺 Bio Sensor")
    st.info("ใช้กล้องเพื่อตรวจวัดชีพจรเบื้องต้น")
    # [Insert your existing room_bio HTML/JS here]

def room_mission():
    st.subheader("📝 บันทึกภารกิจ")
    with st.form("m_form", clear_on_submit=True):
        t = st.text_input("ภารกิจใหม่:")
        if st.form_submit_button("💾 บันทึก") and t:
            db.reference('missions').push({'u': st.session_state.user, 't': t, 'ts': time.time()})
            st.rerun()
    
    data = db.reference('missions').limit_to_last(10).get()
    if data:
        for v in reversed(list(data.values())):
            st.info(f"📌 {v.get('t')} (By: {v.get('u')})")

# ==========================================
# 3. จุดเริ่มระบบ (Main Entry)
# ==========================================

def main():
    st.set_page_config(page_title="SYNAPSE OS", layout="wide")
    init_system()
    
    if not st.session_state.logged_in:
        room_login()
    else:
        with st.sidebar:
            st.title("⚙️ SETTINGS")
            st.write(f"Logged in as: **{st.session_state.user}**")
            if st.button("🚪 LOGOUT"):
                st.session_state.logged_in = False
                st.rerun()

        tabs = st.tabs(["🚀 แกนหลัก", "🛰️ เรดาร์", "🌐 แชตรวม", "🔐 แชตส่วนตัว", "🎧 เพลง", "🩺 ตรวจร่างกาย", "📝 ภารกิจ"])
        with tabs[0]: room_core()
        with tabs[1]: room_radar()
        with tabs[2]: room_public()
        with tabs[3]: room_private()
        with tabs[4]: room_music()
        with tabs[5]: room_bio()
        with tabs[6]: room_mission()

if __name__ == "__main__":
    main()
