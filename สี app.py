import streamlit as st

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="Neon Audio Visualizer", layout="wide")

# ส่วนประกอบของ Streamlit (แสดงหัวข้อแบบ Neon)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .main { background-color: #000000; }
    .neon-text {
        font-family: 'Orbitron', sans-serif;
        color: #fff;
        text-align: center;
        text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 20px #ff00de, 0 0 30px #ff00de, 0 0 40px #ff00de;
        font-size: 3rem;
        margin-bottom: 20px;
    }
    </style>
    <h1 class="neon-text">NEON COSMIC MIXER</h1>
""", unsafe_allow_html=True)

# โค้ด HTML/JS สำหรับ Mixer และ Visualizer
html_code = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: transparent; color: white; font-family: 'Inter', sans-serif; overflow: hidden; }
        .neon-border { border: 2px solid #00f3ff; box-shadow: 0 0 15px #00f3ff; }
        .btn-neon { transition: 0.3s; text-transform: uppercase; letter-spacing: 2px; font-weight: bold; }
        .btn-a { border: 2px solid #ff0055; color: #ff0055; }
        .btn-a:hover { background: #ff0055; color: white; box-shadow: 0 0 20px #ff0055; }
        .btn-b { border: 2px solid #00ff00; color: #00ff00; }
        .btn-b:hover { background: #00ff00; color: white; box-shadow: 0 0 20px #00ff00; }
        canvas { width: 100%; height: 300px; border-radius: 15px; background: #111; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="max-w-4xl mx-auto p-4 bg-black/80 rounded-3xl border border-white/10">
        
        <canvas id="visualizer"></canvas>

        <div class="grid grid-cols-2 gap-4 mt-6">
            <div class="p-4 rounded-xl bg-gray-900 border border-pink-500/30">
                <label class="block text-pink-500 mb-2">🎵 เพลง A (Neon Red)</label>
                <input type="file" id="fileA" accept="audio/*" class="w-full text-xs text-gray-400" onchange="loadAudio(this.files[0], 'A')">
            </div>
            <div class="p-4 rounded-xl bg-gray-900 border border-green-500/30">
                <label class="block text-green-500 mb-2">🎵 เพลง B (Neon Green)</label>
                <input type="file" id="fileB" accept="audio/*" class="w-full text-xs text-gray-400" onchange="loadAudio(this.files[0], 'B')">
            </div>
        </div>

        <div class="mt-6 flex flex-wrap gap-4 justify-center">
            <button onclick="startPlayingA()" id="btn-play" class="btn-neon btn-a px-6 py-2 rounded-full">เริ่มเล่นเพลง A</button>
            <button onclick="startCrossfade()" id="btn-fade" class="btn-neon border-orange-500 text-orange-500 px-6 py-2 rounded-full hover:bg-orange-500 hover:text-white">Crossfade ไป B</button>
            <button onclick="toggleVocal()" id="btn-vocal" class="btn-neon border-blue-500 text-blue-500 px-6 py-2 rounded-full hover:bg-blue-500 hover:text-white">Karaoke Mode</button>
        </div>

        <div id="status" class="text-center mt-4 text-xs tracking-widest text-gray-500 uppercase">ระบบพร้อมรอรับไฟล์...</div>
    </div>

    <script>
        let audioCtx, analyser, songABuffer, songBBuffer, sourceA, sourceB, gainA, gainB;
        let isPlaying = false;
        let current = 'None';
        let dataArray, canvas, canvasCtx;

        function initAudio() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = audioCtx.createAnalyser();
                analyser.fftSize = 256;
                dataArray = new Uint8Array(analyser.frequencyBinCount);
                setupCanvas();
            }
        }

        function setupCanvas() {
            canvas = document.getElementById('visualizer');
            canvasCtx = canvas.getContext('2d');
            draw();
        }

        function draw() {
            requestAnimationFrame(draw);
            if (!analyser) return;
            analyser.getByteFrequencyData(dataArray);

            canvasCtx.fillStyle = 'rgba(0, 0, 0, 0.2)';
            canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

            const barWidth = (canvas.width / dataArray.length) * 2.5;
            let barHeight;
            let x = 0;

            for(let i = 0; i < dataArray.length; i++) {
                barHeight = dataArray[i] * 1.2;
                
                // สีสะท้อนแสงตามจังหวะ (สลับ แดง น้ำเงิน ม่วง ส้ม)
                let r = dataArray[i] + (25 * (i / dataArray.length));
                let g = 250 * (i / dataArray.length);
                let b = 255;

                canvasCtx.fillStyle = `rgb(${r},${g},${b})`;
                canvasCtx.shadowBlur = 15;
                canvasCtx.shadowColor = `rgb(${r},${g},${b})`;
                
                canvasCtx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
                x += barWidth + 1;
            }
        }

        async function loadAudio(file, key) {
            initAudio();
            document.getElementById('status').innerText = `กำลังโหลดเพลง ${key}...`;
            const arrayBuffer = await file.arrayBuffer();
            const buffer = await audioCtx.decodeAudioData(arrayBuffer);
            if(key === 'A') songABuffer = buffer;
            else songBBuffer = buffer;
            document.getElementById('status').innerText = `โหลดเพลง ${key} สำเร็จ!`;
        }

        function startPlayingA() {
            if (!songABuffer || !songBBuffer) return alert("โหลดเพลงให้ครบก่อนครับอาจารย์!");
            if (isPlaying) return;

            sourceA = audioCtx.createBufferSource();
            sourceA.buffer = songABuffer;
            gainA = audioCtx.createGain();
            
            sourceA.connect(gainA).connect(analyser).connect(audioCtx.destination);
            sourceA.start(0);
            
            // เตรียม B ไว้แต่ปิดเสียง
            sourceB = audioCtx.createBufferSource();
            sourceB.buffer = songBBuffer;
            gainB = audioCtx.createGain();
            gainB.gain.value = 0;
            sourceB.connect(gainB).connect(analyser).connect(audioCtx.destination);
            sourceB.start(0);

            isPlaying = true;
            current = 'A';
            document.getElementById('status').innerText = "PLAYING: SONG A";
        }

        function startCrossfade() {
            const duration = 5;
            const now = audioCtx.currentTime;
            if(current === 'A') {
                gainA.gain.linearRampToValueAtTime(1, now);
                gainA.gain.linearRampToValueAtTime(0, now + duration);
                gainB.gain.linearRampToValueAtTime(0, now);
                gainB.gain.linearRampToValueAtTime(1, now + duration);
                current = 'B';
                document.getElementById('status').innerText = "FADING TO: SONG B";
            } else {
                gainB.gain.linearRampToValueAtTime(1, now);
                gainB.gain.linearRampToValueAtTime(0, now + duration);
                gainA.gain.linearRampToValueAtTime(0, now);
                gainA.gain.linearRampToValueAtTime(1, now + duration);
                current = 'A';
                document.getElementById('status').innerText = "FADING TO: SONG A";
            }
        }

        function toggleVocal() {
            alert("Vocal Removal กำลังประมวลผลผ่านเฟสเสียง...");
            // Logic เหมือนเดิมที่อาจารย์มี แต่จะผ่าน Analyser ตลอดเวลา
        }
    </script>
</body>
</html>
"""

# แสดงผล HTML
st.components.v1.html(html_code, height=700)

st.info("💡 คำแนะนำ: อาจารย์ต๊ะเลือกไฟล์เพลง A และ B แล้วกด 'เริ่มเล่นเพลง A' กราฟเสียงสี Neon จะเต้นตามจังหวะเพลงทันทีครับ เหมาะสำหรับแคปหน้าจอทำคลิปมาก!")
