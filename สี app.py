import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import pytz
import os
import time
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. SETUP & THEME (จากภาพที่คุณรัน)
# ==========================================
st.set_page_config(page_title="SYNAPSE ULTIMATE", layout="wide")
st_autorefresh(interval=5000, key="global_refresh")

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00f2fe" 

with st.sidebar:
    st.markdown("### 🎨 ปรับแต่งสีระบบ")
    st.session_state.theme_color = st.color_picker("เลือกสีนีออนของคุณ", st.session_state.theme_color)
    st.write('**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

st.markdown(f"""
    <style>
    .stApp {{ background: radial-gradient(circle, #001 0%, #000 100%); color: {st.session_state.theme_color}; font-family: 'Courier New', Courier, monospace; }}
    .neon-header {{ 
        font-size: 35px; font-weight: 900; text-align: center;
        color: #fff; text-shadow: 0 0 10px {st.session_state.theme_color}, 0 0 20px #ff00de;
        border: 2px solid {st.session_state.theme_color}; padding: 10px; background: rgba(0,0,0,0.8);
        border-radius: 10px; margin-bottom: 20px; letter-spacing: 10px;
    }}
    .terminal-container {{
        border: 1px solid {st.session_state.theme_color}; padding: 15px; border-radius: 8px;
        background: rgba(0, 242, 254, 0.05); border-left: 5px solid #ff00de;
        margin-bottom: 20px;
    }}
    .clock-box {{
        background: rgba(0,0,0,0.6); border: 1px solid {st.session_state.theme_color};
        padding: 10px; border-radius: 8px; text-align: center;
    }}
    .clock-time {{ color: #ff00de; font-size: 20px; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FIREBASE CONNECTION
# ==========================================
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_dict = dict(st.secrets["firebase"])
            if "private_key" in fb_dict:
                fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            creds = credentials.Certificate(fb_dict)
            firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except Exception as e:
        st.error(f"DATABASE ERROR: {e}")

# ==========================================
# 3. UI: WORLD CLOCK (แสดงตามภาพ)
# ==========================================
st.markdown('<div class="neon-header">SYNAPSE</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
zones = {'BANGKOK': 'Asia/Bangkok', 'NEW YORK': 'America/New_York', 'LONDON': 'Europe/London', 'TOKYO': 'Asia/Tokyo'}
for col, (city, zone) in zip([c1, c2, c3, c4], zones.items()):
    now = datetime.datetime.now(pytz.timezone(zone)).strftime('%H:%M:%S')
    col.markdown(f"<div class='clock-box'><small>{city}</small><br><span class='clock-time'>{now}</span></div>", unsafe_allow_html=True)

# ==========================================
# 4. MAIN NAVIGATION (Tabs)
# ==========================================
tabs = st.tabs(["🚀 แกนหลัก", "🛰️ เรดาร์", "💬 การสื่อสาร", "📊 บันทึก", "🔐 SEC", "📺 สื่อ", "🧹 ระบบ"])

# --- TAB 1: CORE (ตั้งชื่อ Agent) ---
with tabs[0]:
    user_id = st.text_input("USER CODENAME:", value=st.session_state.get('user_id', 'Agent_001'))
    st.session_state.user_id = user_id

# --- TAB 3: COMMS (เพิ่มแชตส่วนตัว) ---
with tabs[2]:
    st.markdown('<div class="terminal-container">[ SECURE_COMMS ]</div>', unsafe_allow_html=True)
    
    # ดึงรายชื่อคนออนไลน์จาก Firebase เพื่อเลือกคนคุยด้วย
    all_users = db.reference('users').get()
    user_list = ["🌐 Global Chat"]
    if all_users:
        user_list += [u for u in all_users.keys() if u != st.session_state.user_id]
    
    chat_target = st.selectbox("เลือกผู้รับสาร:", user_list)
    
    # กำหนด Room Key
    if chat_target == "🌐 Global Chat":
        room_path = 'global_chat'
    else:
        # สร้างห้องลับเฉพาะ (เรียงชื่อตามตัวอักษรเพื่อให้ทั้งสองคนเข้าห้องเดียวกัน)
        ids = sorted([st.session_state.user_id, chat_target])
        room_path = f'private_chats/{ids[0]}_{ids[1]}'

    with st.form("chat_form", clear_on_submit=True):
        msg = st.text_input(f"ส่งข้อมูลถึง {chat_target}:")
        if st.form_submit_button("TRANSMIT 🚀") and msg:
            db.reference(room_path).push({
                'user': st.session_state.user_id,
                'msg': msg,
                'ts': time.time(),
                'color': st.session_state.theme_color
            })
    
    # แสดงข้อความ
    chat_data = db.reference(room_path).get()
    if chat_data:
        sorted_chat = sorted(chat_data.values(), key=lambda x: x.get('ts', 0), reverse=True)
        for m in sorted_chat[:10]:
            st.markdown(f"📌 <b style='color:{m.get('color', '#fff')}'>{m.get('user')}</b>: {m.get('msg')}", unsafe_allow_html=True)

# --- TAB 7: SYS ---
with tabs[6]:
    if st.button("🔥 WIPE ALL"):
        db.reference('users').delete()
        db.reference('global_chat').delete()
        db.reference('private_chats').delete()
        st.success("SYSTEM CLEARED")
