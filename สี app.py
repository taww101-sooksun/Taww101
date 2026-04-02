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
    # ตั้งค่าตัวแปรเริ่มต้นใน Session
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'user' not in st.session_state: st.session_state.user = "Guest"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
        
    # เชื่อมต่อ Firebase (ใช้ Secrets จาก Streamlit)
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ Firebase Connection Error: {e}")

# ==========================================
# 1. ระบบ Login (Security)
# ==========================================

def room_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("logo1.jpg", use_container_width=True)
        except:
            st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color};'>SYNAPSE</h1>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align:center;'>🔐 รหัสผ่านเข้าถึงระบบ</h3>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 LOGIN", "📝 REGISTER"])
    
    with tab1:
        with st.form("login_form"):
            u_id = st.text_input("AGENT ID")
            u_pw = st.text_input("PASSWORD", type="password")
            if st.form_submit_button("UNLOCK", use_container_width=True):
                user_data = db.reference(f'users/{u_id}').get()
                if user_data and user_data.get('pw') == u_pw:
                    st.session_state.user = u_id
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("ข้อมูลไม่ถูกต้อง")

    with tab2:
        with st.form("reg_form"):
            new_id = st.text_input("ตั้งชื่อ AGENT ID")
            new_pw = st.text_input("ตั้งรหัสผ่าน")
            if st.form_submit_button("สร้างบัญชี", use_container_width=True):
                if new_id and new_pw:
                    db.reference(f'users/{new_id}').set({'pw': new_pw, 'ts': time.time()})
                    st.success("ลงทะเบียนสำเร็จ!")

# ==========================================
# 2. ห้องควบคุมและฟังก์ชันต่างๆ
# ==========================================

def room_core():
    now = datetime.utcnow() + timedelta(hours=7)
    st.markdown(f"""
        <div style="border: 2px solid {st.session_state.theme_color}; padding: 30px; border-radius: 15px; text-align: center; background: rgba(0,0,0,0.5);">
            <h1 style="color: {st.session_state.theme_color}; font-size: 4em; margin:0;">{now.strftime('%H:%M:%S')}</h1>
            <p style="letter-spacing: 10px; color: {st.session_state.theme_color};">SYSTEM OPERATIONAL</p>
            <hr style="border: 1px solid {st.session_state.theme_color}; opacity: 0.3;">
            <p>AGENT: {st.session_state.user} | STATUS: ONLINE</p>
        </div>
    """, unsafe_allow_html=True)

def room_radar():
    st.subheader("🛰️ ระบบเรดาร์ผ่านดาวเทียม")
    loc = get_geolocation()
    my_lat, my_lon = (loc['coords']['latitude'], loc['coords']['longitude']) if loc else (13.7367, 100.5231)
    
    m = folium.Map(location=[my_lat, my_lon], zoom_start=18, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr='Google Hybrid')
    folium.Marker([my_lat, my_lon], icon=folium.Icon(color='red', icon='user', prefix='fa')).add_to(m)
    
    # ดึงพิกัดเพื่อน
    try:
        users = db.reference('users').get()
        if users:
            for uid, data in users.items():
                if uid != st.session_state.user and data.get('lat'):
                    u_lat, u_lon = data['lat'], data['lon']
                    dist = haversine(my_lat, my_lon, u_lat, u_lon)
                    folium.Marker([u_lat, u_lon], icon=folium.Icon(color='green')).add_to(m)
                    folium.Marker([u_lat-0.0001, u_lon], icon=DivIcon(html=f'<b style="color:lime; background:black; padding:2px;">{uid} ({dist:.2f}km)</b>')).add_to(m)
    except: pass

    st_folium(m, width="100%", height=500)
    if st.button("📡 อัปเดตตำแหน่งลงเครือข่าย", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.toast("ส่งพิกัดสำเร็จ!")

def room_public():
    st.subheader("🌐 เครือข่ายแชตรวม")
    with st.form("chat_form", clear_on_submit=True):
        msg = st.text_input("ข้อความ...")
        if st.form_submit_button("ส่งสัญญาณ"):
            if msg:
                db.reference('public_chat').push({'u': st.session_state.user, 'm': msg, 'ts': time.time()})
                st.rerun()

    data = db.reference('public_chat').order_by_key().limit_to_last(15).get()
    if data:
        for v in reversed(list(data.values())):
            st.markdown(f"**{v['u']}**: {v['m']}")
            st.write("---")

def room_music():
    st.subheader("🎧 Music Station")
    music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if music_files:
        song = music_files[st.session_state.song_index]
        st.info(f"เล่นอยู่: {song}")
        with open(song, "rb") as f:
            st.audio(f.read())
        if st.button("⏭️ เพลงถัดไป"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()
    else:
        st.warning("ไม่พบไฟล์ .mp3 ในเครื่อง")

def room_bio():
    st.subheader("🩺 Bio Sensor")
    st.caption("วางนิ้วชี้ทับเลนส์กล้องและไฟแฟลชเพื่อเริ่มการตรวจวัด")
    bio_html = f"""
    <div style="background:black; color:lime; padding:20px; border:2px solid lime; border-radius:10px; text-align:center; font-family:monospace;">
        <h2 id="bpm">0</h2><p>BPM</p>
        <hr>
        <p id="st">READY</p>
    </div>
    <script>
        // จำลองการอ่านค่า (สามารถใส่ Logic เดิมของต๊ะได้ที่นี่)
        setInterval(() => {{
            document.getElementById('bpm').innerText = Math.floor(70 + Math.random()*10);
        }}, 2000);
    </script>
    """
    components.html(bio_html, height=200)

# ==========================================
# 3. Main Execution
# ==========================================

def main():
    st.set_page_config(page_title="SYNAPSE OS", layout="wide")
    init_system()
    
    if not st.session_state.logged_in:
        room_login()
    else:
        with st.sidebar:
            st.title("⚙️ SETTINGS")
            st.write(f"AGENT: **{st.session_state.user}**")
            if st.button("🚪 LOGOUT"):
                st.session_state.logged_in = False
                st.rerun()

        tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "🌐 PUBLIC", "🎧 MUSIC", "🩺 BIO"])
        
        with tabs[0]: room_core()
        with tabs[1]: room_radar()
        with tabs[2]: room_public()
        with tabs[3]: room_music()
        with tabs[4]: room_bio()

if __name__ == "__main__":
    main()
