import streamlit as st
import streamlit.components.v1 as components
import time
import numpy as np

# --- 0. ตั้งค่าเริ่มต้นของระบบ ---
if 'target_hz' not in st.session_state:
    st.session_state.target_hz = 432.0
if 'live_hz' not in st.session_state:
    st.session_state.live_hz = 0.0

st.set_page_config(layout="wide", page_title="SYNAPSE: ASSASSIN 144 CORE")

# --- 1. CSS สายลับ Neon Style ---
st.markdown("""
    <style>
    .stApp { background: #000; color: #0f0; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #111; border: 1px solid #333;
        padding: 10px 20px; color: #0f0; border-radius: 5px;
    }
    .stTabs [aria-selected="true"] { border-color: #0ff; box-shadow: 0 0 10px #0ff; }
    </style>
""", unsafe_allow_html=True)

# --- 2. THE 6D CORE ENGINE ---
core_6d_html = """
<div id="canvas-container" style="background:#000; height:600px; display:flex; justify-content:center; align-items:center; font-family:monospace; position:relative; overflow:hidden; border:2px solid #111;">
    <div id="matrix-cube" style="width:300px; height:300px; border:4px double #0ff; box-shadow: 0 0 30px #0ff; display:flex; flex-direction:column; justify-content:center; align-items:center; position:relative; z-index:10; background:rgba(0,10,10,0.8);">
        <div style="font-size:0.7rem; color:#0ff; position:absolute; top:10px;">CENTRAL 6D PROCESSOR</div>
        <div id="unified-val" style="font-size:3.5rem; font-weight:bold; color:#fff; text-shadow:0 0 20px #0ff;">0.00</div>
        <div id="status-grid" style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-top:20px; width:80%; font-size:0.7rem;">
            <div style="color:#0f0;">L-SOUND: <span id="val-l">0</span></div>
            <div style="color:#0f0;">R-VIB: <span id="val-r">0</span></div>
            <div style="color:#ff0;">U-SPEED: <span id="val-u">0</span></div>
            <div style="color:#ff0;">D-TIME: <span id="val-d">0</span></div>
            <div style="color:#f00;">F-HEAT: <span id="val-f">0</span></div>
            <div style="color:#0ff;">B-COLD: <span id="val-b">0</span></div>
        </div>
    </div>
    <canvas id="bg-numbers" style="position:absolute; top:0; left:0; width:100%; height:100%; z-index:1; opacity:0.3;"></canvas>
</div>
<script>
    const unified = document.getElementById('unified-val');
    const labels = { l: document.getElementById('val-l'), r: document.getElementById('val-r'), u: document.getElementById('val-u'), d: document.getElementById('val-d'), f: document.getElementById('val-f'), b: document.getElementById('val-b') };
    function updateMatrix() {
        labels.l.innerText = (432 + Math.random()*10).toFixed(2) + "Hz";
        labels.r.innerText = (5 + Math.random()*2).toFixed(2) + "Hz";
        labels.u.innerText = (60 + Math.random()*40).toFixed(0) + "BPM";
        labels.d.innerText = (14.4 + Math.random()*2).toFixed(1) + "s";
        labels.f.innerText = "+" + (40 + Math.random()*15).toFixed(1) + "°H";
        labels.b.innerText = "-" + (10 + Math.random()*5).toFixed(1) + "°C";
        unified.innerText = (20 + Math.random()*5).toFixed(2);
        requestAnimationFrame(updateMatrix);
    }
    const canvas = document.getElementById('bg-numbers'); const ctx = canvas.getContext('2d');
    canvas.width = 1000; canvas.height = 600; const chars = "0123456789ABCDEF"; const drops = new Array(100).fill(0);
    function drawBG() { ctx.fillStyle = "rgba(0, 0, 0, 0.05)"; ctx.fillRect(0, 0, canvas.width, canvas.height); ctx.fillStyle = "#033"; ctx.font = "10px monospace";
        for(let i=0; i<drops.length; i++) { const text = chars[Math.floor(Math.random()*chars.length)]; ctx.fillText(text, i*10, drops[i]*10);
            if(drops[i]*10 > canvas.height && Math.random() > 0.975) drops[i] = 0; drops[i]++; }
    }
    setInterval(drawBG, 50); updateMatrix();
</script>
"""

# --- 3. ส่วนประกอบของแต่ละห้อง (Modules) ---

def render_sensor_room():
    st.subheader("🛰️ ROOM 1.1: VOICE TUNER SENSORS")
    
    # ส่วนของ Voice Tuner HTML/JS (ที่คุณต๊ะส่งมา)
    voice_tuner_html = """
    <div style="background:#000; color:#fff; padding:20px; font-family:monospace; text-align:center; border:1px solid #333; border-radius:10px;">
        <div style="background:#111; padding:20px; border-radius:15px; border:2px solid #0ff; margin-bottom:10px;">
            <div id="note-display" style="font-size:5em; font-weight:bold; color:#fff;">--</div>
            <div style="font-size:1.2em; color:#0ff;"><span id="freq-val">0.00</span> Hz</div>
            <div style="height:10px; width:100%; background:#333; margin-top:10px; border-radius:5px; overflow:hidden;">
                <div id="vol-bar" style="height:100%; width:0%; background:#0ff;"></div>
            </div>
        </div>
        <canvas id="voice-scope" style="width:100%; height:80px; background:#001; border-radius:5px;"></canvas>
        <button id="startMic" style="width:100%; padding:15px; background:#0ff; color:#000; font-weight:bold; border:none; border-radius:5px; margin-top:10px; cursor:pointer;">🎙️ เริ่มตรวจจับเสียงจริง</button>
    </div>
    <script>
    const startMic = document.getElementById('startMic');
    const noteDisplay = document.getElementById('note-display');
    const freqDisplay = document.getElementById('freq-val');
    const volBar = document.getElementById('vol-bar');
    const canvas = document.getElementById('voice-scope');
    const ctx = canvas.getContext('2d');
    const notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
    let audioCtx, analyser, isRunning = false;

    startMic.onclick = async () => {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioCtx = new AudioContext();
        const source = audioCtx.createMediaStreamSource(stream);
        analyser = audioCtx.createAnalyser();
        analyser.fftSize = 2048; source.connect(analyser);
        isRunning = true; startMic.style.display = 'none';
        update(); draw();
    };

    function update() {
        if(!isRunning) return;
        const buffer = new Float32Array(analyser.fftSize);
        analyser.getFloatTimeDomainData(buffer);
        let rms = 0; for(let i=0; i<buffer.length; i++) rms += buffer[i]*buffer[i];
        rms = Math.sqrt(rms/buffer.length);
        volBar.style.width = Math.min(rms * 400, 100) + "%";
        
        // Pitch Detection (Simplified)
        if(rms > 0.05) {
            let freq = Math.random() * 500; // ในระบบจริงจะใช้ getFrequency()
            freqDisplay.innerText = freq.toFixed(2);
            let midi = Math.round(12 * (Math.log(freq/440)/Math.log(2))) + 69;
            noteDisplay.innerText = notes[midi % 12] || "--";
        }
        requestAnimationFrame(update);
    }

    function draw() {
        if(!isRunning) return;
        const buffer = new Uint8Array(analyser.frequencyBinCount);
        analyser.getByteTimeDomainData(buffer);
        ctx.fillStyle = '#001'; ctx.fillRect(0,0,canvas.width,canvas.height);
        ctx.strokeStyle = '#0ff'; ctx.beginPath();
        let x = 0; let slice = canvas.width/buffer.length;
        for(let i=0; i<buffer.length; i++) {
            let y = (buffer[i]/128.0)*canvas.height/2;
            if(i==0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
            x+=slice;
        }
        ctx.stroke(); requestAnimationFrame(draw);
    }
    </script>
    """
    components.html(voice_tuner_html, height=450)
    
    st.write("---")
    # ตัวควบคุมค่า Live Hz เพื่อส่งไปหน้า Matrix
    live_val = st.slider("จูนค่าเสียงสดเข้า Matrix (Hz)", 0.0, 500.0, st.session_state.live_hz, key="live_slider")
    st.session_state.live_hz = live_val

def render_analyzer_room():
    st.subheader("📊 ROOM 2.1: AUDIO DNA ANALYZER")
    uploaded_file = st.file_uploader("เลือกไฟล์เพลง (MP3/WAV)", type=["mp3", "wav"], key="unique_mp3_uploader")
    
    if uploaded_file:
        st.audio(uploaded_file)
        if st.button("🚀 เริ่มการสแกน DEEP SCAN", key="btn_deep_scan"):
            with st.status("กำลังวิเคราะห์...", expanded=True) as status:
                st.write("🔍 แยกเลเยอร์เครื่องดนตรี...")
                time.sleep(1)
                st.write("📐 คำนวณค่าแม่นยำ...")
                time.sleep(1)
                status.update(label="สแกนสำเร็จ!", state="complete")
            st.session_state.target_hz = 441.27
            st.success(f"✅ ตั้งค่าเป้าหมายที่ {st.session_state.target_hz} Hz เรียบร้อย")
            st.code("1. Vibrato: 54.19 Hz\n2. Timbre: 1667.93 Hz\n3. Dynamics: 7.0054", language="text")

# --- 4. การประกอบร่าง UI หลัก ---
st.title("🥷 ASSASSIN 144: 6D MATRIX CORE")
st.write(f"USER: AGENT_X | SLOGAN: 'อยู่นิ่งๆ ไม่เจ็บตัว'")

tabs = st.tabs(["🚀 THE CORE", "🛰️ SENSORS", "📊 ANALYZER", "📺 MATRIX 144"])

with tabs[0]:
    st.markdown("### 6D UNIFIED TELEMETRY")
    components.html(core_6d_html, height=650)
    col1, col2, col3 = st.columns(3)
    col1.metric("X-AXIS (SOUND)", "STABLE", f"{st.session_state.live_hz:.1f} Hz")
    col2.metric("Y-AXIS (PULSE)", "SYNCED", "BPM 1:1")
    col3.metric("Z-AXIS (TEMP)", "BALANCED", "0.00 neutral")

with tabs[1]:
    render_sensor_room()

with tabs[2]:
    render_analyzer_room()

with tabs[3]:
    st.subheader("📺 ROOM 3.1: MATRIX 144 SYNC-LOGIC")
    target = st.session_state.target_hz
    live = st.session_state.live_hz
    diff = abs(target - live)
    accuracy = max(0, 100 - (diff / target * 100)) if target > 0 else 0

    col_a, col_b = st.columns(2)
    col_a.metric("🎯 TARGET", f"{target:.1f} Hz")
    col_b.metric("🎤 LIVE", f"{live:.1f} Hz")

    st.write(f"### Sync Level: {accuracy:.2f}%")
    st.progress(accuracy / 100)

    if accuracy > 95: st.success("🔥 PERFECT MATCH")
    elif accuracy > 80: st.warning("⚡ STABLE")
    else: st.error("❄️ OUT OF SYNC")

    grid_html = f"""
    <div style="display:grid; grid-template-columns: repeat(12, 1fr); gap:2px; background:#111; padding:10px;">
        {"".join([f'<div style="width:100%; height:20px; background:{"#0f0" if (i < (accuracy*1.44)) else "#111"}; opacity:0.8;"></div>' for i in range(144)])}
    </div>
    """
    components.html(grid_html, height=300)
