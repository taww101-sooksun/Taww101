import streamlit as st
import streamlit.components.v1 as components

# --- 🎭 1. มิติดีไซน์สไตล์ Logo3.jpg (เล็ก - เข้ม - ส้มเรืองแสง) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .main-panel { 
        border: 2px solid #FF7F50; 
        border-radius: 12px; 
        padding: 15px; 
        background: #080808;
        box-shadow: 0 0 20px rgba(255, 127, 80, 0.15);
    }
    .neon-text { color: #FF7F50; font-family: 'Courier New', monospace; }
    /* ปรับแต่ง Slider ให้ดูเท่ */
    .stSlider { padding-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# ส่วนหัวจิ๋ว
c_logo, c_title = st.columns([1, 5])
with c_logo: 
    try: st.image("Logo3.jpg", width=55)
    except: st.write("💠")
with c_title: 
    st.markdown("<h3 style='color:#FF7F50; margin:0;'>SYNAPSE CORE v1.1.2</h3>", unsafe_allow_html=True)
    st.caption("TRUTH ENGINE | 3,000 HOURS EXPERIENCE")

# --- 🎛️ 2. แผงควบคุม "3 ปุ่มสไลด์ (สเกล 0-10)" ---
with st.container():
    st.markdown("<div class='main-panel'>", unsafe_allow_html=True)
    
    # ส่วนตั้งค่าช่วงเวลา
    t1, t2, t3 = st.columns(3)
    v1_range = t1.text_input("V1 ช่วง", "1-4, 17-20")
    v2_range = t2.text_input("V2 ช่วง", "1-16")
    bpm = t3.number_input("BPM (ความเร็ว)", 60, 240, 120)

    st.markdown("<hr style='border:0.5px solid #222;'>", unsafe_allow_html=True)
    
    # 🎯 3 ปุ่มสไลด์ที่พี่สั่ง (0.0 - 10.0)
    s1, s2, s3 = st.columns(3)
    # เราจะเอาค่า 0-10 นี้ไปคุมมิติเสียงข้างใน JS
    val_len = s1.slider("1. มิติยาว (LENGTH)", 0.0, 10.0, 5.0)
    val_space = s2.slider("2. มิติกว้าง (SPACE)", 0.0, 10.0, 3.0)
    val_gain = s3.slider("3. มิติดัง (GAIN)", 0.0, 10.0, 7.0)
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- 🚀 3. JavaScript: เครื่องยนต์เสียงสังเคราะห์ (ไม่เหมือนนาฬิกา) ---
# แมปค่า 0-10 ให้เป็นค่าทางเทคนิคที่นิ่งที่สุด
audio_js = f"""
<div style="background:#000; padding:15px; border-radius:10px; border:1px solid #333; text-align:center; margin-top:15px;">
    <button id="runBtn" style="width:100%; padding:15px; background:#FF7F50; border:none; border-radius:8px; font-weight:bold; font-size:18px; color:#000; cursor:pointer; box-shadow: 0 0 15px #FF4500;">
        🔴 EXECUTE SYSTEM
    </button>
    
    <div id="clock" style="font-size:70px; color:#00ff00; font-family:monospace; margin:10px 0; text-shadow: 0 0 10px #00ff00;">00</div>
    
    <div id="board" style="display: flex; flex-wrap: wrap; justify-content: center; gap: 3px;"></div>
</div>

<script>
    let audioCtx;
    const runBtn = document.getElementById('runBtn');
    const clockDisp = document.getElementById('clock');
    const board = document.getElementById('board');

    // วาดจุดห้อง 20 ห้องแบบจิ๋ว
    for(let i=1; i<=20; i++) {{
        let d = document.createElement('div');
        d.id = 'bar-' + i;
        d.style.width = '12px'; d.style.height = '12px';
        d.style.background = '#222'; d.style.borderRadius = '50%';
        board.appendChild(d);
    }}

    // ฟังก์ชันสร้างเสียงสังเคราะห์ (Synth Tone)
    function playSynth(freq, type, l, s, g) {{
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        const filter = audioCtx.createBiquadFilter();

        // แมปค่า 0-10 จากสไลด์ของพี่
        const duration = (l / 10) * 1.5 + 0.05; // 0-10 -> 0.05s ถึง 1.55s
        const release = (s / 10) * 1.0;        // 0-10 -> หางเสียงยาวขึ้น
        const volume = (g / 10) * 0.3;         // 0-10 -> ความดังบาลานซ์

        osc.type = type; // ใช้เสียงแบบ Triangle หรือ Square เพื่อความนุ่ม
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);

        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(2000, audioCtx.currentTime); // ตัดเสียงแหลมให้ไม่เหมือนนาฬิกา

        gain.gain.setValueAtTime(volume, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration + release);

        osc.connect(filter);
        filter.connect(gain);
        gain.connect(audioCtx.destination);

        osc.start();
        osc.stop(audioCtx.currentTime + duration + release);
    }}

    runBtn.onclick = async () => {{
        if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if(audioCtx.state === 'suspended') await audioCtx.resume();
        
        runBtn.disabled = true;
        let step = 1;
        const speed = 60 / {bpm} * 1000;

        const loop = setInterval(() => {{
            clockDisp.innerText = step.toString().padStart(2, '0');
            
            // ไฟวิ่งในตาราง
            document.querySelectorAll('#board div').forEach(d => d.style.boxShadow = 'none');
            const activeDot = document.getElementById('bar-' + step);
            activeDot.style.boxShadow = '0 0 10px #fff';
            activeDot.style.background = '#FF7F50';

            const check = (n, r) => r.split(',').some(p => {{
                if(p.includes('-')) {{ let [a,b] = p.split('-').map(Number); return n>=a && n<=b; }}
                return Number(p) === n;
            }});

            // ส่งค่า 0-10 จากสไลด์ไปที่เสียง
            if(check(step, "{v1_range}")) playSynth(329.63, 'triangle', {val_len}, {val_space}, {val_gain}); // เสียง E4 นุ่มๆ
            if(check(step, "{v2_range}")) playSynth(164.81, 'sine', 2, {val_space}, {val_gain} * 0.5);     // เสียงทุ้มลึก

            if(step >= 20) {{
                clearInterval(loop);
                runBtn.disabled = false;
                clockDisp.style.color = "#FF7F50";
            }}
            step++;
        }}, speed);
    }};
</script>
"""

components.html(audio_js, height=320)

st.markdown("<p style='text-align:center; color:#555; font-size:11px;'>SYNAPSE v1.1.2 | NO CLOCK SOUND | 0-10 CONTROL</p>", unsafe_allow_html=True)
