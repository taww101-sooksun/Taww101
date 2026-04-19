import streamlit as st
import os
import base64

# --- CONFIG & UI HIDING ---
st.set_page_config(page_title="SYNAPSE Player", layout="centered")

def get_base64_bin(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# ซ่อน Streamlit UI เดิมๆ เพื่อความคลีน
hide_ui = """
    /* ใส่ในส่วน <style> */
.logo-img {
    width: 400px;
    filter: drop-shadow(0 0 20px {theme_color});
    animation: logoPulse 4s ease-in-out infinite;
}

@keyframes logoPulse {
    0%, 100% { filter: drop-shadow(0 0 15px {theme_color}) contrast(1.1); transform: scale(1); }
    50% { filter: drop-shadow(0 0 50px {theme_color}) contrast(1.3); transform: scale(1.02); }
}


    /* ตัวหนังสือวิ้งๆ */
    .shimmer-text {
        text-align: center;
        font-weight: bold;
        font-size: 1.5rem;
        background: linear-gradient(90deg, #AFEEEE, #FF7F50, #AFEEEE);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 2s linear infinite;
    }
    @keyframes shine {
        to { background-position: 200% center; }
    }

    /* แถบสีรุ้ง (Rainbow Flow) สำหรับเครื่องเล่น */
    .stAudio {
        background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
        background-size: 1200% 1200%;
        animation: RainbowFlow 15s ease infinite;
        border-radius: 50px;
        padding: 5px;
    }
    @keyframes RainbowFlow {
        0%{background-position:0% 50%}
        50%{background-position:100% 50%}
        100%{background-position:0% 50%}
    }
    </style>
"""
st.markdown(hide_ui, unsafe_allow_html=True)

# --- LOGIC: ดึงไฟล์เพลงจาก Directory ---
song_files = [f for f in os.listdir('.') if f.endswith('.mp3')]

# --- UI DISPLAY ---
# 1. โลโก้ดิ้นได้ (ขนาด 200px)
if os.path.exists("logo1.png"):
    logo_base64 = get_base64_bin("logo1.png")
    st.markdown(f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_base64}" width="200">
        </div>
    """, unsafe_allow_html=True)
else:
    st.warning("กรุณาวางไฟล์ logo1.png ในโฟลเดอร์เดียวกับโค้ด")

# 2. ตัวหนังสือวิ้ง
st.markdown('<div class="shimmer-text">SYNAPSE X COMMAND CENTER</div>', unsafe_allow_html=True)

# 3. ส่วนเลือกเพลงและเครื่องเล่น
if song_files:
    selected_song = st.selectbox("เลือกเพลงที่จะเล่น", song_files)
    
    # อ่านไฟล์เพลงมาทำเป็น Audio Player
    audio_file = open(selected_song, 'rb')
    audio_bytes = audio_file.read()
    st.audio(audio_bytes, format='audio/mp3')
    
    # 4. จำลองกราฟเครื่องเสียง (Visualizer)
    # ใช้ HTML/CSS เพื่อจำลองกราฟแท่งขยับได้
    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: flex-end; height: 50px; gap: 3px;">
            <style>
                .bar { width: 10px; background: #00ffff; animation: equalize 1s infinite alternate; }
                @keyframes equalize { 
                    0% { height: 10px; } 100% { height: 40px; } 
                }
                .bar:nth-child(2) { animation-delay: 0.2s; background: #ff00ff; }
                .bar:nth-child(3) { animation-delay: 0.4s; background: #ffff00; }
                .bar:nth-child(4) { animation-delay: 0.6s; background: #00ff00; }
                .bar:nth-child(5) { animation-delay: 0.1s; background: #ff7f50; }
            </style>
            <div class="bar"></div><div class="bar"></div><div class="bar"></div>
            <div class="bar"></div><div class="bar"></div><div class="bar"></div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.info("ไม่พบไฟล์ .mp3 ในโฟลเดอร์นี้")

# --- ข้อแนะนำการบันทึกวิดีโอลง YouTube ---
st.markdown("---")
with st.expander("คำแนะนำการบันทึกหน้าจอเพื่อลง YouTube"):
    st.write("""
    1. **ใช้ OBS Studio:** ตั้งค่า Canvas เป็น 1080p (1920x1080)
    2. **Window Capture:** เลือกหน้าต่าง Browser ที่รัน Streamlit อยู่
    3. **Bitrate:** ตั้งค่า Bitrate ใน OBS ให้สูง (ประมาณ 10,000 kbps ขึ้นไป) เพื่อให้สีรุ้งไม่แตก
    4. **การเล่นต่อเนื่อง:** ในเครื่องเล่นปกติของ Streamlit จะไม่มีระบบ Queue อัตโนมัติในตัว (Native) 
       แต่คุณสามารถกด 'Loop' ได้โดยการคลิกขวาที่ตัวเครื่องเล่นเสียงครับ
    """)
