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
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from streamlit_autorefresh import st_autorefresh
import hashlib

# --- [ 1. CONFIG หน้าจอ - ห้ามซ้ำ! ] ---
st.set_page_config(page_title="SYNAPSE HUB", layout="wide", initial_sidebar_state="collapsed")

# --- [ 2. ระบบเชื่อมต่อศูนย์บัญชาการ Firebase ] ---
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

# --- [ 3. หัวใจคำนวณ: ระบบถอดรหัส Lunar ] ---
def get_detailed_logic(dt):
    if dt is None: return None
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    day_name = day_names[dt.weekday()]
    if pos <= 14.765:
        m_num = int(pos) + 1
        phase = f"ขึ้น {m_num} ค่ำ"
        res = math.sqrt((day_val**2) + (m_num**2))
        formula, logic_type = f"√({day_val}² + {m_num}²)", "Vector Energy"
    else:
        m_num = int(pos - 14.765) + 1
        phase = f"แรม {m_num} ค่ำ"
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula, logic_type = f"({day_val} × 1.618) / {m_num}", "Golden Ratio"
    return {"res": round(res, 4), "phase": phase, "day_name": day_name, "day_val": day_val, "m_num": m_num, "formula": formula, "type": logic_type}

# --- [ 4. CUSTOM UI & ลบติ่ง (อยู่นิ่งๆ ไม่เจ็บตัว) ] ---
def apply_custom_style():
    theme_color = st.session_state.get('custom_theme', "#00f3ff")
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Kanit:wght@300;600&display=swap');
        
        header, footer, #MainMenu {{visibility: hidden;}}
        .stApp {{ background-color: #000000; color: white; font-family: 'Kanit', sans-serif; }}
        
        /* Neon UI */
        .neon-text {{
            color: #fff;
            text-shadow: 0 0 10px {theme_color}, 0 0 20px {theme_color};
            text-align: center; font-family: 'Orbitron';
        }}
        .stButton>button {{
            border: 1px solid {theme_color} !important;
            background: rgba(0, 0, 0, 0.5);
            color: white; border-radius: 15px;
            box-shadow: 0 0 10px {theme_color};
            transition: 0.3s;
        }}
        .stButton>button:hover {{
            background: {theme_color} !important;
            color: black !important;
            box-shadow: 0 0 30px {theme_color};
        }}
        </style>
    """, unsafe_allow_html=True)

# --- [ 5. ระบบจัดการการเข้าถึง (Login/Register) ] ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    apply_custom_style()
    st.markdown("<h1 class='neon-text'>SYNAPSE AGENT</h1>", unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.image("logo1.png", use_container_width=True) if os.path.exists("logo1.png") else None
            agent_id = st.text_input("ENTER AGENT NAME", placeholder="ระบุชื่อของคุณ...").strip()
            
            if st.button("ACTIVATE SYSTEM", use_container_width=True):
                if agent_id:
                    # ตรวจสอบชื่อใน Firebase
                    user_ref = db.reference(f'users/{agent_id}')
                    user_data = user_ref.get()
                    
                    if not user_data:
                        # ลงทะเบียนใหม่ (Auto-Register)
                        user_ref.set({
                            'created_at': time.time(),
                            'status': 'active',
                            'theme': '#00f3ff'
                        })
                    
                    st.session_state.user = agent_id
                    st.session_state.logged_in = True
                    st.session_state.page = "HOME"
                    st.success(f"ACCESS GRANTED: {agent_id}")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.warning("กรุณาระบุรหัส AGENT")
    st.stop()

# --- [ 6. หน้าหลักศูนย์ควบคุม (HOME) ] ---
apply_custom_style()

if 'page' not in st.session_state:
    st.session_state.page = "HOME"

# ปุ่มย้อนกลับ
if st.session_state.page != "HOME":
    if st.button("⬅️ BACK TO COMMAND CENTER"):
        st.session_state.page = "HOME"
        st.rerun()

if st.session_state.page == "HOME":
    st.markdown(f"<h2 class='neon-text'>COMMAND CENTER: {st.session_state.user}</h2>", unsafe_allow_html=True)
    st.divider()

    c1, c2 = st.columns(2)
    apps = [
        ("🎵 1. MUSIC PLAYER", "1"), ("💬 2. CHAT & RADAR", "2"),
        ("🧬 3. SENSOR UNIT", "6"), ("🛰️ 4. PARALLEL SCAN", "4"),
        ("🔮 5. DESTINY TIMELINE", "5"), ("💖 6. DESTINY CHECK", "7"),
        ("🔢 7. DAILY CODE", "8"), ("📝 8. MEMORY LOG", "9"),
        ("🎨 9. COLOR MASTER", "10"), ("🚀 10. SYSTEM STATUS", "HOME")
    ]

    for i, (name, p_id) in enumerate(apps):
        target_col = c1 if i % 2 == 0 else c2
        if target_col.button(name, use_container_width=True):
            st.session_state.page = p_id
            st.rerun()

# --- [ 7. แต่ละห้อง (ย่อพอสังเขปเพื่อรันจริง) ] ---

# ห้อง 1: Music Mixer
elif st.session_state.page == "1":
    st.markdown("<h2 class='neon-text'>SYNAPSE MIXER</h2>", unsafe_allow_html=True)
    # ใส่โค้ด Mixer HTML/JS ที่ต๊ะมีได้เลย (ผมเว้นไว้เพื่อประหยัดเนื้อที่รัน)
    st.info("ระบบกำลังดึงไฟล์เสียง .mp3 จากคลังข้อมูล...")

# ห้อง 2: Chat & Radar
elif st.session_state.page == "2":
    st_autorefresh(interval=8000, key="chat_refresh")
    st.markdown("<h2 class='neon-text'>TACTICAL RADAR</h2>", unsafe_allow_html=True)
    # โค้ด Folium Map และ Firebase Chat
    st.write("📡 เรดาร์ตรวจพบผู้ใช้งานในพื้นที่...")

# ห้อง 6: Sensor (BPM, dB, G-Force)
elif st.session_state.page == "6":
    st.markdown("<h2 class='neon-text'>VIBRATION & BIO UNIT</h2>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🎙️ AUDIO SCAN", "📳 MOTION"])
    with tab1:
        st.write("วัดค่าเสียงจริง (dB / Hz)")
        # ใส่ components.html(audio_js) ตรงนี้

# ห้อง 8: Daily Code
elif st.session_state.page == "8":
    st.markdown("<h2 class='neon-text'>DAILY SECURITY CODE</h2>", unsafe_allow_html=True)
    today = date.today().strftime("%Y-%m-%d")
    raw = f"{today}_{st.session_state.user}_SYNAPSE"
    h = hashlib.sha256(raw.encode()).hexdigest()
    st.metric("PIN (4 DIGIT)", str(int(h[:4], 16))[-4:].zfill(4))

# ห้อง 10: Color Master
elif st.session_state.page == "10":
    st.markdown("<h2 class='neon-text'>COLOR MASTER</h2>", unsafe_allow_html=True)
    new_c = st.color_picker("ปรับรังสีระบบ", st.session_state.get('custom_theme', '#00f3ff'))
    if st.button("SAVE COLOR"):
        st.session_state.custom_theme = new_c
        st.rerun()
