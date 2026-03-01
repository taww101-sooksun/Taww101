import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time
import os

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="SYNAPSE ROOMS", layout="wide")

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00f2fe" 

with st.sidebar:
    st.markdown("### 🎨 ปรับแต่งสีระบบ")
    picked_color = st.color_picker("เลือกสีนีออนของคุณ", st.session_state.theme_color)
    st.session_state.theme_color = picked_color
    st.write(f"สีปัจจุบัน: {picked_color}")
    st.write("---")
    st.write('**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; }}
    .chat-box {{ 
        border: 1px solid {st.session_state.theme_color}; 
        padding: 10px; border-radius: 10px; margin-bottom: 5px;
        background: rgba(255,255,255,0.05);
    }}
    .stButton>button {{ 
        border: 1px solid {st.session_state.theme_color} !important; 
        color: {st.session_state.theme_color} !important; 
        background-color: transparent !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. FIREBASE ---
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

# --- 3. LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color};'>🔐 SYNAPSE LOGIN</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        u_id = st.text_input("ชื่อโค้ดเนม (ID)")
        u_pw = st.text_input("รหัสผ่าน", type="password")
        if st.button("UNLOCK SYSTEM"):
            if u_pw == "9999999" and u_id:
                st.session_state.logged_in = True
                st.session_state.user_id = u_id
                st.rerun()
            else:
                st.error("ACCESS DENIED")
    st.stop()

# --- 4. CHAT ROOMS ---
st.markdown(f"<h2 style='text-align:center;'>💬 COMMAND: {st.session_state.user_id}</h2>", unsafe_allow_html=True)

chat_rooms = ["🌐 ทั่วไป", "🔒 ลับเฉพาะ", "🎮 บันเทิง", "🛰️ ปฏิบัติการ"]
selected_room = st.selectbox("เลือกห้อง:", chat_rooms)
room_key = selected_room.replace("🌐 ", "").replace("🔒 ", "").replace("🎮 ", "").replace("🛰️ ", "")

with st.container():
    msg = st.text_input(f"ข้อความ ({selected_room}):", key="chat_input")
    if st.button("TRANSMIT 🚀"):
        if msg:
            db.reference(f'chats/{room_key}').push({
                'user': st.session_state.user_id,
                'msg': msg,
                'ts': time.time(),
                'color': st.session_state.theme_color
            })
            st.rerun()

raw_msgs = db.reference(f'chats/{room_key}').get()
if raw_msgs:
    sorted_msgs = sorted(raw_msgs.values(), key=lambda x: x['ts'], reverse=True)
    for m in sorted_msgs[:15]:
        st.markdown(f'<div class="chat-box"><b style="color:{m.get("color", "#fff")};">{m["user"]}:</b> {m["msg"]}</div>', unsafe_allow_html=True)

if st.sidebar.button("LOGOUT"):
    st.session_state.logged_in = False
    st.rerun()
