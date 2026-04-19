import streamlit as st
import base64
import os

# ==========================================
# 1. ตั้งค่าหน้าจอและ Logic ระบบสี (พื้นหลัง/ธีม)
# ==========================================
st.set_page_config(page_title="Synapse Dual Station", layout="wide")

if 'bg_mode' not in st.session_state:
    st.session_state.bg_mode = "turquoise"

def set_bg(mode): st.session_state.bg_mode = mode

# กำหนดตัวแปรชุดสีตามที่คุณสั่ง
if st.session_state.bg_mode == "rainbow":
    # 5.4 สีรุ้งพื้นหลัง (ใช้ Animation RainbowFlow)
    bg_style = "background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff); background-size: 1200% 1200%; animation: RainbowFlow 10s ease infinite;"
    theme_c = "#00FFFF" # สีธีม
    text_c = "#FFFFFF"  # สีตัวหนังสือ
else:
    # 5.1 สีพื้นหลังดำ / 5.2 สีธีมตามเลือก
    bg_style = "background-color: #000000;"
    text_c = "#FFFFFF"
    theme_c = "#FF7F50" if st.session_state.bg_mode == "coral" else "#AFEEEE"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    header, footer, #MainMenu {{visibility: hidden;}}
    
    @keyframes RainbowFlow {{ 0%{{background-position:0% 50%}} 50%{{background-position:100% 50%}} 100%{{background-position:0% 50%}} }}
    @keyframes logoGlow {{ 0%{{filter:drop-shadow(0 0 5px {theme_c}); transform:scale(1);}} 50%{{filter:drop-shadow(0 0 20px {theme_c}); transform:scale(1.02);}} 100%{{filter:drop-shadow(0 0 5px {theme_c}); transform:scale(1);}} }}
    
    .stApp {{ {bg_style} transition: all 0.5s ease; color: {text_c}; }}

    /* 6. กรอบทุกส่วนหนา 4px */
    .custom-border {{
        border: 4px solid {theme_c};
        border-radius: 20px;
        padding: 15px;
        background: rgba(0,0,0,0.8);
        margin-bottom: 20px;
    }}

    /* 1. โโลโก้ดิ้นได้ 300px */
    .logo-box {{
        display: flex;
        justify-content: center;
        margin-top: 20px;
    }}
    .logo-img {{
        width: 300px;
        animation: logoGlow 2s ease-in-out infinite;
    }}

    /* 2. ตัวหนังสือวิ่งต่อจากโลโก้ */
    .marquee-box {{
        width: 100%;
        overflow: hidden;
        border-top: 4px solid {theme_c};
        border-bottom: 4px solid {theme_c};
        margin: 20px 0;
        padding: 10px 0;
        font-family: 'Orbitron', sans-serif;
    }}
    .marquee-text {{
        display: inline-block;
        white-space: nowrap;
        animation: marquee 20s linear infinite;
        font-size: 1.2rem;
        text-shadow: 0 0 10px {theme_c};
    }}
    @keyframes marquee {{ 0% {{transform: translate(100%, 0);}} 100% {{transform: translate(-100%, 0);}} }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. ฟังก์ชันช่วยโหลดไฟล์
# ==========================================
def to_base64(file_path):
    try:
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

logo_url = f"data:image/png;base64,{to_base64('logo1.png')}"
audio_files = [f for f in os.listdir('.') if f.endswith(('.mp3', '.wav', '.ogg'))]

# ==========================================
# 3. เรียงลำดับหน้าจอ (Layout)
# ==========================================

# (1) โลโก้ดิ้นได้
st.markdown(f'<div class="logo-box"><img src="{logo_url}" class="logo-img"></div>', unsafe_allow_html=True)

# (2) ตัวหนังสือวิ่ง
st.markdown(f'<div class="marquee-box"><div class="marquee-text">SYNAPSE DUAL STATION | LIVE EXPERIENCE | อยู่นิ่งๆ ไม่เจ็บตัว | SOUND & VISUAL THERAPY</div></div>', unsafe_allow_html=True)

# (3) กราฟเครื่องเล่น & เวลานับถอยหลัง & ปุ่มแยก A/B
# เตรียมข้อมูลเพลงก่อนส่งเข้า HTML
# (เราจะเลือกไฟล์เพลงจาก Dropdown ด้านล่าง แต่ต้องส่ง Data ไปให้ JS)
# เพื่อให้รันได้จริง ผมจะใช้ session_state เก็บไฟล์ที่เลือก

# (4) ปุ่มใส่รายการเพลง (ย้ายมาไว้ใต้เครื่องเล่น) - ส่วนของ Streamlit Selectbox
col_sel_a, col_sel_b = st.columns(2)
with col_sel_a:
    track_a = st.selectbox("💿 LIST DECK A", audio_files if audio_files else ["No file"])
    data_a = to_base64(track_a)
with col_sel_b:
    track_b = st.selectbox("💿 LIST DECK B", audio_files if audio_files else ["No file"])
    data_b = to_base64(track_b)

# (3) เครื่องเล่น (JS/HTML)
html_player = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .deck {{ border: 4px solid {theme_c}; border-radius: 15px; padding: 15px; background: rgba(0,0,0,0.9); }}
        .vis {{ height: 100px; width: 100%; background: #000; border-radius: 10px; border: 2px solid #222; margin-bottom: 10px; }}
        .btn {{ border: 2px solid {theme_c}; color: {theme_c}; padding: 8px; border-radius: 10px; width: 100%; font-weight: bold; font-family: 'Orbitron'; font-size: 12px; }}
        .btn:hover {{ background: {theme_c}; color: #000; }}
        .timer {{ font-family: 'Orbitron', monospace; color: {theme_c}; font-size: 16px; text-align: center; margin-bottom: 10px; text-shadow: 0 0 5px {theme_c}; }}
        input[type=range] {{ width: 100%; accent-color: {theme_c}; height: 8px; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="grid grid-cols-2 gap-6">
        <div class="deck">
            <canvas id="canA" class="vis"></canvas>
            <div id="tmA" class="timer">--:--</div>
            <div class="grid grid-cols-2 gap-2 mb-4">
                <button onclick="play('A')" class="btn">PLAY</button>
                <button onclick="stop('A')" class="btn">STOP</button>
            </div>
            <div class="text-[10px] text-center mb-1">VOLUME A</div>
            <input type="range" min="0" max="1" step="0.01" value="0.5" oninput="setV('A', this.value)">
        </div>

        <div class="deck">
            <canvas id="canB" class="vis"></canvas>
            <div id="tmB" class="timer">--:--</div>
            <div class="grid grid-cols-2 gap-2 mb-4">
                <button onclick="play('B')" class="btn">PLAY</button>
                <button onclick="stop('B')" class="btn">STOP</button>
            </div>
            <div class="text-[10px] text-center mb-1">VOLUME B</div>
            <input type="range" min="0" max="1" step="0.01" value="0.5" oninput="setV('B', this.value)">
        </div>
    </div>

    <script>
        let ctx, anaA, anaB, sA, sB, gA, gB;
        let dthA = "{data_a}", dthB = "{data_b}";
        let durA = 0, durB = 0;

        function init() {{
            if(!ctx) {{
                ctx = new (window.AudioContext || window.webkitAudioContext)();
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
        function setV(id, v) {{ if(id==='A') gA.gain.value = v; else gB.gain.value = v; }}

        function updateT(id) {{
            if(id==='A' && sA) {{
                let r = Math.max(0, durA - (ctx.currentTime % durA));
                document.getElementById('tmA').innerText = "-" + fmt(r);
            }}
            if(id==='B' && sB) {{
                let r = Math.max(0, durB - (ctx.currentTime % durB));
                document.getElementById('tmB').innerText = "-" + fmt(r);
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
                    c.fillStyle = '{theme_c}';
                    c.fillRect(i*bw, can.height - v/2.5, bw-2, v/2.5);
                }});
            }};
            if(anaA) render('canA', anaA);
            if(anaB) render('canB', anaB);
        }}
    </script>
</body>
</html>
"""
st.components.v1.html(html_player, height=320)

# (5) ชุดเลือกสี (Themes)
st.markdown("---")
st.markdown(f"<p style='text-align:center; color:{theme_c}; font-family:Orbitron;'>GLOBAL THEME CONTROL</p>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: st.button("💎 Turquoise", on_click=set_bg, args=("turquoise",), use_container_width=True)
with c2: st.button("🧡 Coral", on_click=set_bg, args=("coral",), use_container_width=True)
with c3: st.button("🌈 Rainbow Mode", on_click=set_bg, args=("rainbow",), use_container_width=True)

st.markdown(f"<div style='text-align:center; color:{theme_c}; font-size:12px; margin-top:15px; opacity:0.6; font-family:Orbitron;'>อยู่นิ่งๆ ไม่เจ็บตัว</div>", unsafe_allow_html=True)
