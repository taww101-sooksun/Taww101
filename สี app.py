import streamlit as st

st.set_page_config(page_title="Neon Auto-Studio", layout="centered")

# ลิงก์เพลงจาก GitHub (อาจารย์เปลี่ยน URL ตรงนี้เป็นเพลงของอาจารย์เองได้เลย)
SONG_A_URL = "https://www.sample-videos.com/audio/mp3/wave.mp3" 
SONG_B_URL = "https://www.sample-videos.com/audio/mp3/crowd-cheer.mp3"

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .main { background-color: #000; }
    .neon-title {
        font-family: 'Orbitron', sans-serif;
        color: #fff; text-align: center;
        text-shadow: 0 0 10px #00f3ff, 0 0 20px #00f3ff;
        font-size: 1.8rem; margin-bottom: 10px;
    }
    </style>
    <h1 class="neon-title">AUTO NEON MIXER</h1>
""", unsafe_allow_html=True)

html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: transparent; color: white; font-family: 'Inter', sans-serif; overflow: hidden; }}
        .neon-card {{ border: 1px solid #333; background: #0a0a0a; box-shadow: 0 0 20px rgba(0,243,255,0.1); }}
        .visualizer-box {{ height: 120px; background: #000; border-radius: 8px; border: 1px solid #222; }}
        .btn-neon {{ transition: 0.3s; font-weight: bold; letter-spacing: 1px; }}
        .active-a {{ border: 2px solid #ff00de; color: #ff00de; text-shadow: 0 0 5px #ff00de; }}
        .active-b {{ border: 2px solid #00f3ff; color: #00f3ff; text-shadow: 0 0 5px #00f3ff; }}
        .prog-bar {{ height: 4px; background: #111; border-radius: 2px; }}
        .prog-fill {{ height: 100%; width: 0%; transition: width 0.1s; }}
    </style>
</head>
<body>
    <div class="max-w-md mx-auto p-5 neon-card rounded-3xl">
        <canvas id="visualizer" class="visualizer-box w-full mb-4"></canvas>

        <div class="space-y-4">
            <div class="p-3 bg-gray-900/80 rounded-xl border border-pink-500/20">
                <div class="flex justify-between text-[10px] mb-1">
                    <span class="text-pink-500 font-bold">DECK A (GITHUB)</span>
                    <span id="timeA" class="font-mono text-gray-500">READY</span>
                </div>
                <div class="prog-bar"><div id="barA" class="prog-fill" style="background: #ff00de;"></div></div>
            </div>

            <div class="p-3 bg-gray-900/80 rounded-xl border border-cyan-500/20">
                <div class="flex justify-between text-[10px] mb-1">
                    <span class="text-cyan-400 font-bold">DECK B (GITHUB)</span>
                    <span id="timeB" class="font-mono text-gray-500">READY</span>
                </div>
                <div class="prog-bar"><div id="barB" class="prog-fill" style="background: #00f3ff;"></div></div>
            </div>
        </div>

        <div class="grid grid-cols-1 gap-3 mt-6">
            <button onclick="startAutoPlay()" id="master-btn" class="btn-neon active-a py-3 rounded-2xl uppercase text-sm">
                ⚡ Launch Auto-Mix
            </button>
            <div id="status" class="text-[9px] text-center text-gray-600 tracking-widest mt-2 uppercase">ระบบเชื่อมต่อคลังเพลง GitHub แล้ว</div>
        </div>
    </div>

    <script>
        let audioCtx, analyser, songA, songB, sourceA, sourceB, gainA, gainB;
        let isPlaying = false, dataArray;
        const songAUrl = "{SONG_A_URL}";
        const songBUrl = "{SONG_B_URL}";

        async function init() {{
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioCtx.createAnalyser();
            analyser.fftSize = 64;
            dataArray = new Uint8Array(analyser.frequencyBinCount);
            draw();
        }}

        async function loadSong(url) {{
            const res = await fetch(url);
            const arrayBuffer = await res.arrayBuffer();
            return await audioCtx.decodeAudioData(arrayBuffer);
        }}

        function draw() {{
            requestAnimationFrame(draw);
            if(!analyser) return;
            analyser.getByteFrequencyData(dataArray);
            const canvas = document.getElementById('visualizer');
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            let x = 0;
            const bWidth = (canvas.width / dataArray.length) * 2;
            for(let i=0; i<dataArray.length; i++) {{
                let h = (dataArray[i]/255) * canvas.height;
                ctx.fillStyle = `hsl(${{180 + i*5}}, 100%, 50%)`;
                ctx.fillRect(x, canvas.height-h, bWidth-2, h);
                x += bWidth;
            }}
            updateUI();
        }}

        async function startAutoPlay() {{
            if(isPlaying) return;
            await init();
            document.getElementById('status').innerText = "FETCHING SONGS FROM GITHUB...";
            
            songA = await loadSong(songAUrl);
            songB = await loadSong(songBUrl);

            sourceA = audioCtx.createBufferSource(); sourceA.buffer = songA;
            gainA = audioCtx.createGain();
            sourceA.connect(gainA).connect(analyser).connect(audioCtx.destination);

            sourceB = audioCtx.createBufferSource(); sourceB.buffer = songB;
            gainB = audioCtx.createGain(); gainB.gain.value = 0;
            sourceB.connect(gainB).connect(analyser).connect(audioCtx.destination);

            sourceA.start(0); sourceB.start(0);
            isPlaying = true;
            document.getElementById('status').innerText = "AUTO-MIX ACTIVE";

            // เช็คการจบเพลงเพื่อ Auto-Crossfade
            setInterval(() => {{
                let remA = songA.duration - (audioCtx.currentTime % songA.duration);
                if(remA < 10 && gainA.gain.value > 0.9) {{
                    autoFade();
                }}
            }}, 1000);
        }}

        function autoFade() {{
            const now = audioCtx.currentTime;
            gainA.gain.linearRampToValueAtTime(1, now);
            gainA.gain.linearRampToValueAtTime(0, now + 8);
            gainB.gain.linearRampToValueAtTime(0, now);
            gainB.gain.linearRampToValueAtTime(1, now + 8);
            document.getElementById('status').innerText = "CROSSFADING...";
        }}

        function updateUI() {{
            if(!isPlaying) return;
            let timeA = songA.duration - (audioCtx.currentTime % songA.duration);
            document.getElementById('timeA').innerText = "-" + Math.floor(timeA) + "s";
            document.getElementById('barA').style.width = ((songA.duration-timeA)/songA.duration*100) + "%";
            
            let timeB = songB.duration - (audioCtx.currentTime % songB.duration);
            document.getElementById('timeB').innerText = "-" + Math.floor(timeB) + "s";
            document.getElementById('barB').style.width = ((songB.duration-timeB)/songB.duration*100) + "%";
        }}
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=550)
