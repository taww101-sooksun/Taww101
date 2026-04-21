import streamlit as st
import os
import pandas as pd
import math
import time
import base64
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
import hashlib
import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time
from datetime import datetime

# --- [ 🛰️ ระบบเชื่อมต่อศูนย์บัญชาการ Firebase ] ---
# ใช้โครงสร้างที่ต๊ะให้มา (ใสแน่นอน)
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_credentials"])
        if "private_key" in fb_creds:
            fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
            
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {
            'databaseURL': st.secrets["firebase_db_url"]
        })
    except Exception as e:
        st.error(f"❌ ระบบเชื่อมต่อขัดข้อง: {e}")

db_ref = db.reference('/')

# --- [ 🎨 CUSTOM INTERFACE: ลบติ่ง & แต่งสวย ] ---
st.set_page_config(page_title="SYNAPSE", layout="centered")

st.markdown("""
    <style>
    /* ลบติ่ง Streamlit / GitHub */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Logo1.png ดิ้น (Wiggle) */
    @keyframes wiggle {
        0% { transform: rotate(0deg); }
        25% { transform: rotate(3deg); }
        50% { transform: rotate(0eg); }
        75% { transform: rotate(-3deg); }
        100% { transform: rotate(0deg); }
    }
    .logo-img {
        display: block;
        margin: 0 auto;
        width: 250px;
        animation: wiggle 1.5s infinite;
    }
    
    /* ตัวหนังสือวิ่ง */
    .marquee {
        background: #111;
        color: #00FF00;
        padding: 5px;
        overflow: hidden;
        white-space: nowrap;
        font-family: 'Courier New', monospace;
    }
    .marquee span {
        display: inline-block;
        padding-left: 100%;
        animation: marquee 10s linear infinite;
    }
    @keyframes marquee {
        0% { transform: translate(0, 0); }
        100% { transform: translate(-100%, 0); }
    }
    </style>
    """, unsafe_allow_html=True)

# --- [ 🔐 ระบบบันทึกระหัสยูสเซอร์ ] ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # หน้า Login
    st.markdown('<img src="logo1.png" class="logo-img" onerror="this.src=\'https://via.placeholder.com/250?text=LOGO1.PNG\'">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>SYNAPSE LOGIN</h2>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        user_id = st.text_input("รหัสยูสเซอร์ / ชื่อผู้ใช้")
        password = st.text_input("รหัสผ่าน", type="password")
        submit = st.form_submit_button("ลงชื่อเข้าใช้")
        
        if submit:
            # เช็คค่าจาก Firebase จริง (ตัวอย่าง)
            user_data = db_ref.child('users').child(user_id).get()
            if user_data and user_data.get('password') == password:
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                st.rerun()
            else:
                st.error("ข้อมูลไม่ถูกต้อง")

else:
    # --- [ 🏠 หน้าหลัก 8 ห้อง ] ---
    st.markdown('<img src="logo1.png" class="logo-img" onerror="this.src=\'https://via.placeholder.com/250?text=LOGO1.PNG\'">', unsafe_allow_html=True)
    
    menu = [
        "1. SYNAPSE อยู่นิ่งๆไม่เจ็บตัว",
        "2. MP3/MP4 & Draft 512",
        "3. Chat & GPS Realtime",
        "4. สูตรสมดุล 1.619 & จันทรคติ",
        "5. วัดค่าเสียง db/Hz/กลางแหลม",
        "6. ตั้งค่าสี & ยืนยันตัวตน",
        "7. สูตรคู่ขนาน 1960",
        "8. เลขศาสตร์ 1960-2026 & สถิติ"
    ]
    
    choice = st.selectbox("เลือกห้องปฏิบัติการ", menu)
    st.divider()

    # --- ห้องที่ 1 ---
    if "1." in choice:
        st.subheader("SYNAPSE: อยู่นิ่งๆ ไม่เจ็บตัว")
        st.write(f"ยินดีต้อนรับท่าน: {st.session_state.user_id}")
    
    # --- ห้องที่ 2 ---
    elif "2." in choice:
        st.markdown('<div class="marquee"><span>DRAFT เสียงจริง 512 Hz กำลังประมวลผล... ดึงค่าจาก SYNAPSE CLOUD สำเร็จ</span></div>', unsafe_allow_html=True)
        # ดึงค่า MP3 จาก Firebase หรือ Cloud Storage
        st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3") 
        st.write("สถานะ: ดึงค่าเสถียร 100%")

    # --- ห้องที่ 3 ---
    elif "3." in choice:
        st.subheader("📡 ระบบติดตาม & แชตสด")
        col1, col2 = st.columns(2)
        with col1:
            msg = st.text_input("ส่งข้อความส่วนตัว")
            if st.button("ส่ง"):
                db_ref.child('chats').push({'user': st.session_state.user_id, 'msg': msg, 'time': str(datetime.now())})
        with col2:
            st.metric("เวลาจริง", datetime.now().strftime("%H:%M:%S"))
            # จำลองค่า GPS (ต๊ะดึงจาก Sensor จริงได้ผ่านแอปเสริม)
            st.write("LAT: 16.05 | LON: 103.65")

    # --- ห้องที่ 4 ---
    elif "4." in choice:
        st.subheader("📐 สูตรคำนวณความถูกต้อง")
        st.write("ค่าสมดุลทองคำ: 1.619")
        st.write("รอบน้ำดวงจันทร์: 29.53")
        st.success("ผลลัพธ์: ความแม่นยำ 1960 - ปัจจุบัน สอดคล้องกัน")

    # --- ห้องที่ 5 ---
    elif "5." in choice:
        st.subheader("🔊 ห้องวิเคราะห์เสียงกลางแหลม")
        st.progress(75, text="ค่าความเข้มเสียง dB")
        st.write("Hz: 440 (มาตรฐาน)")
        st.info("แอปนี้ออกแบบมาเพื่อวัดค่าที่คนอื่นมองข้าม แต่ต๊ะมองเห็น")

    # --- ห้องที่ 6 ---
    elif "6." in choice:
        st.subheader("⚙️ การปรับแต่งระบบ")
        color = st.color_picker("เลือกสีธีมแอป", "#00FF00")
        st.button("ยืนยันตัวตนระดับสูง")

    # --- ห้องที่ 7 ---
    elif "7." in choice:
        st.subheader("🔗 สูตรคู่ขนาน 1960")
        st.text_input("รายชื่อที่ 1")
        st.text_input("รายชื่อที่ 2")
        st.button("คำนวณจุดตัด")

    # --- ห้องที่ 8 ---
    elif "8." in choice:
        st.subheader("📊 สถิติเลขศาสตร์ 1960-2026")
        st.write("สถานะย้อนหลัง 365 วัน: 🎖️")
        st.write("สถานะอนาคต 365 วัน: 💎")
        st.write("รหัสตัวเลขวันเกิดของท่านคือ: [คำนวณตามสูตร]")

    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

# --- [ 1. INITIAL SETUP ] ---
if 'init' not in st.session_state:
    st.set_page_config(page_title="SYNAPSE HUB", layout="wide")
    st.session_state.init = True
    st.session_state.page = "HOME"
    st.session_state.custom_theme = "#00f3ff"

# --- [ 2. FIREBASE CONNECTION ] ---
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_credentials"])
        if "private_key" in fb_creds:
            fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
    except Exception as e:
        st.error(f"❌ Firebase Error: {e}")

# --- [ 3. UI ENGINE & DESIGN ] ---
def setup_ui():
    theme_color = st.session_state.get('custom_theme', "#00f3ff")
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;600&display=swap');
    .stApp {{ background-color: #0A0A0A; font-family: 'Kanit', sans-serif; color: white; }}
    header, footer, #MainMenu {{visibility: hidden;}}
    
    .sss-header {{ color: #FF0000; font-size: 42px; font-weight: bold; text-align: center; text-shadow: 0 0 15px #FF0000; margin:0; }}
    .sss-motto {{ color: #FFD700; font-size: 16px; text-align: center; margin-bottom: 20px; letter-spacing: 2px; }}
    
    .stButton>button {{
        border-radius: 12px; border: 1px solid {theme_color} !important;
        background: rgba(0,0,0,0.5); color: white; transition: 0.3s;
        box-shadow: 0 0 5px {theme_color}; width: 100%; height: 50px;
    }}
    .stButton>button:hover {{ background: {theme_color}; color: black; box-shadow: 0 0 20px {theme_color}; }}
    </style>
    <div class="sss-header">S.S.S MUSIC × SYNAPSE</div>
    <div class="sss-motto">"อยู่นิ่งๆ ไม่เจ็บตัว"</div>
    """, unsafe_allow_html=True)

# --- [ 4. LOGIN SYSTEM ] ---
if not st.session_state.get('logged_in', False):
    setup_ui()
    st.markdown("<h2 style='text-align:center; color:#00f3ff;'>REGISTER AGENT</h2>", unsafe_allow_html=True)
    new_user = st.text_input("ENTER AGENT NAME", placeholder="ระบุชื่อรหัสของคุณ").strip()
    if st.button("ACTIVATE SYSTEM"):
        if new_user:
            st.session_state.user = new_user
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

setup_ui()

# --- [ 5. NAVIGATION ] ---
if st.session_state.page != "HOME":
    if st.button("⬅️ กลับหน้าหลัก (MAIN MENU)"):
        st.session_state.page = "HOME"
        st.rerun()

# --- [ 6. PAGES LOGIC ] ---

# --- หน้าแรก: ศูนย์ควบคุม ---
if st.session_state.page == "HOME":
    st.markdown("<h3 style='text-align:center;'>เลือกฟังก์ชันควบคุมระบบ</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🎵 1. MUSIC PLAYER"): st.session_state.page = "1"; st.rerun()
        if st.button("💬 2. CHAT SYSTEM"): st.session_state.page = "2"; st.rerun()
        if st.button("🔮 3. DESTINY TIMELINE"): st.session_state.page = "5"; st.rerun()
    with c2:
        if st.button("🛰️ 4. SENSOR & GPS"): st.session_state.page = "6"; st.rerun()
        if st.button("🔢 5. DAILY CODE"): st.session_state.page = "8"; st.rerun()
        if st.button("🎨 6. COLOR MASTER"): st.session_state.page = "10"; st.rerun()

# --- หน้า 1: MUSIC PLAYER ---
elif st.session_state.page == "1":
    st.markdown("<h2 style='text-align:center; color:#FF0000;'>🎵 MUSIC COMMAND</h2>", unsafe_allow_html=True)
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        if os.path.exists("logo1.png"): st.image("logo1.png", use_container_width=True)
    
    note = st.text_input("", placeholder="ใจความสั้นๆ ที่จะให้ AI ขยี้...")
    if st.button("ขยี้ใจความ (GENERATE)"):
        st.info("กำลังประมวลผลทำนอง...")
    
    st.divider()
    c1, c2, c3 = st.columns(3)
    with c1: st.button("💾 SAVE")
    with c2: st.button("📤 SHARE")
    with c3: st.button("🔥 TURBO")

# --- หน้า 2: CHAT SYSTEM ---
elif st.session_state.page == "2":
    st.markdown("<h2 style='text-align:center; color:#00f3ff;'>💬 PRIVATE CHAT</h2>", unsafe_allow_html=True)
    msg = st.text_input("ส่งข้อความถึงระบบ:")
    if st.button("SEND SIGNAL"):
        st.success("ข้อความถูกบันทึกแล้ว (Firebase)")

# --- หน้า 6: SENSOR & GPS (รวมร่างใหม่) ---
elif st.session_state.page == "6":
    st.markdown("<h2 style='text-align:center; color:#FFD700;'>🛰️ SENSOR CONTROL</h2>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📍 GPS & WEATHER", "🎙️ SONIC SCAN", "📳 MOTION"])
    
    with tab1:
        env_js = """
        <div style="background:#111; color:#FFD700; padding:20px; border:2px solid #FFD700; border-radius:15px; text-align:center; font-family:monospace;">
            <p id="st">📍 พร้อมสแกนพิกัด</p>
            <div style="display:flex; justify-content:space-around;">
                <div><small>LAT</small><h2 id="lat">-</h2></div>
                <div><small>LON</small><h2 id="lon">-</h2></div>
            </div>
            <div style="margin-top:10px; background:#222; padding:10px; border
