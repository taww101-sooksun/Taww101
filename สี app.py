import streamlit as st
import os 
import time
import base64
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from folium.features import DivIcon
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from math import radians, cos, sin, asin, sqrt

# ==========================================
# 0. CONFIG & INITIALIZATION
# ==========================================
st.set_page_config(page_title="SYNAPSE OS", layout="wide", initial_sidebar_state="collapsed")

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon, dlat = lon2 - lon1, lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * 6371

def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ ระบบเชื่อมต่อฐานข้อมูลขัดข้อง: {e}")

# ==========================================
# 1. AUTHENTICATION (LOGIN/REGISTER)
# ==========================================
def room_login():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        if os.path.exists("logo1.jpg"):
            st.image("logo1.jpg", use_container_width=True)
        else:
            st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color};'>SYNAPSE</h1>", unsafe_allow_html=True)
        
        tab_l, tab_r = st.tabs(["🔑 UNLOCK SYSTEM", "📝 REGISTER AGENT"])
        
        with tab_l:
            with st.form("login"):
                uid = st.text_input("AGENT ID")
                pw = st.text_input("PASSWORD", type="password")
                if st.form_submit_button("ACCESS GRANTED", use_container_width=True):
                    user_data = db.reference(f'users/{uid}').get()
                    if user_data and user_data.get('pw') == pw:
                        st.session_state.user = uid
                        st.session_state.logged_in = True
                        st.rerun()
                    else: st.error("รหัสผ่านไม่ถูกต้อง")
        
        with tab_r:
            with st.form("reg"):
                new_id = st.text_input("NEW AGENT ID")
                new_pw = st.text_input("SET PASSWORD", type="password")
                if st.form_submit_button("CREATE ACCOUNT", use_container_width=True):
                    db.reference(f'users/{new_id}').set({'pw': new_pw, 'ts': time.time()})
                    st.success("ลงทะเบียนสำเร็จ!")

# ==========================================
# 2. CORE MODULES (RADAR, COMMS, MUSIC)
# ==========================================
def room_radar():
    st.subheader("🛰️ STRATEGIC RADAR (HYBRID SATELLITE)")
    
    # --- แก้ไขจุดนี้: ตรวจสอบโครงสร้างข้อมูล loc อย่างละเอียด ---
    loc = get_geolocation()
    
    # ตั้งค่าพิกัดเริ่มต้น (กรุงเทพฯ)
    my_lat, my_lon = 13.7367, 100.5231 
    
    # เช็คว่า loc มีข้อมูลจริง และมี Key 'coords' อยู่ข้างในไหม
    if loc and 'coords' in loc:
        try:
            my_lat = loc['coords'].get('latitude', 13.7367)
            my_lon = loc['coords'].get('longitude', 100.5231)
        except (KeyError, TypeError):
            st.warning("⚠️ สัญญาณ GPS อ่อน กำลังใช้พิกัดสำรอง...")
    else:
        st.caption("📡 กำลังรอสัญญาณจากดาวเทียม (กรุณากด 'Allow' ในเบราว์เซอร์)...")

    # --- ส่วนที่เหลือของแผนที่เหมือนเดิม ---
    m = folium.Map(
        location=[my_lat, my_lon], 
        zoom_start=18, 
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
        attr='Google'
    )
    
    # Marker ตัวเรา
    folium.Marker([my_lat, my_lon], icon=folium.Icon(color='red', icon='star')).add_to(m)
    folium.Marker(
        [my_lat-0.0001, my_lon], 
        icon=DivIcon(html=f'<div style="font-size:10pt; color:red; font-weight:bold; background:white; padding:2px; border-radius:3px;">📍 {st.session_state.user} (YOU)</div>')
    ).add_to(m)

    # ดึงข้อมูลเพื่อน (Team Radar)
    try:
        users_ref = db.reference('users').get()
        if users_ref:
            for uid, data in users_ref.items():
                if uid != st.session_state.user and 'lat' in data and 'lon' in data:
                    u_lat, u_lon = data['lat'], data['lon']
                    dist = haversine(my_lat, my_lon, u_lat, u_lon)
                    folium.Marker([u_lat, u_lon], icon=folium.Icon(color='green')).add_to(m)
                    folium.Marker(
                        [u_lat-0.0001, u_lon], 
                        icon=DivIcon(html=f'<div style="font-size:8pt; color:green; font-weight:bold; background:white; padding:2px;">👤 {uid} ({dist:.2f}km)</div>')
                    ).add_to(m)
                    folium.PolyLine([[my_lat, my_lon], [u_lat, u_lon]], color=st.session_state.theme_color, weight=1, dash_array='5').add_to(m)
    except:
        pass

    st_folium(m, width="100%", height=500)
    
    if st.button("📡 BROADCAST MY LOCATION", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({
            'lat': my_lat, 
            'lon': my_lon, 
            'ts': time.time()
        })
        st.toast("พิกัดถูกส่งเข้าศูนย์บัญชาการแล้ว")


def room_music():
    st.subheader("🎧 NON-STOP STATION")
    music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if not music_files: return st.warning("ไม่พบไฟล์เพลง")
    
    current = music_files[st.session_state.song_index]
    with open(current, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode()
    
    st.info(f"🎵 NOW PLAYING: {current}")
    
    # JS สำหรับ Auto-Next
    audio_html = f"""
        <audio id="player" controls autoplay style="width:100%;">
            <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
        </audio>
        <script>
            document.getElementById('player').onended = function() {{
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'next'}}, '*');
            }};
        </script>
    """
    res = components.html(audio_html, height=100)
    
    col1, col2, col3 = st.columns(3)
    if col1.button("⏮️ PREV") or res == 'prev':
        st.session_state.song_index = (st.session_state.song_index - 1) % len(music_files)
        st.rerun()
    if col3.button("⏭️ NEXT") or res == 'next':
        st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
        st.rerun()

def room_secure_chat():
    st.subheader("🔐 SECURE MEDIA CHAT")
    users = db.reference('users').get()
    target = st.selectbox("🎯 TARGET AGENT:", [u for u in users.keys() if u != st.session_state.user])
    
    if target:
        rid = "_".join(sorted([st.session_state.user, target]))
        with st.form("chat_form", clear_on_submit=True):
            msg = st.text_input("MESSAGE")
            up = st.file_uploader("UPLOAD MEDIA", type=['jpg', 'png', 'mp4'])
            if st.form_submit_button("SEND"):
                f_data, f_type = (base64.b64encode(up.read()).decode(), up.type) if up else (None, None)
                db.reference(f'private_rooms/{rid}').push({'u': st.session_state.user, 'm': msg, 'f': f_data, 'ft': f_type, 'ts': time.time()})
                st.rerun()

        chats = db.reference(f'private_rooms/{rid}').order_by_key().limit_to_last(10).get()
        if chats:
            for c in reversed(list(chats.values())):
                align = "right" if c['u'] == st.session_state.user else "left"
                color = st.session_state.theme_color if c['u'] == st.session_state.user else "#333"
                st.markdown(f'<div style="text-align:{align};"><div style="display:inline-block; background:{color}; padding:10px; border-radius:10px;"><b>{c["u"]}</b>: {c["m"]}</div></div>', unsafe_allow_html=True)
                if c.get('f'):
                    dec = base64.b64decode(c['f'])
                    if "image" in c['ft']: st.image(dec)
                    else: st.video(dec)

# ==========================================
# 3. MAIN INTERFACE
# ==========================================
def main():
    init_system()
    
    # 1. แสดงโลโก้ที่ Sidebar (เพื่อให้เห็นทุกห้อง)
    with st.sidebar:
        if os.path.exists("logo1.jpg"):
            st.image("logo1.jpg", use_container_width=True)
        else:
            st.markdown(f"<h2 style='text-align:center; color:{st.session_state.theme_color};'>SYNAPSE OS</h2>", unsafe_allow_html=True)
        
        st.markdown("---") # เส้นคั่นเท่ๆ
        
        if st.session_state.logged_in:
            st.write(f"👤 AGENT: **{st.session_state.user}**")
            st.caption(f"'{st.session_state.user}' - อยู่นิ่งๆ ไม่เจ็บตัว")
            if st.button("🚪 LOGOUT", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()

    # 2. ตรวจสอบการ Login
    if not st.session_state.logged_in:
        room_login()
        return

    # 3. ถ้า Login แล้ว ให้แสดง Tabs ปกติ
    tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "💬 SECURE CHAT", "🎧 MUSIC", "⚙️ SETTINGS"])
    
    with tabs[0]:
        # ในห้อง Core อาจจะใส่โลโก้ใหญ่ๆ อีกทีก็ได้ถ้าชอบ
        now = datetime.now()
        st.markdown(f"<h1 style='text-align:center; font-size:4em; color:{st.session_state.theme_color};'>{now.strftime('%H:%M:%S')}</h1>", unsafe_allow_html=True)
        st.info(f"WELCOME BACK, AGENT {st.session_state.user}. ALL SYSTEMS NOMINAL.")
        
    with tabs[1]: room_radar()
    with tabs[2]: room_secure_chat()
    with tabs[3]: room_music()
    with tabs[4]: 
        st.session_state.theme_color = st.color_picker("ปรับสีธีมระบบ", st.session_state.theme_color)
