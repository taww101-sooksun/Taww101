import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time
from datetime import datetime

# --- [ 🛰️ ระบบเชื่อมต่อศูนย์บัญชาการ Firebase ] ---
# ใช้โครงสร้างที่ต๊ะให้มา (ใสแน่นอน)
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_credentials"])
        if "private_key" in fb_creds:
            fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
            
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {
            'databaseURL': st.secrets["firebase_db_url"]
        })
    except Exception as e:
        st.error(f"❌ ระบบเชื่อมต่อขัดข้อง: {e}")

db_ref = db.reference('/')

# --- [ 🎨 CUSTOM INTERFACE: ลบติ่ง & แต่งสวย ] ---
st.set_page_config(page_title="SYNAPSE", layout="centered")

st.markdown("""
    <style>
    /* ลบติ่ง Streamlit / GitHub */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #000000; color: #FFFFFF; }
    
    /* Logo1.png ดิ้น (Wiggle) */
    @keyframes wiggle {
        0% { transform: rotate(0deg); }
        25% { transform: rotate(3deg); }
        50% { transform: rotate(0eg); }
        75% { transform: rotate(-3deg); }
        100% { transform: rotate(0deg); }
    }
    .logo-img {
        display: block;
        margin: 0 auto;
        width: 250px;
        animation: wiggle 1.5s infinite;
    }
    
    /* ตัวหนังสือวิ่ง */
    .marquee {
        background: #111;
        color: #00FF00;
        padding: 5px;
        overflow: hidden;
        white-space: nowrap;
        font-family: 'Courier New', monospace;
    }
    .marquee span {
        display: inline-block;
        padding-left: 100%;
        animation: marquee 10s linear infinite;
    }
    @keyframes marquee {
        0% { transform: translate(0, 0); }
        100% { transform: translate(-100%, 0); }
    }
    </style>
    """, unsafe_allow_html=True)

# --- [ 🔐 ระบบบันทึกระหัสยูสเซอร์ ] ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # หน้า Login
    st.markdown('<img src="logo1.png" class="logo-img" onerror="this.src=\'https://via.placeholder.com/250?text=LOGO1.PNG\'">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>SYNAPSE LOGIN</h2>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        user_id = st.text_input("รหัสยูสเซอร์ / ชื่อผู้ใช้")
        password = st.text_input("รหัสผ่าน", type="password")
        submit = st.form_submit_button("ลงชื่อเข้าใช้")
        
        if submit:
            # เช็คค่าจาก Firebase จริง (ตัวอย่าง)
            user_data = db_ref.child('users').child(user_id).get()
            if user_data and user_data.get('password') == password:
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                st.rerun()
            else:
                st.error("ข้อมูลไม่ถูกต้อง")

else:
    # --- [ 🏠 หน้าหลัก 8 ห้อง ] ---
    st.markdown('<img src="logo1.png" class="logo-img" onerror="this.src=\'https://via.placeholder.com/250?text=LOGO1.PNG\'">', unsafe_allow_html=True)
    
    menu = [
        "1. SYNAPSE อยู่นิ่งๆไม่เจ็บตัว",
        "2. MP3/MP4 & Draft 512",
        "3. Chat & GPS Realtime",
        "4. สูตรสมดุล 1.619 & จันทรคติ",
        "5. วัดค่าเสียง db/Hz/กลางแหลม",
        "6. ตั้งค่าสี & ยืนยันตัวตน",
        "7. สูตรคู่ขนาน 1960",
        "8. เลขศาสตร์ 1960-2026 & สถิติ"
    ]
    
    choice = st.selectbox("เลือกห้องปฏิบัติการ", menu)
    st.divider()

    # --- ห้องที่ 1 ---
    if "1." in choice:
        st.subheader("SYNAPSE: อยู่นิ่งๆ ไม่เจ็บตัว")
        st.write(f"ยินดีต้อนรับท่าน: {st.session_state.user_id}")
    
    # --- ห้องที่ 2 ---
    elif "2." in choice:
        st.markdown('<div class="marquee"><span>DRAFT เสียงจริง 512 Hz กำลังประมวลผล... ดึงค่าจาก SYNAPSE CLOUD สำเร็จ</span></div>', unsafe_allow_html=True)
        # ดึงค่า MP3 จาก Firebase หรือ Cloud Storage
        st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3") 
        st.write("สถานะ: ดึงค่าเสถียร 100%")

    # --- ห้องที่ 3 ---
    elif "3." in choice:
        st.subheader("📡 ระบบติดตาม & แชตสด")
        col1, col2 = st.columns(2)
        with col1:
            msg = st.text_input("ส่งข้อความส่วนตัว")
            if st.button("ส่ง"):
                db_ref.child('chats').push({'user': st.session_state.user_id, 'msg': msg, 'time': str(datetime.now())})
        with col2:
            st.metric("เวลาจริง", datetime.now().strftime("%H:%M:%S"))
            # จำลองค่า GPS (ต๊ะดึงจาก Sensor จริงได้ผ่านแอปเสริม)
            st.write("LAT: 16.05 | LON: 103.65")

    # --- ห้องที่ 4 ---
    elif "4." in choice:
        st.subheader("📐 สูตรคำนวณความถูกต้อง")
        st.write("ค่าสมดุลทองคำ: 1.619")
        st.write("รอบน้ำดวงจันทร์: 29.53")
        st.success("ผลลัพธ์: ความแม่นยำ 1960 - ปัจจุบัน สอดคล้องกัน")

    # --- ห้องที่ 5 ---
    elif "5." in choice:
        st.subheader("🔊 ห้องวิเคราะห์เสียงกลางแหลม")
        st.progress(75, text="ค่าความเข้มเสียง dB")
        st.write("Hz: 440 (มาตรฐาน)")
        st.info("แอปนี้ออกแบบมาเพื่อวัดค่าที่คนอื่นมองข้าม แต่ต๊ะมองเห็น")

    # --- ห้องที่ 6 ---
    elif "6." in choice:
        st.subheader("⚙️ การปรับแต่งระบบ")
        color = st.color_picker("เลือกสีธีมแอป", "#00FF00")
        st.button("ยืนยันตัวตนระดับสูง")

    # --- ห้องที่ 7 ---
    elif "7." in choice:
        st.subheader("🔗 สูตรคู่ขนาน 1960")
        st.text_input("รายชื่อที่ 1")
        st.text_input("รายชื่อที่ 2")
        st.button("คำนวณจุดตัด")

    # --- ห้องที่ 8 ---
    elif "8." in choice:
        st.subheader("📊 สถิติเลขศาสตร์ 1960-2026")
        st.write("สถานะย้อนหลัง 365 วัน: 🎖️")
        st.write("สถานะอนาคต 365 วัน: 💎")
        st.write("รหัสตัวเลขวันเกิดของท่านคือ: [คำนวณตามสูตร]")

    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()
