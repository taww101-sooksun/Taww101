import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time
import os

# --- 1. SET UP & THEME SELECTOR ---
st.set_page_config(page_title="SYNAPSE ROOMS", layout="wide")

# ระบบเลือกสี (Color/Theme Selector)
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00f2fe" # สีเริ่มต้น (Neon Blue)

with st.sidebar:
    st.markdown("### 🎨 ปรับแต่งสีระบบ")
    picked_color = st.color_picker("เลือกสีนีออนของคุณ", st.session_state.theme_color)
    st.session_state.theme_color = picked_color
    st.write(f"สีปัจจุบัน: {picked_color}")
    st.write("---")
    st.write('**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

# ใช้ CSS ฉีดสีตามที่ผู้ใช้เลือก
st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; }}
    .chat-box {{ 
        border: 1px solid {st.session_state.theme_color}; 
        padding: 10px; border-radius: 10px; margin-bottom: 5px;
        background: rgba(255,255,255,0.05);
    }}
    .stButton>button {{ border: 1px solid {st.session_state.theme_color} !important; color: {st.session_state.theme_color} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. FIREBASE CONNECTION ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_dict = dict(st.secrets["firebase"])
            if "private_key" in fb_dict:
                fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            creds = credentials.Certificate(fb_dict)
            firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except Exception as e:
        st.error(f"เชื่อมต่อฐานข้อมูลไม่ได้: {e}")

# --- 3. LOGIN SYSTEM ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color};'>🔐 SYNAPSE LOGIN</h1>", unsafe_allow_html=True)
    with st.center(): # จัดให้อยู่กลางหน้าจอ
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            u_id = st.text_input("ชื่อโค้ดเนม (ID)")
            u_pw = st.text_input("รหัสผ่าน", type="password")
            if st.button("เข้าสู่ระบบ"):
                if u_pw == "9999999" and u_id:
                    st.session_state.logged_in = True
                    st.session_state.user_id = u_id
                    st.rerun()
                else:
                    st.error("รหัสไม่ถูกต้อง หรือลืมใส่ชื่อ")
    st.stop()

# --- 4. MULTI-ROOM CHAT SYSTEM ---
st.markdown(f"<h2 style='text-align:center;'>💬 SYNAPSE COMMAND CENTER</h2>", unsafe_allow_html=True)

# เลือกห้องแชต
chat_rooms = ["🌐 ทั่วไป", "🔒 ลับเฉพาะ", "🎮 บันเทิง/เกม", "🛰️ ปฏิบัติการ"]
selected_room = st.selectbox("เลือกห้องแชต:", chat_rooms)

# แปลงชื่อห้องเป็น Key ของ Firebase
room_key = selected_room.replace(" ", "_").replace("🌐_", "").replace("🔒_", "").replace("🎮_", "").replace("🛰️_", "")

# ส่วนการพิมพ์ข้อความ
with st.container():
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        msg = st.text_input(f"ส่งข้อความไปที่ห้อง {selected_room}:", key="chat_input")
    with col_btn:
        if st.button("ส่ง 🚀"):
            if msg:
                db.reference(f'chats/{room_key}').push({
                    'user': st.session_state.user_id,
                    'msg': msg,
                    'ts': time.time(),
                    'color': st.session_state.theme_color
                })
                st.rerun()

# แสดงข้อความในห้องที่เลือก
st.write(f"--- กำลังคุยในห้อง: {selected_room} ---")
raw_msgs = db.reference(f'chats/{room_key}').get()

if raw_msgs:
    # เรียงข้อความล่าสุดไว้ล่างสุด (หรือบนสุดตามชอบ)
    sorted_msgs = sorted(raw_msgs.values(), key=lambda x: x['ts'], reverse=True)
    for m in sorted_msgs[:20]: # โชว์ 20 ข้อความล่าสุด
        user_color = m.get('color', st.session_state.theme_color)
        st.markdown(f"""
            <div class="chat-box">
                <b style="color:{user_color};">{m['user']}:</b> {m['msg']}
            </div>
        """, unsafe_allow_html=True)
else:
    st.write("ยังไม่มีข้อความในห้องนี้... ประเดิมเลยเพื่อน!")

# --- 5. FOOTER ---
if st.sidebar.button("ออกจากระบบ"):
    st.session_state.logged_in = False
    st.rerun()
