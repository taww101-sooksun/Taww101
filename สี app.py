import streamlit as st
import streamlit.components.v1 as components
import os
import base64

# ==========================================
# ส่วนที่ 1: เตรียมระบบเบื้องต้น
# ==========================================

if 'song_index' not in st.session_state:
    st.session_state.song_index = 0

def get_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return ""

# ดึงโลโก้ (ไฟล์ logo1.png ต้องอยู่ในโฟลเดอร์เดียวกัน)
logo_b64 = get_base64("logo1.png")
logo_data = f"data:image/png;base64,{logo_b64}" if logo_b64 else ""

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Prompt:wght@700&display=swap');
    header {{visibility: hidden;}} footer {{visibility: hidden;}}
    .stApp {{ background: #050505; color: white; }}

    .logo-container {{ display: flex; justify-content: center; margin-top: 10px; }}
    .neon-logo {{
        width: 100px; height: 100px;
        background-image: url("{logo_data}");
        background-size: contain; background-repeat: no-repeat;
        filter: drop-shadow(0 0 12px #00f3ff);
        animation: pulse 2s infinite ease-in-out;
    }}
    @keyframes pulse {{
        0%, 100% {{ transform: scale(1); filter: drop-shadow(0 0 10px #00f3ff); }}
        50% {{ transform: scale(1.08); filter: drop-shadow(0 0 20px #ff00de); }}
    }}
    </style>
    <div class="logo-container"><div class="neon-logo"></div></div>
    """, unsafe_allow_html=True)

# ==========================================
# ส่วนที่ 2: ระบบเลือกไฟล์วิดีโอ
# ==========================================

st.write("### 🎬 VIDEO & MUSIC STATION")
uploaded_video = st.file_uploader("📂 เลือกไฟล์วิดีโอจากเครื่องของคุณ (.mp4)", type=["mp4"])

video_src = ""
if uploaded_video is not None:
    # อ่านข้อมูลวิดีโอและแปลงเป็น Base64 เพื่อส่งให้ HTML Video Tag
    v_data = uploaded_video.read()
    v_b64 = base64.b64encode(v_data).decode()
    video_src = f"data:video/mp4;base64,{v_b64}"
else:
    # ถ้ายังไม่เลือกไฟล์ ให้แสดงข้อความเตือน หรือใส่ Link วิดีโอเริ่มต้น
    st.info("กรุณาเลือกไฟล์วิดีโอก่อนครับ จอถึงจะแสดงผล")

# ==========================================
# ส่วนที่ 3: ระบบเพลงและตัวเล่น HTML
# ==========================================

music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])

if music_files:
    current_song = music_files[st.session_state.song_index]
    with open(current_song, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode()
    
    html_player = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background: transparent; font-family: 'Orbitron', sans-serif; overflow: hidden; }}
            .screen-box {{ background: #000; border: 2px solid #222; border-radius: 15px; overflow: hidden; position: relative; }}
            video {{ width: 100%; display: block; background: #000; }}
            .visualizer {{ height: 60px; background: rgba(0,0,0,0.9); width: 100%; }}
            audio {{ width: 100%; height: 35px; filter: invert(100%) opacity(0.4); }}
        </style>
    </head>
    <body>
        <div class="max-w-xl mx-auto p-2">
            <div class="screen-box">
                <video id="v-player" autoplay loop muted src="{video_src}"></video>
                
                <canvas id="canvas" class="visualizer"></canvas>
            </div>
            
            <div class="mt-2 text-center text-[10px] text-gray-500 uppercase tracking-tighter">
                Audio Engine: {current_song}
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
                    analyser.fftSize = 64;
                    dataArray = new Uint8Array(analyser.frequencyBinCount);
                    render();
                }}
            }};

            audio.onended = () => {{
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'next'}}, '*');
            }};

            function render() {{
                requestAnimationFrame(render);
                analyser.getByteFrequencyData(dataArray);
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                let bw = (canvas.width / dataArray.length) * 2;
                for (let i = 0; i < dataArray.length; i++) {{
                    let h = (dataArray[i] / 255) * canvas.height * 0.8;
                    let hue = (i * 20 + Date.now()/100) % 360;
                    ctx.fillStyle = `hsla(${{hue}}, 70%, 60%, 0.8)`;
                    ctx.shadowBlur = 10;
                    ctx.shadowColor = `hsla(${{hue}}, 70%, 60%, 0.4)`;
                    ctx.fillRect(i * bw, canvas.height - h, bw - 2, h);
                }}
            }}
        </script>
    </body>
    </html>
    """

    # ส่วนรับค่าขากลับเมื่อเพลงจบ
    result = components.html(html_player, height=480)
    if result == "next":
        st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
        st.rerun()

    # ปุ่มคุมเพลง
    col1, col2, col3 = st.columns(3)
    if col1.button("⏮️ BACK"):
        st.session_state.song_index = (st.session_state.song_index - 1) % len(music_files)
        st.rerun()
    if col2.button("🔄 RE"):
        st.rerun()
    if col3.button("⏭️ NEXT"):
        st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
        st.rerun()

st.markdown("<p style='text-align:center; color:#222; font-size:9px; margin-top:20px;'>STAY STILL & HEAL ⚡ SYNAPSE V10</p>", unsafe_allow_html=True)
