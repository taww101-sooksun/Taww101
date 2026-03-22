import streamlit as st
import os
import random
import streamlit.components.v1 as components

# 1. ตั้งค่าหน้าแอป
st.set_page_config(page_title="Vibe Player Pro", layout="centered")

# 2. CSS สายรุ้ง (คงเดิมที่คุณชอบ)
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
    h1, h3, p {{ color: white !important; text-shadow: 2px 2px 4px #000; }}
    .stButton>button {{
        width: 100%;
        background-color: #AFEEEE !important;
        border-radius: 12px;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# 3. จัดการไฟล์เพลง
music_files = [f for f in os.listdir('.') if f.lower().endswith(".mp3")]

if music_files:
    if 'song_index' not in st.session_state:
        st.session_state.song_index = 0

    current_song = music_files[st.session_state.song_index]

    if os.path.exists("logo2.jpg"):
        st.image("logo2.jpg", width=500)

    st.title("🎵 NON-STOP อยู่นิ้งๆไม่เจ็บตัว")
    
    # --- ส่วนที่ 2: แสดงปกเพลง (ตรวจสอบ .jpg, .jpeg, .png) ---
    # ลองหาไฟล์ภาพที่ชื่อเหมือนเพลง
    base_name = os.path.splitext(current_song)[0] # ตัด .mp3 ออก
    cover_file = None
    for ext in ['.jpg', '.jpeg', '.png', '.JPG']:
        if os.path.exists(base_name + ext):
            cover_file = base_name + ext
            break

    if cover_file:
        st.image(cover_file, caption=f"Now Playing: {current_song}", use_container_width=True)
    else:
        st.write("*(ไม่พบไฟล์รูปปกที่ชื่อตรงกับเพลง)*")

    st.write(f"### 🎧 {current_song}")
    st.audio(current_song)

    # --- ส่วนที่ 3: JavaScript สั่งเล่นอัตโนมัติ (เพิ่ม .play()) ---
    components.html(
        f"""
        <script>
        function autoNext() {{
            var audio = window.parent.document.querySelector('audio');
            if (audio) {{
                audio.onended = function() {{
                    var buttons = window.parent.document.querySelectorAll('button');
                    for (var i = 0; i < buttons.length; i++) {{
                        if (buttons[i].textContent.includes('เพลงถัดไป')) {{
                            buttons[i].click();
                            break;
                        }}
                    }}
                }};
                // พยายามสั่งให้เล่นเองถ้าโหลดเสร็จ (อาจติดกฎ Browser ในครั้งแรก)
                audio.play().catch(function(error) {{
                    console.log("Autoplay blocked, wait for user interaction");
                }});
            }}
        }}
        setInterval(autoNext, 1000);
        </script>
        """,
        height=0,
    )

    # --- ส่วนที่ 4: ปุ่มควบคุม ---
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⏭️ เพลงถัดไป"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()
    with c2:
        if st.button("🎲 สุ่มเพลง"):
            st.session_state.song_index = random.randint(0, len(music_files) - 1)
            st.rerun()

    st.markdown("---")
    st.subheader("📜 รายชื่อเพลง")
    for i, song in enumerate(music_files):
        if st.button(f"{i+1}. {song}", key=f"list_{song}"):
            st.session_state.song_index = i
            st.rerun()
else:
    st.error("ไม่พบไฟล์เพลง .mp3")
