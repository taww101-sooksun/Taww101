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

# ตกแต่ง UI แบบฉบับกองบัญชาการ สีสด แสงหายใจ
st.markdown("""
    <style>
    /* พื้นหลังหลัก */
    .stApp { background: radial-gradient(circle, #001 0%, #000 100%); color: #00f2fe; font-family: 'Courier New', Courier, monospace; }
    
    /* หัวข้อหลัก: สีแดงสดตัดฟ้า */
    .neon-header { 
        font-size: 20px; font-weight: 900; text-align: center;
        color: #fff; text-shadow: 0 0 5px #ff1744, 0 0 10px #00f2fe;
        border: 4px double #ff1744; padding: 20px; background: rgba(0,0,0,0.85);
        border-radius: 20px; margin-bottom: 30px;
    }
    
    /* ปุ่มกด: เอฟเฟกต์แสงหายใจ (บ่งบอกว่ากดได้) */
    @keyframes breathing {
        0% { box-shadow: 0 0 5px #ff1744; }
        50% { box-shadow: 0 0 20px #ff1744; }
        100% { box-shadow: 0 0 5px #ff1744; }
    }

    div.stButton > button {
        background: linear-gradient(135deg, #ff1744 0%, #000 50%, #ff00de 100%);
        color: white !important; border: 2px solid #fff; border-radius: 20px;
        height: 20px; font-weight: bold; width: 100%; transition: 0.5s;
        animation: breathing 3s infinite ease-in-out;
    }
    div.stButton > button:hover {
        box-shadow: 0 0 20px #ff00de; transform: scale(1.02);
        background: #fff; color: #000 !important;
    }
    div.stButton > button:active { transform: scale(0.95); }
    
    /* กล่องข้อความแชท */
    .bubble-me { background: rgba(0, 242, 254, 0.15); border: 2px solid #00f2fe; padding: 12px; border-radius: 15px 15px 0 15px; margin-bottom: 10px; color: #fff; }
    .bubble-others { background: rgba(255, 23, 68, 0.15); border: 2px solid #ff1744; padding: 12px; border-radius: 15px 15px 15px 0; margin-bottom: 10px; color: #fff; }
    
    /* กรอบข้อมูลนิ่งๆ (Static) */
    .terminal-container {
        border: 1px solid rgba(0, 242, 254, 0.5); padding: 20px; border-radius: 10px;
        background: rgba(0, 5, 15, 0.9); border-left: 8px solid #00f2fe;
    }
    </style>
    """, unsafe_allow_html=True)
# --- 4. HEADER SECTION ---
if os.path.exists("logo3.jpg"):
    col_l, col_m, col_r = st.columns([1, 1, 1])
    with col_m:
        st.image("logo3.jpg", use_container_width=True)
else:
    st.markdown("<h1 style='text-align: center; color: #00f2fe; text-shadow: 0 0 20px rgba(0,242,254,0.5);'>SYNAPSE CONTROL</h1>", unsafe_allow_html=True)
# ==========================================
# 2. AUTOMATIC HIDDEN AUDIO
# ==========================================
direct_link = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"

st.components.v1.html(f"""
    <audio id="synapse-audio" loop autoplay style="display:none;">
        <source src="{direct_link}" type="audio/mpeg">
    </audio>
    <script>
        var audio = document.getElementById("synapse-audio");
        window.parent.document.addEventListener('click', function() {{
            audio.play();
        }}, {{ once: true }});
    </script>
""", height=0)
with st.sidebar:
    st.markdown("### 🛰️ NETWORK CENTER")
    audio_file = "ตัดเอาทอนสุดท้าย.mp3"
    if os.path.exists(audio_file):
        st.audio(audio_file, format="audio/mp3", loop=True)
    st.write(f"UPTIME: {datetime.datetime.now().strftime('%H:%M:%S')}")


# ==========================================
# 3. FIREBASE INFRASTRUCTURE
# ==========================================
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_dict = dict(st.secrets["firebase"])
            if "private_key" in fb_dict:
                fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            creds = credentials.Certificate(fb_dict)
            firebase_admin.initialize_app(creds, {
                'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
    except Exception as e:
        st.error(f"SYSTEM_ERROR: {e}")

# ==========================================
# 4. SIDEBAR : CONTROL CENTER
# ==========================================
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>CONTROL CENTER</h2>", unsafe_allow_html=True)
    if os.path.exists("logo3.jpg"):
        st.image("logo3.jpg", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 🎵 AUDIO FREQUENCY")
    st.audio(direct_link, format="audio/mpeg", loop=True)
    
    st.markdown("---")
    st.markdown("### 🛡️ QUICK COMMANDS")
    if st.button("🔍 SCAN NETWORK"):
        st.toast("กำลังวิเคราะห์โหนดโครงข่าย...")
    
    st.markdown("---")
    st.write(f"SYSTEM UPTIME: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ==========================================
# 5. MAIN INTERFACE
# ==========================================
st.markdown('<div class="neon-header">S Y N A P S E _ O V E R L O R D</div>', unsafe_allow_html=True)

tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "📊 DATA LOG", "🔐 SECURITY", "📺 MEDIA", "🧹 SYSTEM"])

# --- TAB 1: CORE (IDENTIFICATION) ---
with tabs[0]:
    st.markdown('<div class="terminal-container"><h3>[ PROTOCOL_IDENTIFICATION ]</h3></div>', unsafe_allow_html=True)
    st.session_state.my_name = st.text_input("ระบุชื่อรหัสของคุณ:", value=st.session_state.get('my_name', 'Guest'))
    
    if st.button("🚀 INITIATE QUANTUM LINK"):
        loc = get_geolocation()
        if loc:
            raw_time = loc.get('timestamp', datetime.datetime.now().timestamp())
            local_time = datetime.datetime.fromtimestamp(raw_time/1000).strftime('%Y-%m-%d %H:%M:%S')
            db.reference(f'users/{st.session_state.my_name}').set({
                'lat': loc['coords']['latitude'], 
                'lon': loc['coords']['longitude'],
                'gps_time': local_time,
                'status': 'ACTIVE'
            })
            st.success("GLOBAL POSITIONING SYNCHRONIZED.")

# --- TAB 2: RADAR (GLOBAL MAP) ---
with tabs[1]:
    st.markdown('<div class="terminal-container"><h3>[ GLOBAL_SURVEILLANCE_RADAR ]</h3></div>', unsafe_allow_html=True)
    users = db.reference('users').get()
    m = folium.Map(location=[13.75, 100.5], zoom_start=2, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
    if users:
        for name, info in users.items():
            if isinstance(info, dict) and 'lat' in info:
                f_color = 'cadetblue' if name == st.session_state.my_name else 'red'
                folium.Marker(
                    [info['lat'], info['lon']], 
                    tooltip=f"Agent: {name}",
                    icon=folium.Icon(color=f_color, icon='user', prefix='fa')
                ).add_to(m)
    st_folium(m, width="100%", height=600)

# --- TAB 3: COMMS (CHAT & CALL) ---
with tabs[2]:
    st.markdown('<div class="terminal-container"><h3>[ ENCRYPTED_COMM_PROTOCOL ]</h3></div>', unsafe_allow_html=True)
    webrtc_streamer(key="synapse-vcall", mode=WebRtcMode.SENDRECV)
    
    st.markdown("---")
    chat_mode = st.radio("เลือกช่องทางการสื่อสาร:", ["🌐 ห้องสาธารณะ (Global)", "🔒 ห้องส่วนตัว (Private)"], horizontal=True)

    if chat_mode == "🌐 ห้องสาธารณะ (Global)":
        msg_input = st.chat_input("คุยรวมกับทุกคน...")
        if msg_input:
            db.reference('global_chat').push({'name': st.session_state.my_name, 'msg': msg_input, 'ts': time.time()})
        
        raw_msgs = db.reference('global_chat').get()
        if raw_msgs:
            # เรียงลำดับด้วย Python เพื่อป้องกัน Error
            sorted_msgs = sorted(raw_msgs.values(), key=lambda x: x.get('ts', 0))
            for d in sorted_msgs[-15:]:
                is_me = d.get('name') == st.session_state.my_name
                style = "bubble-me" if is_me else "bubble-others"
                align = "right" if is_me else "left"
                st.markdown(f"<div style='text-align:{align};'><div class='{style}' style='display:inline-block;'><small>{d.get('name')}</small><br>{d.get('msg')}</div></div>", unsafe_allow_html=True)

    else:
        col_u, col_c = st.columns([1, 2])
        with col_u:
            st.write("📡 ONLINE NODES")
            if users:
                for f_name in users.keys():
                    if f_name != st.session_state.my_name:
                        if st.button(f"CONNECT TO {f_name}", key=f"pbtn-{f_name}"):
                            pair = sorted([st.session_state.my_name, f_name])
                            st.session_state.private_room = f"priv_{pair[0]}_{pair[1]}"
                            st.session_state.target_name = f_name
                            st.rerun()
        with col_c:
            room = st.session_state.get('private_room')
            if room:
                st.write(f"🔒 SECURE CHANNEL: {st.session_state.target_name}")
                p_msg = st.chat_input("ส่งข้อความลับ...")
                if p_msg:
                    db.reference(f'private_rooms/{room}').push({'name': st.session_state.my_name, 'msg': p_msg, 'ts': time.time()})
                
                raw_p_msgs = db.reference(f'private_rooms/{room}').get()
                if raw_p_msgs:
                    sorted_p_msgs = sorted(raw_p_msgs.values(), key=lambda x: x.get('ts', 0))
                    for d in sorted_p_msgs[-10:]:
                        align = "right" if d.get('name') == st.session_state.my_name else "left"
                        st.markdown(f"<div style='text-align:{align};'><div class='bubble-me' style='display:inline-block; border-color:#ff00de;'><small>{d.get('name')}</small><br>{d.get('msg')}</div></div>", unsafe_allow_html=True)

# --- TAB 4: DATA LOG ---
with tabs[3]:
    st.markdown('<div class="terminal-container"><h3>[ METADATA_ANALYSIS ]</h3></div>', unsafe_allow_html=True)
    if users:
        st.json(users)
    if st.button("🗑️ CLEAR ACCESS LOGS"):
        db.reference('users').delete()
        st.rerun()

# --- TAB 5: SECURITY ---
with tabs[4]:
    st.markdown('<div class="terminal-container"><h3>[ SECURITY_OVERRIDE ]</h3></div>', unsafe_allow_html=True)
    st.progress(100, "SIGNAL INTEGRITY")
    st.code("QUANTUM_KEY: SH-256-X99-SYNPSE-ALPHA", language="text")

# --- TAB 6: MEDIA ---
with tabs[5]:
    st.markdown('<div class="terminal-container"><h3>[ VISUAL_STREAMS ]</h3></div>', unsafe_allow_html=True)
    st.video("https://www.youtube.com/watch?v=f0h8PjdZzrw")

# --- TAB 7: SYSTEM ---
with tabs[6]:
    st.markdown('<div class="terminal-container"><h3>[ KERNEL_DESTRUCTION ]</h3></div>', unsafe_allow_html=True)
    if st.button("💣 WIPE ALL CHATS"):
        db.reference('private_rooms').delete()
        db.reference('global_chat').delete()
        st.success("ล้างประวัติแชททั้งหมดแล้ว!")
    if st.button("🧼 FULL FACTORY RESET"):
        db.reference('/').delete()
        st.error("ระบบถูกรีเซ็ตค่าเริ่มต้น!")
