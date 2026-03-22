import streamlit as st
import os
import random

# 1. ตั้งค่าหน้าแอปและดีไซน์ (สายรุ้ง + ฟอนต์เท่)
st.set_page_config(page_title="My Playlist Hub", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    .stApp {
        background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
        background-size: 1200% 1200%;
        animation: RainbowFlow 15s ease infinite;
    }
    @keyframes RainbowFlow {
        0%{background-position:0% 50%}
        50%{background-position:100% 50%}
        100%{background-position:0% 50%}
    }
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif;
        color: white !important;
        text-shadow: 2px 2px 4px #000;
    }
    /* สไตล์สำหรับปุ่มรายชื่อเพลง */
    .stButton>button {
        width: 100%;
        text-align: left;
        background-color: rgba(175, 238, 238, 0.8) !important; /* Pale Turquoise แบบโปร่งแสง */
        border: 1px solid white !important;
        border-radius: 10px;
        color: #333 !important;
        margin-bottom: 5px;
    }
    .stButton>button:hover {
        background-color: #FF7F50 !important; /* Coral */
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. ค้นหาไฟล์เพลง
music_files = [f for f in os.listdir('.') if f.lower().endswith(".mp3")]

if music_files:
    # เก็บสถานะเพลงที่เลือก
    if 'current_song' not in st.session_state:
        st.session_state.current_song = music_files[0]

    # แสดงโลโก้
    if os.path.exists("logo2.jpg"):
        st.image("logo2.jpg", width=500)

    st.title("🎵 MY PLAYLIST")

    # --- ส่วนที่ 1: ตัวเล่นเพลงปัจจุบัน ---
    st.write(f"### 🎧 กำลังเล่น: {st.session_state.current_song}")
    
    # แสดงรูปปกถ้ามี (ชื่อเดียวกับเพลงแต่เป็น .jpg)
    cover_image = st.session_state.current_song.replace(".mp3", ".jpg")
    if os.path.exists(cover_image):
        st.image(cover_image, width=300)
    
    st.audio(st.session_state.current_song)

    st.markdown("---")

    # --- ส่วนที่ 2: รายชื่อเพลงทั้งหมด (กดแล้วเล่นเลย) ---
    st.write("### 📜 รายชื่อเพลงทั้งหมด")
    st.write("เลือกเพลงที่ต้องการฟังด้านล่างนี้:")

    for song in music_files:
        # สร้างปุ่มสำหรับทุกเพลง
        if st.button(f"▶️ {song}", key=song):
            st.session_state.current_song = song
            st.rerun() # สั่งให้แอปโหลดใหม่เพื่อเล่นเพลงที่กดทันที

else:
    st.error("ไม่พบไฟล์เพลง .mp3 ในโฟลเดอร์ครับ")
    st.info("วิธีแก้: อัปโหลดเพลงไว้ที่หน้าเดียวกับ app.py นะ")

