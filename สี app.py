import streamlit as st
import os
import random
import streamlit.components.v1 as components

# 1. ตั้งค่าหน้าแอป
st.set_page_config(page_title="Vibe Player Motion", layout="centered")

# 2. CSS สายรุ้ง + ตัวอักษรวิ่ง + กราฟเสียง + กล่องรายชื่อ
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

    /* ชื่อเพลงวิ่ง (Marquee) */
    .marquee {{
        width: 100%;
        overflow: hidden;
        white-space: nowrap;
        background: rgba(0,0,0,0.5);
        padding: 10px 0;
        border-radius: 10px;
        margin-bottom: 20px;
    }}
    .marquee p {{
        display: inline-block;
        padding-left: 100%;
        animation: marquee 15s linear infinite;
        font-family: 'Orbitron', sans-serif;
        font-size: 24px;
        color: #AFEEEE;
        text-shadow: 2px 2px 4px #000;
        margin: 0;
    }}
    @keyframes marquee {{
        0% {{ transform: translate(0, 0); }}
        100% {{ transform: translate(-100%, 0); }}
    }}

    /* กราฟคลื่นเสียงจำลอง */
    .visualizer {{
        display: flex;
        align-items: flex-end;
        justify-content: center;
        height: 50px;
        gap: 3px;
        margin-bottom: 20px;
    }}
    .bar {{
        width: 8px;
        background: #AFEEEE;
        animation: equalize 1s infinite alternate;
    }}
    @keyframes equalize {{
        0% {{ height: 5px; }}
        100% {{ height: 50px; }}
    }}
    /* สุ่มความเร็วให้แต่ละแท่ง */
    .bar:nth-child(1)  {{ animation-duration: 0.4s; }}
    .bar:nth-child(2)  {{ animation-duration: 0.7s; }}
    .bar:nth-child(3)  {{ animation-duration: 0.5s; }}
    .bar:nth-child(4)  {{ animation-duration: 0.9s; }}
    .bar:nth-child(5)  {{ animation-duration: 0.6s; }}

    /* กล่องเก็บรายชื่อเพลง (Scroll Box) */
    .song-box {{
        height: 250px;
        overflow-y: scroll;
        background: rgba(255, 255, 255, 0.2);
        padding: 15px;
        border-radius: 15px;
        border: 2px solid #AFEEEE;
    }}
    </style>
    """, unsafe_allow_html=True)

# 3. จัดการเพลง
music_files = [f for f in os.listdir('.') if f.lower().endswith(".mp3")]

if music_files:
    if 'song_index' not in st.session_state:
        st.session_state.song_index = 0
    
    current_song = music_files[st.session_state.song_index]

    # --- ส่วนแสดงผล ---
    st.title("🚀 MUSIC IN MOTION")

    # 1. ชื่อเพลงวิ่ง
    st.markdown(f'<div class="marquee"><p>NOW PLAYING: {current_song} •--• NEXT SONG UP SOON </p></div>', unsafe_allow_html=True)

    # 2. ปก (วิดีโอหรือรูป)
    base_name = os.path.splitext(current_song)[0]
    if os.path.exists(base_name + ".mp4"):
        st.video(base_name + ".mp4", loop=True, autoplay=True, muted=True)
    elif os.path.exists(base_name + ".jpg"):
        st.image(base_name + ".jpg", use_container_width=True)
    
    # 3. กราฟเสียงจำลอง (Visualizer)
    st.markdown('<div class="visualizer">' + '<div class="bar"></div>'*15 + '</div>', unsafe_allow_html=True)

    st.audio(current_song)

    # 4. กล่องรายชื่อเพลง (Scroll Box)
    st.subheader("📜 Playlist Library")
    with st.container():
        # เราใช้ st.container ร่วมกับ CSS song-box
        st.markdown('<div class="song-box">', unsafe_allow_html=True)
        for i, song in enumerate(music_files):
            if st.button(f"{i+1}. {song}", key=f"box_{song}"):
                st.session_state.song_index = i
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 5. ปุ่มควบคุม
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏭️ เพลงถัดไป"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()
    with col2:
        if st.button("🎲 สุ่มเพลง"):
            st.session_state.song_index = random.randint(0, len(music_files) - 1)
            st.rerun()

    # JavaScript สำหรับ Auto-next
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
        """, height=0
    )
else:
    st.error("ไม่พบไฟล์เพลง")
