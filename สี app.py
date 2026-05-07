import streamlit as st
import base64
import os
import random

# ==========================================
# ส่วนที่ 1: Python กวาดหาเพลงทั้งหมดในเครื่อง
# ==========================================

st.set_page_config(page_title="Synapse Auto-Scanner", layout="centered")

# หาไฟล์ .mp3 ทั้งหมดในโฟลเดอร์เดียวกับไฟล์ .py
music_folder = "." # หรือใส่ path โฟลเดอร์เพลงของคุณ
all_songs = [f for f in os.listdir(music_folder) if f.endswith(".mp3")]

# สุ่มเลือกเพลงมา 2 เพลงแรกเพื่อเริ่มระบบ (หรือจะให้ JS จัดการต่อก็ได้)
if len(all_songs) < 2:
    st.warning("อาจารย์ครับ! หาไฟล์ .mp3 ไม่เจอ (วางไว้ที่เดียวกับไฟล์ .py นะ)")
    song_list = ["No Song Found", "No Song Found"]
else:
    song_list = all_songs

def get_base64_audio(file_name):
    try:
        with open(os.path.join(music_folder, file_name), "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return ""

# ดึงข้อมูลเพลงเริ่มต้น 2 เพลง (เพื่อความเร็วในการโหลดครั้งแรก)
# ส่วนที่เหลือเราจะให้ JS สามารถเลือกสุ่มได้จากรายชื่อ
init_a_data = get_base64_audio(song_list[0]) if len(all_songs) >= 1 else ""
init_b_data = get_base64_audio(song_list[1]) if len(all_songs) >= 2 else ""

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_base64 = get_base64_image("logo1.png")
logo_html_link = f"data:image/png;base64,{logo_base64}" if logo_base64 else ""

# CSS ปรับสีให้นวล (Muted Neon)
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Prompt:wght@700&display=swap');
    header {{visibility: hidden;}} footer {{visibility: hidden;}} #MainMenu {{visibility: hidden;}}
    .stApp {{ background: #080808; }}

    .marquee-container {{
        position: fixed; width: 100%; z-index: 1000;
        background: rgba(0, 0, 0, 0.9);
        font-family: 'Prompt', sans-serif; font-size: 16px;
        white-space: nowrap; overflow: hidden;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }}
    .top-m {{ top: 0; }} .bottom-m {{ bottom: 0; }}
    .marquee-text {{ display: inline-block; padding-left: 100%; animation: marquee 30s linear infinite; color: #666; }}
    @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}

    .block-container::before {{
        content: ""; position: absolute; top: 50px; left: 50%;
        transform: translateX(-50%); width: 80px; height: 80px;
        background-image: url("{logo_html_link}"); background-size: contain;
        z-index: 99; opacity: 0.8;
    }}
    .neon-title {{
        font-family: 'Orbitron', sans-serif; color: #fff;
        text-align: center; font-size: 1.4rem; margin-top: 140px;
        letter-spacing: 10px; opacity: 0.9;
    }}
    </style>
    <div class="marquee-container top-m">
        <div class="marquee-text">อยู่นิ่งๆ ไม่เจ็บตัว ⚡ DETECTED {len(all_songs)} TRACKS ⚡ SYNAPSE AUTO-SCANNER ⚡</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="neon-title">SYNAPSE AUTO-MIX</h1>', unsafe_allow_html=True)

# ==========================================
# ส่วนที่ 2: HTML/JS - ระบบจัดการ Playlist 70 เพลง
# ==========================================

html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: transparent; color: #888; font-family: 'Orbitron', sans-serif; overflow: hidden; }}
        .neon-card {{ background: rgba(20,20,20,0.95); border: 1px solid #333; }}
        .visualizer-box {{ height: 160px; background: #000; border-radius: 4px; }}
        .deck {{ background: rgba(255,255,255,0.02); border: 1px solid transparent; transition: 0.5s; }}
        .deck-active {{ border-color: #00f3ff; background: rgba(0,243,255,0.02); color: #00f3ff; }}
        .btn-start {{ border: 1px solid #444; padding: 10px; font-weight: bold; width: 100%; transition: 0.3s; }}
        .btn-start:hover {{ border-color: #fff; color: #fff; }}
    </style>
</head>
<body>
    <div class="max-w-md mx-auto p-5 neon-card rounded-2xl">
        <canvas id="scope" class="visualizer-box w-full mb-5"></canvas>

        <div id="cardA" class="deck p-4 mb-3 rounded-lg">
            <div class="flex justify-between text-[10px] mb-1">
                <span>DECK A</span><span id="timeA">00:00</span>
            </div>
            <div id="nameA" class="text-[11px] truncate font-bold text-gray-400">{song_list[0] if len(song_list)>0 else "Empty"}</div>
            <div class="h-1 bg-gray-800 mt-3"><div id="barA" class="h-full bg-blue-500 shadow-[0_0_10px_#00f3ff]" style="width:0%"></div></div>
        </div>

        <div id="cardB" class="deck p-4 mb-4 rounded-lg">
            <div class="flex justify-between text-[10px] mb-1">
                <span>DECK B</span><span id="timeB">00:00</span>
            </div>
            <div id="nameB" class="text-[11px] truncate font-bold text-gray-400">{song_list[1] if len(song_list)>1 else "Empty"}</div>
            <div class="h-1 bg-gray-800 mt-3"><div id="barB" class="h-full bg-pink-500 shadow-[0_0_10px_#ff00de]" style="width:0%"></div></div>
        </div>

        <button onclick="startMix()" class="btn-start">INITIALIZE AUTO-MIX</button>
        <div class="text-[9px] text-center mt-3 tracking-widest opacity-30">SCANNER V7.0 | TOTAL {len(all_songs)} FILES</div>
    </div>

    <script>
        let ctx, analyser, songA, songB, gainA, gainB, active = 'A', isPlaying = false, data;
        const rawA = "{init_a_data}";
        const rawB = "{init_b_data}";

        function init() {{
            if (!ctx) {{
                ctx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = ctx.createAnalyser();
                analyser.fftSize = 128;
                data = new Uint8Array(analyser.frequencyBinCount);
                render();
            }}
        }}

        function base64ToArrayBuffer(base64) {{
            let b = window.atob(base64), bytes = new Uint8Array(b.length);
            for (let i=0; i<b.length; i++) bytes[i] = b.charCodeAt(i);
            return bytes.buffer;
        }}

        async function loadInitial() {{
            init();
            if(rawA) songA = await ctx.decodeAudioData(base64ToArrayBuffer(rawA));
            if(rawB) songB = await ctx.decodeAudioData(base64ToArrayBuffer(rawB));
        }}

        function render() {{
            requestAnimationFrame(render);
            if(!analyser) return;
            analyser.getByteFrequencyData(data);
            const can = document.getElementById('scope'), c = can.getContext('2d');
            c.fillStyle = 'rgba(0,0,0,0.2)';
            c.fillRect(0,0,can.width,can.height);
            
            let bw = (can.width / data.length) * 2;
            for(let i=0; i<data.length; i++) {{
                let h = (data[i]/255) * can.height * 0.7;
                let hue = (i * 20 + Date.now()/100) % 360;
                // ปรับสีให้นวลขึ้นด้วยการลด Saturation (70%) และเพิ่มความโปร่งแสง
                c.fillStyle = `hsla(${{hue}}, 60%, 50%, 0.7)`;
                c.shadowBlur = data[i]/20;
                c.shadowColor = `hsla(${{hue}}, 60%, 50%, 0.4)`;
                c.fillRect(i*bw, can.height - h, bw-2, h);
            }}
            updateEngine();
        }}

        function startMix() {{
            if(!songA || !songB) return alert("MUSIC SCANNING...");
            if(isPlaying) return;
            const sA = ctx.createBufferSource(); sA.buffer = songA;
            gainA = ctx.createGain(); sA.connect(gainA).connect(analyser).connect(ctx.destination);
            const sB = ctx.createBufferSource(); sB.buffer = songB;
            gainB = ctx.createGain(); gainB.gain.value = 0; sB.connect(gainB).connect(analyser).connect(ctx.destination);
            sA.loop = sB.loop = true; sA.start(0); sB.start(0);
            isPlaying = true;
            document.getElementById('cardA').classList.add('deck-active');
        }}

        function updateEngine() {{
            if(!isPlaying) return;
            updateUI('A', songA); updateUI('B', songB);
        }}

        function updateUI(s, buf) {{
            let p = (ctx.currentTime % buf.duration) / buf.duration;
            document.getElementById('bar'+s).style.width = (p*100)+"%";
            let rem = buf.duration - (ctx.currentTime % buf.duration);
            let m = Math.floor(rem/60), sec = Math.floor(rem%60);
            document.getElementById('time'+s).innerText = (m<10?'0':'')+m+":"+(sec<10?'0':'')+sec;
            
            // CROSSFADE LOGIC เมื่อใกล้จบเพลง
            if(active === s && rem < 5) crossfade();
        }}

        function crossfade() {{
            let now = ctx.currentTime, dur = 4;
            if(active === 'A') {{
                gainA.gain.linearRampToValueAtTime(0, now+dur); gainB.gain.linearRampToValueAtTime(1, now+dur);
                document.getElementById('cardA').classList.remove('deck-active');
                document.getElementById('cardB').classList.add('deck-active');
                active = 'B';
            }} else {{
                gainB.gain.linearRampToValueAtTime(0, now+dur); gainA.gain.linearRampToValueAtTime(1, now+dur);
                document.getElementById('cardB').classList.remove('deck-active');
                document.getElementById('cardA').classList.add('deck-active');
                active = 'A';
            }}
        }}

        window.onload = loadInitial;
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=620)

st.markdown("""
    <div class="marquee-container bottom-m">
        <div class="marquee-text">อยู่นิ่งๆ ไม่เจ็บตัว ⚡ TOTAL PLAYLIST: {0} TRACKS ⚡ READY TO CAPTURE ⚡</div>
    </div>
""".format(len(all_songs)), unsafe_allow_html=True)
