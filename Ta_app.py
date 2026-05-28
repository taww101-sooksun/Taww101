import streamlit as st
import base64

# ==========================================
# ส่วนที่ 1: การตั้งค่าหน้าจอและ CSS (Cyberpunk Neon)
# ==========================================

st.set_page_config(page_title="Synapse Neon Single Deck", layout="centered")

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
        width: 50px; height: 50px;
        background-image: url("{logo_html_link}");
        background-size: contain;
        background-repeat: no-repeat;
        z-index: 999;
        filter: drop-shadow(0 0 10px #ff00de);
        animation: logo-glow 4s infinite alternate;
    }}

    @keyframes logo-glow {{
        0% {{ filter: drop-shadow(0 0 10px #ff00de); transform: translateX(-50%) scale(1); }}
        50% {{ filter: drop-shadow(0 0 20px #00f3ff); transform: translateX(-50%) scale(1.1); }}
        100% {{ filter: drop-shadow(0 0 10px #ff8c00); transform: translateX(-50%) scale(1); }}
    }}

    .neon-title {{
        font-family: 'Orbitron', sans-serif;
        color: #fff;
        text-align: center;
        text-shadow: 0 0 10px #ff00de, 0 0 20px #00f3ff;
        font-size: 1.6rem;
        margin-top: 50px;
        letter-spacing: 6px;
        animation: text-flicker 2s infinite;
    }}
    @keyframes text-flicker {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.8; }}
    }}

    /* สโลแกนแสงนีออนวิ้งๆ วิ่งสลับสี */
    .neon-slogan {{
        text-align: center; 
        color: #fff; 
        font-size: 5px; 
        font-family: "Orbitron", sans-serif; 
        letter-spacing: 8px;
        margin-top:100px;
        text-shadow: 0 0 5px #ff00de, 0 0 10px #ff00de, 0 0 20px #00f3ff;
        animation: slogan-wink 1s infinite alternate;
    }}

    @keyframes slogan-wink {{
        0%, 100% {{ text-shadow: 0 0 5px #ff00de, 0 0 10px #ff00de, 0 0 20px #ff00de; color: #fff; }}
        50% {{ text-shadow: 0 0 8px #00f3ff, 0 0 15px #00f3ff, 0 0 25px #00f3ff; color: #e0ffff; }}
        82% {{ text-shadow: none; color: #555; }} /* มีจังหวะไฟกะพริบดับนิดๆ แบบหลอดไฟนีออนจริง */
        85% {{ text-shadow: 0 0 8px #00f3ff; color: #fff; }}
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="neon-title">SYNAPSE</h1>', unsafe_allow_html=True)

# ==========================================
# ส่วนที่ 2: HTML/JS - ระบบปลดล็อกเสียงอัตโนมัติเมื่อกดปุ่ม
# ==========================================

html_code = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: transparent; color: white; overflow: hidden; font-family: 'Inter', sans-serif; }
        .neon-card { border: 4px solid #333; background: rgba(0,0,0,0.9); box-shadow: 0 0 30px rgba(255,0,222,0.2); }
        
        .visualizer-box { height: 20px; background: #050505; border-radius: 15px; border: 1px solid #222; }
        
        .deck { padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); background: rgba(255,255,255,0.02); }
        .deck-active { border: 1px solid #00f3ff; box-shadow: 0 0 15px #00f3ff; }
        
        .btn-main { 
            background: linear-gradient(45deg, #ff00de, #00f3ff);
            color: white; font-weight: bold; padding: 12px; border-radius: 10px;
            text-transform: uppercase; letter-spacing: 2px; transition: 0.1s;
            box-shadow: 0 0 15px rgba(255,0,222,0.4);
        }
        .btn-main:hover { transform: scale(1.02); box-shadow: 0 0 25px rgba(0,243,255,0.6); }
        
        .btn-fx {
            background: #111; border: 1px solid #ff00de; color: #ff00de;
            padding: 8px; border-radius: 8px; font-size: 11px; font-weight: bold;
            transition: 0.2s; text-transform: uppercase;
        }
        .btn-fx:hover { background: #ff00de; color: #000; box-shadow: 0 0 10px #ff00de; }
        .btn-fx:active { transform: scale(0.95); }

        .progress-bar { height: 6px; background: #222; border-radius: 10px; overflow: hidden; }
        .progress-inner { height: 100%; width: 0%; background: linear-gradient(90deg, #ff00de, #00f3ff); }
    </style>
</head>
<body>
    <div class="max-w-md mx-auto p-4 neon-card rounded-3xl">
        <canvas id="scope" class="visualizer-box w-full mb-4"></canvas>

        <div id="mainDeck" class="deck mb-4">
            <div class="flex justify-between text-[11px] mb-2">
                <span class="text-cyan-400 font-bold tracking-widest">NOW PLAYING</span>
                <span id="timeLabel" class="font-mono text-gray-400">00:00 / 00:00</span>
            </div>
            
            <input type="file" id="audioFile" class="hidden" accept="audio/*" onchange="handleFile(this.files[0])">
            <div class="flex gap-2 items-center mb-2">
                <button onclick="document.getElementById('audioFile').click()" class="text-[10px] border border-cyan-500 text-cyan-400 px-3 py-1.5 rounded hover:bg-cyan-950 transition">LOAD TRACK</button>
                <div id="fileName" class="text-[12px] truncate text-gray-400 flex-1">No Song Loaded</div>
            </div>
            
            <div class="progress-bar mt-3"><div id="progressBar" class="progress-inner"></div></div>
        </div>

        <button id="playBtn" onclick="togglePlay()" class="btn-main w-full mb-4">▶ PLAY TRACK</button>

        <div class="border border-gray-600 p-3 rounded-xl bg-black/40">
            <div class="text-[10px] text-gray-500 font-bold tracking-wider mb-2 text-center uppercase">LIVE SOUND EFFECTS PANEL</div>
            <div class="grid grid-cols-2 gap-2">
                <button onclick="playFX('airhorn')" class="btn-fx">📣 AIRHORN</button>
                <button onclick="playFX('laser')" class="btn-fx" style="border-color:#00f3ff; color:#00f3ff;">🚀 LASER BEAM</button>
                <button onclick="playFX('scratch')" class="btn-fx" style="border-color:#ff8c00; color:#ff8c00;">💿 VINYL SCRATCH</button>
                <button onclick="playFX('explosion')" class="btn-fx" style="border-color:#9d4edd; color:#9d4edd;">💥 EXPLOSION</button>
            </div>
        </div>

        <div id="status" class="text-[10px] text-center mt-3 text-gray-800 uppercase tracking-widest">System Ready</div>
    </div>

    <script>
        let ctx, analyser, songBuffer, sourceNode, gainNode;
        let isPlaying = false;
        let startTime = 0;
        let pausedAt = 0;
        let dataArray;

        // ฟังก์ชันบังคับปลดล็อก AudioContext เพื่อสู้กับระบบเบราว์เซอร์
        async function ensureAudioContext() {
            if (!ctx) {
                ctx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = ctx.createAnalyser();
                analyser.fftSize = 256;
                dataArray = new Uint8Array(analyser.frequencyBinCount);
                
                gainNode = ctx.createGain();
                gainNode.connect(analyser).connect(ctx.destination);
                
                renderVisualizer();
            }
            if (ctx.state === 'suspended') {
                await ctx.resume();
            }
        }

        async function handleFile(file) {
            if (!file) return;
            await ensureAudioContext();
            
            if (isPlaying) {
                stopTrack();
            }

            document.getElementById('fileName').innerText = "Decoding Audio...";
            try {
                const arrayBuffer = await file.arrayBuffer();
                songBuffer = await ctx.decodeAudioData(arrayBuffer);
                document.getElementById('fileName').innerText = file.name;
                document.getElementById('status').innerText = "Track Loaded Successfully";
                pausedAt = 0;
                updateUI(0);
            } catch (e) {
                document.getElementById('fileName').innerText = "Error loading file";
                alert("ไฟล์นี้ถอดรหัสไม่ได้ครับอาจารย์ ลองใช้ไฟล์ .mp3 หรือ .wav มาตรฐานดูครับ");
            }
        }

        async function togglePlay() {
            await ensureAudioContext();
            if (!songBuffer) return alert("อาจารย์ครับ รบกวนโหลดเพลงก่อนกดเล่นครับ!");

            if (isPlaying) {
                pausedAt = ctx.currentTime - startTime;
                stopTrack();
                document.getElementById('playBtn').innerText = "▶ RESUME TRACK";
                document.getElementById('status').innerText = "Paused";
                document.getElementById('mainDeck').classList.remove('deck-active');
            } else {
                sourceNode = ctx.createBufferSource();
                sourceNode.buffer = songBuffer;
                sourceNode.connect(gainNode);
                
                if (pausedAt >= songBuffer.duration) pausedAt = 0;
                
                sourceNode.start(0, pausedAt);
                startTime = ctx.currentTime - pausedAt;
                isPlaying = true;
                
                document.getElementById('playBtn').innerText = "⏸ PAUSE TRACK";
                document.getElementById('status').innerText = "Playing";
                document.getElementById('mainDeck').classList.add('deck-active');
                
                sourceNode.onended = () => {
                    if (isPlaying && (ctx.currentTime - startTime) >= songBuffer.duration - 0.1) {
                        isPlaying = false;
                        pausedAt = 0;
                        document.getElementById('playBtn').innerText = "▶ PLAY TRACK";
                        document.getElementById('status').innerText = "Finished";
                        document.getElementById('mainDeck').classList.remove('deck-active');
                    }
                };
            }
        }

        function stopTrack() {
            if (sourceNode) {
                try { sourceNode.stop(); } catch(e) {}
                sourceNode.disconnect();
            }
            isPlaying = false;
        }

        function updateUI(currentSeconds) {
            if (!songBuffer) return;
            let dur = songBuffer.duration;
            let p = currentSeconds / dur;
            if (p > 1) p = 1;
            
            document.getElementById('progressBar').style.width = (p * 100) + "%";
            
            let curM = Math.floor(currentSeconds/60), curS = Math.floor(currentSeconds%60);
            let durM = Math.floor(dur/60), durS = Math.floor(dur%60);
            
            document.getElementById('timeLabel').innerText = 
                (curM<10?'0':'')+curM+":"+(curS<10?'0':'')+curS + " / " +
                (durM<10?'0':'')+durM+":"+(durS<10?'0':'')+durS;
        }

        function renderVisualizer() {
            requestAnimationFrame(renderVisualizer);
            if(!analyser) return;
            
            analyser.getByteFrequencyData(dataArray);
            const canvas = document.getElementById('scope');
            const canvasCtx = canvas.getContext('2d');
            canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
            
            let barWidth = (canvas.width / dataArray.length) * 2;
            let x = 0;
            for(let i=0; i<dataArray.length; i++) {
                let barHeight = (dataArray[i]/255) * canvas.height;
                let hue = (i * 5) + (Date.now() / 40) % 360;
                canvasCtx.fillStyle = `hsl(${hue}, 100%, 50%)`;
                canvasCtx.fillRect(x, canvas.height - barHeight, barWidth - 1.5, barHeight);
                x += barWidth;
            }

            if(isPlaying) {
                updateUI(ctx.currentTime - startTime);
            }
        }

        async function playFX(type) {
            await ensureAudioContext();
            const now = ctx.currentTime;
            
            const osc = ctx.createOscillator();
            const fxGain = ctx.createGain();
            osc.connect(fxGain).connect(analyser).connect(ctx.destination);

            if (type === 'airhorn') {
                osc.type = 'sawtooth'; osc.frequency.setValueAtTime(220, now);
                fxGain.gain.setValueAtTime(0.3, now); fxGain.gain.linearRampToValueAtTime(0, now + 0.8);
                osc.start(now); osc.stop(now + 0.8);

                const osc2 = ctx.createOscillator(); const osc3 = ctx.createOscillator();
                const fxGain2 = ctx.createGain(); const fxGain3 = ctx.createGain();
                osc2.type = 'sawtooth'; osc2.frequency.setValueAtTime(293.66, now);
                osc3.type = 'sawtooth'; osc3.frequency.setValueAtTime(349.23, now);
                osc2.connect(fxGain2).connect(analyser).connect(ctx.destination);
                osc3.connect(fxGain3).connect(analyser).connect(ctx.destination);
                fxGain2.gain.setValueAtTime(0.2, now); fxGain2.gain.linearRampToValueAtTime(0, now + 0.8);
                fxGain3.gain.setValueAtTime(0.2, now); fxGain3.gain.linearRampToValueAtTime(0, now + 0.8);
                osc2.start(now); osc2.stop(now + 0.8); osc3.start(now); osc3.stop(now + 0.8);
            } 
            else if (type === 'laser') {
                osc.type = 'sawtooth'; osc.frequency.setValueAtTime(1500, now);
                osc.frequency.exponentialRampToValueAtTime(40, now + 0.4);
                fxGain.gain.setValueAtTime(0.4, now); fxGain.gain.linearRampToValueAtTime(0, now + 0.4);
                osc.start(now); osc.stop(now + 0.4);
            } 
            else if (type === 'scratch') {
                osc.type = 'triangle'; osc.frequency.setValueAtTime(80, now);
                osc.frequency.linearRampToValueAtTime(400, now + 0.15); osc.frequency.linearRampToValueAtTime(100, now + 0.3);
                fxGain.gain.setValueAtTime(0.5, now); fxGain.gain.linearRampToValueAtTime(0, now + 0.3);
                osc.start(now); osc.stop(now + 0.3);
            } 
            else if (type === 'explosion') {
                osc.type = 'square'; osc.frequency.setValueAtTime(100, now);
                osc.frequency.linearRampToValueAtTime(10, now + 0.7);
                fxGain.gain.setValueAtTime(0.6, now); fxGain.gain.exponentialRampToValueAtTime(0.01, now + 0.8);
                osc.start(now); osc.stop(now + 0.8);
            }
        }
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=600)

# แสดงสโลแกนวิ้งๆ นีออนแบบเก๋ๆ ปิดท้ายไฟล์อย่างสมบูรณ์แบบ
st.markdown('<div class="neon-slogan">อยู่นิ่งๆ ไม่เจ็บตัว | CONSOLE v6.2</div>', unsafe_allow_html=True)
