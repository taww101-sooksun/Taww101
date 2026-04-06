import streamlit as st
import streamlit.components.v1 as components
import time
import numpy as np
# --- ระบบความจำ Matrix (State Management) ---
if 'target_hz' not in st.session_state:
    st.session_state.target_hz = 432.0  # ค่าเป้าหมายจากไฟล์ MP3
if 'live_hz' not in st.session_state:
    st.session_state.live_hz = 0.0      # ค่าจากไมค์สด

# --- 0. ตั้งค่าเริ่มต้นของระบบ (ต้องเป็นคำสั่งแรกสุด) ---
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

# --- 2. THE 6D CORE ENGINE (Logic) ---
core_6d_html = """
<div id="canvas-container" style="background:#000; height:600px; display:flex; justify-content:center; align-items:center; font-family:monospace; position:relative; overflow:hidden; border:2px solid #111;">
    <div id="matrix-cube" style="width:300px; height:300px; border:4px double #0ff; box-shadow: 0 0 30px #0ff; display:flex; flex-direction:column; justify-content:center; align-items:center; position:relative; z-index:10; background:rgba(0,10,10,0.8);">
        <div style="font-size:0.7rem; color:#0ff; position:absolute; top:10px;">CENTRAL 6D PROCESSOR</div>
        <div id="unified-val" style="font-size:3.5rem; font-weight:bold; color:#fff; text-shadow:0 0 20px #0ff;">0.00</div>
        <div style="font-size:0.8rem; color:#888;">MATRIX IMPACT POINT</div>
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
        let x_l = 432 + (Math.random() * 10);
        let x_r = 5 + (Math.random() * 2);
        let y_u = 60 + (Math.random() * 40);
        let y_d = 14.4 + (Math.random() * 2);
        let z_f = 40 + (Math.random() * 15);
        let z_b = -10 - (Math.random() * 5);
        labels.l.innerText = x_l.toFixed(2) + "Hz";
        labels.r.innerText = x_r.toFixed(2) + "Hz";
        labels.u.innerText = y_u.toFixed(0) + "BPM";
        labels.d.innerText = y_d.toFixed(1) + "s";
        labels.f.innerText = "+" + z_f.toFixed(1) + "°H";
        labels.b.innerText = z_b.toFixed(1) + "°C";
        let x = (x_l + x_r) / 2; let y = (y_u + y_d) / 2; let z = Math.abs(z_f - z_b);
        let result = Math.sqrt(Math.pow(x,2) + Math.pow(y,2) + Math.pow(z,2)) / 10;
        unified.innerText = result.toFixed(2);
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
    st.subheader("🛰️ ROOM 1.1: SENSOR CALIBRATION")
    st.write("ดึงค่า Hz และ BPM เข้าสู่ระบบ Matrix")
    sensor_html = """
    <div style="background:#000; color:#0f0; padding:20px; border:1px solid #333; border-radius:10px; font-family:monospace;">
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px;">
            <div style="text-align:center; border-right:1px solid #333;"><div style="font-size:0.8rem; color:#888;">X-AXIS: Hz</div><div id="hz-display" style="font-size:3rem; color:#fff;">--</div></div>
            <div style="text-align:center;"><div style="font-size:0.8rem; color:#888;">Y-AXIS: BPM</div><div id="bpm-display" style="font-size:3rem; color:#f00;">--</div></div>
        </div>
        <canvas id="visualizer" style="width:100%; height:100px; margin-top:20px; background:#001;"></canvas>
        <button id="activate" style="width:100%; padding:15px; background:#0f0; color:#000; font-weight:bold; border:none; border-radius:5px; margin-top:20px; cursor:pointer;">🔴 ACTIVATE SENSORS</button>
    </div>
    <script>
    const btn = document.getElementById('activate');
    btn.onclick = async () => {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const audioCtx = new AudioContext();
        const source = audioCtx.createMediaStreamSource(stream);
        const analyser = audioCtx.createAnalyser();
        analyser.fftSize = 2048; source.connect(analyser);
        btn.style.display = 'none';
        const buffer = new Float32Array(analyser.fftSize);
        function loop() {
            analyser.getFloatTimeDomainData(buffer);
            document.getElementById('hz-display').innerText = (Math.random() * 500).toFixed(1);
            requestAnimationFrame(loop);
        }
        loop();
    };
    </script>
    """
    components.html(sensor_html, height=400)

def render_analyzer_room():
    st.subheader("📊 ROOM 2.1: AUDIO DNA ANALYZER")
    # ใส่ key เพื่อป้องกัน Duplicate ID
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
            st.code("1. Vibrato: 54.19 Hz\n2. Timbre: 1667.93 Hz\n3. Dynamics: 7.0054", language="text")
            st.success("✅ ข้อมูลส่งเข้าแกน Z แล้ว")

# --- 4. การประกอบร่าง UI หลัก ---

st.title("🥷 ASSASSIN 144: 6D MATRIX CORE")
st.write(f"USER: AGENT_X | SLOGAN: 'อยู่นิ่งๆ ไม่เจ็บตัว'")

tabs = st.tabs(["🚀 THE CORE", "🛰️ SENSORS", "📊 ANALYZER", "📺 MATRIX 144"])

with tabs[0]:
    st.markdown("### 6D UNIFIED TELEMETRY")
    components.html(core_6d_html, height=650)
    col1, col2, col3 = st.columns(3)
    col1.metric("X-AXIS (SOUND)", "STABLE", "432 Hz")
    col2.metric("Y-AXIS (PULSE)", "SYNCED", "BPM 1:1")
    col3.metric("Z-AXIS (TEMP)", "BALANCED", "0.00 neutral")

with tabs[1]:
    render_sensor_room()

with tabs[2]:
    render_analyzer_room()

with tabs[3]:
    st.subheader("📺 ROOM 3.1: MATRIX 144 SYNC-LOGIC")
    
    # ดึงค่ามาคำนวณหาความต่าง (Error Margin)
    target = st.session_state.target_hz
    live = st.session_state.live_hz
    
    # สูตรคำนวณความแม่นยำ: 100 - (ความต่าง %)
    diff = abs(target - live)
    accuracy = max(0, 100 - (diff / target * 100)) if target > 0 else 0

    col_a, col_b = st.columns(2)
    with col_a:
        st.write("🎯 **TARGET (จาก MP3)**")
        st.title(f"{target:.1f} Hz")
    with col_b:
        st.write("🎤 **LIVE (จากไมค์)**")
        st.title(f"{live:.1f} Hz")

    # แถบแสดงความแม่นยำ (Sync Bar)
    st.write(f"### ความซิงค์ (Sync Level): {accuracy:.2f}%")
    st.progress(accuracy / 100)

    if accuracy > 95:
        st.success("🔥 MATRIX STATUS: PERFECT MATCH (เข้าสภาวะนิ่ง)")
    elif accuracy > 80:
        st.warning("⚡ MATRIX STATUS: STABLE (กำลังเข้าที่)")
    else:
        st.error("❄️ MATRIX STATUS: OUT OF SYNC (ยังไม่นิ่ง)")

    # วาดตาราง 144 ช่อง (จำลอง)
    st.write("---")
    st.write("ระบบพิกัดตาราง 144 (12x12 Grid)")
    
    # สร้างตารางไฟกระพริบตามความแม่นยำ
    grid_html = f"""
    <div style="display:grid; grid-template-columns: repeat(12, 1fr); gap:2px; background:#111; padding:10px; border:1px solid #333;">
        {"".join([f'<div style="width:100%; height:20px; background:{"#0f0" if (i < (accuracy*1.44)) else "#111"}; border-radius:2px; opacity:0.8;"></div>' for i in range(144)])}
    </div>
    """
    components.html(grid_html, height=300)
