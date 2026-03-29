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
# 1. ระบบพื้นฐาน (Core Engine)
# ==========================================
def init_system():
    if 'my_name' not in st.session_state: st.session_state.my_name = ""
    if 'active_room' not in st.session_state: st.session_state.active_room = "🚀 แกนหลัก"
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'text_color' not in st.session_state: st.session_state.text_color = "#FFFFFF"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
        
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except: pass

# ==========================================
# 2. ฟังก์ชันแต่ละห้อง (Modules)
# ==========================================

def room_core():
    st.subheader(f"🚀 ศูนย์ควบคุมแกนกลาง")
    st.info("สถานะระบบ: ONLINE")
    st.write(f"รหัสผู้ใช้งาน: **{st.session_state.my_name}**")
    st.write('สโลแกน: **"อยู่นิ่งๆ ไม่เจ็บตัว"**')
    st.markdown("---")
    st.write("📊 สถิติระบบวันนี้:")
    st.code(f"Time: {datetime.now().strftime('%H:%M:%S')}\nUser: {st.session_state.my_name}\nStatus: Active")

def room_radar():
    st.subheader("🛰️ ระบบเรดาร์รวมกลุ่ม")
    loc = get_geolocation()
    all_users = db.reference('users').get()
    
    # กัน Error ถ้า GPS ยังไม่มา
    lat, lon = 13.7367, 100.5231
    if loc and 'coords' in loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        st.success("📍 สัญญาณพิกัดเสถียร")
    else:
        st.info("🛰️ กำลังรอสัญญาณดาวเทียม...")

    m = folium.Map(location=[lat, lon], zoom_start=15, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                   attr="Google Satellite")

    if all_users:
        for u_id, data in all_users.items():
            u_lat, u_lon = data.get('lat'), data.get('lon')
            if u_lat and u_lon:
                color = 'red' if u_id == st.session_state.my_name else 'green'
                folium.Marker([u_lat, u_lon], tooltip=u_id,
                              icon=folium.Icon(color=color, icon='user')).add_to(m)

    st_folium(m, width="100%", height=400, key="radar_map")

    if loc and 'coords' in loc:
        if st.button("📡 กระจายพิกัดเข้าศูนย์บัญชาการ", use_container_width=True):
            db.reference(f'users/{st.session_state.my_name}').update({
                'lat': lat, 'lon': lon, 'ts': time.time()
            })
            st.rerun()

def room_music():
    st.subheader("🎧 ห้องพักผ่อน (Auto-Next)")
    music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลงใน GitHub")
        return
    
    cur_idx = st.session_state.song_index
    st.audio(music_files[cur_idx], autoplay=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏮️ เพลงก่อนหน้า"):
            st.session_state.song_index = (cur_idx - 1) % len(music_files); st.rerun()
    with col2:
        if st.button("⏭️ เพลงถัดไป"):
            st.session_state.song_index = (cur_idx + 1) % len(music_files); st.rerun()

    # JS สั่งกดปุ่ม "เพลงถัดไป" อัตโนมัติเมื่อเพลงจบ
    js_next = """<script>var check = setInterval(function() { var audio = window.parent.document.querySelector('audio'); if (audio) { audio.onended = function() { var btns = window.parent.document.querySelectorAll('button'); for (var i=0; i<btns.length; i++) { if (btns[i].innerText.includes('เพลงถัดไป')) { btns[i].click(); break; } } }; clearInterval(check); } }, 1000);</script>"""
    components.html(js_next, height=0)

# ==========================================
# 3. หน้าจอหลัก (Main UI)
# ==========================================
def main():
    init_system()

    # CSS ปรับแต่งธีมและปุ่มนูน 3D
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {st.session_state.bg_color} !important; color: {st.session_state.text_color} !important; }}
        div.stButton > button {{
            width: 100%; border-radius: 12px; border: 2px solid {st.session_state.theme_color};
            background-color: rgba(0,0,0,0.2); color: {st.session_state.theme_color} !important;
            padding: 12px; font-weight: bold; box-shadow: 0 5px 0 {st.session_state.theme_color};
            transition: all 0.1s ease; margin-bottom: 10px;
        }}
        div.stButton > button:active {{ transform: translateY(4px); box-shadow: 0 1px 0 {st.session_state.theme_color}; }}
        h1, h2, h3, p, span {{ color: {st.session_state.text_color} !important; }}
        </style>
        """, unsafe_allow_html=True)

    # --- หน้า Login (แสดงโลโก้ logo1.jpg) ---
    if st.session_state.my_name == "":
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ดึงรูป logo1.jpg มาโชว์แบบลบขอบดำ
        if os.path.exists("logo1.jpg"):
            with open("logo1.jpg", "rb") as f:
                data = base64.b64encode(f.read()).decode()
                # ใช้ mix-blend-mode: screen เพื่อลบพื้นหลังสีดำออกให้เนียนตา
                st.markdown(f'''
                    <div style="text-align: center; margin-bottom: 20px;">
                        <img src="data:image/jpeg;base64,{data}" width="280" 
                             style="mix-blend-mode: screen; filter: drop-shadow(0 0 15px {st.session_state.theme_color});">
                    </div>
                ''', unsafe_allow_html=True)
        
        st.title("🛰️ SYNAPSE LOGIN")
        name = st.text_input("ระบุรหัสเรียกขานของท่าน:")
        if st.button("เข้าสู่ระบบ"):
            if name: st.session_state.my_name = name; st.rerun()
        return

    # --- เมนูควบคุมหลัง Login ---
    with st.sidebar:
        st.title("⚙️ SETTINGS")
        st.session_state.theme_color = st.color_picker("🚨 สีนีออน", st.session_state.theme_color)
        if st.button("Logout"): st.session_state.my_name = ""; st.rerun()

    # ปุ่มเมนูหลัก 3D
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 แกนหลัก"): st.session_state.active_room = "🚀 แกนหลัก"
    with c2:
        if st.button("🛰️ เรดาร์"): st.session_state.active_room = "🛰️ เรดาร์"
    
    c3, c4 = st.columns(2)
    with c3:
        if st.button("💬 การสื่อสาร"): st.session_state.active_room = "💬 การสื่อสาร"
    with c4:
        if st.button("🎧 ห้องพัก"): st.session_state.active_room = "🎧 ห้องพัก"

    st.markdown("---")
    
    # รันห้องที่เลือก
    rooms = {"🚀 แกนหลัก": room_core, "🛰️ เรดาร์": room_radar, "💬 การสื่อสาร": room_core, "🎧 ห้องพัก": room_music}
    rooms[st.session_state.active_room]()

if __name__ == "__main__":
    main()
