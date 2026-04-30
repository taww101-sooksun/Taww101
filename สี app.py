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
    # ตั้งค่าตัวแปรพื้นฐานใน Session State
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#1408BF"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'user' not in st.session_state: st.session_state.user = "AGENT-X"
    
    # เชื่อมต่อ Firebase (ใช้ค่าจาก Secrets)
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            if "private_key" in fb_creds:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ ระบบเชื่อมต่อฐานข้อมูลขัดข้อง: {e}")

# ฟังก์ชันจัดการพื้นหลังรุ้ง (CSS)
def apply_custom_background():
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(270deg, #111, #222, {st.session_state.theme_color}22);
            background-size: 400% 400%;
            animation: Gradient 15s ease infinite;
        }}
        @keyframes Gradient {{ 0%{{background-position:0% 50%}} 50%{{background-position:100% 50%}} 100%{{background-position:0% 50%}} }}
        
        /* ตกแต่ง Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(0, 0, 0, 0.5);
            border-radius: 15px;
            padding: 5px;
            border: 1px solid {st.session_state.theme_color};
        }}
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 1. MODULES (The Rooms)
# ==========================================

def room_music():
    st.subheader("🎧 SYNAPSE MUSIC STATION")
    
    # ค้นหาไฟล์เพลง
    music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลง .mp3 ในระบบ")
        return

    current_song = music_files[st.session_state.song_index % len(music_files)]
    st.info(f"🎵 SIGNAL: {current_song}")

    # เครื่องเล่นเพลง
    with open(current_song, "rb") as f:
        audio_bytes = f.read()
    st.audio(audio_bytes, format="audio/mp3", autoplay=True)

    # JS Auto-Next
    components.html("""
        <script>
        setInterval(() => {
            const audios = window.parent.document.querySelectorAll('audio');
            audios.forEach(audio => {
                if (!audio.dataset.listener) {
                    audio.dataset.listener = "true";
                    audio.onended = () => {
                        const btns = window.parent.document.querySelectorAll('button');
                        for (let b of btns) { if (b.innerText.includes('⏭️')) { b.click(); break; } }
                    };
                }
            });
        }, 2000);
        </script>
    """, height=0)

    # ปุ่มควบคุม
    col1, col2, col3 = st.columns(3)
    if col1.button("⏮️ BACK", key="m_prev", use_container_width=True):
        st.session_state.song_index -= 1
        st.rerun()
    if col2.button("🔄 RELOAD", key="m_reload", use_container_width=True):
        st.rerun()
    if col3.button("⏭️ NEXT", key="m_next", use_container_width=True):
        st.session_state.song_index += 1
        st.rerun()

    # รายชื่อเพลง (แก้ Duplicate ID แล้ว)
    with st.expander("📂 SIGNAL LIST"):
        for i, f_name in enumerate(music_files):
            if st.button(f"🎵 {f_name}", key=f"btn_song_{i}", use_container_width=True):
                st.session_state.song_index = i
                st.rerun()

def room_settings():
    st.subheader("🎨 SYSTEM THEME & MODES")
    
    # โหมดสี (Presets)
    color_presets = {
        "🟢 CYBER NEON": "#39FF14",
        "🔵 DEEP SEA": "#1408BF",
        "🔴 RED ALERT": "#FF0000",
        "🟣 PURPLE VIBE": "#800080",
        "🟡 GOLDEN EYE": "#FFD700",
        "⚪ CLASSIC": "#FFFFFF"
    }
    
    col_p, col_a = st.columns([3, 1])
    selected = col_p.selectbox("เลือกโทนสีระบบ", list(color_presets.keys()))
    if col_a.button("APPLY", use_container_width=True):
        st.session_state.theme_color = color_presets[selected]
        st.rerun()
    
    st.write("---")
    st.session_state.theme_color = st.color_picker("ปรับแต่งสีละเอียด", st.session_state.theme_color)
    
    if st.button("🚪 LOGOUT", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ==========================================
# 2. MAIN EXECUTION
# ==========================================
def main():
    init_system()
    apply_custom_background()
    loc = get_geolocation()

    if not st.session_state.logged_in:
        # หน้า Login (ปรับปรุงให้ใช้ Database จริง)
        st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color};'>SYNAPSE LOGIN</h1>", unsafe_allow_html=True)
        tab_login, tab_reg = st.tabs(["🔑 LOGIN", "📝 REGISTER"])
        
        with tab_login:
            with st.form("login_f"):
                u = st.text_input("AGENT ID")
                p = st.text_input("PASSWORD", type="password")
                if st.form_submit_button("ACCESS GRANTED", use_container_width=True):
                    # เช็คข้อมูลจาก Firebase
                    data = db.reference(f'users/{u}').get()
                    if data and data.get('pw') == p:
                        st.session_state.logged_in = True
                        st.session_state.user = u
                        st.rerun()
                    else: st.error("รหัสผ่านไม่ถูกต้อง")
        
        with tab_reg:
            with st.form("reg_f"):
                new_u = st.text_input("NEW ID")
                new_p = st.text_input("SET PW", type="password")
                if st.form_submit_button("CREATE AGENT", use_container_width=True):
                    db.reference(f'users/{new_u}').set({'pw': new_p, 'ts': time.time()})
                    st.success("ลงทะเบียนสำเร็จ!")
    else:
        # หน้าหลักเมื่อ Login แล้ว
        st.sidebar.write(f"👤 AGENT: {st.session_state.user}")
        st.sidebar.caption("'อยู่นิ่งๆ ไม่เจ็บตัว'")
        
        tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "💬 CHAT", "🎧 MUSIC", "⚙️ SETTINGS"])
        
        with tabs[0]: st.write(f"สวัสดี AGENT {st.session_state.user} ระบบพร้อมทำงาน")
        with tabs[3]: room_music()
        with tabs[4]: room_settings()

if __name__ == "__main__":
    main()
