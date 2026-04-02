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
from math import radians, cos, sin, asin, sqrt
from folium.features import DivIcon

# ==========================================
# 0. ระบบพื้นฐาน & CSS สีรุ้ง (คืนชีพชุดสีรุ้ง)
# ==========================================

def init_system():
    if 'user' not in st.session_state: st.session_state.user = "Ta101"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    
    # CSS สำหรับสีรุ้งวิ่งได้ (ตัวหนังสือและกรอบ)
    rainbow_style = """
    <style>
    @keyframes rainbow_animation {
        0% { color: #ff0000; border-color: #ff0000; }
        17% { color: #ff00ff; border-color: #ff00ff; }
        33% { color: #0000ff; border-color: #0000ff; }
        50% { color: #00ffff; border-color: #00ffff; }
        67% { color: #00ff00; border-color: #00ff00; }
        83% { color: #ffff00; border-color: #ffff00; }
        100% { color: #ff0000; border-color: #ff0000; }
    }
    .rainbow-text {
        animation: rainbow_animation 4s linear infinite;
        font-weight: bold;
        filter: drop-shadow(0 0 5px rgba(255,255,255,0.3));
    }
    .rainbow-box {
        border: 4px solid;
        padding: 20px;
        border-radius: 20px;
        animation: rainbow_animation 4s linear infinite;
        background: rgba(0,0,0,0.6);
        box-shadow: 0 0 15px rgba(255,255,255,0.1);
    }
    .stApp { background-color: #000000; }
    </style>
    """
    st.markdown(rainbow_style, unsafe_allow_html=True)
    
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except: pass

# ==========================================
# 1. ฟังก์ชันแสดงโลโก้ (สำหรับใส่ทุกหน้า)
# ==========================================

def show_logo():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        try:
            # พยายามเรียกไฟล์โลโก้
            st.image("logo1.jpg", use_container_width=True)
        except:
            st.markdown("<h1 class='rainbow-text' style='text-align:center;'>SYNAPSE PRO</h1>", unsafe_allow_html=True)

# ==========================================
# 2. ห้องเพลง (คืนชีพรายชื่อเพลง)
# ==========================================

def room_music():
    st.markdown("<h2 class='rainbow-text'>🎧 Music Station</h2>", unsafe_allow_html=True)
    
    # ดึงไฟล์เพลงใหม่ทุกครั้งที่เปิดหน้า
    music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลงในระบบ")
        return

    # แสดงรายชื่อเพลง
    st.write("---")
    with st.container():
        st.caption("📂 คลังเพลง AGENT (เลือกเพื่อเปลี่ยนเพลง)")
        for i, song in enumerate(music_files):
            # ตกแต่งปุ่มที่กำลังเล่นอยู่
            if i == st.session_state.song_index:
                if st.button(f"▶️ NOW PLAYING: {song}", key=f"s_{i}", use_container_width=True):
                    pass
            else:
                if st.button(f"🎵 {song}", key=f"s_{i}", use_container_width=True):
                    st.session_state.song_index = i
                    st.rerun()

    st.write("---")
    
    # ระบบเล่นเพลง
    current_song = music_files[st.session_state.song_index]
    st.markdown(f"กำลังขับขาน: <span class='rainbow-text'>{current_song}</span>", unsafe_allow_html=True)
    
    try:
        with open(current_song, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            audio_html = f'<audio id="p" controls autoplay style="width:100%"><source src="data:audio/mp3;base64,{b64}"></audio>'
            components.html(audio_html, height=100)
    except:
        st.error("ไม่สามารถโหลดไฟล์เสียงได้")

# ==========================================
# 3. ห้องแกนหลัก & ภารกิจ (ฉบับสีรุ้ง)
# ==========================================

def room_core():
    st.markdown("<h2 class='rainbow-text'>🚀 COMMAND CENTER</h2>", unsafe_allow_html=True)
    now = datetime.utcnow() + timedelta(hours=7)
    st.markdown(f"""
        <div class="rainbow-box">
            <h1 style="font-size: 4em; margin:0; color: white;">{now.strftime('%H:%M:%S')}</h1>
            <p style="letter-spacing: 5px; color: white; opacity:0.8;">AGENT STATUS: ONLINE</p>
        </div>
    """, unsafe_allow_html=True)
    st.write("")
    st.markdown(f"🚩 SLOGAN: <span class='rainbow-text'>'อยู่นิ่งๆ ไม่เจ็บตัว'</span>", unsafe_allow_html=True)

# ==========================================
# 4. Main Program
# ==========================================

def main():
    st.set_page_config(page_title="SYNAPSE PRO RAINBOW", layout="wide")
    init_system()

    if not st.session_state.logged_in:
        show_logo()
        # ส่วน Login
        with st.form("login"):
            u = st.text_input("AGENT ID")
            p = st.text_input("PASSWORD", type="password")
            if st.form_submit_button("UNLOCK SYSTEM", use_container_width=True):
                user_data = db.reference(f'users/{u}').get()
                if user_data and user_data.get('pw') == p:
                    st.session_state.user = u
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("เข้าถึงไม่ได้")
        return

    # --- ส่วนที่แสดงทุกหน้าหลัง Login ---
    show_logo() # โลโก้มาแล้วทุกหน้า!
    
    tabs = st.tabs(["🚀 แกนหลัก", "🛰️ เรดาร์", "🌐 แชตรวม", "🔐 แชตลับ", "📞 โทร", "🎧 เพลง", "🩺 ตรวจร่างกาย", "📝 ภารกิจ"])
    
    with tabs[0]: room_core()
    with tabs[1]:
        from math import radians # กัน Error
        # ส่วนเรดาร์เรียกใช้ตามเดิม
        st.subheader("🛰️ ระบบเรดาร์")
        # (ก๊อปปี้โค้ดห้องเรดาร์เดิมใส่ตรงนี้ได้เลย)
    
    with tabs[5]: room_music() # ห้องเพลงคืนชีพ
    
    with tabs[7]:
        st.markdown("<h2 class='rainbow-text'>📝 MISSION LOG</h2>", unsafe_allow_html=True)
        # (ก๊อปปี้โค้ดห้องภารกิจเดิมใส่ตรงนี้ได้เลย)

    with st.sidebar:
        st.title("⚙️ SETTINGS")
        st.write(f"AGENT: **{st.session_state.user}**")
        if st.button("🚪 LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()

if __name__ == "__main__":
    main()
