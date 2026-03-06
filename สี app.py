import streamlit as st
import streamlit.components.v1 as components
import time

# --- 🎭 1. มิติดีไซน์สไตล์ Logo3.jpg ---
st.markdown("<h2 style='color:#FF7F50; text-align:center;'>🔊 SYNAPSE REAL-SOUND ENGINE</h2>", unsafe_allow_html=True)

# --- 🛠️ 2. แผงควบคุมช่วงเวลา (ตามใจพี่) ---
col = st.columns(4)
v1_range = col[0].text_input("V1 ช่วง (เริ่ม-จบ)", "1-4, 16-20")
v2_range = col[1].text_input("V2 ช่วง (เริ่ม-จบ)", "1-16")
bpm = col[2].number_input("SPEED (BPM)", 60, 240, 120)
stop_at = col[3].number_input("STOP AT", 1, 100, 20)

# --- 🚀 3. JavaScript: ตัวส่งเสียงออกลำโพงจริง (ทำได้จริง 100%) ---
# ผมเขียน Engine เสียงไว้ในนี้ เพื่อให้มันดังที่เครื่องพี่โดยตรง ไม่ดีเลย์
audio_js = f"""
<div style="background:#111; padding:20px; border-radius:10px; border:2px solid #FF7F50; text-align:center;">
    <button id="startAudio" style="width:100%; padding:15px; background:#FF7F50; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">
        🔴 กดเพื่อเริ่ม "ฟังเสียงจริง" (ACTIVATE SOUND)
    </button>
    <h1 id="timer" style="font-size:80px; color:#00ff00; font-family:monospace;">00</h1>
</div>

<script>
    let audioCtx;
    const btn = document.getElementById('startAudio');
    const timerDisp = document.getElementById('timer');

    // ฟังก์ชันสร้างเสียง "ตึ่บ" (V1) และ "จิ้ว" (V2)
    function playTone(freq, duration) {{
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
        osc.start();
        osc.stop(audioCtx.currentTime + duration);
    }}

    btn.onclick = async () => {{
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === 'suspended') await audioCtx.resume();
        
        btn.disabled = true;
        btn.innerText = "กำลังบรรเลงความจริง...";
        
        const bpm = {bpm};
        const interval = 60 / bpm * 1000;
        const v1_range = "{v1_range}";
        const v2_range = "{v2_range}";
        const stopAt = {stop_at};

        // ฟังก์ชันเช็คช่วงเวลา (ตามใจพี่)
        const isInRange = (num, rangeStr) => {{
            return rangeStr.split(',').some(p => {{
                if (p.includes('-')) {{
                    const [s, e] = p.split('-').map(Number);
                    return num >= s && num <= e;
                }}
                return Number(p) === num;
            }});
        }};

        let current = 1;
        const playLoop = setInterval(() => {{
            timerDisp.innerText = current.toString().padStart(2, '0');
            
            // ถ้าถึงช่วง V1 ดังเสียงทุ้ม (432Hz)
            if (isInRange(current, v1_range)) playTone(432, 0.2);
            // ถ้าถึงช่วง V2 ดังเสียงแหลม (864Hz)
            if (isInRange(current, v2_range)) playTone(864, 0.1);

            if (current >= stopAt) {{
                clearInterval(playLoop);
                btn.disabled = false;
                btn.innerText = "🏁 จบการทำงาน (RESTART)";
                timerDisp.style.color = "#FF7F50";
            }}
            current++;
        }}, interval);
    }};
</script>
"""

# --- 📊 4. แสดงผล Engine ---
components.html(audio_js, height=300)

st.sidebar.markdown(f"""
### 📝 บันทึกความจริง
- BPM: {bpm}
- เสียง 1: {v1_range}
- เสียง 2: {v2_range}
- **อยู่นิ่งๆ ไม่เจ็บตัว**
""")
