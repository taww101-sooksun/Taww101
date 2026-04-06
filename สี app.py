import streamlit as st

# ใช้ตัวแปรเก็บโค้ด HTML ทั้งหมดที่คุณเขียนไว้
html_code = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; display: flex; flex-direction: column; height: 100vh; overflow: hidden; background: #000; }
        /* ใส่ CSS ของคุณต่อที่นี่ */
    </style>
</head>
<body>
    <h1 style="color: #0f0;">MATH-ELASTIC ENGINE READY</h1>
</body>
</html>
"""

# สั่งให้ Streamlit แสดงผล HTML
st.components.v1.html(html_code, height=800, scrolling=True)

<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SYNAPSE: Math-Elastic 144 Engine</title>
    <style>
        :root { --neon: #0f0; --bg: #050505; --dark: #111; }
        body { 
            background: var(--bg); color: var(--neon); 
            font-family: 'Segoe UI', 'Courier New', monospace; 
            margin: 0; display: flex; flex-direction: column; height: 100vh; overflow: hidden;
        }
        
        /* HEADER SECTION */
        header { 
            padding: 20px; border-bottom: 2px solid var(--neon); 
            background: linear-gradient(to bottom, #000, var(--bg));
            display: flex; justify-content: space-between; align-items: center;
        }
        .brand h1 { margin: 0; font-size: 1.5rem; letter-spacing: 3px; text-shadow: 0 0 10px var(--neon); }
        .brand p { margin: 5px 0 0; font-size: 0.7rem; color: #666; }

        /* VISUALIZER CANVAS */
        .viz-container { position: relative; height: 180px; background: #000; overflow: hidden; }
        canvas { width: 100%; height: 100%; }

        /* CONTROL PANEL */
        .panel { 
            display: flex; gap: 15px; padding: 15px; background: var(--dark); 
            border-bottom: 1px solid #222; justify-content: center; flex-wrap: wrap;
        }
        button, .file-label { 
            background: transparent; border: 1px solid var(--neon); color: var(--neon);
            padding: 10px 20px; cursor: pointer; font-size: 0.8rem; font-weight: bold;
            transition: all 0.3s; text-transform: uppercase;
        }
        button:hover, .file-label:hover { background: var(--neon); color: #000; box-shadow: 0 0 20px var(--neon); }
        button.active { background: #f00; border-color: #f00; color: #fff; animation: blink 1s infinite; }

        /* GRID 144 */
        .grid-scroll { flex: 1; overflow-y: auto; padding: 20px; background: radial-gradient(circle, #111 0%, #050505 100%); }
        .grid { 
            display: grid; grid-template-columns: repeat(12, 1fr); gap: 5px; 
            max-width: 1200px; margin: 0 auto;
        }
        .cell { 
            aspect-ratio: 1; background: rgba(0, 255, 0, 0.02); border: 1px solid #1a1a1a;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            font-size: 0.6rem; color: #333; transition: all 0.1s; border-radius: 2px;
        }
        .cell.active { 
            background: var(--neon); color: #000; border-color: #fff;
            box-shadow: 0 0 25px var(--neon); transform: scale(1.15); z-index: 5;
        }
        .cell.base { border-color: #fff; color: #fff; background: rgba(255,255,255,0.05); }

        /* STATUS OVERLAY */
        #status-bar { position: fixed; bottom: 0; width: 100%; background: #000; font-size: 0.7rem; padding: 5px 20px; border-top: 1px solid #222; color: #888; }

        @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    </style>
</head>
<body>

<header>
    <div class="brand">
        <h1>SYNAPSE MATH-ELASTIC</h1>
        <p>SLOGAN: อยู่นิ่งๆ ไม่เจ็บตัว | MODE: PITCH-SHIFT 144-ENGINE</p>
    </div>
    <div id="db-meter" style="font-family: monospace; font-size: 1.2rem;">-∞ dB</div>
</header>

<div class="viz-container">
    <canvas id="scope"></canvas>
</div>

<div class="panel">
    <button id="btnRec" onclick="toggleRecording()">1. อัดเสียง C4 (3 วินาที)</button>
    <label class="file-label">
        2. เลือกเพลง MP3
        <input type="file" id="audioFile" accept="audio/*" style="display:none">
    </label>
    <button onclick="powerOn()" style="background: rgba(0,255,0,0.1)">3. เดินเครื่องระบบ (START)</button>
    <button onclick="location.reload()" style="border-color:#444; color:#444;">RESET</button>
</div>

<div class="grid-scroll">
    <div class="grid" id="noteGrid"></div>
</div>

<div id="status-bar">SYSTEM READY // WAITING FOR INPUT...</div>

<script>
    const NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
    let audioCtx, masterGain, analyser, userBuffer, mp3Buffer, mp3Source;
    let isRunning = false;
    let lastNoteTime = 0;

    // 1. สร้างตาราง 144 (12 Octaves)
    const grid = document.getElementById('noteGrid');
    for(let i=0; i<144; i++) {
        const div = document.createElement('div');
        div.className = 'cell';
        if(i === 60) div.classList.add('base');
        div.id = `n-${i}`;
        div.innerHTML = `<span>${NOTES[i%12]}</span><span style="opacity:0.5">${Math.floor(i/12)}</span>`;
        grid.appendChild(div);
    }

    // 2. ระบบอัดเสียง
    async function toggleRecording() {
        if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const btn = document.getElementById('btnRec');
        const stream = await navigator.mediaDevices.getUserMedia({audio: true});
        const recorder = new MediaRecorder(stream);
        const chunks = [];
        
        recorder.ondataavailable = e => chunks.push(e.data);
        recorder.onstop = async () => {
            const blob = new Blob(chunks);
            userBuffer = await audioCtx.decodeAudioData(await blob.arrayBuffer());
            document.getElementById('status-bar').innerText = "✅ บันทึกตัวอย่างเสียงแล้ว | พร้อมคำนวณ";
        };
        
        recorder.start();
        btn.classList.add('active');
        btn.innerText = "กำลังรับคลื่นเสียง...";
        setTimeout(() => { recorder.stop(); btn.classList.remove('active'); btn.innerText = "อัดเสียงใหม่"; }, 3000);
    }

    // 3. โหลดเพลง
    document.getElementById('audioFile').onchange = async (e) => {
        if(!audioCtx) audioCtx = new AudioContext();
        const file = e.target.files[0];
        mp3Buffer = await audioCtx.decodeAudioData(await file.arrayBuffer());
        document.getElementById('status-bar').innerText = `🎵 โหลดเพลง: ${file.name} สำเร็จ`;
    };

    // 4. เริ่มระบบคำนวณ
    function powerOn() {
        if(!userBuffer || !mp3Buffer || isRunning) return;
        isRunning = true;
        
        // Setup Nodes
        mp3Source = audioCtx.createBufferSource();
        mp3Source.buffer = mp3Buffer;
        
        analyser = audioCtx.createAnalyser();
        analyser.fftSize = 2048;
        
        masterGain = audioCtx.createGain();
        
        mp3Source.connect(analyser);
        mp3Source.connect(audioCtx.destination);
        mp3Source.start();
        
        document.getElementById('status-bar').innerText = "🚀 ENGINE RUNNING: ANALYZING FREQUENCIES...";
        process();
    }

    // 5. THE ENGINE LOGIC
    function process() {
        if(!isRunning) return;
        
        const data = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(data);
        
        // วาด Scope
        drawVisualizer(data);

        // หาความถี่สูงสุด (Pitch Detection)
        let maxVal = 0;
        let maxIdx = 0;
        for(let i=0; i<data.length; i++) {
            if(data[i] > maxVal) { maxVal = data[i]; maxIdx = i; }
        }

        const now = audioCtx.currentTime;
        // ปรับ Threshold ความดังที่ 200 เพื่อให้จับเฉพาะโน้ตชัดๆ
        if(maxVal > 200 && now - lastNoteTime > 0.1) {
            const freq = maxIdx * (audioCtx.sampleRate / analyser.fftSize);
            // กรองช่วงเสียงมนุษย์ 100Hz - 1200Hz
            if(freq > 100 && freq < 1200) {
                const midi = Math.round(12 * Math.log2(freq / 440) + 69) + 12;
                if(midi >= 0 && midi < 144) {
                    playElasticNote(midi, maxVal / 255);
                    lastNoteTime = now;
                }
            }
        }
        
        requestAnimationFrame(process);
    }

    function playElasticNote(midi, velocity) {
        // UI Effect
        const cell = document.getElementById(`n-${midi}`);
        if(cell) {
            cell.classList.add('active');
            setTimeout(() => cell.classList.remove('active'), 150);
        }

        // Sound Engine
        const voice = audioCtx.createBufferSource();
        const vGain = audioCtx.createGain();
        voice.buffer = userBuffer;
        
        // MATH: n = 60 (C4)
        const playbackRate = Math.pow(2, (midi - 60) / 12);
        voice.playbackRate.value = playbackRate;

        // ADSR Envelope
        vGain.gain.setValueAtTime(0, audioCtx.currentTime);
        vGain.gain.linearRampToValueAtTime(velocity * 0.8, audioCtx.currentTime + 0.03);
        vGain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.4);

        voice.connect(vGain);
        vGain.connect(audioCtx.destination);
        voice.start();
    }

    function drawVisualizer(data) {
        const canvas = document.getElementById('scope');
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        const barWidth = canvas.width / data.length;
        for(let i=0; i<data.length; i++) {
            const h = (data[i] / 255) * canvas.height;
            ctx.fillStyle = `hsl(${120 + data[i]/2}, 100%, 50%)`;
            ctx.fillRect(i * barWidth, canvas.height - h, barWidth, h);
        }
        
        // Update DB Meter
        const avg = data.reduce((a, b) => a + b) / data.length;
        document.getElementById('db-meter').innerText = `${Math.round(avg)} UNIT`;
    }
</script>
</body>
</html>
