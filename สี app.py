import streamlit as st
import time
import base64

st.set_page_config(page_title="Music Video Maker", layout="wide")

# ฟังก์ชันแปลงไฟล์เพลงเป็น Base64 เพื่อให้รันใน HTML ได้พร้อมกัน
def get_audio_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# ใส่ CSS ปรับแต่งความสวยงาม
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .lyric-container {
        font-family: 'Kanit', sans-serif;
        font-size: 42px; /* ขนาดเล็กลงตามที่ขอ */
        font-weight: 500;
        text-align: center;
        height: 70vh;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        text-shadow: 0 0 10px rgba(255,255,255,0.8), 0 0 20px #ff00de;
        transition: all 0.8s ease;
    }
    /* ซ่อนส่วนประกอบของ Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    .stButton>button {
        background-color: #ff00de; color: white; border-radius: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# ข้อมูลเนื้อเพลง
lyrics_data = [
    {"time": 0, "text": "ความจริงที่ฉันให้ไป"},
    {"time": 5, "text": "จะเอาไปทิ้งไว้ที่ไหน"},
    {"time": 11, "text": "ในวันที่ฉันจริงใจ แต่เธอกลับกลายเป็นใครที่ฉันไม่รู้"},
    {"time": 22, "text": "จ้างจะสู้ถึงร้อย ความห่วงใยที่ฉันค่อยประคอง"},
    {"time": 27, "text": "แทบจะมองเป็นแค่ของเล่นที่อยากจะขว้าง"},
    {"time": 31, "text": "แววตาที่พ่นออกมา มันมีแต่ลมลวงหลอก"},
    {"time": 34, "text": "กี่ครั้งที่บอกว่ารัก แต่ค้างในใจกลับคิดจะบอกลา"},
    {"time": 38, "text": "ความจริงของเธอ มันช่างพร่ามัว"},
    {"time": 42, "text": "ก็เข็ดซ้ำๆ จนใจของฉัน มันเริ่มจะชินกับความกลัว"},
    {"time": 49, "text": "ในโลกที่หมุนวนไป ฉันเพิ่งจะรู้ว่าเธอสำคัญเพียงใด"},
    {"time": 60, "text": "ภาพที่เธอยิ้มให้กัน วันนี้มันกลายเป็นเพียงแค่เงา"},
    {"time": 72, "text": "โอ้นางร้ายที่ฉันเคยรักหมดใจ"},
    {"time": 76, "text": "เพราะสิ่งที่เธอให้มา มันคือพิษทิ่มลงไปข้างใน"},
    {"time": 79, "text": "รักคือการปล่อยมือ คือการยื้อเพื่อรอความตาย"},
    {"time": 88, "text": "ในโลกความจริงที่ว่างเปล่า ฉันขอจากไปให้ไกลจากเธอ"},
    {"time": 125, "text": "จบเพลง"}
]

placeholder = st.empty()

try:
    # เตรียมไฟล์เพลง
    audio_base64 = get_audio_base64("ความจริงของเธอคือการโกหก.mp3")
    
    if st.button('🎬 เริ่มการแสดง (อัดวิดีโอเลย)'):
        # ฝัง JavaScript ให้เล่นเพลงทันทีที่กดปุ่ม
        audio_html = f"""
            <audio id="bg-music" autoplay>
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
        
        # เริ่มวิ่งเนื้อเพลง
        start_time = time.time()
        for line in lyrics_data:
            while True:
                elapsed = time.time() - start_time
                if elapsed >= line["time"]:
                    placeholder.markdown(f'<div class="lyric-container">{line["text"]}</div>', unsafe_allow_html=True)
                    break
                time.sleep(0.01)
    else:
        placeholder.markdown('<div class="lyric-container" style="color:#555; font-size:24px;">พร้อมแล้วกดปุ่มเริ่มได้เลยครับ</div>', unsafe_allow_html=True)

except FileNotFoundError:
    st.error("ไม่พบไฟล์ 'ความจริงของเธอคือการโกหก.mp3' กรุณาตรวจสอบชื่อไฟล์ในโฟลเดอร์ครับ")
