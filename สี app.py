import streamlit as st
import os  # ป้องกัน NameError
import random
import time
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
    # ตั้งค่าธีมเริ่มต้น
    if 'theme_color' not in st.session_state:
        st.session_state.theme_color = "#39FF14"
    if 'song_index' not in st.session_state:
        st.session_state.song_index = 0
        
    # เชื่อมต่อ Firebase (ใช้ค่าจาก Secrets)
    if not firebase_admin._apps:
        try:
            # ตรวจสอบชื่อ Key ใน Secrets ของพี่ให้ตรงกันนะครับ
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_db_url"]
            })
        except Exception as e:
            st.error(f"🛰️ Firebase Connection Error: {e}")

def save_log(action):
    try:
        now = datetime.now()
        db.reference(f'synapse_logs/{now.strftime("%Y-%m-%d")}').push({
            'time': now.strftime("%H:%M:%S"),
            'action': action,
            'user': 'Ta101'
        })
    except: pass

# ==========================================
# 2. พื้นที่เก็บห้อง (The Rooms / Modules)
# ==========================================

def room_core():
    st.subheader("🚀 ศูนย์ควบคุมแกนกลาง")
    st.info("สถานะระบบ: ONLINE")
    st.write(f"รหัสผู้ใช้งาน: **Ta101**")
    st.write('สโลแกน: "อยู่นิ่งๆ ไม่เจ็บตัว"')

def room_radar():
    st.subheader("🛰️ ระบบเรดาร์และพิกัดจริง")
    loc = get_geolocation()
    
    if loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        st.success(f"📍 พิกัดปัจจุบัน: {lat}, {lon}")
        
        # แสดงแผนที่ดาวเทียม Google Satellite
        m = folium.Map(location=[lat, lon], zoom_start=17, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                       attr="Google Satellite")
        folium.Marker([lat, lon], tooltip="Ta101", icon=folium.Icon(color='blue')).add_to(m)
        st_folium(m, width="100%", height=400)
        
        if st.button("📡 กระจายสัญญาณพิกัด"):
            db.reference('users/Ta101').update({'lat': lat, 'lon': lon, 'ts': time.time()})
            save_log("LOCATION UPDATED")
            st.toast("ส่งพิกัดสำเร็จ!")
    else:
        st.warning("🚨 กำลังรอสัญญาณ GPS... (โปรดอนุญาตการเข้าถึงตำแหน่ง)")

def room_comms():
    st.subheader("💬 ศูนย์สื่อสารลับ")
    chat_ref = db.reference('public_chat')
    
    with st.form("chat_form", clear_on_submit=True):
        msg_input = st.text_input("ระบุข้อความสัญญาณ...")
        if st.form_submit_button("SEND SIGNAL"):
            if msg_input:
                chat_ref.push({'user': 'Ta101', 'msg': msg_input, 'ts': time.time()})
                save_log(f"SENT MSG: {msg_input}")
                st.rerun()

    # ดึงข้อมูลแบบปลอดภัยป้องกัน KeyError
    msgs = chat_ref.order_by_key().limit_to_last(10).get()
    if msgs:
        for m in reversed(list(msgs.values())):
            u = m.get('user', 'ระบบ')
            msg = m.get('msg', '...') # ใช้ .get ป้องกันแอปพัง
            st.write(f"🟢 **{u}:** {msg}")

def room_music():
    st.subheader("🎧 SYNAPSE ROOMS (BETA V5)")
    music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลง .mp3 ในโฟลเดอร์แอป")
        return

    current_song = music_files[st.session_state.song_index]
    base_name = os.path.splitext(current_song)[0]

    # ส่วนแสดงผล Visual
    st.markdown(f"<div style='border:2px solid {st.session_state.theme_color}; padding:10px; border-radius:10px; text-align:center;'>NOW PLAYING: {current_song}</div>", unsafe_allow_html=True)
    
    col_vis, col_list = st.columns([3, 2])
    with col_vis:
        if os.path.exists(f"{base_name}.mp4"):
            st.video(f"{base_name}.mp4", loop=True, autoplay=True, muted=True)
        elif os.path.exists(f"{base_name}.jpg"):
            st.image(f"{base_name}.jpg", use_container_width=True)
        st.audio(current_song, autoplay=True)

    with col_list:
        st.write("🎧 PLAYLIST")
        for i, song in enumerate(music_files):
            if st.button(f"🎵 {song}", key=f"s_{i}", use_container_width=True):
                st.session_state.song_index = i
                st.rerun()

    # ระบบเล่นต่อเนื่อง (Auto-Next)
    js_next = """
    <script>
    var audio = window.parent.document.querySelector('audio');
    if (audio) {
        audio.onended = function() {
            var btns = window.parent.document.querySelectorAll('button');
            for (var i=0; i<btns.length; i++) {
                if (btns[i].textContent.includes('🎵')) { // คลิกเพลงถัดไปในลิสต์
                    btns[(i+1)%btns.length].click(); break;
                }
            }
        };
    }
    </script>
    """
    components.html(js_next, height=0)

# ==========================================
# 3. แผงวงจรหลัก (Main Switchboard)
# ==========================================
def main():
    init_system()
    
    # Sidebar สำหรับเปลี่ยนสีธีม
    with st.sidebar:
        st.title("⚙️ SETTINGS")
        st.session_state.theme_color = st.color_picker("เลือกสีนีออน", st.session_state.theme_color)
        st.write(f'**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

    room_map = {
        "🚀 แกนหลัก": room_core,
        "🛰️ เรดาร์": room_radar,
        "💬 การสื่อสาร": room_comms,
        "🎧 ห้องพัก": room_music
    }
    
    tabs = st.tabs(list(room_map.keys()))
    for i, room_func in enumerate(room_map.values()):
        with tabs[i]:
            room_func()

if __name__ == "__main__":
    main()
