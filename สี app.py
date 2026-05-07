import streamlit as st
import base64

# ==========================================
# ส่วนที่ 1: UI & Multicolor Neon CSS
# ==========================================

st.set_page_config(page_title="Synapse RGB Chaos", layout="centered")

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
    
    .stApp {{ 
        background: #000;
        background-image: 
            linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(255, 0, 0, 0.05) 50%), 
            linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.03), rgba(0, 0, 255, 0.03));
        background-size: 100% 4px, 3px 100%;
    }}

    /* ตัวหนังสือวิ่งแบบสายรุ้ง */
    .marquee-container {{
        position: fixed;
        width: 100%;
        background: rgba(255, 255, 255, 0.05);
        font-family: 'Prompt', sans-serif;
        font-size: 22px;
        white-space: nowrap;
        overflow: hidden;
        z-index: 1000;
        border-top: 3px solid #ff0000;
        border-bottom: 3px solid #00ff00;
        animation: border-flicker 2s infinite;
    }}
    .top-m {{ top: 0; }}
    .bottom-m {{ bottom: 0; }}
    
    .marquee-text {{
        display: inline-block;
        padding-left: 100%;
        animation: marquee 30s linear infinite, rainbow-text 3s infinite;
        font-weight: 900;
    }}
    
    @keyframes rainbow-text {{
        0% {{ color: #ff0000; text-shadow: 0 0 10px #ff0000; }}
        20% {{ color: #00ff00; text-shadow: 0 0 10px #00ff00; }}
        40% {{ color: #0000ff; text-shadow: 0 0 10px #0000ff; }}
        60% {{ color: #ffffff; text-shadow: 0 0 10px #ffffff; }}
        80% {{ color: #ff00de; text-shadow: 0 0 10px #ff00de; }}
        100% {{ color: #ff0000; text-shadow: 0 0 10px #ff0000; }}
    }}

    @keyframes marquee {{
        0% {{ transform: translate(0, 0); }}
        100% {{ transform: translate(-100%, 0); }}
    }}

    /* แก้ไขตำแหน่ง Logo ไม่ให้ทับตัวหนังสือ */
    .block-container::before {{
        content: "";
        position: absolute;
        top: 40px; left: 50%;
        transform: translateX(-50%);
        width: 100px; height: 100px;
        background-image: url("{logo_html_link}");
        background-size: contain;
        background-repeat: no-repeat;
        z-index: 99;
        filter: drop-shadow(0 0 15px #fff);
    }}

    .neon-title {{
        font-family: 'Orbitron', sans-serif;
        color: #fff;
        text-align: center;
        text-shadow: 0 0 10px #ff0000, 0 0 20px #0000ff;
        font-size: 1.8rem;
        margin-top: 160px; /* เพิ่มระยะห่างลงมา */
        margin-bottom: 20px;
        letter-spacing: 5px;
        animation: glitch-title 1s infinite;
    }}

    @keyframes glitch-title {{
        0% {{ text-shadow: 2px 2px #ff0000, -2px -2px #0000ff; }}
        50% {{ text-shadow: -2px 2px #00ff00, 2px -2px #ff00de; }}
        100% {{ text-shadow: 2px -2px #ffffff, -2px 2px #ff0000; }}
    }}
    </style>

    <div class="marquee-container top-m">
        <div class="marquee-text">อยู่นิ้งๆ ไม่เจ็บตัว ⚡ STAY STILL & HEAL ⚡ NO LIES JUST REAL CODE ⚡ SYNAPSE NEON ⚡</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="neon-title">อยู่นิ้งๆไม่เจ็บตัว</h1>', unsafe_allow_html=True)

# ==========================================
# ส่วนที่ 2: HTML/JS - ปรับสีสันให้หลากสี (Red/Blue/Green/White)
# ==========================================

html_code = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: transparent; color: white; overflow: hidden; font-family: 'Orbitron', sans-serif; }
        
        .neon-card { 
            border: 5px solid;
            border-image: linear-gradient(45deg, #ff0000, #00ff00, #0000ff, #ffffff) 1;
            background: rgba(0,0,0,0.9); 
            box-shadow: 0 0 30px rgba(255,255,255,0.2);
            animation: border-rotate 10s linear infinite;
        }

        @keyframes border-rotate {
            0% { border-image-source: linear-gradient(0deg, #ff0000, #00ff00, #0000ff, #ffffff); }
            100% { border-image-source: linear-gradient(360deg, #ff0000, #00ff00, #0000ff, #ffffff); }
        }
        
        .visualizer-box { height: 180px; background: #000; border: 1px solid #555; }
        
        .deck-a { border-left: 5px solid #ff0000; background: rgba(255,0,0,0.05); }
        .deck-b { border-left: 5px solid #0000ff; background: rgba(0,0,255,0.05); }
        
        .deck-active { outline: 2px solid #ffffff; box-shadow: 0 0 20px #ffffff; }

        .btn-start { 
            background: #ff0000; color: white; font-weight: 900; padding: 12px;
            border: 2px solid #ffffff; text-transform: uppercase;
            box-shadow: 5px 5px 0px #0000ff;
        }
        .btn-start:active { transform: translate(2px, 2px); box-shadow: none; }
    </style>
</head>
<body>
    <div class="max-w-md mx-auto p-4 neon-card">
        <canvas id="scope" class="visualizer-box w-full mb-4"></canvas>

        <div id="cardA" class="deck-a p-3 mb-2">
            <div class="flex justify-between text-[11px] font-bold">
                <span class="text-red-500">SYSTEM: RED [DECK A]</span>
                <span id="timeA">00:00</span>
            </div>
            <button onclick="document.getElementById('inA').click()" class="bg-white text-black text-[9px] px-2 mt-1 font-bold">LOAD RED</button>
            <input type="file" id="inA" class="hidden" onchange="handleFile(this.files[0], 'A')">
            <div id="nameA" class="text-[9px] truncate text-gray-400 mt-1">NO DATA</div>
            <div class="h-1.5 bg-gray-800 mt-1"><div id="barA" class="h-full bg-red-600"></div></div>
        </div>

        <div id="cardB" class="deck-b p-3 mb-2">
            <div class="flex justify-between text-[11px] font-bold">
                <span class="text-blue-500">SYSTEM: BLUE [DECK B]</span>
                <span id="timeB">00:00</span>
            </div>
            <button onclick="document.getElementById('inB').click()" class="bg-white text-black text-[9px] px-2 mt-1 font-bold">LOAD BLUE</button>
            <input type="file" id="inB" class="hidden" onchange="handleFile(this.files[0], 'B')">
            <div id="nameB" class="text-[9px] truncate text-gray-400 mt-1">NO DATA</div>
            <div class="h-1.5 bg-gray-800 mt-1"><div id="barB" class="h-full bg-blue-600"></div></div>
        </div>

        <button onclick="startMix()" class="btn-start w-full mt-2">RUN AUTO-MIXER ENGINE</button>
    </div>

    <script>
        let ctx, analyser, songA, songB, gainA, gainB, active = 'A', isPlaying = false, data;

        function init() {
            if (!ctx) {
                ctx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = ctx.createAnalyser();
                analyser.fftSize = 64; 
                data = new Uint8Array(analyser.frequencyBinCount);
                render();
            }
        }

        async function handleFile(file, side) {
            init();
            document.getElementById('name'+side).innerText = "LOADING...";
            const buffer = await ctx.decodeAudioData(await file.arrayBuffer());
            if(side === 'A') songA = buffer; else songB = buffer;
            document.getElementById('name'+side).innerText = file.name;
        }

        function render() {
            requestAnimationFrame(render);
            if(!analyser) return;
            
            // ปรับลดความละเอียดลงเหลือ 128 เพื่อให้แท่งใหญ่ขึ้น ไม่ดูเยอะเกินไป
            analyser.fftSize = 256; 
            const bufferLength = analyser.frequencyBinCount;
            const dataArray = new Uint8Array(bufferLength);
            analyser.getByteFrequencyData(dataArray);

            const can = document.getElementById('scope');
            const c = can.getContext('2d');
            
            // เคลียร์จอแบบ Fade เพื่อให้มีเงาจางๆ ตามหลัง
            c.fillStyle = 'rgba(0, 0, 0, 0.15)';
            c.fillRect(0, 0, can.width, can.height);
            
            let bw = (can.width / bufferLength) * 2;
            let x = 0;

            for(let i = 0; i < bufferLength; i++) {
                // คำนวณความสูงตามจังหวะเพลง
                let h = (dataArray[i] / 255) * can.height * 0.8;
                
                // --- ส่วนสำคัญ: เปลี่ยนสีตามความดัง (Dynamic Color) ---
                // ใช้ค่าจากเสียงมาคำนวณเฉดสี (Hue) เพื่อให้สีเปลี่ยนไปตามจังหวะ
                let hue = (i * 10 + dataArray[i]) % 360; 
                let currentColor = `hsl(${hue}, 100%, 60%)`;

                // ปรับความฟุ้งให้เต้นตามความแรงของเสียง
                c.shadowBlur = dataArray[i] / 10; 
                c.shadowColor = currentColor;
                c.fillStyle = currentColor;

                // วาดแท่งกราฟ (วาดแบบให้มีช่องว่างนิดหน่อย จะได้ดูไม่รก)
                if (h > 0) {
                    c.fillRect(x, can.height - h, bw - 4, h);
                }

                x += bw;
            }
            
            c.shadowBlur = 0;
            updateEngine();
        }


        function startMix() {
            if(!songA || !songB) return alert("LOAD BOTH FILES!");
            if(isPlaying) return;
            const sA = ctx.createBufferSource(); sA.buffer = songA;
            gainA = ctx.createGain(); sA.connect(gainA).connect(analyser).connect(ctx.destination);
            const sB = ctx.createBufferSource(); sB.buffer = songB;
            gainB = ctx.createGain(); gainB.gain.value = 0; sB.connect(gainB).connect(analyser).connect(ctx.destination);
            sA.loop = sB.loop = true; sA.start(0); sB.start(0);
            isPlaying = true;
            document.getElementById('cardA').classList.add('deck-active');
        }

        function updateEngine() {
            if(!isPlaying) return;
            updateUI('A', songA); updateUI('B', songB);
        }

        function updateUI(s, buf) {
            let p = (ctx.currentTime % buf.duration) / buf.duration;
            document.getElementById('bar'+s).style.width = (p*100)+"%";
            let rem = buf.duration - (ctx.currentTime % buf.duration);
            let m = Math.floor(rem/60), sec = Math.floor(rem%60);
            document.getElementById('time'+s).innerText = (m<10?'0':'')+m+":"+(sec<10?'0':'')+sec;
            if(active === s && rem < 5) crossfade();
        }

        function crossfade() {
            let now = ctx.currentTime, dur = 4;
            if(active === 'A') {
                gainA.gain.linearRampToValueAtTime(0, now+dur); gainB.gain.linearRampToValueAtTime(1, now+dur);
                document.getElementById('cardA').classList.remove('deck-active'); document.getElementById('cardB').classList.add('deck-active');
                active = 'B';
            } else {
                gainB.gain.linearRampToValueAtTime(0, now+dur); gainA.gain.linearRampToValueAtTime(1, now+dur);
                document.getElementById('cardB').classList.remove('deck-active'); document.getElementById('cardA').classList.add('deck-active');
                active = 'A';
            }
        }
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=650)

st.markdown("""
    <div class="marquee-container bottom-m">
        <div class="marquee-text">อยู่นิ่งๆ ไม่เจ็บตัว ⚡ SYSTEM STATUS: RGB CHAOS ⚡ V.6.0 ⚡ อยู่นิ่งๆ ไม่เจ็บตัว ⚡</div>
    </div>
""", unsafe_allow_html=True)
