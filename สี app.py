import streamlit as st
import time

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="SYNAPSE - 4 in 1", layout="centered", initial_sidebar_state="collapsed")

# --- 2. CUSTOM CSS (ธีมมืดนีออนแดง) ---
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="stAppViewContainer"] {background-color: #000000;}
    .block-container {padding-top: 1.5rem !important;}
    .marquee-box {
        background: rgba(255, 75, 75, 0.05);
        border: 2px solid #FF4B4B;
        border-radius: 10px;
        padding: 15px;
        margin: 20px 0;
        box-shadow: 0 0 20px rgba(255, 75, 75, 0.2);
    }
    video {border-radius: 15px; border: 1px solid #444; width: 100% !important;}
    </style>
    """, unsafe_allow_html=True)

# --- 3. ส่วนหัวข้อ ---
st.markdown("<div style='text-align: center;'><h1 style='color: #FF4B4B; text-shadow: 0 0 15px #FF4B4B;'>📡 SYNAPSE 4-1</h1><p style='color: #888;'>รวม 4 ใจ เป็น 1 สัญญาณ</p></div>", unsafe_allow_html=True)

# --- 4. ส่วนวิดีโอและเสียง ---
try:
    with open('วันที่ขอบคุณไม่มีใคร 4-1 ปล่อยวาง.mp4', 'rb') as v_file:
        st.video(v_file.read())
except FileNotFoundError:
    st.info("💡 รอไฟล์มหากาพย์ 4-1 ของคุณอยู่ครับ")

# --- 5. เนื้อเพลงมหากาพย์ (รวม 4 เพลง) ---
mega_lyrics = """
[เริ่ม] วันหนึ่งถ้าเธอมองย้อนกลับมา อาจจะเห็นสิ่งที่เคยทำพังลงไป แต่ถึงตอนนั้น ฉันคงเดินไกล... 
[ความจริง] ความจริงที่ฉันให้ไป จะเอาไปทิ้งไว้ที่ไหน ในวันที่ฉันจริงใจ แต่เธอทิ้งไปเหมือนเป็นแค่ของเล่น... 
[ขอบคุณ] ขอบคุณถ้อยคำที่เคยทำฉันร้าว คำที่ทำให้ใจฉันแทบไม่เหลืออะไร กลับกลายเป็นทางให้ฉันหันมาเจอแสงในตัวเอง... 
[ปล่อยวาง] ปล่อยวางความโกรธที่เผาใจ ทิ้งความโลภที่ไม่มีวันพอ อยู่นิ่งๆ ไม่เจ็บตัว แค่รู้เท่าทันแล้ววางลงตรงนี้...
"""

st.markdown(f"""
    <div class="marquee-box">
        <marquee scrollamount="8" style="color: #FF4B4B; font-size: 22px; font-weight: bold; font-family: 'Kanit', sans-serif;">
            {mega_lyrics}
        </marquee>
    </div>
    """, unsafe_allow_html=True)

# --- 6. ปุ่ม BROADCAST ---
if st.button("📡 BROADCAST 4-1 SIGNAL", use_container_width=True):
    st.success("ส่งสัญญาณครบ 4 ภาค: ปล่อยวางโดยสมบูรณ์")
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
