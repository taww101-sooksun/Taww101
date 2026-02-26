import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os
import time
import random
import string
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. CORE SYSTEM CONFIGURATION (NEON THEME)
# ==========================================
st.set_page_config(page_title="SYNAPSE QUANTUM CONTROL", layout="wide")
st_autorefresh(interval=5000, key="global_refresh")

# ตกแต่ง UI ขั้นสูงสำหรับถ่ายวิดีโอ
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #001 0%, #000 100%); color: #00f2fe; font-family: 'Courier New', Courier, monospace; }
    
    .neon-header { 
        font-size: 50px; font-weight: 900; text-align: center;
        color: #fff; text-shadow: 0 0 10px #00f2fe, 0 0 20px #ff00de;
        border: 2px solid #00f2fe; padding: 15px; background: rgba(0,0,0,0.8);
        border-radius: 15px; margin-bottom: 20px;
    }
    
    div.stButton > button {
        background: linear-gradient(135deg, #00f2fe 0%, #000 50%, #ff00de 100%);
        color: white !important; border: 1px solid #fff; border-radius: 5px;
        height: 45px; font-weight: bold; width: 100%; transition: 0.3s;
        box-shadow: 0 0 8px #00f2fe;
    }
    div.stButton > button:hover { box-shadow: 0 0 20px #ff00de; transform: translateY(-2px); }
    
    .terminal-container {
        border: 1px solid #00f2fe; padding: 20px; border-radius: 10px;
        background: rgba(0, 242, 254, 0.05); border-left: 5px solid #ff00de;
        margin-bottom: 15px;
    }
    
    .logo-img { display: block; margin-left: auto; margin-right: auto; width: 150px; border-radius: 50%; border: 2px solid #00f2fe; box-shadow: 0 0 15px #00f2fe; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FIREBASE INFRASTRUCTURE
# ==========================================
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_dict = dict(st.secrets["firebase"])
            if "private_key" in fb_dict:
                fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            creds = credentials.Certificate(fb_dict)
            firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except: pass

# ==========================================
# 3. GLOBAL LOGO DISPLAY (โชว์ทุกหน้า)
# ==========================================
def display_global_header():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if os.path.exists("logo3.jpg"):
            st.image("logo3.jpg", width=400)
        st.markdown('<div class="neon-header">S Y N A P S E</div>', unsafe_allow_html=True)

# ==========================================
# 4. SIDEBAR : LIVE STATUS
# ==========================================
with st.sidebar:
    st.markdown("### ⚡ SYSTEM STATUS")
    st.success("SATELLITE: CONNECTED")
    st.info(f"OS: SYNAPSE V2.0")
    st.warning(f"TIME: {datetime.datetime.now().strftime('%H:%M:%S')}")
    st.markdown("---")
    # เพลงประกอบ (YouTube ที่เพื่อนให้มา)
    st.markdown("### 🎵 BACKGROUND MUSIC")
    yt_id = "F3zR5W0Bv0U" # ลิงก์ยูทูปที่เพื่อนให้
    st.components.v1.html(f'<iframe width="100%" height="150" src="https://www.youtube.com/embed/{yt_id}?autoplay=1&loop=1&playlist={yt_id}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>', height=170)

# ==========================================
# 5. MAIN INTERFACE (TABS 1-7)
# ==========================================
display_global_header()
tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "📊 LOGS", "🔐 SECURITY", "📺 MEDIA", "🧹 SYSTEM"])

# --- TAB 1: CORE (IDENTIFICATION) ---
with tabs[0]:
    st.markdown('<div class="terminal-container"><h3>[ USER_LOGIN_PROTOCOL ]</h3></div>', unsafe_allow_html=True)
    st.session_state.my_name = st.text_input("ENTER CODENAME:", value=st.session_state.get('my_name', 'Agent_X'))
    if st.button("🚀 INITIATE QUANTUM LINK"):
        loc = get_geolocation()
        if loc:
            db.reference(f'users/{st.session_state.my_name}').set({
                'lat': loc['coords']['latitude'], 'lon': loc['coords']['longitude'],
                'gps_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'status': 'ACTIVE'
            })
            st.success("GPS LINK ESTABLISHED.")

# --- TAB 2: RADAR (GPS MAP) ---
with tabs[1]:
    st.markdown('<div class="terminal-container"><h3>[ GLOBAL_SURVEILLANCE ]</h3></div>', unsafe_allow_html=True)
    users = db.reference('users').get()
    if users:
        m = folium.Map(location=[13.75, 100.5], zoom_start=2, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
        for name, info in users.items():
            if isinstance(info, dict) and 'lat' in info:
                folium.Marker([info['lat'], info['lon']], popup=name, icon=folium.Icon(color='red')).add_to(m)
        st_folium(m, width="100%", height=500)

# --- TAB 3: COMMS (VIDEO & CHAT) ---
with tabs[2]:
    st.markdown('<div class="terminal-container"><h3>[ ENCRYPTED_COMM_LINK ]</h3></div>', unsafe_allow_html=True)
    webrtc_streamer(key="call", mode=WebRtcMode.SENDRECV, rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
    st.markdown("---")
    chat_input = st.chat_input("TRANSMIT DATA...")
    if chat_input:
        db.reference('global_chat').push({'user': st.session_state.my_name, 'msg': chat_input, 'ts': time.time()})
    
    msgs = db.reference('global_chat').order_by_child('ts').limit_to_last(10).get()
    if msgs:
        for m in msgs.values():
            st.markdown(f"**{m['user']}**: {m['msg']}")

# --- TAB 4: DATA LOG ---
with tabs[3]:
    st.markdown('<div class="terminal-container"><h3>[ DATABASE_RAW_DUMP ]</h3></div>', unsafe_allow_html=True)
    if users: st.json(users)
    if st.button("🗑️ PURGE ACCESS LOGS"):
        db.reference('users').delete()
        st.rerun()

# --- TAB 5: SECURITY (PASSWORD GEN) ---
with tabs[4]:
    st.markdown('<div class="terminal-container"><h3>[ QUANTUM_KEY_GENERATOR ]</h3></div>', unsafe_allow_html=True)
    length = st.slider("KEY LENGTH", 8, 32, 16)
    if st.button("🔑 GENERATE SECURE KEY"):
        new_key = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=length))
        st.code(new_key, language="text")
        st.info("รหัสผ่านนี้ถูกสร้างขึ้นแบบสุ่มและไม่ถูกบันทึกลงฐานข้อมูล")

# --- TAB 6: MEDIA (YOUTUBE PROMO) ---
with tabs[5]:
    st.markdown('<div class="terminal-container"><h3>[ SATELLITE_BROADCAST ]</h3></div>', unsafe_allow_html=True)
    # แสดงวิดีโอที่เพื่อนส่งมาเป็นหน้าหลัก
    st.video(f"https://www.youtube.com/watch?v={yt_id}")
    st.write("📢 กำลังเล่นเพลงร็อกเสียงสูง (Non-Hardcore) ที่ร้อยเรียงมาจากความจริง")

# --- TAB 7: SYSTEM (WIPE) ---
with tabs[6]:
    st.markdown('<div class="terminal-container"><h3>[ SYSTEM_DESTRUCTION ]</h3></div>', unsafe_allow_html=True)
    if st.button("💣 WIPE ALL SYSTEM DATA"):
        db.reference('/').delete()
        st.error("DATABASE CLEARED.")
