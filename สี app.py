<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SYNAPSE: Math-Elastic Healer V.1</title>
    <style>
        body { background: #050505; color: #0f0; font-family: 'Courier New', monospace; margin: 0; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
        .top-section { height: 180px; border-bottom: 2px solid #0f0; position: relative; background: #000; }
        canvas { width: 100%; height: 100%; }
        .overlay { position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.8); padding: 10px; border: 1px solid #0f0; z-index: 10; }
        
        .controls { padding: 15px; display: flex; gap: 10px; background: #111; justify-content: center; border-bottom: 1px solid #333; }
        button { background: #000; color: #0f0; border: 1px solid #0f0; padding: 10px 15px; cursor: pointer; font-weight: bold; font-size: 12px; }
        button:hover { background: #0f0; color: #000; }
        button.active { background: #f00; color: #fff; border-color: #f00; animation: blink 1s infinite; }
        
        .grid-container { flex: 1; overflow-y: auto; padding: 10px; background: #000; }
        .grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 2px; }
        .cell { height: 45px; background: #0a0a0a; border: 1px solid #1a1a1a; display: flex; align-items: center; justify-content: center; font-size: 9px; color: #444; }
        .cell.active { background: #0f0 !important; color: #000 !important; box-shadow: 0 0 15px #0f0; transform: scale(1.05); z-index: 5; }
        .cell.base { border: 1px solid #fff; color: #fff; background: #111; }

        @keyframes blink { 50% { opacity: 0.5; } }
    </style>
</head>
<body>

<div class="top-section">
    <canvas id="viz"></canvas>
    <div class="overlay">
        <b style="color: #fff;">SYSTEM: MATH-ELASTIC (V.1)</b><br>
        <span id="status" style="font-size: 12px;">สถานะ: รอการบันทึกเสียงต้นแบบ C4...</span>
    </div>
</div>

<div class="controls">
    <button id="recBtn" onclick="handleRec()">1. อัดเสียง C4 (โดกลาง)</button>
    <input type="file" id="mp3File" accept="audio/*" style="display:none" onchange="loadMP3(this)">
    <button onclick="document.getElementById('mp3File').click()">2. เลือกเพลง MP3</button>
    <button id="startBtn" onclick="toggleEngine()" style="border-color: #0f0; color: #0f0;">3. เดินเครื่อง (START)</button>
</div>

<div class="grid-container">
    <div class="grid" id="grid"></div>
</div>

<script>
    const NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
    let audioCtx, masterGain, mp3Buffer, userBuffer;
    let isRunning = false, isRecording = false;
    let analyser, sourceNode;
    let lastTriggerTime = 0;
    const activeCells = new Set();

    // 1. สร้างตาราง 144 ช่อง
    const gridEl = document.getElementById('grid');
    for(let i=0; i<144; i++) {
        const div = document.createElement('div');
        div.className = 'cell' + (i === 60 ? ' base' : '');
        div.id = `c-${i}`;
        div.innerHTML = `${NOTES[i%12]}${Math.floor(i/12)}`;
        gridEl.appendChild(div);
    }

    // 2. เริ่มระบบ Audio
    function initAudio() {
        if(!audioCtx) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            masterGain = audioCtx.createGain();
            masterGain.connect(audioCtx.destination);
        }
    }

    // 3. จัดการการอัดเสียง (บันทึกตัวอย่างเสียงคุณต๊ะ)
    async function handleRec() {
        initAudio();
        const btn = document.getElementById('recBtn');
        if(!isRecording) {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const recorder = new MediaRecorder(stream);
            const chunks = [];
            recorder.ondataavailable = e => chunks.push(e.data);
            recorder.onstop = async () => {
                const blob = new Blob(chunks);
                const arrayBuffer = await blob.arrayBuffer();
                userBuffer = await audioCtx.decodeAudioData(arrayBuffer);
                document.getElementById('status').innerText = "✅ บันทึกเสียงต้นแบบสำเร็จ!";
            };
            recorder.start();
            btn.classList.add('active');
            btn.innerText = "กำลังอัด... (ร้อง 'อาาา' โน้ต C4)";
            isRecording = true;
            setTimeout(() => { recorder.stop(); btn.classList.remove('active'); btn.innerText = "อัดเสียงใหม่"; isRecording = false; }, 3000);
        }
    }

    // 4. โหลดไฟล์ MP3
    async function loadMP3(input) {
        initAudio();
        const file = input.files[0];
        if(!file) return;
        document.getElementById('status').innerText = "⏳ กำลังถอดรหัสเพลง...";
        const arrayBuffer = await file.arrayBuffer();
        mp3Buffer = await audioCtx.decodeAudioData(arrayBuffer);
        document.getElementById('status').innerText = "✅ เพลงพร้อมแล้ว! กด START";
    }

    // 5. เดินเครื่องคำนวณ (The Math Engine)
    function toggleEngine() {
        if(!userBuffer || !mp3Buffer) return alert("อัดเสียงและเลือกเพลงก่อนครับ!");
        const btn = document.getElementById('startBtn');
        if(!isRunning) {
            isRunning = true;
            btn.innerText = "STOP SYSTEM";
            btn.style.borderColor = "#f00";
            btn.style.color = "#f00";
            runEngine();
        } else {
            location.reload(); // รีเซ็ตระบบง่ายที่สุด
        }
    }

    function runEngine() {
        sourceNode = audioCtx.createBufferSource();
        sourceNode.buffer = mp3Buffer;
        analyser = audioCtx.createAnalyser();
        analyser.fftSize = 2048;
        
        sourceNode.connect(analyser);
        analyser.connect(audioCtx.destination);
        sourceNode.start();

        const canvas = document.getElementById('viz');
        const ctx = canvas.getContext('2d');
        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        function loop() {
            if(!isRunning) return;
            analyser.getByteFrequencyData(dataArray);
            
            // วาดกราฟ
            ctx.fillStyle = 'rgba(0,0,0,0.2)';
            ctx.fillRect(0,0,canvas.width, canvas.height);
            
            let maxVal = 0, maxIdx = 0;
            for(let i=0; i<dataArray.length; i++) {
                if(dataArray[i] > maxVal) { maxVal = dataArray[i]; maxIdx = i; }
                if(dataArray[i] > 100) {
                    ctx.fillStyle = '#0f0';
                    ctx.fillRect(i * 2, canvas.height - dataArray[i]/2, 1, dataArray[i]/2);
                }
            }

            // --- ตรรกะคณิตศาสตร์ (Real-time Pitch Detection) ---
            if(maxVal > 150) { // ความดังต้องถึงเกณฑ์
                const freq = maxIdx * (audioCtx.sampleRate / analyser.fftSize);
                if(freq > 80 && freq < 1200) {
                    // สูตรแปลง Hz เป็น MIDI Index (0-143)
                    const midi = Math.round(12 * Math.log2(freq / 440) + 69);
                    const gridIdx = midi + 12; // ปรับ Offset ให้ตรงตาราง

                    if(gridIdx >= 0 && gridIdx < 144) {
                        const now = audioCtx.currentTime;
                        // ป้องกันเสียงซ้อนกันมากเกินไป (Gate Time 100ms)
                        if(now - lastTriggerTime > 0.1) {
                            triggerVoice(gridIdx, maxVal/255);
                            lastTriggerTime = now;
                        }
                    }
                }
            }
            requestAnimationFrame(loop);
        }
        loop();
    }

    // 6. ฟังก์ชันเล่นเสียงที่ผ่านการ "ยืดหด" (Elastic Shift)
    function triggerVoice(idx, vol) {
        const cell = document.getElementById(`c-${idx}`);
        if(cell) {
            cell.classList.add('active');
            setTimeout(() => cell.classList.remove('active'), 150);
        }

        const voice = audioCtx.createBufferSource();
        voice.buffer = userBuffer;
        
        // --- MATH: Pitch Shifting Ratio ---
        // สูตร: Rate = 2 ^ ((Target - Base) / 12)
        // Base ของเราคือ C4 (Index 60)
        const ratio = Math.pow(2, (idx - 60) / 12);
        voice.playbackRate.setTargetAtTime(ratio, audioCtx.currentTime, 0.01);

        const vGain = audioCtx.createGain();
        vGain.gain.setValueAtTime(0, audioCtx.currentTime);
        vGain.gain.linearRampToValueAtTime(vol * 0.7, audioCtx.currentTime + 0.05);
        vGain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.5);

        voice.connect(vGain);
        vGain.connect(masterGain);
        voice.start();
        voice.stop(audioCtx.currentTime + 0.6);
    }
</script>

</body>
</html>
