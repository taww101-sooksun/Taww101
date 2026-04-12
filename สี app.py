import streamlit as st
import time

# --- 1. SET PAGE CONFIG (ต้องอยู่อันดับแรกเสมอ) ---
st.set_page_config(
    page_title="SYNAPSE - BROADCAST",
    page_icon="📡",
    layout="wide", # ใช้แบบกว้างจะดูเต็มตาเวลาลง YouTube
    initial_sidebar_state="collapsed"
)

# --- 2. CUSTOM CSS (จัดเต็มแสงสีและซ่อนเมนู) ---
st.markdown("""
    <style>
    /* ซ่อนส่วนประกอบ Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ปรับพื้นหลังและสี Font */
    [data-testid="stAppViewContainer"] {
        background-color: #000000;
        color: #FF4B4B;
    }
    
    /* ปรับแต่งปุ่มให้ดูมีแสงนีออน */
    .stButton>button {
        background-color: #1E1E1E;
        color: #FF4B4B;
        border: 2px solid #FF4B4B;
        border-radius: 20px;
        box-shadow: 0 0 10px #FF4B4B;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #FF4B4B;
        color: white;
        box-shadow: 0 0 25px #FF4B4B;
    }

    /* ตกแต่ง Marquee */
    .marquee-container {
        background: rgba(255, 75, 75, 0.1);
        border-top: 2px solid #FF4B4B;
        border-bottom: 2px solid #FF4B4B;
        padding: 10px 0;
        margin: 20px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. เนื้อเพลง (จัดรูปแบบเป็นบรรทัดเดียวเพื่อให้วิ่งยาวๆ) ---
lyrics = " [Verse 1] ขอบคุณถ้อยคำที่เคยทำฉันร้าว... [Chorus] ขอบคุณทุกคำที่เคยทำให้ฉันเจ็บ... คงไม่รู้เลยว่าฉันเข้มแข็งแค่ไหน... มันปลุกคนใหม่ให้ลุกขึ้นเดินไป... ถึงเดินไปเพียงลำพัง... ก็มีฉันคนนี้... ที่ไม่กลัวอีกต่อไป... (โอ้ฮู้) [Verse 2] ขอบคุณรอยช้ำที่เคยทำให้ฉันท้อ... มันสอนให้ฉันกอดตัวเองแน่นกว่าเดิม... ฉันได้ยินเสียงหัวใจตัวเองดังชัดกว่าครั้งไหน..."

# --- 4. การแสดงผลหน้าจอ ---

# หัวข้อหลัก
st.markdown("<h1 style='text-align: center; color: #FF4B4B; text-shadow: 2px 2px 10px #FF4B4B;'>📡 SYNAPSE</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>สโลแกน: อยู่นิ่งๆ ไม่เจ็บตัว</p>", unsafe_allow_html=True)

# ตัวหนังสือวิ่ง
st.markdown(f"""
    <div class="marquee-container">
        <marquee scrollamount="10" style="font-size: 24px; font-weight: bold;">
            {lyrics}
        </marquee>
    </div>
    """, unsafe_allow_html=True)

# จัดการ Media (Video & Audio)
# ใช้ columns 5 ช่อง เพื่อบีบช่องกลางให้วิดีโอเล็กลงและดูเด่น (Ratio: 1:1:2:1:1)
empty1, empty2, main_col, empty3, empty4 = st.columns([1, 0.5, 2, 0.5, 1])

with main_col:
    # ส่วนวิดีโอ
    try:
        with open('video.mp4', 'rb') as v_file:
            st.video(v_file.read())
    except FileNotFoundError:
        st.info("📍 ระบบพร้อมใช้งาน: รอการเชื่อมต่อไฟล์วิดีโอ (video.mp4)")

    # ส่วนเสียง
    try:
        with open('music.mp3', 'rb') as a_file:
            st.audio(a_file.read(), format='audio/mp3')
    except FileNotFoundError:
        st.info("📍 ระบบพร้อมใช้งาน: รอการเชื่อมต่อไฟล์เสียง (music.mp3)")

st.write("") # เว้นวรรค

# --- 5. ปุ่ม BROADCAST ---
# ใช้ columns เพื่อบีบปุ่มให้ขนาดพอดี ไม่ยาวเกินไป
b_col1, b_col2, b_col3 = st.columns([1, 2, 1])
with b_col2:
    if st.button("📡 BROADCAST MY SIGNAL", use_container_width=True):
        try:
            # จำลองการทำงาน (ใส่ logic Firebase ของคุณที่นี่)
            progress_bar = st.progress(0)
            for percent_complete in range(100):
                time.sleep(0.01)
                progress_bar.progress(percent_complete + 1)
            
            st.toast("SIGNAL BROADCASTED TO NETWORK", icon="🛰️")
            st.success("DATA TRANSMISSION COMPLETE")
            
        except Exception as e:
            st.error(f"SYSTEM ERROR: {e}")

# --- 6. เพิ่มลูกเล่นด้านล่าง ---
st.markdown("<br><br><p style='text-align: center; color: #333;'>SECURE CONNECTION ACTIVE | SYSTEM v3.0</p>", unsafe_allow_html=True)
