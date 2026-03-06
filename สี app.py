import streamlit as st
import streamlit.components.v1 as components
import os

# --- 🎭 1. มิติดีไซน์สไตล์ Logo3 (Dark & Orange) ---
st.set_page_config(page_title="SYNAPSE CORE", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #000; color: #FF7F50; }
    .main-panel { border: 2px solid #FF7F50; border-radius: 12px; padding: 15px; background: #080808; }
    .neon-clock { font-family: monospace; font-size: 70px; color: #00ff00; text-align: center; text-shadow: 0 0 15px #00ff00; }
    </style>
""", unsafe_allow_html=True)

# --- 🖼️ 2. ส่วนหัว (เรียกชื่อไฟล์ logo3.jpg ให้ตรงเป๊ะ) ---
c1, c2 = st.columns([1, 5])
with c1:
    # ดึงไฟล์ logo3.jpg ตามที่พี่แจ้ง (ใส่ดัก Error ไว้เพื่อความปลอดภัยสูงสุด)
    target_logo = "logo3.jpg"
    if os.path.exists(target_logo):
        st.image(target_logo, width=60)
    else:
        # ถ้าหาไม่เจอจริงๆ ให้ขึ้นไอคอนแทน ไม่ให้แอปแดง
        st.markdown("<h2 style='margin:0;'>🔥</h2>", unsafe_allow_html=True)
with c2:
    st.markdown("<h3 style='margin:0; color:#FF7F50;'>SYNAPSE DYNAMIC v1.1.8</h3>", unsafe_allow_html=True)
    st.caption("FIXED: logo3.jpg | STATUS: อยู่นิ่งๆ ไม่เจ็บตัว")

# --- 🎛️ 3. แผงควบคุมมิติเสียง (ตื่น-ตึง) ---
st.markdown("<div class='main-panel'>", unsafe_allow_html=True)
col_cfg = st.columns(4)
l1 = col_cfg[0].text_input("L1 (ตื่น)", "1, 3, 5, 7, 9, 11, 13, 15, 17, 19")
l2 = col_cfg[1].text_input("L2 (ตึง)", "2, 4, 6, 8, 10, 12, 14, 16, 18, 20")
bpm = col_cfg[2].number_input("BPM", 60, 240, 120)
stop_val = col_cfg[3].number_input("STOP", 1, 100, 20)

# --- 🎯 4. 3 ปุ่มสไลด์มหาประลัย 0-10 ---
s1, s2, s3 = st.columns(3)
v_len = s1.slider("1. ความยาว (LEN)", 0.0, 10.0, 5.0)
v_space = s2.slider("2. ความกังวาน (SPACE)", 0.0, 10.0, 4.0)
v_gain = s3.slider("3. ความดัง (GAIN)", 0.0, 10.0, 7.0)
st.markdown("</div>", unsafe_allow_html=True)

# --- 🚀 5. JavaScript: เครื่องยนต์เสียงจริง (Real Web Audio) ---
audio_engine_js = f"""
<div style="background:#000; padding:15px; border:1px solid #333; border-radius:10px; text-align:center; margin-top:10px;">
    <button id="playBtn" style="width:100%; padding:15px; background:#FF7F50; border:none; border-radius:8px; font-weight:bold; font-size:18px; cursor:pointer; color:#000;">
        🔴 EXECUTE ENGINE
    </button>
    <div id="clock" class="neon-clock">00</div>
    <div id="grid" style="display:flex; flex-wrap:wrap; justify-content:center; gap:4px; margin-top:10px;"></div>
</div>

<script>
    let audioCtx;
    const btn = document.getElementById('playBtn');
    const clock = document.getElementById('clock');
    const grid = document.getElementById('grid');

    for(let i=1; i<=20; i++) {{
        let d = document.createElement('div'); d.id = 'dot-'+i;
        d.style.width='10px'; d.style.height='10px'; d.style.background='#222'; d.style.borderRadius='50%';
        grid.appendChild(d);
    }}

    function playFlow(f, isAccent, l, s, g) {{
        const o = audioCtx.createOscillator();
        const gn = audioCtx.createGain();
        const fl = audioCtx.createBiquadFilter();

        const dur = (l/10) * 0.7 + 0.05;
        const rel = (s/10) * 1.2;
        const volume = (g/10) * (isAccent ? 0.28 : 0.14);

        o.type = isAccent ? 'triangle' : 'sine';
        o.frequency.setValueAtTime(isAccent ? f * 1.01 : f, audioCtx.currentTime);
        fl.type = 'lowpass';
        fl.frequency.setValueAtTime(isAccent ? 2800 : 700, audioCtx.currentTime);

        gn.gain.setValueAtTime(0, audioCtx.currentTime);
        gn.gain.linearRampToValueAtTime(volume, audioCtx.currentTime + 0.02);
        gn.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + dur + rel);

        o.connect(fl); fl.connect(gn); gn.connect(audioCtx.destination);
        o.start(); o.stop(audioCtx.currentTime + dur + rel);
    }}

    btn.onclick = async () => {{
        if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if(audioCtx.state === 'suspended') await audioCtx.resume();
        btn.disabled = true; btn.style.background = "#444";
        let cur = 1;
        const ms = 60 / {bpm} * 1000;

        const loop = setInterval(() => {{
            clock.innerText = cur.toString().padStart(2, '0');
            document.querySelectorAll('#grid div').forEach(d => d.style.background = '#222');
            document.getElementById('dot-'+cur).style.background = '#FF7F50';

            const check = (n, r) => r.split(',').some(p => {{
                if(p.includes('-')) {{ let [a,b] = p.split('-').map(Number); return n>=a && n<=b; }}
                return Number(p) === n;
            }});

            const isAccent = (cur % 2 !== 0);
            if(check(cur, "{l1}")) playFlow(329.63, isAccent, {v_len}, {v_space}, {v_gain});
            if(check(cur, "{l2}")) playFlow(164.81, !isAccent, {v_len}, {v_space}, {v_gain});

            if(cur >= {stop_val}) {{ clearInterval(loop); btn.disabled = false; btn.style.background = "#FF7F50"; }}
            cur++;
        }}, ms);
    }};
</script>
"""

components.html(audio_engine_js, height=350)
