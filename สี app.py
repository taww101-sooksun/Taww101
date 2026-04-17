import streamlit as st
import os

st.set_page_config(page_title="Neon Synapse Station", layout="centered")

# สแกนเพลง
music_files = [f for f in os.listdir('.') if f.endswith('.mp3')]
music_files.sort()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .main { background-color: #000; }
    .neon-header {
        font-family: 'Orbitron', sans-serif;
        color: #fff; text-align: center;
        text-shadow: 0 0 10px #ff00de, 0 0 20px #ff00de, 0 0 30px #00f3ff;
        font-size: 1.8rem; margin: 10px 0;
    }
    </style>
    <h1 class="neon-header">SYNAPSE NEON STATION</h1>
""", unsafe_allow_html=True)

html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: transparent; color: white; font-family: 'Inter', sans-serif; }}
        .neon-card {{ background: rgba(10, 10, 10, 0.95); border: 2px solid #333; box-shadow: 0 0 30px rgba(255, 0, 222, 0.2); }}
        .visualizer-box {{ height: 140px; background: #000; border-radius: 15px; border: 1px solid #444; }}
        .playlist-area {{ height: 180px; overflow-y: auto; scrollbar-color: #ff00de #111; }}
        .song-item {{ transition: 0.3s; cursor: pointer; border-left: 4px solid #222; margin-bottom: 2px; }}
        .song-item:hover {{ background: rgba(255, 0, 222, 0.2); border-left: 4px solid #ff00de; }}
        .active-song {{ background: rgba(0, 243, 255, 0.15); border-left: 4px solid #00f3ff; color: #00f3ff; font-weight: bold; }}
        
        /* ปุ่มสไตล์ Neon สะท้อนแสง */
        .btn-glow {{ 
            background: #000; color: #fff; border: 2px solid #ff00de;
            box-shadow: 0 0 10px #ff00de, inset 0 0 5px #ff00de;
            text-shadow: 0 0 5px #fff; transition: 0.3s;
        }}
        .btn-glow:hover {{ background: #ff00de; box-shadow: 0 0 25px #ff00de; }}
        .btn-next {{ border-color: #00f3ff; box-shadow: 0 0 10px #00f3ff; color: #00f3ff; }}
        .btn-next:hover {{ background: #00f3ff; color: #000; box-shadow: 0 0 25px #00f3ff; }}
    </style>
</head>
<body>
    <div class="max-w-md mx-auto p-5 neon-card rounded-[30px]">
        <canvas id="visualizer" class="visualizer-box w-full mb-5"></canvas>

        <div class="text-center mb-5">
            <div id="status" class="text-[10px] tracking-[4px] text-pink-500 uppercase font-bold mb-1">System Standby</div>
            <div id="now-playing" class="text-xs text-gray-300 truncate px-4 mb-2">กรุณากด START เพื่อโหลดเพลง</div>
            <div id="timer" class="text-3xl font-mono text-white text-shadow-[0_0_10px_#fff]">00:00</div>
        </div>

        <div class="playlist-area mb-5 pr-2" id="playlist"></div>

        <div class="grid grid-cols-2 gap-4">
            <button onclick="unlockAudio()" id="start-btn" class="btn-glow py-3 rounded-2xl font-bold uppercase tracking-widest text-xs">Start System</button>
            <button onclick="playNext()" class="btn-glow btn-next py-3 rounded-2xl font-bold uppercase tracking-widest text-xs">Next Track ⏭️</button>
        </div>
    </div>

    <script>
        const songs = {music_files};
        let audioCtx, analyser, currentSource, dataArray;
        let currentIndex = 0;
        let isUnlocked = false;

        // ปลดล็อกระบบเสียง
        async function unlockAudio() {{
            if (!audioCtx) {{
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = audioCtx.createAnalyser();
                analyser.fftSize = 128; // เพิ่มความละเอียดกราฟ
                dataArray = new Uint8Array(analyser.frequencyBinCount);
                renderPlaylist();
                draw();
            }}
            if (audioCtx.state === 'suspended') {{
                await audioCtx.resume();
            }}
            isUnlocked = true;
            document.getElementById('start-btn').style.display = 'none';
            document.getElementById('status').innerText = "System Online";
            playSong(0);
        }}

        function renderPlaylist() {{
            const list = document.getElementById('playlist');
            list.innerHTML = songs.map((s, i) => `
                <div class="song-item p-3 text-[11px] flex justify-between bg-white/5 rounded-lg" id="song-${{i}}" onclick="playSong(${{i}})">
                    <span class="truncate pr-2">${{i+1}}. ${{s}}</span>
                    <span class="text-pink-500">PLAY</span>
                </div>
            `).join('');
        }}

        async function playSong(index) {{
            if (!isUnlocked) return;
            if (currentSource) currentSource.stop();
            
            currentIndex = index;
            document.getElementById('now-playing').innerText = songs[index];
            document.getElementById('status').innerText = "Now Playing";

            document.querySelectorAll('.song-item').forEach(el => el.classList.remove('active-song'));
            document.getElementById('song-'+index).classList.add('active-song');

            try {{
                const response = await fetch("./" + encodeURIComponent(songs[index]));
                const arrayBuffer = await response.arrayBuffer();
                const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);

                currentSource = audioCtx.createBufferSource();
                currentSource.buffer = audioBuffer;
                currentSource.connect(analyser).connect(audioCtx.destination);
                currentSource.start(0);

                currentSource.onended = () => {{
                    playNext();
                }};
            }} catch(e) {{
                console.error(e);
                document.getElementById('status').innerText = "Load Error";
            }}
        }}

        function playNext() {{
            playSong((currentIndex + 1) % songs.length);
        }}

        function draw() {{
            requestAnimationFrame(draw);
            analyser.getByteFrequencyData(dataArray);
            const canvas = document.getElementById('visualizer');
            const ctx = canvas.getContext('2d');
            
            // ล้างจอแบบ Fade เพื่อให้เกิดเงาตาม (Motion Blur)
            ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            const bWidth = (canvas.width / dataArray.length) * 2;
            let x = 0;

            for(let i=0; i<dataArray.length; i++) {{
                let h = (dataArray[i]/255) * canvas.height;
                
                // สีสะท้อนแสง Neon (ไล่เฉด ส้ม-ม่วง-น้ำเงิน-เขียว)
                const hue = i * 4;
                ctx.fillStyle = `hsl(${{hue + 280}}, 100%, 50%)`;
                
                // เพิ่มแสง Glow ให้แท่งกราฟ
                ctx.shadowBlur = 15;
                ctx.shadowColor = `hsl(${{hue + 280}}, 100%, 50%)`;
                
                ctx.fillRect(x, canvas.height - h, bWidth - 2, h);
                x += bWidth;
            }}

            // ตัวเลขเวลา
            if(currentSource && currentSource.buffer) {{
                let currTime = audioCtx.currentTime % currentSource.buffer.duration;
                let rem = currentSource.buffer.duration - currTime;
                let m = Math.floor(rem/60);
                let s = Math.floor(rem%60);
                document.getElementById('timer').innerText = (m<10?'0':'')+m+":"+(s<10?'0':'')+s;
            }}
        }}
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=620)
