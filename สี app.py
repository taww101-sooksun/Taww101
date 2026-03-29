import streamlit as st
import os 
import random
import time
import base64
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# ==========================================
# 1. กลไกกลาง (Core Engine)
# ==========================================
def init_system():
    if 'my_name' not in st.session_state: st.session_state.my_name = "Ta101"
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

def get_base64_img(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# ==========================================
# 2. ระบบห้องและฟีเจอร์ใหม่
# ==========================================

def room_core():
    # --- ส่วนนาฬิกาจับพิกัด (นาฬิกาที่คำนวณเวลาตามตำแหน่ง) ---
    loc = get_geolocation()
    current_time = datetime.now()
    
    st.subheader("🚀 ศูนย์ควบคุมแกนกลาง")
    
    # คำนวณเวลาท้องถิ่นคร่าวๆ จาก Longitude (ทุก 15 องศาคือ 1 ชม.)
    if loc and 'coords' in loc:
        lon = loc['coords']['longitude']
        offset = round(lon / 15) - 7 # เทียบจากเวลาไทย (GMT+7)
        local_time = current_time + timedelta(hours=offset)
        st.success(f"🕰️ เวลาพิกัดปัจจุบัน: {local_time.strftime('%H:%M:%S')} (Offset: {offset:+d}h)")
        st.caption(f"📍 LAT: {loc['coords']['latitude']:.4f} | LON: {lon:.4f}")
    
    st.info("สถานะระบบ: ONLINE")
    st.write(f"รหัสผู้ใช้งาน: **{st.session_state.my_name}**")
    st.write('สโลแกน: **"อยู่นิ่งๆ ไม่เจ็บตัว"**')
    st.markdown("---")
    st.code(f"System Sync: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\nStatus: Ready")

def room_radar():
    st.subheader("🛰️ ระบบเรดาร์รวมกลุ่ม (ระบุชื่อบนหมุด)")
    loc = get_geolocation()
    all_users = db.reference('users').get()
    
    lat, lon = 13.7367, 100.5231
    if loc and 'coords' in loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']

    m = folium.Map(location=[lat, lon], zoom_start=15, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                   attr="Google Satellite")

    if all_users:
        for u_id, data in all_users.items():
            u_lat, u_lon = data.get('lat'), data.get('lon')
            if u_lat and u_lon:
                # ใส่ชื่อลงไปในหมุด (Tooltip โชว์ตลอด / Popup คลิกโชว์)
                folium.Marker(
                    [u_lat, u_lon],
                    popup=f"USER: {u_id}",
                    tooltip=f"<b>{u_id}</b>", # โชว์ชื่อตัวหนาบนหมุด
                    icon=folium.Icon(color='red' if u_id == st.session_state.my_name else 'green', icon='user')
                ).add_to(m)

    st_folium(m, width="100%", height=500, key="radar_main")

    if loc and st.button("📡 กระจายพิกัดระบุตัวตน", use_container_width=True):
        db.reference(f'users/{st.session_state.my_name}').update({
            'lat': lat, 'lon': lon, 'ts': time.time()
        })
        st.toast("ส่งพิกัดเข้าศูนย์บัญชาการแล้ว!")

# ==========================================
# 3. หน้าจอหลักและการแต่งสวย (UI/UX)
# ==========================================
def main():
    init_system()
    
    # CSS ชุดใหญ่: ปุ่ม 3D ยกสูง และธีมมืด
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {st.session_state.bg_color} !important; color: {st.session_state.text_color} !important; }}
        
        /* ปุ่มเมนูแบบยกสูง 3D ชัดเจน */
        div.stButton > button {{
            width: 100%; border-radius: 15px; border: 2px solid {st.session_state.theme_color};
            background-color: rgba(0,0,0,0.6); color: {st.session_state.theme_color} !important;
            padding: 15px; font-weight: bold; font-size: 18px;
            box-shadow: 0 8px 0 {st.session_state.theme_color}; /* ยกสูงขึ้น */
            transition: all 0.1s ease; margin-bottom: 15px;
        }}
        div.stButton > button:active {{
            transform: translateY(6px); /* ยุบลงเวลาคลิก */
            box-shadow: 0 2px 0 {st.session_state.theme_color};
        }}
        
        h1, h2, h3, p, span {{ color: {st.session_state.text_color} !important; }}
        </style>
        """, unsafe_allow_html=True)

    # --- ส่วนหัวและโลโก้ (logo1.jpg แบบไร้กรอบ) ---
    logo_data = get_base64_img("logo1.jpg")
    if logo_data:
        st.markdown(f'''
            <div style="text-align: center; padding: 20px;">
                <img src="data:image/jpeg;base64,{logo_data}" width="280" 
                     style="mix-blend-mode: screen; filter: drop-shadow(0 0 15px {st.session_state.theme_color});">
            </div>
        ''', unsafe_allow_html=True)
    
    # เมนูหลักแบบเดิม (ปุ่มกดแยก)
    c1, c2 = st.columns(2)
    with c1:
        btn_core = st.button("🚀 แกนหลัก")
        btn_comms = st.button("💬 การสื่อสาร")
    with c2:
        btn_radar = st.button("🛰️ เรดาร์")
        btn_music = st.button("🎧 ห้องพัก")

    # จัดการการเปลี่ยนหน้า
    if btn_core: st.session_state.active_room = "🚀 แกนหลัก"
    if btn_radar: st.session_state.active_room = "🛰️ เรดาร์"
    if btn_comms: st.session_state.active_room = "💬 การสื่อสาร"
    if btn_music: st.session_state.active_room = "🎧 ห้องพัก"

    st.markdown("---")

    # แสดงห้องตามที่เลือก
    if st.session_state.active_room == "🚀 แกนหลัก":
        room_core()
    elif st.session_state.active_room == "🛰️ เรดาร์":
        room_radar()
    elif st.session_state.active_room == "💬 การสื่อสาร":
        room_comms()
    elif st.session_state.active_room == "🎧 ห้องพัก":
        room_music()

    with st.sidebar:
        st.title("⚙️ SETTINGS")
        st.session_state.theme_color = st.color_picker("🚨 สีหลัก (นีออน)", st.session_state.theme_color)
        st.session_state.bg_color = st.color_picker("🌑 สีพื้นหลัง", st.session_state.bg_color)
        st.write(f'**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

if __name__ == "__main__":
    main()
