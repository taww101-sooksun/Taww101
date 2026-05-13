import streamlit as st
import base64
import os
import random

# --- 1. ตั้งค่าพื้นฐาน ---
st.set_page_config(page_title="Synapse Auto-Mixer", layout="centered")

# ลบเมนูและเครดิต Streamlit ออก (ลับติ้ง)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #000; }
    </style>
    """, unsafe_allow_html=True)

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

# สแกนหาเพลงทั้งหมดในโฟลเดอร์
all_songs = [f for f in os.listdir('.') if f.endswith('.mp3')]
logo_b64 = get_base64_image("logo1.png")

if not all_songs:
    st.error("หาเพลง .mp3 ไม่เจอเลยเพื่อน")
    st.stop()

# --- 2. ฟังก์ชันเตรียมข้อมูลส่งไป JavaScript ---
# แปลงเพลงทั้งหมดเป็น Dictionary เพื่อให้ JS เลือกเพลงเองได้
song_data = {}
for s in all_songs:
    with open(s, "rb") as f:
        song_data[s] = base64.b64encode(f.read()).decode()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .neon-text {
        font-family: 'Orbitron', sans-serif;
        color: #fff; text-align: center; font-size: 1.5rem;
        text-shadow: 0 0 10px #ff00de, 0 0 20px #00f3ff;
        margin-bottom: 10px;
    }
    </style>
    <div class="neon-text">SYNAPSE AUTO-STREAM</div>
    """, unsafe_allow_html=True)

# --- 3. HTML/JS Engine (ระบบ Auto-Next) ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: transparent; color: white; font-family: 'Orbitron', sans-serif; }}
        .neon-card {{ border: 2px solid #333; background: #0a0a0a; box-shadow: 0 0 20px rgba(255,0,222,0.2); }}
        .visualizer {{ height: 80px; background: #000; border-radius: 8px; }}
        .status-box {{ font-size: 10px; color: #00f3ff; margin-bottom: 5px; }}
    </style>
</head>
<body>
    <div class="max-w-md mx-auto p-5 neon-card rounded-2xl text-center">
        <div style="width:50px; height:50px; margin:0 auto 10px; background:url('data:image/png;base64,{logo_b64}') center/contain no-repeat;"></div>
        <div id="status" class="status-box">READY TO PLAY</div>
        <canvas id="scope" class="visualizer w-full mb-4"></canvas>
        
        <div class="text-left text-[11px] bg-black p-3 rounded-lg border border-gray-800">
            <div id="song-name" class="truncate text-pink-500">Waiting for start...</div>
            <div class="w-full bg-gray-900 h-1 mt-2"><div id="bar" class="h-full bg-pink-500 w-0"></div></div>
            <div id="time" class="text-right mt-1 text-[9px]">00:00</div>
        </div>

        <button onclick="bootEngine()" class="w-full bg-gradient-to-r from-pink-600 to-cyan-600 py-3 rounded-lg font-bold mt-4">
            START AUTO-PLAY
        </button>
    </div>

    <script>
        const songs = {song_data}; // ข้อมูลเพลงทั้งหมด
        const songNames = Object.keys(songs);
        let ctx, analyser, data, currentSrc, currentBuf, t0;

        async function bootEngine() {{
            if(ctx) return;
            ctx = new (window.AudioContext || window.webkitAudioContext)();
            analyser = ctx.createAnalyser();
            data = new Uint8Array(analyser.frequencyBinCount);
            playNext();
            render();
        }}

        async function playNext() {{
            const name = songNames[Math.floor(Math.random() * songNames.length)];
            document.getElementById('status').innerText = "LOADING NEXT...";
            document.getElementById('song-name').innerText = "NEXT: " + name;

            const r = await fetch('data:audio/mp3;base64,' + songs[name]);
            const ab = await r.arrayBuffer();
            const buf = await ctx.decodeAudioData(ab);

            if(currentSrc) {{ currentSrc.stop(); }}

            const src = ctx.createBufferSource();
            src.buffer = buf;
            src.connect(analyser).connect(ctx.destination);
            src.start(0);
            
            currentSrc = src;
            currentBuf = buf;
            t0 = ctx.currentTime;
            
            document.getElementById('status').innerText = "NOW PLAYING";
            document.getElementById('song-name').innerText = name;

            // เมื่อเพลงจบ ให้เรียก playNext ใหม่เองอัตโนมัติ
            src.onended = () => {{ playNext(); }};
        }}

        function render() {{
            requestAnimationFrame(render);
            analyser.getByteFrequencyData(data);
            const can = document.getElementById('scope');
            const c = can.getContext('2d');
            c.clearRect(0,0,can.width,can.height);
            for(let i=0; i<data.length; i+=5) {{
                c.fillStyle = '#ff00de';
                c.fillRect(i, can.height - data[i]/3, 3, data[i]/3);
            }}
            if(currentBuf) {{
                let elapsed = ctx.currentTime - t0;
                let pct = (elapsed / currentBuf.duration) * 100;
                document.getElementById('bar').style.width = pct + "%";
                let rem = Math.max(0, currentBuf.duration - elapsed);
                document.getElementById('time').innerText = Math.floor(rem/60) + ":" + Math.floor(rem%60).toString().padStart(2,'0');
            }}
        }}
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=450)
st.markdown("<div style='text-align:center; color:#333; font-size:10px;'>อยู่นิ่งๆ ไม่เจ็บตัว | AUTO-PLAY MODE</div>", unsafe_allow_html=True)
