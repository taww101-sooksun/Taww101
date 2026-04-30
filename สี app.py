import streamlit as st
import os 
import time
import base64
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from math import radians, cos, sin, asin, sqrt
import pytz
from timezonefinder import TimezoneFinder
from datetime import datetime
from streamlit_js_eval import get_geolocation 

# ==========================================
# 0. CONFIG & INITIALIZATION
# ==========================================
st.set_page_config(page_title="SYNAPSE OS", layout="wide", initial_sidebar_state="collapsed")

def init_system():
    # ตั้งค่าตัวแปรพื้นฐาน
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#1408BF"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'user' not in st.session_state: st.session_state.user = "AGENT-X"
    
    # เชื่อมต่อ Firebase
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            # จัดการ private_key ให้ถูกต้อง
            if "private_key" in fb_creds:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ ระบบเชื่อมต่อฐานข้อมูลขัดข้อง: {e}")

# ==========================================
# 1. THE ROOMS (โมดูลความสามารถต่างๆ)
# ==========================================

# --- ห้องเพลงที่คุณต้องการ (ใส่เข้าไปได้เลย) ---
def room_music():
    st.subheader("🎧 ระบบสถานีเพลงต่อเนื่อง (Non-Stop Station) อยู่นิ้งๆไม่เจ็บตัว🎙")
    
    music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลง .mp3 ในระบบ")
        return

    if st.session_state.song_index >= len(music_files):
        st.session_state.song_index = 0

    current_song = music_files[st.session_state.song_index]
    st.info(f"🎵 กำลังเล่น: {current_song}")

    with open(current_song, "rb") as f:
        audio_bytes = f.read()
    st.audio(audio_bytes, format="audio/mp3", autoplay=True)

    # JS สำหรับ Auto-Next
    components.html(
        """
        <script>
        const autoNext = () => {
            const audios = window.parent.document.querySelectorAll('audio');
            audios.forEach(audio => {
                if (!audio.dataset.listener) {
                    audio.dataset.listener = "true";
                    audio.onended = () => {
                        const buttons = window.parent.document.querySelectorAll('button');
                        for (let btn of buttons) {
                            if (btn.innerText.includes('⏭️ Next')) {
                                btn.click();
                                break;
                            }
                        }
                    };
                }
            });
        };
        setInterval(autoNext, 2000);
        </script>
        """,
        height=0,
    )

    col1, col2, col3 = st.columns(3)
    if col1.button("⏮️ Back", key="main_prev", use_container_width=True):
        st.session_state.song_index = (st.session_state.song_index - 1) % len(music_files)
        st.rerun()
    if col2.button("🔄 Reload", key="main_reload", use_container_width=True):
        st.rerun()
    if col3.button("⏭️ Next", key="main_next", use_container_width=True):
        st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
        st.rerun()

    st.write("---")
    st.subheader("📂 รายชื่อเพลงทั้งหมด")
    for i, f_name in enumerate(music_files):
        is_playing = (i == st.session_state.song_index)
        label = f"▶️ {f_name}" if is_playing else f"🎵 {f_name}"
        if st.button(label, key=f"list_btn_{i}", use_container_width=True):
            st.session_state.song_index = i
            st.rerun()

with tabs[5]:  # ห้อง SETTINGS
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-align:center;'>⚙️ SYSTEM CONFIGURATION</h2>", unsafe_allow_html=True)
    
    # --- ส่วนที่ 1: เลือกโหมดสีด่วน (Presets) ---
    st.subheader("🎨 QUICK THEME MODE")
    
    # นิยามสีประจำโหมดต่างๆ
    color_presets = {
        "🟢 CYBER NEON": "#39FF14",
        "🔵 DEEP SEA": "#1408BF",
        "🔴 RED ALERT": "#FF0000",
        "🟣 PURPLE VIBE": "#800080",
        "🟡 GOLDEN EYE": "#FFD700",
        "🟠 SUNSET FLOW": "#FF7F50",
        "⚪ CLASSIC WHITE": "#FFFFFF"
    }
    
    # สร้างเมนูให้เลือก
    col_preset, col_apply = st.columns([3, 1])
    selected_mode = col_preset.selectbox("เลือกโทนสีของระบบ", list(color_presets.keys()), label_visibility="collapsed")
    
    if col_apply.button("APPLY MODE", use_container_width=True):
        st.session_state.theme_color = color_presets[selected_mode]
        st.toast(f"จูนสีระบบเป็น {selected_mode} เรียบร้อย!")
        st.rerun()

    st.markdown("---")

    # --- ส่วนที่ 2: ปรับแต่งสีละเอียด (Custom) ---
    st.subheader("🛠️ CUSTOM COLOR")
    st.session_state.theme_color = st.color_picker("ปรับแต่งสีตามใจชอบ", st.session_state.theme_color)
    
    # --- ส่วนที่ 3: ระบบ LOGOUT ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🔴 TERMINATE SESSION (LOGOUT)", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# --- ห้องอื่นๆ (Core, Radar, Chat, Call - ตามที่คุณเขียนมา) ---
# ... (ใส่โค้ด room_core, room_radar, room_secure_chat ตามที่คุณมี) ...

# ==========================================
# 2. MAIN SYSTEM
# ==========================================
def main():
    init_system()
    # apply_custom_background() # เรียกใช้ฟังก์ชัน CSS ของคุณ
    
    loc = get_geolocation() 

    if not st.session_state.logged_in:
        # แสดงหน้า Login จากฟังก์ชันที่คุณเขียน (room_login)
        # room_login() 
        st.title("🛡️ SYNAPSE LOGIN")
        # (ตัวอย่างการ login ง่ายๆ)
        with st.form("login"):
            u = st.text_input("AGENT ID")
            p = st.text_input("PASSWORD", type="password")
            if st.form_submit_button("LOGIN"):
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
    else:
        # เมื่อ Login แล้ว ให้แสดง Tabs ทั้งหมด
        tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "💬 CHAT", "📞 CALL", "🎧 MUSIC", "⚙️ SETTINGS"])
        
        # เชื่อมห้องเพลงเข้ากับ Tab ที่ 5
        # with tabs[0]: room_core(loc)
        # with tabs[1]: room_radar(loc)
        with tabs[4]: 
            room_music() # เรียกใช้ห้องเพลงที่นี่
        with tabs[5]:  room_settingh
            st.session_state.theme_color = st.color_picker("ปรับแต่งสีระบบ", st.session_state.theme_color)
with tabs [2
5
if __name__ == "__main__":
    main()
