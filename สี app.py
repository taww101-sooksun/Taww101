import streamlit as st
import base64

# --- 1. ตั้งค่าหน้าเว็บ (ห้ามมีอะไรอยู่ก่อนบรรทัดนี้) ---
st.set_page_config(page_title="SYNAPSE 4-1", layout="wide")

# --- 2. ฟังก์ชันซ่อนส่วนเกิน Streamlit และดึงรูป ---
def hide_and_style():
    st.markdown("""
        <style>
        header, footer, #MainMenu {visibility: hidden;}
        .stApp { background-color: #000000; }
        .block-container { padding-top: 1rem; }
        </style>
    """, unsafe_allow_html=True)

def display_logo(path):
    try:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <div style="text-align: center;">
                <img src="data:image/png;base64,{data}" style="width: 140px; filter: drop-shadow(0 0 10px #ff1744);">
            </div>
        """, unsafe_allow_html=True)
    except:
        st.markdown("<h1 style='text-align: center; color: #ff1744;'>SYNAPSE</h1>", unsafe_allow_html=True)

# --- 3. เริ่มรันหน้าตา UI ---
hide_and_style()
display_logo("static/logo1.png")

st.markdown("<h2 style='text-align: center; color: #00f2fe;'>อยู่นิ่งๆ ไม่เจ็บตัว</h2>", unsafe_allow_html=True)
st.write("---")

# --- 4. ระบบคุมชั้น (Hierarchy Logic) ---
if 'nav_level' not in st.session_state:
    st.session_state.nav_level = "HOME"

# ปุ่มย้อนกลับ (โชว์เฉพาะเมื่อไม่ได้อยู่หน้าแรก)
if st.session_state.nav_level != "HOME":
    if st.button("⬅️ BACK"):
        if "." in st.session_state.nav_level:
            st.session_state.nav_level = ".".join(st.session_state.nav_level.split(".")[:-1])
        else:
            st.session_state.nav_level = "HOME"
        st.rerun()

# --- 5. เนื้อหาแต่ละหน้า ---
if st.session_state.nav_level == "HOME":
    st.write("📡 **COMMAND CENTER ONLINE**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 CORE SYSTEM", use_container_width=True):
            st.session_state.nav_level = "1"
            st.rerun()
    with col2:
        if st.button("🛰️ SATELLITE", use_container_width=True):
            st.session_state.nav_level = "2"
            st.rerun()

elif st.session_state.nav_level == "1":
    st.subheader("🚀 CORE SYSTEM")
    st.write("ยินดีต้อนรับเข้าสู่ระบบหลัก...")
    # เพี้ยนอยากใส่ปุ่มย่อย 1.1, 1.2 เพิ่มตรงนี้ได้เลย

elif st.session_state.nav_level == "2":
    st.subheader("🛰️ SATELLITE CONTROL")
    st.info("กำลังรับสัญญาณจากจานดาวเทียม...")
