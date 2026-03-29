import streamlit as st
import os 
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
    
    # --- แก้ไขเวลา GPS ให้ตรงพิกัด ---
    loc = get_geolocation()
    if loc and 'coords' in loc:
        lon = loc['coords']['longitude']
        lat = loc['coords']['latitude']
        
        # คำนวณเวลาตามพิกัดจริง (Solar Time Estimate)
        # ปกติ GMT+7 คือ 105 องศา, เราหาผลต่างเพื่อปรับเวลาให้ตรงจุดที่ยืน
        utc_now = datetime.utcnow()
        local_offset = lon / 15.0 # ทุก 15 องศาคือ 1 ชม.
        gps_time = utc_now + timedelta(hours=local_offset)
        
        st.markdown(f"""
            <div style='background: rgba(0,255,0,0.1); padding:15px; border-radius:10px; border-left: 5px solid {st.session_state.theme_color};'>
                🕰️ <b>เวลาพิกัดจริง (GPS):</b> {gps_time.strftime('%H:%M:%S')}<br>
                📍 <b>พิกัดดาวเทียม:</b> {lat:.4f}, {lon:.4f}
            </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.info("สถานะระบบ: ONLINE")
    st.write(f"รหัสเรียกขาน: **{st.session_state.my_name}**")
    st.write('สโลแกน: **"อยู่นิ่งๆ ไม่เจ็บตัว"**')

def room_music():
    st.subheader("🎧 ศูนย์ความบันเทิง (Auto-Next)")
    
    # ค้นหาไฟล์ทั้ง MP3 และ MP4
    media_files = sorted([f for f in os.listdir('.') if f.lower().endswith((".mp3", ".mp4"))])
    
    if not media_files:
        st.warning("⚠️ ไม่พบไฟล์สื่อในระบบ")
        return
    
    cur_idx = st.session_state.song_index
    cur_file = media_files[cur_idx]
    
    # แสดงผลตามชนิดไฟล์
    if cur_file.lower().endswith(".mp4"):
        st.video(cur_file, autoplay=True)
    else:
        # ถ้ามีรูปโลโก้ให้โชว์คู่กับเพลง
        logo_data = get_base64_img("logo1.jpg")
        if logo_data:
            st.markdown(f'<center><img src="data:image/jpeg;base64,{logo_data}" style="width:200px; mix-blend-mode: screen;"></center>', unsafe_allow_html=True)
        st.audio(cur_file, autoplay=True)

    st.markdown(f"📡 กำลังเล่น: **{cur_file}**")

    # ระบบเล่นต่อเนื่อง (Auto-Next JS)
    # ค้นหาทั้งแท็ก <video> และ <audio> ถ้าจบให้กดปุ่ม 'ถัดไป'
    js_auto = """
    <script>
    function setupAutoNext() {
        var media = window.parent.document.querySelector('video') || window.parent.document.querySelector('audio');
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
    setTimeout(setupAutoNext, 2000);
    </script>
    """
    components.html(js_auto, height=0)

    # ปุ่มควบคุม
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⏮️ ย้อนกลับ"):
            st.session_state.song_index = (cur_idx - 1) % len(media_files); st.rerun()
    with c2:
        if st.button("⏭️ ถัดไป"):
            st.session_state.song_index = (cur_idx + 1) % len(media_files); st.rerun()

# ==========================================
# 3. แผงวงจรหลัก (UI & Styling)
# ==========================================
def main():
    init_system()

    st.markdown(f"""
        <style>
        .stApp {{ background-color: #000000 !important; color: #FFFFFF !important; }}
        div.stButton > button {{
            width: 100%; border-radius: 12px; border: 2px solid {st.session_state.theme_color};
            background-color: rgba(0,0,0,0.4); color: {st.session_state.theme_color} !important;
            padding: 12px; font-weight: bold; box-shadow: 0 6px 0 {st.session_state.theme_color};
            transition: all 0.1s ease; margin-bottom: 10px;
        }}
        div.stButton > button:active {{ transform: translateY(4px); box-shadow: 0 1px 0 {st.session_state.theme_color}; }}
        </style>
        """, unsafe_allow_html=True)

    # โลโก้ logo1.jpg แบบไร้ขอบ
    logo_data = get_base64_img("logo1.jpg")
    if logo_data:
        st.markdown(f'<div style="text-align: center;"><img src="data:image/jpeg;base64,{logo_data}" style="width:220px; mix-blend-mode: screen; filter: drop-shadow(0 0 10px {st.session_state.theme_color});"></div>', unsafe_allow_html=True)

    # เมนูเลือกห้อง
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 แกนหลัก"): st.session_state.active_room = "🚀 แกนหลัก"
        if st.button("💬 การสื่อสาร"): st.session_state.active_room = "💬 การสื่อสาร"
    with c2:
        if st.button("🛰️ เรดาร์"): st.session_state.active_room = "🛰️ เรดาร์"
        if st.button("🎧 ห้องพัก"): st.session_state.active_room = "🎧 ห้องพัก"

    st.markdown("---")
    
    if st.session_state.active_room == "🚀 แกนหลัก":
        room_core()
    elif st.session_state.active_room == "🛰️ เรดาร์":
        from room_radar_module import room_radar # แยกไฟล์เรดาร์ไว้เพื่อความสะอาด
        room_radar()
    elif st.session_state.active_room == "🎧 ห้องพัก":
        room_music()

if __name__ == "__main__":
    main()
