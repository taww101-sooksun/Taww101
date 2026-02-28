import streamlit as st

# --- 1. ตัวเชื่อมสถานะ (หัวใจหลัก) ---# --- เริ่มรันระบบ ---
setup_ui()          # เรียกใช้หน้าตา
init_firebase()     # เชื่อมฐานข้อมูล
music_url = play_audio() # สั่งเปิดเพลง

# แสดงส่วนหัว (Logo + Clocks)
# ... โค้ดส่วนหัว ...

# สร้าง Tabs แล้วส่งไปให้ฟังก์ชัน render_tabs จัดการ
main_tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "📊 LOG", "🔐 SEC", "📺 MEDIA", "🧹 SYS"])
render_tabs(main_tabs, music_url)

if 'nav_level' not in st.session_state:
    st.session_state.nav_level = "HOME" # หน้าแรก

# --- 2. ฟังก์ชันวาดกรอบ (UI Style) ---def setup_ui():
    st.markdown("""
        <style>
        .stApp { background: radial-gradient(circle, #001 0%, #000 100%); color: #00f2fe; }
        .neon-header { 
            font-size: 40px; font-weight: 900; text-align: center;
            color: #fff; text-shadow: 0 0 15px #ff1744, 0 0 20px #00f2fe;
            border: 10px double #ff1744; padding: 20px; border-radius: 20px;
        }
        /* ... (โค้ด CSS อื่นๆ ที่เหลือ) ... */
        </style>
    """, unsafe_allow_html=True)

def draw_box(title, target_level):
    # วาดกรอบสวยๆ แบบที่เพื่อนชอบ
    if st.button(title, use_container_width=True):
        st.session_state.nav_level = target_level
        st.rerun()
def setup_ui():
    st.markdown("""
        <style>
        .stApp { background: radial-gradient(circle, #001 0%, #000 100%); color: #00f2fe; }
        .neon-header { 
            font-size: 40px; font-weight: 900; text-align: center;
            color: #fff; text-shadow: 0 0 15px #ff1744, 0 0 20px #00f2fe;
            border: 10px double #ff1744; padding: 20px; border-radius: 20px;
        }
        /* ... (โค้ด CSS อื่นๆ ที่เหลือ) ... */
        </style>
    """, unsafe_allow_html=True)

# --- 3. การประกอบร่าง ---
st.title("SYNAPSE HIERARCHY SYSTEM")

# ปุ่มย้อนกลับ (อยู่นิ่งๆ ไม่เจ็บตัว ต้องมีทางถอย!)
if st.session_state.nav_level != "HOME":
    if st.button("⬅️ BACK"):
        # วิธีถอยกลับแบบฉลาด
        if "." in st.session_state.nav_level:
            # ตัดเลขท้ายออก เช่น 1.1.1 -> 1.1
            st.session_state.nav_level = ".".join(st.session_state.nav_level.split(".")[:-1])
        else:
            st.session_state.nav_level = "HOME"
        st.rerun()

st.write(f"CURRENT PATH: **{st.session_state.nav_level}**")
st.markdown("---")

# --- 4. ระบบคุมชั้น (Navigation Logic) ---

# ชั้นที่ 0: หน้าแรก
if st.session_state.nav_level == "HOME":
    c1, c2 = st.columns(2)
    with c1: draw_box("กรอบที่ 1", "1")
    with c2: draw_box("กรอบที่ 2", "2")
    with c1: draw_box("กรอบที่ 3", "3")
    with c2: draw_box("กรอบที่ 4", "4")

# ชั้นที่ 1: เมื่อเจาะจงเลข 1
elif st.session_state.nav_level == "1":
    c1, c2 = st.columns(2)
    with c1: draw_box("กรอบที่ 1.1", "1.1")
    with c2: draw_box("กรอบที่ 1.2", "1.2")
    with c1: draw_box("กรอบที่ 1.3", "1.3")
    with c2: draw_box("กรอบที่ 1.4", "1.4")

# ชั้นที่ 2: เมื่อเจาะจงเลข 1.1
elif st.session_state.nav_level == "1.1":
    c1, c2 = st.columns(2)
    with c1: draw_box("กรอบที่ 1.1.1", "1.1.1")
    with c2: draw_box("กรอบที่ 1.1.2", "1.1.2")
    with c1: draw_box("กรอบที่ 1.1.3", "1.1.3")
    with c2: draw_box("กรอบที่ 1.1.4", "1.1.4")

# ชั้นอื่นๆ (สมมุติว่ายังไม่ได้ทำเนื้อหา)
else:
    st.warning(f"ระบบส่วน {st.session_state.nav_level} กำลังพัฒนา...")
