import streamlit as st
import streamlit as st
import base64
import streamlit as st
import base64

# --- 1. การตั้งค่าหน้าเว็บและลบส่วนเกินของ Streamlit ---
st.set_page_config(page_title="SYNAPSE 4-1", layout="wide")

def hide_st_elements():
    st.markdown("""
        <style>
        /* ลบแถบ Header, Footer และปุ่มเมนูขวาบน */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        
        /* ปรับพื้นหลังแอปให้เป็นสีดำสนิท */
        .stApp { background-color: #000000; }
        
        /* จัดการระยะห่างด้านบนให้โลโก้อยู่ในตำแหน่งที่สวยงาม */
        .block-container { padding-top: 2rem; }
        </style>
    """, unsafe_allow_html=True)

hide_st_elements()

# --- 2. ฟังก์ชันเรียกใช้โลโก้แทนที่ติ่งเดิม ---
def get_base64_img(img_path):
    try:
        with open(img_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

# ดึงโลโก้จากโฟลเดอร์ static ที่เพี้ยนสร้างไว้
img_base64 = get_base64_img("static/logo1.png")

if img_base64:
    # แสดงโลโก้ตรงกลางพร้อมเอฟเฟกต์แสงฟุ้ง (Neon Drop Shadow)
    st.markdown(f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{img_base64}" 
                 style="width: 150px; filter: drop-shadow(0 0 15px #ff1744);">
        </div>
    """, unsafe_allow_html=True)
else:
    # กรณีหาไฟล์ไม่เจอ ให้โชว์ Text เท่ๆ แทน
    st.markdown("<h1 style='text-align: center; color: #ff1744;'>SYNAPSE</h1>", unsafe_allow_html=True)

# --- 3. เข้าสู่ระบบ Hierarchy ของเพี้ยนต่อได้เลย ---
st.markdown("<h3 style='text-align: center; color: #00f2fe; opacity: 0.8;'>อยู่นิ่งๆ ไม่เจ็บตัว</h3>", unsafe_allow_html=True)
st.write("---")

# --- 1. ตั้งค่าหน้าเว็บและลบติ่ง Streamlit (Footer/Header/Menu) ---
st.set_page_config(page_title="SYNAPSE 4-1", layout="wide")

def hide_streamlit_style():
    st.markdown("""
        <style>
        /* ลบแถบเมนูข้างบน และเครดิตข้างล่าง */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* ปรับพื้นหลังให้ดำสนิทแบบระบบ Command */
        .stApp { background-color: #000000; }
        </style>
        """, unsafe_allow_html=True)

hide_streamlit_style()

# --- 2. ฟังก์ชันดึงรูป logo1.png มาแสดงแบบไร้กรอบ ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def display_logo(file_path):
    try:
        bin_str = get_base64_of_bin_file(file_path)
        # ปรับ CSS ให้โลโก้มีเงาสีแดงจางๆ (Neon) จะได้ดูเท่ๆ
        st.markdown(f"""
            <div style="text-align: center;">
                <img src="data:image/png;base64,{bin_str}" style="width: 120px; filter: drop-shadow(0 0 10px #ff1744);">
            </div>
        """, unsafe_allow_html=True)
    except:
        # ถ้าหาไฟล์ไม่เจอ ให้โชว์เป็นข้อความแทน (ป้องกัน Error)
        st.markdown("<h2 style='text-align: center; color: #ff1744;'>SYNAPSE 4-1</h2>", unsafe_allow_html=True)

# เรียกใช้โลโก้ (ดึงจากโฟลเดอร์ static ที่เพี้ยนทำไว้)
display_logo("static/logo1.png")

# --- หลังจากนี้ก็ใส่โค้ด Hierarchy (ระบบคุมชั้น) ของเพี้ยนต่อได้เลย ---
st.markdown("<h3 style='text-align: center; color: #00f2fe;'>อยู่นิ่งๆ ไม่เจ็บตัว</h3>", unsafe_allow_html=True)
st.write("---")

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
