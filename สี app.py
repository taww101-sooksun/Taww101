import streamlit as st
import os
import random
import streamlit.components.v1 as components

# --- 1. SET UP ---
st.set_page_config(page_title="SYNAPSE ROOMS", layout="wide")

# ระบบจำค่าสี
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#39FF14" # เขียวเลมอนนีออนแบบในรูปคุณ
if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#121212"
if 'song_index' not in st.session_state:
    st.session_state.song_index = 0

# Sidebar ปรับแต่ง
with st.sidebar:
    st.markdown("### 🎨 ปรับแต่งระบบ")
    # แก้ปัญหา Logo หาย: เช็คไฟล์ก่อนโชว์
    if os.path.exists("logo2.jpg"):
        st.image("logo2.jpg", use_container_width=True)
    
    st.session_state.theme_color = st.color_picker("เลือกสีนีออน", st.session_state.theme_color)
    st.session_state.bg_color = st.color_picker("เลือกสีพื้นหลัง", st.session_state.bg_color)
    st.write("---")
    st.markdown('**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

# --- 2. CSS CUSTOM THEME ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    
    .stApp {{
        background-color: {st.session_state.bg_color} !important;
        color: {st.session_state.theme_color} !important;
    }}

    /* ชื่อเพลงวิ่ง */
    .marquee {{
        width: 100%;
        overflow: hidden;
        white-space: nowrap;
        background: rgba(0,0,0,0.4);
        padding: 15px 0;
        border-radius: 12px;
        border: 2px solid {st.session_state.theme_color};
        box-shadow: 0 0 10px {st.session_state.theme_color}55;
    }}
    .marquee p {{
        display: inline-block;
        padding-left: 100%;
        animation: marquee 25s linear infinite;
        font-family: 'Orbitron', sans-serif;
        font-size: 20px;
        color: {st.session_state.theme_color};
    }}
    @keyframes marquee {{
        0% {{ transform: translate(0, 0); }}
        100% {{ transform: translate(-100%, 0); }}
    }}

    /* ปรับแต่งปุ่มและขอบกล่อง */
    .stButton>button {{
        width: 100%;
        background-color: transparent !important;
        color: {st.session_state.theme_color} !important;
        border: 1px solid {st.session_state.theme_color} !important;
        border-radius: 8px !important;
    }}
    .stButton>button:hover {{
        box-shadow: 0 0 15px {st.session_state.theme_color};
        background-color: {st.session_state.theme_color} !important;
        color: #000 !important;
    }}

    h1, h2, h3, p, span {{ font-family: 'Orbitron', sans-serif; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. ระบบเพลง ---
music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

if music_files:
    current_song = music_files[st.session_state.song_index]

    # หัวข้อหลัก + Logo (ถ้ามี)
    col1, col2 = st.columns([1, 5])
    with col1:
        if os.path.exists("logo2.jpg"):
            st.image("logo2.jpg", width=80)
    with col2:
        st.title("🎸 อยู่นิ่งๆไม่เจ็บตัว MUSIC")

    # ป้ายวิ่ง
    st.markdown(f'<div class="marquee"><p>NOW PLAYING: {current_song} --- UP NEXT: {music_files[(st.session_state.song_index + 1) % len(music_files)]}</p></div>', unsafe_allow_html=True)

    # ปก/วิดีโอ
    base_name = os.path.splitext(current_song)[0]
    if os.path.exists(base_name + ".mp4"):
        st.video(base_name + ".mp4", loop=True, autoplay=True, muted=True)
    elif os.path.exists(base_name + ".jpg"):
        st.image(base_name + ".jpg", use_container_width=True)

    # เครื่องเล่นเพลง (ใส่ ID เพื่อให้ JS หาเจอ)
    st.audio(current_song)

    st.markdown("---")
    
    # รายชื่อเพลง
    st.subheader(f"🎧 เพลงของอยู่นิ่งๆไม่เจ็บตัว 🎸")
    with st.container(border=True, height=220):
        for i, song in enumerate(music_files):
            btn_label = f"▶️ {i+1}. {song}" if i == st.session_state.song_index else f"{i+1}. {song}"
            if st.button(btn_label, key=f"s_{i}"):
                st.session_state.song_index = i
                st.rerun()

    # ปุ่มควบคุม
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⏭️ เพลงถัดไป"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()
    with c2:
        if st.button("🎲 สุ่มเพลง"):
            st.session_state.song_index = random.randint(0, len(music_files) - 1)
            st.rerun()

    # --- 4. JS: เล่นต่อเนื่อง (Force Next Track) ---
    components.html(
        f"""
        <script>
        var skipTime = 10; // ข้ามก่อนจบ 10 วิ
        var fadeSec = 12;

        function syncAudio() {{
            // ค้นหา Audio Tag ในหน้าจอแม่ (Parent)
            var audio = window.parent.document.querySelector('audio');
            var buttons = window.parent.document.querySelectorAll('button');

            if (audio) {{
                // ระบบเล่นอัตโนมัติ (ถ้ามันหยุดเดินให้สั่งรันต่อ)
                if (audio.paused && audio.currentTime > 0 && audio.currentTime < (audio.duration - 1)) {{
                    audio.play().catch(e => {{}});
                }}

                // ระบบเปลี่ยนเพลงล่วงหน้า 10 วิ
                if (audio.duration > 0 && (audio.duration - audio.currentTime) < skipTime) {{
                    for (var i = 0; i < buttons.length; i++) {{
                        if (buttons[i].textContent.includes('เพลงถัดไป')) {{
                            buttons[i].click();
                            break;
                        }}
                    }}
                }}

                // ระบบ Fade
                if (audio.currentTime < fadeSec) {{
                    audio.volume = Math.min(audio.currentTime / fadeSec, 1);
                }} else if (audio.duration - audio.currentTime < fadeSec) {{
                    audio.volume = Math.max((audio.duration - audio.currentTime) / fadeSec, 0);
                }} else {{
                    audio.volume = 1;
                }}
            }}
        }}
        setInterval(syncAudio, 800);
        </script>
        """, height=0
    )
else:
    st.error("ไม่พบไฟล์เพลง .mp3")
