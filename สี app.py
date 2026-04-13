import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="centered")

# --- UI สเปกตามสั่ง + กราฟ 7 สี ---
player_ui = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: transparent; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        
        /* กรอบหลักตามสเปก */
        .main-frame {
            width: 400px; height: 500px;
            background-color: rgba(0, 0, 0, 0.5);
            border: 4px solid;
            border-image: linear-gradient(to bottom right, #8b00ff, #ff0000) 1;
            border-radius: 0px;
            box-shadow: 0 0 15px #00f2fe;
            padding: 10px;
            color: #f0f0f0;
            font-family: sans-serif;
            box-sizing: border-box;
            display: flex; flex-direction: column;
        }

        /* กรอบในสำหรับกราฟเสียง */
        .inner-panel {
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid #8b00ff;
            box-shadow: inset 0 0 10px #00f2fe;
            padding: 5px; margin-bottom: 15px;
        }

        #viz-canvas { width: 100%; height: 120px; background: #000; }

        /* ปุ่มสไตล์ Synapse */
        .cmd-btn {
            width: 100%; background: transparent; border: 2px solid #ff0000;
            color: #f0f0f0; padding: 10px; font-weight: bold;
            margin-top: 8px; cursor: pointer; transition: 0.3s;
            box-shadow: 0 0 5px #ff0000; text-transform: uppercase;
        }
        .cmd-btn:hover { background: #00f2fe; color: #000; box-shadow: 0 0 20px #00f2fe; border-color: #00f2fe; }

        /* แถบเลื่อน EQ */
        .eq-label { font-size: 10px; color: #00f2fe; margin-top: 5px; }
        input[type=range] { -webkit-appearance: none; width: 100%; background: transparent; }
        input[type=range]::-webkit-slider-runnable-track { height: 3px; background: #8b00ff; }
        input[type=range]::-webkit-slider-thumb { 
            -webkit-appearance: none; height: 12px; width: 12px; 
            background: #f0f0f0; border-radius: 0; margin-top: -4px; box-shadow: 0 0 8px #00f2fe;
        }
    </style>
</head>
<body>
    <div class="main-frame">
        <div style="text-align:center; font-weight:bold; letter-spacing:2px; margin-bottom:10px;">SYNAPSE COMMAND CENTER</div>
        
        <input type="file" id="file-up" class="text-[10px] mb-2 w-full text-gray-400">

        <div class="inner-panel">
            <canvas id="viz-canvas"></canvas>
        </div>

        <div id="track-info" class="text-[12px] truncate mb-4 text-[#00f2fe]">WAITING FOR SCAN...</div>

        <div class="grid grid-cols-3 gap-2 mb-4">
            <div><div class="eq-label">BASS</div><input type="range" id="low" min="-20" max="20" value="0"></div>
            <div><div class="eq-label">MID</div><input type="range" id="mid" min="-20" max="20" value="0"></div>
            <div><div class="eq-label">HIGH</div><input type="range" id="high" min="-20" max="20" value="0"></div>
        </div>

        <button id="play-btn" class="cmd-btn">PLAY / PAUSE</button>
        <button id="vocal-btn" class="cmd-btn" style="border-color:#8b00ff; box-shadow:0 0 5px #8b00ff;">VOCAL CANCEL</button>

        <div style="margin-top:auto; text-align:center; font-size:10px; opacity:0.5;">อยู่นิ่งๆ ไม่เจ็บตัว</div>
    </div>

    <audio id="audio" crossorigin="anonymous"></audio>

    <script>
        let aCtx, src, ana, lowF, midF, highF, split, merg, inv, isCut=false;
        const audio = document.getElementById('audio');
        const canvas = document.getElementById('viz-canvas');
        const ctx = canvas.getContext('2d');

        function init() {
            if (aCtx) return;
            aCtx = new AudioContext();
            src = aCtx.createMediaElementSource(audio);
            ana = aCtx.createAnalyser();
            ana.fftSize = 256;

            lowF = aCtx.createBiquadFilter(); lowF.type = 'lowshelf'; lowF.frequency.value = 250;
            midF = aCtx.createBiquadFilter(); midF.type = 'peaking'; midF.frequency.value = 1000;
            highF = aCtx.createBiquadFilter(); highF.type = 'highshelf'; highF.frequency.value = 4000;

            split = aCtx.createChannelSplitter(2);
            merg = aCtx.createChannelMerger(2);
            inv = aCtx.createGain(); inv.gain.value = -1;

            route(false);
            draw();
        }

        function route(cut) {
            src.disconnect(); lowF.disconnect(); midF.disconnect(); highF.disconnect();
            if(cut) {
                src.connect(split); split.connect(merg, 0, 0); split.connect(inv, 1, 0); inv.connect(merg, 0, 0);
                merg.connect(lowF);
            } else { src.connect(lowF); }
            lowF.connect(midF); midF.connect(highF); highF.connect(ana); ana.connect(aCtx.destination);
        }

        document.getElementById('file-up').onchange = (e) => {
            init();
            const file = e.target.files[0];
            audio.src = URL.createObjectURL(file);
            document.getElementById('track-info').innerText = "SCANNING: " + file.name;
            audio.play();
        };

        document.getElementById('play-btn').onclick = () => { init(); audio.paused ? audio.play() : audio.pause(); };
        document.getElementById('vocal-btn').onclick = (e) => {
            isCut = !isCut; route(isCut);
            e.target.style.background = isCut ? "#8b00ff" : "transparent";
        };

        // กราฟ 7 สี (Rainbow Visualizer)
        function draw() {
            requestAnimationFrame(draw);
            const data = new Uint8Array(ana.frequencyBinCount);
            ana.getByteFrequencyData(data);
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            const barWidth = (canvas.width / data.length) * 2.5;
            let x = 0;

            for(let i = 0; i < data.length; i++) {
                let h = data[i] / 2;
                // ใช้ HSL เพื่อไล่สีสายรุ้ง (7 สี) ตามตำแหน่งแท่งกราฟ
                let hue = i * (360 / data.length); 
                ctx.fillStyle = `hsl(${hue}, 100%, 50%)`;
                ctx.fillRect(x, canvas.height - h, barWidth, h);
                x += barWidth + 1;
            }
        }

        document.getElementById('low').oninput = (e) => lowF.gain.value = e.target.value;
        document.getElementById('mid').oninput = (e) => midF.gain.value = e.target.value;
        document.getElementById('high').oninput = (e) => highF.gain.value = e.target.value;
    </script>
</body>
</html>
"""

components.html(player_ui, height=550)
