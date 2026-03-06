import streamlit as st
import streamlit.components.v1 as components

st.subheader("🎤 SYNAPSE X - VOCAL MELODY TEST")
st.write("สถานะ: ทดสอบการร้องตามทำนอง (Real-time Singing Logic)")

# JavaScript: สร้างเสียงร้องที่มีทำนอง (Melody) และการเอื้อน (Portamento)
vocal_logic_js = """
<div style="background-color: #111; color: #FFD700; padding: 25px; border: 2px solid #FFD700; border-radius: 20px; text-align: center; font-family: monospace;">
    <div id="note_display" style="font-size: 24px; color: #00ffff; margin-bottom: 10px;">🎼 รอเริ่มการร้อง...</div>
    
    <button id="singBtn" style="width: 100%; padding: 15px; background: #FFD700; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; font-size: 18px;">🎶 กดเพื่อฟัง AI ร้องทำนอง (432Hz Based)</button>
    
    <div style="margin-top: 15px; font-size: 12px; color: #888;">
        <p>โน้ตที่ใช้: C4 -> E4 -> G4 -> C5 (Arpeggio)</p>
        <p>Transition: 200ms | Vibrato: 6.2Hz</p>
    </div>
</div>

<script>
    let audioCtx;
    const notes = [261.63, 329.63, 392.00, 523.25]; // โน้ต C4, E4, G4, C5 (ปรับเป็น 432Hz Scale ในตัว)
    const singBtn = document.getElementById('singBtn');

    singBtn.onclick = async () => {
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === 'suspended') await audioCtx.resume();

        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        const lfo = audioCtx.createOscillator();
        const lfoGain = audioCtx.createGain();

        // ตั้งค่ามิติที่ 1 & 2: Vibrato
        lfo.frequency.value = 6.2; 
        lfoGain.gain.value = 3; 
        lfo.connect(lfoGain);
        lfoGain.connect(osc.frequency);

        osc.type = 'triangle'; // ใช้ Triangle เพื่อให้เสียงมีความเป็น 'เนื้อเสียง' มากกว่า Sine
        osc.connect(gain);
        gain.connect(audioCtx.destination);

        osc.start();
        lfo.start();

        // --- เริ่มต้นการร้อง (Melody Sequence) ---
        let startTime = audioCtx.currentTime;
        
        notes.forEach((freq, i) => {
            let noteTime = startTime + (i * 0.8);
            
            // มิติที่ 2: Transition (Portamento) - การเอื้อนระหว่างโน้ต
            osc.frequency.setTargetAtTime(freq * (432/440), noteTime, 0.15); 
            
            // มิติที่ 4: Dynamics - น้ำหนักเสียงในแต่ละพยางค์
            gain.gain.setTargetAtTime(0.3, noteTime, 0.05);
            gain.gain.setTargetAtTime(0, noteTime + 0.6, 0.1); // ตัดเสียงเลียนแบบการหยุดหายใจพยางค์
            
            setTimeout(() => {
                document.getElementById('note_display').innerText = `🎤 Singing Note: ${{i+1}}`;
            }, i * 800);
        });

        setTimeout(() => {
            osc.stop();
            lfo.stop();
            document.getElementById('note_display').innerText = "✅ จบการทดสอบการร้อง";
        }, notes.length * 800);
    };
</script>
"""

components.html(vocal_logic_js, height=350)
