import streamlit as st
import os
import random
import streamlit.components.v1 as components

# 1. ตั้งค่าหน้าแอป
st.set_page_config(page_title="Vibe Player Motion", layout="centered")

# 2. CSS สายรุ้ง + ตัวอักษรวิ่ง + กราฟเสียง + กล่องรายชื่อ (อัปเดตใหม่)
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

    /* กราฟคลื่นเสียงจำลอง แบบมีสีสัน (Gradient Colors) */
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
        /* เปลี่ยนสีเป็น Gradient: Pale Turquoise ถึง Coral */
        background: linear-gradient(180deg, #AFEEEE, #FF7F50);
        animation: equalize 1s infinite alternate;
        border-radius: 3px;
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
    .bar:nth-child(6)  {{ animation-duration: 0.4s; }}
    .bar:nth-child(7)  {{ animation-duration: 0.8s; }}
    .bar:nth-child(8)  {{ animation-duration: 0.5s; }}
    .bar:nth-child(9)  {{ animation-duration: 0.9s; }}
    .bar:nth-child(10) {{ animation-duration: 0.7s; }}

    /* ตกแต่งปุ่มในรายชื่อเพลงให้สวยงาม */
    .stButton>button {{
        width: 100%;
        text-align: left;
        background-color: rgba(175, 238, 238, 0.8) !important; /* Pale Turquoise โปร่งแสง */
        color: #333 !important;
        border-radius: 10px !important;
        font-weight: bold;
        border: 2px solid white !important;
        margin-bottom: 5px;
    }}
    .stButton>button:hover {{
        background-color: #FF7F50 !important; /* เปลี่ยนเป็น Coral ตอน Hover */
        color: white !important;
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
    st.title("🎸อยู่นิ้งๆไม่เจ็บตัว MUSIC IN MOTION 🎧")

    # 1. ชื่อเพลงวิ่ง (คงเดิม)
    st.markdown(f'<div class="marquee"><p>NOW PLAYING: {current_song} •--• NEXT TRACK UP SOON </p></div>', unsafe_allow_html=True)

    # 2. ปก (วิดีโอหรือรูป)
    base_name = os.path.splitext(current_song)[0]
    if os.path.exists(base_name + ".mp4"):
        st.video(base_name + ".mp4", loop=True, autoplay=True, muted=True)
    elif os.path.exists(base_name + ".jpg"):
        st.image(base_name + ".jpg", use_container_width=True)
    
    # 3. กราฟเสียงจำลอง แบบมีสีสัน
    st.markdown('<div class="visualizer">' + '<div class="bar"></div>'*15 + '</div>', unsafe_allow_html=True)

    st.audio(current_song)

    st.markdown("---")

    # 4. กล่องรายชื่อเพลง (แก้บั๊กให้เข้ากล่องชัวร์ 100% ด้วย st.container height)
    st.subheader("📜 Playlist Library")
    
    # วิธีใหม่: ใช้ st.container ที่ล็อคความสูงและมี Scrollbar ของ Streamlit เอง
    # รับรองว่าปุ่มไม่มีทางเด้งออกไปนอกกล่องเหมือนในรูปที่แล้วครับ
    with st.container(height=250):
        for i, song in enumerate(music_files):
            if st.button(f"{i+1}. {song}", key=f"box_{song}"):
                st.session_state.song_index = i
                st.rerun()

    # 5. ปุ่มควบคุม (คงเดิม)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏭️ เพลงถัดไป"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()
    with col2:
        if st.button("🎲 สุ่มเพลง"):
            st.session_state.song_index = random.randint(0, len(music_files) - 1)
            st.rerun()

    # JavaScript สำหรับ Auto-next (คงเดิม)
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
    st.error("ไม่พบไฟล์เพลง .mp3")
