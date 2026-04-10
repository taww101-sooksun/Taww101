import streamlit as st
import time
import base64

st.set_page_config(page_title="Split Screen MV", layout="wide")

def get_file_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

# ดีไซน์ Layout บน-ล่าง
st.markdown("""
    <style>
    .stApp { background-color: #000; }
    
    /* ส่วนบน: วิดีโอ */
    .video-section {
        width: 100%;
        max-width: 700px;
        margin: auto;
        border: 2px solid #333;
        border-radius: 15px;
        overflow: hidden;
    }
    
    /* ส่วนล่าง: พื้นที่เนื้อเพลง */
    .lyric-section {
        width: 100%;
        height: 250px;
        background-color: #000;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 20px;
    }

    .lyric-text {
        font-family: 'Kanit', sans-serif;
        font-size: 40px;
        font-weight: bold;
        color: #fff;
        text-shadow: 0 0 10px #fff, 0 0 20px #ff00de, 0 0 30px #ff00de;
        text-align: center;
        transition: all 0.5s ease;
    }

    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# เนื้อเพลง (ใส่ให้ครบตามจังหวะเพลง)
lyrics_data = [
    {"time": 0, "text": "เตรียมตัวบันทึก..."},
    {"time": 8, "text": "ความจริงที่ฉันให้ไป"},
    {"time": 13, "text": "จะเอาไปทิ้งไว้ที่ไหน"},
    {"time": 18, "text": "ในวันที่ฉันจริงใจ..."},
    {"time": 22, "text": "แต่เธอเป็นใครที่ฉันไม่รู้จัก"},
    # ... ท่านสามารถเพิ่มเนื้อเพลงบรรทัดอื่นๆ ต่อตรงนี้ได้เลยครับ ...
    {"time": 190, "text": "จบการแสดง"}
]

video_data = get_file_base64("1000014353.mp4")

if video_data:
    # สร้าง Container สำหรับวิดีโอ (ส่วนบน)
    video_placeholder = st.empty()
    
    # สร้าง Container สำหรับเนื้อเพลง (ส่วนล่าง)
    lyric_placeholder = st.empty()

    if st.button('🎬 เริ่มเล่นหน้าจอ บน-ล่าง'):
        # แสดงวิดีโอส่วนบน
        video_html = f"""
            <div class="video-section">
                <video id="myVideo" width="100%" autoplay>
                    <source src="data:video/mp4;base64,{video_data}" type="video/mp4">
                </video>
            </div>
        """
        video_placeholder.markdown(video_html, unsafe_allow_html=True)
        
        # เริ่มรันเนื้อเพลงส่วนล่าง
        start_time = time.time()
        for line in lyrics_data:
            while True:
                elapsed = time.time() - start_time
                if elapsed >= line["time"]:
                    # อัปเดตเนื้อเพลงที่ส่วนล่าง
                    lyric_placeholder.markdown(f"""
                        <div class="lyric-section">
                            <div class="lyric-text">{line["text"]}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    break
                time.sleep(0.01)
    else:
        st.info("พร้อมแล้วกดปุ่มเริ่มเพื่ออัดวิดีโอครับ")
else:
    st.error("ไม่พบไฟล์วิดีโอ 1000014353.mp4 ในโฟลเดอร์")

