import streamlit as st
import time
import base64
import streamlit as st

# --- ส่วนค้นหารูปภาพอัตโนมัติ ---
st.markdown("### 🔍 ค้นหาภาพพื้นหลัง")
search_query = st.text_input("พิมพ์แนวภาพที่ต้องการ (ภาษาอังกฤษ):", "abstract dark red")

if search_query:
    # สร้าง URL สำหรับดึงรูปจาก Unsplash แบบสุ่มตามคำค้นหา
    # ขนาด 800x400 เพื่อให้เหมาะกับแอป
    image_url = f"https://source.unsplash.com/featured/800x400?{search_query.replace(' ', ',')}"
    
    st.image(image_url, caption=f"ภาพแนว {search_query}", use_column_width=True)
    st.info("💡 ถ้าไม่ชอบรูปนี้ ให้ลองกดลบตัวอักษรแล้วพิมพ์ใหม่ รูปจะเปลี่ยนไปเรื่อยๆ ครับ")

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="SYNAPSE 4-1", layout="centered", initial_sidebar_state="collapsed")

# --- 2. เตรียมเนื้อเพลง (ต้องไว้ก่อนเรียกใช้) ---
mega_lyrics = """
[เริ่ม] วันหนึ่งถ้าเธอมองย้อนกลับมา... อาจจะเห็นสิ่งที่เคยทำพังลงไป... แต่ถึงตอนนั้น ฉันคงเดินไกล... ทิ้งเรื่องของเราไว้ในอดีตคำที่เธอเคยให้... 
[ความจริง] ความจริงที่ฉันให้ไป จะเอาไปทิ้งไว้ที่ไหน ในวันที่ฉันจริงใจ แต่เธอทิ้งไปเหมือนเป็นแค่ของเล่น... 
[ขอบคุณ] ขอบคุณถ้อยคำที่เคยทำฉันร้าว คำที่ทำให้ใจฉันแทบไม่เหลืออะไร กลับกลายเป็นทางให้ฉันหันมาเจอแสงในตัวเอง... 
[ปล่อยวาง] ปล่อยวางความโกรธที่เผาใจ ทิ้งความโลภที่ไม่มีวันพอ อยู่นิ่งๆ ไม่เจ็บตัว แค่รู้เท่าทันแล้ววางลงตรงนี้...
"""

# --- 3. CUSTOM CSS ---
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="stAppViewContainer"] {background-color: #000000;}
    .block-container {padding-top: 1rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important;}
    
    .video-container {
        position: relative;
        width: 100%;
        border-radius: 10px;
        overflow: hidden;
        border: 2px solid #444;
    }
    .marquee-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        background: rgba(0, 0, 0, 0.6);
        padding: 10px 0;
        z-index: 10;
        border-bottom: 1px solid rgba(255, 75, 75, 0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. ส่วนหัวข้อ ---
st.markdown("""
    <div style='text-align: center;'>
        <h1 style='color: #FF4B4B; text-shadow: 0 0 15px #FF4B4B; font-size: 28px;'>📡 SYNAPSE 4-1</h1>
        <p style='color: #666; font-size: 12px;'>อยู่นิ่งๆ ไม่เจ็บตัว</p>
    </div>
    """, unsafe_allow_html=True)

# --- 5. ส่วนวิดีโอแบบ Overlay ---
try:
    with open('วันที่ขอบคุณไม่มีใคร 4-1 ปล่อยวาง.mp4', 'rb') as v_file:
        video_bytes = v_file.read()
        base64_video = base64.b64encode(video_bytes).decode()
        
        st.markdown(f"""
            <div class="video-container">
                <div class="marquee-overlay">
                    <marquee scrollamount="8" style="color: #FF4B4B; font-size: 18px; font-weight: bold; font-family: 'Kanit', sans-serif;">
                        {mega_lyrics}
                    </marquee>
                </div>
                <video autoplay loop muted playsinline style="width: 100%;">
                    <source src="data:video/mp4;base64,{base64_video}" type="video/mp4">
                </video>
            </div>
            """, unsafe_allow_html=True)
except FileNotFoundError:
    st.info("💡 รอไฟล์มหากาพย์: วันที่ขอบคุณไม่มีใคร 4-1 ปล่อยวาง.mp4")

# --- 6. ส่วนเสียงและปุ่ม ---
try:
    with open('วันที่ขอบคุณไม่มีใคร 4-1 ปล่อยวาง.mp3', 'rb') as a_file:
        st.audio(a_file.read(), format='audio/mp3')
except:
    pass

if st.button("📡 BROADCAST 4-1 SIGNAL", use_container_width=True):
    st.success("SIGNAL BROADCASTED!")
