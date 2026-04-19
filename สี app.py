import streamlit as st
import base64
import os

# ==========================================
# 1. การตั้งค่าหน้าจอ (เปลี่ยนเป็น WIDE เพื่อให้โลโก้ใหญ่พอ) และระบบสี
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

# ฟังก์ชันโหลดโลโก้ขยับได้ (Glow)
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
    
    /* สไตล์โลโก้ขนาด 400px และขยับได้ */
    .logo-container {{
        display: flex;
        justify-content: center;
        margin-bottom: -50px; /* ลดระยะห่างด้านล่าง */
        position: relative;
    }}
    .logo-img {{
        width: 400px;
        animation: logoGlow 3s ease-in-out infinite;
    }}
    @keyframes logoGlow {{
        0% {{ filter: drop-shadow(0 0 10px {theme_color}); }}
        50% {{ filter: drop-shadow(0 0 30px {theme_color}); }}
        100% {{ filter: drop-shadow(0 0 10px {theme_color}); }}
    }}

    /* สไตล์ตัวหนังสือวิ่ง (Marquee) */
    .marquee-container {{
        width: 100%;
        overflow: hidden;
        background: transparent;
        color: #fff;
        font-family: 'Orbitron', sans-serif;
        font-size: 14px;
        letter-spacing: 2px;
        padding: 5px 0;
        border-top: 1px solid {theme_color};
        border-bottom: 1px solid {theme_color};
        margin-top: 15px;
    }}
    .marquee-text {{
        display: inline-block;
        padding-left: 100%;
        animation: marquee 25s linear infinite;
        white-space: nowrap;
    }}
    @keyframes marquee {{
        0% {{ transform: translate(0, 0); }}
        100% {{ transform: translate(-100%, 0); }}
    }}
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
# 4. เครื่องเล่นแยก Deck A และ Deck B (เหมือนเดิม)
# ==========================================
# (ส่วนนี้เหมือนกับโค้ดเดิม ไม่ต้องเปลี่ยน)
html_dual_deck = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .deck-box {{ background: rgba(0,0,0,0.8); border: 2px solid {theme_color}; border-radius: 15px; padding: 12px; }}
        .vis-canvas {{ height: 80px; width: 100%; background: #000; border-radius: 8px; margin-bottom: 10px; }}
        .btn {{ border: 1px solid {theme_color}; color: {theme_color}; font-size: 10px; padding: 5px; border-radius: 5px; width: 100%; font-weight: bold; }}
        .btn:hover {{ background: {theme_color}; color: #000; }}
        .timer {{ font-family: 'Orbitron', monospace; color: {theme_color}; font-size: 11px; text-align: center; margin-bottom: 5px; }}
        input[type=range] {{ width: 100%; accent-color: {theme_color}; }}
    </style>
</head>
<body class="bg-transparent text-white">
    <div class="grid grid-cols-2 gap-4">
        <div class="deck-box">
            <canvas id="canA" class="vis-canvas"></canvas>
            <div id="tmA" class="timer">-00:00</div>
            <div class="flex gap-2 mb-2">
                <button onclick="play('A')" class="btn">PLAY</button>
                <button onclick="stop('A')" class="btn">STOP</button>
            </div>
            <p class="text-[8px] mb-1">VOLUME</p>
            <input type="range" min="0" max="1" step="0.01" value="0.5" oninput="setVol('A', this.value)">
        </div>

        <div class="deck-box">
            <canvas id="canB" class="vis-canvas"></canvas>
            <div id="tmB" class="timer">-00:00</div>
            <div class="flex gap-2 mb-2">
                <button onclick="play('B')" class="btn">PLAY</button>
                <button onclick="stop('B')" class="btn">STOP</button>
            </div>
            <p class="text-[8px] mb-1">VOLUME</p>
            <input type="range" min="0" max="1" step="0.01" value="0.5" oninput="setVol('B', this.value)">
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
                anaA.fftSize = 128; anaB.fftSize = 128;
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
            const now = ctx.currentTime;
            if(id==='A' && sA) {{
                let r = Math.max(0, durA - (ctx.currentTime % durA));
                document.getElementById('tmA').innerText = "- " + fmt(r);
            }}
            if(id==='B' && sB) {{
                let r = Math.max(0, durB - (ctx.currentTime % durB));
                document.getElementById('tmB').innerText = "- " + fmt(r);
            }}
            setTimeout(() => updateT(id), 500);
        }}

        function fmt(s) {{
            let m = Math.floor(s/60); let sec = Math.floor(s%60);
            return (m<10?'0':'')+m+":"+(sec<10?'0':'')+sec;
        }}

        function draw() {{
            requestAnimationFrame(draw);
            const render = (canId, ana) => {{
                const can = document.getElementById(canId), c = can.getContext('2d');
                const f = new Uint8Array(ana.frequencyBinCount); ana.getByteFrequencyData(f);
                c.clearRect(0,0,can.width,can.height);
                const bw = (can.width / f.length) * 2;
                f.forEach((v, i) => {{
                    c.fillStyle = '{theme_color}';
                    c.fillRect(i*bw, can.height - v/3, bw-1, v/3);
                }});
            }};
            if(anaA) render('canA', anaA);
            if(anaB) render('canB', anaB);
        }}
    </script>
</body>
</html>
"""

st.components.v1.html(html_dual_deck, height=300)

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
# (ส่วนนี้เหมือนเดิม ลดระยะห่างลง)
st.markdown("<p style='text-align:center; color:#fff; font-size:10px; margin-top:5px; margin-bottom:5px;'>GLOBAL THEME</p>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: st.button("💎 Turquoise", on_click=set_bg, args=("turquoise",), use_container_width=True)
with c2: st.button("🧡 Coral", on_click=set_bg, args=("coral",), use_container_width=True)
with c3: st.button("🌈 Rainbow", on_click=set_bg, args=("rainbow",), use_container_width=True)
