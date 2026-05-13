import streamlit as st
import base64
import os

# --- ตั้งค่าพื้นฐาน ---
st.set_page_config(page_title="Synapse Neon Mixer", layout="centered")

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

def get_audio_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return None

# สแกนหาเพลง
all_songs = [f for f in os.listdir('.') if f.endswith('.mp3')]
all_songs = sorted(all_songs)

# ดึงข้อมูลโลโก้
logo_b64 = get_base64_image("logo1.png")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #000; }
    
    /* ข้อความวิ้งๆ Neon Flicker */
    .neon-text {
        font-family: 'Orbitron', sans-serif;
        color: #fff;
        text-align: center;
        font-size: 1.8rem;
        letter-spacing: 5px;
        text-shadow: 0 0 10px #ff00de, 0 0 20px #ff00de, 0 0 40px #00f3ff;
        animation: flicker 1.5s infinite alternate;
        margin-bottom: 20px;
    }

    @keyframes flicker {
        0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% {
            opacity: 1;
            text-shadow: 0 0 10px #ff00de, 0 0 20px #ff00de, 0 0 40px #00f3ff;
        }
        20%, 24%, 55% {
            opacity: 0.5;
            text-shadow: none;
        }
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="neon-text">SYNAPSE MIXER</div>', unsafe_allow_html=True)

# ส่วนเลือกเพลง
if all_songs:
    col1, col2 = st.columns(2)
    with col1: sA = st.selectbox("DECK A", all_songs, key="sA")
    with col2: sB = st.selectbox("DECK B", all_songs, key="sB")
    
    audio_a = get_audio_base64(sA)
    audio_b = get_audio_base64(sB)
else:
    st.error("ไม่พบไฟล์ .mp3 ในโฟลเดอร์")
    st.stop()

# --- HTML/JS Engine (ฉบับแก้ Hex Color Error) ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* ต้องใช้ double braces {{ }} ล้อมรอบ CSS ทั้งหมด */
        body {{ background: transparent; color: white; font-family: 'Orbitron', sans-serif; overflow: hidden; }}
        .neon-card {{ 
            border: 2px solid #333; 
            background: rgba(10,10,10,0.95); 
            box-shadow: 0 0 20px rgba(255,0,222,0.3);
            position: relative;
        }}
        .logo-box {{
            width: 60px; height: 60px;
            margin: 0 auto 15px auto;
            background: url('data:image/png;base64,{logo_b64}') no-repeat center;
            background-size: contain;
            filter: drop-shadow(0 0 8px #00f3ff);
        }}
        .visualizer {{ height: 100px; background: #000; border-radius: 10px; border: 1px solid #222; }}
        .deck {{ padding: 12px; border-radius: 10px; border: 1px solid #222; margin-top: 10px; transition: 0.3s; }}
        .active-a {{ border-color: #ff00de; box-shadow: 0 0 10px #ff00de; }}
        .active-b {{ border-color: #00f3ff; box-shadow: 0 0 10px #00f3ff; }}
        .btn-mix {{
            background: linear-gradient(45deg, #ff00de, #00f3ff);
            width: 100%; padding: 15px; border-radius: 10px; font-weight: bold; margin-top: 15px; cursor: pointer;
        }}
        .progress {{ height: 4px; background: #222; margin-top: 5px; }}
        .bar {{ height: 100%; width: 0%; background: #ff00de; }}
    </style>
</head>
<body>
    <div class="max-w-md mx-auto p-6 neon-card rounded-3xl text-center">
        <div class="logo-box"></div>
        <canvas id="scope" class="visualizer w-full"></canvas>

        <div id="deckA" class="deck text-left">
            <div class="flex justify-between text-[10px]">
                <span style="color:#ff00de">DECK A</span>
                <span id="tA">00:00</span>
            </div>
            <div class="text-[11px] truncate">{sA}</div>
            <div class="progress"><div id="barA" class="bar"></div></div>
        </div>

        <div id="deckB" class="deck text-left">
            <div class="flex justify-between text-[10px]">
                <span style="color:#00f3ff">DECK B</span>
                <span id="tB">00:00</span>
            </div>
            <div class="text-[11px] truncate">{sB}</div>
            <div class="progress"><div id="barB" class="bar" style="background:#00f3ff"></div></div>
        </div>

        <button onclick="start()" class="btn-mix">🚀 START AUTO-MIX</button>
        <div id="status" class="text-[9px] mt-4 text-gray-500 uppercase">System Ready</div>
    </div>

    <script>
        let ctx, analyser, songA, songB, gA, gB, srcA, srcB;
        let isPlaying = false, active = 'A', data;

        async function toBuf(b64) {{
            const r = await fetch('data:audio/mp3;base64,' + b64);
            const ab = await r.arrayBuffer();
            return await ctx.decodeAudioData(ab);
        }}

        <script>
        let ctx, analyser, songA, songB, gA, gB, srcA, srcB;
        let isPlaying = false, active = 'A', data;

        async function toBuf(b64) {
            const r = await fetch('data:audio/mp3;base64,' + b64);
            const ab = await r.arrayBuffer();
            return await ctx.decodeAudioData(ab);
        }

        async function start() {
            if(isPlaying) return;
            try {
                document.getElementById('status').innerText = "BOOTING ENGINE...";
                ctx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = ctx.createAnalyser();
                data = new Uint8Array(analyser.frequencyBinCount);

                // โหลดเพลงเตรียมไว้ (แต่ยังไม่สั่งเล่น)
                songA = await toBuf('{audio_a}');
                songB = await toBuf('{audio_b}');

                // เริ่มเล่นแค่เพลง A ก่อน
                playDeckA();
                
                isPlaying = true;
                document.getElementById('status').innerText = "PLAYING: DECK A";
                render();
            } catch(e) {
                alert("Error: " + e);
            }
        }

        function playDeckA() {
            active = 'A';
            srcA = ctx.createBufferSource();
            srcA.buffer = songA;
            gA = ctx.createGain();
            srcA.connect(gA).connect(analyser).connect(ctx.destination);
            gA.gain.value = 1; // ดังปกติ
            srcA.start(0);
            document.getElementById('deckA').classList.add('active-a');
            document.getElementById('deckB').classList.remove('active-b');
        }

        function playDeckB() {
            active = 'B';
            srcB = ctx.createBufferSource();
            srcB.buffer = songB;
            gB = ctx.createGain();
            srcB.connect(gB).connect(analyser).connect(ctx.destination);
            gB.gain.value = 0; // เริ่มที่เงียบๆ
            srcB.start(0);
            
            // ค่อยๆ เร่งเสียง B ขึ้นมาใน 5 วินาที
            gB.gain.linearRampToValueAtTime(1, ctx.currentTime + 5);
            document.getElementById('deckB').classList.add('active-b');
            document.getElementById('deckA').classList.remove('active-a');
        }

        function render() {
            requestAnimationFrame(render);
            analyser.getByteFrequencyData(data);
            const can = document.getElementById('scope');
            const c = can.getContext('2d');
            c.clearRect(0,0,can.width,can.height);
            for(let i=0; i<data.length; i++) {
                c.fillStyle = 'hsl(' + (i*2 + (active=='A'?300:190)) + ', 100%, 50%)';
                c.fillRect(i*3, can.height-(data[i]/2.5), 2, data[i]/2.5);
            }
            updateProgress();
        }

        function updateProgress() {
            // เช็คเพลง A
            if (srcA && active == 'A') {
                let curr = (ctx.currentTime - srcA.startTime || 0) % songA.duration; // แก้จุดนี้เพื่อหาเวลาเล่นจริง
                // เนื่องจาก AudioBufferSourceNode ไม่มี property 'currentTime' โดยตรง 
                // เราจะใช้วิธีคำนวณเวลาที่ผ่านไปแทน (แบบง่ายๆ)
                let rem = songA.duration - (ctx.currentTime % songA.duration); 
                
                document.getElementById('tA').innerText = Math.floor(rem/60) + ":" + Math.floor(rem%60).toString().padStart(2,'0');
                document.getElementById('barA').style.width = ((songA.duration - rem)/songA.duration*100) + "%";

                // ถ้าเหลือ 8 วินาที ให้เริ่มเล่นเพลง B
                if (rem < 8 && active == 'A') {
                    active = 'MIXING_TO_B'; 
                    gA.gain.linearRampToValueAtTime(0, ctx.currentTime + 5); // ค่อยๆ หรี่ A
                    playDeckB(); // เริ่มเล่น B
                    document.getElementById('status').innerText = "CROSSFADING TO B...";
                }
            }
            
            // เช็คเพลง B (ถ้าเล่นอยู่)
            if (srcB && active == 'B') {
                let rem = songB.duration - (ctx.currentTime % songB.duration);
                document.getElementById('tB').innerText = Math.floor(rem/60) + ":" + Math.floor(rem%60).toString().padStart(2,'0');
                document.getElementById('barB').style.width = ((songB.duration - rem)/songB.duration*100) + "%";
            }
        }
    </script>
