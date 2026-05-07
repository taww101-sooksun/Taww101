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

# CSS: โลโก้เต้นและ UI นีออนนวล
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Prompt:wght@700&display=swap');
    header {{visibility: hidden;}} footer {{visibility: hidden;}}
    .stApp {{ background: #050505; color: white; }}

    .logo-container {{ display: flex; justify-content: center; margin-top: 20px; }}
    .neon-logo {{
        width: 100px; height: 100px;
        background-image: url("{logo_html_link}");
        background-size: contain; background-repeat: no-repeat;
        filter: drop-shadow(0 0 10px #00f3ff);
        animation: pulse 2s infinite ease-in-out;
    }}
    @keyframes pulse {{
        0%, 100% {{ transform: scale(1); filter: drop-shadow(0 0 10px #00f3ff); }}
        50% {{ transform: scale(1.08); filter: drop-shadow(0 0 20px #ff00de); }}
    }}

    .neon-title {{
        font-family: 'Orbitron', sans-serif; text-align: center;
        font-size: 1.5rem; letter-spacing: 5px; margin: 15px 0;
        color: #fff; text-shadow: 0 0 8px #00f3ff;
    }}
    </style>
    <div class="logo-container"><div class="neon-logo"></div></div>
    <h1 class="neon-title">SYNAPSE</h1>
    """, unsafe_allow_html=True)

# ==========================================
# ส่วนที่ 2: Logic การดึงเพลง
# ==========================================

music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])

if not music_files:
    st.warning("⚠️ ไม่พบไฟล์ .mp3 ในเครื่องเพื่อนเลย วางไว้โฟลเดอร์เดียวกับโค้ดนะ")
else:
    current_song = music_files[st.session_state.song_index]
    
    # แปลงเพลงเป็น Base64
    with open(current_song, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode()
    
    # HTML Visualizer + Audio Logic
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background: transparent; font-family: 'Orbitron', sans-serif; overflow: hidden; }}
            .visualizer {{ height: 200px; background: #000; border: 1px solid #222; border-radius: 10px; }}
            audio {{ width: 100%; filter: invert(100%) opacity(0.5); margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="max-w-md mx-auto p-4 bg-[#0000ff] rounded-xl border border-[#ff0000]">
            <canvas id="canvas" class="visualizer w-full"></canvas>
            <div class="text-[10px] text-cyan-400 mt-3 text-center truncate tracking-widest uppercase">
                Now Playing: {current_song}
            </div>
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
                    analyser.fftSize = 256;
                    dataArray = new Uint8Array(analyser.frequencyBinCount);
                    render();
                }}
            }};

            // เมื่อเพลงจบ ส่งค่ากลับไปหา Streamlit เพื่อกด 'Next' อัตโนมัติ
            audio.onended = () => {{
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'next_track'}}, '*');
            }};

            function render() {{
                requestAnimationFrame(render);
                analyser.getByteFrequencyData(dataArray);
                ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                let bw = (canvas.width / dataArray.length) * 2;
                for (let i = 0; i < dataArray.length; i++) {{
                    let h = (dataArray[i] / 255) * canvas.height * 0.7;
                    let hue = (i * 15 + Date.now()/80) % 360;
                    ctx.fillStyle = `hsla(${{hue}}, 60%, 55%, 0.7)`;
                    ctx.shadowBlur = dataArray[i]/20;
                    ctx.shadowColor = `hsla(${{hue}}, 60%, 55%, 0.4)`;
                    ctx.fillRect(i * bw, canvas.height - h, bw - 3, h);
                }}
            }}
        </script>
    </body>
    </html>
    """

    # ใช้ Custom Component เพื่อรับค่าขากลับ (Event 'next_track')
    result = components.html(html_code, height=350)

    # เช็คว่าเพลงจบหรือยังจาก JS ขากลับ
    if result == "next_track":
        st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
        st.rerun()

    # ปุ่มควบคุม
    col1, col2, col3 = st.columns(3)
    if col1.button("⏮️ ก่อนหน้า"):
        st.session_state.song_index = (st.session_state.song_index - 1) % len(music_files)
        st.rerun()
    if col2.button("🔄 เริ่มใหม่"):
        st.rerun()
    if col3.button("⏭️ ถัดไป"):
        st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
        st.rerun()

    # รายชื่อเพลง
    st.write("---")
    with st.expander(f"📂 รายชื่อเพลงทั้งหมด ({len(music_files)} เพลง)"):
        for i, f in enumerate(music_files):
            if st.button(f"🎼 {f}", key=f"s_{i}", use_container_width=True):
                st.session_state.song_index = i
                st.rerun()

st.markdown("<p style='text-align:center; color:#222; font-size:10px; margin-top:50px;'>⚡ SYNAPSE V8.0 | อยู่นิ่งๆ ไม่เจ็บตัว ⚡</p>", unsafe_allow_html=True)
