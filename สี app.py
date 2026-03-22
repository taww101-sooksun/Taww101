import streamlit as st
import os
import random
import streamlit.components.v1 as components

# 1. ตั้งค่าหน้าแอป
st.set_page_config(page_title="Vibe Player Pro Max", layout="centered")

# 2. CSS ปรับปรุงขอบกล่องรายการเพลง
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

    /* ปรับปรุงขอบกล่องรายการเพลงให้ชัดเจน */
    [data-testid="stVVerticalBlock"] > div > div > [data-testid="stVerticalBlockBorderWrapper"] {{
        border: 3px solid #AFEEEE !important;
        border-radius: 15px !important;
        background: rgba(0, 0, 0, 0.4) !important;
        box-shadow: 0px 0px 15px rgba(175, 238, 238, 0.5);
        padding: 10px;
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
        animation: marquee 30s linear infinite;
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

    st.markdown(f'<div class="marquee"><p>NOW PLAYING: {current_song} •--• NEXT TRACK UP SOON </p></div>', unsafe_allow_html=True)

    # ปก
    base_name = os.path.splitext(current_song)[0]
    if os.path.exists(base_name + ".mp4"):
        st.video(base_name + ".mp4", loop=True, autoplay=True, muted=True)
    elif os.path.exists(base_name + ".jpg"):
        st.image(base_name + ".jpg", use_container_width=True)
    
    st.audio(current_song)

    st.markdown("---")

    # 5. กล่องรายชื่อเพลง (เพิ่ม Border ผ่าน Container)
    st.subheader("🎧 รายชื่อเพลง")
    with st.container(border=True, height=250):
        for i, song in enumerate(music_files):
            # เน้นสีเพลงที่กำลังเล่นอยู่
            label = f"▶️ {i+1}. {song}" if i == st.session_state.song_index else f"{i+1}. {song}"
            if st.button(label, key=f"box_{i}"):
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

    # 7. JavaScript: แก้ไข Fade และระบบเปลี่ยนเพลงก่อนจบ 10 วินาที
    components.html(
        """
        <script>
        var fadeDuration = 12; 
        var skipThreshold = 10; // เปลี่ยนเพลงก่อนจบ 10 วินาที
        var hasSkipped = false;

        function handleAudioSync() {
            var audio = window.parent.document.querySelector('audio');
            var buttons = window.parent.document.querySelectorAll('button');
            
            if (audio) {
                // 1. ระบบ Fade In (ป้องกันเสียงกระชาก)
                if (audio.currentTime < fadeDuration) {
                    audio.volume = Math.max(0, Math.min(audio.currentTime / fadeDuration, 1));
                } 
                // 2. ระบบ Fade Out (เริ่มเบาลงก่อนจบ)
                else if (audio.duration - audio.currentTime < fadeDuration) {
                    audio.volume = Math.max(0, (audio.duration - audio.currentTime) / fadeDuration);
                } 
                else {
                    audio.volume = 1;
                }

                // 3. ระบบเปลี่ยนเพลงล่วงหน้า (Skip before end)
                if (audio.duration > 0 && (audio.duration - audio.currentTime) < skipThreshold && !hasSkipped) {
                    hasSkipped = true; // กัน Loop รัวๆ
                    for (var i = 0; i < buttons.length; i++) {
                        if (buttons[i].textContent.includes('เพลงถัดไป')) {
                            buttons[i].click();
                            break;
                        }
                    }
                }

                if (audio.paused && audio.currentTime == 0) {
                    audio.play().catch(e => {});
                }
            }
        }
        setInterval(handleAudioSync, 300); // เช็คถี่ขึ้นเพื่อความเนียน
        </script>
        """, height=0
    )
else:
    st.error("ไม่พบไฟล์เพลง .mp3 ในโฟลเดอร์ครับ")
