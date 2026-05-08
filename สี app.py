import streamlit as st
import streamlit.components.v1 as components
import os
import base64

# ==========================================
# ส่วนที่ 1: ระบบจัดการข้อมูลและ Session
# ==========================================

st.set_page_config(page_title="Synapse OnePage V12", layout="centered")

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

# ==========================================
# ส่วนที่ 2: UI & Multi-Tone Neon CSS
# ==========================================

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Prompt:wght@700&display=swap');
    header {{visibility: hidden;}} footer {{visibility: hidden;}}
    .stApp {{ background: #000; color: white; overflow: hidden; }}
    
    /* จัดการโลโก้ให้เล็กลงและเต้น */
    .logo-container {{ display: flex; justify-content: center; margin-top: -30px; }}
    .neon-logo {{
        width: 70px; height: 70px;
        background-image: url("{logo_data}");
        background-size: contain; background-repeat: no-repeat;
        filter: drop-shadow(0 0 10px #00f3ff);
        animation: pulseEffect 1s infinite ease-in-out;
    }}
    @keyframes pulseEffect {{
        0%, 100% {{ transform: scale(1); opacity: 0.7; filter: drop-shadow(0 0 10px #00f3ff); }}
        50% {{ transform: scale(1.1); opacity: 1; filter: drop-shadow(0 0 20px #ff00de); }}
    }}

    /* ตัวหนังสือวิ่งแบบเนียนๆ สลับสี */
    .marquee-box {{
        width: 100%; overflow: hidden; background: rgba(0,0,0,0.5);
        margin: 5px 0; 
        border-top: 1px solid #ff0000; border-bottom: 1px solid #00ff00;
        box-shadow: 0 0 10px rgba(0,255,0,0.3);
    }}
    .marquee-text {{
        display: inline-block; white-space: nowrap; font-family: 'Prompt';
        font-size: 13px; font-weight: 900; 
        color: #fff; text-shadow: 0 0 10px #ffffff;
        animation: scrollText 12s linear infinite, rainbow-text-marquee 4s infinite;
    }}
    @keyframes rainbow-text-marquee {{
        0% {{ text-shadow: 0 0 10px #ff0000; }}
        25% {{ text-shadow: 0 0 10px #00ff00; }}
        50% {{ text-shadow: 0 0 10px #0000ff; }}
        75% {{ text-shadow: 0 0 10px #ff00de; }}
        100% {{ text-shadow: 0 0 10px #ff0000; }}
    }}
    @keyframes scrollText {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    
    /* ปรับแต่ง Dropdown และปุ่มคุม */
    .stSelectbox, .stButton {{ margin-top: -10px; margin-bottom: 5px; }}
    .stButton>button {{ 
        border: 1px solid #ff00de; background: #111; color: #ff00de; font-weight: 900;
        box-shadow: 0 0 10px #ff00de; font-family: 'Orbitron';
    }}
    .stButton>button:hover {{ border: 1px solid #00f3ff; color: #00f3ff; box-shadow: 0 0 15px #00f3ff; }}
    </style>
    
    <div class="logo-container"><div class="neon-logo"></div></div>
    <div class="marquee-box">
        <div class="marquee-text">อยู่นิ่งๆ ไม่เจ็บตัว ⚡ DETECTED 70+ TRACKS ⚡ Real Chaos Player ⚡</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# ส่วนที่ 3: ระบบจัดการไฟล์
# ==========================================

# 1. จัดการวิดีโอ
uploaded_video = st.file_uploader("🎬 วิดีโอ", type=["mp4"], label_visibility="collapsed")
video_src = ""
if uploaded_video:
    v_b64 = base64.b64encode(uploaded_video.read()).decode()
    video_src = f"data:video/mp4;base64,{v_b64}"

# 2. จัดการเพลง
music_folder = "." # ปรับเป็นที่เก็บเพลงของคุณ
music_files = sorted([f for f in os.listdir(music_folder) if f.endswith(".mp3")])

if music_files:
    # เลือกเพลงผ่าน Dropdown
    selected_song_name = st.selectbox(
        "🎵 ลิสต์เพลง:", 
        music_files, 
        index=st.session_state.song_index,
        label_visibility="collapsed"
    )
    
    # อัปเดต index เมื่อมีการเลือก
    new_index = music_files.index(selected_song_name)
    if new_index != st.session_state.song_index:
        st.session_state.song_index = new_index
        st.rerun()

    current_song = music_files[st.session_state.song_index]
    with open(os.path.join(music_folder, current_song), "rb") as f:
        audio_b64 = base64.b64encode(f.read()).decode()

    # ==========================================
    # ส่วนที่ 4: HTML Player (Filled Video + Chaos Visualizer)
    # ==========================================
    
    html_player = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background: transparent; overflow: hidden; }}
            
            /* กล่องหลักแบบขอบนีออนสายรุ้ง (Border Gradient Animation) */
            .main-box {{ 
                background: #000; border: 3px solid; 
                border-image: linear-gradient(to right, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff, #ff0000) 1;
                border-radius: 12px; padding: 5px; 
                animation: rainbow-border 5s linear infinite;
            }}
            @keyframes rainbow-border {{
                0% {{ border-image-source: linear-gradient(0deg, #ff0000, #00ff00, #0000ff, #ff00de); }}
                100% {{ border-image-source: linear-gradient(360deg, #ff0000, #00ff00, #0000ff, #ff00de); }}
            }}
            
            /* จอวิดีโอแบบเต็ม */
            #v-screen {{ 
                width: 100%; border-radius: 8px; background: #000; 
                aspect-ratio: 16/16; 
                object-fit: fill; /* ปรับให้ภาพเต็มจอ */
                border: 4px solid #fff;
            }}
            
            /* จอเครื่องเสียงแบบละเอียด */
            #canvas {{ height: 40px; width: 100%; margin-top: 3px; border-radius: 4px; background: #050505; }}
            
            audio {{ width: 100%; height: 50px; filter: invert(100%) opacity(0.3); margin-top: 3px; }}
        </style>
    </head>
    <body>
        <div class="main-box">
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
                    // ปรับความละเอียดเป็น 256
                    analyser.fftSize = 256; 
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
                    
                    // ส่วนสีสลับ แดง เขียว น้ำเงิน ขาว ม่วง
                    let colors = ['#ff0000', '#00ff00', '#0000ff', '#ffffff', '#ff00de'];
                    let currentColor = colors[i % 5];
                    
                    ctx.fillStyle = currentColor;
                    // เพิ่มความฟุ้งแบบละเอียด
                    ctx.shadowBlur = dataArray[i]/10; 
                    ctx.shadowColor = currentColor;
                    
                    ctx.fillRect(i * bw, canvas.height - h, bw - 2, h);
                }}
            }}
        </script>
    </body>
    </html>
    """

    # ส่วนรับค่าขากลับเมื่อเพลงจบ
    result = components.html(html_player, height=310)
    
    if result == "next":
        st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
        st.rerun()

    # ปุ่มคุมเพลงขนาดกะทัดรัดแบบขอบนีออน
    st.write("---")
    c1, c2, c3 = st.columns(3)
    if c1.button("BACK", use_container_width=True):
        st.session_state.song_index = (st.session_state.song_index - 1) % len(music_files)
        st.rerun()
    if c2.button("RE", use_container_width=True):
        st.rerun()
    if c3.button("NEXT", use_container_width=True):
        st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
        st.rerun()

else:
    st.info("วางไฟล์ .mp3 ไว้ในโฟลเดอร์เดียวกับโค้ดเพื่อเริ่มเล่นครับ")

st.markdown("<p style='text-align:center; color:#111; font-size:9px;'>⚡ Real Chaos V12 | NO DULL MOMENTS ⚡</p>", unsafe_allow_html=True)
