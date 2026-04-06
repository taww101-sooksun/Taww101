import streamlit as st
import streamlit.components.v1 as components
import time

st.set_page_config(layout="wide", page_title="SYNAPSE: ASSASSIN 144 CORE")

# --- CSS สายลับ Neon Style ---
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

# --- 6D CORE ENGINE (HTML/JS/CSS) ---
# นี่คือส่วนที่จะคำนวณเลข 6 ทิศทางสวนกันกลางจอ
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

    <div style="position:absolute; width:100%; height:1px; background:rgba(0,255,255,0.2); top:50%;"></div>
    <div style="position:absolute; width:1px; height:100%; background:rgba(0,255,255,0.2); left:50%;"></div>

    <canvas id="bg-numbers" style="position:absolute; top:0; left:0; width:100%; height:100%; z-index:1; opacity:0.3;"></canvas>
</div>

<script>
    const unified = document.getElementById('unified-val');
    const labels = {
        l: document.getElementById('val-l'), r: document.getElementById('val-r'),
        u: document.getElementById('val-u'), d: document.getElementById('val-d'),
        f: document.getElementById('val-f'), b: document.getElementById('val-b')
    };

    function updateMatrix() {
        // จำลองการดึงค่าจากแกน X, Y, Z (ในระบบจริงจะดึงจาก Mic/Pulse/Analyze)
        let x_l = 432 + (Math.random() * 10); // Sound Hz
        let x_r = 5 + (Math.random() * 2);   // Vibrato
        let y_u = 60 + (Math.random() * 40);  // BPM
        let y_d = 14.4 + (Math.random() * 2); // Duration
        let z_f = 40 + (Math.random() * 15);  // Heat
        let z_b = -10 - (Math.random() * 5);  // Cold

        // อัปเดตตัวเลข 6 ทิศทาง
        labels.l.innerText = x_l.toFixed(2) + "Hz";
        labels.r.innerText = x_r.toFixed(2) + "Hz";
        labels.u.innerText = y_u.toFixed(0) + "BPM";
        labels.d.innerText = y_d.toFixed(1) + "s";
        labels.f.innerText = "+" + z_f.toFixed(1) + "°H";
        labels.b.innerText = z_b.toFixed(1) + "°C";

        // สูตรคณิตศาสตร์ Assassin 144: SQRT(X^2 + Y^2 + Z^2)
        // (คำนวณจากค่าเฉลี่ยแต่ละแกน)
        let x = (x_l + x_r) / 2;
        let y = (y_u + y_d) / 2;
        let z = Math.abs(z_f - z_b);
        let result = Math.sqrt(Math.pow(x,2) + Math.pow(y,2) + Math.pow(z,2)) / 10;
        
        unified.innerText = result.toFixed(2);
        
        // ขยับกรอบตามจังหวะสั่น (Vibrato)
        const cube = document.getElementById('matrix-cube');
        cube.style.transform = `translate(${(Math.random()-0.5)*2}px, ${(Math.random()-0.5)*2}px)`;

        requestAnimationFrame(updateMatrix);
    }

    // ทำ Background Digital Rain
    const canvas = document.getElementById('bg-numbers');
    const ctx = canvas.getContext('2d');
    canvas.width = 1000; canvas.height = 600;
    const chars = "0123456789ABCDEF";
    const drops = new Array(100).fill(0);

    function drawBG() {
        ctx.fillStyle = "rgba(0, 0, 0, 0.05)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = "#033";
        ctx.font = "10px monospace";
        for(let i=0; i<drops.length; i++) {
            const text = chars[Math.floor(Math.random()*chars.length)];
            ctx.fillText(text, i*10, drops[i]*10);
            if(drops[i]*10 > canvas.height && Math.random() > 0.975) drops[i] = 0;
            drops[i]++;
        }
    }
    setInterval(drawBG, 50);
    updateMatrix();
</script>
"""

# --- การวาง Layout แบบ Hierarchy ---
st.title("🥷 ASSASSIN 144: 6D MATRIX CORE")
st.write(f"USER: AGENT_X | SLOGAN: 'อยู่นิ่งๆ ไม่เจ็บตัว'")

# ระบบ Tabs แยกห้อง (Hierarchy 1.0)
tabs = st.tabs(["🚀 THE CORE", "🛰️ SENSORS", "📊 ANALYZER", "📺 MATRIX 144"])

with tabs[0]:
    st.markdown("### 6D UNIFIED TELEMETRY")
    components.html(core_6d_html, height=650)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("X-AXIS (SOUND)", "STABLE", "432 Hz")
    with col2:
        st.metric("Y-AXIS (PULSE)", "SYNCED", "BPM 1:1")
    with col3:
        st.metric("Z-AXIS (TEMP)", "BALANCED", "0.00 neutral")

with tabs[1]:
    st.info("ห้อง 1.1: กำลังรอการเชื่อมต่อกับ Digital Stethoscope และ Voice Tuner...")
    if st.button("เข้าสู่หน้าจูนสัญญาณ (SENSORS)"):
        st.write("ระบบกำลังเรียกใช้ห้อง 1.1...")

with tabs[2]:
    st.info("ห้อง 2.1: ส่วนวิเคราะห์ MP3 (7 ค่าแม่นยำ)")
    st.write("ผลลัพธ์การสแกนกีตาร์/กลอง/เบส จะถูกส่งมาที่นี่")

with tabs[3]:
    st.info("ห้อง 3.1: ตาราง 144 ช่อง (Visualizer)")
    st.write("ไฟกระพริบจะทำงานเมื่อ THE CORE คำนวณพิกัดสำเร็จ")

