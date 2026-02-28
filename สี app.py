import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os
import time
import pandas as pd
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. CORE SYSTEM CONFIGURATION (ULTRA NEON)
# ==========================================
st.set_page_config(page_title="SYNAPSE QUANTUM CONTROL", layout="wide")
st_autorefresh(interval=5000, key="global_refresh")

# ปรับปรุง UI ให้ใกล้เคียงคลิป: เน้นแสงกระจาย (Blur Glow) และพื้นหลังมืดสนิท
st.markdown("""
    <style>
    /* พื้นหลังดำสนิทแบบ OLED */
    .stApp { 
        background-color: #000000;
        background-image: radial-gradient(circle at 50% 50%, #050505 0%, #000000 100%);
        color: #00f2fe; 
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* หัวข้อหลัก: แสงนีออนฟุ้งๆ แบบในคลิป */
    .neon-header { 
        font-size: clamp(30px, 5vw, 60px); font-weight: 800; text-align: center;
        color: #fff; 
        text-shadow: 0 0 10px #ff1744, 0 0 20px #ff1744, 0 0 40px #ff1744;
        border: 2px solid #ff1744; padding: 25px; 
        background: rgba(20, 0, 0, 0.6);
        border-radius: 15px; margin-bottom: 40px;
        box-shadow: 0 0 15px rgba(255, 23, 68, 0.4), inset 0 0 15px rgba(255, 23, 68, 0.2);
    }
    
    /* ปุ่มกด: สไตล์ Cyberpunk Button */
    div.stButton > button {
        background: transparent;
        color: #ff1744 !important; 
        border: 2px solid #ff1744; 
        border-radius: 4px;
        height: 55px; font-weight: bold; width: 100%; 
        transition: all 0.4s ease;
        text-transform: uppercase;
        letter-spacing: 4px;
        box-shadow: 0 0 10px rgba(255, 23, 68, 0.2);
    }
    div.stButton > button:hover {
        background: #ff1744;
        color: white !important;
        box-shadow: 0 0 30px #ff1744;
        transform: translateY(-3px);
    }
    div.stButton > button:active { transform: scale(0.98); }
    
    /* กล่องข้อความแชท: เน้นขอบเรืองแสง */
    .bubble-me { 
        background: rgba(0, 242, 254, 0.05); 
        border: 1px solid #00f2fe; 
        padding: 15px; border-radius: 20px 20px 0 20px; 
        margin-bottom: 12px; color: #fff;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.2);
    }
    .bubble-others { 
        background: rgba(255, 23, 68, 0.05); 
        border: 1px solid #ff1744; 
        padding: 15px; border-radius: 20px 20px 20px 0; 
        margin-bottom: 12px; color: #fff;
        box-shadow: 0 0 10px rgba(255, 23, 68, 0.2);
    }
    
    /* กรอบ Terminal: สไตล์ Glassmorphism */
    .terminal-container {
        border: 1px solid rgba(255, 255, 255, 0.1); 
        padding: 25px; border-radius: 15px;
        background: rgba(255, 255, 255, 0.03); 
        backdrop-filter: blur(10px);
        border-left: 5px solid #00f2fe;
    }

    /* Tab Decoration */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 5px 5px 0 0;
        color: #fff;
    }
    </style>
    """, unsafe_allow_html=True)
# ==========================================
col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    if os.path.exists("logo3.jpg"):
        st.image("logo3.jpg", width=400)
    st.markdown('<div class="neon-header">SYNAPSE</div>', unsafe_allow_html=True)

st.markdown("### 🌐 GLOBAL REAL-TIME MONITOR")
c1, c2, c3, c4 = st.columns(4)
zones = {'BANGKOK': 'Asia/Bangkok', 'NEW YORK': 'America/New_York', 'LONDON': 'Europe/London', 'TOKYO': 'Asia/Tokyo'}
for col, (city, zone) in zip([c1, c2, c3, c4], zones.items()):
    now = datetime.datetime.now(pytz.timezone(zone)).strftime('%H:%M:%S')
    col.markdown(f"<div class='clock-box'><small>{city}</small><br><span class='clock-time'>{now}</span></div>", unsafe_allow_html=True)

# ==========================================
# 2. AUDIO & FIREBASE (โครงสร้างเดิม)
# ==========================================
direct_link = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"

st.components.v1.html(f"""
    <audio id="synapse-audio" loop autoplay style="display:none;"><source src="{direct_link}" type="audio/mpeg"></audio>
    <script>
        var audio = document.getElementById("synapse-audio");
        window.parent.document.addEventListener('click', function() {{ audio.play(); }}, {{ once: true }});
    </script>
""", height=0)

if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_dict = dict(st.secrets["firebase"])
            if "private_key" in fb_dict: fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            creds = credentials.Certificate(fb_dict)
            firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except Exception as e: st.error(f"SYSTEM_ERROR: {e}")

# ==========================================
# 4. SIDEBAR : CONTROL CENTER
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#ff1744;'>CENTRAL UNIT</h2>", unsafe_allow_html=True)
    if os.path.exists("logo3.jpg"): st.image("logo3.jpg", use_container_width=True)
    st.markdown("---")
    st.audio(direct_link, format="audio/mpeg", loop=True)
    if st.button("📡 SCAN NETWORK"): st.toast("SCANNING...")
    st.write(f"SYSTEM UPTIME: {datetime.datetime.now().strftime('%H:%M:%S')}")

# ==========================================
# 5. MAIN INTERFACE
# ==========================================
st.markdown('<div class="neon-header">S Y N A P S E _ O V E R L O R D</div>', unsafe_allow_html=True)
tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "📊 LOG", "🔐 SEC", "📺 MEDIA", "🧹 SYS"])

# --- TAB 1: CORE ---
with tabs[0]:
    st.markdown('<div class="terminal-container"><h3>[ USER_SYNC ]</h3></div>', unsafe_allow_html=True)
    my_name = st.text_input("ระบุชื่อรหัสของคุณ:", value=st.session_state.get('my_name', 'Agent_01'))
    st.session_state.my_name = my_name
    if st.button("🚀 INITIATE LINK"):
        loc = get_geolocation()
        if loc:
            raw_time = loc.get('timestamp', datetime.datetime.now().timestamp())
            local_time = datetime.datetime.fromtimestamp(raw_time/1000).strftime('%Y-%m-%d %H:%M:%S')
            db.reference(f'users/{my_name}').set({'lat': loc['coords']['latitude'], 'lon': loc['coords']['longitude'], 'gps_time': local_time, 'status': 'ACTIVE'})
            st.success("LINK ESTABLISHED.")

# --- TAB 2: RADAR ---
with tabs[1]:
    st.markdown('<div class="terminal-container"><h3>[ RADAR_SURVEILLANCE ]</h3></div>', unsafe_allow_html=True)
    users = db.reference('users').get()
    m = folium.Map(location=[13.75, 100.5], zoom_start=2, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
    if users:
        for name, info in users.items():
            if isinstance(info, dict) and 'lat' in info:
                f_color = 'cadetblue' if name == st.session_state.my_name else 'red'
                folium.Marker([info['lat'], info['lon']], tooltip=f"Agent: {name}", icon=folium.Icon(color=f_color, icon='user', prefix='fa')).add_to(m)
    st_folium(m, width="100%", height=500)

# --- TAB 3: COMMS (แยกห้องแชท) ---
with tabs[2]:
    st.markdown('<div class="terminal-container"><h3>[ COMMS_CENTER ]</h3></div>', unsafe_allow_html=True)
    webrtc_streamer(key="synapse-vcall", mode=WebRtcMode.SENDRECV)
    st.markdown("---")
    chat_mode = st.radio("SELECT MODE:", ["🌐 GLOBAL", "🔒 PRIVATE"], horizontal=True)

    if chat_mode == "🌐 GLOBAL":
        msg_input = st.chat_input("TRANSMIT TO ALL...")
        if msg_input: db.reference('global_chat').push({'name': st.session_state.my_name, 'msg': msg_input, 'ts': time.time()})
        raw_msgs = db.reference('global_chat').get()
        if raw_msgs:
            sorted_msgs = sorted(raw_msgs.values(), key=lambda x: x.get('ts', 0))
            for d in sorted_msgs[-15:]:
                align = "right" if d.get('name') == st.session_state.my_name else "left"
                style = "bubble-me" if d.get('name') == st.session_state.my_name else "bubble-others"
                st.markdown(f"<div style='text-align:{align};'><div class='{style}' style='display:inline-block;'><small>{d.get('name')}</small><br>{d.get('msg')}</div></div>", unsafe_allow_html=True)
    else:
        col_u, col_c = st.columns([1, 2])
        with col_u:
            st.write("📡 NODES")
            if users:
                for f_name in users.keys():
                    if f_name != st.session_state.my_name:
                        if st.button(f"CONNECT: {f_name}", key=f"pbtn-{f_name}"):
                            st.session_state.private_room = f"priv_{'_'.join(sorted([st.session_state.my_name, f_name]))}"
                            st.session_state.target_name = f_name
                            st.rerun()
        with col_c:
            room = st.session_state.get('private_room')
            if room:
                st.write(f"🔒 PRIV_CH: {st.session_state.target_name}")
                p_msg = st.chat_input("PRIVATE MSG...")
                if p_msg: db.reference(f'private_rooms/{room}').push({'name': st.session_state.my_name, 'msg': p_msg, 'ts': time.time()})
                raw_p_msgs = db.reference(f'private_rooms/{room}').get()
                if raw_p_msgs:
                    for d in sorted(raw_p_msgs.values(), key=lambda x: x.get('ts', 0))[-10:]:
                        align = "right" if d.get('name') == st.session_state.my_name else "left"
                        st.markdown(f"<div style='text-align:{align};'><div class='bubble-me' style='display:inline-block; border-color:#ff1744;'><small>{d.get('name')}</small><br>{d.get('msg')}</div></div>", unsafe_allow_html=True)

# --- TAB 4-7: DATA, SEC, MEDIA, SYS (คงเดิม) ---
with tabs[3]:
    if users: st.json(users)
with tabs[4]:
    st.progress(100, "SIGNAL SECURE")
    st.code("X-KEY: QUANTUM-RED-ALPHA")
with tabs[5]:
    st.video("https://www.youtube.com/watch?v=f0h8PjdZzrw")
with tabs[6]:
    if st.button("💣 WIPE CHATS"):
        db.reference('private_rooms').delete()
        db.reference('global_chat').delete()
    if st.button("🧼 FULL RESET"): db.reference('/').delete()
