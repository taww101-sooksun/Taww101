import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="SYNAPSE: X-CHORDS ENGINE")

# --- กลไกคณิตศาสตร์ดนตรีแบบ "เต็มสูบ" ---
html_code = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <style>
        :root { --neon: #0f0; --dim: #053305; --bg: #020202; }
        body { 
            background: var(--bg); color: var(--neon); font-family: 'Courier New', monospace;
            margin: 0; display: flex; flex-direction: column; height: 100vh; overflow: hidden;
        }
        
        /* สถาปัตยกรรมหน้าจอ */
        header { padding: 15px; border-bottom: 2px solid var(--neon); display: flex; justify-content: space-between; }
        .main-engine { display: flex; flex: 1; overflow: hidden; gap: 10px; padding: 10px; }
        
        /* ฝั่งซ้าย: กระดาน 144 (Melody) */
        .melody-zone { flex: 2; overflow-y: auto; background: #000; border: 1px solid var(--dim); padding: 10px; }
        .grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 3px; }
        .cell { 
            aspect-ratio: 1; border: 1px solid #111; font-size: 0.6rem; 
            display: flex; align-items: center; justify-content: center; color: #222;
            transition: 0.1s; border-radius: 3px;
        }
        .cell.active { background: var(--neon); color: #000; box-shadow: 0 0 15px var(--neon); transform: scale(1.1); z-index: 5; }

        /* ฝั่งขวา: แผงควบคุมคอร์ด (Chord Engine) */
        .chord-zone { flex: 1; background: #050505; border-left: 1px solid var(--neon); padding: 15px; }
        .chord-btn { 
            width: 100%; padding: 15px; margin-bottom: 10px; border: 1px solid var(--dim); 
            background: #000; color: var(--neon); text-align: left; cursor: pointer;
        }
        .chord-btn.active { border-color: #fff; background: var(--dim); box-shadow: inset 0 0 10px var(--neon); }

        /* ระบบบันทึก (LOG) */
        #status-bar { height: 30px; background: #111; font-size: 0.7rem; padding: 5px 20px; border-top: 1px solid var(--dim); }
        
        /* ปุ่มควบคุม */
        .controls { padding: 15px; background: #000; border-top: 1px solid var(--neon); display: flex; gap: 10px; }
        button { background: none; border: 1px solid var(--neon); color: var(--neon); padding: 8px 15px; cursor: pointer; font-weight: bold; }
        button:hover { background: var(--neon); color: #000; }
        button.rec { border-color: #f00; color: #f00; }
    </style>
</head>
<body>

<header>
    <div><strong>SYNAPSE X-ENGINE</strong> | "อยู่นิ่งๆ ไม่เจ็บตัว"</div>
    <div id="freq-val">DETECTING...</div>
</header>

<div class="main-engine">
    <div class="melody-zone">
        <div style="font-size: 0.7rem; color: #444; margin-bottom: 10px;">MELODY MATRIX (144 SLOTS)</div>
        <div class="grid" id="noteGrid"></div>
    </div>
    
    <div class="chord-zone">
        <div style="font-size: 0.7rem; color: #444; margin-bottom: 10px;">HARMONY ANALYZER (CHORDS)</div>
        <div id="chord-display">
            </div>
        <canvas id="wave-scope" style="width:100%; height:100px; margin-top:20px; border:1px solid #111;"></canvas>
    </div>
</div>

<div class="controls">
    <button id="btnRec" class="rec" onclick="startSampling()">1. SAMPLING (ร้องอาาา)</button>
    <input type="file" id="audioIn" accept="audio/*" style="display:none">
    <button onclick="document.getElementById('audioIn').click()">2. LOAD MP3</button>
    <button onclick="runEngine()">3. START ENGINE</button>
</div>

<div id="status-bar">WAITING FOR COMMAND...</div>

<script>
    const NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
    let audioCtx, userBuf, mp3Buf, analyser, isRunning = false;
    let lastMidi = -1;

    // สร้างตาราง 144
    const grid = document.getElementById('noteGrid');
    for(let i=0; i<144; i++){
        const d = document.createElement('div');
        d.className = 'cell'; d.id = `m-${i}`;
        d.innerHTML = NOTES[i%12];
        grid.appendChild(d);
    }

    async function startSampling() {
        if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const stream = await navigator.mediaDevices.getUserMedia({audio: true});
        const rec = new MediaRecorder(stream);
        const chunks = [];
        rec.ondataavailable = e => chunks.push(e.data);
        rec.onstop = async () => {
            userBuf = await audioCtx.decodeAudioData(await new Blob(chunks).arrayBuffer());
            document.getElementById('status-bar').innerText = "✅ หัวเชื้อเสียงพร้อมแล้ว!";
        };
        rec.start();
        document.getElementById('btnRec').innerText = "🔴 กำลังดูดเสียง...";
        setTimeout(() => { rec.stop(); document.getElementById('btnRec').innerText = "SAMPLING จบแล้ว"; }, 3000);
    }

    document.getElementById('audioIn').onchange = async (e) => {
        if(!audioCtx) audioCtx = new AudioContext();
        mp3Buf = await audioCtx.decodeAudioData(await e.target.files[0].arrayBuffer());
        document.getElementById('status-bar').innerText = "🎵 โหลดดนตรีเรียบร้อย";
    };

    function runEngine() {
        if(!userBuf || !mp3Buf) return alert("อัดเสียงและโหลดเพลงก่อนครับ!");
        isRunning = true;
        const source = audioCtx.createBufferSource();
        source.buffer = mp3Buf;
        analyser = audioCtx.createAnalyser();
        analyser.fftSize = 2048;
        source.connect(analyser);
        source.connect(audioCtx.destination);
        source.start();
        process();
    }

    function process() {
        if(!isRunning) return;
        const data = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(data);
        
        let maxV = 0, maxI = 0;
        for(let i=0; i<data.length; i++) { if(data[i] > maxV) { maxV = data[i]; maxI = i; } }

        if(maxV > 200) {
            const freq = maxI * (audioCtx.sampleRate / 2048);
            const midi = Math.round(12 * Math.log2(freq / 440) + 69) + 12;
            
            if(midi != lastMidi && midi >= 0 && midi < 144) {
                triggerVoice(midi, maxV/255);
                // ระบบคอร์ด (ประสานเสียง 3 ไลน์อัตโนมัติ)
                triggerVoice(midi + 4, maxV/500); // Major Third
                triggerVoice(midi + 7, maxV/500); // Perfect Fifth
                lastMidi = midi;
            }
        }
        requestAnimationFrame(process);
    }

    function triggerVoice(m, v) {
        const cell = document.getElementById(`m-${m}`);
        if(cell) { 
            cell.classList.add('active'); 
            setTimeout(() => cell.classList.remove('active'), 100); 
        }
        const s = audioCtx.createBufferSource();
        const g = audioCtx.createGain();
        s.buffer = userBuf;
        s.playbackRate.value = Math.pow(2, (m - 60) / 12);
        g.gain.setValueAtTime(0, audioCtx.currentTime);
        g.gain.linearRampToValueAtTime(v, audioCtx.currentTime + 0.05);
        g.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);
        s.connect(g); g.connect(audioCtx.destination);
        s.start();
    }
</script>
</body>
</html>
"""

components.html(html_code, height=800)
