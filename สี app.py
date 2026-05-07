import streamlit as st
import base64

# ==========================================
# ส่วนที่ 1: การตั้งค่าหน้าจอและ CSS (เพิ่มความรกและสีสันระดับ Ultra)
# ==========================================

st.set_page_config(page_title="Synapse Neon Mixer - Chaos Edition", layout="centered")

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_base64 = get_base64_image("logo1.png")
logo_html_link = f"data:image/png;base64,{logo_base64}" if logo_base64 else ""

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Prompt:wght@700&display=swap');
    
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    
    /* พื้นหลังแบบ Scanlines ให้ดูรกๆ แบบจอเก่า */
    .stApp {{ 
        background: radial-gradient(circle, #1a0033 0%, #000000 100%);
        background-image: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
        background-size: 100% 4px, 3px 100%;
    }}

    /* ตัวหนังสือวิ่งบน-ล่าง */
    .marquee-container {{
        position: fixed;
        width: 100%;
        background: rgba(255, 0, 222, 0.1);
        color: #00f3ff;
        font-family: 'Prompt', sans-serif;
        font-size: 20px;
        white-space: nowrap;
        overflow: hidden;
        z-index: 1000;
        border-top: 2px solid #ff00de;
        border-bottom: 2px solid #00f3ff;
        text-shadow: 0 0 10px #00f3ff;
    }}
    .top-m {{ top: 0; }}
    .bottom-m {{ bottom: 0; }}
    
    .marquee-text {{
        display: inline-block;
        padding-left: 100%;
        animation: marquee 15s linear infinite;
    }}
    
    @keyframes marquee {{
        0% {{ transform: translate(0, 0); }}
        100% {{ transform: translate(-100%, 0); }}
    }}

    /* Logo Neon หมุนแรงๆ */
    .block-container::before {{
        content: "";
        position: absolute;
        top: 40px; left: 50%;
        transform: translateX(-50%);
        width: 120px; height: 120px;
        background-image: url("{logo_html_link}");
        background-size: contain;
        background-repeat: no-repeat;
        z-index: 99;
        animation: extreme-glow 2s infinite alternate;
    }}

    @keyframes extreme-glow {{
        0% {{ filter: drop-shadow(0 0 20px #ff00de) hue-rotate(0deg); transform: translateX(-50%) scale(1); }}
        100% {{ filter: drop-shadow(0 0 40px #00f3ff) hue-rotate(360deg); transform: translateX(-50%) scale(1.15); }}
    }}

    .neon-title {{
        font-family: 'Orbitron', sans-serif;
        color: #fff;
        text-align: center;
        text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 20px #ff00de, 0 0 30px #ff00de, 0 0 40px #ff00de;
        font-size: 2rem;
        margin-top: 150px;
        letter-spacing: 5px;
        animation: flicker 0.5s infinite;
    }}
    
    @keyframes flicker {{
        0%, 100% {{ opacity: 1; }}
        41% {{ opacity: 0.8; }}
        42% {{ opacity: 0.1; }}
        43% {{ opacity: 0.8; }}
    }}
    </style>

    <div class="marquee-container top-m">
        <div class="marquee-text">อยู่นิ่งๆ ไม่เจ็บตัว ⚡ STAY STILL & HEAL ⚡ SYNAPSE NEON MIXER ⚡ อยู่นิ่งๆ ไม่เจ็บตัว ⚡ SYSTEM OVERLOAD ⚡</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="neon-title">SYNAPSE NEON</h1>', unsafe_allow_html=True)

# ==========================================
# ส่วนที่ 2: HTML/JS - ปรับ Visualizer ให้สะบัดแบบรกๆ
# ==========================================

html_code = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: transparent; color: white; overflow: hidden; font-family: 'Orbitron', sans-serif; }
        .neon-card { 
            border: 4px double #ff00de; 
            background: rgba(10,0,20,0.8); 
            box-shadow: 0 0 50px rgba(255,0,222,0.5), inset 0 0 20px rgba(0,243,255,0.3);
            backdrop-filter: blur(10px);
        }
        
        .visualizer-box { height: 180px; background: #000; border: 2px solid #00f3ff; box-shadow: 0 0 20px #00f3ff; }
        
        .deck { padding: 15px; border-radius: 5px; border: 1px solid #444; margin-bottom: 10px; background: rgba(255,255,255,0.05); }
        .deck-active { border: 2px solid #ff00de !important; animation: pulse 1s infinite; }
        
        @keyframes pulse {
            0% { box-shadow: 0 0 5px #ff00de; }
            50% { box-shadow: 0 0 25px #ff00de; }
            100% { box-shadow: 0 0 5px #ff00de; }
        }

        .btn-mix { 
            background: #fff; color: #000; font-weight: 900; padding: 15px; border-radius: 0;
            text-transform: uppercase; letter-spacing: 4px; transition: 0.2s;
            border: 3px solid #ff00de; clip-path: polygon(10% 0, 100% 0, 90% 100%, 0% 100%);
        }
        .btn-mix:hover { background: #ff00de; color: #fff; transform: skewX(-5deg); }
    </style>
</head>
<body>
    <div class="max-w-md mx-auto p-6 neon-card rounded-sm">
        <canvas id="scope" class="visualizer-box w-full mb-4"></canvas>

        <div id="cardA" class="deck">
            <div class="flex justify-between text-[12px] mb-2">
                <span class="text-pink-500 font-black">DECK A [STAY]</span>
                <span id="timeA" class="text-white">00:00</span>
            </div>
            <input type="file" id="inA" class="hidden" onchange="handleFile(this.files[0], 'A')">
            <button onclick="document.getElementById('inA').click()" class="bg-pink-600 text-[10px] px-4 py-1">LOAD FILE</button>
            <div id="nameA" class="text-[10px] mt-2 truncate text-cyan-300">WAITING...</div>
            <div class="h-2 bg-gray-900 mt-2"><div id="barA" class="h-full bg-pink-500 shadow-[0_0_10px_#ff00de]"></div></div>
        </div>

        <div id="cardB" class="deck">
            <div class="flex justify-between text-[12px] mb-2">
                <span class="text-cyan-400 font-black">DECK B [HEAL]</span>
                <span id="timeB" class="text-white">00:00</span>
            </div>
            <input type="file" id="inB" class="hidden" onchange="handleFile(this.files[0], 'B')">
            <button onclick="document.getElementById('inB').click()" class="bg-cyan-600 text-[10px] px-4 py-1">LOAD FILE</button>
            <div id="nameB" class="text-[10px] mt-2 truncate text-pink-300">WAITING...</div>
            <div class="h-2 bg-gray-900 mt-2"><div id="barB" class="h-full bg-cyan-400 shadow-[0_0_10px_#00f3ff]"></div></div>
        </div>

        <button onclick="startMix()" class="btn-mix w-full mt-4">INITIALIZE SYSTEM</button>
    </div>

    <script>
        let ctx, analyser, songA, songB, gainA, gainB, sourceA, sourceB;
        let active = 'A', isPlaying = false, data;

        function init() {
            if (!ctx) {
                ctx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = ctx.createAnalyser();
                analyser.fftSize = 128; // ปรับให้แท่งใหญ่และลกขึ้น
                data = new Uint8Array(analyser.frequencyBinCount);
                render();
            }
        }

        async function handleFile(file, side) {
            init();
            document.getElementById('name'+side).innerText = "LOADING CORE...";
            const buffer = await ctx.decodeAudioData(await file.arrayBuffer());
            if(side === 'A') songA = buffer; else songB = buffer;
            document.getElementById('name'+side).innerText = "READY: " + file.name;
        }

        function render() {
            requestAnimationFrame(render);
            if(!analyser) return;
            analyser.getByteFrequencyData(data);
            const can = document.getElementById('scope');
            const c = can.getContext('2d');
            
            // เคลียร์จอแบบทิ้งรอย (Motion Blur)
            c.fillStyle = 'rgba(0, 0, 0, 0.2)';
            c.fillRect(0, 0, can.width, can.height);
            
            let bw = (can.width / data.length) * 2;
            let x = 0;
            for(let i=0; i<data.length; i++) {
                let h = (data[i]/255) * can.height * 0.8;
                let hue = (i * 5) + (Date.now() / 10) % 360;
                c.fillStyle = `hsl(${hue}, 100%, 60%)`;
                c.shadowBlur = 15;
                c.shadowColor = `hsl(${hue}, 100%, 50%)`;
                c.fillRect(x, can.width/2 - h/2, bw - 2, h); // วาดจากตรงกลางให้ดูเหมือนคลื่นไฟฟ้า
                x += bw;
            }
            updateEngine();
        }

        function startMix() {
            if(!songA || !songB) return alert("LOAD BOTH DECKS FIRST!");
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
            document.getElementById('cardA').classList.add('deck-active');
        }

        function updateEngine() {
            if(!isPlaying) return;
            updateUI('A', songA, gainA);
            updateUI('B', songB, gainB);
        }

        function updateUI(s, buffer, gain) {
            let bar = document.getElementById('bar'+s);
            let time = document.getElementById('time'+s);
            let p = (ctx.currentTime % buffer.duration) / buffer.duration;
            bar.style.width = (p * 100) + "%";
            let rem = buffer.duration - (ctx.currentTime % buffer.duration);
            let m = Math.floor(rem/60), sec = Math.floor(rem%60);
            time.innerText = (m<10?'0':'')+m+":"+(sec<10?'0':'')+sec;
            if(active === s && rem < 5) crossfade();
        }

        function crossfade() {
            let next = (active === 'A' ? 'B' : 'A');
            let now = ctx.currentTime;
            if(active === 'A') {
                gainA.gain.linearRampToValueAtTime(0, now + 4);
                gainB.gain.linearRampToValueAtTime(1, now + 4);
                document.getElementById('cardA').classList.remove('deck-active');
                document.getElementById('cardB').classList.add('deck-active');
            } else {
                gainB.gain.linearRampToValueAtTime(0, now + 4);
                gainA.gain.linearRampToValueAtTime(1, now + 4);
                document.getElementById('cardB').classList.remove('deck-active');
                document.getElementById('cardA').classList.add('deck-active');
            }
            active = next;
        }
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=650)

st.markdown("""
    <div class="marquee-container bottom-m">
        <div class="marquee-text">อยู่นิ่งๆ ไม่เจ็บตัว ⚡ STAY STILL & HEAL ⚡ SYNAPSE NEON MIXER ⚡ อยู่นิ่งๆ ไม่เจ็บตัว ⚡ SYSTEM OVERLOAD ⚡</div>
    </div>
""", unsafe_allow_html=True)
