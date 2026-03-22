import streamlit as st
import os
import random
import streamlit.components.v1 as components

# 1. ตั้งค่าหน้าแอป
st.set_page_config(page_title="Vibe Music Player", layout="centered")

# 2. ใส่ CSS แบบจัดเต็ม (ฟอนต์เท่ + พื้นหลังสายรุ้ง + ปรับแต่งตัวหนังสือ)
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

    /* ตัวหนังสือแบบเท่ๆ */
    h1, h2, h3, .stMarkdown p {
        font-family: 'Orbitron', sans-serif;
        color: white !important;
        text-shadow: 3px 3px 6px #000000;
        letter-spacing: 2px;
    }

    /* ตกแต่งปุ่มและกล่องเลือก */
    .stSelectbox, .stButton>button {
        background-color: #AFEEEE !important;
        border: 2px solid white !important;
        border-radius: 15px !important;
        font-weight: bold;
    }

    /* ตัวเล่นเพลง */
    audio {
        width: 100%;
        filter: drop-shadow(0px 0px 10px #AFEEEE);
        border-radius: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. ส่วนจัดการไฟล์เพลงและรูปภาพ
music_files = [f for f in os.listdir('.') if f.lower().endswith(".mp3")]

if music_files:
    if 'song_index' not in st.session_state:
        st.session_state.song_index = 0

    # แสดงโลโก้ด้านบน
    if os.path.exists("logo2.jpg"):
        st.image("logo2.jpg", width=400)

    st.title("🎧 MY VIBE PLAYER")

    # ส่วนแสดงภาพปก (Cover Art)
    selected_song = music_files[st.session_state.song_index]
    cover_image = selected_song.replace(".mp3", ".jpg") # หาไฟล์ชื่อเดียวกับเพลงแต่เป็น .jpg
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if os.path.exists(cover_image):
            st.image(cover_image, caption="Now Playing", use_container_width=True)
        else:
            # ถ้าไม่มีรูปปก ให้ใช้รูป logo3.jpg แทน
            st.image("logo3.jpg", caption="Default Cover", use_container_width=True)
    
    with col2:
        st.write(f"### SONG: \n {selected_song}")
        # ปุ่มปรับทุ่มแหลม (จำลองความรู้สึก)
        tone = st.select_slider("ปรับโทนเสียง (Vibe Tone)", options=["Bass Boost", "Normal", "Treble High"])
        
    # ปรับ Filter เสียงตามตัวเลือก (ผ่าน CSS)
    audio_filter = "brightness(100%)"
    if tone == "Bass Boost": audio_filter = "contrast(150%) saturate(150%)"
    if tone == "Treble High": audio_filter = "brightness(120%) contrast(110%)"

    st.markdown(f"<style>audio {{ filter: {audio_filter}; }}</style>", unsafe_allow_html=True)

    # ตัวเล่นเพลง
    st.audio(selected_song)

    # 4. ปุ่มควบคุม
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⏮️ Previous"):
            st.session_state.song_index = (st.session_state.song_index - 1) % len(music_files)
            st.rerun()
    with c2:
        if st.button("⏭️ Next"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()
    with c3:
        if st.button("🎲 Shuffle"):
            st.session_state.song_index = random.randint(0, len(music_files)-1)
            st.rerun()

    # JavaScript สำหรับเล่นต่อเนื่อง
    components.html("""
        <script>
        function checkAudio() {
            var audio = window.parent.document.querySelector('audio');
            if (audio && !audio.paused) {
                audio.onended = function() {
                    var buttons = window.parent.document.querySelectorAll('button');
                    for (var i = 0; i < buttons.length; i++) {
                        if (buttons[i].textContent.includes('Next')) {
                            buttons[i].click();
                            break;
                        }
                    }
                };
            }
        }
        setInterval(checkAudio, 2000);
        </script>
        """, height=0)

else:
    st.error("อัปโหลดไฟล์ .mp3 เข้ามาก่อนนะ!")
