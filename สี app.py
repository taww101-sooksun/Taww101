import streamlit as st
import os
import random
import streamlit.components.v1 as components

# 1. ตั้งค่าหน้าแอป
st.set_page_config(page_title="Vibe Player Final", layout="centered")

# 2. CSS แบบใหม่: ใช้ "Scroll Bar" ของตัว Streamlit เองแทน HTML เพื่อลดโอกาสเบี้ยว
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    
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

    /* ชื่อเพลงวิ่งด้านบน */
    .marquee-text {{
        font-family: 'Orbitron', sans-serif;
        font-size: 20px;
        color: #AFEEEE;
        background: rgba(0,0,0,0.7);
        padding: 10px;
        border-radius: 10px;
        border: 2px solid white;
        text-align: center;
        margin-bottom: 10px;
    }}

    /* ตกแต่งปุ่มให้เด่น */
    .stButton>button {{
        width: 100%;
        background-color: #AFEEEE !important;
        color: #333 !important;
        border-radius: 10px;
        font-weight: bold;
    }}

    /* กราฟเสียง */
    .visualizer {{
        display: flex;
        align-items: flex-end;
        justify-content: center;
        height: 30px;
        gap: 3px;
        margin: 10px 0;
    }}
    .bar {{
        width: 6px;
        background: white;
        animation: equalize 0.8s infinite alternate;
    }}
    @keyframes equalize {{
        0% {{ height: 5px; }}
        100% {{ height: 30px; }}
    }}
    </style>
    """, unsafe_allow_html=True)

# 3. ตรวจสอบไฟล์เพลง
music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

if music_files:
    if 'song_index' not in st.session_state:
        st.session_state.song_index = 0
    
    current_song = music_files[st.session_state.song_index]

    # --- ส่วนหัวแอป ---
    st.markdown(f'<div class="marquee-text">NOW VIBING: {current_song}</div>', unsafe_allow_html=True)

    # ปก (วิดีโอ/รูป)
    base_name = os.path.splitext(current_song)[0]
    if os.path.exists(base_name + ".mp4"):
        st.video(base_name + ".mp4", loop=True, autoplay=True, muted=True)
    elif os.path.exists(base_name + ".jpg"):
        st.image(base_name + ".jpg", use_container_width=True)

    # กราฟเสียง
    st.markdown('<div class="visualizer">' + '<div class="bar"></div>'*10 + '</div>', unsafe_allow_html=True)

    # ตัวเล่นเพลง
    st.audio(current_song)

    # --- ส่วนควบคุม ---
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⏭️ เพลงถัดไป"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()
    with c2:
        if st.button("🎲 สุ่มเพลง"):
            st.session_state.song_index = random.randint(0, len(music_files)-1)
            st.rerun()

    st.markdown("---")

    # --- ส่วนกล่อง Playlist แบบใหม่ (ใช้ st.container ล็อคความสูง) ---
    st.subheader("📜 Playlist Library")
    
    # ใช้ container ร่วมกับ CSS เพื่อสร้างกล่องที่มี Scrollbar ของระบบจริงๆ
    with st.container(height=300):
        for i, song in enumerate(music_files):
            if st.button(f"{i+1}. {song}", key=f"p_{i}"):
                st.session_state.song_index = i
                st.rerun()

    # --- JavaScript บังคับเล่นเพลงถัดไป (ฉบับเน้นย้ำ) ---
    components.html(
        """
        <script>
        function checkAudio() {
            const audio = window.parent.document.querySelector('audio');
            const buttons = window.parent.document.querySelectorAll('button');
            
            if (audio) {
                // ถ้าเพลงจบ ให้กดเพลงถัดไป
                audio.onended = function() {
                    for (let btn of buttons) {
                        if (btn.innerText.includes('เพลงถัดไป')) {
                            btn.click();
                            break;
                        }
                    }
                };
                
                // แก้ปัญหาเพลงไม่เล่นเอง: ถ้า paused อยู่ให้สั่ง play
                if (audio.paused && audio.currentTime > 0 && audio.currentTime < audio.duration) {
                     audio.play().catch(e => console.log("User interaction required"));
                }
            }
        }
        setInterval(checkAudio, 1500);
        </script>
        """, height=0
    )
else:
    st.write("ยังไม่มีไฟล์เพลงในระบบครับ")
