import streamlit as st
import base64

# --- 1. ตั้งค่าหน้าเว็บ & ลบติ่ง (อยู่นิ่งๆ ไม่เจ็บตัว) ---
st.set_page_config(page_title="SYNAPSE 4-1", layout="wide")

def setup_ui():
    st.markdown("""
        <style>
        header, footer, #MainMenu {visibility: hidden;}
        .stApp { background: radial-gradient(circle, #001 0%, #000 100%); color: #00f2fe; }
        .neon-text { 
            text-align: center; color: #fff; 
            text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe;
            font-size: 20px; font-weight: bold;
        }
        .stButton>button { border-radius: 10px; border: 1px solid #ff1744; background: rgba(0,0,0,0.5); color: white; }
        </style>
    """, unsafe_allow_html=True)

def display_logo(path):
    try:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{data}" style="width: 120px; filter: drop-shadow(0 0 10px #ff1744);"></div>', unsafe_allow_html=True)
    except:
        st.markdown("<h1 style='text-align: center; color: #ff1744;'>SYNAPSE</h1>", unsafe_allow_html=True)

def draw_box(title, target_level):
    if st.button(title, key=target_level, use_container_width=True):
        st.session_state.nav_level = target_level
        st.rerun()

# --- 2. เริ่มระบบ ---
if 'nav_level' not in st.session_state:
    st.session_state.nav_level = "HOME"

setup_ui()
display_logo("static/logo1.png")

# ปุ่มย้อนกลับ
if st.session_state.nav_level != "HOME":
    if st.button("⬅️ BACK"):
        if "." in st.session_state.nav_level:
            st.session_state.nav_level = ".".join(st.session_state.nav_level.split(".")[:-1])
        else:
            st.session_state.nav_level = "HOME"
        st.rerun()

st.write(f"LOCATION: **{st.session_state.nav_level}**")
st.markdown("---")

# --- 3. เนื้อหาแต่ละชั้น (Hierarchy Logic) ---

# หน้าแรก
if st.session_state.nav_level == "HOME":
    c1, c2 = st.columns(2)
    with c1: draw_box("🚀 CORE (MUSIC/LYRICS)", "1")
    with c2: draw_box("📺 MEDIA (VIDEO)", "2")

# ชั้นที่ 1: หน้าเล่นเพลงและเนื้อเพลง
elif st.session_state.nav_level == "1":
    st.subheader("🚀 CORE SYSTEM: AUDIO & LYRICS")
    
    # --- ส่วนของ MP3 ---
    st.write("🎵 Now Playing: *Secret Track*")
    st.audio("static/1.mp3") # อย่าลืมเอาไฟล์ 1.mp3 ใส่ในโฟลเดอร์ static นะเพี้ยน
    
    # --- ส่วนของเนื้อเพลงวิ้งๆ ---
    st.markdown("""
        <div class="neon-text">
            <br>✨ เนื้อเพลงบรรทัดที่ 1... ✨<br>
            ✨ เนื้อเพลงบรรทัดที่ 2... ✨<br>
            ✨ อยู่นิ่งๆ ไม่เจ็บตัว... ✨
        </div>
    """, unsafe_allow_html=True)

# ชั้นที่ 2: หน้าวีดีโอ
elif st.session_state.nav_level == "2":
    st.subheader("📺 MEDIA SYSTEM: VIDEO FEED")
    
    # --- ส่วนของ VDO (ตัวอย่างจาก YouTube) ---
    st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    st.info("กำลังรับสัญญาณจากดาวเทียม...")

else:
    st.warning(f"⚠️ พิกัด {st.session_state.nav_level} ยังไม่ได้ติดตั้งอุปกรณ์")
