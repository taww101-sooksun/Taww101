import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os
import time
import random
import string
import pandas as pd
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. SETUP & THEME (COMPACT & POWERFUL)
# ==========================================
st.set_page_config(page_title="SYNAPSE V2", layout="wide")
st_autorefresh(interval=5000, key="global_refresh")

st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle, #001 0%, #000 100%); color: #00f2fe; font-family: 'Courier New', Courier, monospace; }
    
    /* หัวข้อหลัก SYNAPSE */
    .neon-header { 
        font-size: 35px; font-weight: 900; text-align: center;
        color: #fff; text-shadow: 0 0 10px #00f2fe, 0 0 20px #ff00de;
        border: 2px solid #00f2fe; padding: 10px; background: rgba(0,0,0,0.8);
        border-radius: 10px; margin-bottom: 20px; letter-spacing: 10px;
    }
    
    /* กรอบเนื้อหาภายใน */
    .terminal-container {
        border: 1px solid #00f2fe; padding: 15px; border-radius: 8px;
        background: rgba(0, 242, 254, 0.05); border-left: 5px solid #ff00de;
        margin-bottom: 15px;
    }
    
    /* ตกแต่งปุ่ม */
    div.stButton > button {
        background: linear-gradient(135deg, #00f2fe 0%, #000 100%);
        color: white !important; border: 1px solid #fff; transition: 0.3s;
    }
    div.stButton > button:hover { box-shadow: 0 0 15px #ff00de; transform: scale(1.02); }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FIREBASE INITIALIZATION
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
# 3. GLOBAL LOGO & HEADER (โชว์ทุกหน้า)
# ==========================================
# แสดง Logo ขนาด 400 กึ่งกลาง
col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    if os.path.exists("logo3.jpg"):
        st.image("logo3.jpg", width=400)
    st.markdown('<div class="neon-header">SYNAPSE</div>', unsafe_allow_html=True)

# ==========================================
# 4. SIDEBAR (AUDIO CONTROL)
# ==========================================
audio_file = "ฉันผิดเองที่เดินหนี้ความจริง.mp3"
with st.sidebar:
    st.markdown("### 🛰️ NETWORK PLAYER")
    if os.path.exists(audio_file):
        st.audio(audio_file, format="audio/mp3", loop=True)
    st.markdown("---")
    st.write(f"SYSTEM UPTIME: {datetime.datetime.now().strftime('%H:%M:%S')}")

# ==========================================
# 5. MAIN TABS (ทุกหน้าใช้งานได้จริง)
# ==========================================
tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "📊 LOGS", "🔐 SEC", "📺 MEDIA", "🧹 SYS"])

# --- TAB 1: CORE (ระบบยืนยันตัวตน) ---
with tabs[0]:
    st.markdown('<div class="terminal-container">[ AUTHENTICATION_PROTOCOL ]</div>', unsafe_allow_html=True)
    st.session_state.my_name = st.text_input("ระบุชื่อรหัสของคุณ:", value=st.session_state.get('my_name', 'Agent_X'))
    if st.button("🚀 CONNECT TO CLOUD"):
        st.success(f"ยินดีต้อนรับ {st.session_state.my_name} เข้าสู่ระบบ SYNAPSE")

# --- TAB 2: RADAR (แผนที่ส่องพิกัด) ---
with tabs[1]:
    st.markdown('<div class="terminal-container">[ GLOBAL_RADAR_FEED ]</div>', unsafe_allow_html=True)
    m = folium.Map(location=[13.75, 100.5], zoom_start=5, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google")
    st_folium(m, width="100%", height=400)

# --- TAB 3: COMMS (ระบบแชทและวิดีโอคอล) ---
with tabs[2]:
    st.markdown('<div class="terminal-container">[ SECURE_COMMUNICATION ]</div>', unsafe_allow_html=True)
    
    # วิดีโอคอล (WebRTC)
    webrtc_streamer(key="video-call", mode=WebRtcMode.SENDRECV)
    
    st.markdown("---")
    st.subheader("💬 ระบบแชทลับ (Global Chat)")
    
    # ฟอร์มส่งข้อความแชท
    with st.form("chat_form", clear_on_submit=True):
        msg = st.text_input("พิมพ์ข้อความที่ต้องการส่ง...")
        submitted = st.form_submit_tag("TRANSMIT")
        if submitted and msg:
            db.reference('global_chat').push({
                'user': st.session_state.my_name,
                'msg': msg,
                'ts': time.time()
            })
    
    # แสดงข้อความแชท 10 ข้อความล่าสุด
    chat_history = db.reference('global_chat').order_by_child('ts').limit_to_last(10).get()
    if chat_history:
        for k, v in reversed(chat_history.items()):
            st.markdown(f"**{v['user']}**: {v['msg']}")

# --- TAB 4: LOGS (วิเคราะห์ข้อมูล) ---
with tabs[3]:
    st.markdown('<div class="terminal-container">[ DATA_METRICS ]</div>', unsafe_allow_html=True)
    log_data = pd.DataFrame({
        "ID": ["SYS-01", "SYS-02", "SYS-03"],
        "STATUS": ["ONLINE", "ONLINE", "ENCRYPTED"],
        "LATENCY": ["12ms", "24ms", "10ms"]
    })
    st.dataframe(log_data, use_container_width=True)

# --- TAB 5: SEC (สุ่มรหัสผ่าน) ---
with tabs[4]:
    st.markdown('<div class="terminal-container">[ QUANTUM_SECURITY ]</div>', unsafe_allow_html=True)
    if st.button("🔑 GENERATE MASTER KEY"):
        key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        st.code(key)

# --- TAB 6: MEDIA (โชว์วิดีโอและเพลง) ---
with tabs[5]:
    st.markdown('<div class="terminal-container">[ BROADCAST_CHANNEL ]</div>', unsafe_allow_html=True)
    st.video("https://www.youtube.com/watch?v=F3zR5W0Bv0U")
    if os.path.exists(audio_file):
        st.audio(audio_file)

# --- TAB 7: SYS (ล้างระบบ) ---
with tabs[6]:
    st.markdown('<div class="terminal-container">[ SYSTEM_WIPE ]</div>', unsafe_allow_html=True)
    if st.button("💣 DELETE ALL LOGS"):
        db.reference('global_chat').delete()
        st.error("ข้อมูลการแชทถูกล้างทั้งหมดแล้ว!")
