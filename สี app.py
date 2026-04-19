import streamlit as st
import base64
import os

# ==========================================
# 1. การตั้งค่าหน้าจอและระบบสี
# ==========================================
st.set_page_config(page_title="Synapse Dual Station", layout="wide")

if 'bg_mode' not in st.session_state:
    st.session_state.bg_mode = "turquoise"

def set_bg(mode): st.session_state.bg_mode = mode

if st.session_state.bg_mode == "rainbow":
    current_style = "background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff); background-size: 1200% 1200%; animation: RainbowFlow 10s ease infinite;"
    theme_color = "#00FFFF"
elif st.session_state.bg_mode == "coral":
    current_style = "background-color: #FF7F50;"
    theme_color = "#FF7F50"
else:
    current_style = "background-color: #000000;"
    theme_color = "#AFEEEE"

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_base64 = get_base64_image("logo1.png")
logo_url = f"data:image/png;base64,{logo_base64}"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    header, footer, #MainMenu {{visibility: hidden;}}
    @keyframes RainbowFlow {{ 0%{{background-position:0% 50%}} 50%{{background-position:100% 50%}} 100%{{background-position:0% 50%}} }}
    .stApp {{ {current_style} transition: all 0.5s ease; }}
    
    .logo-container {{ display: flex; justify-content: center; margin-bottom: -50px; position: relative; }}
    .logo-img {{ width: 400px; animation: logoGlow 3s ease-in-out infinite; }}
    @keyframes logoGlow {{ 0% {{ filter: drop-shadow(0 0 10px {theme_color}); }} 50% {{ filter: drop-shadow(0 0 30px {theme_color}); }} 100% {{ filter: drop-shadow(0 0 10px {theme_color}); }} }}

    .marquee-container {{ width: 100%; overflow: hidden; background: transparent; color: #fff; font-family: 'Orbitron', sans-serif; font-size: 14px; letter-spacing: 2px; padding: 5px 0; border-top: 1px solid {theme_color}; border-bottom: 1px solid {theme_color}; margin-top: 15px; margin-bottom: 5px; }}
    .marquee-text {{ display: inline-block; padding-left: 100%; animation: marquee 25s linear infinite; white-space: nowrap; }}
    @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
    
    /* สไตล์สำหรับ HTML Mixer และ Multi-band Visualizer */
    .mixer-container {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }}
    .deck-box {{ background: rgba(0,0,0,0.8); border: 2px solid {theme_color}; border-radius: 15px; padding: 12px; }}
    .vis-frame {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 10px; }}
    .vis-canvas {{ height: 80px; width: 100%; background: #000; border-radius: 8px; border: 1px solid {theme_color}55; }}
    .btn {{ border: 1px solid {theme_color}; color: {theme_color}; font-size: 10px; padding: 5px; border-radius: 5px; width: 100%; font-weight: bold; margin-bottom: 10px; }}
    .btn:hover {{ background: {theme_color}; color: #000; }}
    .timer {{ font-family: 'Orbitron', monospace; color: {theme_color}; font-size: 11px; text-align: center; margin-bottom: 5px; }}
    input[type=range] {{ width: 100%; accent-color: {theme_color}; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. ส่วนหัว (โลโก้ขนาด 400px ขยับได้)
# ==========================================
st.markdown(f'<div class="logo-container"><img src="{logo_url}" class="logo-img"></div>', unsafe_allow_html=True)

# ==========================================
# 3. เลือกเพลง
# ==========================================
audio_files = [f for f in os.listdir('.') if f.endswith(('.mp3', '.wav', '.ogg'))]

def to_base64(file):
    try:
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

col1, col2 = st.columns(2)
with col1:
    track_a = st.selectbox("SELECT DECK A", audio_files if audio_files else ["No file"])
    data_a = to_base64(track_a)
with col2:
    track_b = st.selectbox("SELECT DECK B", audio_files if audio_files else ["No file"])
    data_b = to_base64(track_b)

# ==========================================
# 4. เครื่องเล่นแยก Deck A และ Deck B พร้อม Multi-band Visualizer
# ==========================================
html_dual_deck = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .vis-canvas {{ height: 80px; width: 100%; background: #000; border-radius: 8px; margin-bottom: 10px; border: 1px solid {theme_color}55; }}
    </style>
</head>
<body class="bg-transparent text-white">
    <div class="mixer-container">
        <div class="deck-box">
            <div id="tmA" class="timer">-00:00</div>
            <div class="flex gap-2 mb-2">
                <button onclick="play('A')" class="btn">PLAY</button>
                <button onclick="stop('A')" class="btn">STOP</button>
            </div>
            <p class="text-[8px] mb-1">VOLUME</p>
            <input type="range" min="0" max="1" step="0.01" value="0.5" oninput="setVol('A', this.value)">
            <div class="vis-frame">
                <canvas id="canA_bar" class="vis-canvas"></canvas>
                <canvas id="canA_wave" class="vis-canvas"></canvas>
                <canvas id="canA_cir" class="vis-canvas"></canvas>
                <canvas id="canA_rad" class="vis-canvas"></canvas>
            </div>
        </div>

        <div class="deck-box">
            <div id="tmB" class="timer">-00:00</div>
            <div class="flex gap-2 mb-2">
                <button onclick="play('B')" class="btn">PLAY</button>
                <button onclick="stop('B')" class="btn">STOP</button>
            </div>
            <p class="text-[8px] mb-1">VOLUME</p>
            <input type="range" min="0" max="1" step="0.01" value="0.5" oninput="setVol('B', this.value)">
            <div class="vis-frame">
                <canvas id="canB_bar" class="vis-canvas"></canvas>
                <canvas id="canB_wave" class="vis-canvas"></canvas>
                <canvas id="canB_cir" class="vis-canvas"></canvas>
                <canvas id="canB_rad" class="vis-canvas"></canvas>
            </div>
        </div>
    </div>

    <script>
        let ctx, anaA, anaB, sA, sB, gA, gB;
        let dthA = "{data_a}", dthB = "{data_b}";
        let durA = 0, durB = 0;

        function init() {{
            if(!ctx) {{
                ctx = new AudioContext();
                anaA = ctx.createAnalyser(); anaB = ctx.createAnalyser();
                // เพิ่ม FFT Size เพื่อความละเอียดสูงสุด (256 frequency bins)
                anaA.fftSize = 512; anaB.fftSize = 512;
                gA = ctx.createGain(); gB = ctx.createGain();
                gA.connect(ctx.destination); gB.connect(ctx.destination);
                draw();
            }}
        }}

        async function play(id) {{
            init();
            const dec = async (b) => ctx.decodeAudioData(Uint8Array.from(atob(b), c => c.charCodeAt(0)).buffer);
            if(id === 'A') {{
                if(sA) sA.stop();
                const b = await dec(dthA); durA = b.duration;
                sA = ctx.createBufferSource(); sA.buffer = b;
                sA.connect(gA).connect(anaA); sA.start(0);
                updateT('A');
            }} else {{
                if(sB) sB.stop();
                const b = await dec(dthB); durB = b.duration;
                sB = ctx.createBufferSource(); sB.buffer = b;
                sB.connect(gB).connect(anaB); sB.start(0);
                updateT('B');
            }}
        }}

        function stop(id) {{ if(id==='A' && sA) sA.stop(); if(id==='B' && sB) sB.stop(); }}
        function setVol(id, v) {{ if(id==='A') gA.gain.value = v; else gB.gain.value = v; }}

        function updateT(id) {{
            if(id==='A' && sA) {{
                let r = Math.max(0, durA - (ctx.currentTime % durA));
                document.getElementById('tmA').innerText = "- " + fmt(r);
                setTimeout(() => updateT('A'), 500);
            }}
            if(id==='B' && sB) {{
                let r = Math.max(0, durB - (ctx.currentTime % durB));
                document.getElementById('tmB').innerText = "- " + fmt(r);
                setTimeout(() => updateT('B'), 500);
            }}
        }}

        function fmt(s) {{
            let m = Math.floor(s/60); let sec = Math.floor(s%60);
            return (m<10?'0':'')+m+":"+(sec<10?'0':'')+sec;
        }}

        function draw() {{
            requestAnimationFrame(draw);
            const render = (canId, ana) => {{
                const renderBar = (canIdBar, data) => {{
                    const can = document.getElementById(canIdBar), c = can.getContext('2d');
                    c.clearRect(0,0,can.width,can.height);
                    const bw = (can.width / data.length) * 2;
                    data.forEach((v, i) => {{
                        c.fillStyle = '{theme_color}';
                        c.fillRect(i*bw, can.height - v/3, bw-1, v/3);
                    }});
                }};
                const renderWave = (canIdWave, data) => {{
                    const can = document.getElementById(canIdWave), c = can.getContext('2d');
                    c.clearRect(0,0,can.width,can.height);
                    c.strokeStyle = '{theme_color}';
                    c.lineWidth = 1;
                    c.beginPath();
                    data.forEach((v, i) => {{
                        const x = i / data.length * can.width;
                        const y = can.height / 2 + (v / 128 - 1) * can.height / 2;
                        if(i === 0) c.moveTo(x,y); else c.lineTo(x,y);
                    }});
                    c.stroke();
                }};
                const renderCircle = (canIdCir, data) => {{
                    const can = document.getElementById(canIdCir), c = can.getContext('2d');
                    c.clearRect(0,0,can.width,can.height);
                    c.strokeStyle = '{theme_color}';
                    c.lineWidth = 1;
                    c.beginPath();
                    data.forEach((v, i) => {{
                        const r = data[i] / 2;
                        const a = i / data.length * 2 * Math.PI;
                        const x = can.width / 2 + r * Math.cos(a);
                        const y = can.height / 2 + r * Math.sin(a);
                        if(i === 0) c.moveTo(x,y); else c.lineTo(x,y);
                    }});
                    c.stroke();
                }};
                const renderRadial = (canIdRad, data) => {{
                    const can = document.getElementById(canIdRad), c = can.getContext('2d');
                    c.clearRect(0,0,can.width,can.height);
                    c.strokeStyle = '{theme_color}';
                    c.lineWidth = 1;
                    data.forEach((v, i) => {{
                        const a = i / data.length * 2 * Math.PI;
                        const r1 = can.height / 4;
                        const r2 = r1 + v / 2;
                        const x1 = can.width / 2 + r1 * Math.cos(a);
                        const y1 = can.height / 2 + r1 * Math.sin(a);
                        const x2 = can.width / 2 + r2 * Math.cos(a);
                        const y2 = can.height / 2 + r2 * Math.sin(a);
                        c.beginPath();
                        c.moveTo(x1, y1);
                        c.lineTo(x2, y2);
                        c.stroke();
                    }});
                }};

                const f = new Uint8Array(ana.frequencyBinCount); ana.getByteFrequencyData(f);
                const t = new Uint8Array(ana.fftSize); ana.getByteTimeDomainData(t);
                
                renderBar(canId+'_bar', f);
                renderWave(canId+'_wave', t);
                renderCircle(canId+'_cir', f);
                renderRadial(canId+'_rad', f);
            }};
            if(anaA) render('canA', anaA);
            if(anaB) render('canB', anaB);
        }}
    </script>
</body>
</html>
"""

st.components.v1.html(html_dual_deck, height=350)

# ==========================================
# 5. ตัวหนังสือวิ่ง (Marquee)
# ==========================================
st.markdown(f"""
    <div class="marquee-container">
        <div class="marquee-text">SYNAPSE DUAL STATION | LIVE NOW | เพลงของคุณ | โหมดของคุณ | อยู่นิ่งๆ ไม่เจ็บตัว</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 6. ปุ่มควบคุมธีม
# ==========================================
st.markdown("<p style='text-align:center; color:#fff; font-size:10px; margin-top:5px; margin-bottom:5px;'>GLOBAL THEME</p>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: st.button("💎 Turquoise", on_click=set_bg, args=("turquoise",), use_container_width=True)
with c2: st.button("🧡 Coral", on_click=set_bg, args=("coral",), use_container_width=True)
with c3: st.button("🌈 Rainbow", on_click=set_bg, args=("rainbow",), use_container_width=True)
