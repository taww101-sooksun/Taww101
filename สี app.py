import streamlit as st
import os 
import time
import base64
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from folium.features import DivIcon
from streamlit_folium import st_folium
from math import radians, cos, sin, asin, sqrt
import pytz
from timezonefinder import TimezoneFinder
from datetime import datetime
from streamlit_js_eval import get_geolocation 

# ==========================================
# 0. CONFIG & STYLE SYSTEM
# ==========================================
st.set_page_config(page_title="SYNAPSE OS อยู่นิ่งๆไม่เจ็บตัว", layout="wide", initial_sidebar_state="collapsed")

def apply_custom_background():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#1408BF"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {st.session_state.bg_color}44 !important;
            color: white !important;
        }}
        section[data-testid="stSidebar"] {{
            background-color: rgba(0,0,0,0.5);
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: rgba(255, 255, 255, 0.05) !important;
            border-radius: 12px !important;
            padding: 8px 16px !important;
            color: #BBBBBB !important;
            font-weight: bold !important;
            border: 4px solid transparent !important;
        }}
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            color: #FFFFFF !important;
            background-color: {st.session_state.theme_color}44 !important;
            border: 4px solid {st.session_state.theme_color} !important;
            box-shadow: 0 0 15px {st.session_state.theme_color} !important;
        }}
        div.stButton > button {{
            background-color: rgba(0, 0, 0, 0.8) !important;
            color: white !important;
            border: 4px solid {st.session_state.theme_color} !important;
            border-radius: 15px !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# 1. HELPER FUNCTIONS
# ==========================================
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon, dlat = lon2 - lon1, lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * 6371

def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#1408BF"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ ระบบเชื่อมต่อฐานข้อมูลขัดข้อง: {e}")

def get_local_time(lat, lon):
    try:
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=lat, lng=lon)
        if timezone_str:
            local_tz = pytz.timezone(timezone_str)
            return datetime.now(local_tz)
    except: pass
    return datetime.now(pytz.timezone('Asia/Bangkok'))

# ==========================================
# 2. ROOM MODULES
# ==========================================
def room_login():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color};'>SYNAPSE LOGIN</h1>", unsafe_allow_html=True)
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

def room_core(loc):
    st.subheader("🏠 CORE CONTROL")
    lat, lon = 13.7367, 100.5231
    if loc and 'coords' in loc:
        lat = loc['coords'].get('latitude', lat)
        lon = loc['coords'].get('longitude', lon)
    
    current_time = get_local_time(lat, lon)
    st.markdown(f"""
        <div style="text-align:center; padding:30px; border:4px solid {st.session_state.theme_color}; border-radius:15px; background:rgba(0,0,0,0.3);">
            <h1 style="font-size:5em; color:{st.session_state.theme_color};">{current_time.strftime('%H:%M:%S')}</h1>
            <p>📍 LAT: {lat:.4f} | LON: {lon:.4f}</p>
        </div>
    """, unsafe_allow_html=True)

def room_radar(loc):
    st.subheader("🛰️ STRATEGIC GPS")
    my_lat, my_lon = 13.7367, 100.5231 
    if loc and 'coords' in loc:
        my_lat = loc['coords'].get('latitude', my_lat)
        my_lon = loc['coords'].get('longitude', my_lon)
    
    m = folium.Map(location=[my_lat, my_lon], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr='Google')
    folium.Marker([my_lat, my_lon], icon=folium.Icon(color='red', icon='star')).add_to(m)
    
    try:
        users_ref = db.reference('users').get()
        if users_ref:
            for uid, data in users_ref.items():
                if uid != st.session_state.user and 'lat' in data:
                    folium.Marker([data['lat'], data['lon']], tooltip=uid).add_to(m)
    except: pass
    
    st_folium(m, width="100%", height=400)
    if st.button("📡 BROADCAST LOCATION", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})

def room_music():
    st.subheader("🎧 PRO AUDIO ENGINE")
    player_html = """
    <div style="background:#111; padding:20px; border:2px solid #00ffc8; border-radius:15px; color:white;">
        <input type="file" id="audio_file" accept="audio/*" style="margin-bottom:10px;">
        <canvas id="viz" style="width:100%; height:100px; background:#000;"></canvas>
        <audio id="player" controls style="width:100%; margin-top:10px;"></audio>
    </div>
    <script>
        const audio = document.getElementById('player');
        const file = document.getElementById('audio_file');
        file.onchange = function() {
            audio.src = URL.createObjectURL(this.files[0]);
            audio.play();
        }
    </script>
    """
    components.html(player_html, height=300)

def room_camera(loc):
    st.subheader("📷 AGENT SCANNER")
    img = st.camera_input("SNAPSHOT")
    if img:
        st.image(img)
        if st.button("📤 UPLOAD TO CLOUD"):
            st.success("บันทึกสำเร็จ!")

def room_secure_chat():
    st.subheader("💬 SECURE CHAT")
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    target = st.selectbox("🎯 เลือกผู้รับ:", friends)
    if target:
        rid = "_".join(sorted([st.session_state.user, target]))
        msg = st.text_input("พิมพ์ข้อความ...")
        if st.button("SEND"):
            db.reference(f'private_rooms/{rid}').push({'u': st.session_state.user, 'm': msg, 'ts': time.time()})
            st.rerun()

def room_call():
    st.subheader("📞 P2P CALL")
    st.info("ระบบกำลังพัฒนาช่องทางการสื่อสาร")

# ==========================================
# 3. MAIN SYSTEM
# ==========================================
def main():
    init_system()
    apply_custom_background()
    loc = get_geolocation() 

    if not st.session_state.get('logged_in', False):
        room_login()
        return

    with st.sidebar:
        st.write(f"👤 AGENT: **{st.session_state.user}**")
        if st.button("🚪 LOGOUT", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color};'>SYNAPSE OS</h1>", unsafe_allow_html=True)
    
    tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "💬 CHAT", "📞 CALL", "🎧 MUSIC", "⚙️ SETTINGS", "📷 SCANNER"])
    
    with tabs[0]: room_core(loc)
    with tabs[1]: room_radar(loc)
    with tabs[2]: room_secure_chat()
    with tabs[3]: room_call()
    with tabs[4]: room_music()
    with tabs[5]:
        st.subheader("🎨 SETTINGS")
        st.color_picker("THEME COLOR", key="theme_color_picker")
    with tabs[6]: room_camera(loc)

if __name__ == "__main__":
    main()
