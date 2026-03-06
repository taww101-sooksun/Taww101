import streamlit as st
import streamlit.components.v1 as components
import os

# --- 🎭 1. ดีไซน์ Dark Mode ---
st.set_page_config(page_title="SYNAPSE CORE v1.2.0", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #000; color: #FF7F50; }
    .main-panel { border: 2px solid #FF7F50; border-radius: 12px; padding: 15px; background: #080808; }
    .neon-clock { font-family: monospace; font-size: 60px; color: #00ff00; text-align: center; text-shadow: 0 0 10px #00ff00; }
    </style>
""", unsafe_allow_html=True)

# --- 🖼️ 2. ส่วนหัว (ดึง logo3.jpg) ---
c1, c2 = st.columns([1, 5])
with c1:
    if os.path.exists("logo3.jpg"): 
        st.image("logo3.jpg", width=60)
    else: 
        st.markdown("<h2 style='margin:0;'>🔊</h2>", unsafe_allow_html=True)
with c2:
    st.markdown("<h3 style='margin:0; color:#FF7F50;'>SYNAPSE MULTI-DIMENSION v1.2.0</h3>", unsafe_allow_html=True)
    st.caption("FIXED ERROR | MULTI-TONE ENGINE | สเกล 0-10")

# --- 🎛️ 3. แผงควบคุมมิติเสียง ---
st.markdown("<div class='main-panel'>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
v_low = col1.text_input("1. ทุ้มต่ำ (Deep Bass)", "1, 5, 9, 13, 17")
v_high = col2.text_input("2. แหลม (Sharp Treble)", "3, 7, 11, 15, 19")
v_main = col1.text_input("3. เสียงหลัก (Dynamic Mid)", "1-20")
v_fx = col2.text_input("4. เอฟเฟกต์ (FX Rise)", "10, 20")

st.markdown("<hr style='border:0.5px solid #333;'>", unsafe_allow_html=True)

s1, s2, s3 = st.columns(3)
val_len = s1.slider("สั้น-ยาว (LENGTH)", 0.0, 10.0, 5.0)
val_space = s2.slider("ลึก-กังวาน (SPACE)", 0.0, 10.0, 4.0)
val_gain = s3.slider("ดัง-เบา (GAIN)", 0.0, 10.0, 7.0)
bpm = st.slider("ความเร็ว (BPM)", 60, 200, 120)
st.markdown("</div>", unsafe_allow_html=True)

# --- 🚀 4. JavaScript Engine (ฉบับแก้ปีกกา {{ }}) ---
audio_engine_js = f"""
<div style="background:#000; padding:15px; border:1px solid #444; border-radius:10px; text-align:center; margin-top:10px;">
    <button id="run" style="width:100%; padding:15px; background:#FF7F50; border:none; border-radius:8px; font-weight:bold; font-size:18px; cursor:pointer;">
        🔴 EXECUTE REAL-SOUND ENGINE
    </button>
    <div id="clock" class="neon-clock">00</div>
    <div id="viz" style="display:flex; justify-content:center; gap:3px; height:30px; align-items:flex-end;"></div>
</div>

<script>
    let audioCtx;
    const btn = document.getElementById('run');
    const clock = document.getElementById('clock');
    const viz = document.getElementById('viz');

    // สร้างแท่งไฟ 20 ห้อง
    for(let i=1; i<=20; i++) {{
        let b = document.createElement('div'); b.id = 'b-' + i;
        b.style.width='8px'; b.style.height='5px'; b.style.background='#333';
        viz.appendChild(b);
    }}

    function playSound(freq, type, gMult, filterFreq, isShort) {{
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        const filter = audioCtx.createBiquadFilter();

        const duration = isShort ? 0.05 : ({val_len} / 10) * 0.8 + 0.1;
        const release = ({val_space} / 10) * 1.5;
        const vol = ({val_gain} / 10) * 0.15 * gMult;

        osc.type = type;
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(filterFreq, audioCtx.currentTime);

        gain.gain.setValueAtTime(0, audioCtx.currentTime);
        gain.gain.linearRampToValueAtTime(vol, audioCtx.currentTime + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration + release);

        osc.connect(filter); filter.connect(gain); gain.connect(audioCtx.destination);
        osc.start(); osc.stop(audioCtx.currentTime + duration + release);
    }}

    btn.onclick = async () => {{
        if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if(audioCtx.state === 'suspended') await audioCtx.resume();
        btn.disabled = true;
        let step = 1;
        const ms = 60 / {bpm} * 1000;

        const loop = setInterval(() => {{
            clock.innerText = step.toString().padStart(2, '0');
            document.querySelectorAll('#viz div').forEach(d => {{ d.style.background='#333'; d.style.height='5px'; }});
            const activeBar = document.getElementById('b-' + step);
            if(activeBar) {{ activeBar.style.background='#FF7F50'; activeBar.style.height='25px'; }}

            const check = (n, r) => r.split(',').some(p => {{
                if(p.includes('-')) {{ 
                    let parts = p.split('-').map(Number);
                    return n >= parts[0] && n <= parts[1]; 
                }}
                return Number(p) === n;
            }});

            // --- มิติเสียงหลากหลาย (ทุ้ม-แหลม-สั้น-ยาว) ---
            if(check(step, "{v_low}")) playSound(55, 'sine', 2.0, 200, false);
            if(check(step, "{v_high}")) playSound(3000, 'square', 0.1, 4000, true);
            if(check(step, "{v_main}")) playSound(step % 2 === 0 ? 220 : 330, 'triangle', 0.6, 1500, false);
            if(check(step, "{v_fx}")) playSound(880, 'sawtooth', 0.3, 3000, false);

            if(step >= 20) {{ 
                clearInterval(loop); 
                btn.disabled = false; 
                clock.style.color = "#FF7F50";
            }}
            step++;
        }}, ms);
    }};
</script>
"""

components.html(audio_engine_js, height=350)
