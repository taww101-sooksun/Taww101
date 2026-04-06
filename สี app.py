import streamlit as st
import streamlit.components.v1 as components

# --- 1. SET UP หน้าจอ (Python Part) ---
st.set_page_config(layout="wide", page_title="SYNAPSE CORE")

# --- 2. รวมร่าง HTML/CSS/JS (The Reality Engine) ---
# ผมใช้เครื่องหมาย ''' เพื่อป้องกัน Syntax Error ที่คุณต๊ะเจอครับ
html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { background: #050505; color: #0f0; font-family: 'Courier New', monospace; margin: 0; overflow-y: auto; }
        .top-section { height: 160px; border-bottom: 2px solid #0f0; padding: 15px; background: #000; position: sticky; top: 0; z-index: 100; }
        .grid-container { padding: 15px; background: #050505; }
        .grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 4px; }
        .cell { 
            height: 50px; background: #111; border: 1px solid #222; 
            display: flex; align-items: center; justify-content: center; 
            font-size: 10px; color: #444; transition: 0.1s;
        }
        .cell.active { background: #0f0 !important; color: #000; box-shadow: 0 0 20px #0f0; transform: scale(1.1); z-index: 10; font-weight: bold; }
        .cell.base { border: 1.5px solid #fff; color: #fff; }
        
        .controls { display: flex; gap: 10px; margin-top: 10px; }
        button { 
            background: #000; color: #0f0; border: 1px solid #0f0; padding: 10px 20px; 
            cursor: pointer; font-weight: bold; text-transform: uppercase;
        }
        button:hover { background: #0f0; color: #000; }
        #status { font-size: 14px; color: #ffaa00; margin-bottom: 5px; }
    </style>
</head>
<body>

<div class="top-section">
    <div id="status">🔴 SYSTEM OFFLINE: กดปุ่มเพื่อเชื่อมต่อความจริง...</div>
    <div class="controls">
        <button onclick="startEngine()">1. เชื่อมต่อ FIREBASE & MIC</button>
        <button onclick="recordBase()">2. อัดเสียงต้นแบบ (C4)</button>
    </div>
    <div style="margin-top:10px; font-size:12px;">
        TARGET: <span id="targetHz">432.00</span> Hz | LIVE: <span id="liveHz" style="color:#fff">0.00</span> Hz
    </div>
</div>

<div class="grid-container">
    <div class="grid" id="matrix"></div>
</div>

<script type="module">
    import { initializeApp } from "https://www.gstatic.com/firebasejs/9.17.1/firebase-app.js";
    import { getDatabase, ref, set, onValue } from "https://www.gstatic.com/firebasejs/9.17.1/firebase-database.js";

    // --- CONFIG FIREBASE ของคุณต๊ะ ---
    const firebaseConfig = { databaseURL: "https://sooksun1-default-rtdb.firebaseio.com/" };
    const app = initializeApp(firebaseConfig);
    const db = getDatabase(app);
    const syncRef = ref(db, 'live/sync_node');

    let audioCtx, analyser, userBuffer;
    let isRunning = false;

    // สร้าง Matrix 144
    const matrixEl = document.getElementById('matrix');
    const notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
    for(let i=0; i<144; i++) {
        const div = document.createElement('div');
        div.className = 'cell' + (i === 60 ? ' base' : '');
        div.id = 'c-' + i;
        div.innerText = notes[i%12] + Math.floor(i/12);
        matrixEl.appendChild(div);
    }

    // เริ่มระบบ
    window.startEngine = async () => {
        if(isRunning) return;
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        // SENDER: วิเคราะห์ไมค์แล้วส่งขึ้น Cloud
        const source = audioCtx.createMediaStreamSource(stream);
        analyser = audioCtx.createAnalyser();
        analyser.fftSize = 2048;
        source.connect(analyser);
        
        // RECEIVER: ดักฟังค่าจาก Cloud มาโชว์ที่จอ
        onValue(syncRef, (snapshot) => {
            const data = snapshot.val();
            if(data && data.idx !== undefined) {
                triggerCell(data.idx, data.hz);
            }
        });

        isRunning = true;
        document.getElementById('status').innerText = "🟢 SYSTEM ONLINE: กำลังดักฟังข้อมูลจริง...";
        analyzeLoop();
    };

    function analyzeLoop() {
        const buffer = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteFrequencyData(buffer);
        
        let maxV = 0, maxI = 0;
        for(let i=0; i<buffer.length; i++) {
            if(buffer[i] > maxV) { maxV = buffer[i]; maxI = i; }
        }

        if(maxV > 150) {
            const freq = maxI * (audioCtx.sampleRate / analyser.fftSize);
            const midi = Math.round(12 * Math.log2(freq / 440) + 69);
            const idx = midi + 12; // ปรับ Offset เข้าตาราง 144

            if(idx >= 0 && idx < 144) {
                // ยิงความจริงขึ้น Firebase
                set(syncRef, { idx: idx, hz: freq.toFixed(2), time: Date.now() });
            }
        }
        requestAnimationFrame(analyzeLoop);
    }

    function triggerCell(idx, hz) {
        document.getElementById('liveHz').innerText = hz;
        const cell = document.getElementById('c-' + idx);
        if(cell) {
            cell.classList.add('active');
            setTimeout(() => cell.classList.remove('active'), 150);
        }
        // ถ้ามี userBuffer (เสียงอัด) ให้เล่นเสียงด้วย Math-Elastic
        if(userBuffer) playElastic(idx);
    }

    // ส่วนอัดเสียงต้นแบบ C4
    window.recordBase = async () => {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const recorder = new MediaRecorder(stream);
        const chunks = [];
        recorder.ondataavailable = e => chunks.push(e.data);
        recorder.onstop = async () => {
            const ab = await new Blob(chunks).arrayBuffer();
            userBuffer = await audioCtx.decodeAudioData(ab);
            document.getElementById('status').innerText = "✅ บันทึกเสียง C4 สำเร็จ! พร้อม Healer";
        };
        recorder.start();
        document.getElementById('status').innerText = "🎙️ กำลังอัดเสียง... (ร้อง 'อา' โน้ตโดกลาง)";
        setTimeout(() => recorder.stop(), 3000);
    };

    function playElastic(idx) {
        const source = audioCtx.createBufferSource();
        source.buffer = userBuffer;
        // สูตร Math-Elastic: ยืดหดเสียงตามตำแหน่งตารางเทียบกับ C4 (60)
        source.playbackRate.value = Math.pow(2, (idx - 60) / 12);
        source.connect(audioCtx.destination);
        source.start();
    }
</script>
</body>
</html>
"""

# --- 3. รัน HTML บน Streamlit ---
components.html(html_template, height=1000, scrolling=True)
