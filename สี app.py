import streamlit as st
import streamlit.components.v1 as components
import os
import base64

# ==========================================
# ส่วนที่ 1: ระบบจัดการข้อมูลและ Session
# ==========================================

st.set_page_config(page_title="Synapse OnePage", layout="centered")

if 'song_index' not in st.session_state:
    st.session_state.song_index = 0

def get_base64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except: return ""
    return ""

logo_b64 = get_base64("logo1.png")
logo_data = f"data:image/png;base64,{logo_b64}" if logo_b64 else ""

# CSS: บีบทุกอย่างให้กระชับสำหรับมือถือ
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Prompt:wght@700&display=swap');
    header {{visibility: hidden;}} footer {{visibility: hidden;}}
    .stApp {{ background: #050505; color: white; overflow: hidden; }}
    
    /* จัดการโลโก้ให้เล็กลง */
    .logo-container {{ display: flex; justify-content: center; margin-top: -30px; }}
    .neon-logo {{
        width: 80px; height: 80px;
        background-image: url("{logo_data}");
        background-size: contain; background-repeat: no-repeat;
        filter: drop-shadow(0 0 8px #00f3ff);
        animation: pulse 2s infinite ease-in-out;
    }}
    @keyframes pulse {{
        0%, 100% {{ transform: scale(1); opacity: 0.8; }}
        50% {{ transform: scale(1.05); opacity: 1; filter: drop-shadow(0 0 15px #ff00de); }}
    }}

    /* ตัวหนังสือวิ่งแบบเนียนๆ */
    .marquee-box {{
        width: 100%; overflow: hidden; background: rgba(255,255,255,0.05);
        margin: 5px 0; border-y: 1px solid rgba(0,243,255,0.3);
    }}
    .marquee-text {{
        display: inline-block; white-space: nowrap; font-family: 'Prompt';
        font-size: 14px; color: #00f3ff; animation: scroll 15s linear infinite;
    }}
    @keyframes scroll {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    
    /* ปรับแต่ง Dropdown */
    .stSelectbox {{ margin-top: -10px; }}
    </style>
    
    <div class="logo-container"><div class="neon-logo"></div></div>
    <div class="marquee-box">
        <div class="marquee-text">อยู่นิ่งๆ ไม่เจ็บตัว ⚡ SYNAPSE AUTO-MIX ⚡ NO LIES JUST REAL CODE ⚡</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# ส่วนที่ 2: ระบบจัดการไฟล์
# ==========================================

# 1. จัดการวิดีโอ
uploaded_video = st.file_uploader("🎬 เลือกวิดีโอ", type=["mp4"], label_visibility="collapsed")
video_src = ""
if uploaded_video:
    v_b64 = base64.b64encode(uploaded_video.read()).decode()
    video_src = f"data:video/mp4;base64,{v_b64}"

# 2. จัดการเพลง
music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])

if music_files:
    # เลือกเพลงผ่าน Dropdown
    selected_song_name = st.selectbox(
        "🎵 เลือกเพลงจากคลัง (70+ เพลง)", 
        music_files, 
        index=st.session_state.song_index,
        key="song_selector"
    )
    
    # อัปเดต index เมื่อมีการเลือกใน Dropdown
    new_index = music_files.index(selected_song_name)
    if new_index != st.session_state.song_index:
        st.session_state.song_index = new_index
        st.rerun()

    current_song = music_files[st.session_state.song_index]
    with open(current_song, "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode()

    # ==========================================
    # ส่วนที่ 3: HTML Player (Video + Visualizer)
    # ==========================================
    
    html_player = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background: transparent; overflow: hidden; }}
            .main-container {{ background: #111; border: 1px solid #333; border-radius: 12px; padding: 8px; }}
            #v-screen {{ width: 100%; border-radius: 8px; background: #000; aspect-ratio: 16/9; object-fit: cover; }}
            #canvas {{ height: 50px; width: 100%; margin-top: 5px; }}
            audio {{ width: 100%; height: 30px; filter: invert(100%) opacity(0.3); margin-top: 5px; }}
        </style>
    </head>
    <body>
        <div class="main-container">
            <video id="v-screen" autoplay loop muted src="{video_src}"></video>
            <canvas id="canvas"></canvas>
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
                    let h = (dataArray[i] / 255) * canvas.height * 0.9;
                    let hue = (i * 25 + Date.now()/100) % 360;
                    ctx.fillStyle = `hsla(${{hue}}, 70%, 60%, 0.8)`;
                    ctx.fillRect(i * bw, canvas.height - h, bw - 2, h);
                }}
            }}
        </script>
    </body>
    </html>
    """

    # ส่วนรับค่าขากลับเมื่อเพลงจบ
    result = components.html(html_player, height=330)
    
    if result == "next":
        st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
        st.rerun()

    # ปุ่มคุมเพลงขนาดกะทัดรัด
    c1, c2, c3 = st.columns(3)
    if c1.button("⏮️", use_container_width=True):
        st.session_state.song_index = (st.session_state.song_index - 1) % len(music_files)
        st.rerun()
    if c2.button("🔄", use_container_width=True):
        st.rerun()
    if c3.button("⏭️", use_container_width=True):
        st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
        st.rerun()

else:
    st.info("วางไฟล์ .mp3 ไว้ในโฟลเดอร์เดียวกับโค้ดเพื่อเริ่มเล่นครับ")

st.markdown("<p style='text-align:center; color:#333; font-size:10px;'>⚡ SYNAPSE V11 | ONE-SCREEN MODE ⚡</p>", unsafe_allow_html=True)
