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
        border-radius: px;
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
