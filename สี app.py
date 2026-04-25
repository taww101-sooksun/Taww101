import streamlit as st
import os

# ตั้งค่าหน้าจอให้กว้างและซ่อนเมนู Streamlit ทั้งหมด
st.set_page_config(page_title="SYNAPSE", layout="wide")

# 1. ลบ Logo/Menu ของ Streamlit และใส่ CSS สำหรับ UI ทั้งหมด
st.markdown("""
    <style>
    /* ลบส่วนเกินของ Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0px;}

    /* พื้นหลังและธีมหลัก */
    body {
        background-color: var(--bg-color, #000);
        color: var(--text-color, #fff);
        font-family: 'Arial', sans-serif;
        overflow-x: hidden;
    }

    /* โครงสร้างส่วนบน (Logo & Slogan) */
    .header-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 30px;
        padding: 40px 0;
    }

    .slogan {
        font-size: 24px;
        font-weight: bold;
        text-shadow: 2px 2px 10px var(--neon-color, #ff00ea);
        max-width: 200px;
    }

    .main-logo {
        width: 200px;
        transition: transform 0.1s ease;
        filter: drop-shadow(0 0 15px var(--neon-color, #ff00ea));
    }

    /* กราฟเสียง Visualizer */
    #visualizer {
        width: 100%;
        height: 100px;
        background: transparent;
        display: block;
        margin: 20px 0;
    }

    /* ตัวหนังสือวิ่ง */
    .marquee-container {
        background: rgba(255,255,255,0.1);
        padding: 10px 0;
        margin-bottom: 30px;
    }

    /* เครื่องเล่นเพลงคู่ A-B */
    .dual-player {
        display: flex;
        justify-content: center;
        gap: 20px;
        padding: 20px;
    }

    .player-box {
        border: 2px solid var(--neon-color, #ff00ea);
        border-radius: 20px;
        padding: 20px;
        width: 350px;
        background: var(--card-bg, rgba(0,0,0,0.8));
        box-shadow: 0 0 20px var(--neon-color, #ff00ea);
        text-align: center;
    }

    .btn-neon {
        background: transparent;
        border: 1px solid var(--neon-color, #ff00ea);
        color: var(--neon-color, #ff00ea);
        padding: 10px 20px;
        margin: 5px;
        border-radius: 10px;
        cursor: pointer;
        transition: 0.3s;
    }

    .btn-neon:hover {
        background: var(--neon-color, #ff00ea);
        color: white;
    }

    /* แถบเลื่อนปรับแต่งสี */
    .color-panel {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(0,0,0,0.8);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #444;
    }
    </style>
""", unsafe_allow_html=True)

# 2. จัดเตรียมไฟล์เพลง (ดึงไฟล์ .mp3 จากหน้าเดียวกับ .py)
mp3_files = [f for f in os.listdir('.') if f.endswith('.mp3')]
if not mp3_files:
    st.error("ไม่พบไฟล์ .mp3 ในโฟลเดอร์เดียวกัน")
    st.stop()

# 3. HTML Structure & JavaScript (หัวใจหลักของ Visualizer และ Crossfade)
st.markdown(f"""
    <div class="header-container">
        <div class="slogan" style="text-align: right;">SYNAPSE</div>
        <img src="app/static/logo1.png" class="main-logo" id="logoImg" onerror="this.src='https://via.placeholder.com/200?text=Logo1.png'">
        <div class="slogan">อยู่นิ่งๆ<br>ไม่เจ็บตัว</div>
    </div>

    <canvas id="visualizer"></canvas>

    <div class="marquee-container">
        <marquee scrollamount="8" style="font-size: 20px;">
            🎧 กำลังเล่น: <span id="trackName">เตรียมความพร้อม...</span> | ยินดีต้อนรับสู่ SYNAPSE Command Center | อยู่นิ่งๆ ไม่เจ็บตัว 🎧
        </marquee>
    </div>

    <div class="dual-player">
        <div class="player-box" id="boxA">
            <h3>Player A</h3>
            <div id="timeA">00:00</div>
            <button class="btn-neon" onclick="playMusic('A')">PLAY</button>
            <input type="range" min="0" max="1" step="0.1" onchange="setVol('A', this.value)"> Vol
        </div>
        <div class="player-box" id="boxB">
            <h3>Player B</h3>
            <div id="timeB">00:00</div>
            <button class="btn-neon" onclick="playMusic('B')">PLAY</button>
            <input type="range" min="0" max="1" step="0.1" onchange="setVol('B', this.value)"> Vol
        </div>
    </div>

    <div class="color-panel">
        <label>ปรับสีธีม (Neon):</label><br>
        <input type="color" id="neonPicker" value="#ff00ea" oninput="updateColors()">
        <br><label>พื้นหลัง:</label><br>
        <input type="color" id="bgPicker" value="#000000" oninput="updateColors()">
    </div>

    <audio id="audioA" src="{mp3_files[0] if len(mp3_files) > 0 else ''}"></audio>
    <audio id="audioB" src="{mp3_files[1] if len(mp3_files) > 1 else mp3_files[0]}"></audio>

    <script>
    const audioA = document.getElementById('audioA');
    const audioB = document.getElementById('audioB');
    const logo = document.getElementById('logoImg');
    const canvas = document.getElementById('visualizer');
    const ctx = canvas.getContext('2d');

    let audioContext, analyser, source;

    function initAudio() {{
        if (!audioContext) {{
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioContext.createAnalyser();
            // เชื่อมต่อ Visualizer (ดึงจากตัวที่เล่นอยู่)
            source = audioContext.createMediaElementSource(audioA);
            source.connect(analyser);
            analyser.connect(audioContext.destination);
            analyser.fftSize = 64;
            draw();
        }}
    }}

    function draw() {{
        requestAnimationFrame(draw);
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        analyser.getByteFrequencyData(dataArray);

        // โลโก้เต้นตามเบส
        const base = dataArray[2]; // ความถี่ต่ำ (Bass)
        const scale = 1 + (base / 500);
        logo.style.transform = `scale(${{scale}})`;

        // วาดกราฟสี่เหลี่ยมผืนผ้า
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const barWidth = (canvas.width / bufferLength) * 2.5;
        let x = 0;
        for(let i = 0; i < bufferLength; i++) {{
            const barHeight = dataArray[i] / 2;
            ctx.fillStyle = document.getElementById('neonPicker').value;
            ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
            x += barWidth + 1;
        }}
    }}

    function playMusic(p) {{
        initAudio();
        const active = p === 'A' ? audioA : audioB;
        active.play();
        document.getElementById('trackName').innerText = active.src.split('/').pop();
    }}

    function setVol(p, v) {{
        const target = p === 'A' ? audioA : audioB;
        target.volume = v;
    }}

    function updateColors() {{
        const neon = document.getElementById('neonPicker').value;
        const bg = document.getElementById('bgPicker').value;
        document.documentElement.style.setProperty('--neon-color', neon);
        document.documentElement.style.setProperty('--bg-color', bg);
    }}

    // ระบบ Crossfade อัตโนมัติ 10 วินาที
    setInterval(() => {{
        if (audioA.duration - audioA.currentTime < 10 && !audioA.paused && audioB.paused) {{
            fade(audioA, audioB);
        }}
    }}, 1000);

    function fade(out, inv) {{
        inv.volume = 0;
        inv.play();
        let vol = 1;
        const interval = setInterval(() => {{
            if (vol > 0.1) {{
                vol -= 0.1;
                out.volume = vol;
                inv.volume = 1 - vol;
            }} else {{
                out.pause();
                clearInterval(interval);
            }}
        }}, 1000);
    }}
    </script>
""", unsafe_allow_html=True)

# 4. สำหรับสโลแกนใน Streamlit sidebar (ถ้าอยากใช้เพิ่ม)
# st.sidebar.write("SYNAPSE Command")
