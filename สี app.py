import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="SYNAPSE MP3 VISUALIZER")

st.title("📟 SYNAPSE: RAINBOW MP3 PLAYER")
st.write("สถานะ: `READY` | อัดเสียงคุณ > เลือกเพลง > ดูการร่ายรำของแสง")

rainbow_player_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { background: #050505; color: #0f0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .player-card { 
            background: #111; border: 2px solid #333; border-radius: 20px; padding: 30px; 
            width: 90%; max-width: 800px; box-shadow: 0 0 50px rgba(0,0,0,1); text-align: center;
        }
        
        /* Vinyl Disk Effect */
        .disk-container { position: relative; width: 200px; height: 200px; margin: 0 auto 20px; }
        .disk { 
            width: 100%; height: 100%; background: radial-gradient(circle, #333 10%, #000 11%, #111 100%); 
            border-radius: 50%; border: 5px solid #222; animation: rotate 5s linear infinite; animation-play-state: paused;
        }
        .disk.playing { animation-play-state: running; }
        .disk-center { 
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            width: 40px; height: 40px; background: #0f0; border-radius: 50%; box-shadow: 0 0 20px #0f0;
        }
        @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

        .controls { display: flex; flex-direction: column; gap: 15px; margin-top: 20px; }
        .btn-group { display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; }
        
        button { 
            background: transparent; color: #0f0; border: 1px solid #0f0; padding: 10px 20px; 
            border-radius: 5px; cursor: pointer; transition: 0.3s; font-weight: bold;
        }
        button:hover { background: rgba(0,255,0,0.1); box-shadow: 0 0 10px #0f0; }
        button.active { background: #f00; border-color: #f00; color: #fff; }

        .grid-visualizer { 
            display: grid; grid-template-columns: repeat(24, 1fr); gap: 4px; 
            margin-top: 30px; background: #000; padding: 15px; border-radius: 10px; border: 1px solid #222;
        }
        .cell { 
            aspect-ratio: 1; background: #1a1a1a; border-radius: 2px; 
            transition: all 0.2s ease;
        }
    </style>
</head>
<body>
    <div class="player-card">
        <div class="disk-container">
            <div class="disk" id="vinyl"></div>
            <div class="disk-center"></div>
        </div>
        
        <h2 id="track-name" style="color: #fff; margin-bottom: 5px;">- NO TRACK LOADED -</h2>
        <div id="status-msg" style="color: #666; font-size: 0.8em; margin-bottom: 20px;">READY TO SYNC</div>

        <div class="controls">
            <div class="btn-group">
                <button id="recBtn">🎙️ อัดเสียงต้นแบบ (3 วิ)</button>
                <input type="file" id="mp3File" accept="audio/*" style="display:none;">
                <button onclick="document.getElementById('mp3File').click()">📂 เลือกไฟล์ MP3</button>
                <button id="startBtn" style="background:#0f0; color:#000;">▶️ PLAY & SYNC</button>
            </div>
        </div>

        <div class="grid-visualizer" id="grid"></div>
    </div>

    <script>
        let audioCtx, userBuffer, mp3Buffer, isRunning = false;
        const statusMsg = document.getElementById('status-msg');
        const vinyl = document.getElementById('vinyl');
        let lastTriggerTime = 0;

        // สร้างตารางไฟ (ขยายเป็น 144 ช่อง แต่จัดเรียงแบบ Compact)
        const grid = document.getElementById('grid');
        for(let i=0; i<144; i++) {
            const div = document.createElement('div');
            div.className = 'cell';
            div.id = 'c' + i;
            grid.appendChild(div);
        }

        // --- Logic เหมือนเดิม แต่ปรับจูนความละมุน ---
        document.getElementById('recBtn').onclick = async function() {
            if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const stream = await navigator.mediaDevices.getUserMedia({audio: true});
            const recorder = new MediaRecorder(stream);
            const chunks = [];
            this.classList.add('active');
            recorder.ondataavailable = e => chunks.push(e.data);
            recorder.onstop = async () => {
                const arrayBuf = await (new Blob(chunks)).arrayBuffer();
                userBuffer = await audioCtx.decodeAudioData(arrayBuf);
                this.classList.remove('active');
                statusMsg.innerText = "VOICE SYNCED ✅";
            };
            setTimeout(() => recorder.stop(), 3000);
            recorder.start();
        };

        document.getElementById('mp3File').onchange = async function(e) {
            if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const file = e.target.files[0];
            document.getElementById('track-name').innerText = file.name;
            const arrayBuf = await file.arrayBuffer();
            mp3Buffer = await audioCtx.decodeAudioData(arrayBuf);
            statusMsg.innerText = "MP3 LOADED ✅";
        };

        document.getElementById('startBtn').onclick = function() {
            if(!userBuffer || !mp3Buffer) return alert("อัดเสียงและเลือกเพลงก่อนนะเพื่อน!");
            isRunning = true;
            vinyl.classList.add('playing');
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

            let maxVal = 0, maxIdx = 0;
            for(let i=20; i<200; i++) {
                if(data[i] > maxVal) { maxVal = data[i]; maxIdx = i; }
            }

            if(maxVal > 180 && audioCtx.currentTime - lastTriggerTime > 0.12) {
                const freq = maxIdx * (audioCtx.sampleRate / analyser.fftSize);
                const midi = Math.round(12 * Math.log2(freq / 440) + 69);
                const gridIdx = Math.min(Math.max(midi + 12, 0), 143);
                triggerEffect(gridIdx, maxVal/255);
                lastTriggerTime = audioCtx.currentTime;
            }
            requestAnimationFrame(() => process(analyser));
        }

        function triggerEffect(idx, vol) {
            const cell = document.getElementById('c' + idx);
            if(cell) {
                const hue = (idx / 144) * 360;
                cell.style.background = `hsl(${hue}, 100%, 50%)`;
                cell.style.boxShadow = `0 0 15px hsl(${hue}, 100%, 50%)`;
                setTimeout(() => {
                    cell.style.background = "#1a1a1a";
                    cell.style.boxShadow = "none";
                }, 250);
            }

            // เสียงบำบัดแบบ Smooth
            const s = audioCtx.createBufferSource();
            s.buffer = userBuffer;
            let rate = Math.pow(2, (idx - 60)/12);
            s.playbackRate.value = Math.max(0.7, Math.min(rate, 1.4)); // กรองเสียงแหลม
            
            const filter = audioCtx.createBiquadFilter();
            filter.type = "lowpass";
            filter.frequency.value = 2000;

            const g = audioCtx.createGain();
            g.gain.setValueAtTime(vol * 0.3, audioCtx.currentTime);
            g.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.5);
            
            s.connect(filter); filter.connect(g); g.connect(audioCtx.destination);
            s.start();
        }
    </script>
</body>
</html>
"""

components.html(rainbow_player_html, height=750)

st.info("💡 วิธีเล่น: อัดเสียงตัวเองหนึ่งโน้ตนิ่งๆ ก่อน (C4) แล้วค่อยโหลดเพลง MP3 ที่ชอบมาเปิดครับ")
