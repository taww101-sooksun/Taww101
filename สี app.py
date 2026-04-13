import streamlit as st
import base64

# --- 1. Setup ---
st.set_page_config(page_title="SYNAPSE 4-1", layout="wide")

def setup_ui():
    st.markdown("""
        <style>
        header, footer, #MainMenu {visibility: hidden;}
        .stApp { background: radial-gradient(circle, #001 0%, #000 100%); color: #00f2fe; }
        .neon-header { 
            font-size: 40px; font-weight: 900; text-align: center;
            color: #fff; text-shadow: 0 0 15px #ff1744, 0 0 20px #00f2fe;
            border: 10px double #ff1744; padding: 20px; border-radius: 20px;
        }
        .stButton>button { border-radius: 10px; border: 1px solid #ff1744; background: rgba(0,0,0,0.5); color: white; }
        </style>
    """, unsafe_allow_html=True)

def display_logo(path):
    try:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        st.markdown(f'<div style="text-align: center;"><img src="data:image/png;base64,{data}" style="width: 140px; filter: drop-shadow(0 0 10px #ff1744);"></div>', unsafe_allow_html=True)
    except:
        st.markdown("<h1 style='text-align: center; color: #ff1744;'>SYNAPSE</h1>", unsafe_allow_html=True)

# --- 2. Execution ---
if 'nav_level' not in st.session_state:
    st.session_state.nav_level = "HOME"

setup_ui()
display_logo("static/logo1.png")

if st.session_state.nav_level != "HOME":
    if st.button("⬅️ BACK"):
        if "." in st.session_state.nav_level:
            st.session_state.nav_level = ".".join(st.session_state.nav_level.split(".")[:-1])
        else:
            st.session_state.nav_level = "HOME"
        st.rerun()

# --- 3. Logic ---
if st.session_state.nav_level == "HOME":
    st.markdown("<div class='neon-header'>MAIN CENTER</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 CORE", key="b1", use_container_width=True):
            st.session_state.nav_level = "1"
            st.rerun()
    with c2:
        if st.button("🛰️ RADAR", key="b2", use_container_width=True):
            st.session_state.nav_level = "2"
            st.rerun()
# --- 3. เนื้อหาภายในแต่ละชั้น (Logic ต่อจากเดิม) ---
if st.session_state.nav_level == "HOME":
    st.markdown("<div class='neon-header'>MAIN CENTER</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: draw_box("🚀 CORE SYSTEM", "1")
    with c2: draw_box("🛰️ RADAR CONTROL", "2")

elif st.session_state.nav_level == "1":
    st.subheader("🚀 CORE SYSTEM (ระบบประมวลผลหลัก)")
    # ลองใส่ปุ่มย่อยลงไปอีกชั้น
    c1, c2 = st.columns(2)
    with c1: draw_box("📁 1.1 DATABASE", "1.1")
    with c2: draw_box("📁 1.2 SETTINGS", "1.2")
    st.info("เลือกหัวข้อเพื่อจัดการระบบภายใน")

elif st.session_state.nav_level == "1.1":
    st.subheader("📁 DATABASE 1.1")
    st.write("สถานะ: **กำลังเชื่อมต่อกับไฟล์ 1.mp3...**")
    # เพี้ยนสามารถเอาโค้ดเล่นเพลงมาใส่ตรงนี้ได้เลย
    st.audio("1.mp3") 

elif st.session_state.nav_level == "2":
    st.subheader("🛰️ RADAR CONTROL")
    st.warning("กำลังค้นหาสัญญาณดาวเทียม...")
    # ใส่ลูกเล่นอื่นๆ เช่น สแกนหาพิกัด
    st.progress(75, text="SCANNING...")

else:
    st.error(f"⚠️ ไม่พบพิกัด {st.session_state.nav_level} ในระบบ")
