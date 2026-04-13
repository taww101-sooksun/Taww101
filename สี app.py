import streamlit as st
import base64
import os

# --- 1. Setup UI & Neon Style ---
st.set_page_config(page_title="SYNAPSE 4-1", layout="wide")

def setup_ui():
    st.markdown("""
        <style>
        header, footer, #MainMenu {visibility: hidden;}
        .stApp { background: #000; color: #00f2fe; }
        .neon-text { 
            text-align: center; color: #fff; font-size: 30px; font-weight: bold;
            text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe, 0 0 40px #00f2fe;
            animation: flicker 2s infinite alternate;
        }
        @keyframes flicker { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
        .stButton>button { border-radius: 10px; border: 1px solid #ff1744; background: rgba(0,0,0,0.5); color: white; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. ฟังก์ชันดึงไฟล์ MP3 แบบปลอดภัย ---
def play_audio(file_name):
    # เช็คว่าไฟล์มีอยู่จริงไหมในโฟลเดอร์ปัจจุบัน
    if os.path.exists(file_name):
        try:
            with open(file_name, "rb") as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการอ่านไฟล์: {e}")
    else:
        # ถ้าหาไฟล์ไม่เจอ ให้โชว์คำเตือนแทนการ Error พังทั้งหน้า
        st.warning(f"⚠️ ไม่พบไฟล์ {file_name} ใน GitHub ของคุณ (เช็คชื่อไฟล์อีกรอบนะเพี้ยน)")

# --- 3. เริ่มรันระบบ ---
if 'nav_level' not in st.session_state:
    st.session_state.nav_level = "HOME"

setup_ui()

# ปุ่มย้อนกลับ
if st.session_state.nav_level != "HOME":
    if st.button("⬅️ BACK"):
        if "." in st.session_state.nav_level:
            st.session_state.nav_level = ".".join(st.session_state.nav_level.split(".")[:-1])
        else:
            st.session_state.nav_level = "HOME"
        st.rerun()

# --- 4. Logic หน้าจอ ---
if st.session_state.nav_level == "HOME":
    st.markdown("<div class='neon-text'>SYNAPSE COMMAND</div>", unsafe_allow_html=True)
    if st.button("🚀 เข้าสู่ระบบ CORE", use_container_width=True):
        st.session_state.nav_level = "1"
        st.rerun()

elif st.session_state.nav_level == "1":
    st.markdown("<div class='neon-text'>🎵 AUDIO SYSTEM</div>", unsafe_allow_html=True)
    
    # สั่งเล่นไฟล์ 1.mp3 ที่วางอยู่หน้าเดียวกับ app.py
    play_audio("1.mp3") 
    
    st.markdown("<div class='neon-text' style='font-size:20px;'>✨ อยู่นิ่งๆ ไม่เจ็บตัว ✨</div>", unsafe_allow_html=True)
