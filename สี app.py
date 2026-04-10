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
# 0. CONFIG & STYLING
# ==========================================
st.set_page_config(page_title="SYNAPSE OS", layout="wide", initial_sidebar_state="collapsed")

def apply_custom_background():
    # ใช้สีจาก session_state ถ้าไม่มีให้ใช้สีน้ำเงินพื้นฐาน
    theme = st.session_state.get('theme_color', "#1408BF")
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(270deg, #AFEEEE, #FF7F50, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
            background-size: 1600% 1600%;
            animation: RainbowFlow 60s ease infinite;
        }}
        @keyframes RainbowFlow {{
            0%{{background-position:0% 50%}}
            50%{{background-position:100% 50%}}
            100%{{background-position:0% 50%}}
        }}
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(0, 0, 0, 0.7) !important;
            border-radius: 20px !important;
            padding: 10px !important;
            border: 2px solid {theme} !important;
            box-shadow: 0 0 15px {theme}88;
        }}
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            color: #FFFFFF !important;
            background-color: {theme}44 !important;
            border: 1px solid {theme} !important;
            box-shadow: 0 0 15px {theme} !important;
            transform: scale(1.05);
        }}
        div.stButton > button {{
            background-color: rgba(0, 0, 0, 0.8) !important;
            color: white !important;
            border: 2px solid {theme} !important;
            border-radius: 15px !important;
            filter: drop-shadow(0 0 5px {theme});
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def show_logo():
    """ฟังก์ชันแสดงโลโก้ logo1.png แบบมีไฟนีออน"""
    theme = st.session_state.get('theme_color', "#1408BF")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if os.path.exists("logo1.png"):
            with open("logo1.png", "rb") as f:
                data = base64.b64encode(f.read()).decode()
            st.markdown(f"""
                <div style="text-align:center; filter: drop-shadow(0 0 10px {theme});">
                    <img src="data:image/png;base64,{data}" style="width:100%; max-width:200px; border-radius:15px;">
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"<h1 style='text-align:center; color:{theme}; text-shadow: 0 0 10px {theme};'>SYNAPSE OS</h1>", unsafe_allow_html=True)

# ==========================================
# 1. UTILS & SYSTEM INIT
# ==========================================
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon, dlat = lon2 - lon1, lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * 6371

def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#1408BF"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    
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
        tz_str = tf.timezone_at(lat=lat, lng=lon)
        if tz_str:
            return datetime.now(pytz.timezone(tz_str))
    except: pass
    return datetime.now(pytz.timezone('Asia/Bangkok'))

# ==========================================
# 2. ROOM MODULES
# ==========================================
def room_login():
    show_logo()
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        tab_l, tab_r = st.tabs(["🔑 UNLOCK SYSTEM", "📝 REGISTER"])
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
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
    
    current_time = get_local_time(lat, lon)
    st.markdown(f"""
        <div style="text-align:center; padding:30px; border:4px solid {st.session_state.theme_color}; border-radius:15px; background:rgba(0,0,0,0.3); box-shadow: 0 0 20px {st.session_state.theme_color}44;">
            <h1 style="font-size:5em; color:{st.session_state.theme_color}; margin:0; font-family: monospace;">{current_time.strftime('%H:%M:%S')}</h1>
            <p style="color:#888;">📍 LAT: {lat:.4f} | LON: {lon:.4f}</p>
        </div>
    """, unsafe_allow_html=True)

def room_radar(loc):
    st.subheader("🛰️ STRATEGIC GPS")
    my_lat, my_lon = 13.7367, 100.5231 
    if loc and 'coords' in loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']
    
    m = folium.Map(location=[my_lat, my_lon], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr='Google')
    folium.Marker([my_lat, my_lon], icon=folium.Icon(color='red', icon='star')).add_to(m)
    
    st_folium(m, width="100%", height=300)
    if st.button("📡 BROADCAST MY LOCATION", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.toast("ส่งพิกัดสำเร็จ!")

def room_music():
    st.subheader("🎧 NON-STOP STATION")
    music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if music_files:
        current_song = music_files[st.session_state.song_index]
        st.info(f"🎵 กำลังเล่น: {current_song}")
        with open(current_song, "rb") as f:
            st.audio(f.read(), format="audio/mp3", autoplay=True)
        
        col1, col2, col3 = st.columns(3)
        if col1.button("⏮️ Back"):
            st.session_state.song_index = (st.session_state.song_index - 1) % len(music_files)
            st.rerun()
        if col3.button("⏭️ Next"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()

# ==========================================
# 3. MAIN EXECUTION
# ==========================================
def main():
    init_system()
    apply_custom_background()
    loc = get_geolocation() 

    if not st.session_state.logged_in:
        room_login()
    else:
        # แสดงโลโก้ด้านบนสุดของทุกห้องเมื่อ Login แล้ว
        show_logo()
        
        with st.sidebar:
            st.write(f"👤 AGENT: **{st.session_state.user}**")
            if st.button("🚪 LOGOUT", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()

        tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "💬 CHAT", "🎧 MUSIC", "⚙️ SETTINGS"])
        with tabs[0]: room_core(loc)
        with tabs[1]: room_radar(loc)
        with tabs[3]: room_music()
        with tabs[4]: 
            st.session_state.theme_color = st.color_picker("ปรับแต่งสีระบบ", st.session_state.theme_color)
            if st.button("บันทึกการตั้งค่า"): st.rerun()

if __name__ == "__main__":
    main()
