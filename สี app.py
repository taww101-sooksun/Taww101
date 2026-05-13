import streamlit as st
import streamlit.components.v1 as components
import os
import base64
import streamlit as st
import base64
import os

# --- 1. ตั้งค่าพื้นฐาน ---
st.set_page_config(page_title="Synapse Neon Mixer", layout="centered")

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

def get_audio_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return None

# สแกนหาเพลงในเครื่อง
all_songs = [f for f in os.listdir('.') if f.endswith('.mp3')]
all_songs = sorted(all_songs)
logo_b64 = get_base64_image("logo1.png")

# --- 2. สไตล์หน้าจอ (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #000; }
    .neon-text {
        font-family: 'Orbitron', sans-serif;
        color: #fff;
        text-align: center;
        font-size: 1.8rem;
        letter-spacing: 5px;
        text-shadow: 0 0 10px #ff00de, 0 0 20px #ff00de, 0 0 40px #00f3ff;
        animation: flicker 1.5s infinite alternate;
        margin-bottom: 20px;
    }
    @keyframes flicker {
        0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% { opacity: 1; text-shadow: 0 0 10px #ff00de, 0 0 20px #ff00de, 0 0 40px #00f3ff; }
        20%, 24%, 55% { opacity: 0.5; text-shadow: none; }
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="neon-text">SYNAPSE MIXER</div>', unsafe_allow_html=True)

# --- 3. ส่วนเลือกเพลง ---
if all_songs:
    col1, col2 = st.columns(2)
    with col1: sA = st.selectbox("DECK A (เริ่มก่อน)", all_songs, key="sA")
    with col2: sB = st.selectbox("DECK B (เล่นต่อ)", all_songs, key="sB")
    
    audio_a = get_audio_base64(sA)
    audio_b = get_audio_base64(sB)
else:
    st.error("ไม่พบไฟล์ .mp3 ในโฟลเดอร์")
    st.stop()

# --- 4. หัวใจสำคัญ: HTML/JS Mixer Engine ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: transparent; color: white; font-family: 'Orbitron', sans-serif; overflow: hidden; }}
        .neon-card {{ 
            border: 2px solid #333; 
            background: rgba(10,10,10,0.95); 
            box-shadow: 0 0 20px rgba(255,0,222,0.3);
            position: relative;
        }}
        .logo-box {{
            width: 60px; height: 60px;
            margin: 0 auto 15px auto;
            background: url('data:image/png;base64,{logo_b64}') no-repeat center;
            background-size: contain;
            filter: drop-shadow(0 0 8px #00f3ff);
        }}
        .visualizer {{ height: 100px; background: #000; border-radius: 10px; border: 1px solid #222; }}
        .deck {{ padding: 12px; border-radius: 10px; border: 1px solid #222; margin-top: 10px; transition: 0.3s; opacity: 0.5; }}
        .active-a {{ border-color: #ff00de; box-shadow: 0 0 10px #ff00de; opacity: 1; }}
        .active-b {{ border-color: #00f3ff; box-shadow: 0 0 10px #00f3ff; opacity: 1; }}
        .btn-mix {{
            background: linear-gradient(45deg, #ff00de, #00f3ff);
            width: 100%; padding: 15px; border-radius: 10px; font-weight: bold; margin-top: 15px; cursor: pointer;
        }}
        .progress {{ height: 4px; background: #222; margin-top: 5px; }}
        .bar {{ height: 100%; width: 0%; background: #ff00de; }}
    </style>
</head>
<body>
    <div class="max-w-md mx-auto p-6 neon-card rounded-3xl text-center">
        <div class="logo-box"></div>
        <canvas id="scope" class="visualizer w-full"></canvas>

        <div id="deckA" class="deck text-left">
            <div class="flex justify-between text-[10px]">
                <span style="color:#ff00de">DECK A</span>
                <span id="tA">00:00</span>
            </div>
            <div class="text-[11px] truncate">{sA}</div>
            <div class="progress"><div id="barA" class="bar"></div></div>
        </div>

        <div id="deckB" class="deck text-left">
            <div class="flex justify-between text-[10px]">
                <span style="color:#00f3ff">DECK B</span>
                <span id="tB">00:00</span>
            </div>
            <div class="text-[11px] truncate">{sB}</div>
            <div class="progress"><div id="barB" class="bar" style="background:#00f3ff"></div></div>
        </div>

        <button onclick="start()" class="btn-mix">🚀 START MIXING</button>
        <div id="status" class="text-[9px] mt-4 text-gray-500 uppercase">SYSTEM READY</div>
    </div>

    <script>
        let ctx, analyser, songA, songB, gA, gB, srcA, srcB;
        let isPlaying = false, active = 'A', data;

        async function toBuf(b64) {{
            const r = await fetch('data:audio/mp3;base64,' + b64);
            const ab = await r.arrayBuffer();
            return await ctx.decodeAudioData(ab);
        }}

        async function start() {{
            if(isPlaying) return;
            try {{
                document.getElementById('status').innerText = "BOOTING...";
                ctx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = ctx.createAnalyser();
                data = new Uint8Array(analyser.frequencyBinCount);

                songA = await toBuf('{audio_a}');
                songB = await toBuf('{audio_b}');

                playDeckA();
                
                isPlaying = true;
                render();
            }} catch(e) {{
                alert("Error: " + e);
            }}
        }}

        function playDeckA() {{
            active = 'A';
            srcA = ctx.createBufferSource();
            srcA.buffer = songA;
            gA = ctx.createGain();
            srcA.connect(gA).connect(analyser).connect(ctx.destination);
            srcA.start(0);
            srcA.t0 = ctx.currentTime; // เก็บเวลาที่เริ่มเล่น
            document.getElementById('deckA').classList.add('active-a');
            document.getElementById('status').innerText = "PLAYING DECK A";
        }}

        function playDeckB() {{
            active = 'B';
            srcB = ctx.createBufferSource();
            srcB.buffer = songB;
            gB = ctx.createGain();
            srcB.connect(gB).connect(analyser).connect(ctx.destination);
            gB.gain.value = 0; 
            srcB.start(0);
            srcB.t0 = ctx.currentTime;
            
            // ค่อยๆ เพิ่มเสียง B ใน 5 วินาที
            gB.gain.linearRampToValueAtTime(1, ctx.currentTime + 5);
            document.getElementById('deckB').classList.add('active-b');
            document.getElementById('deckA').classList.remove('active-a');
        }}

        function render() {{
            requestAnimationFrame(render);
            analyser.getByteFrequencyData(data);
            const can = document.getElementById('scope');
            const c = can.getContext('2d');
            c.clearRect(0,0,can.width,can.height);
            for(let i=0; i<data.length; i++) {{
                c.fillStyle = 'hsl(' + (i*2 + (active=='A'?300:190)) + ', 100%, 50%)';
                c.fillRect(i*3, can.height-(data[i]/2.5), 2, data[i]/2.5);
            }}
            updateProgress();
        }}

        function updateProgress() {{
            if (active == 'A' && srcA) {{
                let elapsed = ctx.currentTime - srcA.t0;
                let rem = songA.duration - elapsed;
                
                document.getElementById('tA').innerText = Math.floor(rem/60) + ":" + Math.floor(rem%60).toString().padStart(2,'0');
                document.getElementById('barA').style.width = (elapsed/songA.duration*100) + "%";

                // ถ้าเหลือ 8 วินาที ให้สั่งเล่น B และ Fade Out A
                if (rem < 8) {{
                    active = 'B'; 
                    gA.gain.linearRampToValueAtTime(0, ctx.currentTime + 5);
                    playDeckB();
                    document.getElementById('status').innerText = "CROSSFADING...";
                }}
            }} else if (active == 'B' && srcB) {{
                let elapsed = ctx.currentTime - srcB.t0;
                let rem = songB.duration - elapsed;
                document.getElementById('tB').innerText = Math.floor(rem/60) + ":" + Math.floor(rem%60).toString().padStart(2,'0');
                document.getElementById('barB').style.width = (elapsed/songB.duration*100) + "%";
                document.getElementById('status').innerText = "PLAYING DECK B";
            }}
        }}
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=600)
st.markdown("<div style='text-align:center; color:#444; font-size:10px;'>อยู่นิ่งๆ ไม่เจ็บตัว | MIXER V.2</div>", unsafe_allow_html=True)
# ฟังก์ชันช่วยแปลงไฟล์ (ต้องมีอยู่ในโค้ดหลักของคุณ)
def get_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

# สมมติค่าตัวแปรเบื้องต้น
primary_neon = "#00FFCC"

if "page" not in st.session_state:
    st.session_state.page = "1"

if st.session_state.page == "1":
    st.markdown("<h2 style='color:#00FFCC; font-family:monospace;'>🎧 SYNAPSE DJ STATION V.3</h2>", unsafe_allow_html=True)
    
    all_songs = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
    
    if not all_songs:
        st.warning("⚠️ ไม่พบไฟล์ .mp3 ในระบบ")
    else:
        col_sel_a, col_sel_b = st.columns(2)
        with col_sel_a:
            song_a = st.selectbox("💿 DECK A (LEFT)", ["-- Select --"] + all_songs, key="sa")
        with col_sel_b:
            song_b = st.selectbox("💿 DECK B (RIGHT)", ["-- Select --"] + all_songs, key="sb")

        data_a = get_base64(song_a) if song_a != "-- Select --" else ""
        data_b = get_base64(song_b) if song_b != "-- Select --" else ""

        mixer_html = f"""
        <div style="background: #000; border: 2px solid {primary_neon}; border-radius: 20px; padding: 15px; font-family: monospace; color: white;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div style="border: 1px solid {primary_neon}; padding: 10px; border-radius: 15px; text-align: center;">
                    <div style="display: flex; justify-content: space-between; font-size: 10px; color: {primary_neon};">
                        <span id="curA">00:00</span><span id="remA">-00:00</span>
                    </div>
                    <canvas id="canvasA" style="width: 100%; height: 60px; background: #111; margin: 5px 0; border-radius:5px;"></canvas>
                    <input type="range" id="volA" min="0" max="1" step="0.01" value="0.7" style="width: 100%;">
                    <div style="margin-top: 10px;">
                        <button onclick="control('A', 'play')" style="background:{primary_neon}; border:none; padding:5px 10px; border-radius:5px; cursor:pointer;">PLAY</button>
                        <button onclick="control('A', 'pause')" style="background:none; border:1px solid {primary_neon}; color:{primary_neon}; padding:5px 10px; border-radius:5px; cursor:pointer;">PAUSE</button>
                    </div>
                </div>

                <div style="border: 1px solid #FF44CC; padding: 10px; border-radius: 15px; text-align: center;">
                    <div style="display: flex; justify-content: space-between; font-size: 10px; color: #FF44CC;">
                        <span id="curB">00:00</span><span id="remB">-00:00</span>
                    </div>
                    <canvas id="canvasB" style="width: 100%; height: 60px; background: #111; margin: 5px 0; border-radius:5px;"></canvas>
                    <input type="range" id="volB" min="0" max="1" step="0.01" value="0.7" style="width: 100%;">
                    <div style="margin-top: 10px;">
                        <button onclick="control('B', 'play')" style="background:#FF44CC; border:none; padding:5px 10px; border-radius:5px; color:white; cursor:pointer;">PLAY</button>
                        <button onclick="control('B', 'pause')" style="background:none; border:1px solid #FF44CC; color:#FF44CC; padding:5px 10px; border-radius:5px; cursor:pointer;">PAUSE</button>
                    </div>
                </div>
            </div>

            <div style="margin-top:20px; text-align:center;">
                <small>CROSSFADER (A <-> B)</small><br>
                <input type="range" id="fader" min="0" max="1" step="0.01" value="0.5" style="width: 80%;">
            </div>

            <audio id="audioA" src="data:audio/mp3;base64,{data_a}"></audio>
            <audio id="audioB" src="data:audio/mp3;base64,{data_b}"></audio>

            <script>
                const audA = document.getElementById('audioA');
                const audB = document.getElementById('audioB');
                const fader = document.getElementById('fader');
                let audioCtx;
                let analyserA, analyserB;
                let sourceA, sourceB;

                function initAudio() {{
                    if (!audioCtx) {{
                        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                        
                        // Setup Deck A
                        analyserA = audioCtx.createAnalyser();
                        sourceA = audioCtx.createMediaElementSource(audA);
                        sourceA.connect(analyserA);
                        analyserA.connect(audioCtx.destination);
                        
                        // Setup Deck B
                        analyserB = audioCtx.createAnalyser();
                        sourceB = audioCtx.createMediaElementSource(audB);
                        sourceB.connect(analyserB);
                        analyserB.connect(audioCtx.destination);

                        startVisualizer('canvasA', analyserA, '{primary_neon}');
                        startVisualizer('canvasB', analyserB, '#FF44CC');
                    }}
                }}

                function startVisualizer(canvasID, analyser, color) {{
                    const canvas = document.getElementById(canvasID);
                    const ctx = canvas.getContext('2d');
                    analyser.fftSize = 64;
                    const bufferLength = analyser.frequencyBinCount;
                    const dataArray = new Uint8Array(bufferLength);

                    function draw() {{
                        requestAnimationFrame(draw);
                        analyser.getByteFrequencyData(dataArray);
                        ctx.clearRect(0, 0, canvas.width, canvas.height);
                        let barWidth = (canvas.width / bufferLength) * 2.5;
                        let x = 0;
                        for(let i = 0; i < bufferLength; i++) {{
                            let barHeight = dataArray[i] / 5;
                            ctx.fillStyle = color;
                            ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
                            x += barWidth + 1;
                        }}
                    }}
                    draw();
                }}

                function control(deck, action) {{
                    initAudio();
                    if (audioCtx.state === 'suspended') audioCtx.resume();
                    const target = (deck === 'A') ? audA : audB;
                    if (action === 'play') target.play();
                    else target.pause();
                }}

                // Volume & Fader Logic
                function updateVolumes() {{
                    const volA = document.getElementById('volA').value;
                    const volB = document.getElementById('volB').value;
                    const f = parseFloat(fader.value);
                    audA.volume = volA * (1 - f);
                    audB.volume = volB * f;
                }}

                fader.oninput = updateVolumes;
                document.getElementById('volA').oninput = updateVolumes;
                document.getElementById('volB').oninput = updateVolumes;

                // Time Update
                const updateUI = (aud, cur, rem) => {{
                    aud.ontimeupdate = () => {{
                        const fmt = s => new Date(s * 1000).toISOString().substr(14, 5);
                        document.getElementById(cur).innerText = fmt(aud.currentTime);
                        if(aud.duration) document.getElementById(rem).innerText = "-" + fmt(aud.duration - aud.currentTime);
                    }};
                }}
                updateUI(audA, 'curA', 'remA');
                updateUI(audB, 'curB', 'remB');
            </script>
        </div>
        """
        components.html(mixer_html, height=450)
        st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | Tactical Sound Module v4.2")
