import streamlit as st
import os
import random
import streamlit.components.v1 as components

# 1. ตั้งค่าหน้าแอปและดีไซน์
st.set_page_config(page_title="Non-Stop MP3 Player", layout="centered")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    .stApp {{
        background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
        background-size: 1200% 1200%;
        animation: RainbowFlow 15s ease infinite;
    }}
    @keyframes RainbowFlow {{
        0%{{background-position:0% 50%}}
        50%{{background-position:100% 50%}}
        100%{{background-position:0% 50%}}
    }}
    h1, h3, p {{
        font-family: 'Orbitron', sans-serif;
        color: white !important;
        text-shadow: 2px 2px 4px #000;
    }}
    .stButton>button {{
        width: 100%;
        background-color: #AFEEEE !important;
        color: #333 !important;
        border-radius: 12px;
        font-weight: bold;
        border: 2px solid white !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. จัดการไฟล์เพลง
music_files = [f for f in os.listdir('.') if f.lower().endswith(".mp3")]

if music_files:
    # เก็บสถานะเพลงปัจจุบัน
    if 'song_index' not in st.session_state:
        st.session_state.song_index = 0

    current_song = music_files[st.session_state.song_index]

    # แสดงโลโก้
    if os.path.exists("logo3.jpg"):
        st.image("logo3.jpg", width=150)

    st.title("🎵 NON-STOP VIBE")
    
    # --- ส่วนที่ 1: เครื่องเล่นเพลง ---
    st.write(f"### 🎧 กำลังเล่น: {current_song}")
    st.audio(current_song)

    # --- ส่วนที่ 2: ระบบเล่นต่อเนื่อง (JavaScript) ---
    # สคริปต์นี้จะแอบตรวจว่าเพลงจบหรือยัง ถ้าจบจะมากดปุ่ม "เพลงถัดไป" ให้เอง
    components.html(
        """
        <script>
        function autoNext() {
            var audio = window.parent.document.querySelector('audio');
            if (audio) {
                audio.onended = function() {
                    var buttons = window.parent.document.querySelectorAll('button');
                    for (var i = 0; i < buttons.length; i++) {
                        if (buttons[i].textContent.includes('เพลงถัดไป')) {
                            buttons[i].click();
                            break;
                        }
                    }
                };
            }
        }
        setInterval(autoNext, 1000);
        </script>
        """,
        height=0,
    )

    # --- ส่วนที่ 3: ปุ่มควบคุม ---
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏭️ เพลงถัดไป"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()
    with col2:
        if st.button("🎲 สุ่มเพลง"):
            st.session_state.song_index = random.randint(0, len(music_files) - 1)
            st.rerun()

    st.markdown("---")
    
    # --- ส่วนที่ 4: รายชื่อเพลงทั้งหมด ---
    st.subheader("📜 รายชื่อเพลงในคลัง")
    for i, song in enumerate(music_files):
        if st.button(f"{i+1}. {song}", key=f"btn_{song}"):
            st.session_state.song_index = i
            st.rerun()

    st.info("💡 **เคล็ดลับ:** เพื่อให้เพลงเล่นต่อเนื่องไม่หยุด กรุณา **'เปิดหน้าจอแอปค้างไว้'** นะครับ (ถ้าพับหน้าจอหรือสลับแอป ระบบอาจจะหยุดทำงานตามนโยบายของ Browser มือถือครับ)")

else:
    st.error("ไม่เจอไฟล์เพลง .mp3 เลยครับ")
