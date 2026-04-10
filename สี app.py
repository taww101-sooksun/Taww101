import streamlit as st
import time

# ตั้งค่าหน้าจอเป็นแบบ Wide และซ่อน Menu ของ Streamlit เพื่อให้แคปจอสวยๆ
st.set_page_config(page_title="Lyric Video Creator", layout="wide")

# CSS สำหรับ Green Screen และตัวหนังสือวิ้ง
st.markdown("""
    <style>
    /* พื้นหลังสีเขียวสำหรับทำ Green Screen */
    .stApp {
        background-color: #00FF00;
    }
    .lyric-box {
        font-family: 'Kanit', sans-serif;
        font-size: 60px;
        font-weight: bold;
        text-align: center;
        height: 80vh;
        display: flex;
        align-items: center;
        justify-content: center;
        line-height: 1.2;
    }
    .glow {
        color: #ffffff;
        text-shadow: 0 0 15px #fff, 0 0 25px #ff00de, 0 0 35px #ff00de;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    /* ซ่อน UI ของ Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# ข้อมูลเนื้อเพลงแบบจัดเต็ม (Time Sync คร่าวๆ ตามคลิป)
lyrics_data = [
    {"time": 0, "text": "ความจริงที่ฉันให้ไป"},
    {"time": 5, "text": "จะเอาไปทิ้งไว้ที่ไหน"},
    {"time": 11, "text": "ในวันที่ฉันจริงใจ แต่เธอกลับกลายเป็นใครที่ฉันไม่รู้"},
    {"time": 22, "text": "จ้างจะสู้ถึงร้อย ความห่วงใยที่ฉันคอยประคอง"},
    {"time": 27, "text": "แทบจะมองเป็นแค่ของเล่น ที่อยากจะขว้างหรืออยากจะลอง"},
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
    {"time": 92, "text": "จะบอกว่ารักฉันจริง แต่การกระทำมันดูย้อนแย้ง"},
    {"time": 96, "text": "มันแสงสว่างที่ปลายอุโมงค์ แต่มันคือไฟที่คอยแผดเผา"},
    {"time": 100, "text": "นี่คือเวรกรรมที่ฉันยอมทน"},
    {"time": 104, "text": "ใจจะพังให้กลายเป็นกำแพงที่แข็งแรงและไม่ยอมคน"},
    {"time": 108, "text": "ไม่ต้องมีคำลา ไม่ต้องมีสัญญา ทิ้งท้าย"},
    {"time": 114, "text": "ปล่อยให้ภาพวันหลังจางหายไปในความหลัง"},
    {"time": 120, "text": "ฉันไม่เจ็บอีกต่อไป ฉันไม่เลือกใคร... แต่ฉันเลือกตัวเอง"},
    {"time": 125, "text": "จบเพลง"}
]

placeholder = st.empty()

if st.button('กดตรงนี้แล้วเริ่มอัดหน้าจอเลย!'):
    # นับถอยหลังให้เตรียมตัวอัดจอ
    for i in range(3, 0, -1):
        placeholder.markdown(f'<div class="lyric-box">{i}</div>', unsafe_allow_html=True)
        time.sleep(1)
        
    start_time = time.time()
    for i in range(len(lyrics_data)):
        while True:
            elapsed = time.time() - start_time
            if elapsed >= lyrics_data[i]["time"]:
                placeholder.markdown(f'<div class="lyric-box glow">{lyrics_data[i]["text"]}</div>', unsafe_allow_html=True)
                break
            time.sleep(0.05)
    
    st.balloons()
else:
    placeholder.markdown('<div class="lyric-box" style="color:black; font-size:30px;">เตรียมแอปอัดหน้าจอให้พร้อม แล้วกดปุ่มเริ่ม</div>', unsafe_allow_html=True)
