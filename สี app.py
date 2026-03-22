import streamlit as st
import os
import random
import streamlit.components.v1 as components

# 1. ตั้งค่าหน้าแอป
st.set_page_config(page_title="Vibe Player Pro Max", layout="centered")

# 2. CSS สายรุ้ง + ตัวอักษรวิ่ง + กราฟเสียง + ดีไซน์ปุ่ม (จัดเต็ม)
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    
    .stApp {{
        background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
        background-size: 1200% 1200%;
        animation: RainbowFlow 30s ease infinite;
    }}
    @keyframes RainbowFlow {{
        0%{{background-position:0% 50%}}
        50%{{background-position:100% 50%}}
        100%{{background-position:0% 50%}}
    }}

    .marquee {{
        width: 100%;
        overflow: hidden;
        white-space: nowrap;
        background: rgba(0,0,0,0.6);
        padding: 15px 0;
        border-radius: 12px;
        margin-bottom: 15px;
        border: 2px solid #AFEEEE;
    }}
    .marquee p {{
        display: inline-block;
        padding-left: 100%;
        animation: marquee 15s linear infinite;
        font-family: 'Orbitron', sans-serif;
        font-size: 22px;
        color: #AFEEEE;
        text-shadow: 2px 2px 4px #000;
        margin: 0;
    }}
    @keyframes marquee {{
        0% {{ transform: translate(0, 0); }}
        100% {{ transform: translate(-100%, 0); }}
    }}

    .visualizer {{
        display: flex;
        align-items: flex-end;
        justify-content: center;
        height: 50px;
        gap: 3px;
        margin-bottom: 15px;
    }}
    .bar {{
        width: 8px;
        background: linear-gradient(180deg, #AFEEEE, #FF7F50);
        animation: equalize 1s infinite alternate;
        border-radius: 3px;
    }}
    @keyframes equalize {{
        0% {{ height: 5px; }}
        100% {{ height: 50px; }}
    }}
    .bar:nth-child(odd) {{ animation-duration: 0.6s; }}
    .bar:nth-child(even) {{ animation-duration: 0.9s; }}

    .stButton>button {{
        width: 100%;
        text-align: left;
        background-color: rgba(175, 238, 238, 0.8) !important;
        color: #333 !important;
        border-radius: 10px !important;
        font-weight: bold;
        border: 2px solid white !important;
        margin-bottom: 5px;
    }}
    .stButton>button:hover {{
        background-color: #FF7F50 !important;
        color: white !important;
    }}
    h1, h3, p, span {{ font-family: 'Orbitron', sans-serif; color: white !important; text-shadow: 2px 2px 4px #000; }}
    </style>
    """, unsafe_allow_html=True)

# 3. จัดการไฟล์เพลง
music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

if music_files:
    if 'song_index' not in st.session_state:
        st.session_state.song_index = 0
    
    current_song = music_files[st.session_state.song_index]

    st.title("🎸 อยู่นิ่งๆไม่เจ็บตัว 🎼 MUSIC")

    # 1. ชื่อเพลงวิ่ง
    st.markdown(f'<div class="marquee"><p>NOW PLAYING: {current_song} •--• NEXT TRACK UP SOON </p></div>', unsafe_allow_html=True)

    # 2. ปก (วิดีโอหรือรูป)
    base_name = os.path.splitext(current_song)[0]
    if os.path.exists(base_name + ".mp4"):
        st.video(base_name + ".mp4", loop=True, autoplay=True, muted=True)
    elif os.path.exists(base_name + ".jpg"):
        st.image(base_name + ".jpg", use_container_width=True)
    
    # 3. กราฟเสียงสีสัน
    st.markdown('<div class="visualizer">' + '<div class="bar"></div>'*20 + '</div>', unsafe_allow_html=True)

    # 4. เครื่องเล่นเพลง
    st.audio(current_song)

    st.markdown("---")

    # 5. กล่องรายชื่อเพลง (ล็อคเข้าที่ด้วย Container)
    st.subheader("📜 ฟังผลงานเพลง🎧🎼อยู่นิ้งๆไม่เจ็บตัว🎸")
    with st.container(height=300):
        for i, song in enumerate(music_files):
            if st.button(f"{i+1}. {song}", key=f"box_{i}"):
                st.session_state.song_index = i
                st.rerun()

    # 6. ปุ่มควบคุม
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏭️ เพลงถัดไป"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()
    with col2:
        if st.button("🎲 สุ่มเพลง"):
            st.session_state.song_index = random.randint(0, len(music_files) - 1)
            st.rerun()

    # 7. JavaScript: Fade In/Out (12s) + Auto-Next (บังคับเล่น)
    components.html(
        """
        <script>
        var fadeDuration = 12; // ตั้งค่า Fade 12 วินาที

        function handleAudioSync() {
            var audio = window.parent.document.querySelector('audio');
            var buttons = window.parent.document.querySelectorAll('button');
            
            if (audio) {
                // ระบบ Fade In (เริ่มเพลง)
                if (audio.currentTime < fadeDuration && !audio.paused) {
                    audio.volume = Math.min(audio.currentTime / fadeDuration, 1);
                } 
                // ระบบ Fade Out (จบเพลง)
                else if (audio.duration - audio.currentTime < fadeDuration && !audio.paused) {
                    audio.volume = Math.max((audio.duration - audio.currentTime) / fadeDuration, 0);
                } 
                else {
                    audio.volume = 1;
                }

                // ระบบ Auto-Next
                audio.onended = function() {
                    for (var i = 0; i < buttons.length; i++) {
                        if (buttons[i].textContent.includes('เพลงถัดไป')) {
                            buttons[i].click();
                            break;
                        }
                    }
                };

                // บังคับ Play กรณีโหลดเพลงใหม่แล้วนิ่ง
                if (audio.paused && audio.currentTime == 0) {
                    audio.play().catch(e => console.log("User interaction needed"));
                }
            }
        }
        setInterval(handleAudioSync, 500);
        </script>
        """, height=0
    )
else:
    st.error("ไม่พบไฟล์เพลง .mp3 ในโฟลเดอร์ครับ")
