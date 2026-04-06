import streamlit as st
import streamlit.components.v1 as components

# --- 1. SET PAGE ---
st.set_page_config(layout="wide", page_title="SYNAPSE: MATH-ELASTIC")

# --- 2. UI HEADER ---
st.title("🥷 SYNAPSE: MATH-ELASTIC HEALER")
st.write("สถานะ: `READY` | ระบบคำนวณคณิตศาสตร์ยืดหดเสียง 144 ช่องสัญญาณ")

# --- 3. THE HEART (HTML/JS/MATH) ---
# เราจะยก Logic ที่คุณเขียนมาปรับปรุงให้ 'เนียน' ขึ้นในนี้
math_engine_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { background: #000; color: #0f0; font-family: monospace; margin: 0; overflow: hidden; }
        .container { display: flex; flex-direction: column; height: 100vh; }
        canvas { width: 100%; height: 150px; background: #050505; border-bottom: 1px solid #0f0; }
        .controls { padding: 10px; display: flex; gap: 10px; background: #111; }
        button { background: #000; color: #0f0; border: 1px solid #0f0; padding: 10px; cursor: pointer; }
        button:hover { background: #0f0; color: #000; }
        button.active { background: #f00; color: #fff; }
        .grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 2px; padding: 10px; flex: 1; overflow-y: auto; }
        .cell { height: 30px; background: #111; border: 1px solid #222; font-size: 0.6em; display: flex; align-items: center; justify-content: center; }
        .cell.active { background: #0ff; color: #000; box-shadow: 0 0 10px #0ff; transform: scale(1.1); z-index: 5; }
    </style>
</head>
<body>
    <div class="container">
        <canvas id="viz"></canvas>
        <div class="controls">
            <button id="recBtn">1. อัดเสียงต้นแบบ (C4)</button>
            <input type="file" id="mp3File" accept="audio/*" style="color:#0f0">
            <button id="startBtn">2. START ENGINE</button>
            <div id="msg" style="font-size:0.8em; margin-left:10px; align-self:center;">รอการตั้งค่า...</div>
        </div>
        <div class="grid" id="grid"></div>
    </div>

    <script>
        let audioCtx, userBuffer, mp3Buffer, isRunning = false;
        const viz = document.getElementById('viz');
        const ctx = viz.getContext('2d');
        const msg = document.getElementById('msg');
        let lastTriggerTime = 0;

        // สร้างตาราง 144
        const grid = document.getElementById('grid');
        for(let i=0; i<144; i++) {
            const div = document.createElement('div');
            div.className = 'cell';
            div.id = 'c' + i;
            div.innerText = i;
            grid.appendChild(div);
        }

        // ระบบอัดเสียง
        document.getElementById('recBtn').onclick = async function() {
            if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const stream = await navigator.mediaDevices.getUserMedia({audio: true});
            const recorder = new MediaRecorder(stream);
            const chunks = [];
            this.classList.add('active');
            this.innerText = "กำลังอัด (ร้อง อ่าาา ยาวๆ)...";
            
            recorder.ondataavailable = e => chunks.push(e.data);
            recorder.onstop = async () => {
                const blob = new Blob(chunks);
                const arrayBuf = await blob.arrayBuffer();
                userBuffer = await audioCtx.decodeAudioData(arrayBuf);
                this.classList.remove('active');
                this.innerText = "✅ อัดเสียงสำเร็จ";
                msg.innerText = "เสียงต้นแบบพร้อมแล้ว";
            };
            setTimeout(() => recorder.stop(), 3000); // อัด 3 วินาที
            recorder.start();
        };

        // โหลด MP3
        document.getElementById('mp3File').onchange = async function(e) {
            if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const file = e.target.files[0];
            const arrayBuf = await file.arrayBuffer();
            mp3Buffer = await audioCtx.decodeAudioData(arrayBuf);
            msg.innerText = "โหลด MP3 สำเร็จ";
        };

        // เริ่มรันระบบ
        document.getElementById('startBtn').onclick = function() {
            if(!userBuffer || !mp3Buffer) return alert("อัดเสียงและเลือก MP3 ก่อน!");
            isRunning = true;
            const source = audioCtx.createBufferSource();
            source.buffer = mp3Buffer;
            const analyser = audioCtx.createAnalyser();
            analyser.fftSize = 1024;
            source.connect(analyser);
            analyser.connect(audioCtx.destination);
            source.start();
            process(analyser);
        };

        function process(analyser) {
            if(!isRunning) return;
            const data = new Uint8Array(analyser.frequencyBinCount);
            analyser.getByteFrequencyData(data);

            // วาด Viz
            ctx.clearRect(0,0,viz.width, viz.height);
            ctx.fillStyle = '#0f0';
            for(let i=0; i<data.length; i++) {
                ctx.fillRect(i*2, 150-data[i]/2, 1, data[i]/2);
            }

            // --- MATH LOGIC: หา Frequency หลักเพื่อเปลี่ยนโน้ต ---
            let maxVal = 0, maxIdx = 0;
            // โฟกัสช่วง 150Hz - 1000Hz (ย่านเสียงร้อง)
            for(let i=10; i<100; i++) {
                if(data[i] > maxVal) { maxVal = data[i]; maxIdx = i; }
            }

            if(maxVal > 150 && audioCtx.currentTime - lastTriggerTime > 0.1) {
                const freq = maxIdx * (audioCtx.sampleRate / analyser.fftSize);
                const midi = Math.round(12 * Math.log2(freq / 440) + 69);
                const gridIdx = Math.min(Math.max(midi + 12, 0), 143);
                
                triggerVoice(gridIdx, maxVal/255);
                lastTriggerTime = audioCtx.currentTime;
            }
            requestAnimationFrame(() => process(analyser));
        }

        function triggerVoice(idx, vol) {
            const cell = document.getElementById('c' + idx);
            if(cell) {
                cell.classList.add('active');
                setTimeout(() => cell.classList.remove('active'), 100);
            }

            const s = audioCtx.createBufferSource();
            s.buffer = userBuffer;
            // MATH: Playback Rate = 2^(n/12)
            const diff = idx - 60; // เทียบกับ C4
            s.playbackRate.value = Math.pow(2, diff/12);
            
            const g = audioCtx.createGain();
            g.gain.value = vol * 0.5;
            g.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);
            
            s.connect(g);
            g.connect(audioCtx.destination);
            s.start();
        }
    </script>
</body>
</html>
"""

# --- 4. RENDER ---
# กำหนดความสูงให้พอดีกับหน้าจอ
components.html(math_engine_html, height=800, scrolling=True)

st.info("💡 วิธีใช้: 1.กดอัดเสียง (ร้อง C4 ค้างไว้) -> 2.เลือกไฟล์ MP3 -> 3.กด START ENGINE")
