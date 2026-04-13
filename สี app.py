import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SYNAPSE PRO PLAYER", layout="centered")

# --- สไตล์นีออน (อยู่นิ่งๆ ไม่เจ็บตัว) ---
st.markdown("""
    <style>
    .stApp { background-color: #000; color: #00f2fe; }
    header, footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; text-shadow: 0 0 10px #00f2fe;'>SYNAPSE PRO</h1>", unsafe_allow_html=True)

# --- 🧪 ส่วนของ HTML + JavaScript (ใส่ความสามารถทั้งหมดที่คุณต้องการ) ---
player_code = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: transparent; color: #00f2fe; overflow: hidden; }
        .neon-box { border: 1px solid #00f2fe; box-shadow: 0 0 10px #00f2fe; border-radius: 20px; padding: 20px; }
        .slider { -webkit-appearance: none; width: 100%; height: 4px; background: #333; outline: none; border-radius: 10px; }
        .slider::-webkit-slider-thumb { -webkit-appearance: none; width: 12px; height: 12px; background: #00f2fe; border-radius: 50%; cursor: pointer; }
        canvas { width: 100%; height: 80px; background: #111; border-radius: 10px; }
    </style>
</head>
<body>
    <div class="neon-box">
        <input type="file" id="upload" accept="audio/*" class="text-xs mb-4 w-full">
        <canvas id="viz"></canvas>
        <div id="name" class="text-center font-bold my-2 truncate">รอยืนยันไฟล์...</div>
        
        <div class="grid grid-cols-3 gap-2 text-[10px] text-center mb-4">
            <div>BASS<br><input type="range" id="b" min="-20" max="20" value="0" class="slider"></div>
            <div>MID<br><input type="range" id="m" min="-20" max="20" value="0" class="slider"></div>
            <div>TREBLE<br><input type="range" id="h" min="-20" max="20" value="0" class="slider"></div>
        </div>

        <div class="flex gap-2">
            <button id="p" class="flex-1 bg-[#00f2fe] text-black font-bold py-2 rounded-lg text-sm">PLAY/PAUSE</button>
            <button id="v" class="flex-1 border border-[#ff007f] text-[#ff007f] font-bold py-2 rounded-lg text-sm">VOCAL CUT</button>
        </div>
    </div>

    <audio id="a" crossorigin="anonymous"></audio>

    <script>
        let ctx, src, ana, g, l, m, h, spl, mer, inv, isCut = false;
        const a = document.getElementById('a');
        const canvas = document.getElementById('viz');
        const ctxt = canvas.getContext('2d');

        function setup() {
            if (ctx) return;
            ctx = new AudioContext();
            src = ctx.createMediaElementSource(a);
            ana = ctx.createAnalyser();
            ana.fftSize = 128;
            l = ctx.createBiquadFilter(); l.type = 'lowshelf'; l.frequency.value = 250;
            m = ctx.createBiquadFilter(); m.type = 'peaking'; m.frequency.value = 1000;
            h = ctx.createBiquadFilter(); h.type = 'highshelf'; h.frequency.value = 4000;
            g = ctx.createGain();
            spl = ctx.createChannelSplitter(2);
            mer = ctx.createChannelMerger(2);
            inv = ctx.createGain(); inv.gain.value = -1;
            connect(false);
            draw();
        }

        function connect(cut) {
            src.disconnect(); l.disconnect(); m.disconnect(); h.disconnect(); g.disconnect();
            if(cut) {
                src.connect(spl); spl.connect(mer, 0, 0); spl.connect(inv, 1, 0); inv.connect(mer, 0, 0);
                mer.connect(l);
            } else { src.connect(l); }
            l.connect(m); m.connect(h); h.connect(g); g.connect(ana); ana.connect(ctx.destination);
        }

        document.getElementById('upload').onchange = (e) => {
            setup();
            const file = e.target.files[0];
            a.src = URL.createObjectURL(file);
            document.getElementById('name').innerText = file.name;
            a.play();
        };

        document.getElementById('p').onclick = () => { setup(); if(a.paused) a.play(); else a.pause(); };
        document.getElementById('v').onclick = (e) => { 
            isCut = !isCut; connect(isCut);
            e.target.style.background = isCut ? "#ff007f" : "transparent";
            e.target.style.color = isCut ? "#fff" : "#ff007f";
        };

        document.getElementById('b').oninput = (e) => l.gain.value = e.target.value;
        document.getElementById('m').oninput = (e) => m.gain.value = e.target.value;
        document.getElementById('h').oninput = (e) => h.gain.value = e.target.value;

        function draw() {
            requestAnimationFrame(draw);
            const data = new Uint8Array(ana.frequencyBinCount);
            ana.getByteFrequencyData(data);
            ctxt.clearRect(0,0,canvas.width,canvas.height);
            data.forEach((v, i) => {
                ctxt.fillStyle = '#00f2fe';
                ctxt.fillRect(i*3, canvas.height - v/3, 2, v/3);
            });
        }
    </script>
</body>
</html>
"""

# แสดงผลเครื่องเล่นเพลงใน Streamlit
components.html(player_code, height=450)

st.info("💡 คำแนะนำ: เมื่อรันใน Streamlit ต้องกด 'PLAY' หรือ 'เลือกไฟล์' ก่อนเพื่อให้ Browser ยอมให้ระบบเสียงทำงานครับ")
