import streamlit as st
import os
import random
import base64

# --- 1. SET UP ---
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="centered")

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#39FF14"
if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#000000"
if 'song_index' not in st.session_state:
    st.session_state.song_index = 0

# --- 2. ฟังก์ชันแปลงรูปโลโก้ ---
def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

logo_b64 = get_base64("logo1.png")

# --- 3. CSS หน้าหลัก ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background-color: {st.session_state.bg_color} !important; }}

    .logo-container {{ display: flex; justify-content: center; margin-top: 20px; }}
    .main-logo {{
        width: 100px; height: 100px;
        background-image: url("data:image/png;base64,{logo_b64}");
        background-size: contain; background-repeat: no-repeat;
        filter: drop-shadow(0 0 15px {st.session_state.theme_color});
        animation: pulse 2s infinite alternate;
    }}
    @keyframes pulse {{ from {{ transform: scale(1); }} to {{ transform: scale(1.1); }} }}

    .neon-title {{
        font-family: 'Orbitron', sans-serif; color: #fff; text-align: center;
        text-shadow: 0 0 10px {st.session_state.theme_color};
        font-size: 1.8rem; margin: 20px 0;
    }}
    </style>
    <div class="logo-container"><div class="main-logo"></div></div>
    <h1 class="neon-title">SYNAPSE COMMAND CENTER</h1>
    """, unsafe_allow_html=True)

# --- 4. ระบบจัดการไฟล์เพลง ---
music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

if music_files:
    current_song = music_files[st.session_state.song_index]
    
    # ส่วนปรับสีหน้าหลัก
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.theme_color = st.color_picker("🎨 สีระบบ", st.session_state.theme_color)
    with c2:
        st.session_state.bg_color = st.color_picker("🌑 สีพื้นหลัง", st.session_state.bg_color)

    # วิดีโอหรือรูปปก
    base_name = os.path.splitext(current_song)[0]
    if os.path.exists(base_name + ".mp4"):
        st.video(base_name + ".mp4", loop=True, autoplay=True, muted=True)
    elif os.path.exists(base_name + ".jpg"):
        st.image(base_name + ".jpg", use_container_width=True)

    # --- 5. AUDIO ENGINE (เน้นให้เสียงออก) ---
    # ใช้ HTML5 Audio ร่วมกับ Web Audio API เพื่อความชัวร์
    html_mixer = f"""
    <div id="mixer-container">
        <canvas id="canvas" style="width:100%; height:100px; background:#000; border:2px solid {st.session_state.theme_color}; border-radius:15px;"></canvas>
        <button id="powerBtn" style="width:100%; padding:20px; margin-top:10px; border-radius:15px; background:transparent; color:{st.session_state.theme_color}; border:3px solid {st.session_state.theme_color}; font-family:'Orbitron', sans-serif; font-weight:bold; cursor:pointer; box-shadow: 0 0 15px {st.session_state.theme_color};">
            CLICK TO START AUDIO ⚡
        </button>
        <audio id="mainAudio" src="./{current_song}" crossorigin="anonymous"></audio>
        <div id="trackName" style="color:{st.session_state.theme_color}; text-align:center; font-size:12px; margin-top:10px; font-family:sans-serif;">STATUS: READY</div>
    </div>

    <script>
        const audio = document.getElementById('mainAudio');
        const btn = document.getElementById('powerBtn');
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        let audioCtx, analyser, source, dataArray;

        btn.onclick = function() {{
            if (!audioCtx) {{
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = audioCtx.createAnalyser();
                source = audioCtx.createMediaElementSource(audio);
                source.connect(analyser);
                analyser.connect(audioCtx.destination);
                analyser.fftSize = 64;
                dataArray = new Uint8Array(analyser.frequencyBinCount);
                renderFrame();
            }}
            
            if (audio.paused) {{
                audio.play().then(() => {{
                    btn.innerText = "SYSTEM ACTIVE 🟢";
                    btn.style.opacity = "0.5";
                    document.getElementById('trackName').innerText = "PLAYING: {current_song}";
                }}).catch(err => {{
                    document.getElementById('trackName').innerText = "ERROR: " + err.message;
                }});
            }}
        }};

        function renderFrame() {{
            requestAnimationFrame(renderFrame);
            analyser.getByteFrequencyData(dataArray);
            ctx.fillStyle = "#000";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            const barWidth = (canvas.width / dataArray.length) * 2;
            for (let i = 0; i < dataArray.length; i++) {{
                let h = (dataArray[i] / 255) * canvas.height;
                ctx.fillStyle = "{st.session_state.theme_color}";
                ctx.fillRect(i * barWidth, canvas.height - h, barWidth - 2, h);
            }}
        }}

        // เมื่อเพลงจบให้กดปุ่ม NEXT ของ Streamlit
        audio.onended = function() {{
            window.parent.document.querySelector('button[title="⏭️ NEXT"]').click();
        }};
    </script>
    """
    st.components.v1.html(html_mixer, height=250)

    # ปุ่มควบคุม
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏭️ NEXT"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()
    with col2:
        if st.button("🎲 RANDOM"):
            st.session_state.song_index = random.randint(0, len(music_files) - 1)
            st.rerun()

    with st.expander("🎼 TRACKLIST"):
        for i, song in enumerate(music_files):
            if st.button(f"{'▶️' if i==st.session_state.song_index else '▪️'} {song}", key=f"list_{i}"):
                st.session_state.song_index = i
                st.rerun()
else:
    st.error("ไม่พบไฟล์เพลง .mp3 ในโฟลเดอร์ครับ")
