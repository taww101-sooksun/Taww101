import streamlit as st
import time

# --- 1. SET PAGE CONFIG ---
st.set_page_config(
    page_title="SYNAPSE",
    layout="centered",  # ใช้ centered จะคุมทรงบนมือถือได้นิ่งกว่า
    initial_sidebar_state="collapsed"
)

# --- 2. CUSTOM CSS (เน้นแก้หน้าจอมือถือโดยเฉพาะ) ---
st.markdown("""
    <style>
    /* ซ่อนส่วนประกอบ Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* ปรับพื้นหลัง */
    [data-testid="stAppViewContainer"] {
        background-color: #000000;
    }

    /* จัดการระยะขอบหน้าจอให้พอดีเป๊ะ ไม่เหลือขอบขาวเยอะ */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }
    
    /* ตกแต่งกรอบตัวหนังสือวิ่งให้พอดี */
    .marquee-box {
        background: rgba(255, 75, 75, 0.1);
        border: 2px solid #FF4B4B;
        border-radius: 5px;
        padding: 5px;
        margin: 10px 0;
        overflow: hidden; /* กันตัวหนังสือหลุดกรอบ */
    }

    /* ปรับขนาดวิดีโอให้พอดีหน้าจอ */
    video {
        width: 100% !important;
        border-radius: 10px;
        border: 1px solid #333;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. การแสดงผลหน้าจอ ---

# โลโก้และชื่อ (ใส่แสงฟุ้ง)
st.markdown("""
    <div style='text-align: center;'>
        <h1 style='color: #FF4B4B; text-shadow: 0 0 15px #FF4B4B; margin-bottom: 0px;'>📡 SYNAPSE</h1>
        <p style='color: #888; font-size: 14px;'>สโลแกน: อยู่นิ่งๆ ไม่เจ็บตัว</p>
    </div>
    """, unsafe_allow_html=True)

# เนื้อเพลง (แก้ให้แสดงผลต่อเนื่อง)
lyrics = "ขอบคุณทุกคำที่เคยทำให้ฉันเจ็บ... คงไม่รู้เลยว่าฉันเข้มแข็งแค่ไหน... มันปลุกคนใหม่ให้ลุกขึ้นเดินไป... ถึงเดินไปเพียงลำพัง... ก็มีฉันคนนี้... ที่ไม่กลัวอีกต่อไป..."

# ตัวหนังสือวิ่ง (ใส่ใน div class ที่เราแต่งไว้)
st.markdown(f"""
    <div class="marquee-box">
        <marquee scrollamount="7" style="color: #FF4B4B; font-size: 20px; font-weight: bold; font-family: 'Kanit', sans-serif;">
            {lyrics}
        </marquee>
    </div>
    """, unsafe_allow_html=True)

# --- 4. ส่วนวิดีโอ (เน้นเต็มจอพอดีเป๊ะ) ---
try:
    with open('video.mp4', 'rb') as v_file:
        # ไม่ต้องใส่คอลัมน์แล้ว เพื่อให้มันขยายเต็มที่ในมือถือ
        st.video(v_file.read())
except FileNotFoundError:
    st.info("📍 รอไฟล์ video.mp4")

# --- 5. ปุ่ม BROADCAST (ดีไซน์นีออน) ---
st.markdown("<br>", unsafe_allow_html=True)
if st.button("📡 BROADCAST MY SIGNAL", use_container_width=True):
    st.toast("TRANSMITTING...", icon="⚡")
    time.sleep(1)
    st.toast("SIGNAL BROADCASTED!", icon="🛰️")

# ซ่อนเพลงไว้เบื้องหลัง (เพราะในวิดีโอมีเพลงอยู่แล้ว จะได้ไม่ตีกัน)
# ถ้าต้องการเปิดเพลงแยกค่อยเพิ่ม st.audio ครับ
