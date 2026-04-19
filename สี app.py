import streamlit as st
import base64
import os

# ==========================================
# 1. การตั้งค่าหน้าจอและระบบธีมสี
# ==========================================
st.set_page_config(page_title="Synapse Studio Mixer", layout="centered")

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#AFEEEE" # สี Pale Turquoise ที่ขอมา

with st.sidebar:
    st.markdown("### 🎨 SYNAPSE CUSTOMIZER")
    st.session_state.theme_color = st.color_picker("ปรับสีนีออนระบบ", st.session_state.theme_color)
    st.write(f"สีปัจจุบัน: {st.session_state.theme_color}")
    st.markdown("---")
    st.info('สโลแกน: "อยู่นิ่งๆ ไม่เจ็บตัว"')

theme_c = st.session_state.theme_color

# ==========================================
# 2. ฟังก์ชันสแกนหาไฟล์เพลงในโฟลเดอร์หลัก
# ==========================================
# สแกนไฟล์ที่มีนามสกุล .mp3, .wav, .ogg ในโฟลเดอร์เดียวกับไฟล์ .py
audio_extensions = ('.mp3', '.wav', '.ogg', '.m4a')
music_files = [f for f in os.listdir('.') if f.endswith(audio_extensions)]

# ==========================================
# 3. จัดการ Logo และ CSS (จัดสมดุลไม่ให้ทับตัวหนังสือ)
# ==========================================
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_base64 = get_base64_image("logo1.png")
logo_url = f"data:image/png;base64,{logo_base64}" if logo_base64 else ""

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    header, footer, #MainMenu {{visibility: hidden;}}
    
    .main {{ 
        background: #000;
        background: linear-gradient(270deg, #000, #111, #000);
        background-size: 400% 400%;
    }}

    /* จัดระเบียบส่วนหัวให้สมดุล */
    .header-box {{
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 30px 0 20px 0;
    }}

    .logo-frame {{
        width: 110px;
        height: 110px;
        margin-bottom: 20px;
        filter: drop-shadow(0 0 10px {theme_c});
        animation: glow 2s infinite alternate;
    }}

    @keyframes glow {{
        from {{ filter: drop-shadow(0 0 5px {theme_c}); transform: scale(1); }}
        to {{ filter: drop-shadow(0 0 20px {theme_c}); transform: scale(1.05); }}
    }}

    .neon-text {{
        font-family: 'Orbitron', sans-serif;
        color: #fff;
        text-shadow: 0 0 10px {theme_c}, 0 0 20px {theme_c};
        font-size: 1.6rem;
        letter-spacing: 4px;
        text-align: center;
    }}
    </style>

    <div class="header-box">
        <img src="{logo_url}" class="logo-frame">
        <div class="neon-text">SYNAPSE STUDIO</div>
        <div style="color:{theme_c}; font-size:11px; margin-top:8px; opacity:0.8;">อยู่นิ่งๆ ไม่เจ็บตัว</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. ส่วนเลือกเพลง (ดึงจากไฟล์ในเครื่อง/GitHub)
# ==========================================
st.markdown(f"<div style='color:{theme_c}; font-size:12px; margin-bottom:10px;'>🎵 เลือกเพลงสำหรับ DECK A และ B:</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    track_a = st.selectbox("เลือกเพลง DECK A", music_files if music_files else ["ไม่มีไฟล์เพลงในโฟลเดอร์"])
with col2:
    track_b = st.selectbox("เลือกเพลง DECK B", music_files if music_files else ["ไม่มีไฟล์เพลงในโฟลเดอร์"])

# แปลงเพลงเป็น Base64 เพื่อส่งเข้า HTML Mixer
def get_audio_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return ""

audio_a_data = get_audio_base64(track_a) if track_a in music_files else ""
audio_b_data = get_audio_base64(track_b) if track_b in music_files else ""

# ==========================================
# 5. เครื่องเล่นเพลงและ Visualizer
# ==========================================
html_mixer = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: transparent; color: white; }}
        .mixer-card {{
            border: 1px solid {theme_c}55;
            background: rgba(10,10,10,0.9);
            box-shadow: 0 0 25px {theme_c}22;
            border-radius: 20px;
            padding: 20px;
        }}
        .visual-box {{
            height: 120px; background: #000; border-radius: 12px;
            border: 1px solid {theme_c}33; margin-bottom: 20px;
        }}
        .btn-action {{
            border: 2px solid {theme_c};
            color: {theme_c};
            padding: 12px; border-radius: 15px; width: 100%;
            font-weight: bold; transition: 0.3s;
            text-shadow: 0 0 5px {theme_c};
            background: transparent;
        }}
        .btn-action:hover {{ background: {theme_c}; color: #000; }}
        .progress-bar {{ height: 4px; background: #222; border-radius: 2px; overflow: hidden; margin-top: 8px; }}
        .progress-fill {{ height: 100%; width: 0%; background: {theme_c}; box-shadow: 0 0 10px {theme_c}; }}
    </style>
</head>
<body>
    <div class="mixer-card">
        <canvas id="canvas" class="visual-box w-full"></canvas>
        
        <div class="grid grid-cols-2 gap-4 mb-6">
            <div>
                <div class="flex justify-between text-[9px]" style="color:{theme_c}">
                    <span>DECK A: {track_a}</span>
                    <span id="tA">00:00</span>
                </div>
                <div class="progress-bar"><div id="bA" class="progress-fill"></div></div>
            </div>
            <div>
                <div class="flex justify-between text-[9px]" style="color:{theme_c}">
                    <span>DECK B: {track_b}</span>
                    <span id="tB">00:00</span>
                </div>
                <div class="progress-bar"><div id="bB" class="progress-fill"></div></div>
            </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
            <button onclick="startMix()" class="btn-action">LOAD & PLAY</button>
            <button onclick="fade()" class="btn-action">CROSSFADE</button>
        </div>
    </div>

    <script>
        let ctx, analyser, sA, sB, gA, gB, isPlaying=false, cur='A';
        const rawA = "{audio_a_data}";
        const rawB = "{audio_b_data}";

        async function decode(base64) {{
            const buffer = Uint8Array.from(atob(base64), c => c.charCodeAt(0)).buffer;
            return await ctx.decodeAudioData(buffer);
        }}

        async function startMix() {{
            if(!ctx) {{
                ctx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = ctx.createAnalyser();
                analyser.fftSize = 128;
                draw();
            }}
            if(isPlaying) return;
            
            const dataA = await decode(rawA);
            const dataB = await decode(rawB);

            sA = ctx.createBufferSource(); sA.buffer = dataA;
            gA = ctx.createGain(); sA.connect(gA).connect(analyser).connect(ctx.destination);
            
            sB = ctx.createBufferSource(); sB.buffer = dataB;
            gB = ctx.createGain(); gB.gain.value = 0;
            sB.connect(gB).connect(analyser).connect(ctx.destination);

            sA.start(0); sB.start(0);
            isPlaying = true;
        }}

        function fade() {{
            const now = ctx.currentTime;
            if(cur==='A') {{
                gA.gain.linearRampToValueAtTime(0, now+4);
                gB.gain.linearRampToValueAtTime(1, now+4);
                cur='B';
            }} else {{
                gB.gain.linearRampToValueAtTime(0, now+4);
                gA.gain.linearRampToValueAtTime(1, now+4);
                cur='A';
            }}
        }}

        function draw() {{
            requestAnimationFrame(draw);
            const can = document.getElementById('canvas');
            const c = can.getContext('2d');
            const freq = new Uint8Array(analyser.frequencyBinCount);
            analyser.getByteFrequencyData(freq);

            c.fillStyle = 'rgba(0,0,0,0.2)';
            c.fillRect(0,0,can.width,can.height);
            
            const bw = (can.width / freq.length) * 2.5;
            freq.forEach((v, i) => {{
                c.fillStyle = '{theme_c}';
                c.fillRect(i*bw, can.height - v/2, bw-1, v/2);
            }});
        }}
    </script>
</body>
</html>
"""

st.components.v1.html(html_mixer, height=480)

# Footer
st.markdown(f"<div style='text-align:center; color:{theme_c}; font-size:10px; margin-top:20px; opacity:0.4; font-family:Orbitron;'>COMMAND CENTER V2 | 2026</div>", unsafe_allow_html=True)
