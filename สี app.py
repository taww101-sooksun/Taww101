import streamlit as st
import time
import base64

st.set_page_config(page_title="MV Maker - อยู่นิ่งๆ ไม่เจ็บตัว", layout="wide")

def get_audio_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

# ดีไซน์หน้าจอให้ดูน่าสนใจ (Modern Dark Mode)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;500&display=swap');
    .stApp { background-color: #000000; }
    .lyric-box {
        font-family: 'Kanit', sans-serif;
        font-size: 38px; /* ขนาดเล็กตามที่ท่านต้องการ */
        font-weight: 500;
        text-align: center;
        height: 60vh;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #FFFFFF;
        text-shadow: 0 0 8px rgba(255,255,255,0.6), 0 0 15px #ff00de;
        line-height: 1.5;
        padding: 40px;
    }
    #MainMenu, footer, header {visibility: hidden;}
    .stButton>button {
        background: linear-gradient(45deg, #ff00de, #7000ff);
        color: white; border-radius: 30px; border: none;
        padding: 10px 30px; font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

# เนื้อเพลงแบบละเอียด (Time Sync)
lyrics_data = [
    {"time": 0, "text": "เตรียมตัวบันทึกวิดีโอ..."},
    {"time": 8, "text": "ความจริงที่ฉันให้ไป"},
    {"time": 13, "text": "จะเอาไปทิ้งไว้ที่ไหน"},
    {"time": 18, "text": "ในวันที่ฉันจริงใจ..."},
    {"time": 22, "text": "แต่เเธอเป็นใครที่ฉันไม่รู้จัก"},
    {"time": 31, "text": "เริ่มจางจากศูนย์ถึงร้อย\nความห่วงใยที่ฉันคอยประคอง"},
    {"time": 35, "text": "แต่เธอกลับมองเป็นแค่ของเล่นที่อยากจะขว้าง"},
    {"time": 39, "text": "แววตาที่พ่นออกมา มีแต่ลมที่ลวงหลอก"},
    {"time": 42, "text": "กี่ครั้งที่บอกว่ารัก แต่ในใจคิดจะบอกลา"},
    {"time": 45, "text": "ความจริงของเธอมันช่างพร่ามัว"},
    {"time": 47, "text": "เข็ดซ้ำๆ จนใจของฉันเริ่มชินกับความกลัว"},
    {"time": 53, "text": "ทุกประสบการณ์คือบทเรียน\nที่เขียนด้วยน้ำตา"},
    {"time": 58, "text": "ในโลกที่หมุนวนไป..."},
    {"time": 61, "text": "ฉันเพิ่งจะรู้ว่าเธอสำคัญเพียงใด"},
    {"time": 65, "text": "ในวันที่สาย..."},
    {"time": 70, "text": "ภาพที่เธอยิ้มให้กัน\nวันนี้กลายเป็นเพียงแค่เงา"},
    {"time": 76, "text": "โอ้ นางร้ายที่ฉันเคยรักหมดใจ"},
    {"time": 81, "text": "รักที่เธอให้มา มันคือพิษทิ่มลงข้างใน"},
    {"time": 85, "text": "รักคือการปล่อยมือ\nหรือการยื้อเพื่อรอความตาย"},
    {"time": 90, "text": "ในโลกความจริงที่ว่างเปล่า..."},
    {"time": 94, "text": "ฉันขอเดินจากไป ให้ไกลจากเธอ"},
    {"time": 113, "text": "วันนั้นเธอเดินไป... ฉันมองดูไกลๆ"},
    {"time": 117, "text": "ไม่คิดจะเหนี่ยวรั้ง..."},
    {"time": 120, "text": "ปล่อยให้ภาพวันนั้น จางหายไปในความหลัง"},
    {"time": 125, "text": "ฉันไม่เจ็บอีกต่อไป... ฉันไม่เหลือใคร"},
    {"time": 129, "text": "แต่ฉันมีตัวฉันเอง..."},
    {"time": 133, "text": "โอ้ นางร้ายที่ฉันเคยรักหมดใจ (Hook)"},
    {"time": 137, "text": "รักที่เธอให้มา มันคือพิษทิ่มลงข้างใน"},
    {"time": 141, "text": "รักคือการปล่อยมือ\nหรือการยื้อเพื่อรอความตาย"},
    {"time": 146, "text": "ในโลกความจริงที่ว่างเปล่า..."},
    {"time": 150, "text": "ฉันขอเดินจากไป ให้ไกลจากเธอ"},
    {"time": 155, "text": "ไม่เจ็บอีกแล้ว... (Outro)"},
    {"time": 190, "text": "อยู่นิ่งๆ ไม่เจ็บตัว..."},
    {"time": 199, "text": "จบการแสดง"}
]

placeholder = st.empty()
audio_str = get_audio_base64("1000014353.mp4") # ใช้ไฟล์ที่คุณอัปโหลดมา

if audio_str:
    if st.button('🎬 เริ่มเล่นและบันทึกวิดีโอ'):
        # สั่งเล่นเพลง (Hidden Audio Player)
        st.markdown(f"""
            <audio id="bg-music" autoplay>
                <source src="data:video/mp4;base64,{audio_str}" type="video/mp4">
            </audio>
            """, unsafe_allow_html=True)
        
        # วิ่งเนื้อเพลง
        start_time = time.time()
        for line in lyrics_data:
            while True:
                elapsed = time.time() - start_time
                if elapsed >= line["time"]:
                    placeholder.markdown(f'<div class="lyric-box">{line["text"]}</div>', unsafe_allow_html=True)
                    break
                time.sleep(0.01)
    else:
        placeholder.markdown('<div class="lyric-box" style="color:#444;">กดปุ่มด้านบนเพื่อเริ่ม<br><span style="font-size:18px;">เพลงและเนื้อจะเล่นพร้อมกันทันที</span></div>', unsafe_allow_html=True)
else:
    st.error("กรุณาตรวจสอบว่าไฟล์วิดีโออยู่ในโฟลเดอร์เดียวกับโค้ดครับ")
