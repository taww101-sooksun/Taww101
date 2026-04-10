import streamlit as st
import time

# ตั้งค่าหน้าจอและซ่อน UI ส่วนเกิน
st.set_page_config(page_title="Lyric Video Player", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #00FF00; /* Green Screen สำหรับดูดสีออก */
    }
    .lyric-box {
        font-family: 'Kanit', sans-serif;
        font-size: 65px;
        font-weight: bold;
        text-align: center;
        height: 60vh;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1.3;
        color: #ffffff;
        text-shadow: 0 0 20px #ff00de, 0 0 40px #ff00de;
    }
    /* ซ่อนเครื่องเล่นเพลงตอนจะอัดจอ (ถ้าต้องการ) หรือแสดงไว้ก็ได้ */
    audio {
        width: 100%;
        filter: invert(100%); /* ปรับสีเครื่องเล่นให้ตัดกับพื้นหลัง */
    }
    </style>
    """, unsafe_allow_html=True)

# 1. แสดงเครื่องเล่นเพลง
st.write("### 🎵 เครื่องเล่นเพลง")
audio_file = open('ความจริงของเธอคือการโกหก.mp3', 'rb')
audio_bytes = audio_file.read()
st.audio(audio_bytes, format='audio/mp3')

# 2. ข้อมูลเนื้อเพลงและเวลา
lyrics_data = [
    {"time": 0, "text": "ความจริงที่ฉันให้ไป"},
    {"time": 5, "text": "จะเอาไปทิ้งไว้ที่ไหน"},
    {"time": 11, "text": "ในวันที่ฉันจริงใจ แต่เธอกลับกลายเป็นใครที่ฉันไม่รู้"},
    {"time": 22, "text": "จ้างจะสู้ถึงร้อย ความห่วงใยที่ฉันค่อยประคอง"},
    {"time": 27, "text": "แทบจะมองเป็นแค่ของเล่น ที่อยากจะขว้างหรืออยากจะลอง"},
    {"time": 31, "text": "แววตาที่พ่นออกมา มันมีแต่ลมลวงหลอก"},
    {"time": 34, "text": "กี่ครั้งที่บอกว่ารัก แต่ค้างในใจกับคิดจะบอกลา"},
    {"time": 38, "text": "ความจริงของเธอ มันช่างพร่ามัว"},
    {"time": 42, "text": "ก็เข็ดซ้ำๆ จนใจของฉัน มันเริ่มจะชินกับความกลัว"},
    {"time": 49, "text": "ในโลกที่หมุนวนไป ฉันเพิ่งจะรู้ว่าเธอสำคัญเพียงใด"},
    {"time": 60, "text": "ภาพที่เธอยิ้มให้กัน วันนี้มันกลายเป็นเพียงแค่เงา"},
    {"time": 72, "text": "โอ้นางร้ายที่ฉันเคยรักหมดใจ"},
    {"time": 76, "text": "เพราะยิ่งที่เธอให้มา มันคือพิษทิ่มลงไปข้างใน"},
    {"time": 79, "text": "รักคือการปล่อยมือ คือการยื้อเพื่อรอความตาย"},
    {"time": 88, "text": "ในโลกความจริงที่ว่างเปล่า ฉันขอจากไปให้ไกลจากเธอ"},
    {"time": 92, "text": "จะบอกว่ารักฉันจริง แต่การกระทำมันดูย้อนแย้ง"},
    {"time": 96, "text": "มันแสงสว่างที่ปลายอุโมงค์ แต่มันคือไฟที่คอยแผดเผา"},
    {"time": 100, "text": "นี่คือเวรกรรมที่ฉันยอมทน"},
    {"time": 104, "text": "ใจจะพังให้กลายเป็นกำแพงที่แข็งแรงและไม่ยอมคน"},
    {"time": 108, "text": "ไม่ต้องมีคำลา ไม่ต้องมีสัญญา ทิ้งท้าย"},
    {"time": 114, "text": "ปล่อยให้ภาพวันหลังจางหายไปในความหลัง"},
    {"time": 120, "text": "ฉันไม่เจ็บอีกต่อไป ฉันไม่เลือกใคร... แต่ฉันมีตัวฉันเอง"},
    {"time": 125, "text": "จบเพลง"}
]

placeholder = st.empty()

# 3. ปุ่มเริ่มรันเนื้อเพลง
if st.button('เริ่มแสดงเนื้อเพลง (กดพร้อมเล่นเพลง)'):
    start_time = time.time()
    for line in lyrics_data:
        while True:
            elapsed = time.time() - start_time
            if elapsed >= line["time"]:
                placeholder.markdown(f'<div class="lyric-box">{line["text"]}</div>', unsafe_allow_html=True)
                break
            time.sleep(0.01)
else:
    placeholder.markdown('<div class="lyric-box" style="color:#000; font-size:30px;">กดเล่นเพลงแล้วกดปุ่มเริ่มรันเนื้อเพลงครับ</div>', unsafe_allow_html=True)
