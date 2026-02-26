import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from streamlit_autorefresh import st_autorefresh

# --- 1. CORE SYSTEM & NEON UI ---
st.set_page_config(page_title="SYNAPSE QUANTUM CONTROL", layout="wide")
st_autorefresh(interval=5000, key="global_refresh")

st.markdown("""
    <style>
    /* พื้นหลังและฟอนต์สไตล์ห้องควบคุม */
    .stApp { background: radial-gradient(circle, #001 0%, #000 100%); color: #00f2fe; font-family: 'Courier New', Courier, monospace; }
    
    /* หัวข้อหลักแบบเรืองแสงสไตล์ Cyberpunk */
    .neon-title { 
        font-size: 60px; font-weight: 900; text-align: center;
        color: #fff; text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe, 0 0 30px #ff00de;
        border: 4px double #00f2fe; padding: 20px; margin: 20px 0; background: rgba(0,0,0,0.5);
    }
    
    /* ปุ่มกดแบบมีลวดลายและ Animation */
    div.stButton > button {
        background: linear-gradient(135deg, #00f2fe 0%, #000 50%, #ff00de 100%);
        color: white; border: 2px solid #fff; border-radius: 10px;
        height: 50px; font-weight: bold; text-transform: uppercase;
        box-shadow: 0 0 15px #00f2fe; transition: all 0.5s;
    }
    div.stButton > button:hover {
        box-shadow: 0 0 30px #ff00de; transform: translateY(-3px) scale(1.02);
    }
    
    /* กรอบเนื้อหาที่มีลวดลาย */
    .terminal-box {
        border: 1px solid #00f2fe; background: rgba(0, 242, 254, 0.05);
        padding: 20px; border-left: 10px solid #00f2fe; margin: 10px 0;
        box-shadow: inset 0 0 10px #00f2fe;
    }
    
    /* ตกแต่ง Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 15px; }
    .stTabs [data-baseweb="tab"] {
        background: #111; border: 1px solid #00f2fe; color: #00f2fe;
        padding: 10px 30px; border-radius: 5px; font-weight: bold;
    }
    .stTabs [aria-selected="true"] { background: #00f2fe !important; color: #000 !important; box-shadow: 0 0 20px #00f2fe; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR : THE JUKEBOX & STATUS ---
with st.sidebar:
    st.markdown("<h2 style='text-align:center;'>🛰️ CONTROL PANEL</h2>", unsafe_allow_html=True)
    if os.path.exists("logo3.jpg"):
        st.image("logo3.jpg", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 🎵 SYNAPSE RADIO (27 MINS)")
    song_url = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
    st.audio(song_url, format="audio/mpeg", loop=True)
    st.info("💡 ระบบจะเล่นเพลงวนลูป 27 นาที ตลอดการใช้งาน")
    
    st.markdown("---")
    st.markdown("### 🛠️ QUICK COMMANDS")
    c1, c2 = st.columns(2)
    with c1: st.button("🛰️ SCAN")
    with c2: st.button("🔒 LOCK")
    st.button("🔴 EMERGENCY RESET")
    st.markdown("---")
    st.write(f"SYSTEM TIME: {datetime.datetime.now().strftime('%H:%M:%S')}")

# --- 3. MAIN HEADER ---
st.markdown('<div class="neon-title">S Y N A P S E _ O V E R L O R D</div>', unsafe_allow_html=True)

# --- 4. FIREBASE LOGIC ---
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        if "private_key" in fb_dict: fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except: st.error("Firebase Connection Failed.")

# --- 5. THE 10 TABS EXPERIENCE ---
t1, t2, t3, t4, t5, t6, t7 = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "📊 LOGS", "🔐 SECURE", "📺 MEDIA", "🛠️ KERNEL"])

with t1: # CORE ACCESS
    st.markdown('<div class="terminal-box"><h3>[ SYSTEM_ACCESS_PROTOCOL ]</h3></div>', unsafe_allow_html=True)
    st.session_state.my_name = st.text_input("IDENTIFY YOURSELF:", value=st.session_state.get('my_name', 'Guest'))
    if st.button("🚀 INITIATE QUANTUM LINK"):
        loc = get_geolocation()
        if loc:
            raw_time = loc.get('timestamp', datetime.datetime.now().timestamp())
            local_time = datetime.datetime.fromtimestamp(raw_time/1000).strftime('%Y-%m-%d %H:%M:%S')
            db.reference(f'users/{st.session_state.my_name}').set({
                'lat': loc['coords']['latitude'], 'lon': loc['coords']['longitude'],
                'gps_time': local_time, 'status': 'online'
            })
            st.success("GLOBAL POSITIONING SYNCHRONIZED.")

with t2: # RADAR (GPS MAP)
    st.markdown('<div class="terminal-box"><h3>[ SATELLITE_GLOBAL_RADAR ]</h3></div>', unsafe_allow_html=True)
    users = db.reference('users').get()
    if users:
        m = folium.Map(location=[13.75, 100.5], zoom_start=2, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
        for name, info in users.items():
            if isinstance(info, dict) and 'lat' in info:
                m_color = 'cadetblue' if name == st.session_state.my_name else 'red'
                folium.Marker([info['lat'], info['lon']], popup=f"{name}\n{info.get('gps_time')}",
                              icon=folium.Icon(color=m_color, icon='screenshot')).add_to(m)
        st_folium(m, width="100%", height=550)

with t3: # COMMS (CHAT)
    st.markdown('<div class="terminal-box"><h3>[ ENCRYPTED_MESSAGE_STREAM ]</h3></div>', unsafe_allow_html=True)
    # ใส่ระบบแชทเดิมที่นี่...
    st.info("กำลังรอการเชื่อมต่อจากปลายทาง...")

with t4: # LOGS
    st.markdown('<div class="terminal-box"><h3>[ NETWORK_DATALOG ]</h3></div>', unsafe_allow_html=True)
    if users: st.json(users)

with t5: # SECURE
    st.markdown('<div class="terminal-box"><h3>[ CRYPTO_VAULT ]</h3></div>', unsafe_allow_html=True)
    st.write("ระบบเข้ารหัสข้อมูลขั้นสูงทำงานอยู่...")
    st.progress(85, text="ENCRYPTION STRENGTH")

with t6: # MEDIA
    st.markdown('<div class="terminal-box"><h3>[ VISUAL_SURVEILLANCE ]</h3></div>', unsafe_allow_html=True)
    st.write("ใส่ลิงก์กล้องหรือวิดีโอที่นี่...")
    st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ") # ต้วอย่างวิดีโอ

with t7: # KERNEL
    st.markdown('<div class="terminal-box"><h3>[ SYSTEM_KERNEL_DUMP ]</h3></div>', unsafe_allow_html=True)
    st.code(f"USER: {st.session_state.get('my_name')}\nPLATFORM: SYNAPSE_V101\nSTATUS: ACTIVE", language="text")
