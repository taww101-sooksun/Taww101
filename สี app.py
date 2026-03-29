import streamlit as st
import os
import time
import base64
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# ==========================================
# 1. ระบบพื้นฐาน & การตั้งค่าสี (3 ชุดสี)
# ==========================================
def init_system():
    if 'my_name' not in st.session_state: st.session_state.my_name = ""
    if 'active_room' not in st.session_state: st.session_state.active_room = "🚀 แกนหลัก"
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    
    # ชุดสี 3 รูปแบบ
    themes = {
        "🟢 Cyber Green": "#39FF14",
        "🔵 Marine Blue": "#00F3FF",
        "🔴 Warning Red": "#FF3131"
    }
    
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except: pass
    return themes

# ==========================================
# 2. ระบบแชต (สาธารณะ & ส่วนตัว)
# ==========================================
def room_comms():
    st.subheader("💬 ศูนย์สื่อสารระบบ")
    tab1, tab2 = st.tabs(["📢 กระดานสาธารณะ", "🔒 แชตส่วนตัว"])
    
    with tab1:
        st.write("--- กระดานข้อความกลาง ---")
        chat_ref = db.reference('public_chat')
        with st.form("pub_chat", clear_on_submit=True):
            msg = st.text_input("พิมพ์ข้อความลงกระดาน...")
            if st.form_submit_button("ส่งข้อความ"):
                if msg:
                    chat_ref.push({'user': st.session_state.my_name, 'msg': msg, 'ts': time.time()})
                    st.rerun()
        
        msgs = chat_ref.order_by_key().limit_to_last(15).get()
        if msgs:
            for m in reversed(list(msgs.values())):
                st.write(f"🟢 **{m.get('user')}:** {m.get('msg')}")

    with tab2:
        st.write("--- ข้อความเฉพาะกลุ่ม ---")
        target_user = st.text_input("ระบุชื่อผู้รับ (รหัสเรียกขาน):")
        private_ref = db.reference(f'private_chats/{st.session_state.my_name}')
        if target_user:
            with st.form("priv_chat", clear_on_submit=True):
                p_msg = st.text_input(f"ส่งถึง {target_user}:")
                if st.form_submit_button("ส่งส่วนตัว"):
                    db.reference(f'private_chats/{target_user}').push({
                        'from': st.session_state.my_name, 'msg': p_msg, 'ts': time.time()
                    })
                    st.success("ส่งแล้ว")
        
        # แสดงแชตที่มีคนส่งมาหาเรา
        p_msgs = private_ref.limit_to_last(10).get()
        if p_msgs:
            for pm in reversed(list(p_msgs.values())):
                st.warning(f"📩 **จาก {pm.get('from')}:** {pm.get('msg')}")

# ==========================================
# 3. ห้องพักผ่อน & รายชื่อเพลง
# ==========================================
def room_music():
    st.subheader("🎧 รายชื่อเพลงในระบบ")
    music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลงใน GitHub")
        return

    # แสดงรายการเพลงทั้งหมดให้เลือก
    for i, song in enumerate(music_files):
        if st.button(f"🎵 {i+1}. {song}", key=f"s_{i}"):
            st.session_state.song_index = i
            st.rerun()

    st.markdown("---")
    st.write(f"กำลังเล่น: **{music_files[st.session_state.song_index]}**")
    st.audio(music_files[st.session_state.song_index], autoplay=True)

# ==========================================
# 4. หน้าจอหลัก (Main UI)
# ==========================================
def main():
    themes = init_system()

    st.markdown(f"""
        <style>
        .stApp {{ background-color: #000000 !important; color: #FFFFFF !important; }}
        div.stButton > button {{
            width: 100%; border-radius: 12px; border: 2px solid {st.session_state.theme_color};
            background-color: rgba(0,0,0,0.5); color: {st.session_state.theme_color} !important;
            padding: 10px; font-weight: bold; box-shadow: 0 4px 0 {st.session_state.theme_color};
            transition: all 0.1s ease; margin-bottom: 8px;
        }}
        div.stButton > button:active {{ transform: translateY(3px); box-shadow: 0 1px 0 {st.session_state.theme_color}; }}
        </style>
        """, unsafe_allow_html=True)

    if st.session_state.my_name == "":
        # แสดงโลโก้ logo1.jpg
        if os.path.exists("logo1.jpg"):
            with open("logo1.jpg", "rb") as f:
                data = base64.b64encode(f.read()).decode()
                st.markdown(f'<center><img src="data:image/jpeg;base64,{data}" width="250" style="mix-blend-mode: screen; filter: drop-shadow(0 0 10px {st.session_state.theme_color});"></center>', unsafe_allow_html=True)
        
        st.title("🛰️ SYNAPSE LOGIN")
        name = st.text_input("รหัสเรียกขาน:")
        if st.button("เข้าสู่ระบบ"):
            if name: st.session_state.my_name = name; st.rerun()
        return

    with st.sidebar:
        st.title("⚙️ SETTINGS")
        selected_theme = st.selectbox("เลือกชุดสีระบบ:", list(themes.keys()))
        st.session_state.theme_color = themes[selected_theme]
        if st.button("Log out"): st.session_state.my_name = ""; st.rerun()

    # เมนูหลักปุ่มนูน
    cols = st.columns(2)
    with cols[0]:
        if st.button("🚀 แกนหลัก"): st.session_state.active_room = "🚀 แกนหลัก"
        if st.button("💬 การสื่อสาร"): st.session_state.active_room = "💬 การสื่อสาร"
    with cols[1]:
        if st.button("🛰️ เรดาร์"): st.session_state.active_room = "🛰️ เรดาร์"
        if st.button("🎧 ห้องพัก"): st.session_state.active_room = "🎧 ห้องพัก"

    st.markdown("---")
    
    if st.session_state.active_room == "🚀 แกนหลัก":
        st.subheader("🚀 ศูนย์ควบคุมแกนกลาง")
        st.write(f"รหัส: **{st.session_state.my_name}**")
        st.write('สโลแกน: **"อยู่นิ่งๆ ไม่เจ็บตัว"**')
    elif st.session_state.active_room == "💬 การสื่อสาร":
        room_comms()
    elif st.session_state.active_room == "🎧 ห้องพัก":
        room_music()
    # ... (ส่วนเรดาร์ใช้โค้ดเดิมได้เลยครับ)

if __name__ == "__main__":
    main()
