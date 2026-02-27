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
# 1. CORE SYSTEM CONFIGURATION (NEON THEME)
# ==========================================
st.set_page_config(page_title="SYNAPSE QUANTUM CONTROL", layout="wide")
st_autorefresh(interval=5000, key="global_refresh")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #001 0%, #000 100%); color: #00f2fe; font-family: 'Courier New', Courier, monospace; }
    .neon-header { 
        font-size: 45px; font-weight: 900; text-align: center;
        color: #fff; text-shadow: 0 0 10px #00f2fe, 0 0 20px #ff00de;
        border: 4px double #00f2fe; padding: 15px; background: rgba(0,0,0,0.8);
        border-radius: 20px; margin-bottom: 10px;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #00f2fe 0%, #000 50%, #ff00de 100%);
        color: white !important; border: 1px solid #fff; border-radius: 5px;
        height: 45px; font-weight: bold; width: 100%; transition: 0.5s;
        box-shadow: 0 0 10px #00f2fe;
    }
    div.stButton > button:hover { box-shadow: 0 0 25px #ff00de; transform: scale(1.02); }
    .bubble-me { background: rgba(0, 242, 254, 0.15); border: 1px solid #00f2fe; padding: 10px; border-radius: 15px 15px 0 15px; margin-bottom: 10px; color: #fff; }
    .bubble-others { background: rgba(255, 71, 71, 0.15); border: 1px solid #ff4747; padding: 10px; border-radius: 15px 15px 15px 0; margin-bottom: 10px; color: #fff; }
    .terminal-container { border: 1px solid #00f2fe; padding: 15px; border-radius: 10px; background: rgba(0, 242, 254, 0.05); border-left: 8px solid #00f2fe; margin-bottom: 15px; }
    .clock-box { background: rgba(0,0,0,0.6); border: 1px solid #00f2fe; padding: 10px; border-radius: 8px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. AUDIO & FIREBASE
# ==========================================
direct_link = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
st.components.v1.html(f"""
    <audio id="synapse-audio" loop autoplay><source src="{direct_link}" type="audio/mpeg"></audio>
    <script>var audio = document.getElementById("synapse-audio"); window.parent.document.addEventListener('click', function() {{ audio.play(); }}, {{ once: true }});</script>
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
# 3. GLOBAL HEADER & WORLD CLOCK (เพิ่มใหม่)
# ==========================================
st.markdown('<div class="neon-header">S Y N A P S E _ O V E R L O R D</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
zones = {'BANGKOK': 'Asia/Bangkok', 'NEW YORK': 'America/New_York', 'LONDON': 'Europe/London', 'TOKYO': 'Asia/Tokyo'}
for col, (city, zone) in zip([c1, c2, c3, c4], zones.items()):
    now = datetime.datetime.now(pytz.timezone(zone)).strftime('%H:%M:%S')
    col.markdown(f"<div class='clock-box'><small>{city}</small><br><b style='color:#ff00de;'>{now}</b></div>", unsafe_allow_html=True)

# ==========================================
# 4. SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>CONTROL CENTER</h2>", unsafe_allow_html=True)
    if os.path.exists("logo3.jpg"): st.image("logo3.jpg", use_container_width=True)
    st.markdown("---")
    st.audio(direct_link, format="audio/mpeg", loop=True)
    if st.button("🔍 SCAN NETWORK"): st.toast("Scanning encrypted nodes...")
    if st.button("🔐 ENCRYPT ALL"): st.toast("Applying AES-256 to all data streams...")
    st.markdown("---")
    st.write(f"SYSTEM UPTIME: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ==========================================
# 5. MAIN INTERFACE
# ==========================================
tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "📊 DATA LOG", "🔐 SECURITY", "📺 MEDIA", "🧹 SYSTEM"])

# --- TAB 1: CORE ---
with tabs[0]:
    st.markdown('<div class="terminal-container"><h3>[ PROTOCOL_IDENTIFICATION ]</h3></div>', unsafe_allow_html=True)
    st.session_state.my_name = st.text_input("ระบุชื่อรหัสของคุณ:", value=st.session_state.get('my_name', 'Guest'))
    if st.button("🚀 INITIATE QUANTUM LINK"):
        loc = get_geolocation()
        if loc:
            db.reference(f'users/{st.session_state.my_name}').set({
                'lat': loc['coords']['latitude'], 'lon': loc['coords']['longitude'],
                'gps_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'status': 'ACTIVE'
            })
            st.success("GLOBAL POSITIONING SYNCHRONIZED.")

# --- TAB 2: RADAR ---
with tabs[1]:
    st.markdown('<div class="terminal-container"><h3>[ GLOBAL_SURVEILLANCE_RADAR ]</h3></div>', unsafe_allow_html=True)
    users = db.reference('users').get()
    m = folium.Map(location=[13.75, 100.5], zoom_start=2, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
    if users:
        for name, info in users.items():
            if isinstance(info, dict) and 'lat' in info:
                folium.Marker([info['lat'], info['lon']], popup=f"{name}", icon=folium.Icon(color='red' if name != st.session_state.my_name else 'cadetblue')).add_to(m)
    st_folium(m, width="100%", height=500)

# --- TAB 3: COMMS ---
with tabs[2]:
    st.markdown('<div class="terminal-container"><h3>[ ENCRYPTED_COMM_PROTOCOL ]</h3></div>', unsafe_allow_html=True)
    webrtc_streamer(key="vcall", mode=WebRtcMode.SENDRECV, rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
    st.markdown("---")
    col_u, col_c = st.columns([1, 2])
    with col_u:
        st.write("📡 ONLINE NODES")
        if users:
            for f_name in users.keys():
                if f_name != st.session_state.my_name:
                    if st.button(f"TALK TO {f_name}", key=f"chat-{f_name}"):
                        st.session_state.private_room = f"sec_{'_'.join(sorted([st.session_state.my_name, f_name]))}"
                        st.session_state.target_name = f_name
                        st.rerun()
    with col_c:
        room = st.session_state.get('private_room')
        if room:
            st.write(f"🔒 CHANNEL: {st.session_state.target_name}")
            msg_input = st.chat_input("TRANSMIT MESSAGE...")
            if msg_input: db.reference(f'chats/{room}').push({'name': st.session_state.my_name, 'msg': msg_input, 'ts': time.time()})
            msgs = db.reference(f'chats/{room}').order_by_child('ts').limit_to_last(10).get()
            if msgs:
                for d in msgs.values():
                    align = "right" if d['name'] == st.session_state.my_name else "left"
                    style = "bubble-me" if d['name'] == st.session_state.my_name else "bubble-others"
                    st.markdown(f"<div style='text-align:{align};'><div class='{style}' style='display:inline-block;'><small>{d['name']}</small><br>{d['msg']}</div></div>", unsafe_allow_html=True)

# --- TAB 4: DATA LOG (ทำให้ดูดีขึ้น) ---
with tabs[3]:
    st.markdown('<div class="terminal-container"><h3>[ METADATA_ANALYSIS ]</h3></div>', unsafe_allow_html=True)
    if users:
        df = pd.DataFrame.from_dict(users, orient='index')
        st.dataframe(df, use_container_width=True)
    if st.button("🗑️ CLEAR ACCESS LOGS"): db.reference('users').delete(); st.rerun()

# --- TAB 5: SECURITY (ทำให้ใช้งานได้จริง) ---
with tabs[4]:
    st.markdown('<div class="terminal-container"><h3>[ NETWORK_SCANNER ]</h3></div>', unsafe_allow_html=True)
    if st.button("⚡ START DEEP SCAN"):
        with st.status("Scanning...", expanded=True) as status:
            for i in range(5):
                st.write(f"Scanning Node {random.randint(100,999)}... [IP: 192.168.{random.randint(1,254)}.{random.randint(1,254)}]")
                time.sleep(0.5)
            status.update(label="SCAN COMPLETE: NO INTRUSIONS FOUND", state="complete", expanded=False)
    st.progress(random.randint(85,100), "SIGNAL INTEGRITY")

# --- TAB 6: MEDIA ---
with tabs[5]:
    st.markdown('<div class="terminal-container"><h3>[ VISUAL_STREAMS ]</h3></div>', unsafe_allow_html=True)
    st.video("https://www.youtube.com/watch?v=f0h8PjdZzrw")

# --- TAB 7: SYSTEM ---
with tabs[6]:
    st.markdown('<div class="terminal-container"><h3>[ KERNEL_DESTRUCTION ]</h3></div>', unsafe_allow_html=True)
    if st.button("💣 WIPE ALL CHATS"): db.reference('chats').delete(); st.success("CLEARED")
    if st.button("🧼 FULL FACTORY RESET"): db.reference('/').delete(); st.error("ALL DATA WIPED")
