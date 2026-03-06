import streamlit as st
import streamlit.components.v1 as components

# --- 🎭 1. มิติดีไซน์ Logo3.jpg (เล็ก - เข้ม - ส้มเรืองแสง) ---
st.markdown("""
    <style>
    .stApp { background-color: #000000; }
    .main-panel { 
        border: 2px solid #FF7F50; 
        border-radius: 10px; 
        padding: 10px; 
        background: #0a0a0a;
        box-shadow: 0 0 15px #FF450033;
    }
    .neon-text { color: #FF7F50; font-family: monospace; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# ส่วนหัวจิ๋ว
c_logo, c_title = st.columns([1, 5])
with c_logo: 
    try: st.image("Logo3.jpg", width=50)
    except: st.write("💠")
with c_title: 
    st.markdown("<h4 style='color:#FF7F50; margin:0;'>SYNAPSE CORE v1.1.1</h4>", unsafe_allow_html=True)
    st.caption("สโลแกน: อยู่นิ่งๆ ไม่เจ็บตัว")

# --- 🎛️ 2. แผงควบคุม "3 ปุ่มสไลด์" (หัวใจหลัก) ---
with st.container():
    st.markdown("<div class='main-panel'>", unsafe_allow_html=True)
    
    # บรรทัดบน: ตั้งค่าทางเทคนิค (เล็กๆ)
    t1, t2, t3 = st.columns(3)
    v1_range = t1.text_input("V1 ช่วง", "1-4, 17-20")
    v2_range = t2.text_input("V2 ช่วง", "1-16")
    bpm = t3.number_input("BPM", 60, 240, 120)

    st.markdown("<hr style='border:0.5px solid #333;'>", unsafe_allow_html=True)
    
    # บรรทัดล่าง: 3 ปุ่มสไลด์มหาประลัย
    s1, s2, s3 = st.columns(3)
    sl_len = s1.slider("1. LENGTH", 0.1, 1.0, 0.4)
    sl_rev = s2.slider("2. REVERB", 0.0, 1.0, 0.3)
    sl_gain = s3.slider("3. GAIN", 0.0, 1.0, 0.5)
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- 🚀 3. เครื่องยนต์เสียง + กระดานห้องเพลง (JS ทำได้จริง) ---
# ปุ่มเล่น และตารางจะอยู่ใน Component เดียวกันเพื่อให้วิ่งพร้อมกันแบบไม่หลอก
audio_board_js = f"""
<div style="background:#000; padding:15px; border-radius:10px; border:1px solid #444; text-align:center; margin-top:10px;">
    <button id="play" style="width:100%; padding:10px; background:#FF7F50; border:none; border-radius:5px; font-weight:bold; cursor:pointer; color:#000;">
        ▶️ PLAY ENGINE
    </button>
    
    <div id="clock" style="font-size:50px; color:#00ff00; font-family:monospace; margin:10px 0;">00</div>
    
    <div id="board" style="display: flex; flex-wrap: wrap; justify-content: center; gap: 2px;"></div>
</div>

<script>
    let audioCtx;
    const btn = document.getElementById('play');
    const clock = document.getElementById('clock');
    const board = document.getElementById('board');

    // สร้างกระดาน 20 ห้อง
    for(let i=1; i<=20; i++) {{
        let dot = document.createElement('div');
        dot.id = 'step-' + i;
        dot.style.width = '15px'; dot.style.height = '15px';
        dot.style.background = '#222'; dot.style.borderRadius = '2px';
        board.appendChild(dot);
    }}

    function playSound(freq, dur, rev, gainVal) {{
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        const verb = audioCtx.createConvolver(); // จำลอง Reverb แบบจิ๋วด้วย Decay
        
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        gain.gain.setValueAtTime(gainVal, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + dur + rev);
        
        osc.start();
        osc.stop(audioCtx.currentTime + dur + rev);
    }}

    btn.onclick = async () => {{
        if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if(audioCtx.state === 'suspended') await audioCtx.resume();
        
        btn.disabled = true;
        let cur = 1;
        const interval = 60 / {bpm} * 1000;
        
        const loop = setInterval(() => {{
            clock.innerText = cur.toString().padStart(2, '0');
            
            // ล้างสีบอร์ดเก่า
            document.querySelectorAll('#board div').forEach(d => d.style.border = 'none');
            const currentDot = document.getElementById('step-' + cur);
            currentDot.style.border = '2px solid #fff';

            // เช็คช่วง V1, V2 และส่งเสียงตาม 3 ปุ่มสไลด์
            const isIn = (n, r) => r.split(',').some(p => {{
                if(p.includes('-')) {{ let [s,e] = p.split('-').map(Number); return n>=s && n<=e; }}
                return Number(p) === n;
            }});

            if(isIn(cur, "{v1_range}")) playSound(432, {sl_len}, {sl_rev}, {sl_gain});
            if(isIn(cur, "{v2_range}")) playSound(864, 0.1, {sl_rev}, {sl_gain} * 0.5);

            if(cur >= 20) {{
                clearInterval(loop);
                btn.disabled = false;
                clock.style.color = "#FF7F50";
            }}
            cur++;
        }}, interval);
    }};
</script>
"""

components.html(audio_board_js, height=300)

st.markdown("<p style='text-align:center; color:#444; font-size:10px;'>TRUTH SYSTEM 1.1.1 - NO DECEPTION</p>", unsafe_allow_html=True)
