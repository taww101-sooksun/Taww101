import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import folium
from streamlit_folium import st_folium
import os
import random
import time
import streamlit.components.v1 as components

# --- 1. SET UP & THEME ---
st.set_page_config(page_title="SYNAPSE ROOMS", layout="wide")

# ระบบจำค่าสีนีออน (Color Selector จากโค้ดที่พี่ส่งมา)
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#39FF14" 
if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#000000"

with st.sidebar:
    if os.path.exists("logo2.jpg"):
        st.image("logo2.jpg", use_container_width=True)
    st.markdown("### 🎨 ปรับแต่งสีระบบ")
    st.session_state.theme_color = st.color_picker("เลือกสีนีออน", st.session_state.theme_color)
    st.session_state.bg_color = st.color_picker("เลือกสีพื้นหลัง", st.session_state.bg_color)
    st.write("---")
    st.markdown('**สโลแกน:** \n*"อยู่นิ่งๆ ไม่เจ็บตัว"*')

# --- 2. CSS DYNAMIC THEME (นีออน & Marquee) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    .stApp {{ background-color: {st.session_state.bg_color} !important; color: {st.session_state.theme_color} !important; }}
    .marquee {{
        width: 100%; overflow: hidden; white-space: nowrap; background: rgba(0,0,0,0.6);
        padding: 15px 0; border-radius: 12px; margin-bottom: 15px; border: 2px solid {st.session_state.theme_color};
    }}
    .marquee p {{
        display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite;
        font-family: 'Orbitron', sans-serif; font-size: 22px; color: {st.session_state.theme_color};
    }}
    @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
    .stButton>button {{
        width: 100%; background-color: transparent !important; color: {st.session_state.theme_color} !important;
        border: 3px solid {st.session_state.theme_color} !important; border-radius: 10px;
    }}
    h1, h2, h3, p, span, label {{ font-family: 'Orbitron', sans-serif; color: {st.session_state.theme_color} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. INITIALIZE FIREBASE (ใช้ Secrets ปลอดภัย 100%) ---
if not firebase_admin._apps:
    try:
        fb_config = {
            "type": "service_account",
            "project_id": st.secrets["project_id"],
            "private_key": st.secrets["private_key"].replace('\\n', '\n'),
            "client_email": st.secrets["client_email"],
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        cred = credentials.Certificate(fb_config)
        firebase_admin.initialize_app(cred, {'databaseURL': "https://sooksun1-default-rtdb.firebaseio.com/"})
        st.toast("✅ SYNAPSE ONLINE")
    except Exception as e:
        st.error(f"🚨 Firebase Error: {e}")

# --- 4. MAIN INTERFACE (TABS) ---
tabs = st.tabs(["🎸 MUSIC", "🛰️ RADAR", "📞 COMMS"])

# --- TAB 1: MUSIC PLAYER (ระบบจัดการเพลงที่พี่ให้มา) ---
with tabs[0]:
    music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if music_files:
        if 'song_index' not in st.session_state: st.session_state.song_index = 0
        current_song = music_files[st.session_state.song_index]
        
        st.markdown(f'<div class="marquee"><p>NOW PLAYING: {current_song} •--• NEXT TRACK UP SOON </p></div>', unsafe_allow_html=True)
        
        # แสดงภาพประกอบเพลง
        base_name = os.path.splitext(current_song)[0]
        if os.path.exists(base_name + ".jpg"):
            st.image(base_name + ".jpg", use_container_width=True)
        
        st.audio(current_song)
        
        # ปุ่มควบคุม
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⏭️ เพลงถัดไป"):
                st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
                st.rerun()
        with col2:
            if st.button("🎲 สุ่มเพลง"):
                st.session_state.song_index = random.randint(0, len(music_files)-1)
                st.rerun()
    else:
        st.warning("ไม่พบไฟล์เพลงใน GitHub")

# --- TAB 2: RADAR (แผนที่ดาวเทียม Google Hybrid) ---
with tabs[1]:
    st.subheader("🛰️ STRATEGIC RADAR (Google Hybrid)")
    # พิกัดเบื้องต้น (กรุงเทพฯ)
    lat_v, lon_v = 13.7563, 100.5018
    google_hybrid = 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'
    
    m = folium.Map(location=[lat_v, lon_v], zoom_start=16, tiles=google_hybrid, attr='Google Satellite')
    folium.Marker([lat_v, lon_v], popup="CENTER", icon=folium.Icon(color='red')).add_to(m)
    st_folium(m, width="100%", height=500)

# --- TAB 3: COMMS (ฆ่าติ่ง JOIN / ระบบคอล) ---
with tabs[2]:
    st.subheader("💬 SECURE VOICE CALL")
    # โค้ด Jitsi ที่พี่ต้องการ (ฆ่าติ่ง Join และลบ Watermark)
    jitsi_code = f"""
        <div id="meet" style="height:500px; width:100%; border:2px solid {st.session_state.theme_color}; border-radius:15px;"></div>
        <script src="https://meet.jit.si/external_api.js"></script>
        <script>
            const options = {{
                roomName: 'SYNAPSE_SOOKSUN1_SECURE',
                width: '100%', height: 500,
                parentNode: document.querySelector('#meet'),
                configOverwrite: {{
                    prejoinPageEnabled: false,
                    disableDeepLinking: true,
                    startWithAudioMuted: false,
                    startWithVideoMuted: false,
                    enableWelcomePage: false
                }},
                interfaceConfigOverwrite: {{
                    SHOW_JITSI_WATERMARK: false,
                    HIDE_INVITE_ON_WELCOME_PAGE: true,
                    TOOLBAR_BUTTONS: ['microphone', 'camera', 'hangup', 'chat']
                }}
            }};
            new JitsiMeetExternalAPI('meet.jit.si', options);
        </script>
    """
    components.html(jitsi_code, height=520)

# --- 5. ระบบ DATABASE STATUS (ยิงข้อมูลเข้า Firebase) ---
st.write("---")
st.subheader("📡 SYSTEM STATUS UPDATE")
msg = st.text_input("ระบุสถานะปัจจุบัน:", value="Online")
if st.button("🚀 UPDATE STATUS"):
    try:
        db.reference('logs').push({'user': 'Ta101', 'msg': msg, 'ts': time.time()})
        st.success("อัปเดตสถานะสำเร็จ!")
    except: st.error("ส่งไม่สำเร็จ")
