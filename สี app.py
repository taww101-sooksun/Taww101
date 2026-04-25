import streamlit as st
import base64
import streamlit as st
import base64

# ==========================================
# ส่วนที่ 1: การตั้งค่าหน้าจอและ CSS (ย้าย Logo มาตรงกลาง + เพิ่มสี Neon)
# ==========================================

# ต้องเรียก st.set_page_config() เป็นคำสั่งแรกสุดของ Streamlit
st.set_page_config(page_title="Synapse Studio Mixer", layout="centered")

# ฟังก์ชันสำหรับแปลงรูปเป็น Base64 (เพื่อให้รูปโชว์ใน CSS ได้)
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return "" # ถ้าไม่เจอรูปจะไม่โชว์อะไร

# โหลด Logo และแปลงเป็น HTML link
logo_html_link = ""
logo_base64 = get_base64_image("logo1.png")
if logo_base64:
    logo_html_link = f"data:image/png;base64,{logo_base64}"

# CSS สำหรับซ่อนส่วนเกิน, แปะ Logo ตรงกลาง, และสไตล์หัวข้อ
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

    /* 1. ซ่อนเมนูเดิมและ Footer */
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    
    /* 2. ตั้งค่าพื้นหลังและดันเนื้อหาขึ้นให้สุด */
    .main {{ background-color: #000000; }}
    .block-container {{
        padding-top: 1rem;
        padding-bottom: 0rem;
        position: relative; /* เพื่อให้ Logo ลอยเทียบกับกล่องนี้ */
    }}

    /* 3. [จุดที่แก้ไข] สร้าง Logo ใหม่ไปแปะที่ "ตรงกลางด้านบน" */
    .block-container::before {{
        content: "";
        position: absolute;
        top: 20px; /* ระยะห่างจากขอบบน */
        left: 50%; /* เลื่อนมาตรงกลาง */
        transform: translateX(-50%) scale(1); /* ปรับให้จุดกลางรูปอยู่ตรงกลางหน้าจอเป๊ะ */
        width: 100px;  /* ปรับขนาด Logo ตามต้องการ (เช่น 120px) */
        height: 100px;
        background-image: url("{logo_html_link}");
        background-size: contain;
        background-repeat: no-repeat;
        z-index: 999;
        
        /* 4. เอฟเฟกต์แสง Neon Glow และ Animation ให้ Logo (กู้คืนสีสัน) */
        filter: drop-shadow(0 0 5px #ff00de); /* แสงเริ่มต้นสีชมพู */
        animation: logo-pulsing 2s infinite alternate; /* เล่น Animation */
    }}

    /* Animation สำหรับ Logo ขยายเข้า-ออก และแสงวูบวาบ */
    @keyframes logo-pulsing {{
        from {{ 
            filter: drop-shadow(0 0 5px #ff00de); 
            transform: translateX(-50%) scale(1); 
        }}
        to {{ 
            filter: drop-shadow(0 0 15px #ff00de); /* แสงเข้มขึ้น */
            transform: translateX(-50%) scale(1.05); /* ขยายใหญ่ขึ้นนิดหน่อย */
        }}
    }}

    /* 5. สไตล์หัวข้อแอป Neon (กู้คืนสีสันจัดเต็ม) */
    .neon-title {{
        font-family: 'Orbitron', sans-serif;
        color: #fff;
        text-align: center;
        /* แสง Neon สีชมพู-น้ำเงิน-ม่วง สลับกัน */
        text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 20px #ff00de, 0 0 30px #00f3ff, 0 0 40px #ff00de;
        font-size: 1.8rem;
        margin-top: 130px; /* เผื่อพื้นที่ให้ Logo ตรงกลาง */
        margin-bottom: 10px;
        letter-spacing: 2px;
    }}
    </style>
    """, unsafe_allow_html=True)

# แสดงหัวข้อแอป
st.markdown('<h1 class="neon-title">SYNAPSE อยู่นิ่งๆ ไม่เจ็บตัว</h1>', unsafe_allow_html=True)


# ==========================================
# ส่วนที่ 2: โค้ด HTML/JS สำหรับ Mixer และ Visualizer (สีสันกู้คืนเต็มสูบ)
# ==========================================

html_code = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: transparent; color: white; font-family: 'Inter', sans-serif; overflow: hidden; }
        
        /* สไตล์กล่องหลักและกล่องเพลง (เน้นขอบเรืองแสง) */
        .neon-box { border: 1px solid rgba(255, 255, 255, 0.1); background: rgba(10, 10, 10, 0.95); box-shadow: 0 0 20px rgba(0,243,255,0.1); }
        .deck-box { border-left: 4px solid; background: rgba(20, 20, 20, 0.8); transition: 0.3s; }
        .deck-box:hover { background: rgba(30, 30, 30, 1); }
        
        /* --- [จุดที่แก้ไข] ย่อขนาดกราฟเสียงให้เล็กลงอีกนิด --- */
        .visualizer-container { height: 120px; background: #000; border-radius: 12px; border: 1px solid #333; }
        
        /* ปุ่มสไตล์ Neon สะท้อนแสง (กู้คืนสี แดง/เขียว/ส้ม) */
        .btn-neon { transition: 0.2s; font-weight: bold; text-transform: uppercase; font-size: 11px; letter-spacing: 1px; }
        .neon-red { border: 2px solid #ff0055; color: #ff0055; text-shadow: 0 0 5px #ff0055; box-shadow: 0 0 10px rgba(255,0,85,0.3); }
        .neon-red:hover { background: #ff0055; color: white; box-shadow: 0 0 20px #ff0055; }
        .neon-green { border: 2px solid #00ffcc; color: #00ffcc; text-shadow: 0 0 5px #00ffcc; box-shadow: 0 0 10px rgba(0,255,204,0.3); }
        .neon-green:hover { background: #00ffcc; color: black; box-shadow: 0 0 20px #00ffcc; }
        
        /* แถบเวลา (กู้คืนการไล่เฉดสี ส้ม-ม่วง-น้ำเงิน) */
        .progress-bg { height: 5px; background: #1a1a1a; border-radius: 3px; overflow: hidden; }
        .progress-fill { height: 100%; width: 0%; background: linear-gradient(90deg, #ff00de, #00f3ff, #ff8c00); transition: width 0.1s linear; }
    </style>
</head>
<body>
    <div class="max-w-md mx-auto p-5 neon-box rounded-3xl">
        
        <canvas id="visualizer" class="visualizer-container w-full mb-5"></canvas>

        <div class="p-4 deck-box border-pink-600 rounded-r-xl mb-3">
            <div class="flex justify-between items-center mb-1">
                <span class="text-[10px] text-pink-500 font-bold uppercase tracking-widest">Deck A</span>
                <span id="timeA" class="text-[10px] font-mono text-gray-400">READY</span>
            </div>
            <div id="nameA" class="text-xs font-semibold mb-2 truncate text-gray-100">ยังไม่ได้โหลดเพลง A...</div>
            <input type="file" id="inputA" accept="audio/*" class="hidden" onchange="loadAudio(this.files[0], 'A')">
            <button onclick="document.getElementById('inputA').click()" class="text-[9px] bg-pink-900/40 px-3 py-1.5 rounded-lg border border-pink-500/50 text-pink-200">เลือกไฟล์ A</button>
            <div class="progress-bg mt-3"><div id="barA" class="progress-fill"></div></div>
        </div>

        <div class="p-4 deck-box border-cyan-400 rounded-r-xl mb-5">
            <div class="flex justify-between items-center mb-1">
                <span class="text-[10px] text-cyan-400 font-bold uppercase tracking-widest">Deck B</span>
                <span id="timeB" class="text-[10px] font-mono text-gray-400">READY</span>
            </div>
            <div id="nameB" class="text-xs font-semibold mb-2 truncate text-gray-100">ยังไม่ได้โหลดเพลง B...</div>
            <input type="file" id="inputB" accept="audio/*" class="hidden" onchange="loadAudio(this.files[0], 'B')">
            <button onclick="document.getElementById('inputB').click()" class="text-[9px] bg-cyan-900/40 px-3 py-1.5 rounded-lg border border-cyan-500/50 text-cyan-200">เลือกไฟล์ B</button>
            <div class="progress-bg mt-3"><div id="barB" class="progress-fill" style="background: #00ffcc;"></div></div>
        </div>

        <div class="grid grid-cols-2 gap-4">
            <button onclick="startPlaying()" id="btn-play" class="btn-neon neon-red py-3 rounded-2xl">Start Mix</button>
            <button onclick="startCrossfade()" id="btn-fade" class="btn-neon neon-green py-3 rounded-2xl">Crossfade</button>
        </div>
    </div>

    <script>
        let audioCtx, analyser, songA, songB, gainA, gainB, sourceA, sourceB;
        let isPlaying = false, current = 'A', dataArray;

        function initAudio() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = audioCtx.createAnalyser();
                analyser.fftSize = 128;
                dataArray = new Uint8Array(analyser.frequencyBinCount);
                draw();
            }
        }

        function draw() {
            requestAnimationFrame(draw);
            if (!analyser) return;
            analyser.getByteFrequencyData(dataArray);
            const canvas = document.getElementById('visualizer');
            const ctx = canvas.getContext('2d');
            
            // ล้างจอแบบ Fade เพื่อให้เกิดเงาตาม
            ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            const bWidth = (canvas.width / dataArray.length) * 2;
            let x = 0;
            for(let i = 0; i < dataArray.length; i++) {
                let h = (dataArray[i] / 255) * canvas.height;
                // [กู้คืนสีสัน] สีสะท้อนแสง ส้ม-ม่วง-น้ำเงิน-ส้ม
                ctx.fillStyle = `hsl(${{280 + i*4}}, 100%, 50%)`;
                ctx.fillRect(x, canvas.height - h, bWidth - 1, h);
                x += bWidth;
            }
            updateUI();
        }

        async function loadAudio(file, key) {
            initAudio();
            document.getElementById('name'+key).innerText = "Loading: " + file.name;
            const buffer = await audioCtx.decodeAudioData(await file.arrayBuffer());
            if(key === 'A') songA = buffer; else songB = buffer;
            document.getElementById('name'+key).innerText = file.name;
        }

        function startPlaying() {
            if (!songA || !songB) return alert("โหลดเพลงให้ครบทั้ง A และ B ก่อนครับอาจารย์!");
            if (isPlaying) return;

            sourceA = audioCtx.createBufferSource(); sourceA.buffer = songA;
            gainA = audioCtx.createGain();
            sourceA.connect(gainA).connect(analyser).connect(audioCtx.destination);
            
            sourceB = audioCtx.createBufferSource(); sourceB.buffer = songB;
            gainB = audioCtx.createGain(); gainB.gain.value = 0;
            sourceB.connect(gainB).connect(analyser).connect(audioCtx.destination);

            sourceA.start(0); sourceB.start(0);
            isPlaying = true; startTime = audioCtx.currentTime;
        }

        function startCrossfade() {
            if(!isPlaying) return;
            const now = audioCtx.currentTime;
            const dur = 5;
            if(current === 'A') {
                gainA.gain.linearRampToValueAtTime(1, now); gainA.gain.linearRampToValueAtTime(0, now+dur);
                gainB.gain.linearRampToValueAtTime(0, now); gainB.gain.linearRampToValueAtTime(1, now+dur);
                current = 'B';
            } else {
                gainB.gain.linearRampToValueAtTime(1, now); gainB.gain.linearRampToValueAtTime(0, now+dur);
                gainA.gain.linearRampToValueAtTime(0, now); gainA.gain.linearRampToValueAtTime(1, now+dur);
                current = 'A';
            }
        }

        function updateUI() {
            if(!isPlaying) return;
            const now = audioCtx.currentTime;
            if(sourceA && songA) {
                let remA = songA.duration - (now % songA.duration);
                document.getElementById('timeA').innerText = "-" + formatTime(remA);
                document.getElementById('barA').style.width = ((songA.duration - remA)/songA.duration*100) + "%";
            }
            if(sourceB && songB) {
                let remB = songB.duration - (now % songB.duration);
                document.getElementById('timeB').innerText = "-" + formatTime(remB);
                document.getElementById('barB').style.width = ((songB.duration - remB)/songB.duration*100) + "%";
            }
        }

        function formatTime(sec) {
            let m = Math.floor(sec/60);
            let s = Math.floor(sec%60);
            return (m<10?'0':'')+m+":"+(s<10?'0':'')+s;
        }
    </script>
</body>
</html>
"""

# แสดงผล HTML Mixer
st.components.v1.html(html_code, height=620)

# Footer สไตล์อาจารย์ต๊ะ
st.markdown("""
<div style='text-align: center; color: #444; font-size: 11px; margin-top: 10px; font-family: "Inter", sans-serif; letter-spacing: 1px;'>
    อยู่นิ่งๆ ไม่เจ็บตัว | Command Center | © 2026
</div>
""", unsafe_allow_html=True)
# ==========================================
# ส่วนที่ 1: การตั้งค่าหน้าจอและ CSS (ย้าย Logo มาตรงกลาง + เพิ่มสี Neon)
# ==========================================

# ต้องเรียก st.set_page_config() เป็นคำสั่งแรกสุดของ Streamlit
st.set_page_config(page_title="Synapse Studio Mixer", layout="centered")

# ฟังก์ชันสำหรับแปลงรูปเป็น Base64 (เพื่อให้รูปโชว์ใน CSS ได้)
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return "" # ถ้าไม่เจอรูปจะไม่โชว์อะไร

# โหลด Logo และแปลงเป็น HTML link
logo_html_link = ""
logo_base64 = get_base64_image("logo1.png")
if logo_base64:
    logo_html_link = f"data:image/png;base64,{logo_base64}"

# CSS สำหรับซ่อนส่วนเกิน, แปะ Logo ตรงกลาง, และสไตล์หัวข้อ
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');

    /* 1. ซ่อนเมนูเดิมและ Footer */
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    
    /* 2. ตั้งค่าพื้นหลังและดันเนื้อหาขึ้นให้สุด */
    .main {{ background-color: #000000; }}
    .block-container {{
        padding-top: 1rem;
        padding-bottom: 0rem;
        position: relative; /* เพื่อให้ Logo ลอยเทียบกับกล่องนี้ */
    }}

    /* 3. [จุดที่แก้ไข] สร้าง Logo ใหม่ไปแปะที่ "ตรงกลางด้านบน" */
    .block-container::before {{
        content: "";
        position: absolute;
        top: 20px; /* ระยะห่างจากขอบบน */
        left: 50%; /* เลื่อนมาตรงกลาง */
        transform: translateX(-50%) scale(1); /* ปรับให้จุดกลางรูปอยู่ตรงกลางหน้าจอเป๊ะ */
        width: 100px;  /* ปรับขนาด Logo ตามต้องการ (เช่น 120px) */
        height: 100px;
        background-image: url("{logo_html_link}");
        background-size: contain;
        background-repeat: no-repeat;
        z-index: 999;
        
        /* 4. เอฟเฟกต์แสง Neon Glow และ Animation ให้ Logo (กู้คืนสีสัน) */
        filter: drop-shadow(0 0 5px #ff00de); /* แสงเริ่มต้นสีชมพู */
        animation: logo-pulsing 2s infinite alternate; /* เล่น Animation */
    }}

    /* Animation สำหรับ Logo ขยายเข้า-ออก และแสงวูบวาบ */
    @keyframes logo-pulsing {{
        from {{ 
            filter: drop-shadow(0 0 5px #ff00de); 
            transform: translateX(-50%) scale(1); 
        }}
        to {{ 
            filter: drop-shadow(0 0 15px #ff00de); /* แสงเข้มขึ้น */
            transform: translateX(-50%) scale(1.05); /* ขยายใหญ่ขึ้นนิดหน่อย */
        }}
    }}

    /* 5. สไตล์หัวข้อแอป Neon (กู้คืนสีสันจัดเต็ม) */
    .neon-title {{
        font-family: 'Orbitron', sans-serif;
        color: #fff;
        text-align: center;
        /* แสง Neon สีชมพู-น้ำเงิน-ม่วง สลับกัน */
        text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 20px #ff00de, 0 0 30px #00f3ff, 0 0 40px #ff00de;
        font-size: 1.8rem;
        margin-top: 130px; /* เผื่อพื้นที่ให้ Logo ตรงกลาง */
        margin-bottom: 10px;
        letter-spacing: 2px;
    }}
    </style>
    """, unsafe_allow_html=True)

# แสดงหัวข้อแอป
st.markdown('<h1 class="neon-title">SYNAPSE อยู่นิ่งๆ ไม่เจ็บตัว</h1>', unsafe_allow_html=True)


# ==========================================
# ส่วนที่ 2: โค้ด HTML/JS สำหรับ Mixer และ Visualizer (สีสันกู้คืนเต็มสูบ)
# ==========================================

html_code = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: transparent; color: white; font-family: 'Inter', sans-serif; overflow: hidden; }
        
        /* สไตล์กล่องหลักและกล่องเพลง (เน้นขอบเรืองแสง) */
        .neon-box { border: 1px solid rgba(255, 255, 255, 0.1); background: rgba(10, 10, 10, 0.95); box-shadow: 0 0 20px rgba(0,243,255,0.1); }
        .deck-box { border-left: 4px solid; background: rgba(20, 20, 20, 0.8); transition: 0.3s; }
        .deck-box:hover { background: rgba(30, 30, 30, 1); }
        
        /* --- [จุดที่แก้ไข] ย่อขนาดกราฟเสียงให้เล็กลงอีกนิด --- */
        .visualizer-container { height: 120px; background: #000; border-radius: 12px; border: 1px solid #333; }
        
        /* ปุ่มสไตล์ Neon สะท้อนแสง (กู้คืนสี แดง/เขียว/ส้ม) */
        .btn-neon { transition: 0.2s; font-weight: bold; text-transform: uppercase; font-size: 11px; letter-spacing: 1px; }
        .neon-red { border: 2px solid #ff0055; color: #ff0055; text-shadow: 0 0 5px #ff0055; box-shadow: 0 0 10px rgba(255,0,85,0.3); }
        .neon-red:hover { background: #ff0055; color: white; box-shadow: 0 0 20px #ff0055; }
        .neon-green { border: 2px solid #00ffcc; color: #00ffcc; text-shadow: 0 0 5px #00ffcc; box-shadow: 0 0 10px rgba(0,255,204,0.3); }
        .neon-green:hover { background: #00ffcc; color: black; box-shadow: 0 0 20px #00ffcc; }
        
        /* แถบเวลา (กู้คืนการไล่เฉดสี ส้ม-ม่วง-น้ำเงิน) */
        .progress-bg { height: 5px; background: #1a1a1a; border-radius: 3px; overflow: hidden; }
        .progress-fill { height: 100%; width: 0%; background: linear-gradient(90deg, #ff00de, #00f3ff, #ff8c00); transition: width 0.1s linear; }
    </style>
</head>
<body>
    <div class="max-w-md mx-auto p-5 neon-box rounded-3xl">
        
        <canvas id="visualizer" class="visualizer-container w-full mb-5"></canvas>

        <div class="p-4 deck-box border-pink-600 rounded-r-xl mb-3">
            <div class="flex justify-between items-center mb-1">
                <span class="text-[10px] text-pink-500 font-bold uppercase tracking-widest">Deck A</span>
                <span id="timeA" class="text-[10px] font-mono text-gray-400">READY</span>
            </div>
            <div id="nameA" class="text-xs font-semibold mb-2 truncate text-gray-100">ยังไม่ได้โหลดเพลง A...</div>
            <input type="file" id="inputA" accept="audio/*" class="hidden" onchange="loadAudio(this.files[0], 'A')">
            <button onclick="document.getElementById('inputA').click()" class="text-[9px] bg-pink-900/40 px-3 py-1.5 rounded-lg border border-pink-500/50 text-pink-200">เลือกไฟล์ A</button>
            <div class="progress-bg mt-3"><div id="barA" class="progress-fill"></div></div>
        </div>

        <div class="p-4 deck-box border-cyan-400 rounded-r-xl mb-5">
            <div class="flex justify-between items-center mb-1">
                <span class="text-[10px] text-cyan-400 font-bold uppercase tracking-widest">Deck B</span>
                <span id="timeB" class="text-[10px] font-mono text-gray-400">READY</span>
            </div>
            <div id="nameB" class="text-xs font-semibold mb-2 truncate text-gray-100">ยังไม่ได้โหลดเพลง B...</div>
            <input type="file" id="inputB" accept="audio/*" class="hidden" onchange="loadAudio(this.files[0], 'B')">
            <button onclick="document.getElementById('inputB').click()" class="text-[9px] bg-cyan-900/40 px-3 py-1.5 rounded-lg border border-cyan-500/50 text-cyan-200">เลือกไฟล์ B</button>
            <div class="progress-bg mt-3"><div id="barB" class="progress-fill" style="background: #00ffcc;"></div></div>
        </div>

        <div class="grid grid-cols-2 gap-4">
            <button onclick="startPlaying()" id="btn-play" class="btn-neon neon-red py-3 rounded-2xl">Start Mix</button>
            <button onclick="startCrossfade()" id="btn-fade" class="btn-neon neon-green py-3 rounded-2xl">Crossfade</button>
        </div>
    </div>

    <script>
        let audioCtx, analyser, songA, songB, gainA, gainB, sourceA, sourceB;
        let isPlaying = false, current = 'A', dataArray;

        function initAudio() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = audioCtx.createAnalyser();
                analyser.fftSize = 128;
                dataArray = new Uint8Array(analyser.frequencyBinCount);
                draw();
            }
        }

        function draw() {
            requestAnimationFrame(draw);
            if (!analyser) return;
            analyser.getByteFrequencyData(dataArray);
            const canvas = document.getElementById('visualizer');
            const ctx = canvas.getContext('2d');
            
            // ล้างจอแบบ Fade เพื่อให้เกิดเงาตาม
            ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            const bWidth = (canvas.width / dataArray.length) * 2;
            let x = 0;
            for(let i = 0; i < dataArray.length; i++) {
                let h = (dataArray[i] / 255) * canvas.height;
                // [กู้คืนสีสัน] สีสะท้อนแสง ส้ม-ม่วง-น้ำเงิน-ส้ม
                ctx.fillStyle = `hsl(${{280 + i*4}}, 100%, 50%)`;
                ctx.fillRect(x, canvas.height - h, bWidth - 1, h);
                x += bWidth;
            }
            updateUI();
        }

        async function loadAudio(file, key) {
            initAudio();
            document.getElementById('name'+key).innerText = "Loading: " + file.name;
            const buffer = await audioCtx.decodeAudioData(await file.arrayBuffer());
            if(key === 'A') songA = buffer; else songB = buffer;
            document.getElementById('name'+key).innerText = file.name;
        }

        function startPlaying() {
            if (!songA || !songB) return alert("โหลดเพลงให้ครบทั้ง A และ B ก่อนครับอาจารย์!");
            if (isPlaying) return;

            sourceA = audioCtx.createBufferSource(); sourceA.buffer = songA;
            gainA = audioCtx.createGain();
            sourceA.connect(gainA).connect(analyser).connect(audioCtx.destination);
            
            sourceB = audioCtx.createBufferSource(); sourceB.buffer = songB;
            gainB = audioCtx.createGain(); gainB.gain.value = 0;
            sourceB.connect(gainB).connect(analyser).connect(audioCtx.destination);

            sourceA.start(0); sourceB.start(0);
            isPlaying = true; startTime = audioCtx.currentTime;
        }

        function startCrossfade() {
            if(!isPlaying) return;
            const now = audioCtx.currentTime;
            const dur = 5;
            if(current === 'A') {
                gainA.gain.linearRampToValueAtTime(1, now); gainA.gain.linearRampToValueAtTime(0, now+dur);
                gainB.gain.linearRampToValueAtTime(0, now); gainB.gain.linearRampToValueAtTime(1, now+dur);
                current = 'B';
            } else {
                gainB.gain.linearRampToValueAtTime(1, now); gainB.gain.linearRampToValueAtTime(0, now+dur);
                gainA.gain.linearRampToValueAtTime(0, now); gainA.gain.linearRampToValueAtTime(1, now+dur);
                current = 'A';
            }
        }

        function updateUI() {
            if(!isPlaying) return;
            const now = audioCtx.currentTime;
            if(sourceA && songA) {
                let remA = songA.duration - (now % songA.duration);
                document.getElementById('timeA').innerText = "-" + formatTime(remA);
                document.getElementById('barA').style.width = ((songA.duration - remA)/songA.duration*100) + "%";
            }
            if(sourceB && songB) {
                let remB = songB.duration - (now % songB.duration);
                document.getElementById('timeB').innerText = "-" + formatTime(remB);
                document.getElementById('barB').style.width = ((songB.duration - remB)/songB.duration*100) + "%";
            }
        }

        function formatTime(sec) {
            let m = Math.floor(sec/60);
            let s = Math.floor(sec%60);
            return (m<10?'0':'')+m+":"+(s<10?'0':'')+s;
        }
    </script>
</body>
</html>
"""

# แสดงผล HTML Mixer
st.components.v1.html(html_code, height=620)

# Footer สไตล์อาจารย์ต๊ะ
st.markdown("""
<div style='text-align: center; color: #444; font-size: 11px; margin-top: 10px; font-family: "Inter", sans-serif; letter-spacing: 1px;'>
    อยู่นิ่งๆ ไม่เจ็บตัว | Command Center | © 2026
</div>
""", unsafe_allow_html=True)
