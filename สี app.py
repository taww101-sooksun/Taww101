import streamlit as st
import base64
import os

# ==========================================
# 1. การตั้งค่าหน้าจอและ Logic ระบบสี
# ==========================================
st.set_page_config(page_title="Synapse Studio Mixer", layout="centered")

if 'bg_mode' not in st.session_state:
    st.session_state.bg_mode = "turquoise"

def set_bg(mode):
    st.session_state.bg_mode = mode

# กำหนดตัวแปรสีสำหรับใช้งาน
if st.session_state.bg_mode == "rainbow":
    current_style = """
        background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
        background-size: 1200% 1200%;
        animation: RainbowFlow 10s ease infinite;
    """
    theme_color = "#00FFFF" # ใช้สี Cyan สว่างๆ ในโหมดรุ้ง
elif st.session_state.bg_mode == "coral":
    current_style = "background-color: #FF7F50;"
    theme_color = "#FF7F50"
else:
    current_style = "background-color: #000000;"
    theme_color = "#AFEEEE"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    header, footer, #MainMenu {{visibility: hidden;}}
    
    @keyframes RainbowFlow {{
        0%{{background-position:0% 50%}}
        50%{{background-position:100% 50%}}
        100%{{background-position:0% 50%}}
    }}

    .stApp {{ {current_style} transition: all 0.5s ease; }}

    .header-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        padding-top: 20px;
    }}

    .logo-img {{
        width: 120px;
        filter: drop-shadow(0 0 10px {theme_color});
        margin-bottom: 10px;
    }}

    .neon-title {{
        font-family: 'Orbitron', sans-serif;
        color: #fff;
        text-shadow: 0 0 15px {theme_color};
        font-size: 1.8rem;
        letter-spacing: 5px;
        margin-top: 5px;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. ส่วนหัว (Logo & Title)
# ==========================================
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_url = f"data:image/png;base64,{get_base64_image('logo1.png')}"

st.markdown(f"""
    <div class="header-container">
        <img src="{logo_url}" class="logo-img">
        <h1 class="neon-title">SYNAPSE STUDIO</h1>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 3. HTML VISUALIZER & MIXER (ย้ายขึ้นมาใต้หัวข้อ)
# ==========================================
audio_files = [f for f in os.listdir('.') if f.endswith(('.mp3', '.wav', '.ogg'))]

col_sel_a, col_sel_b = st.columns(2)
with col_sel_a: track_a = st.selectbox("DECK A", audio_files if audio_files else ["No file"])
with col_sel_b: track_b = st.selectbox("DECK B", audio_files if audio_files else ["No file"])

def to_base64(file):
    try:
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

data_a = to_base64(track_a) if track_a in audio_files else ""
data_b = to_base64(track_b) if track_b in audio_files else ""

# ส่วนของเครื่องเล่นเพลงที่รวมกราฟและเวลานับถอยหลัง
html_mixer = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .vis-card {{ background: rgba(0,0,0,0.7); border: 2px solid {theme_color}; border-radius: 20px; padding: 15px; margin-top: 10px; }}
        .btn-ui {{ border: 1px solid {theme_color}; color: {theme_color}; width: 100%; padding: 8px; border-radius: 8px; font-weight: bold; font-size: 11px; }}
        .btn-ui:hover {{ background: {theme_color}; color: #000; }}
        .timer {{ font-family: 'Orbitron', monospace; color: {theme_color}; font-size: 14px; text-align: center; margin-bottom: 5px; }}
    </style>
</head>
<body class="bg-transparent text-white">
    <div class="vis-card">
        <div class="timer">
            <span id="labelA">A: READY</span> | <span id="labelB">B: READY</span>
        </div>
        
        <canvas id="canvas" style="height: 100px; width: 100%; background: #000; border-radius: 10px; margin-bottom: 15px;"></canvas>
        
        <div class="grid grid-cols-2 gap-4">
            <button onclick="play()" class="btn-ui">LOAD & START</button>
            <button onclick="fade()" class="btn-ui">CROSSFADE</button>
        </div>
    </div>

    <script>
        let ctx, ana, sA, sB, gA, gB, isP=false, cur='A';
        let durA = 0, durB = 0;

        async function play() {{
            if(!ctx) {{ ctx = new AudioContext(); ana = ctx.createAnalyser(); ana.fftSize = 256; draw(); }}
            if(isP) return;
            const dec = async (b) => ctx.decodeAudioData(Uint8Array.from(atob(b), c => c.charCodeAt(0)).buffer);
            
            const bA = await dec("{data_a}"); durA = bA.duration;
            sA = ctx.createBufferSource(); sA.buffer = bA;
            gA = ctx.createGain(); sA.connect(gA).connect(ana).connect(ctx.destination);
            
            const bB = await dec("{data_b}"); durB = bB.duration;
            sB = ctx.createBufferSource(); sB.buffer = bB;
            gB = ctx.createGain(); gB.gain.value = 0; sB.connect(gB).connect(ana).connect(ctx.destination);
            
            sA.start(0); sB.start(0); 
            isP = true;
            updateTimer();
        }}

        function fade() {{
            const n = ctx.currentTime;
            if(cur==='A') {{ gA.gain.linearRampToValueAtTime(0,n+3); gB.gain.linearRampToValueAtTime(1,n+3); cur='B'; }}
            else {{ gB.gain.linearRampToValueAtTime(0,n+3); gA.gain.linearRampToValueAtTime(1,n+3); cur='A'; }}
        }}

        function updateTimer() {{
            if(!isP) return;
            const now = ctx.currentTime;
            const remA = Math.max(0, durA - (now % durA));
            const remB = Math.max(0, durB - (now % durB));
            
            document.getElementById('labelA').innerText = "A: -" + fmt(remA);
            document.getElementById('labelB').innerText = "B: -" + fmt(remB);
            setTimeout(updateTimer, 500);
        }}

        function fmt(s) {{
            let m = Math.floor(s/60); let sec = Math.floor(s%60);
            return (m<10?'0':'')+m+":"+(sec<10?'0':'')+sec;
        }}

        function draw() {{
            requestAnimationFrame(draw);
            const can = document.getElementById('canvas'), c = can.getContext('2d');
            const f = new Uint8Array(ana.frequencyBinCount); ana.getByteFrequencyData(f);
            c.clearRect(0,0,can.width,can.height);
            
            const bw = (can.width / f.length) * 2;
            f.forEach((v, i) => {{
                // สีกราฟเปลี่ยนตามธีมที่เลือกมา
                c.fillStyle = '{theme_color}';
                c.fillRect(i*bw, can.height - v/2.5, bw-1, v/2.5);
            }});
        }}
    </script>
</body>
</html>
"""

st.components.v1.html(html_mixer, height=300)

# ==========================================
# 4. ปุ่มควบคุมสีด้านล่าง
# ==========================================
st.markdown("<p style='text-align:center; color:#fff; font-size:10px; margin-top:20px;'>SELECT THEME</p>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: st.button("💎 Turquoise", on_click=set_bg, args=("turquoise",), use_container_width=True)
with c2: st.button("🧡 Coral", on_click=set_bg, args=("coral",), use_container_width=True)
with c3: st.button("🌈 Rainbow", on_click=set_bg, args=("rainbow",), use_container_width=True)

st.markdown(f"<div style='text-align:center; color:{theme_color}; font-size:11px; margin-top:10px; opacity:0.6; font-family:Orbitron;'>อยู่นิ่งๆ ไม่เจ็บตัว</div>", unsafe_allow_html=True)
