import streamlit as st
import time

# --- 1. SET PAGE CONFIG (อันดับแรก) ---
st.set_page_config(
    page_title="SYNAPSE - 4 in 1 OVERLAY",
    layout="centered", # Centered คุมทรงบนมือถือได้ดีกว่า
    initial_sidebar_state="collapsed"
)

# --- 2. CUSTOM CSS (จัดเต็มแสงสี ซ่อนเมนู และทำ Overlay) ---
st.markdown("""
    <style>
    /* ซ่อนส่วนประกอบ Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="stAppViewContainer"] {background-color: #000000;}
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }

    /* --- ส่วนสำคัญ: CSS สำหรับ Overlay --- */
    /* กรอปคลุมวิดีโอ */
    .video-container {
        position: relative;
        width: 100%;
        border-radius: 10px;
        overflow: hidden; /* กันตัวหนังสือล้น */
        border: 2px solid #444;
        box-shadow: 0 0 20px rgba(255, 75, 75, 0.2);
    }

    /* ตัว Video Player */
    .video-container video {
        width: 100% !important;
        display: block;
    }

    /* กล่องตัวหนังสือวิ่ง (วางทับด้านบน) */
    .marquee-overlay {
        position: absolute;
        top: 0;  /* วางชิดขอบบนของวิดีโอ */
        left: 0;
        width: 100%;
        background: rgba(0, 0, 0, 0.6); /* พื้นหลังดำโปร่งแสง */
        padding: 8px 0;
        z-index: 10; /* ให้ลอยอยู่เหนือวิดีโอ */
        border-bottom: 1px solid rgba(255, 75, 75, 0.5);
    }
    /* ----------------------------------- */

    /* ตกแต่งปุ่ม BROADCAST */
    .stButton>button {
        background-color: #1E1E1E;
        color: #FF4B4B;
        border: 2px solid #FF4B4B;
        border-radius: 20px;
        box-shadow: 0 0 10px #FF4B4B;
        font-weight: bold;
        transition: 0.3s;
        margin-top: 15px;
    }
    .stButton>button:hover {
        background-color: #FF4B4B;
        color: white;
        box-shadow: 0 0 25px #FF4B4B;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ส่วนหัวข้อแอป (ทำให้น้อยลงเพื่อให้พื้นที่วิดีโอเด่น) ---
st.markdown("""
    <div style='text-align: center;'>
        <h1 style='color: #FF4B4B; text-shadow: 0 0 15px #FF4B4B; margin-bottom: 0px; font-size: 28px;'>📡 SYNAPSE 4-1</h1>
        <p style='color: #666; font-size: 12px; margin-top: 0px;'>อยู่นิ่งๆ ไม่เจ็บตัว</p>
    </div>
    """, unsafe_allow_html=True)

# --- 4. เนื้อเพลงมหากาพย์ (รวม 4 เพลง) ---
mega_lyrics = """
[เริ่ม] วันหนึ่งถ้าเธมองย้อนกลับมา... อาจจะเห็นสิ่งที่เคยทำพังลงไป... แต่ถึงตอนนั้น ฉันคงเดินไกล... ทิ้งเรื่องของเราไว้ในอดีตคำที่เธอเคยให้... 
[ความจริง] ความจริงที่ฉันให้ไป จะเอาไปทิ้งไว้ที่ไหน ในวันที่ฉันจริงใจ แต่เธอทิ้งไปเหมือนเป็นแค่ของเล่น... 
[ขอบคุณ] ขอบคุณถ้อยคำที่เคยทำฉันร้าว คำที่ทำให้ใจฉันแทบไม่เหลืออะไร กลับกลายเป็นทางให้ฉันหันมาเจอแสงในตัวเอง... 
[ปล่อยวาง] ปล่อยวางความโกรธที่เผาใจ ทิ้งความโลภที่ไม่มีวันพอ อยู่นิ่งๆ ไม่เจ็บตัว แค่รู้เท่าทันแล้ววางลงตรงนี้...
"""

# --- 5. ส่วนวิดีโอแบบ Overlay (ชื่อไฟล์ตรงเป๊ะตามที่คุณบอก) ---
try:
    with open('วันที่ขอบคุณไม่มีใคร 4-1 ปล่อยวาง.mp4', 'rb') as v_file:
        video_bytes = v_file.read()
        
        # ใช้ HTML เพื่อสร้าง Structure สำหรับ Overlay
        st.markdown(f"""
            <div class="video-container">
                <div class="marquee-overlay">
                    <marquee scrollamount="8" style="color: #FF4B4B; font-size: 18px; font-weight: bold; font-family: 'Kanit', sans-serif;">
                        {mega_lyrics}
                    </marquee>
                </div>
                <video autoplay loop muted playsinline>
                    <source src="data:video/mp4;base64,{st.base64_encode(video_bytes)}" type="video/mp4">
                </video>
            </div>
            """, unsafe_allow_html=True)
except FileNotFoundError:
    st.info("💡 รอไฟล์มหากาพย์: วันที่ขอบคุณไม่มีใคร 4-1 ปล่อยวาง.mp4")

# --- 6. ส่วนเสียง (Audio Player) ---
# เผื่อวิดีโอไม่มีเสียง หรืออยากเปิดแยก
try:
    with open('วันที่ขอบคุณไม่มีใคร 4-1 ปล่อยวาง.mp3', 'rb') as a_file:
        st.audio(a_file.read(), format='audio/mp3')
except FileNotFoundError:
    pass 

# --- 7. ปุ่ม BROADCAST ---
b_col1, b_col2, b_col3 = st.columns([1, 2, 1])
with b_col2:
    if st.button("📡 BROADCAST 4-1 SIGNAL", use_container_width=True):
        st.success("ส่งสัญญาณครบ 4 ภาค: ปล่อยวางโดยสมบูรณ์")
