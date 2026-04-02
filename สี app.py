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
# 0. ระบบพื้นฐาน & CSS สีรุ้ง
# ==========================================

def init_system():
    if 'user' not in st.session_state: st.session_state.user = "Ta101"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    
    # CSS สำหรับทำให้ตัวหนังสือและกรอบเป็นสีรุ้งวิ่งได้
    rainbow_css = """
    <style>
    @keyframes rainbow {
        0% { color: #ff0000; border-color: #ff0000; }
        20% { color: #ff8000; border-color: #ff8000; }
        40% { color: #ffff00; border-color: #ffff00; }
        60% { color: #00ff00; border-color: #00ff00; }
        80% { color: #0000ff; border-color: #0000ff; }
        100% { color: #ff0000; border-color: #ff0000; }
    }
    .rainbow-text {
        animation: rainbow 3s linear infinite;
        font-weight: bold;
    }
    .rainbow-box {
        border: 3px solid;
        padding: 20px;
        border-radius: 15px;
        animation: rainbow 3s linear infinite;
        background: rgba(0,0,0,0.5);
        text-align: center;
    }
    </style>
    """
    st.markdown(rainbow_css, unsafe_allow_html=True)
    
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except: pass

# ==========================================
# 1. ฟังก์ชันแสดงโลโก้ (เรียกใช้ทุกหน้า)
# ==========================================

def show_logo():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        try:
            # พยายามโหลดโลโก้ของต๊ะ
            st.image("logo1.jpg", use_container_width=True)
        except:
            st.markdown("<h1 class='rainbow-text' style='text-align:center;'>SYNAPSE</h1>", unsafe_allow_html=True)

# ==========================================
# 2. ห้องเพลง (แก้ไขให้รายชื่อเพลงไม่หาย)
# ==========================================

def room_music():
    st.subheader("🎧 ระบบสถานีเพลง (Non-Stop)")
    
    # สแกนหาไฟล์ .mp3 ในโฟลเดอร์ปัจจุบัน
    files = [f for f in os.listdir('.') if f.endswith(".mp3")]
    
    if not files:
        st.warning("⚠️ ไม่พบไฟล์เพลงในระบบ (กรุณาอัปโหลดไฟล์ .mp3 ไว้ในโฟลเดอร์แอป)")
        return

    # แสดงรายชื่อเพลงทั้งหมดในรูปแบบตารางเลือก
    with st.expander("📂 คลังเพลงทั้งหมด (เลือกเล่นได้)", expanded=True):
        for i, f in enumerate(files):
            # เน้นสีรุ้งที่เพลงที่กำลังเล่นอยู่
            label = f"🎶 {f}" if i == st.session_state.song_index else f"🎵 {f}"
            if st.button(label, key=f"s_{i}", use_container_width=True):
                st.session_state.song_index = i
                st.rerun()

    # ส่วนตัวเล่นเพลง
    current = files[st.session_state.song_index]
    st.markdown(f"กำลังเล่น: <span class='rainbow-text'>{current}</span>", unsafe_allow_html=True)
    
    try:
        with open(current, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            st.components.v1.html(f'<audio controls autoplay style="width:100%"><source src="data:audio/mp3;base64,{b64}"></audio>', height=80)
    except:
        st.error("เล่นเพลงไม่ได้")

# ==========================================
# 3. ห้องภารกิจ & แกนหลัก (ฉบับสีรุ้ง)
# ==========================================

def room_core():
    now = datetime.utcnow() + timedelta(hours=7)
    st.markdown(f"""
        <div class="rainbow-box">
            <h1 style="font-size: 4em; margin:0;">{now.strftime('%H:%M:%S')}</h1>
            <p style="letter-spacing: 5px;">SYSTEM ONLINE</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f"🚩 SLOGAN: <span class='rainbow-text'>'อยู่นิ่งๆ ไม่เจ็บตัว'</span>", unsafe_allow_html=True)

# ==========================================
# 4. Main Program
# ==========================================

def main():
    st.set_page_config(page_title="SYNAPSE RAINBOW", layout="wide")
    init_system()

    if not st.session_state.get('logged_in', False):
        # หน้า Login ก็ใส่โลโก้
        show_logo()
        # ... (โค้ดส่วน Login เหมือนเดิม) ...
        # สมมติถ้าต๊ะ Login ผ่านแล้วให้เปลี่ยนค่าเป็น True
        if st.button("UNLOCK (DEMO)"): 
            st.session_state.logged_in = True
            st.rerun()
        return

    # --- ส่วนที่แสดงทุกหน้าหลัง Login ---
    show_logo() # แสดงโลโก้ด้านบนสุดของทุกหน้า
    
    tabs = st.tabs(["🚀 แกนหลัก", "🛰️ เรดาร์", "🎧 เพลง", "📝 ภารกิจ"])
    
    with tabs[0]: room_core()
    with tabs[1]: st.write("ส่วนเรดาร์ (โค้ดเดิมของต๊ะทำงานได้ปกติ)")
    with tabs[2]: room_music()
    with tabs[3]: 
        st.subheader("📝 บันทึกภารกิจ")
        st.markdown("<p class='rainbow-text'>กำลังตรวจสอบสถานะภารกิจ...</p>", unsafe_allow_html=True)
        # ... (โค้ด Mission เดิม) ...

if __name__ == "__main__":
    main()
