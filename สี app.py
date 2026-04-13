import streamlit as st
import base64

def display_logo(path):
    try:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 20px;">
                <img src="data:image/png;base64,{data}" style="width: 140px; filter: drop-shadow(0 0 10px #ff1744);">
            </div>
        """, unsafe_allow_html=True)
    except:
        # ถ้าหาไฟล์ไม่เจอ ให้โชว์ Text เท่ๆ แทน ป้องกันแอปพัง
        st.markdown("<h1 style='text-align: center; color: #ff1744;'>SYNAPSE</h1>", unsafe_allow_html=True)

# เรียกใช้ก่อนเริ่มเนื้อหา
display_logo("static/logo1.png")

def display_logo(path):
    try:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        st.markdown(f"""
            <div style="text-align: center;">
                <img src="data:image/png;base64,{data}" style="width: 130px; filter: drop-shadow(0 0 10px #ff1744);">
            </div>
        """, unsafe_allow_html=True)
    except:
        pass # ถ้าไม่มีรูปก็ปล่อยผ่าน ไม่ให้แอปพัง

# เรียกใช้โลโก้ก่อนขึ้นหัวข้อ
display_logo("static/logo1.png")

# --- 1. นิยามฟังก์ชันทั้งหมดก่อน (ประกาศตัวตน) ---

def setup_ui():
    st.markdown("""
def setup_ui():
    st.markdown("""
        <style>
        /* ซ่อนติ่งเมนูขาวๆ ด้านบน และเครดิตด้านล่าง */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        
        /* ปรับแต่งพื้นหลังและฟอนต์ตามสไตล์ SYNAPSE */
        .stApp { background: radial-gradient(circle, #001 0%, #000 100%); color: #00f2fe; }
        .neon-header { 
            font-size: 40px; font-weight: 900; text-align: center;
            color: #fff; text-shadow: 0 0 15px #ff1744, 0 0 20px #00f2fe;
            border: 10px double #ff1744; padding: 20px; border-radius: 20px;
        }
        .stButton>button { border-radius: 10px; border: 1px solid #ff1744; background: rgba(0,0,0,0.5); color: white; }
        </style>
    """, unsafe_allow_html=True)


def draw_box(title, target_level):
    if st.button(title, key=target_level, use_container_width=True):
        st.session_state.nav_level = target_level
        st.rerun()

# --- 2. เริ่มรันระบบ ---

# ตรวจสอบสถานะหน้าปัจจุบัน
if 'nav_level' not in st.session_state:
    st.session_state.nav_level = "HOME"

setup_ui()

st.title("📡 SYNAPSE HIERARCHY")

# ปุ่มย้อนกลับแบบฉลาดที่เพี้ยนเขียนไว้
if st.session_state.nav_level != "HOME":
    if st.button("⬅️ BACK"):
        if "." in st.session_state.nav_level:
            st.session_state.nav_level = ".".join(st.session_state.nav_level.split(".")[:-1])
        else:
            st.session_state.nav_level = "HOME"
        st.rerun()

st.write(f"STATUS: **ONLINE** | LOCATION: **{st.session_state.nav_level}**")
st.markdown("---")

# --- 3. ระบบ Navigation Logic (ตามที่เพี้ยนออกแบบ) ---

if st.session_state.nav_level == "HOME":
    c1, c2 = st.columns(2)
    with c1: draw_box("📦 กรอบที่ 1 (MAIN)", "1")
    with c2: draw_box("📦 กรอบที่ 2 (SUB)", "2")

elif st.session_state.nav_level == "1":
    st.subheader("ชั้นที่ 1: ระบบหลัก")
    c1, c2 = st.columns(2)
    with c1: draw_box("📂 1.1 เจาะลึก", "1.1")
    with c2: draw_box("📂 1.2 รายงาน", "1.2")

elif st.session_state.nav_level == "1.1":
    st.subheader("ชั้นที่ 2: ข้อมูลภายใน 1.1")
    st.info("อยู่นิ่งๆ ไม่เจ็บตัว - ข้อมูลถูกเข้ารหัสไว้แล้ว")
    draw_box("🔐 1.1.1 ความลับสูงสุด", "1.1.1")

else:
    st.warning(f"⚠️ พิกัด {st.session_state.nav_level} ยังไม่เปิดใช้งาน")
