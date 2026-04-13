import streamlit as st
import base64

# ฟังก์ชันสำหรับแปลงรูปภาพเป็นรหัส Base64
def get_base64_img(img_path):
    try:
        with open(img_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

# เรียกใช้งาน: ดึงรูปจากโฟลเดอร์ static
img_base64 = get_base64_img("static/logo1.png")

if img_base64:
    # แสดงโลโก้ตรงกลางหน้าจอ พร้อมใส่เงาเรืองแสง (Neon Drop Shadow)
    st.markdown(f"""
        <div style="text-align: center; margin-top: -20px; margin-bottom: 20px;">
            <img src="data:image/png;base64,{img_base64}" 
                 style="width: 150px; filter: drop-shadow(0 0 10px #ff1744);">
        </div>
    """, unsafe_allow_html=True)

# --- 1. นิยามฟังก์ชันทั้งหมดก่อน (ประกาศตัวตน) ---

def setup_ui():
    st.markdown("""
        <style>
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
st.markdown("""
    <style>
    /* 1. ซ่อนแถบ Header ด้านบนทั้งหมด (รวมถึงติ่งเมนูขวาบน) */
    header {visibility: hidden;}
    
    /* 2. ซ่อนแถบ Footer ด้านล่าง (Made with Streamlit) */
    footer {visibility: hidden;}
    
    /* 3. ซ่อนปุ่มเมนูหลัก (แฮมเบอร์เกอร์เมนู) */
    #MainMenu {visibility: hidden;}
    
    /* 4. (แถม) ดันเนื้อหาขึ้นไปให้สุด ไม่ให้เหลือที่ว่างด้านบน */
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    </style>
    """, unsafe_allow_html=True)

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
