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
# 1. ระบบพื้นฐาน & ชุดสีรุ้ง 3 แบบ (แบบเก่า)
# ==========================================
def init_system():
    if 'my_name' not in st.session_state: st.session_state.my_name = ""
    if 'active_room' not in st.session_state: st.session_state.active_room = "🚀 แกนหลัก"
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    
    # ดึงชุดสีรุ้ง/นีออน 3 แบบเดิมกลับมา
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
# 2. ระบบแชต & กระดานข้อความ (แบบเก่า)
# ==========================================
def room_comms():
    st.subheader("💬 ศูนย์สื่อสาร SYNAPSE")
    chat_ref = db.reference('public_chat')
    
    # ส่วนพิมพ์ข้อความ
    with st.form("chat_form", clear_on_submit=True):
        msg = st.text_input("พิมพ์ข้อความแจ้งศูนย์...")
        if st.form_submit_button("SEND / ส่ง"):
            if msg:
                chat_ref.push({
                    'user': st.session_state.my_name, 
                    'msg': msg, 
                    'ts': time.time()
                })
                st.rerun()
    
    st.markdown("---")
    st.write("📋 กระดานข้อความล่าสุด:")
    # ดึงข้อความมาโชว์บนกระดาน
    msgs = chat_ref.order_by_key().limit_to_last(15).get()
    if msgs:
        for m in reversed(list(msgs.values())):
            st.info(f"👤 **{m.get('user')}:** {m.get('msg')}")

# ==========================================
# 3. แผนที่ดาวเทียม (Radar)
# ==========================================
def room_radar():
    st.subheader("🛰️ ระบบเรดาร์พิกัดดาวเทียม")
    loc = get_geolocation()
    
    # ค่าเริ่มต้นถ้า GPS ยังไม่มา
    lat, lon = 13.7367, 100.5231
    if loc and 'coords' in loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        st.success("📍 พิกัดดาวเทียมเสถียร")
    else:
        st.warning("🛰️ กำลังค้นหาสัญญาณดาวเทียม...")

    # แผนที่แบบ Satellite (ดาวเทียม)
    m = folium.Map(location=[lat, lon], zoom_start=16, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                   attr="Google Satellite")

    # ดึงพิกัดเพื่อนๆ มาโชว์
    all_users = db.reference('users').get()
    if all_users:
        for u_id, data in all_users.items():
            u_lat, u_lon = data.get('lat'), data.get('lon')
            if u_lat and u_lon:
                color = 'red' if u_id == st.session_state.my_name else 'green'
                folium.Marker([u_lat, u_lon], popup=u_id,
                              icon=folium.Icon(color=color, icon='info-sign')).add_to(m)

    st_folium(m, width="100%", height=450, key="radar_map")

    if loc and 'coords' in loc:
        if st.button("📡 กระจายพิกัดปัจจุบัน", use_container_width=True):
            db.reference(f'users/{st.session_state.my_name}').update({
                'lat': lat, 'lon': lon, 'ts': time.time()
            })
            st.toast("อัปเดตตำแหน่งแล้ว")

# ==========================================
# 4. ห้องพัก & รายชื่อเพลง
# ==========================================
def room_music():
    st.subheader("🎧 รายชื่อเพลงในระบบ")
    music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลง")
        return

    # แสดง Playlist ให้เลือกเพลง
    for i, song in enumerate(music_files):
        if st.button(f"🎵 {i+1}. {song}", key=f"song_{i}"):
            st.session_state.song_index = i
            st.rerun()

    st.markdown("---")
    st.write(f"กำลังเล่น: **{music_files[st.session_state.song_index]}**")
    st.audio(music_files[st.session_state.song_index], autoplay=True)

# ==========================================
# 5. หน้าจอหลัก (Main UI)
# ==========================================
def main():
    themes = init_system()

    # CSS ปุ่มนูน 3D และธีมมืด
    st.markdown(f"""
        <style>
        .stApp {{ background-color: #000000 !important; color: #FFFFFF !important; }}
        div.stButton > button {{
            width: 100%; border-radius: 12px; border: 2px solid {st.session_state.theme_color};
            background-color: rgba(0,0,0,0.4); color: {st.session_state.theme_color} !important;
            padding: 12px; font-weight: bold; box-shadow: 0 5px 0 {st.session_state.theme_color};
            transition: all 0.1s ease; margin-bottom: 10px;
        }}
        div.stButton > button:active {{ transform: translateY(4px); box-shadow: 0 1px 0 {st.session_state.theme_color}; }}
        </style>
        """, unsafe_allow_html=True)

    # หน้า Login (ดึงรูป logo1.jpg)
    if st.session_state.my_name == "":
        if os.path.exists("logo1.jpg"):
            with open("logo1.jpg", "rb") as f:
                data = base64.b64encode(f.read()).decode()
                # ลบขอบดำด้วย mix-blend-mode
                st.markdown(f'<center><img src="data:image/jpeg;base64,{data}" width="250" style="mix-blend-mode: screen; filter: drop-shadow(0 0 10px {st.session_state.theme_color});"></center>', unsafe_allow_html=True)
        
        st.title("🛰️ SYNAPSE LOGIN")
        name = st.text_input("รหัสเรียกขาน:")
        if st.button("ENTER"):
            if name: st.session_state.my_name = name; st.rerun()
        return

    # แถบข้างสำหรับเลือกชุดสี
    with st.sidebar:
        st.title("⚙️ SETTINGS")
        selected_theme = st.selectbox("เลือกชุดสีระบบ (สีรุ้ง):", list(themes.keys()))
        st.session_state.theme_color = themes[selected_theme]
        if st.button("Logout"): st.session_state.my_name = ""; st.rerun()

    # เมนูเลือกห้องแบบปุ่มนูน (Tab แบบเก่า)
    tabs = st.tabs(["🚀 แกนหลัก", "🛰️ เรดาร์", "💬 แชต", "🎧 เพลง"])
    
    with tabs[0]:
        st.subheader("🚀 ศูนย์ควบคุมแกนกลาง")
        st.write(f"รหัสผู้ใช้งาน: **{st.session_state.my_name}**")
        st.write('สโลแกน: **"อยู่นิ่งๆ ไม่เจ็บตัว"**')
        st.markdown("---")
        st.code(f"Time: {datetime.now().strftime('%H:%M:%S')}\nStatus: Active")
    
    with tabs[1]:
        room_radar()
        
    with tabs[2]:
        room_comms()
        
    with tabs[3]:
        room_music()

if __name__ == "__main__":
    main()
