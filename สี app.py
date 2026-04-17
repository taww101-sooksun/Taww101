import streamlit as st

st.set_page_config(page_title="Neon Studio Mixer", layout="centered")

# CSS สไตล์ Neon อาจารย์ต๊ะ
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .main { background-color: #000000; }
    .neon-title {
        font-family: 'Orbitron', sans-serif;
        color: #fff;
        text-align: center;
        text-shadow: 0 0 10px #ff00de, 0 0 20px #ff00de;
        font-size: 2rem;
        margin-bottom: 10px;
    }
    </style>
    <h1 class="neon-title">NEON STUDIO MIXER</h1>
""", unsafe_allow_html=True)

html_code = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: transparent; color: white; font-family: 'Inter', sans-serif; overflow: hidden; }
        .neon-box { border: 1px solid rgba(255, 255, 255, 0.1); background: rgba(15, 15, 15, 0.9); }
        .visualizer-container { height: 150px; background: #000; border-radius: 10px; border: 1px solid #333; }
        .btn-neon { transition: 0.2s; font-weight: bold; font-size: 12px; }
        .neon-red { border: 2px solid #ff0055; color: #ff0055; box-shadow: 0 0 10px #ff0055; }
        .neon-green { border: 2px solid #00ffcc; color: #00ffcc; box-shadow: 0 0 10px #00ffcc; }
        .progress-bg { height: 6px; background: #222; border-radius: 3px; overflow: hidden; }
        .progress-fill { height: 100%; width: 0%; background: linear-gradient(90deg, #ff00de, #00f3ff); }
    </style>
</head>
<body>
    <div class="max-w-md mx-auto p-4 neon-box rounded-2xl">
        
        <canvas id="visualizer" class="visualizer-container w-full"></canvas>

        <div class="mt-4 p-3 border-l-4 border-pink-600 bg-gray-900/50 rounded-r-lg">
            <div class="flex justify-between items-center mb-1">
                <span class="text-[10px] text-pink-500 font-bold uppercase">Song A</span>
                <span id="timeA" class="text-[10px] font-mono text-gray-400">00:00</span>
            </div>
            <div id="nameA" class="text-xs font-semibold mb-2 truncate text-gray-200">ยังไม่ได้โหลดเพลง A...</div>
            <input type="file" id="inputA" accept="audio/*" class="hidden" onchange="loadAudio(this.files[0], 'A')">
            <button onclick="document.getElementById('inputA').click()" class="text-[10px] bg-pink-900/30 px-2 py-1 rounded border border-pink-500/50 text-pink-300">เลือกเพลง A</button>
            <div class="progress-bg mt-2"><div id="barA" class="progress-fill"></div></div>
        </div>

        <div class="mt-3 p-3 border-l-4 border-cyan-500 bg-gray-900/50 rounded-r-lg">
            <div class="flex justify-between items-center mb-1">
                <span class="text-[10px] text-cyan-400 font-bold uppercase">Song B</span>
                <span id="timeB" class="text-[10px] font-mono text-gray-400">00:00</span>
            </div>
            <div id="nameB" class="text-xs font-semibold mb-2 truncate text-gray-200">ยังไม่ได้โหลดเพลง B...</div>
            <input type="file" id="inputB" accept="audio/*" class="hidden" onchange="loadAudio(this.files[0], 'B')">
            <button onclick="document.getElementById('inputB').click()" class="text-[10px] bg-cyan-900/30 px-2 py-1 rounded border border-cyan-500/50 text-cyan-300">เลือกเพลง B</button>
            <div class="progress-bg mt-2"><div id="barB" class="progress-fill" style="background: #00ffcc;"></div></div>
        </div>

        <div class="grid grid-cols-2 gap-3 mt-4">
            <button onclick="startPlaying()" id="btn-play" class="btn-neon neon-red py-2 rounded-lg uppercase">Start Mix</button>
            <button onclick="startCrossfade()" id="btn-fade" class="btn-neon neon-green py-2 rounded-lg uppercase">Crossfade</button>
        </div>
    </div>

    <script>
        let audioCtx, analyser, songA, songB, gainA, gainB, sourceA, sourceB;
        let isPlaying = false, current = 'A';
        let dataArray, canvas, canvasCtx;

        function initAudio() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = audioCtx.createAnalyser();
                analyser.fftSize = 128;
                dataArray = new Uint8Array(analyser.frequencyBinCount);
                canvas = document.getElementById('visualizer');
                canvasCtx = canvas.getContext('2d');
                draw();
            }
        }

        function draw() {
            requestAnimationFrame(draw);
            if (!analyser) return;
            analyser.getByteFrequencyData(dataArray);
            canvasCtx.fillStyle = '#000';
            canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
            let x = 0;
            const barWidth = (canvas.width / dataArray.length) * 2;
            for(let i = 0; i < dataArray.length; i++) {
                let h = (dataArray[i] / 255) * canvas.height;
                // สีสะท้อนแสง ส้ม-ม่วง-น้ำเงิน
                canvasCtx.fillStyle = `hsl(${280 + (i*2)}, 100%, 50%)`;
                canvasCtx.fillRect(x, canvas.height - h, barWidth-1, h);
                x += barWidth;
            }
            updateUI();
        }

        async function loadAudio(file, key) {
            initAudio();
            document.getElementById('name'+key).innerText = "Loading: " + file.name;
            const buffer = await audioCtx.decodeAudioData(await file.arrayBuffer());
            if(key === 'A') songA = buffer; else songB = buffer;
            document.getElementById('name'+key).innerText = file.name;
        }

        function startPlaying() {
            if (!songA || !songB) return alert("โหลดเพลงก่อนครับ!");
            if (isPlaying) return;

            sourceA = audioCtx.createBufferSource(); sourceA.buffer = songA;
            gainA = audioCtx.createGain();
            sourceA.connect(gainA).connect(analyser).connect(audioCtx.destination);
            
            sourceB = audioCtx.createBufferSource(); sourceB.buffer = songB;
            gainB = audioCtx.createGain(); gainB.gain.value = 0;
            sourceB.connect(gainB).connect(analyser).connect(audioCtx.destination);

            sourceA.start(0); sourceB.start(0);
            isPlaying = true; startTime = audioCtx.currentTime;
        }

        function startCrossfade() {
            const now = audioCtx.currentTime;
            const dur = 5;
            if(current === 'A') {
                gainA.gain.linearRampToValueAtTime(1, now); gainA.gain.linearRampToValueAtTime(0, now+dur);
                gainB.gain.linearRampToValueAtTime(0, now); gainB.gain.linearRampToValueAtTime(1, now+dur);
                current = 'B';
            } else {
                gainB.gain.linearRampToValueAtTime(1, now); gainB.gain.linearRampToValueAtTime(0, now+dur);
                gainA.gain.linearRampToValueAtTime(0, now); gainA.gain.linearRampToValueAtTime(1, now+dur);
                current = 'A';
            }
        }

        function updateUI() {
            if(!isPlaying) return;
            // คำนวณเวลาที่เหลือแบบง่ายๆ (อ้างอิงจากความยาวเพลง)
            if(sourceA && songA) {
                let remA = songA.duration - (audioCtx.currentTime % songA.duration);
                document.getElementById('timeA').innerText = "-" + formatTime(remA);
                document.getElementById('barA').style.width = ((songA.duration - remA)/songA.duration*100) + "%";
            }
            if(sourceB && songB) {
                let remB = songB.duration - (audioCtx.currentTime % songB.duration);
                document.getElementById('timeB').innerText = "-" + formatTime(remB);
                document.getElementById('barB').style.width = ((songB.duration - remB)/songB.duration*100) + "%";
            }
        }

        function formatTime(sec) {
            let m = Math.floor(sec/60);
            let s = Math.floor(sec%60);
            return (m<10?'0':'')+m+":"+(s<10?'0':'')+s;
        }
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=600)

st.markdown("""
<div style='text-align: center; color: #555; font-size: 10px;'>
    อยู่นิ่งๆ ไม่เจ็บตัว | ระบบ Mix เพลงแบบ Real-time Studio
</div>
""", unsafe_allow_html=True)
