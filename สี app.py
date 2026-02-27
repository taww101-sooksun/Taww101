import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import pytz
import os
import time
import pandas as pd
import random
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. SETUP & THEME
# ==========================================
st.set_page_config(page_title="SYNAPSE QUANTUM CONTROL", layout="wide")
st_autorefresh(interval=5000, key="global_refresh")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #001 0%, #000 100%); color: #00f2fe; font-family: 'Courier New', Courier, monospace; }
    .neon-header { 
        font-size: 50px; font-weight: 900; text-align: center;
        color: #fff; text-shadow: 0 0 10px #00f2fe, 0 0 20px #ff00de;
        border: 4px double #00f2fe; padding: 15px; background: rgba(0,0,0,0.8);
        border-radius: 20px; margin-bottom: 20px;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #00f2fe 0%, #000 50%, #ff00de 100%);
        color: white !important; border: 1px solid #fff; border-radius: 5px;
        height: 45px; font-weight: bold; width: 100%; transition: 0.5s;
    }
    .bubble-me { background: rgba(0, 242, 254, 0.2); border: 1px solid #00f2fe; padding: 10px; border-radius: 15px 15px 0 15px; margin-bottom: 10px; }
    .bubble-others { background: rgba(255, 71, 71, 0.2); border: 1px solid #ff4747; padding: 10px; border-radius: 15px 15px 15px 0; margin-bottom: 10px; }
    .terminal-container { border: 1px solid #00f2fe; padding: 15px; border-radius: 10px; background: rgba(0, 242, 254, 0.05); border-left: 8px solid #00f2fe; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. AUDIO (รอลิ้งก์ใหม่จากเพื่อน)
# ==========================================
# ใส่ลิ้งก์ที่เพื่อนต้องการตรงนี้ได้เลย
NEW_DIRECT_LINK = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a" 

st.components.v1.html(f"""
    <audio id="synapse-audio" loop autoplay><source src="{NEW_DIRECT_LINK}" type="audio/mpeg"></audio>
    <script>var audio = document.getElementById("synapse-audio"); window.parent.document.addEventListener('click', function() {{ audio.play(); }}, {{ once: true }});</script>
""", height=0)

# ==========================================
# 3. FIREBASE INITIALIZATION
# ==========================================
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_dict = dict(st.secrets["firebase"])
            if "private_key" in fb_dict: fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            creds = credentials.Certificate(fb_dict)
            firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except Exception as e: st.error(f"SYSTEM_ERROR: {e}")

# ==========================================
# 4. SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>CONTROL CENTER</h2>", unsafe_allow_html=True)
    if os.path.exists("logo3.jpg"): st.image("logo3.jpg", use_container_width=True)
    st.markdown("---")
    st.audio(NEW_DIRECT_LINK, format="audio/mpeg", loop=True)
    st.write(f"UPTIME: {datetime.datetime.now().strftime('%H:%M:%S')}")

# ==========================================
# 5. MAIN INTERFACE
# ==========================================
st.markdown('<div class="neon-header">S Y N A P S E _ O V E R L O R D</div>', unsafe_allow_html=True)

tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 PUBLIC", "🔒 PRIVATE", "📊 LOG", "🔐 SEC", "🧹 SYS"])

# --- TAB 1: CORE (IDENTIFICATION) ---
with tabs[0]:
    st.markdown('<div class="terminal-container"><h3>[ USER_SYNC ]</h3></div>', unsafe_allow_html=True)
    my_name = st.text_input("ระบุชื่อรหัสของคุณ:", value=st.session_state.get('my_name', 'Guest'))
    st.session_state.my_name = my_name
    if st.button("🚀 INITIATE LINK"):
        loc = get_geolocation()
        if loc:
            db.reference(f'users/{my_name}').set({
                'lat': loc['coords']['latitude'], 'lon': loc['coords']['longitude'],
                'status': 'ONLINE', 'ts': time.time()
            })
            st.success("SYNCHRONIZED.")

# --- TAB 2: RADAR (มุดระบุตัวตน) ---
with tabs[1]:
    st.markdown('<div class="terminal-container"><h3>[ RADAR_MAP ]</h3></div>', unsafe_allow_html=True)
    users = db.reference('users').get()
    m = folium.Map(location=[13.75, 100.5], zoom_start=3, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google")
    if users:
        for name, info in users.items():
            if isinstance(info, dict) and 'lat' in info:
                # แยกสี: เราสีฟ้า คนอื่นสีแดง และใส่ชื่อที่มุด
                f_color = 'cadetblue' if name == st.session_state.my_name else 'red'
                folium.Marker(
                    [info['lat'], info['lon']], 
                    tooltip=f"Agent: {name}",
                    popup=f"Status: {info.get('status')}",
                    icon=folium.Icon(color=f_color, icon='user', prefix='fa')
                ).add_to(m)
    st_folium(m, width="100%", height=500)

# --- TAB 3: PUBLIC CHAT (ห้องสาธารณะ) ---
with tabs[2]:
    st.markdown('<div class="terminal-container"><h3>[ GLOBAL_COMMUNICATION ]</h3></div>', unsafe_allow_html=True)
    pub_input = st.chat_input("คุยในห้องสาธารณะ...")
    if pub_input:
        db.reference('global_chat').push({'name': st.session_state.my_name, 'msg': pub_input, 'ts': time.time()})
    
    msgs = db.reference('global_chat').order_by_child('ts').limit_to_last(15).get()
    if msgs:
        for d in msgs.values():
            align = "right" if d['name'] == st.session_state.my_name else "left"
            style = "bubble-me" if d['name'] == st.session_state.my_name else "bubble-others"
            st.markdown(f"<div style='text-align:{align};'><div class='{style}' style='display:inline-block;'><small>{d['name']}</small><br>{d['msg']}</div></div>", unsafe_allow_html=True)

# --- TAB 4: PRIVATE CHAT (ระบบเพิ่มเพื่อน/แยกคุย) ---
with tabs[3]:
    st.markdown('<div class="terminal-container"><h3>[ PRIVATE_CHANNELS ]</h3></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.write("👥 รายชื่อ Agent")
        if users:
            for other_user in users.keys():
                if other_user != st.session_state.my_name:
                    if st.button(f"คุยกับ {other_user}", key=f"p-{other_user}"):
                        # สร้าง ID ห้องแชทเฉพาะ 2 คน
                        pair = sorted([st.session_state.my_name, other_user])
                        st.session_state.current_private = f"priv_{pair[0]}_{pair[1]}"
                        st.session_state.talking_to = other_user
                        st.rerun()
    with col2:
        room = st.session_state.get('current_private')
        if room:
            st.write(f"🔒 แชทส่วนตัวกับ: **{st.session_state.talking_to}**")
            p_input = st.chat_input("ส่งข้อความส่วนตัว...", key="p_input")
            if p_input:
                db.reference(f'private_rooms/{room}').push({'name': st.session_state.my_name, 'msg': p_input, 'ts': time.time()})
            
            p_msgs = db.reference(f'private_rooms/{room}').order_by_child('ts').limit_to_last(10).get()
            if p_msgs:
                for d in p_msgs.values():
                    align = "right" if d['name'] == st.session_state.my_name else "left"
                    st.markdown(f"<div style='text-align:{align};'><div class='bubble-me' style='display:inline-block; border-color:#ff00de;'><small>{d['name']}</small><br>{d['msg']}</div></div>", unsafe_allow_html=True)
        else:
            st.info("เลือกชื่อ Agent ทางซ้ายเพื่อเริ่มการสนทนาส่วนตัว")

# --- TAB 7: SYSTEM ---
with tabs[6]:
    if st.button("💣 RESET GLOBAL CHAT"): db.reference('global_chat').delete(); st.rerun()
    if st.button("🧼 RESET ALL DATA"): db.reference('/').delete(); st.error("DATABASE WIPED")
