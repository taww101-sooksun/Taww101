import streamlit as st
import base64
import os
import streamlit as st
import base64

# ==========================================
# ส่วนที่ 1: การตั้งค่าหน้าจอและ CSS (กู้คืนสีสัน Neon ขั้นสุด)
# ==========================================

st.set_page_config(page_title="Synapse Neon Mixer", layout="centered")

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_base64 = get_base64_image("logo1.png")
logo_html_link = f"data:image/png;base64,{logo_base64}" if logo_base64 else ""

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    .stApp {{ background-color: #000; }}

    /* Logo ตรงกลางพร้อมแสง Neon หมุนสลับสี */
    .block-container::before {{
        content: "";
        position: absolute;
        top: 10px; left: 50%;
        transform: translateX(-50%);
        width: 100px; height: 100px;
        background-image: url("{logo_html_link}");
        background-size: contain;
        background-repeat: no-repeat;
        z-index: 999;
        filter: drop-shadow(0 0 10px #ff00de);
        animation: logo-glow 4s infinite alternate;
    }}

    @keyframes logo-glow {{
        0% {{ filter: drop-shadow(0 0 10px #ff00de); transform: translateX(-50%) scale(1); }}
        50% {{ filter: drop-shadow(0 0 25px #00f3ff); transform: translateX(-50%) scale(1.1); }}
        100% {{ filter: drop-shadow(0 0 10px #ff8c00); transform: translateX(-50%) scale(1); }}
    }}

    .neon-title {{
        font-family: 'Orbitron', sans-serif;
        color: #fff;
        text-align: center;
        text-shadow: 0 0 10px #ff00de, 0 0 20px #00f3ff;
        font-size: 1.6rem;
        margin-top: 110px;
        letter-spacing: 3px;
        animation: text-flicker 2s infinite;
    }}
    @keyframes text-flicker {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.8; }}
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="neon-title">SYNAPSE NEON MIXER</h1>', unsafe_allow_html=True)

# ==========================================
# ส่วนที่ 2: HTML/JS - ระบบเล่นต่อเนื่อง + สีสันสะบัด
# ==========================================

html_code = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: transparent; color: white; overflow: hidden; font-family: 'Inter', sans-serif; }
        .neon-card { border: 2px solid #333; background: rgba(0,0,0,0.9); box-shadow: 0 0 30px rgba(255,0,222,0.2); }
        
        /* กราฟเสียงสีรุ้งสะบัด */
        .visualizer-box { height: 150px; background: #050505; border-radius: 15px; border: 1px solid #222; }
        
        .deck { padding: 15px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px; transition: 0.5s; }
        .deck-active { border: 1px solid #00f3ff; box-shadow: 0 0 15px #00f3ff; background: rgba(0,243,255,0.05); }
        
        /* ปุ่มสไตล์ Cyberpunk */
        .btn-mix { 
            background: linear-gradient(45deg, #ff00de, #00f3ff);
            color: white; font-weight: bold; padding: 12px; border-radius: 10px;
            text-transform: uppercase; letter-spacing: 2px; transition: 0.3s;
            box-shadow: 0 0 15px rgba(255,0,222,0.4);
        }
        .btn-mix:hover { transform: scale(1.05); box-shadow: 0 0 25px rgba(0,243,255,0.6); }
        
        .progress-bar { height: 6px; background: #222; border-radius: 10px; overflow: hidden; }
        .progress-inner { height: 100%; width: 0%; background: linear-gradient(90deg, #ff00de, #ff8c00); }
    </style>
</head>
<body>
    <div class="max-w-md mx-auto p-4 neon-card rounded-3xl">
        <canvas id="scope" class="visualizer-box w-full mb-4"></canvas>

        <div id="cardA" class="deck">
            <div class="flex justify-between text-[10px] mb-2">
                <span id="labelA" class="text-pink-500 font-bold">DECK A</span>
                <span id="timeA" class="font-mono">00:00</span>
            </div>
            <input type="file" id="inA" class="hidden" onchange="handleFile(this.files[0], 'A')">
            <button onclick="document.getElementById('inA').click()" class="text-[10px] border border-gray-600 px-3 py-1 rounded">LOAD A</button>
            <div id="nameA" class="text-[11px] mt-1 truncate text-gray-400">No Song</div>
            <div class="progress-bar mt-2"><div id="barA" class="progress-inner"></div></div>
        </div>

        <div id="cardB" class="deck">
            <div class="flex justify-between text-[10px] mb-2">
                <span id="labelB" class="text-cyan-400 font-bold">DECK B</span>
                <span id="timeB" class="font-mono">00:00</span>
            </div>
            <input type="file" id="inB" class="hidden" onchange="handleFile(this.files[0], 'B')">
            <button onclick="document.getElementById('inB').click()" class="text-[10px] border border-gray-600 px-3 py-1 rounded">LOAD B</button>
            <div id="nameB" class="text-[11px] mt-1 truncate text-gray-400">No Song</div>
            <div class="progress-bar mt-2"><div id="barB" class="progress-inner" style="background: #00f3ff;"></div></div>
        </div>

        <button onclick="startMix()" class="btn-mix w-full mt-2">🔥 START AUTO-MIX</button>
        <div id="status" class="text-[10px] text-center mt-3 text-gray-500 uppercase tracking-widest">System Ready</div>
    </div>

    <script>
        let ctx, analyser, songA, songB, gainA, gainB, sourceA, sourceB;
        let active = 'A', isPlaying = false, data;

        function init() {
            if (!ctx) {
                ctx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = ctx.createAnalyser();
                analyser.fftSize = 256;
                data = new Uint8Array(analyser.frequencyBinCount);
                render();
            }
        }

        async function handleFile(file, side) {
            init();
            document.getElementById('name'+side).innerText = "Loading...";
            const buffer = await ctx.decodeAudioData(await file.arrayBuffer());
            if(side === 'A') songA = buffer; else songB = buffer;
            document.getElementById('name'+side).innerText = file.name;
        }

        function render() {
            requestAnimationFrame(render);
            if(!analyser) return;
            analyser.getByteFrequencyData(data);
            const can = document.getElementById('scope');
            const c = can.getContext('2d');
            c.clearRect(0,0,can.width,can.height);
            
            let bw = (can.width / data.length) * 2.5;
            let x = 0;
            for(let i=0; i<data.length; i++) {
                let h = (data[i]/255) * can.height;
                let hue = (i * 3) + (Date.now() / 50) % 360;
                c.fillStyle = `hsl(${hue}, 100%, 50%)`;
                c.fillRect(x, can.height - h, bw - 1, h);
                x += bw;
            }
            updateEngine();
        }

        function startMix() {
            if(!songA || !songB) return alert("อาจารย์ครับ โหลดเพลงให้ครบ A/B ก่อน!");
            if(isPlaying) return;
            
            sourceA = ctx.createBufferSource(); sourceA.buffer = songA;
            gainA = ctx.createGain(); 
            sourceA.connect(gainA).connect(analyser).connect(ctx.destination);
            
            sourceB = ctx.createBufferSource(); sourceB.buffer = songB;
            gainB = ctx.createGain(); gainB.gain.value = 0;
            sourceB.connect(gainB).connect(analyser).connect(ctx.destination);
            
            sourceA.loop = true; sourceB.loop = true;
            sourceA.start(0); sourceB.start(0);
            isPlaying = true;
            document.getElementById('status').innerText = "Playing: Deck A";
            document.getElementById('cardA').classList.add('deck-active');
        }

        function updateEngine() {
            if(!isPlaying) return;
            let now = ctx.currentTime;
            
            // ระบบเช็กเวลาและ Auto-Crossfade เมื่อเพลงใกล้จบ (สมมติเล่น Loop)
            // ในที่นี้ใช้การอัปเดต Progress Bar และ UI
            updateUI('A', songA, gainA);
            updateUI('B', songB, gainB);
        }

        function updateUI(s, buffer, gain) {
            let bar = document.getElementById('bar'+s);
            let time = document.getElementById('time'+s);
            // จำลองการเดินของเวลาใน Loop
            let p = (ctx.currentTime % buffer.duration) / buffer.duration;
            bar.style.width = (p * 100) + "%";
            
            let rem = buffer.duration - (ctx.currentTime % buffer.duration);
            let m = Math.floor(rem/60), sec = Math.floor(rem%60);
            time.innerText = (m<10?'0':'')+m+":"+(sec<10?'0':'')+sec;

            // AUTO CROSSFADE LOGIC: เมื่อเหลือ 5 วินาทีสุดท้าย
            if(active === s && rem < 5) {
                crossfade();
            }
        }

        function crossfade() {
            let next = (active === 'A' ? 'B' : 'A');
            let now = ctx.currentTime;
            let dur = 4; // วินาทีในการ Fade
            
            if(active === 'A') {
                gainA.gain.linearRampToValueAtTime(0, now + dur);
                gainB.gain.linearRampToValueAtTime(1, now + dur);
                document.getElementById('cardA').classList.remove('deck-active');
                document.getElementById('cardB').classList.add('deck-active');
            } else {
                gainB.gain.linearRampToValueAtTime(0, now + dur);
                gainA.gain.linearRampToValueAtTime(1, now + dur);
                document.getElementById('cardB').classList.remove('deck-active');
                document.getElementById('cardA').classList.add('deck-active');
            }
            active = next;
            document.getElementById('status').innerText = "Auto-Mixing to: Deck " + active;
        }
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=650)

st.markdown("""
<div style='text-align: center; color: #555; font-size: 12px; font-family: "Orbitron"; letter-spacing: 2px;'>
    อยู่นิ่งๆ ไม่เจ็บตัว | AUTO-MIX ENGINE v5.0 | © 2026
</div>
""", unsafe_allow_html=True)

# ==========================================
# ส่วนที่ 1: การตั้งค่าหน้าจอและดึงไฟล์ MP3
# ==========================================

st.set_page_config(page_title="Synapse Neon Mixer", layout="centered")

# ฟังก์ชันดึงรายชื่อเพลง .mp3 ในโฟลเดอร์เดียวกัน
def get_mp3_files():
    files = [f for f in os.listdir('.') if f.endswith('.mp3')]
    return sorted(files)

# แปลงไฟล์เป็น Base64 เพื่อส่งให้ HTML/JS (ทำได้จริงและไม่หลอก)
def get_audio_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    except:
        return None

# สแกนเพลง
all_songs = get_mp3_files()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #000; }
    .neon-title {
        font-family: 'Orbitron', sans-serif;
        color: #fff; text-align: center;
        text-shadow: 0 0 10px #ff00de, 0 0 20px #00f3ff;
        font-size: 1.6rem; letter-spacing: 3px;
        margin-bottom: 20px;
    }
    .song-list-container {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid #333;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="neon-title">SYNAPSE NEON MIXER</h1>', unsafe_allow_html=True)

# --- ส่วนเลือกเพลงจาก List ---
st.markdown("<div class='song-list-container'>", unsafe_allow_html=True)
st.write("🎵 คลังเพลงในเครื่องของคุณ")

if not all_songs:
    st.warning("⚠️ ไม่พบไฟล์ .mp3 ในโฟลเดอร์เดียวกับไฟล์ .py นี้ครับ")
else:
    col1, col2 = st.columns(2)
    with col1:
        select_a = st.selectbox("เลือกเพลงใส่ DECK A", all_songs, key="sA")
    with col2:
        select_b = st.selectbox("เลือกเพลงใส่ DECK B", all_songs, key="sB")

    # เตรียมข้อมูล Base64
    audio_a_b64 = get_audio_base64(select_a)
    audio_b_b64 = get_audio_base64(select_b)
st.markdown("</div>", unsafe_allow_html=True)

# --- แก้ไขส่วนการเตรียมข้อมูลก่อนเข้า HTML ---
# ใช้ f-string แบบระวังเรื่องเครื่องหมาย ` 
# และตรวจสอบว่ามีเพลงถูกเลือกจริงไหม
song_a_name = select_a if all_songs else ""
song_b_name = select_b if all_songs else ""

# ==========================================
# ส่วนที่ 2: HTML/JS Mixer Engine (ฉบับแก้ไข Error)
# ==========================================

html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: transparent; color: white; overflow: hidden; font-family: 'Inter', sans-serif; }}
        .neon-card {{ border: 2px solid #333; background: rgba(0,0,0,0.9); box-shadow: 0 0 30px rgba(255,0,222,0.2); }}
        .visualizer-box {{ height: 120px; background: #050505; border-radius: 15px; border: 1px solid #222; }}
        .deck {{ padding: 10px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 8px; }}
        .deck-active {{ border: 1px solid #00f3ff; box-shadow: 0 0 10px #00f3ff; background: rgba(0,243,255,0.05); }}
        .btn-mix {{ 
            background: linear-gradient(45deg, #ff00de, #00f3ff);
            color: white; font-weight: bold; padding: 12px; border-radius: 10px;
            text-transform: uppercase; letter-spacing: 2px; width: 100%; cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="max-w-md mx-auto p-4 neon-card rounded-3xl">
        <canvas id="scope" class="visualizer-box w-full mb-4"></canvas>

        <div id="cardA" class="deck">
            <div class="flex justify-between text-[10px]">
                <span class="text-pink-500 font-bold">DECK A</span>
                <span id="timeA">00:00</span>
            </div>
            <div class="text-[11px] truncate text-gray-300">{song_a_name}</div>
        </div>

        <div id="cardB" class="deck">
            <div class="flex justify-between text-[10px]">
                <span class="text-cyan-400 font-bold">DECK B</span>
                <span id="timeB">00:00</span>
            </div>
            <div class="text-[11px] truncate text-gray-300">{song_b_name}</div>
        </div>

        <button id="mainBtn" onclick="startMix()" class="btn-mix">🔥 START NEON MIX</button>
        <div id="status" class="text-[9px] text-center mt-3 text-gray-500 uppercase">Ready</div>
    </div>

    <script>
        let ctx, analyser, songA, songB, gainA, gainB, sourceA, sourceB;
        let isPlaying = false, data;

        // แก้ไข: ใช้ Single Quote แทน Backtick ในการรับค่าจาก Python
        const b64A = '{audio_a_b64 if audio_a_b64 else ""}';
        const b64B = '{audio_b_b64 if audio_b_b64 else ""}';

        async function base64ToBuffer(b64) {{
            const resp = await fetch('data:audio/mp3;base64,' + b64);
            const arrayBuf = await resp.arrayBuffer();
            return await ctx.decodeAudioData(arrayBuf);
        }}

        async function startMix() {{
            if (!b64A || !b64B) {{ alert('โหลดเพลงไม่สำเร็จครับ!'); return; }}
            if (isPlaying) return;

            try {{
                document.getElementById('status').innerText = "LOADING ENGINE...";
                ctx = new (window.AudioContext || window.webkitAudioContext)();
                
                // ถอดรหัสเพลง
                songA = await base64ToBuffer(b64A);
                songB = await base64ToBuffer(b64B);

                analyser = ctx.createAnalyser();
                analyser.fftSize = 64;
                data = new Uint8Array(analyser.frequencyBinCount);

                sourceA = ctx.createBufferSource(); sourceA.buffer = songA;
                gainA = ctx.createGain(); sourceA.connect(gainA).connect(analyser).connect(ctx.destination);
                
                sourceB = ctx.createBufferSource(); sourceB.buffer = songB;
                gainB = ctx.createGain(); gainB.gain.value = 0;
                sourceB.connect(gainB).connect(analyser).connect(ctx.destination);

                sourceA.loop = true; sourceB.loop = true;
                sourceA.start(0); sourceB.start(0);
                
                isPlaying = true;
                render();
                document.getElementById('cardA').classList.add('deck-active');
                document.getElementById('status').innerText = "SYSTEM ONLINE";
                document.getElementById('mainBtn').innerText = "MIXER ACTIVE";
            }} catch(e) {{
                alert('Error: ' + e);
            }}
        }}

        function render() {{
            requestAnimationFrame(render);
            analyser.getByteFrequencyData(data);
            const can = document.getElementById('scope');
            const c = can.getContext('2d');
            c.clearRect(0,0,can.width,can.height);
            
            let bw = can.width / data.length;
            for(let i=0; i<data.length; i++) {{
                let h = (data[i]/255) * can.height;
                // แก้จุดนี้: ใช้การต่อสตริงธรรมดาแทน Backtick เพื่อเลี่ยง Error ใน Python
                c.fillStyle = 'hsl(' + (i * 10) + ', 100%, 50%)';
                c.fillRect(i*bw, can.height-h, bw-1, h);
            }}
        }}
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=550)
