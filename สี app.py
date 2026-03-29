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
# 1. กลไกกลาง (Core Engine)
# ==========================================
def init_system():
    # จัดการ session state สำหรับชื่อผู้ใช้และห้อง
    if 'my_name' not in st.session_state: st.session_state.my_name = ""
    if 'active_room' not in st.session_state: st.session_state.active_room = "🚀 แกนหลัก"
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
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
# 2. พื้นที่เก็บห้อง (Modules)
# ==========================================

def room_core():
    st.subheader(f"🚀 ศูนย์ควบคุม: {st.session_state.my_name}")
    st.info("สถานะระบบ: ONLINE")
    st.write(f"รหัสเรียกขาน: **{st.session_state.my_name}**")
    st.write('สโลแกน: **"อยู่นิ่งๆ ไม่เจ็บตัว"**')

def room_radar():
    st.subheader("🛰️ ระบบเรดาร์ระบุชื่อ (Real-time)")
    loc = get_geolocation()
    all_users = db.reference('users').get()
    
    lat, lon = 13.7367, 100.5231
    if loc and 'coords' in loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']

    # แผนที่ดาวเทียม
    m = folium.Map(location=[lat, lon], zoom_start=15, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                   attr="Google Satellite")

    if all_users:
        for u_id, data in all_users.items():
            u_lat, u_lon = data.get('lat'), data.get('lon')
            if u_lat and u_lon:
                # แก้ไข: ระบุชื่อบนหมุดแผนที่ (Tooltip & Popup)
                folium.Marker(
                    [u_lat, u_lon], 
                    tooltip=f"<b>{u_id}</b>", 
                    popup=u_id,
                    icon=folium.Icon(color='red' if u_id == st.session_state.my_name else 'green', icon='user')
                ).add_to(m)

    st_folium(m, width="100%", height=450, key="radar_map")

    if loc and st.button("📡 กระจายพิกัดระบุชื่อ", use_container_width=True):
        db.reference(f'users/{st.session_state.my_name}').update({
            'lat': lat, 'lon': lon, 'ts': time.time()
        })
        st.toast("อัปเดตตำแหน่งพิกัดแล้ว!")

def room_music():
    st.subheader("🎧 ห้องพักผ่อน (Auto-Next)")
    music_files = sorted([f for f in os.listdir('.') if f.lower().endswith((".mp3", ".mp4"))])
    
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์สื่อ")
        return
    
    cur_idx = st.session_state.song_index
    cur_file = music_files[cur_idx]
    
    # แสดงผลสื่อ
    if cur_file.lower().endswith(".mp4"):
        st.video(cur_file, autoplay=True)
    else:
        st.audio(cur_file, autoplay=True)
    
    st.markdown(f"📡 กำลังเล่น: **{cur_file}**")

    # แก้ไข: ระบบเล่นต่อเนื่อง (Auto-Next) แบบใหม่
    js_next = """
    <script>
    function checkEnd() {
        var media = window.parent.document.querySelector('audio') || window.parent.document.querySelector('video');
        if (media) {
            media.onended = function() {
                var btns = window.parent.document.querySelectorAll('button');
                for (var i=0; i<btns.length; i++) {
                    if (btns[i].innerText.includes('ถัดไป')) {
                        btns[i].click();
                        break;
                    }
                }
            };
        }
    }
    setTimeout(checkEnd, 2000);
    </script>
    """
    components.html(js_next, height=0)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("⏮️ ย้อนกลับ"):
            st.session_state.song_index = (cur_idx - 1) % len(music_files); st.rerun()
    with c2:
        if st.button("⏭️ ถัดไป"):
            st.session_state.song_index = (cur_idx + 1) % len(music_files); st.rerun()

# ==========================================
# 3. แผงวงจรหลัก (Switchboard & Login)
# ==========================================
def main():
    init_system()

    # CSS ปรับแต่งปุ่มและโลโก้
    st.markdown(f"""
        <style>
        .stApp {{ background-color: #000000 !important; color: #FFFFFF !important; }}
        div.stButton > button {{
            width: 100%; border-radius: 12px; border: 2px solid {st.session_state.theme_color};
            background-color: rgba(0,0,0,0.4); color: {st.session_state.theme_color} !important;
            padding: 12px; font-weight: bold; box-shadow: 0 5px 0 {st.session_state.theme_color};
            transition: all 0.1s ease;
        }}
        div.stButton > button:active {{ transform: translateY(4px); box-shadow: 0 1px 0 {st.session_state.theme_color}; }}
        </style>
        """, unsafe_allow_html=True)

    # แก้ไข: ระบบใส่ชื่อก่อนเข้าแอป (Login Page)
    if st.session_state.my_name == "":
        logo_data = get_base64_img("logo1.jpg")
        if logo_data:
            st.markdown(f'<center><img src="data:image/jpeg;base64,{logo_data}" style="width:250px; mix-blend-mode: screen;"></center>', unsafe_allow_html=True)
        
        st.title("🛰️ SYNAPSE LOGIN")
        name_input = st.text_input("ระบุรหัสเรียกขาน (Username):")
        if st.button("เข้าสู่ระบบ (ENTER)"):
            if name_input:
                st.session_state.my_name = name_input
                st.rerun()
        return

    # หน้าหลักแอป
    with st.sidebar:
        st.title("⚙️ SETTINGS")
        if st.button("Logout"): 
            st.session_state.my_name = ""
            st.rerun()

    # เมนูเลือกห้อง
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 แกนหลัก"): st.session_state.active_room = "🚀 แกนหลัก"
        if st.button("💬 การสื่อสาร"): st.session_state.active_room = "💬 การสื่อสาร"
    with c2:
        if st.button("🛰️ เรดาร์"): st.session_state.active_room = "🛰️ เรดาร์"
        if st.button("🎧 ห้องพัก"): st.session_state.active_room = "🎧 ห้องพัก"

    st.markdown("---")
    
    # รันห้องที่เลือก
    if st.session_state.active_room == "🚀 แกนหลัก": room_core()
    elif st.session_state.active_room == "🛰️ เรดาร์": room_radar()
    elif st.session_state.active_room == "🎧 ห้องพัก": room_music()
    # (เพิ่มห้องสื่อสารตามโค้ดเดิมของพี่ได้เลย)

if __name__ == "__main__":
    main()
