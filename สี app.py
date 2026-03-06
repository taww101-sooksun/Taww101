import streamlit as st
import streamlit.components.v1 as components

# --- 🎭 1. มิติเครื่องจักร (Logo3.jpg Style) ---
st.markdown("""
    <style>
    .stApp { background-color: #000; }
    .main-panel { border: 1px solid #FF7F50; border-radius: 10px; padding: 15px; background: #080808; }
    .neon-text { color: #FF7F50; font-family: monospace; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

st.image("Logo3.jpg", width=50)
st.markdown("<h4 style='color:#FF7F50;'>SYNAPSE DYNAMIC v1.1.5</h4>", unsafe_allow_html=True)

# --- 🎛️ 2. แผงควบคุม (เน้นตามใจพี่) ---
with st.container():
    st.markdown("<div class='main-panel'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    v1_range = c1.text_input("V1 ช่วง", "1-4, 17-20")
    v2_range = c2.text_input("V2 ช่วง", "1-16")
    bpm = c3.number_input("BPM", 60, 240, 120)

    st.markdown("<p class='neon-text'>🎚️ 3 ปุ่มสไลด์ (0-10)</p>", unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    v_len = s1.slider("1. ความยาว (LEN)", 0.0, 10.0, 5.0)
    v_space = s2.slider("2. ความกังวาน (SPACE)", 0.0, 10.0, 4.0)
    v_gain = s3.slider("3. ความดัง (GAIN)", 0.0, 10.0, 7.0)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 🚀 3. JavaScript: เครื่องยนต์เสียง "ตื่น...ตึง" (Dynamic Tone) ---
audio_dynamic_js = f"""
<div style="background:#000; padding:15px; border-radius:10px; border:1px solid #333; text-align:center; margin-top:10px;">
    <button id="play" style="width:100%; padding:15px; background:#FF7F50; border:none; border-radius:8px; font-weight:bold; cursor:pointer; font-size:18px;">
        🔴 EXECUTE REAL-FLOW
    </button>
    <div id="clock" style="font-size:70px; color:#00ff00; font-family:monospace; margin:10px 0; text-shadow: 0 0 15px #00ff00;">00</div>
    <div id="grid" style="display: flex; flex-wrap: wrap; justify-content: center; gap: 3px;"></div>
</div>

<script>
    let audioCtx;
    const btn = document.getElementById('play');
    const clock = document.getElementById('clock');
    const grid = document.getElementById('grid');

    for(let i=1; i<=20; i++) {{
        let d = document.createElement('div'); d.id = 'bar-'+i;
        d.style.width='12px'; d.style.height='12px'; d.style.background='#222'; d.style.borderRadius='50%';
        grid.appendChild(d);
    }}

    // ฟังก์ชันสร้างเสียง "ตื่น-ตึง"
    function playFlow(freq, isAccent, l, s, g) {{
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        const filter = audioCtx.createBiquadFilter();

        // จังหวะ "ตื่น" (Accent) จะสว่างและดังกว่า / จังหวะ "ตึง" จะทุ้มและนุ่มกว่า
        const duration = (l/10) * 0.8 + 0.1;
        const release = (s/10) * 1.2;
        const volume = (g/10) * (isAccent ? 0.3 : 0.15); // สลับความดัง
        
        osc.type = isAccent ? 'triangle' : 'sine'; // สลับเนื้อเสียง
        osc.frequency.setValueAtTime(isAccent ? freq * 1.02 : freq, audioCtx.currentTime); // บิดคีย์นิดๆ ให้ดูมีชีวิต
        
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(isAccent ? 3000 : 800, audioCtx.currentTime); // "ตื่น" จะใส "ตึง" จะทุ้ม

        gain.gain.setValueAtTime(0, audioCtx.currentTime);
        gain.gain.linearRampToValueAtTime(volume, audioCtx.currentTime + 0.02); // Attack นุ่มๆ
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
            document.querySelectorAll('#grid div').forEach(d => d.style.background = '#222');
            document.getElementById('bar-'+step).style.background = '#FF7F50';

            const check = (n, r) => r.split(',').some(p => {{
                if(p.includes('-')) {{ let [a,b] = p.split('-').map(Number); return n>=a && n<=b; }}
                return Number(p) === n;
            }});

            // ตรรกะ "ตื่น-ตึง": ห้องคี่ (1,3,5..) = ตื่น / ห้องคู่ (2,4,6..) = ตึง
            const isAccent = (step % 2 !== 0);

            if(check(step, "{v1_range}")) playFlow(329.63, isAccent, {v_len}, {v_space}, {v_gain}); 
            if(check(step, "{v2_range}")) playFlow(164.81, !isAccent, {v_len}*0.5, {v_space}, {v_gain}*0.6);

            if(step >= 20) {{ clearInterval(loop); btn.disabled = false; }}
            step++;
        }}, ms);
    }};
</script>
"""

components.html(audio_dynamic_js, height=350)
