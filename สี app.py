import streamlit as st
import time
import base64

st.set_page_config(page_title="Lyrics Overlay MV", layout="wide")

def get_file_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

# ปรับแต่ง CSS เพื่อให้ตัวหนังสือซ้อนทับวิดีโอ
st.markdown("""
    <style>
    .stApp { background-color: #000; }
    
    /* จัดตำแหน่งวิดีโอให้เต็มจอ */
    .video-container {
        position: relative;
        width: 100%;
        max-width: 800px;
        margin: auto;
    }
    
    video {
        width: 100%;
        border-radius: 10px;
    }

    /* จัดวางเนื้อเพลงให้ลอยทับวิดีโอ */
    .lyric-overlay {
        position: absolute;
        top: 70%; /* ปรับตำแหน่งความสูงของเนื้อเพลง (0-100) */
        left: 50%;
        transform: translate(-50%, -50%);
        width: 90%;
        text-align: center;
        z-index: 999;
        pointer-events: none; /* เพื่อให้ยังกดปุ่มวิดีโอได้ */
        font-family: 'Kanit', sans-serif;
        font-size: 32px;
        font-weight: bold;
        color: white;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.8), 0 0 20px #ff00de;
    }

    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ข้อมูลเนื้อเพลง (เหมือนเดิม)
lyrics_data = [
    {"time": 0, "text": ""},
    {"time": 8, "text": "ความจริงที่ฉันให้ไป"},
    {"time": 13, "text": "จะเอาไปทิ้งไว้ที่ไหน"},
    {"time": 18, "text": "ในวันที่ฉันจริงใจ..."},
    {"time": 22, "text": "แต่เเธอเป็นใครที่ฉันไม่รู้จัก"},
    # ... (ท่านสามารถก๊อปปี้เนื้อเพลงที่เคยให้ไว้มาใส่ต่อให้ครบได้เลยครับ)
    {"time": 190, "text": "จบการแสดง"}
]

video_base64 = get_file_base64("1000014353.mp4")

if video_base64:
    st.write("### 🎬 Lyric Video Overlay")
    
    # ส่วนควบคุมการเล่น
    if st.button('เริ่มเล่นวิดีโอพร้อมเนื้อเพลง'):
        # แสดงวิดีโอและเนื้อเพลงซ้อนกัน
        video_html = f"""
            <div class="video-container">
                <video id="myVideo" autoplay>
                    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                </video>
                <div id="lyric-text" class="lyric-overlay"></div>
            </div>
        """
        st.markdown(video_html, unsafe_allow_html=True)
        
        # ตัว Placeholder สำหรับอัปเดตเนื้อเพลงลอยทับ
        # ใน Streamlit เราจะอัปเดตผ่านทาง JavaScript หรือ loop
        # แต่เพื่อให้เนียนที่สุด ผมใช้ loop ของ Streamlit อัปเดต HTML div
        
        lyric_placeholder = st.empty()
        start_time = time.time()
        
        for line in lyrics_data:
            while True:
                elapsed = time.time() - start_time
                if elapsed >= line["time"]:
                    # ใช้ JS เพื่อเปลี่ยนตัวหนังสือใน div ที่ซ้อนอยู่
                    st.components.v1.html(f"""
                        <script>
                        var parentDoc = window.parent.document;
                        var lyricDiv = parentDoc.getElementById('lyric-text');
                        if(lyricDiv) {{
                            lyricDiv.innerHTML = '{line["text"]}';
                        }}
                        </script>
                    """, height=0)
                    break
                time.sleep(0.01)
    else:
        st.info("กรุณากดปุ่มด้านบนเพื่อเริ่มการแสดง")
else:
    st.error("ไม่พบไฟล์ 1000014353.mp4")
