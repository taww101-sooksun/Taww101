import streamlit as st
import os
import random
import base64

# --- 1. SET UP ---
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="centered")

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#39FF14" # เขียวนีออน
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

# --- 3. CSS สไตล์หน้าหลัก (ย้ายทุกอย่างมาไว้ตรงกลาง) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background-color: {st.session_state.bg_color} !important; }}

    .logo-container {{
        display: flex; justify-content: center; margin-top: 20px;
    }}
    .main-logo {{
        width: 100px; height: 100px;
        background-image: url("data:image/png;base64,{logo_b64}");
        background-size: contain; background-repeat: no-repeat;
        filter: drop-shadow(0 0 15px {st.session_state.theme_color});
        animation: pulse 2s infinite alternate;
    }}
    @keyframes pulse {{
        from {{ transform: scale(1); opacity: 0.8; }}
        to {{ transform: scale(1.1); opacity: 1; }}
    }}

    .neon-title {{
        font-family: 'Orbitron', sans-serif;
        color: #fff; text-align: center;
        text-shadow: 0 0 10px {st.session_state.theme_color}, 0 0 20px {st.session_state.theme_color};
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
    
    # ส่วนปรับสี (ย้ายจาก Sidebar มาไว้หน้าหลัก)
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.session_state.theme_color = st.color_picker("🎨 ปรับสีนีออน", st.session_state.theme_color)
    with col_c2:
        st.session_state.bg_color = st.color_picker("🌑 สีพื้นหลัง", st.session_state.bg_color)

    st.write("---")

    # ส่วนแสดงผลวิดีโอ/รูปปก
    base_name = os.path.splitext(current_song)[0]
    if os.path.exists(base_name + ".mp4"):
        st.video(base_name + ".mp4", loop=True, autoplay=True, muted=True)
    elif os.path.exists(base_name + ".jpg"):
        st.image(base_name + ".jpg", use_container_width=True)

    # --- 5. หัวใจหลัก: Audio Engine (แก้ปัญหาเสียงไม่มา) ---
    html_mixer = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .vis-box {{ height: 100px; background: #000; border: 2px solid {st.session_state.theme_color}; border-radius: 15px; margin-bottom: 15px; }}
            .btn-start {{
                width: 100%; padding: 15px; border-radius: 15px; 
                background: transparent; color: {st.session_state.theme_color};
                border: 2px solid {st.session_state.theme_color};
                font-family: 'Orbitron', sans-serif; font-weight: bold; cursor: pointer;
                box-shadow: 0 0 10px {st.session_state.theme_color};
                transition: 0.3s; margin-bottom: 10px;
            }}
            .btn-start:hover {{ background: {st.session_state.theme_color}; color: #000; }}
        </style>
    </head>
    <body>
        <canvas id="canvas" class="vis-box" style="width:100%"></canvas>
        <button id="playBtn" class="btn-start">⚡ ACTIVATE SYSTEM & PLAY</button>
        <div id="status" style="color:{st.session_state.theme_color}; font-size:10px; text-align:center; font-family:sans-serif;">STATUS: STANDBY</div>

        <script>
            let audioCtx, analyser, source, dataArray;
            const songUrl = "./{current_song}";
            const playBtn = document.getElementById('playBtn');

            async function initAndPlay() {{
                try {{
                    if(!audioCtx) {{
                        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                        analyser = audioCtx.createAnalyser();
                        analyser.fftSize = 64;
                        dataArray = new Uint8Array(analyser.frequencyBinCount);
                        draw();
                    }}
                    
                    if (audioCtx.state === 'suspended') await audioCtx.resume();

                    document.getElementById('status').innerText = "LOADING AUDIO...";
                    const res = await fetch(songUrl);
                    const buffer = await audioCtx.decodeAudioData(await res.arrayBuffer());
                    
                    if(source) source.stop();
                    source = audioCtx.createBufferSource();
                    source.buffer = buffer;
                    
                    // ระบบ Gain (Fade In)
                    let gainNode = audioCtx.createGain();
                    gainNode.gain.setValueAtTime(0, audioCtx.currentTime);
                    gainNode.gain.linearRampToValueAtTime(1, audioCtx.currentTime + 3);
                    
                    source.connect(gainNode).connect(analyser).connect(audioCtx.destination);
                    source.start(0);
                    
                    playBtn.style.display = "none";
                    document.getElementById('status').innerText = "NOW PLAYING: {current_song}";

                    source.onended = () => {{
                        // สั่งให้ Streamlit เปลี่ยนเพลงถัดไป
                        window.parent.document.querySelector('button[title="⏭️ NEXT"]').click();
                    }};
                }} catch(e) {{
                    document.getElementById('status').innerText = "ERROR: " + e.message;
                }}
            }}

            function draw() {{
                requestAnimationFrame(draw);
                analyser.getByteFrequencyData(dataArray);
                const canvas = document.getElementById('canvas');
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#000';
                ctx.fillRect(0,0,canvas.width, canvas.height);
                const bWidth = (canvas.width / dataArray.length) * 2.5;
                for(let i=0; i<dataArray.length; i++) {{
                    let h = (dataArray[i]/255) * canvas.height;
                    ctx.fillStyle = '{st.session_state.theme_color}';
                    ctx.shadowBlur = 15; ctx.shadowColor = '{st.session_state.theme_color}';
                    ctx.fillRect(i*bWidth, canvas.height-h, bWidth-3, h);
                }}
            }}

            playBtn.onclick = () => initAndPlay();
        </script>
    </body>
    </html>
    """
    st.components.v1.html(html_mixer, height=220)

    # ปุ่มควบคุมของ Streamlit
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏭️ NEXT"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()
    with col2:
        if st.button("🎲 RANDOM"):
            st.session_state.song_index = random.randint(0, len(music_files) - 1)
            st.rerun()

    # รายชื่อเพลงด้านล่าง
    with st.expander("🎼 TRACKLIST"):
        for i, song in enumerate(music_files):
            if st.button(f"{'▶️' if i==st.session_state.song_index else '▪️'} {song}", key=f"list_{i}"):
                st.session_state.song_index = i
                st.rerun()
else:
    st.error("ไม่พบไฟล์เพลง .mp3 ครับอาจารย์ต๊ะ")
