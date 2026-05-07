import streamlit as st
import streamlit.components.v1 as components
import os
import base64

# ==========================================
# ส่วนที่ 1: เตรียม Session State & ข้อมูล
# ==========================================

if 'song_index' not in st.session_state:
    st.session_state.song_index = 0

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_base64 = get_base64_image("logo1.png")
logo_html_link = f"data:image/png;base64,{logo_base64}" if logo_base64 else ""

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Prompt:wght@700&display=swap');
    header {{visibility: hidden;}} footer {{visibility: hidden;}}
    .stApp {{ background: #050505; color: white; }}

    .logo-container {{ display: flex; justify-content: center; margin-top: 10px; }}
    .neon-logo {{
        width: 100px; height: 100px;
        background-image: url("{logo_html_link}");
        background-size: contain; background-repeat: no-repeat;
        filter: drop-shadow(0 0 10px #00f3ff);
        animation: pulse 2s infinite ease-in-out;
    }}
    @keyframes pulse {{
        0%, 100% {{ transform: scale(1); filter: drop-shadow(0 0 10px #00f3ff); }}
        50% {{ transform: scale(1.05); filter: drop-shadow(0 0 15px #ff00de); }}
    }}
    </style>
    <div class="logo-container"><div class="neon-logo"></div></div>
    """, unsafe_allow_html=True)

# ==========================================
# ส่วนที่ 2: ส่วนเลือกไฟล์วิดีโอ (Video Upload)
# ==========================================

st.subheader("📽️ ระบบฉายวิดีโอ & คุมเสียง")
video_file = st.file_uploader("เลือกไฟล์วิดีโอจากเครื่องของคุณ (.mp4)", type=["mp4"])

video_url = ""
if video_file is not None:
    # แปลงวิดีโอเป็น Base64 เพื่อให้เล่นใน HTML ได้
    video_bytes = video_file.read()
    video_b64 = base64.b64encode(video_bytes).decode()
    video_url = f"data:video/mp4;base64,{video_b64}"

# ==========================================
# ส่วนที่ 3: Logic การดึงเพลงและ HTML Player
# ==========================================

music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])

if not music_files:
    st.warning("⚠️ ไม่พบไฟล์ .mp3 ในเครื่อง (วางไว้โฟลเดอร์เดียวกับโค้ดนะ)")
else:
    current_song = music_files[st.session_state.song_index]
    with open(current_song, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode()
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background: transparent; font-family: 'Orbitron', sans-serif; overflow: hidden; color: white; }}
            .video-screen {{ width: 100%; border-radius: 12px; border: 2px solid #333; background: #000; aspect-ratio: 16/9; object-fit: cover; }}
            .mini-visualizer {{ height: 80px; background: rgba(0,0,0,0.8); border: 1px solid #222; border-radius: 8px; margin-top: 10px; }}
            audio {{ width: 100%; height: 30px; filter: invert(100%) opacity(0.3); margin-top: 8px; }}
        </style>
    </head>
    <body>
        <div class="max-w-xl mx-auto p-3 bg-[#111] rounded-2xl border border-[#222] shadow-2xl">
            <video id="video-player" class="video-screen" controls autoplay muted loop src="{video_url}"></video>
            
            <div class="text-[9px] text-gray-500 mt-2 text-center tracking-widest uppercase">
                🎵 Visualizer: {current_song}
            </div>

            <canvas id="canvas" class="mini-visualizer w-full"></canvas>
            
            <audio id="audio" controls autoplay src="data:audio/mp3;base64,{audio_b64}"></audio>
        </div>

        <script>
            const audio = document.getElementById('audio');
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');
            let audioCtx, analyser, source, dataArray;

            audio.onplay = () => {{
                if (!audioCtx) {{
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    analyser = audioCtx.createAnalyser();
                    source = audioCtx.createMediaElementSource(audio);
                    source.connect(analyser);
                    analyser.connect(audioCtx.destination);
                    analyser.fftSize = 64; // ลดขนาดเพื่อให้แท่งกราฟดูใหญ่ในจอเล็ก
                    dataArray = new Uint8Array(analyser.frequencyBinCount);
                    render();
                }}
            }};

            audio.onended = () => {{
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'next_track'}}, '*');
            }};

            function render() {{
                requestAnimationFrame(render);
                analyser.getByteFrequencyData(dataArray);
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                let bw = (canvas.width / dataArray.length) * 2;
                for (let i = 0; i < dataArray.length; i++) {{
                    let h = (dataArray[i] / 255) * canvas.height * 0.8;
                    let hue = (i * 25 + Date.now()/100) % 360;
                    ctx.fillStyle = `hsla(${{hue}}, 70%, 60%, 0.8)`;
                    ctx.shadowBlur = 10;
                    ctx.shadowColor = `hsla(${{hue}}, 70%, 60%, 0.5)`;
                    // วาดกราฟจากกึ่งกลางขึ้นลงให้ดูฟุ้ง
                    ctx.fillRect(i * bw, (canvas.height/2) - (h/2), bw - 2, h);
                }}
            }}
        </script>
    </body>
    </html>
    """

    result = components.html(html_code, height=520)

    if result == "next_track":
        st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
        st.rerun()

    # ส่วนควบคุมเพลง
    col1, col2, col3 = st.columns(3)
    if col1.button("⏮️ ก่อนหน้า"):
        st.session_state.song_index = (st.session_state.song_index - 1) % len(music_files)
        st.rerun()
    if col2.button("🔄 เริ่มเพลงใหม่"):
        st.rerun()
    if col3.button("⏭️ ถัดไป"):
        st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
        st.rerun()

    with st.expander("📂 เลือกเพลงจากคลัง"):
        for i, f in enumerate(music_files):
            if st.button(f"🎼 {f}", key=f"s_{i}", use_container_width=True):
                st.session_state.song_index = i
                st.rerun()

st.markdown("<p style='text-align:center; color:#222; font-size:10px; margin-top:30px;'>⚡ SYNAPSE V9.0 | จอวิดีโอ & เครื่องเสียงมินิ ⚡</p>", unsafe_allow_html=True)
