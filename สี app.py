import streamlit as st
import os
import random
import streamlit.components.v1 as components

# 1. ตั้งค่าหน้าแอปและ CSS (สายรุ้ง)
st.set_page_config(page_title="Non-Stop Rainbow Music", layout="centered")

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
        background-size: 1200% 1200%;
        animation: RainbowFlow 10s ease infinite;
    }}
    @keyframes RainbowFlow {{
        0%{{background-position:0% 50%}}
        50%{{background-position:100% 50%}}
        100%{{background-position:0% 50%}}
    }}
    .stSelectbox, .stButton>button {{
        background-color: #AFEEEE !important;
        border-radius: 10px;
    }}
    h1, h3 {{ color: white; text-shadow: 2px 2px 4px #000; }}
    </style>
    """, unsafe_allow_html=True)

# 2. จัดการรายชื่อเพลง
music_files = [f for f in os.listdir('.') if f.lower().endswith(".mp3")]

if music_files:
    # เก็บสถานะเพลงปัจจุบันใน Session
    if 'song_index' not in st.session_state:
        st.session_state.song_index = 0

    # ฟังก์ชันเปลี่ยนเพลง
    def next_song():
        st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)

    # แสดงโลโก้
    if os.path.exists("logo2.jpg"):
        st.image("logo2.jpg", width=600)

    st.title("🎵 คลังเพลงเพื่อนรัก (Non-Stop)")
    
    # เลือกเพลง
    selected_song = st.selectbox("เลือกเพลง:", music_files, index=st.session_state.song_index, key="song_select")
    
    # อัปเดต Index ตามที่เลือก manual
    st.session_state.song_index = music_files.index(selected_song)

    # --- ส่วนสำคัญ: เครื่องเล่นเพลงพร้อมคำสั่ง JavaScript ---
    st.write(f"### 🎧 กำลังเล่น: {selected_song}")
    
    # แสดงตัวเล่นเพลงและให้ ID กับมัน
    st.audio(selected_song, format="audio/mp3")

    # JavaScript: ตรวจสอบว่าเพลงจบหรือยัง ถ้าจบให้กดปุ่ม 'Next' จำลอง
    components.html(
        """
        <script>
            // ค้นหาตัวเล่นเพลงในหน้าเว็บ
            const audio = window.parent.document.querySelector('audio');
            if (audio) {
                audio.onended = function() {
                    // เมื่อเพลงจบ ให้ส่งคำสั่งไปที่ Streamlit เพื่อเปลี่ยนเพลง
                    window.parent.document.querySelector('button[kind="secondary"]').click();
                };
            }
        </script>
        """,
        height=0,
    )

    # ปุ่มเปลี่ยนเพลง (ที่ JavaScript จะมาแอบกดให้)
    if st.button("⏭️ เล่นเพลงถัดไป"):
        next_song()
        st.rerun()

    st.info("💡 เพลงจะเล่นต่อเนื่องอัตโนมัติ (เปิดหน้าจอค้างไว้นะครับ)")

else:
    st.error("ไม่เจอไฟล์เพลง .mp3 เลยครับ")
