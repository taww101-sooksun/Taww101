import streamlit as st
import os

st.set_page_config(page_title="Neon Playlist Mixer", layout="centered")

# 1. สแกนหาไฟล์เพลงในโฟลเดอร์ปัจจุบัน
music_files = [f for f in os.listdir('.') if f.endswith('.mp3')]
music_files.sort() # เรียงตามชื่อไฟล์

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .main { background-color: #000; }
    .neon-text {
        font-family: 'Orbitron', sans-serif;
        color: #fff; text-align: center;
        text-shadow: 0 0 10px #ff00de, 0 0 20px #00f3ff;
        font-size: 1.5rem; margin-bottom: 5px;
    }
    </style>
    <h1 class="neon-text">SYNAPSE MUSIC STATION</h1>
""", unsafe_allow_html=True)

# 2. ส่งรายชื่อเพลงไปให้ JavaScript ผ่าน HTML Component
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: transparent; color: white; font-family: 'Inter', sans-serif; }}
        .glass-panel {{ background: rgba(20, 20, 20, 0.9); border: 1px solid #333; box-shadow: 0 0 20px rgba(255,0,222,0.1); }}
        .visualizer-box {{ height: 120px; background: #000; border-radius: 12px; border: 1px solid #222; }}
        .playlist-scroll {{ height: 150px; overflow-y: auto; scrollbar-width: thin; }}
        .song-item {{ transition: 0.2s; cursor: pointer; border-left: 3px solid transparent; }}
        .song-item:hover {{ background: rgba(255,0,222,0.1); border-left: 3px solid #ff00de; }}
        .active-song {{ background: rgba(0,243,255,0.1); border-left: 3px solid #00f3ff; color: #00f3ff; }}
        .neon-btn {{ border: 1px solid #ff00de; color: #ff00de; font-weight: bold; font-size: 12px; }}
        .neon-btn:hover {{ background: #ff00de; color: white; box-shadow: 0 0 15px #ff00de; }}
    </style>
</head>
<body>
    <div class="max-w-md mx-auto p-4 glass-panel rounded-3xl">
        <canvas id="visualizer" class="visualizer-box w-full mb-4"></canvas>

        <div class="mb-4 text-center">
            <div id="now-playing" class="text-[11px] text-cyan-400 font-bold uppercase tracking-tighter truncate">รอเริ่มการเล่น...</div>
            <div id="timer" class="text-[24px] font-mono text-white leading-none mt-1">00:00</div>
        </div>

        <div class="playlist-scroll space-y-1 mb-4 pr-2" id="playlist">
            </div>

        <div class="grid grid-cols-2 gap-2">
            <button onclick="playNext()" class="neon-btn py-2 rounded-xl uppercase">Next Song ⏭️</button>
            <button onclick="initPlayer()" id="start-btn" class="bg-white text-black font-bold py-2 rounded-xl uppercase text-[12px]">Start System</button>
        </div>
    </div>

    <script>
        const songs = {music_files}; // รายชื่อเพลงจาก Python
        let audioCtx, analyser, currentSource, currentGain, dataArray;
        let currentIndex = 0;
        let isStarted = false;

        function initPlayer() {{
            if (isStarted) return;
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioCtx.createAnalyser();
            analyser.fftSize = 64;
            dataArray = new Uint8Array(analyser.frequencyBinCount);
            renderPlaylist();
            playSong(0);
            draw();
            isStarted = true;
            document.getElementById('start-btn').innerText = "System Online";
        }}

        function renderPlaylist() {{
            const list = document.getElementById('playlist');
            list.innerHTML = songs.map((s, i) => `
                <div class="song-item p-2 text-[10px] flex justify-between" id="song-${{i}}" onclick="playSong(${{i}})">
                    <span>${{i+1}}. ${{s}}</span>
                </div>
            `).join('');
        }}

        async function playSong(index) {{
            if (!audioCtx) return;
            if (currentSource) currentSource.stop();
            
            currentIndex = index;
            const songName = songs[index];
            document.getElementById('now-playing').innerText = "Playing: " + songName;
            
            // Highlight playlist
            document.querySelectorAll('.song-item').forEach(el => el.classList.remove('active-song'));
            document.getElementById('song-'+index).classList.add('active-song');

            // Load file
            const response = await fetch("./" + songName);
            const arrayBuffer = await response.arrayBuffer();
            const audioBuffer = await audioCtx.decodeAudioData(arrayBuffer);

            currentSource = audioCtx.createBufferSource();
            currentSource.buffer = audioBuffer;
            currentGain = audioCtx.createGain();
            
            currentSource.connect(currentGain).connect(analyser).connect(audioCtx.destination);
            currentSource.start(0);

            // เมื่อเพลงจบ ให้เล่นเพลงถัดไปอัตโนมัติ
            currentSource.onended = () => {{
                playNext();
            }};
        }}

        function playNext() {{
            let nextIndex = (currentIndex + 1) % songs.length;
            playSong(nextIndex);
        }}

        function draw() {{
            requestAnimationFrame(draw);
            analyser.getByteFrequencyData(dataArray);
            const canvas = document.getElementById('visualizer');
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            let x = 0;
            const bWidth = (canvas.width / dataArray.length) * 2;
            for(let i=0; i<dataArray.length; i++) {{
                let h = (dataArray[i]/255) * canvas.height;
                ctx.fillStyle = `hsl(${{280 + i*5}}, 100%, 50%)`;
                ctx.shadowBlur = 10;
                ctx.shadowColor = ctx.fillStyle;
                ctx.fillRect(x, canvas.height-h, bWidth-2, h);
                x += bWidth;
            }}

            // อัปเดตเวลาถอยหลัง
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

st.components.v1.html(html_code, height=580)

if not music_files:
    st.warning("⚠️ ไม่พบไฟล์ .mp3 ในโฟลเดอร์นี้ครับอาจารย์ ลองเช็คดูว่าวางไฟล์ถูกที่หรือยัง")
else:
    st.success(f"📂 ตรวจพบเพลงในคลังทั้งหมด {len(music_files)} เพลง พร้อมลุยครับ!")
