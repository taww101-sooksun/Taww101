import streamlit as st
import streamlit.components.v1 as components

# --- 🎭 1. มิติเครื่องจักร (Dark & Neon Orange) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .layer-box { 
        border: 1px solid #FF7F50; 
        border-radius: 8px; 
        padding: 10px; 
        margin-bottom: 5px;
        background: #080808;
    }
    .neon-label { color: #FF7F50; font-size: 12px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ส่วนหัว
c_logo, c_title = st.columns([1, 5])
with c_logo: 
    try: st.image("Logo3.jpg", width=50)
    except: st.write("💠")
with c_title: 
    st.markdown("<h3 style='color:#FF7F50; margin:0;'>SYNAPSE MULTI-CORE v1.1.3</h3>", unsafe_allow_html=True)

# --- 🎛️ 2. แผงควบคุม 4 เลเยอร์ (สั่งงานตามใจ) ---
st.markdown("<p class='neon-label'>🎼 SEQUENCE LAYERS (1-20 BARS)</p>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
l1 = col1.text_input("L1 (เช่น Kick):", "1, 5, 9, 13, 17")
l2 = col2.text_input("L2 (เช่น Snare):", "5, 13")
l3 = col1.text_input("L3 (Vocal Main):", "1-8, 16-20")
l4 = col2.text_input("L4 (FX/Atmosphere):", "1-20")

# --- 🎚️ 3. ปุ่มสไลด์ 0-10 (คุมมิติรวม) ---
st.markdown("<div class='layer-box'>", unsafe_allow_html=True)
s1, s2, s3, s4 = st.columns(4)
bpm = s1.number_input("BPM", 60, 240, 120)
v_len = s2.slider("LENGTH", 0.0, 10.0, 5.0)
v_space = s3.slider("SPACE", 0.0, 10.0, 3.0)
v_gain = s4.slider("GAIN", 0.0, 10.0, 7.0)
st.markdown("</div>", unsafe_allow_html=True)

# --- 🚀 4. JavaScript: เครื่องยนต์ 4 เสียง (ทำได้จริง ไม่หลอกลวง) ---
audio_multi_js = f"""
<div style="background:#000; padding:15px; border-radius:10px; border:1px solid #333; text-align:center; margin-top:10px;">
    <button id="exec" style="width:100%; padding:15px; background:#FF7F50; border:none; border-radius:8px; font-weight:bold; color:#000; cursor:pointer;">
        🔴 EXECUTE 4-LAYER ENGINE
    </button>
    <div id="clock" style="font-size:60px; color:#00ff00; font-family:monospace; margin:5px 0;">00</div>
    <div id="grid" style="display: flex; flex-wrap: wrap; justify-content: center; gap: 2px;"></div>
</div>

<script>
    let audioCtx;
    const grid = document.getElementById('grid');
    const clock = document.getElementById('clock');
    const btn = document.getElementById('exec');

    // สร้างจุดไฟ 20 ห้อง
    for(let i=1; i<=20; i++) {{
        let d = document.createElement('div');
        d.id = 'st-' + i;
        d.style.width = '12px'; d.style.height = '12px';
        d.style.background = '#222'; d.style.borderRadius = '50%';
        grid.appendChild(d);
    }}

    function playSynth(freq, type, gMult) {{
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        const duration = ({v_len}/10) * 0.5 + 0.1;
        const volume = ({v_gain}/10) * 0.2 * gMult;

        osc.type = type;
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        gain.gain.setValueAtTime(volume, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration + ({v_space}/10));

        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + duration + ({v_space}/10));
    }}

    btn.onclick = async () => {{
        if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if(audioCtx.state === 'suspended') await audioCtx.resume();
        btn.disabled = true;
        let step = 1;
        const ms = 60 / {bpm} * 1000;

        const loop = setInterval(() => {{
            clock.innerText = step.toString().padStart(2, '0');
            document.querySelectorAll('#grid div').forEach(d => d.style.background = '#222');
            document.getElementById('st-' + step).style.background = '#FF7F50';

            const isIn = (n, r) => r.split(',').some(p => {{
                if(p.includes('-')) {{ let [a,b] = p.split('-').map(Number); return n>=a && n<=b; }}
                return Number(p) === n;
            }});

            if(isIn(step, "{l1}")) playSynth(60, 'sine', 1.5);    // L1: Bass/Kick (ทุ้ม)
            if(isIn(step, "{l2}")) playSynth(800, 'square', 0.3); // L2: Snare (คม)
            if(isIn(step, "{l3}")) playSynth(432, 'triangle', 0.8); // L3: Vocal (นุ่ม)
            if(isIn(step, "{l4}")) playSynth(1200, 'sine', 0.2);   // L4: Hi-hat/FX (แหลม)

            if(step >= 20) {{ clearInterval(loop); btn.disabled = false; }}
            step++;
        }}, ms);
    }};
</script>
"""

components.html(audio_multi_js, height=300)
