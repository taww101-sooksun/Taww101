import streamlit as st
import streamlit.components.v1 as components

st.title("🎙️ SYNAPSE X - ฟังเสียงแห่งความจริง")
st.write("สถานะ: ระบบสังเคราะห์เสียงโต้ตอบชีวภาพ (Dynamic Vocal Synthesis)")

# ส่วนติดต่อผู้ใช้สำหรับจำลองค่าจาก Sensor
col1, col2 = st.columns(2)
with col1:
    user_bpm = st.slider("💓 ชีพจรจริง (BPM)", 60, 120, 72)
with col2:
    stress_level = st.slider("🌡️ ระดับความเครียด (Environment)", 0, 100, 20)

# JavaScript: หัวใจของเครื่องยนต์เสียงที่ 'คัดมาแล้ว'
audio_engine_js = f"""
<div style="background-color: #000; color: #FFD700; padding: 30px; border: 3px solid #FFD700; border-radius: 25px; text-align: center; font-family: 'Courier New', monospace;">
    <div id="status_light" style="width: 20px; height: 20px; background: #f00; border-radius: 50%; margin: 0 auto 10px; box-shadow: 0 0 10px #f00;"></div>
    <h2 id="mode_text">SYSTEM READY</h2>
    
    <div style="margin: 20px 0;">
        <canvas id="scope" style="width: 100%; height: 80px; background: #111; border-radius: 10px; border: 1px solid #333;"></canvas>
    </div>

    <button id="masterBtn" style="width: 100%; padding: 20px; background: #FFD700; border: none; border-radius: 15px; font-weight: bold; font-size: 20px; cursor: pointer; color: #000;">
        🔊 เริ่มฟังคลื่นความจริง (START)
    </button>

    <div style="margin-top: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 12px; text-align: left;">
        <div>📍 Carrier: <span id="hz_val">432</span> Hz</div>
        <div>📍 Vibrato: <span id="vib_val">6.0</span> Hz</div>
        <div>📍 Transition: <span id="trans_val">150</span> ms</div>
    </div>
</div>

<script>
    let audioCtx, osc, gain, lfo, lfoGain;
    let isRunning = false;
    
    // ดึงค่าจาก Streamlit (จำลองการรับค่าจาก Bio-Sensor)
    let currentBPM = {user_bpm};
    let currentStress = {stress_level};

    const btn = document.getElementById('masterBtn');
    const canvas = document.getElementById('scope');
    const ctx = canvas.getContext('2d');

    function initAudio() {{
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        osc = audioCtx.createOscillator();
        gain = audioCtx.createGain();
        lfo = audioCtx.createOscillator(); // ตัวทำ Vibrato (มิติที่ 1)
        lfoGain = audioCtx.createGain();   // ตัวทำ Depth (มิติที่ 2)

        osc.type = 'sine'; 
        osc.frequency.setValueAtTime(432, audioCtx.currentTime); 

        // ตั้งค่า Vibrato ตามมิติความสมจริงที่นายส่งมา
        lfo.frequency.setValueAtTime(6.0, audioCtx.currentTime); 
        lfoGain.gain.setValueAtTime(4, audioCtx.currentTime); // ความกว้างของการแกว่ง

        lfo.connect(lfoGain);
        lfoGain.connect(osc.frequency);
        osc.connect(gain);
        gain.connect(audioCtx.destination);

        gain.gain.setValueAtTime(0, audioCtx.currentTime);
        gain.gain.linearRampToValueAtTime(0.4, audioCtx.currentTime + 1.5); // Fade in นุ่มๆ (Transition)

        osc.start();
        lfo.start();
        drawScope();
    }}

    function updateLogic() {{
        if(!isRunning) return;
        
        // 🧠 ความฉลาดของแอป: ปรับพารามิเตอร์ตามค่าชีพจร
        // ยิ่ง BPM สูง (ใจสั่น) -> เราต้องดึงความถี่ลงต่ำ (Calm Mode)
        let targetFreq = 432 - (currentBPM - 72);
        osc.frequency.setTargetAtTime(targetFreq, audioCtx.currentTime, 0.2);
        
        // ยิ่งเครียด (Stress สูง) -> ลด Vibrato ให้ช้าลงเพื่อความนิ่ง
        let targetVib = 6.5 - (currentStress / 40);
        lfo.frequency.setTargetAtTime(targetVib, audioCtx.currentTime, 0.2);

        document.getElementById('hz_val').innerText = targetFreq.toFixed(1);
        document.getElementById('vib_val').innerText = targetVib.toFixed(1);
        document.getElementById('mode_text').innerText = currentBPM > 90 ? "⚠️ RELAXING MODE" : "🟢 STABLE MODE";
    }}

    function drawScope() {{
        requestAnimationFrame(drawScope);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.beginPath();
        ctx.strokeStyle = '#FFD700';
        for(let i=0; i<canvas.width; i++) {{
            let v = Math.sin(i * 0.1 + (Date.now() * 0.01)) * 20 + 40;
            ctx.lineTo(i, v);
        }}
        ctx.stroke();
    }}

    btn.onclick = () => {{
        if(!isRunning) {{
            initAudio();
            isRunning = true;
            btn.innerText = "🛑 หยุดระบบ (STOP)";
            btn.style.background = "#f00";
            document.getElementById('status_light').style.background = "#0f0";
            document.getElementById('status_light').style.boxShadow = "0 0 10px #0f0";
            setInterval(updateLogic, 100);
        }} else {{
            gain.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.5);
            setTimeout(() => {{ location.reload(); }}, 500);
        }}
    }};
</script>
"""

components.html(audio_engine_js, height=500)

st.info("💡 ความจริงที่คุณจะได้ยิน: เมื่อคุณเลื่อน BPM ให้สูงขึ้น เสียงจะค่อยๆ ทุ้มและนุ่มลงโดยอัตโนมัติ เพื่อดึงจังหวะหัวใจของคุณให้กลับมานิ่งครับ")
