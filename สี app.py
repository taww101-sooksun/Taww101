import streamlit as st
import time

# 1. ตั้งค่าหน้าแอป
st.set_page_config(page_title="Lyrics Sync App", page_icon="🎵")

# 2. ใส่ CSS เพื่อให้ตัวหนังสือ "วิ้ง" (Glow Effect)
st.markdown("""
    <style>
    .lyric-box {
        font-size: 40px;
        font-weight: bold;
        text-align: center;
        min-height: 150px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.5s ease-in-out;
    }
    /* เอฟเฟกต์วิ้ง */
    .glow {
        color: #fff;
        text-shadow: 0 0 10px #fff, 0 0 20px #00f2ff, 0 0 30px #00f2ff, 0 0 40px #00f2ff;
        transform: scale(1.1);
    }
    .normal {
        color: #444;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎵 เครื่องเล่นเนื้อเพลงวิ้งๆ")

# 3. เตรียมข้อมูลเนื้อเพลงและเวลา (Time markers ในวินาที)
lyrics_data = [
    {"time": 0, "text": "ความจริงที่ฉันให้ไป"},
    {"time": 5, "text": "จะเอาไปทิ้งไว้ที่ไหน"},
    {"time": 11, "text": "ในวันที่ฉันจริงใจ"},
    {"time": 16, "text": "แต่เธอกลับกลายเป็นใครที่ฉันไม่รู้"},
    {"time": 22, "text": "จ้างจะสู้ถึงร้อย ความห่วงใยที่ฉันคอยประคอง"}
]

# 4. ส่วนแสดงผล
placeholder = st.empty()  # ใช้สำหรับอัปเดตตัวหนังสือซ้ำๆ ในตำแหน่งเดิม

if st.button('เริ่มเล่นเนื้อเพลง'):
    start_time = time.time()
    
    # วนลูปเช็คเวลาเพื่อเปลี่ยนเนื้อเพลง
    current_index = 0
    while current_index < len(lyrics_data):
        elapsed_time = time.time() - start_time
        
        # ถ้าถึงเวลาของเนื้อเพลงบรรทัดนั้น
        if elapsed_time >= lyrics_data[current_index]["time"]:
            text = lyrics_data[current_index]["text"]
            # อัปเดต HTML พร้อม Class 'glow'
            placeholder.markdown(f'<div class="lyric-box glow">{text}</div>', unsafe_allow_html=True)
            
            # เช็คว่าจะเปลี่ยนบรรทัดถัดไปเมื่อไหร่
            if current_index + 1 < len(lyrics_data):
                # รอจนกว่าจะถึงเวลาบรรทัดถัดไป
                next_time = lyrics_data[current_index + 1]["time"]
                time.sleep(0.1) # ป้องกัน Loop ทำงานหนักเกินไป
                if elapsed_time >= next_time:
                    current_index += 1
            else:
                break
        else:
            time.sleep(0.1)

    st.success("จบเพลงแล้วครับ")
else:
    placeholder.markdown('<div class="lyric-box normal">กดปุ่มด้านล่างเพื่อเริ่ม</div>', unsafe_allow_html=True)
