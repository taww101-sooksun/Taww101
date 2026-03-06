import streamlit as st
import streamlit.components.v1 as components
import os

# --- 🎭 1. ดีไซน์แบบดุดัน (Logo3 Style) ---
st.set_page_config(page_title="SYNAPSE BEAT-MACHINE", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #000; color: #FF7F50; }
    .control-box { border: 2px solid #FF7F50; border-radius: 10px; padding: 15px; background: #050505; }
    .neon-text { color: #00ff00; font-family: monospace; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 🖼️ 2. ส่วนหัว (logo3.jpg) ---
c1, c2 = st.columns([1, 4])
with c1:
    if os.path.exists("logo3.jpg"): st.image("logo3.jpg", width=70)
    else: st.markdown("## 🥁")
with c2:
    st.markdown("<h2 style='margin:0; color:#FF7F50;'>SYNAPSE BEAT-MACHINE</h2>", unsafe_allow_html=True)
    st.markdown("<span class='neon-text'>STATUS: อยู่นิ่งๆ ไม่เจ็บตัว (TikTok Mode)</span>", unsafe_allow_html=True)

# --- 🎛️ 3. แผงควบคุมเลเยอร์เสียง (1-20 ห้อง) ---
st.markdown("<div class='control-box'>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
k_kick = col1.text_input("🥁 KICK (ตึ่บๆ)", "1, 3, 5, 7, 9, 11, 13, 15, 17, 19")
b_bass = col2.text_input("🎸 DEEP BASS (เบสหนัก)", "1-20")
s_synth = col1.text_input("🎹 SYNTH LEAD (สูง-ต่ำ)", "1, 2, 5, 6, 9, 10, 13, 14, 17, 18")
f_fx = col2.text_input("⚡ SFX/VOCAL (เอฟเฟกต์)", "4, 8, 12, 16, 20")

st.markdown("<hr style='border:0.5px solid #333;'>", unsafe_allow_html=True)

# 🎯 3 ปุ่มสไลด์มหาประลัย 0-10
s1, s2, s3 = st.columns(3)
v_sub = s1.slider("1. แรงปะทะเบส (SUB)", 0.0, 10.0, 9.0)
v_mod = s2.slider("2. มิติเสียง (MODULATE)", 0.0, 10.0, 5.0)
v_gain = s3.slider("3. ความดังรวม (GAIN)", 0.0, 10.0, 8.0)
bpm = st.slider("ความเร็ว (BPM - TikTok แนะนำ 128+)", 100, 160, 128)
st.markdown("</div>", unsafe_allow_html=True)

# --- 🚀 4. JavaScript Engine: พลังเสียงเบสและกลอง ---
audio_engine_js = f"""
<div style="background:#000; padding:20px; border:1px solid #444; border-radius:10px; text-align:center; margin-top:15px;">
    <button id="play" style="width:100%; padding:20px; background:#FF7F50; border:none; border-radius:10px; font-weight:bold; font-size:22px; cursor:pointer; box-shadow: 0 0 20px #FF4500;">
        🔥 START BEAT ENGINE
    </button>
    <div id="clock" style="font-size:80px; color:#00ff00; font-family:monospace; margin:10px 0;">00</div>
    <div id="meter" style="display:flex; justify-content:center; gap:5px; height:40px;"></div>
</div>

<script>
    let audioCtx;
    const btn = document.getElementById('play');
    const clock = document.getElementById('clock');
    const meter = document.getElementById('meter');

    for(let i=1; i<=20; i++) {{
        let d = document.createElement('div'); d.id = 'm-'+i;
        d.style.width='15px'; d.style.height='10px'; d.style.background='#222';
        meter.appendChild(d);
    }}

    // --- ฟังก์ชันสร้างเสียงเบสหนักและ Kick ---
    function playDrum(type, freq, volMult, dec) {{
        const osc = audioCtx.createOscillator();
        const gn = audioCtx.createGain();
        
        const vol = ({v_gain}/10) * volMult;
        
        osc.type = type;
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + dec);
        
        gn.gain.setValueAtTime(vol, audioCtx.currentTime);
        gn.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + dec);
        
        osc.connect(gn); gn.connect(audioCtx.destination);
        osc.start(); osc.stop(audioCtx.currentTime + dec);
    }}

    function playSynth(freq, type, gMult) {{
        const osc = audioCtx.createOscillator();
        const gn = audioCtx.createGain();
        const fl = audioCtx.createBiquadFilter();
        
        const mod = ({v_mod}/10);
        const volume = ({v_gain}/10) * gMult;

        osc.type = type;
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        fl.type = 'lowpass';
        fl.frequency.setValueAtTime(500 + (mod * 3000), audioCtx.currentTime);

        gn.gain.setValueAtTime(0, audioCtx.currentTime);
        gn.gain.linearRampToValueAtTime(volume, audioCtx.currentTime + 0.05);
        gn.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.5);

        osc.connect(fl); fl.connect(gn); gn.connect(audioCtx.destination);
        osc.start(); osc.stop(audioCtx.currentTime + 0.6);
    }}

    btn.onclick = async () => {{
        if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if(audioCtx.state === 'suspended') await audioCtx.resume();
        btn.disabled = true;
        let step = 1;
        const speed = 60 / {bpm} * 1000;

        const loop = setInterval(() => {{
            clock.innerText = step.toString().padStart(2, '0');
            document.querySelectorAll('#meter div').forEach(d => {{ d.style.background='#222'; d.style.height='10px'; }});
            const active = document.getElementById('m-'+step);
            active.style.background='#FF7F50'; active.style.height='35px';

            const check = (n, r) => r.split(',').some(p => {{
                if(p.includes('-')) {{ let [a,b] = p.split('-').map(Number); return n>=a && n<=b; }}
                return Number(p) === n;
            }});

            // 1. KICK (ใช้ความถี่ต่ำมาก + กระแทก)
            if(check(step, "{k_kick}")) playDrum('sine', 150, 0.8, 0.2);
            // 2. BASS (เบสหนักสั่นสะเทือน) - ปรับตามปุ่ม SUB
            if(check(step, "{b_bass}")) playDrum('triangle', 60, ({v_sub}/10) * 0.7, 0.4);
            // 3. SYNTH (เสียงหลักสูง-ต่ำ)
            if(check(step, "{s_synth}")) playSynth(step % 4 === 0 ? 440 : 220, 'sawtooth', 0.2);
            // 4. SFX (เสียงหวีด/ระเบิด)
            if(check(step, "{f_fx}")) playSynth(1200, 'square', 0.1);

            if(step >= 20) {{ clearInterval(loop); btn.disabled = false; }}
            step++;
        }}, speed);
    }};
</script>
"""

components.html(audio_engine_js, height=450)
