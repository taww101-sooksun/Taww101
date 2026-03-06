import streamlit as st
import streamlit.components.v1 as components
import time
import numpy as np

# --- 🎭 1. มิติดีไซน์ & CSS (ดำเงา-แดงเงา-เขียวสะท้อนแสง) ---
st.markdown("""
    <style>
    .stApp { background: #000; color: #fff; }
    .main-panel { border: 2px solid #FF7F50; border-radius: 20px; padding: 20px; background: rgba(20,20,20,0.9); }
    .logo-img { border-radius: 50%; border: 3px solid #00ff00; box-shadow: 0 0 15px #00ff00; }
    </style>
""", unsafe_allow_html=True)

# --- 🖼️ 2. ส่วนหัวเครื่องยนต์ (Logo3.jpg) ---
c1, c2 = st.columns([1, 4])
with c1: st.image("Logo3.jpg", width=100)
with c2: 
    st.title("SYNAPSE QUANTUM X")
    st.markdown(f"🕒 {time.strftime('%H:%M:%S')} | **สโลแกน: อยู่นิ่งๆ ไม่เจ็บตัว**")

# --- 🔊 3. ระบบส่งเสียงจริง (The Audio Router Engine) ---
# ผมใช้ JavaScript เพื่อส่งเสียงออกลำโพงพี่โดยตรงแบบ Real-time ไม่มีการหลอก!
audio_engine_js = """
<div style="background: #111; color: #00ff00; padding: 20px; border: 2px solid #00ff00; border-radius: 15px; text-align: center;">
    <h3 id="status">STATUS: STANDBY</h3>
    <button id="playBtn" style="width: 100%; padding: 15px; background: #FF7F50; border: none; border-radius: 10px; font-weight: bold; cursor: pointer;">
        🔴 EXECUTE: ส่งเสียงออกลำโพง (PLAY)
    </button>
</div>

<script>
    let audioCtx;
    document.getElementById('playBtn').onclick = async () => {
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === 'suspended') await audioCtx.resume();
        
        document.getElementById('status').innerText = "STATUS: PLAYING REAL SOUND...";
        
        // --- ตรรกะการสร้างเสียงที่ 'ยาว' และ 'บาลานซ์' ---
        function playTone(freq, duration, gainVal) {
            let osc = audioCtx.createOscillator();
            let gain = audioCtx.createGain();
            let lfo = audioCtx.createOscillator(); // มิติ Vibrato
            let lfoG = audioCtx.createGain();

            osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
            lfo.frequency.value = 6.0; // Vibrato 6Hz
            lfoG.gain.value = 4;
            
            lfo.connect(lfoG); lfoG.connect(osc.frequency);
            osc.connect(gain); gain.connect(audioCtx.destination);
            
            gain.gain.setValueAtTime(0, audioCtx.currentTime);
            gain.gain.linearRampToValueAtTime(gainVal, audioCtx.currentTime + 0.1);
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
            
            osc.start(); lfo.start();
            osc.stop(audioCtx.currentTime + duration);
        }

        // เล่นเสียงตัวอย่าง (C4 - E4 - G4) แบบลากยาว
        playTone(261.6, 1.5, 0.3); // ตึ่บ
        setTimeout(() => playTone(329.6, 1.5, 0.2), 500); // จิ้ว
    };
</script>
"""

# --- 🎼 4. กระดาน 8 บรรทัด (8 Layers) ---
st.divider()
for i in range(8):
    with
