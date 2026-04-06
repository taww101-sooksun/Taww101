import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="SYNAPSE: X-CHORDS VOWEL-COLOR")

# --- โค้ด HTML/JS แบบ Color Coding เต็มสูบ ---
html_code = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <style>
        :root { --dim: #111; --bg: #000; }
        body { 
            background: var(--bg); color: #fff; font-family: 'Courier New', monospace;
            margin: 0; display: flex; flex-direction: column; height: 100vh; overflow: hidden;
        }
        
        /* สถาปัตยกรรมหน้าจอ */
        header { padding: 15px; border-bottom: 2px solid #333; display: flex; justify-content: space-between; align-items: center;}
        .main-engine { display: flex; flex: 1; overflow: hidden; gap: 10px; padding: 10px; }
        
        /* ฝั่งซ้าย: กระดาน 248832 (Melody Zone) */
        .melody-zone { flex: 2; overflow-y: auto; background: #000; border: 1px solid #222; padding: 10px; }
        .grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 3px; }
        .cell { 
            aspect-ratio: 1; border: 1px solid #111; font-size: 0.6rem; 
            display: flex; align-items: center; justify-content: center; color: #222;
            transition: background-color 0.1s, box-shadow 0.1s; border-radius: 3px;
        }

        /* สีไฟกระพริบตามสระ */
        .cell.a-active { background-color: #0f0; color: #000; box-shadow: 0 0 15px #0f0; transform: scale(1.1); }
        .cell.i-active { background-color: #0ff; color: #000; box-shadow: 0 0 15px #0ff; transform: scale(1.1); }
        .cell.u-active { background-color: #80f; color: #fff; box-shadow: 0 0 15px #80f; transform: scale(1.1); }
        .cell.e-active { background-color: #ff0; color: #000; box-shadow: 0 0 15px #ff0; transform: scale(1.1); }
        .cell.o-active { background-color: #f80; color: #000; box-shadow: 0 0 15px #f80; transform: scale(1.1); }

        /* ฝั่งขวา: แผงควบคุมสระและคอร์ด (Control Panel) */
        .control-panel { flex: 1; background: #050505; border-left: 1px solid #333; padding: 15px; }
        .vowel-btn { 
            width: 100%; padding: 15px; margin-bottom: 10px; border: 1px solid #222; 
            background: #000; text-align: left; cursor: pointer; color: #fff; font-weight: bold;
        }
        .vowel-btn:hover { border-color: #555; }
        .vowel-btn.active { border-color: #fff; box-shadow: inset 0 0 10px rgba(255,255,255,0.2); }
        
        /* สีปุ่มสระ */
        #btn-a.active { background-color: #040; color: #0f0; border-color: #0f0; }
        #btn-i.active { background-color: #044; color: #0ff; border-color: #0ff; }
        #btn-u.active { background-color: #304; color: #80f; border-color: #80f; }
        #btn-e.active { background-color: #440; color: #ff0; border-color: #ff0; }
        #btn-o.active { background-color: #420; color: #f80; border-color: #f80; }

        /* ระบบบันทึก (LOG) */
        #status-bar { height: 30px; background: #111; font-size: 0.7rem; padding: 5px 20px; border-top: 1px solid #222; color: #888; }
        
        /* ปุ่มควบคุมหลัก */
        .controls { padding: 15px; background: #000; border-top: 1px solid #333; display: flex; gap: 10px; }
        button.main-btn { background: none; border: 1px solid #555; color: #fff; padding: 10px 20px; cursor: pointer; font-weight: bold; text-transform: uppercase;}
        button.main-btn:hover { background: #111; border-color: #fff; }
        button.main-btn.rec { border-color: #f00; color: #f00; }
        button.main-btn.rec.active { background: #f00; color: #fff; animation: blink 1s infinite; }

        @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    </style>
</head>
<body>

<header>
    <div><strong>SYNAPSE X-ENGINE</strong> | "อยู่นิ่งๆ ไม่เจ็บตัว" Vowel Color Edition</div>
    <div id="freq-val" style="color: #444;">DETECTING...</div>
</header>

<div class="main-engine">
    <div class="melody-zone">
        <div style="font-size: 0.7rem; color: #444; margin-bottom: 10px;">MELODY MATRIX (144 SLOTS)</div>
        <div class="grid" id="noteGrid"></div>
    </div>
    
    <div class="control-panel">
        <div style="font-size: 0.7rem; color: #444; margin-bottom: 15px;">VOWEL SELECTOR</div>
        <div id="vowel-controls">
            <button class="vowel-btn a-btn active" id="btn-a" onclick="setVowel('a')">A - อา (Neon Green)</button>
            <button class="vowel-btn i-btn" id="btn-i" onclick="setVowel('i')">I - อี (Ice Blue)</button>
            <button class="vowel-btn u-btn" id="btn-u" onclick="setVowel('u')">U - อู (Deep Purple)</button>
            <button class="vowel-btn e-btn" id="btn-e" onclick="setVowel('e')">E - เอ (Golden Yellow)</button>
            <button class="vowel-btn o-btn" id="btn-o" onclick="setVowel('o')">O - โอ (Orange Blazing)</button>
        </div>
        <canvas id="wave-scope" style="width:100%; height:80px; margin-top:20px; border:1px solid #111;"></canvas>
    </div>
</div>

<div class="controls">
    <button id="btnRec" class="main-btn rec" onclick="startSampling()">1. SAMPLING (ร้อง: อา-อี-อู-เอ-โอ 3วิ)</button>
    <input type="file" id="audioIn" accept="audio/*" style="display:none">
    <button class="main-btn" onclick="document.getElementById('audioIn').click()">2. LOAD MP3</button>
    <button class="main-btn" onclick="runEngine()">3. START ENGINE</button>
</div>

<div id="status-bar">WAITING FOR COMMAND...</div>

<script>
    const NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
    // สัดส่วนพิกัดของสระในไฟล์เสียง 3 วิ (Sampling Time)
    const VOWEL_MAP = { a: 0.0, i: 0.6, u: 1.2, e: 1.8, o: 2.4 };
    let currentVowel = 'a';
    let audioCtx, userBuf, mp3Buf, analyser, isRunning = false;
    let lastMidi = -1;

    // สร้างตาราง 144 ช่อง
    const grid = document.getElementById('noteGrid');
    for(let i=0; i<248832; i++){
        const d = document.createElement('div');
        d.className = 'cell'; d.id = `m-${i}`;
        d.innerHTML = NOTES[i%12];
        grid.appendChild(d);
    }

    // ฟังก์ชันเลือกสระ (เปลี่ยนสีปุ่มและกำหนดพิกัดเสียง)
    function setVowel(vowel) {
        currentVowel = vowel;
        document.querySelectorAll('.vowel-btn').forEach(b => b.classList.remove('active'));
        document.getElementById(`btn-${vowel}`).classList.add('active');
        document.getElementById('status-bar').innerText = `✅ เปลี่ยนเสียงเป็นสระ: ${vowel.toUpperCase()}`;
    }

    async function startSampling() {
        if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const stream = await navigator.mediaDevices.getUserMedia({audio: true});
        const rec = new MediaRecorder(stream);
        const chunks = [];
        const btnRec = document.getElementById('btnRec');

        rec.ondataavailable = e => chunks.push(e.data);
        rec.onstop = async () => {
            userBuf = await audioCtx.decodeAudioData(await new Blob(chunks).arrayBuffer());
            document.getElementById('status-bar').innerText = "✅ หัวเชื้อสระ 5 ตัวพร้อมแล้ว!";
            btnRec.innerText = "SAMPLING จบแล้ว";
            btnRec.classList.remove('active');
        };
        rec.start();
        btnRec.classList.add('active');
        btnRec.innerText = "🔴 ร้อง อา-อี-อู-เอ-โอ ยาวๆ...";
        // ให้ร้องตัวละ 0.6 วินาที (รวม 3 วินาทีพอดี)
        setTimeout(() => { rec.stop(); }, 3000); 
    }

    document.getElementById('audioIn').onchange = async (e) => {
        if(!audioCtx) audioCtx = new AudioContext();
        mp3Buf = await audioCtx.decodeAudioData(await e.target.files[0].arrayBuffer());
        document.getElementById('status-bar').innerText = "🎵 โหลดดนตรีเรียบร้อย";
    };

    function runEngine() {
        if(!userBuf || !mp3Buf) return alert("อัดเสียง (อา-อี-อู-เอ-โอ) และโหลดเพลงก่อนครับ!");
        isRunning = true;
        const source = audioCtx.createBufferSource();
        source.buffer = mp3Buf;
        analyser = audioCtx.createAnalyser();
        analyser.fftSize = 2048;
        source.connect(analyser);
        source.connect(audioCtx.destination);
        source.start();
        process();
        document.getElementById('status-bar').innerText = "🚀 เดินเครื่อง X-ENGINE: ร้องตามสระที่เลือก...";
    }

    function process() {
        if(!isRunning) return;
        const data = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(data);
        
        let maxV = 0, maxI = 0;
        for(let i=0; i<data.length; i++) { if(data[i] > maxV) { maxV = data[i]; maxI = i; } }

        if(maxV > 210) { // ปรับ Threshold ความดังให้สูงขึ้นเพื่อให้จับตัวโน้ตชัดๆ
            const freq = maxI * (audioCtx.sampleRate / 2048);
            const midi = Math.round(12 * Math.log2(freq / 440) + 69) + 12;
            
            if(midi != lastMidi && midi >= 0 && midi < 144) {
                // ยิงเสียงสระปัจจุบัน
                triggerVowelVoice(midi, maxV/255);
                lastMidi = midi;
            }
        }
        requestAnimationFrame(process);
    }

    function triggerVowelVoice(m, v) {
        // หาพิกัดเริ่มต้นของสระในไฟล์ 3 วิ
        const startTime = VOWEL_MAP[currentVowel];
        
        // แสดงผลไฟกระพริบตามสีของสระ
        const cell = document.getElementById(`m-${m}`);
        if(cell) { 
            const vowelClass = `${currentVowel}-active`;
            cell.classList.add(vowelClass); 
            // ให้สว่างค้างไว้ 150ms เพื่อให้เห็นสีชัดเจน
            setTimeout(() => cell.classList.remove(vowelClass), 150); 
        }

        // ยิงเสียงสระจากพิกัดที่กำหนด
        const source = audioCtx.createBufferSource();
        const gainNode = audioCtx.createGain();
        source.buffer = userBuf;
        // บิดความเร็วเสียง
        source.playbackRate.value = Math.pow(2, (m - 60) / 12); 
        
        // ADSR Envelope (นุ่มนวลขึ้น)
        gainNode.gain.setValueAtTime(0, audioCtx.currentTime);
        gainNode.gain.linearRampToValueAtTime(v * 0.8, audioCtx.currentTime + 0.04);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.35);

        source.connect(gainNode); 
        gainNode.connect(audioCtx.destination);
        
        // เล่นเสียงสระจากพิกัด (startTime) เป็นเวลา 0.5 วินาที
        source.start(0, startTime, 0.5); 
    }
</script>
</body>
</html>
"""

components.html(html_code, height=900)
