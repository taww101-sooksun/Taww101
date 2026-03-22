import streamlit as st
import os
import random
import streamlit.components.v1 as components

# --- 1. SET UP & THEME SELECTOR ---
st.set_page_config(page_title="Vibe Player Pro Max", layout="wide")

# ค่าเริ่มต้นของสี
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00f2fe" 
if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#000000"

with st.sidebar:
    if os.path.exists("logo2.jpg"):
        st.image("logo2.jpg", use_container_width=True)
        
    st.markdown("### 🎨 ปรับแต่งสีระบบ")
    # เลือกสีนีออน (เส้นขอบ/ตัวอักษร)
    st.session_state.theme_color = st.color_picker("เลือกสีนีออน", st.session_state.theme_color)
    # เลือกสีพื้นหลัง
    st.session_state.bg_color = st.color_picker("เลือกสีพื้นหลัง", st.session_state.bg_color)
    
    st.write("---")
    st.markdown(f'**สโลแกน:** \n*"อยู่นิ่งๆ ไม่เจ็บตัว"*')

# --- 2. CSS Dynamic Theme ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    
    .stApp {{
        background-color: {st.session_state.bg_color} !important;
        color: {st.session_state.theme_color} !important;
    }}

    /* ขอบกล่องรายการเพลง */
    [data-testid="stVVerticalBlock"] > div > div > [data-testid="stVerticalBlockBorderWrapper"] {{
        border: 2px solid {st.session_state.theme_color} !important;
        border-radius: 15px !important;
        background: rgba(255, 255, 255, 0.05) !important;
        box-shadow: 0px 0px 15px {st.session_state.theme_color}44;
        padding: 15px;
    }}

    .marquee {{
        width: 100%;
        overflow: hidden;
        white-space: nowrap;
        background: rgba(0,0,0,0.5);
        padding: 15px 0;
        border-radius: 12px;
        margin-bottom: 15px;
        border: 2px solid {st.session_state.theme_color};
    }}
    .marquee p {{
        display: inline-block;
        padding-left: 100%;
        animation: marquee 30s linear infinite;
        font-family: 'Orbitron', sans-serif;
        font-size: 22px;
        color: {st.session_state.theme_color};
        text-shadow: 0px 0px 10px {st.session_state.theme_color};
    }}
    @keyframes marquee {{
        0% {{ transform: translate(0, 0); }}
        100% {{ transform: translate(-100%, 0); }}
    }}

    .stButton>button {{
        width: 100%;
        background-color: transparent !important;
        color: {st.session_state.theme_color} !important;
        border: 1px solid {st.session_state.theme_color} !important;
        border-radius: 10px !important;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        background-color: {st.session_state.theme_color} !important;
        color: {st.session_state.bg_color} !important;
        box-shadow: 0px 0px 15px {st.session_state.theme_color};
    }}
    
    h1, h2, h3, p, span {{ font-family: 'Orbitron', sans-serif; color: {st.session_state.theme_color} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. ระบบจัดการเพลง ---
music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

if music_files:
    if 'song_index' not in st.session_state:
        st.session_state.song_index = 0
    
    current_song = music_files[st.session_state.song_index]

    # หัวข้อ
    st.title("🎸 อยู่นิ้งๆไม่เจ็บตัว 🎼 MUSIC")

    # 1. ชื่อเพลงวิ่ง
    st.markdown(f'<div class="marquee"><p>NOW PLAYING: {current_song} •--• NEXT TRACK UP SOON </p></div>', unsafe_allow_html=True)

    # 2. ปก/วิดีโอ
    base_name = os.path.splitext(current_song)[0]
    if os.path.exists(base_name + ".mp4"):
        st.video(base_name + ".mp4", loop=True, autoplay=True, muted=True)
    elif os.path.exists(base_name + ".jpg"):
        st.image(base_name + ".jpg", use_container_width=True)
    
    # 3. เครื่องเล่นเพลง
    st.audio(current_song)

    st.markdown("---")

    # 4. กล่องรายชื่อเพลง
    st.subheader("🎧 เพลงของอยู่นิ้งๆไม่เจ็บตัว🎸")
    with st.container(border=True, height=250):
        for i, song in enumerate(music_files):
            label = f"▶️ {i+1}. {song}" if i == st.session_state.song_index else f"{i+1}. {song}"
            if st.button(label, key=f"box_{i}"):
                st.session_state.song_index = i
                st.rerun()

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

    # 6. JavaScript: ปรับปรุงให้เล่นต่อเนื่องและ Fade เนียนขึ้น
    components.html(
        """
        <script>
        var fadeDuration = 12; 
        var skipThreshold = 10; 
        var hasSkipped = false;

        function checkAndPlay() {
            var audio = window.parent.document.querySelector('audio');
            var buttons = window.parent.document.querySelectorAll('button');
            
            if (audio) {
                // บังคับเล่น (แก้ปัญหาเพลงหยุดเดิน)
                if (audio.paused && audio.currentTime > 0 && audio.currentTime < (audio.duration - 1)) {
                    audio.play().catch(e => console.log("Waiting for user interaction"));
                }

                // Fade In
                if (audio.currentTime < fadeDuration) {
                    audio.volume = Math.max(0, Math.min(audio.currentTime / fadeDuration, 1));
                } 
                // Fade Out & Skip
                else if (audio.duration - audio.currentTime < fadeDuration) {
                    audio.volume = Math.max(0, (audio.duration - audio.currentTime) / fadeDuration);
                    
                    // เปลี่ยนเพลงก่อนจบ 10 วิ
                    if ((audio.duration - audio.currentTime) < skipThreshold && !hasSkipped) {
                        hasSkipped = true;
                        for (var i = 0; i < buttons.length; i++) {
                            if (buttons[i].textContent.includes('เพลงถัดไป')) {
                                buttons[i].click();
                                break;
                            }
                        }
                    }
                } else {
                    audio.volume = 1;
                }
            }
        }
        // ตรวจสอบทุกๆ 500ms
        setInterval(checkAndPlay, 500);
        </script>
        """, height=0
    )
else:
    st.error("ไม่พบไฟล์เพลง .mp3 ในโฟลเดอร์")
