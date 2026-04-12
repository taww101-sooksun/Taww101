import streamlit as st
import time

# --- 1. SET PAGE CONFIG ---
st.set_page_config(
    page_title="SYNAPSE",
    layout="centered", 
    initial_sidebar_state="collapsed"
)

# --- 2. CUSTOM CSS (จัดระเบียบให้พอดีจอ) ---
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="stAppViewContainer"] {background-color: #000000;}
    
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* กรอบตัวหนังสือวิ่ง */
    .marquee-box {
        background: rgba(255, 75, 75, 0.1);
        border: 2px solid #FF4B4B;
        border-radius: 8px;
        padding: 12px;
        margin-top: 15px;
        box-shadow: 0 0 15px rgba(255, 75, 75, 0.3);
    }

    /* ตกแต่งวิดีโอ */
    video {
        border-radius: 12px;
        border: 2px solid #333;
        width: 100% !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ส่วนหัวข้อ ---
st.markdown("""
    <div style='text-align: center;'>
        <h1 style='color: #FF4B4B; text-shadow: 0 0 20px #FF4B4B; margin-bottom: 0px;'>📡 SYNAPSE</h1>
        <p style='color: #666; font-size: 14px;'>อยู่นิ่งๆ ไม่เจ็บตัว</p>
    </div>
    """, unsafe_allow_html=True)

# --- 4. ส่วนวิดีโอ (เอาขึ้นก่อนเพื่อให้เด่น) ---
try:
    with open('video.mp4', 'rb') as v_file:
        st.video(v_file.read())
except FileNotFoundError:
    st.info("📍 ระบบพร้อม: รอไฟล์ video.mp4")

# --- 5. เนื้อเพลงแบบเต็ม (ใช้เครื่องหมายอัญประกาศ 3 อันเพื่อให้เนื้อความครบ) ---
full_lyrics = """
[Verse 1] ขอบคุณถ้อยคำที่เคยทำฉันร้าว คำที่ทำให้ใจฉันแทบไม่เหลืออะไร คืนที่ร้องไห้จนไม่รู้จะไปทางไหน กลับกลายเป็นทางให้ฉันหันมาเจอแสงในตัวเอง --- 
[Chorus] ขอบคุณทุกคำที่เคยทำให้ฉันเจ็บ คงไม่รู้เลยว่าฉันเข้มแข็งแค่ไหน มันปลุกคนใหม่ให้ลุกขึ้นเดินไป ถึงเดินไปเพียงลำพัง ก็มีฉันคนนี้ ที่ไม่กลัวอีกต่อไป (โอ้ฮู้) --- 
[Verse 2] ขอบคุณรอยช้ำที่เคยทำให้ฉันท้อ มันสอนให้ฉันกอดตัวเองแน่นกว่าเดิม วันที่ไม่มีใครอยู่ข้างกันเหมือนก่อน ฉันได้ยินเสียงหัวใจตัวเองดังชัดกว่าครั้งไหน --- 
[Chorus] ขอบคุณทุกคำที่เคยทำให้ฉันเจ็บ คงไม่รู้เลยว่าฉันเข้มแข็งแค่ไหน มันปลุกคนใหม่ให้ลุกขึ้นเดินไป ถึงเดินไปเพียงลำพัง ก็มีฉันคนนี้ ที่ไม่กลัวอีกต่อไป
"""

# แสดงตัวหนังสือวิ่งใต้คลิป
st.markdown(f"""
    <div class="marquee-box">
        <marquee scrollamount="8" style="color: #FF4B4B; font-size: 22px; font-weight: bold; font-family: 'Kanit', sans-serif;">
            {full_lyrics}
        </marquee>
    </div>
    """, unsafe_allow_html=True)

# --- 6. ปุ่ม BROADCAST ---
st.markdown("<br>", unsafe_allow_html=True)
if st.button("📡 BROADCAST MY SIGNAL", use_container_width=True):
    with st.spinner('Broadcasting...'):
        time.sleep(1)
        st.toast("SIGNAL SENT TO NETWORK", icon="🛰️")
