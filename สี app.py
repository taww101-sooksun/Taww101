import streamlit as st
import streamlit.components.v1 as components
import os
import base64
import streamlit as st
import base64

# ==========================================
# ส่วนที่ 1: การตั้งค่าหน้าจอและ CSS (กู้คืนสีสัน Neon ขั้นสุด)
# ==========================================

st.set_page_config(page_title="Synapse Neon Mixer", layout="centered")

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_base64 = get_base64_image("logo1.png")
logo_html_link = f"data:image/png;base64,{logo_base64}" if logo_base64 else ""

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    .stApp {{ background-color: #000; }}

    /* Logo ตรงกลางพร้อมแสง Neon หมุนสลับสี */
    .block-container::before {{
        content: "";
        position: absolute;
        top: 10px; left: 50%;
        transform: translateX(-50%);
        width: 100px; height: 100px;
        background-image: url("{logo_html_link}");
        background-size: contain;
        background-repeat: no-repeat;
        z-index: 999;
        filter: drop-shadow(0 0 10px #ff00de);
        animation: logo-glow 4s infinite alternate;
    }}

    @keyframes logo-glow {{
        0% {{ filter: drop-shadow(0 0 10px #ff00de); transform: translateX(-50%) scale(1); }}
        50% {{ filter: drop-shadow(0 0 25px #00f3ff); transform: translateX(-50%) scale(1.1); }}
        100% {{ filter: drop-shadow(0 0 10px #ff8c00); transform: translateX(-50%) scale(1); }}
    }}

    .neon-title {{
        font-family: 'Orbitron', sans-serif;
        color: #fff;
        text-align: center;
        text-shadow: 0 0 10px #ff00de, 0 0 20px #00f3ff;
        font-size: 1.6rem;
        margin-top: 110px;
        letter-spacing: 3px;
        animation: text-flicker 2s infinite;
    }}
    @keyframes text-flicker {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.8; }}
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="neon-title">SYNAPSE NEON MIXER</h1>', unsafe_allow_html=True)

# ==========================================
# ส่วนที่ 2: HTML/JS - ระบบเล่นต่อเนื่อง + สีสันสะบัด
# ==========================================

html_code = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: transparent; color: white; overflow: hidden; font-family: 'Inter', sans-serif; }
        .neon-card { border: 2px solid #333; background: rgba(0,0,0,0.9); box-shadow: 0 0 30px rgba(255,0,222,0.2); }
        
        /* กราฟเสียงสีรุ้งสะบัด */
        .visualizer-box { height: 150px; background: #050505; border-radius: 15px; border: 1px solid #222; }
        
        .deck { padding: 15px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px; transition: 0.5s; }
        .deck-active { border: 1px solid #00f3ff; box-shadow: 0 0 15px #00f3ff; background: rgba(0,243,255,0.05); }
        
        /* ปุ่มสไตล์ Cyberpunk */
        .btn-mix { 
            background: linear-gradient(45deg, #ff00de, #00f3ff);
            color: white; font-weight: bold; padding: 12px; border-radius: 10px;
            text-transform: uppercase; letter-spacing: 2px; transition: 0.3s;
            box-shadow: 0 0 15px rgba(255,0,222,0.4);
        }
        .btn-mix:hover { transform: scale(1.05); box-shadow: 0 0 25px rgba(0,243,255,0.6); }
        
        .progress-bar { height: 6px; background: #222; border-radius: 10px; overflow: hidden; }
        .progress-inner { height: 100%; width: 0%; background: linear-gradient(90deg, #ff00de, #ff8c00); }
    </style>
</head>
<body>
    <div class="max-w-md mx-auto p-4 neon-card rounded-3xl">
        <canvas id="scope" class="visualizer-box w-full mb-4"></canvas>

        <div id="cardA" class="deck">
            <div class="flex justify-between text-[10px] mb-2">
                <span id="labelA" class="text-pink-500 font-bold">DECK A</span>
                <span id="timeA" class="font-mono">00:00</span>
            </div>
            <input type="file" id="inA" class="hidden" onchange="handleFile(this.files[0], 'A')">
            <button onclick="document.getElementById('inA').click()" class="text-[10px] border border-gray-600 px-3 py-1 rounded">LOAD A</button>
            <div id="nameA" class="text-[11px] mt-1 truncate text-gray-400">No Song</div>
            <div class="progress-bar mt-2"><div id="barA" class="progress-inner"></div></div>
        </div>

        <div id="cardB" class="deck">
            <div class="flex justify-between text-[10px] mb-2">
                <span id="labelB" class="text-cyan-400 font-bold">DECK B</span>
                <span id="timeB" class="font-mono">00:00</span>
            </div>
            <input type="file" id="inB" class="hidden" onchange="handleFile(this.files[0], 'B')">
            <button onclick="document.getElementById('inB').click()" class="text-[10px] border border-gray-600 px-3 py-1 rounded">LOAD B</button>
            <div id="nameB" class="text-[11px] mt-1 truncate text-gray-400">No Song</div>
            <div class="progress-bar mt-2"><div id="barB" class="progress-inner" style="background: #00f3ff;"></div></div>
        </div>

        <button onclick="startMix()" class="btn-mix w-full mt-2">🔥 START AUTO-MIX</button>
        <div id="status" class="text-[10px] text-center mt-3 text-gray-500 uppercase tracking-widest">System Ready</div>
    </div>

    <script>
        let ctx, analyser, songA, songB, gainA, gainB, sourceA, sourceB;
        let active = 'A', isPlaying = false, data;

        function init() {
            if (!ctx) {
                ctx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = ctx.createAnalyser();
                analyser.fftSize = 256;
                data = new Uint8Array(analyser.frequencyBinCount);
                render();
            }
        }

        async function handleFile(file, side) {
            init();
            document.getElementById('name'+side).innerText = "Loading...";
            const buffer = await ctx.decodeAudioData(await file.arrayBuffer());
            if(side === 'A') songA = buffer; else songB = buffer;
            document.getElementById('name'+side).innerText = file.name;
        }

        function render() {
            requestAnimationFrame(render);
            if(!analyser) return;
            analyser.getByteFrequencyData(data);
            const can = document.getElementById('scope');
            const c = can.getContext('2d');
            c.clearRect(0,0,can.width,can.height);
            
            let bw = (can.width / data.length) * 2.5;
            let x = 0;
            for(let i=0; i<data.length; i++) {
                let h = (data[i]/255) * can.height;
                let hue = (i * 3) + (Date.now() / 50) % 360;
                c.fillStyle = `hsl(${hue}, 100%, 50%)`;
                c.fillRect(x, can.height - h, bw - 1, h);
                x += bw;
            }
            updateEngine();
        }

        function startMix() {
            if(!songA || !songB) return alert("อาจารย์ครับ โหลดเพลงให้ครบ A/B ก่อน!");
            if(isPlaying) return;
            
            sourceA = ctx.createBufferSource(); sourceA.buffer = songA;
            gainA = ctx.createGain(); 
            sourceA.connect(gainA).connect(analyser).connect(ctx.destination);
            
            sourceB = ctx.createBufferSource(); sourceB.buffer = songB;
            gainB = ctx.createGain(); gainB.gain.value = 0;
            sourceB.connect(gainB).connect(analyser).connect(ctx.destination);
            
            sourceA.loop = true; sourceB.loop = true;
            sourceA.start(0); sourceB.start(0);
            isPlaying = true;
            document.getElementById('status').innerText = "Playing: Deck A";
            document.getElementById('cardA').classList.add('deck-active');
        }

        function updateEngine() {
            if(!isPlaying) return;
            let now = ctx.currentTime;
            
            // ระบบเช็กเวลาและ Auto-Crossfade เมื่อเพลงใกล้จบ (สมมติเล่น Loop)
            // ในที่นี้ใช้การอัปเดต Progress Bar และ UI
            updateUI('A', songA, gainA);
            updateUI('B', songB, gainB);
        }

        function updateUI(s, buffer, gain) {
            let bar = document.getElementById('bar'+s);
            let time = document.getElementById('time'+s);
            // จำลองการเดินของเวลาใน Loop
            let p = (ctx.currentTime % buffer.duration) / buffer.duration;
            bar.style.width = (p * 100) + "%";
            
            let rem = buffer.duration - (ctx.currentTime % buffer.duration);
            let m = Math.floor(rem/60), sec = Math.floor(rem%60);
            time.innerText = (m<10?'0':'')+m+":"+(sec<10?'0':'')+sec;

            // AUTO CROSSFADE LOGIC: เมื่อเหลือ 5 วินาทีสุดท้าย
            if(active === s && rem < 5) {
                crossfade();
            }
        }

        function crossfade() {
            let next = (active === 'A' ? 'B' : 'A');
            let now = ctx.currentTime;
            let dur = 4; // วินาทีในการ Fade
            
            if(active === 'A') {
                gainA.gain.linearRampToValueAtTime(0, now + dur);
                gainB.gain.linearRampToValueAtTime(1, now + dur);
                document.getElementById('cardA').classList.remove('deck-active');
                document.getElementById('cardB').classList.add('deck-active');
            } else {
                gainB.gain.linearRampToValueAtTime(0, now + dur);
                gainA.gain.linearRampToValueAtTime(1, now + dur);
                document.getElementById('cardB').classList.remove('deck-active');
                document.getElementById('cardA').classList.add('deck-active');
            }
            active = next;
            document.getElementById('status').innerText = "Auto-Mixing to: Deck " + active;
        }
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=650)

st.markdown("""
<div style='text-align: center; color: #555; font-size: 12px; font-family: "Orbitron"; letter-spacing: 2px;'>
    อยู่นิ่งๆ ไม่เจ็บตัว | AUTO-MIX ENGINE v5.0 | © 2026
</div>
""", unsafe_allow_html=True)

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
