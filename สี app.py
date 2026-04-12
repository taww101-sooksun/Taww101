import streamlit as st
import time
import streamlit as st

# โค้ดสำหรับซ่อนส่วนประกอบของ Streamlit
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;} /* ซ่อนเมนูขวาบน (Hamburger Menu) */
            footer {visibility: hidden;}    /* ซ่อนคำว่า "Made with Streamlit" ด้านล่าง */
            header {visibility: hidden;}    /* ซ่อนแถบ Header ด้านบนสุด */
            
            /* กรณีต้องการให้ระยะขอบด้านบนหายไปด้วย (ทำให้หน้าแอปชิดขอบบน) */
            .block-container {
                padding-top: 1rem;
                padding-bottom: 1rem;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- ต่อจากตรงนี้คือโค้ดหน้าจอแอปของคุณ ---
st.title("SYNAPSE อยู่นิ้งๆไม่เจ็บตัว")

# --- การตั้งค่าเบื้องต้น ---
st.set_page_config(page_title="My Signal App", layout="centered")

# --- 1. ส่วนเนื้อเพลงวิ่ง (Marquee) ---
lyrics = "[Verse 1]
ขอบคุณถ้อยคำที่เคยทำฉันร้าว
คำที่ทำให้ใจฉันแทบไม่เหลืออะไร
คืนที่ร้องไห้จนไม่รู้จะไปทางไหน
กลับกลายเป็นทางให้ฉันหันมาเจอแสงในตัวเอง

[Chorus]
ขอบคุณทุกคำที่เคยทำให้ฉันเจ็บ
คงไม่รู้เลยว่าฉันเข้มแข็งแค่ไหน
มันปลุกคนใหม่ให้ลุกขึ้นเดินไป
ถึงเดินไปเพียงลำพัง
ก็มีฉันคนนี้
ที่ไม่กลัวอีกต่อไป (โอ้ฮู้)

[Verse 2]
ขอบคุณรอยช้ำที่เคยทำให้ฉันท้อ
มันสอนให้ฉันกอดตัวเองแน่นกว่าเดิม
วันที่ไม่มีใครอยู่ข้างกันเหมือนก่อน
ฉันได้ยินเสียงหัวใจตัวเองดังชัดกว่าครั้งไหน

[Chorus]
ขอบคุณทุกคำที่เคยทำให้ฉันเจ็บ
คงไม่รู้เลยว่าฉันเข้มแข็งแค่ไหน
มันปลุกคนใหม่ให้ลุกขึ้นเดินไป
ถึงเดินไปเพียงลำพัง
ก็มีฉันคนนี้
ที่ไม่กลัวอีกต่อไป (ไม่กลัวอีกต่อไป)"

st.markdown(
    f"""
    <div style="background-color: #1E1E1E; padding: 15px; border-radius: 10px; border: 2px solid #FF4B4B; margin-bottom: 20px;">
        <marquee behavior="scroll" direction="left" scrollamount="8" style="color: #FF4B4B; font-size: 20px; font-weight: bold; font-family: 'Kanit', sans-serif;">
            {lyrics}
        </marquee>
    </div>
    """,
    unsafe_allow_html=True
)

# --- 2. ส่วนวิดีโอและเสียง (Media) ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎥 Video")
    # ใส่ชื่อไฟล์ .mp4 ของคุณตรงนี้
    try:
        video_file = open('video.mp4', 'rb')
        st.video(video_file.read())
    except FileNotFoundError:
        st.warning("ไม่พบไฟล์ video.mp4")

with col2:
    st.markdown("### 🎵 Audio")
    # ใส่ชื่อไฟล์ .mp3 ของคุณตรงนี้
    try:
        audio_file = open('music.mp3', 'rb')
        st.audio(audio_file.read(), format='audio/mp3')
    except FileNotFoundError:
        st.warning("ไม่พบไฟล์ music.mp3")

st.divider() # เส้นคั่นกลางหน้า

# --- 3. ส่วนปุ่ม BROADCAST (อันที่คุณเขียนตอนแรก) ---
# ผมใส่ try...except เพื่อป้องกันแอปพังถ้ายังไม่ได้ต่อ Firebase
if st.button("📡 BROADCAST MY SIGNAL", use_container_width=True):
    try:
        # สมมติว่าตั้งค่า db และตัวแปรตำแหน่งไว้แล้ว
        # my_lat, my_lon = 13.75, 100.50 
        
        if 'user' in st.session_state:
            # db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
            st.toast("SIGNAL BROADCASTED TO NETWORK", icon="🛰️")
        else:
            st.error("กรุณาระบุตัวตนใน session_state ก่อน")
            
    except NameError:
        st.error("ตัวแปร db หรือตำแหน่ง ยังไม่ได้ถูกกำหนดค่า")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาด: {e}")
