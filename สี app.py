import streamlit as st
import streamlit.components.v1 as components

st.subheader("🎼 SYNAPSE X - FULL MUSIC ENGINE TEST")
st.write("สถานะ: กำลังรันระบบดนตรีและเสียงร้องจาก Logic ภายใน")

# JavaScript: รวมร่างดนตรี (Beat) และ เสียงร้อง (Melody)
full_music_js = """
<div style="background-color: #111; color: #FFD700; padding: 25px; border: 2px solid #FFD700; border-radius: 20px; text-align: center; font-family: monospace;">
    <div id="vocal_stat" style="color: #00ffff; font-size: 20px; margin-bottom: 10px;">🎤 รอการร้อง...</div>
    <div id="beat_stat" style="color: #ff00ff; font-size: 14px; margin-bottom: 20px;">🥁 จังหวะดนตรี: Standby</div>
    
    <button id="playMusic" style="width: 100%; padding: 20px; background: #FFD700; border: none; border-radius: 15px; font-weight: bold; cursor: pointer; font-size: 20px;">🎹 PLAY: ร้องเพลง + ดนตรี</button>
</div>

<script>
    let audioCtx;
    const melody = [261.63, 293.66, 329.63, 349.23]; // โน้ต C4, D4, E4, F4 (Vocal)
    
    async function startMusic() {
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === 'suspended') await audioCtx.resume();

        let startTime = audioCtx.currentTime;

        // --- 1. ส่วนของเสียงดนตรี (The Beat/Backing) ---
        function playDrum(time) {
            let osc = audioCtx.createOscillator();
            let g = audioCtx.createGain();
            osc.frequency.setValueAtTime(150, time);
            osc.frequency.exponentialRampToValueAtTime(0.01, time + 0.1);
            g.gain.setValueAtTime(0.3, time);
            g.gain.exponentialRampToValueAtTime(0.01, time + 0.1);
            osc.connect(g); g.connect(audioCtx.destination);
            osc.start(time); osc.stop(time + 0.1);
        }

        // --- 2. ส่วนของเสียงร้อง (The Vocal Logic) ---
        function playVocal(freq, time, duration) {
            let vOsc = audioCtx.createOscillator();
            let vGain = audioCtx.createGain();
            let vLfo = audioCtx.createOscillator();
            let vLfoG = audioCtx.createGain();

            vOsc.type = 'sawtooth'; // เสียงที่มี Harmonic เยอะขึ้นเพื่อให้เหมือนคน
            vOsc.frequency.setValueAtTime(freq * (432/440), time);
            
            // ใส่ Vibrato (มิติความสมจริง)
            vLfo.frequency.value = 6.0;
            vLfoG.gain.value = 4;
            vLfo.connect(vLfoG); vLfoG.connect(vOsc.frequency);

            // คุมน้ำหนักเสียง (Dynamics)
            vGain.gain.setValueAtTime(0, time);
            vGain.gain.linearRampToValueAtTime(0.2, time + 0.1); // Attack
            vGain.gain.linearRampToValueAtTime(0, time + duration - 0.1); // Release

            // Low-pass Filter เพื่อให้เสียงนุ่มนวล (Timbre)
            let filter = audioCtx.createBiquadFilter();
            filter.type = 'lowpass';
            filter.frequency.value = 1500;

            vOsc.connect(filter); filter.connect(vGain); vGain.connect(audioCtx.destination);
            vOsc.start(time); vLfo.start(time);
            vOsc.stop(time + duration); vLfo.stop(time + duration);
        }

        // รัน Loop ดนตรีและเสียงร้อง
        for (let i = 0; i < 8; i++) {
            let time = startTime + (i * 0.5);
            playDrum(time); // เล่นจังหวะทุกๆ 0.5 วินาที
            
            if (i % 2 === 0) {
                let noteIdx = (i / 2) % melody.length;
                playVocal(melody[noteIdx], time, 0.9); // ร้องโน้ตทุกๆ 1 วินาที
                setTimeout(() => {
                    document.getElementById('vocal_stat').innerText = "🎤 Singing Note: " + (noteIdx + 1);
                    document.getElementById('beat_stat').innerText = "🥁 Beat: " + (i + 1);
                }, i * 500);
            }
        }
    }

    document.getElementById('playMusic').onclick = startMusic;
</script>
"""

components.html(full_music_js, height=400)
