import streamlit as st
import streamlit.components.v1 as components

# --- 1. SET PAGE CONFIG ---
st.set_page_config(layout="wide", page_title="SYNAPSE: MATH-ELASTIC 7-COLOR")

# --- 2. HEADER ---
st.title("🥷 SYNAPSE: MATH-ELASTIC HEALER (RAINBOW CORE)")
st.write("สถานะ: `FINALIZING` | ระบบบำบัดด้วยคณิตศาสตร์ 7 สี 144 ช่องสัญญาณ")

# --- 3. THE RAINBOW ENGINE (HTML/JS/MATH) ---
rainbow_engine_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { background: #000; color: #0f0; font-family: 'Courier New', monospace; margin: 0; overflow: hidden; }
        .container { display: flex; flex-direction: column; height: 100vh; }
        canvas { width: 100%; height: 150px; background: #050505; border-bottom: 2px solid #333; }
        
        .controls { padding: 15px; display: flex; gap: 15px; background: #111; border-bottom: 1px solid #0f0; flex-wrap: wrap; }
        button { 
            background: #000; color: #0f0; border: 1px solid #0f0; padding: 12px 20px; 
            cursor: pointer; font-weight: bold; text-transform: uppercase;
        }
        button:hover { background: #0f0; color: #000; box-shadow: 0 0 15px #0f0; }
        button.active { background: #f00; border-color: #f00; color: #fff; }
        
        .grid { 
            display: grid; grid-template-columns: repeat(12, 1fr); gap: 3px; 
            padding: 15px; flex: 1; overflow-y: auto; background: #080808;
        }
        .cell { 
            height: 40px; background: #111; border: 1px solid #222; 
            font-size: 0.7em; display: flex; align-items: center; justify-content: center;
            transition: all 0.1s ease; color: #444; border-radius: 3px;
        }
        .cell.active { transform: scale(1.15); z-index: 10; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <canvas id="viz"></canvas>
        <div class="controls">
            <button id="recBtn">1. อัดเสียงต้นแบบ (C4)</button>
            <div style="background:#222; padding:10px; border-radius:5px;">
                <label>2. เลือก MP3:</label>
                <input type="file" id="mp3File" accept="audio/*" style="color:#0f0; margin-left:10px;">
            </div>
            <button id="startBtn">3. START MATH ENGINE</button>
            <div id="msg" style="color:#0ff; font-size:0.9em; align-self:center;">- SYSTEM STANDBY -</div>
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

        // 1. ระบบอัดเสียง (Base Note)
        document.getElementById('recBtn').onclick = async function() {
            if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            try {
                const stream = await navigator.mediaDevices.getUserMedia({audio: true});
                const recorder = new MediaRecorder(stream);
                const chunks = [];
                this.classList.add('active');
                this.innerText = "🎙️ กำลังอัดเสียง...";
                
                recorder.ondataavailable = e => chunks.push(e.data);
                recorder.onstop = async () => {
                    const blob = new Blob(chunks);
                    const arrayBuf = await blob.arrayBuffer();
                    userBuffer = await audioCtx.decodeAudioData(arrayBuf);
                    this.classList.remove('active');
                    this.innerText = "✅ บันทึกสำเร็จ (C4)";
                    msg.innerText = "Math-Base Acquired.";
                };
                setTimeout(() => recorder.stop(), 3000); 
                recorder.start();
            } catch(e) { alert("Mic Access Denied"); }
        };

        // 2. โหลด MP3
        document.getElementById('mp3File').onchange = async function(e) {
            if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const file = e.target.files[0];
            msg.innerText = "⏳ Decoding MP3...";
            const arrayBuf = await file.arrayBuffer();
            mp3Buffer = await audioCtx.decodeAudioData(arrayBuf);
            msg.innerText = "MP3 Synced.";
        };

        // 3. รันระบบ (Math Logic)
        document.getElementById('startBtn').onclick = function() {
            if(!userBuffer || !mp3Buffer) return alert("กรุณาอัดเสียงและเลือก MP3 ก่อนครับ!");
            isRunning = true;
            const source = audioCtx.createBufferSource();
            source.buffer = mp3Buffer;
            const analyser = audioCtx.createAnalyser();
            analyser.fftSize = 2048;
            source.connect(analyser);
            analyser.connect(audioCtx.destination);
            source.start();
            msg.innerText = "🚀 ENGINE RUNNING (7-COLORS MODE)";
            process(analyser);
        };

        function process(analyser) {
            if(!isRunning) return;
            const data = new Uint8Array(analyser.frequencyBinCount);
            analyser.getByteFrequencyData(data);

            // วาด Viz 7 สี
            ctx.clearRect(0,0,viz.width, viz.height);
            for(let i=0; i<data.length; i+=4) {
                const hue = (i / data.length) * 360;
                ctx.fillStyle = `hsl(${hue}, 100%, 50%)`;
                ctx.fillRect(i * (viz.width/data.length) * 2, viz.height - data[i]/2, 2, data[i]/2);
            }

            // ค้นหาโดมิแนนต์โน้ต (Human Voice Range)
            let maxVal = 0, maxIdx = 0;
            for(let i=15; i<150; i++) { // ตัดเสียงเบสต่ำๆ ออก
                if(data[i] > maxVal) { maxVal = data[i]; maxIdx = i; }
            }

            // ถ้าความดังถึงเกณฑ์ และทิ้งช่วงห่างนิดนึงเพื่อไม่ให้เสียงรัวเกินไป
            if(maxVal > 170 && audioCtx.currentTime - lastTriggerTime > 0.08) {
                const freq = maxIdx * (audioCtx.sampleRate / analyser.fftSize);
                const midi = Math.round(12 * Math.log2(freq / 440) + 69);
                const gridIdx = Math.min(Math.max(midi + 12, 0), 143);
                
                triggerRainbowVoice(gridIdx, maxVal/255);
                lastTriggerTime = audioCtx.currentTime;
            }
            requestAnimationFrame(() => process(analyser));
        }

        function triggerRainbowVoice(idx, vol) {
            const cell = document.getElementById('c' + idx);
            if(cell) {
                // MATH: คำนวณสีตามช่องโน้ต (รุ้ง 7 สี)
                const hue = (idx / 144) * 360;
                const color = `hsl(${hue}, 100%, 50%)`;
                
                cell.classList.add('active');
                cell.style.background = color;
                cell.style.boxShadow = `0 0 20px ${color}`;
                cell.style.color = "#000";

                setTimeout(() => {
                    cell.classList.remove('active');
                    cell.style.background = "#111";
                    cell.style.boxShadow = "none";
                    cell.style.color = "#444";
                }, 150);
            }

            // เล่นเสียงยืดหดตามคณิตศาสตร์
            const s = audioCtx.createBufferSource();
            s.buffer = userBuffer;
            const diff = idx - 60; // เทียบกับ C4
            s.playbackRate.value = Math.pow(2, diff/12);
            
            const g = audioCtx.createGain();
            g.gain.setValueAtTime(vol * 0.6, audioCtx.currentTime);
            g.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.4);
            
            s.connect(g);
            g.connect(audioCtx.destination);
            s.start();
        }
    </script>
</body>
</html>
"""

# --- 4. RENDER ---
components.html(rainbow_engine_html, height=850, scrolling=True)

st.success("✨ ระบบติดตั้ง 7-Colors Rainbow Engine เรียบร้อย!")
st.info("💡 คำแนะนำสุดท้ายของวัน: ร้องโน้ตเดียวให้นิ่งที่สุดตอนอัด แล้วเพลงจะออกมาสวยครับ พักผ่อนได้!")
