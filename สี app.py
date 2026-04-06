import streamlit as st
import streamlit.components.v1 as components

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="SYNAPSE AUDIO SYSTEM", layout="wide")

def synapse_audio_player():
    # ส่วนของ HTML/CSS/JS ที่รวมความสามารถทั้งหมด
    player_html = """
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;500&display=swap');
            
            body {
                margin: 0; padding: 0;
                font-family: 'Kanit', sans-serif;
                height: 100vh;
                display: flex; align-items: center; justify-content: center;
                /* Background แบบผสม: รูปภาพ + Rainbow Flow */
                background: linear-gradient(270deg, rgba(255,0,0,0.5), rgba(0,255,200,0.5), rgba(0,0,255,0.5));
                background-size: 600% 600%;
                animation: RainbowFlow 15s ease infinite;
                overflow: hidden;
            }

            @keyframes RainbowFlow {
                0%{background-position:0% 50%}
                50%{background-position:100% 50%}
                100%{background-position:0% 50%}
            }

            .player-card {
                background: rgba(13, 17, 23, 0.85);
                backdrop-filter: blur(10px);
                border: 2px solid #00ffc8;
                box-shadow: 0 0 30px rgba(0, 255, 200, 0.3);
                width: 100%; max-width: 450px;
                padding: 2rem; border-radius: 2rem;
                color: white; z-index: 10;
            }

            /* ปุ่มทรงหยดน้ำ Morphing */
            .liquid-btn {
                background: #00ffc8;
                color: #0d1117;
                font-weight: bold;
                border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%;
                transition: 0.5s;
                animation: liquidMorph 4s infinite alternate;
                cursor: pointer;
                padding: 12px 24px;
                border: none;
            }
            @keyframes liquidMorph {
                0% { border-radius: 30% 70% 70% 30% / 30% 30% 70% 70%; }
                100% { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }
            }
            .liquid-btn:hover { transform: scale(1.05); background: #ffffff; }

            #visualizer-canvas {
                background: rgba(0,0,0,0.3);
                border-radius: 12px;
                height: 80px; width: 100%;
                border-bottom: 2px solid #00ffc8;
            }

            .progress-container {
                height: 6px; background: #30363d;
                border-radius: 3px; cursor: pointer;
            }
            .progress-fill {
                height: 100%; background: #00ffc8;
                width: 0%; border-radius: 3px;
                box-shadow: 0 0 10px #00ffc8;
            }
            
            input[type="range"] {
                accent-color: #00ffc8;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div class="player-card">
            <div class="text-center mb-4">
                <h1 class="text-xl font-bold text-[#00ffc8]">SYNAPSE HYBRID AUDIO</h1>
                <p class="text-xs text-gray-400">"อยู่นิ่งๆ ไม่เจ็บตัว"</p>
            </div>

            <canvas id="visualizer-canvas" class="mb-4"></canvas>

            <div class="mb-4 text-center">
                <h2 id="song-title" class="text-lg font-semibold truncate">เลือกเพลงเพื่อเริ่มระบบ</h2>
                <p id="song-info" class="text-xs text-gray-400">READY TO SCAN DEVICES</p>
            </div>

            <div class="mb-4">
                <div class="progress-container" id="prog-container">
                    <div class="progress-fill" id="prog-fill"></div>
                </div>
                <div class="flex justify-between text-[10px] mt-1">
                    <span id="cur-time">0:00</span>
                    <span id="total-dur">0:00</span>
                </div>
            </div>

            <div class="flex justify-around items-center mb-6">
                <button onclick="prevTrack()" class="text-[#00ffc8]">PREV</button>
                <button id="play-pause-btn" onclick="togglePlay()" class="liquid-btn">PLAY</button>
                <button onclick="nextTrack()" class="text-[#00ffc8]">NEXT</button>
            </div>

            <div class="grid grid-cols-2 gap-4 mt-4 border-t border-gray-700 pt-4">
                <div>
                    <label class="block text-[10px] mb-1">VOLUME</label>
                    <input type="range" id="vol-slider" min="0" max="1" step="0.01" value="0.8" class="w-full">
                </div>
                <div>
                    <label class="block text-[10px] mb-1">BASS BOOST</label>
                    <input type="range" id="low-slider" min="-10" max="15" step="1" value="0" class="w-full">
                </div>
            </div>

            <div class="mt-6">
                <input type="file" id="file-input" multiple accept="audio/*" class="hidden" onchange="handleFiles(this.files)">
                <button onclick="document.getElementById('file-input').click()" class="w-full py-2 bg-gray-800 border border-[#00ffc8] rounded-lg text-xs hover:bg-gray-700">
                    + เพิ่มเพลงเข้าเพลย์ลิสต์
                </button>
            </div>
        </div>

        <audio id="main-audio"></audio>

        <script>
            let audioCtx, source, analyzer, gainNode, lowFilter;
            let tracks = [];
            let currentIdx = 0;
            const audio = document.getElementById('main-audio');
            const playBtn = document.getElementById('play-pause-btn');

            function initAudio() {
                if (audioCtx) return;
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                source = audioCtx.createMediaElementSource(audio);
                
                analyzer = audioCtx.createAnalyser();
                analyzer.fftSize = 256;

                gainNode = audioCtx.createGain();
                
                lowFilter = audioCtx.createBiquadFilter();
                lowFilter.type = 'lowshelf';
                lowFilter.frequency.value = 200;

                source.connect(lowFilter);
                lowFilter.connect(gainNode);
                gainNode.connect(analyzer);
                analyzer.connect(audioCtx.destination);

                drawVisualizer();
            }

            function handleFiles(files) {
                Array.from(files).forEach(f => {
                    tracks.push({ name: f.name, url: URL.createObjectURL(f) });
                });
                if (tracks.length > 0 && audio.src === "") loadTrack(0);
            }

            function loadTrack(idx) {
                initAudio();
                currentIdx = idx;
                audio.src = tracks[currentIdx].url;
                document.getElementById('song-title').innerText = tracks[currentIdx].name;
                audio.play();
                playBtn.innerText = "PAUSE";
            }

            function togglePlay() {
                if (!audio.src) return;
                initAudio();
                if (audio.paused) { audio.play(); playBtn.innerText = "PAUSE"; }
                else { audio.pause(); playBtn.innerText = "PLAY"; }
            }

            function nextTrack() { if(currentIdx < tracks.length-1) loadTrack(currentIdx+1); }
            function prevTrack() { if(currentIdx > 0) loadTrack(currentIdx-1); }

            // Visualizer
            function drawVisualizer() {
                const canvas = document.getElementById('visualizer-canvas');
                const ctx = canvas.getContext('2d');
                const bufferLength = analyzer.frequencyBinCount;
                const dataArray = new Uint8Array(bufferLength);

                function animate() {
                    requestAnimationFrame(animate);
                    analyzer.getByteFrequencyData(dataArray);
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    
                    let barWidth = (canvas.width / bufferLength) * 2.5;
                    let x = 0;
                    for(let i = 0; i < bufferLength; i++) {
                        let barHeight = dataArray[i] / 2;
                        ctx.fillStyle = `rgb(0, 255, ${dataArray[i]})`;
                        ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
                        x += barWidth + 1;
                    }
                }
                animate();
            }

            // Listeners
            document.getElementById('vol-slider').oninput = (e) => gainNode.gain.value = e.target.value;
            document.getElementById('low-slider').oninput = (e) => lowFilter.gain.value = e.target.value;
            
            audio.ontimeupdate = () => {
                const per = (audio.currentTime / audio.duration) * 100;
                document.getElementById('prog-fill').style.width = per + "%";
                document.getElementById('cur-time').innerText = Math.floor(audio.currentTime/60) + ":" + Math.floor(audio.currentTime%60).toString().padStart(2,'0');
            };
        </script>
    </body>
    </html>
    """
    components.html(player_html, height=700)

# รันฟังก์ชัน
st.title("🛰️ SYNAPSE COMMAND CENTER")
synapse_audio_player()
