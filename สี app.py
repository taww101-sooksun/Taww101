import streamlit as st
import os
import random
import streamlit.components.v1 as components

# 1. ตั้งค่าหน้าแอป
st.set_page_config(page_title="Vibe Motion Fix", layout="centered")

# 2. CSS แบบคุมเข้ม (บังคับทุกอย่างเข้าที่)
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

    /* ชื่อเพลงวิ่ง */
    .marquee {{
        width: 100%;
        overflow: hidden;
        background: rgba(0,0,0,0.6);
        padding: 15px 0;
        border-radius: 15px;
        border: 2px solid #AFEEEE;
        margin-bottom: 20px;
    }}
    .marquee p {{
        display: inline-block;
        white-space: nowrap;
        animation: marquee 15s linear infinite;
        font-family: 'Orbitron', sans-serif;
        font-size: 22px;
        color: #AFEEEE;
        margin: 0;
    }}
    @keyframes marquee {{
        0% {{ transform: translateX(100%); }}
        100% {{ transform: translateX(-100%); }}
    }}

    /* กราฟเสียง */
    .visualizer {{
        display: flex;
        align-items: flex-end;
        justify-content: center;
        height: 40px;
        gap: 4px;
        margin: 15px 0;
    }}
    .bar {{
        width: 10px;
        background: #AFEEEE;
        animation: equalize 0.8s infinite alternate;
        border-radius: 2px;
    }}
    @keyframes equalize {{
        0% {{ height: 5px; }}
        100% {{ height: 40px; }}
    }}

    /* บังคับกล่องรายชื่อเพลง (Scroll Box) ให้ใช้งานได้จริง */
    .song-container {{
        background: rgba(0, 0, 0, 0.4);
        border: 3px solid #AFEEEE;
        border-radius: 20px;
        height: 300px;
        overflow-y: auto;
        padding: 20px;
        margin-top: 20px;
    }}
    
    /* ตกแต่ง Scrollbar ให้ดูเท่ */
    .song-container::-webkit-scrollbar {{
        width: 8px;
    }}
    .song-container::-webkit-scrollbar-thumb {{
        background: #AFEEEE;
        border-radius: 10px;
    }}

    h1, h3, p {{
        font-family: 'Orbitron', sans-serif;
        color: white !important;
        text-shadow: 2px 2px 4px #000;
    }}
    </style>
    """, unsafe_allow_html=True)

# 3. จัดการเพลง
music_files = [f for f in os.listdir('.') if f.lower().endswith(".mp3")]

if music_files:
    if 'song_index' not in st.session_state:
        st.session_state.song_index = 0
    
    current_song = music_files[st.session_state.song_index]

    st.title("🎸อยู่นิ้งๆไม่เจ็บตัว MUSIC🎧")

    # 1. ชื่อเพลงวิ่ง (Marquee)
    st.markdown(f'<div class="marquee"><p>NOW PLAYING: {current_song} •--• NEXT TRACK LOADING... </p></div>', unsafe_allow_html=True)

    # 2. ปกวิดีโอ/รูป
    base_name = os.path.splitext(current_song)[0]
    if os.path.exists(base_name + ".mp4"):
        st.video(base_name + ".mp4", loop=True, autoplay=True, muted=True)
    elif os.path.exists(base_name + ".jpg"):
        st.image(base_name + ".jpg", use_container_width=True)
    
    # 3. กราฟเสียง + เครื่องเล่น
    st.markdown('<div class="visualizer">' + '<div class="bar" style="animation-delay: '+str(random.random())+'s"></div>'*12 + '</div>', unsafe_allow_html=True)
    st.audio(current_song)

    # 4. ปุ่มควบคุมหลัก
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⏭️ เพลงถัดไป"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()
    with c2:
        if st.button("🎲 สุ่มเพลง"):
            st.session_state.song_index = random.randint(0, len(music_files) - 1)
            st.rerun()

    # 5. กล่องรายชื่อเพลง (ใส่ HTML บังคับเข้ากล่อง)
    st.write("### 📜 Playlist Library")
    
    # สร้าง HTML สำหรับปุ่มข้างในกล่อง
    song_list_html = ""
    st.markdown('<div class="song-container">', unsafe_allow_html=True)
    for i, song in enumerate(music_files):
        if st.button(f"{i+1}. {song}", key=f"list_{song}"):
            st.session_state.song_index = i
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # 6. JavaScript สำหรับ Auto-next + บังคับ Play
    components.html(
        """
        <script>
        function startSync() {
            var audio = window.parent.document.querySelector('audio');
            if (audio) {
                // เมื่อเพลงจบ ให้กดปุ่มถัดไป
                audio.onended = function() {
                    var buttons = window.parent.document.querySelectorAll('button');
                    for (var i = 0; i < buttons.length; i++) {
                        if (buttons[i].textContent.includes('เพลงถัดไป')) {
                            buttons[i].click();
                            break;
                        }
                    }
                };
                // พยายามสั่งเล่น (ถ้ามันค้าง)
                if (audio.paused) {
                    audio.play().catch(e => console.log("Waiting for user..."));
                }
            }
        }
        setInterval(startSync, 2000); // เช็คทุก 2 วินาที
        </script>
        """, height=0
    )
else:
    st.error("ไม่พบไฟล์เพลง")
