import streamlit as st
import os 
import random
import time
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import hashlib
from math import radians, cos, sin, asin, sqrt

# ==========================================
# 0. ฟังก์ชันเสริม (Helper Functions)
# ==========================================
def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_pass(password, hashed_pw):
    return hash_pass(password) == hashed_pw

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 
    return c * r

# 🔒 ฟังก์ชันสร้าง ID ห้องแชตส่วนตัว (แก้ Error NameError)
def get_chat_id(user1, user2):
    users = sorted([str(user1), str(user2)])
    return f"private_{users[0]}_{users[1]}"

# ==========================================
# 1. ระบบยืนยันตัวตน (Auth System)
# ==========================================
def auth_system():
    st.markdown(f"<h2 style='text-align:center; color:{st.session_state.theme_color};'>🔐 SYNAPSE ACCESS</h2>", unsafe_allow_html=True)
    auth_tab = st.tabs(["เข้าสู่ระบบ", "ลงทะเบียน"])
    
    with auth_tab[0]: # Login
        with st.form("login_form"):
            user_in = st.text_input("Username")
            pass_in = st.text_input("Password", type="password")
            if st.form_submit_button("LOGIN", use_container_width=True):
                user_data = db.reference(f'users/{user_in}').get()
                if user_data and check_pass(pass_in, user_data.get('password')):
                    st.session_state.user = user_in
                    st.session_state.logged_in = True
                    st.success("กำลังเข้าสู่ระบบ...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("ชื่อผู้ใช้หรือรหัสผ่านผิดพลาด")

    with auth_tab[1]: # Register
        with st.form("reg_form"):
            new_user = st.text_input("สร้าง Username (อังกฤษเท่านั้น)")
            new_pass = st.text_input("สร้าง Password", type="password")
            conf_pass = st.text_input("ยืนยัน Password", type="password")
            if st.form_submit_button("REGISTER", use_container_width=True):
                if new_pass != conf_pass: st.warning("รหัสผ่านไม่ตรงกัน")
                elif len(new_user) < 3: st.warning("Username สั้นเกินไป")
                else:
                    exists = db.reference(f'users/{new_user}').get()
                    if exists: st.error("ชื่อนี้ถูกใช้งานแล้ว")
                    else:
                        db.reference(f'users/{new_user}').set({
                            'password': hash_pass(new_pass),
                            'created_at': time.time()
                        })
                        st.success("ลงทะเบียนสำเร็จ!")

# ==========================================
# 2. กลไกกลาง (Core Engine)
# ==========================================
def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'text_color' not in st.session_state: st.session_state.text_color = "#FFFFFF"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user' not in st.session_state: st.session_state.user = ""
        
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ Firebase Error: {e}")

# ==========================================
# 3. ห้องต่างๆ (Rooms)
# ==========================================
def room_core():
    st.subheader("🚀 ศูนย์ควบคุมแกนกลาง")
    now = datetime.utcnow() + timedelta(hours=7)
    st.info(f"สถานะระบบ: ONLINE | ผู้ใช้: {st.session_state.user}")
    st.write(f"เวลาปัจจุบัน: {now.strftime('%H:%M:%S')}")

def room_radar():
    st.subheader("🛰️ เรดาร์ตรวจจับพิกัด")
    loc = get_geolocation()
    my_lat, my_lon = 13.7367, 100.5231 
    if loc: my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']
    
    m = folium.Map(location=[my_lat, my_lon], zoom_start=14)
    folium.Marker([my_lat, my_lon], tooltip="คุณ", icon=folium.Icon(color='red')).add_to(m)
    st_folium(m, width="100%", height=400)

def room_comms():
    st.subheader("💬 ศูนย์สื่อสาร SYNAPSE")
    t1, t2, t3 = st.tabs(["🌐 Lobby", "🔒 Private", "📞 Video Call"])
    
    with t1: # Lobby
        chat_ref = db.reference('public_chat')
        with st.form("chat_f", clear_on_submit=True):
            msg = st.text_input("ข้อความสาธารณะ...")
            if st.form_submit_button("SEND") and msg:
                chat_ref.push({'user': st.session_state.user, 'msg': msg, 'ts': time.time()})
        
    with t2: # Private Chat (จุดที่เคย Error)
        all_u = db.reference('users').get()
        if all_u:
            friends = [uid for uid in all_u.keys() if uid != st.session_state.user]
            target = st.selectbox("คุยกับใคร:", [""] + friends, key="p_select")
            if target:
                c_id = get_chat_id(st.session_state.user, target)
                p_ref = db.reference(f'private_chats/{c_id}')
                with st.form("p_form", clear_on_submit=True):
                    p_msg = st.text_input("ข้อความลับ...")
                    if st.form_submit_button("SEND PRIVATE") and p_msg:
                        p_ref.push({'sender': st.session_state.user, 'msg': p_msg, 'ts': time.time()})
                # แสดงแชต
                msgs = p_ref.order_by_key().limit_to_last(10).get()
                if msgs:
                    for m in reversed(list(msgs.values())):
                        st.write(f"**{m['sender']}:** {m['msg']}")

    with t3: # Video Call
        st.write("ระบบ Video Call พร้อมใช้งาน (PeerJS)")

def room_music():
    st.subheader("🎧 เพลง")
    st.write("รายการเพลงในเครื่อง...")

def room_sensor():
    st.subheader("📟 วัดเสียง")
    st.write("Sensor Ready...")

def room_mission():
    st.subheader("📝 ภารกิจ")
    st.write("บันทึกภารกิจ...")

def room_bio_sensor():
    st.subheader("🩺 ตรวจร่างกาย")
    st.write("Bio Sensor Ready...")

# ==========================================
# 4. แผงวงจรหลัก (Main)
# ==========================================
def main():
    init_system()

    st.markdown(f"""
        <style>
        .stApp {{ background-color: {st.session_state.bg_color}; }}
        h1, h2, h3, p, span, label {{ color: {st.session_state.text_color} !important; }}
        </style>
    """, unsafe_allow_html=True)

    if not st.session_state.logged_in:
        auth_system()
        return

    with st.sidebar:
        st.title(f"👤 {st.session_state.user}")
        if st.button("🚪 LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()
        st.markdown("---")
        st.session_state.theme_color = st.color_picker("🚨 สีหลัก", st.session_state.theme_color)
        st.write('**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

    room_map = {
        "🚀 แกนหลัก": room_core, "🛰️ เรดาร์": room_radar, "💬 สื่อสาร": room_comms,
        "🎧 เพลง": room_music, "📟 วัดเสียง": room_sensor, "📝 ภารกิจ": room_mission, "🩺 ตรวจร่างกาย": room_bio_sensor,
    }
    
    tabs = st.tabs(list(room_map.keys()))
    for i, (name, room_func) in enumerate(room_map.items()):
        with tabs[i]: room_func()

if __name__ == "__main__":
    main()
