import streamlit as st
import os  # <<--- ตัวนี้แหละครับที่หายไป ทำให้เกิด Error
import random
import time
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components

import streamlit as st
# ... (import อื่นๆ ตามที่พี่ส่งมาใน requirements.txt) ...

# ==========================================
# 1. กลไกกลาง (Core Engine) - ห้ามแก้ส่วนนี้บ่อย
# ==========================================
def init_system():
    if 'active_room' not in st.session_state:
        st.session_state.active_room = "🚀 แกนหลัก"
    # แทรกการเชื่อมต่อ Firebase ตรงนี้ครั้งเดียวใช้ได้ทุกห้อง

# ==========================================
# 2. พื้นที่เก็บห้อง (The Rooms / Modules) 
# อยากเพิ่มอะไรใหม่ ให้สร้างฟังก์ชัน def ใหม่ตรงนี้
# ==========================================

def room_core():
    st.subheader("🚀 ศูนย์ควบคุมแกนกลาง")
    # ใส่โค้ด Hierarchy/Navigation

def room_radar():
    st.subheader("🛰️ ระบบเรดาร์และพิกัด")
    # ใส่โค้ด Folium Map / GPS

def room_comms():
    st.subheader("💬 ศูนย์สื่อสารลับ")
    # ใส่โค้ด Chat / Private Signal

def room_music():
    st.subheader("🎧 ห้องพักผ่อน (SYNAPSE ROOMS)")
    # ใส่โค้ด Music Player / Suno AI
def room_music():
    st.subheader("🎧 SYNAPSE ROOMS (BETA V5)")
    
    # --- 1. ตรวจสอบไฟล์เพลงในโฟลเดอร์ ---
    music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลง .mp3 ในศูนย์บัญชาการ")
        return

    # --- 2. ตั้งค่าสถานะการเล่น (Session State) ---
    if 'song_index' not in st.session_state:
        st.session_state.song_index = 0
    
    current_song = music_files[st.session_state.song_index]
    base_name = os.path.splitext(current_song)[0] # ชื่อไฟล์แบบไม่มี .mp3

    # --- 3. ส่วนแสดงผล (Visual & Title) ---
    st.markdown(f"""
        <div style="border: 2px solid {st.session_state.theme_color}; padding: 10px; border-radius: 10px; text-align: center; background: rgba(0,0,0,0.5);">
            <h2 style="color: {st.session_state.theme_color}; margin: 0;">NOW PLAYING: {current_song}</h2>
        </div>
    """, unsafe_allow_html=True)

    # เช็ค Visual (Video > Image > Default)
    col_vis, col_list = st.columns([3, 2])
    
    with col_vis:
        found_visual = False
        # เช็ควิดีโอ (.mp4)
        if os.path.exists(f"{base_name}.mp4"):
            st.video(f"{base_name}.mp4", loop=True, autoplay=True, muted=True)
            found_visual = True
        # เช็คภาพ (.jpg, .png)
        else:
            for ext in [".jpg", ".png", ".jpeg"]:
                if os.path.exists(base_name + ext):
                    st.image(base_name + ext, use_container_width=True)
                    found_visual = True
                    break
        
        if not found_visual:
            st.info(f"📡 ไม่มีข้อมูล Visual สำหรับ: {base_name}")

        # เครื่องเล่นเพลง (เปิด Autoplay)
        st.audio(current_song, autoplay=True)

    # --- 4. รายชื่อเพลง (Playlist) ---
    with col_list:
        st.markdown(f"<h3 style='color: {st.session_state.theme_color}'>🎧 PLAYLIST</h3>", unsafe_allow_html=True)
        with st.container(border=True, height=300):
            for i, song in enumerate(music_files):
                # ถ้าเป็นเพลงปัจจุบันให้มีสัญลักษณ์บอก
                label = f"▶️ {song}" if i == st.session_state.song_index else f"🎵 {song}"
                if st.button(label, key=f"song_{i}", use_container_width=True):
                    st.session_state.song_index = i
                    save_log(f"CHANGING TRACK TO: {song}") # บันทึก Log ทุกครั้งที่เปลี่ยนเพลง
                    st.rerun()

    # --- 5. ปุ่มควบคุม (Next / Random) ---
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⏭️ เพลงถัดไป", use_container_width=True):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()
    with c2:
        if st.button("🎲 สุ่มเพลง", use_container_width=True):
            st.session_state.song_index = random.randint(0, len(music_files) - 1)
            st.rerun()

    # --- 6. ระบบเล่นต่อเนื่อง (JavaScript Bridge) ---
    js_code = f"""
    <script>
    var audio = window.parent.document.querySelector('audio');
    if (audio) {{
        audio.onended = function() {{
            var buttons = window.parent.document.querySelectorAll('button');
            for (var i = 0; i < buttons.length; i++) {{
                if (buttons[i].textContent.includes('เพลงถัดไป')) {{
                    buttons[i].click();
                    break;
                }}
            }}
        }};
    }}
    </script>
    """
    components.html(js_code, height=0)


def room_new_feature():
    st.subheader("✨ ความสามารถใหม่ (อนาคต)")
    st.info("พี่อยากเพิ่มอะไร แค่มาเขียนตรงนี้ครับ!")

# ==========================================
# 3. แผงวงจรหลัก (Main Switchboard)
# ==========================================
def main():
    init_system()
    
    # เมนูเลือกห้องแบบ Dynamic (เพิ่มชื่อห้องตรงนี้ได้เลย)
    room_map = {
        "🚀 แกนหลัก": room_core,
        "🛰️ เรดาร์": room_radar,
        "💬 การสื่อสาร": room_comms,
        "🎧 ห้องพัก": room_music,
        "✨ อัปเกรด": room_new_feature  # แค่เพิ่มบรรทัดนี้ ห้องใหม่ก็โผล่มาทันที
    }
    
    # วาดเมนู Tabs
    tabs = st.tabs(list(room_map.keys()))
    
    for i, (room_name, room_func) in enumerate(room_map.items()):
        with tabs[i]:
            room_func()

if __name__ == "__main__":
    main()
