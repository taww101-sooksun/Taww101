import streamlit as st
import streamlit.components.v1 as components
import os

# --- 🎭 1. ดีไซน์แบบเครื่องจักร (Dark & Neon Orange) ---
st.set_page_config(page_title="SYNAPSE INDEPENDENT", layout="wide") # ปรับเป็น wide เพื่อให้วางสไลด์สวยๆ

st.markdown("""
    <style>
    .stApp { background-color: #000; color: #FF7F50; }
    .chan-card { 
        border: 1px solid #333; border-radius: 8px; padding: 10px; 
        background: #080808; margin-bottom: 10px;
    }
    .neon-text { color: #00ff00; font-family: monospace; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# --- 🖼️ 2. ส่วนหัว (logo3.jpg) ---
c1, c2 = st.columns([1, 8])
with c1:
    if os.path.exists("logo3.jpg"): st.image("logo3.jpg", width=60)
    else: st.write("🔊")
with c2:
    st.markdown("<h2 style='margin:0; color:#FF7F50;'>SYNAPSE INDEPENDENT v1.5.0</h2>", unsafe_allow_html=True)

# --- 🎛️ 3. แผงควบคุม 10 เลเยอร์แบบแยกอิสระ ---
st.markdown("<p class='neon-text'>🎚️ INDEPENDENT CHANNEL MIXER</p>", unsafe_allow_html=True)

# ฟังก์ชันสร้างช่องควบคุม
def create_channel(name, default_seq, freq_val, type_val):
    with st.container():
        st.markdown(f"<div class='chan-card'>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([2, 2, 3, 3])
        seq = col1.text_input(f"{name}", default_seq, key=f"seq_{name}")
        sus = col3.slider(f"ยาว (SUS)", 0.1, 3.0, 0.8, key=f"sus_{name}")
        tone = col4.slider(f"ทุ้ม-แหลม", 100, 5000, 2000, key=f"tone_{name}")
        st.markdown("</div>", unsafe_allow_html=True)
        return {"seq": seq, "sus": sus, "tone": tone, "freq": freq_val, "type": type_val}

# สร้าง 10 ช่อง (ปรับแยกได้เหมือนกันทุกช่อง)
channels = []
ch_data = [
    ("1. SUB BASS", "1-20", 50, "sine"),
    ("2. KICK", "1, 5, 9, 13, 17", 120, "sine"),
    ("3. LOW (DO)", "1, 9", 261, "triangle"),
    ("4. MID (RE)", "2, 10", 293, "triangle"),
    ("5. HIGH (MI)", "3, 11", 329, "triangle"),
    ("6. LEAD", "5, 13", 440, "sawtooth"),
    ("7. HI-HAT", "1-20", 6000, "sine"),
    ("8. SFX", "4, 12", 1000, "square"),
    ("9. VOCAL", "1, 17", 350, "sawtooth"),
    ("10. TAIL", "20", 150, "sine")
]

for name, seq, f, t in ch_data:
    channels.append(create_channel(name, seq, f, t))

bpm = st.slider("ความเร็ว (BPM)", 60, 180, 120)

# --- 🚀 4. JavaScript Engine: พลังแยก 10 ทาง ---
# สร้างอาเรย์ข้อมูลส่งไป JS
js_channels = str([{ "seq": c["seq"], "sus": c["sus"], "tone": c["tone"], "freq": c["freq"], "type": c["type"] } for c in channels])

audio_engine_js = f"""
<div style="background:#000; padding:20px; border:1px solid #FF7F50; border-radius:10px; text-align:center; margin-top:10px;">
    <button id="run" style="width:100%; padding:20px; background:#FF7F50; border:none; border-radius:8px; font-weight:bold; font-size:24px; cursor:pointer;">
        🔴 EXECUTE 10-CHANNEL MIXER
    </button>
    <div id="clock" style="font-size:80px; color:#00ff00; font-family:monospace; margin:10px 0;">00</div>
</div>

<script>
    let audioCtx;
    const btn = document.getElementById('run');
    const clock = document.getElementById('clock');
    const chData = {js_channels};

    function play(f, type, sus, filterFreq) {{
        const o = audioCtx.createOscillator();
        const g = audioCtx.createGain();
        const fl = audioCtx.createBiquadFilter();

        o.type = type;
        o.frequency.setValueAtTime(f, audioCtx.currentTime);
        fl.type = 'lowpass';
        fl.frequency.setValueAtTime(filterFreq, audioCtx.currentTime);

        g.gain.setValueAtTime(0, audioCtx.currentTime);
        g.gain.linearRampToValueAtTime(0.2, audioCtx.currentTime + 0.02);
        g.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + sus);

        o.connect(fl); fl.connect(g); g.connect(audioCtx.destination);
        o.start(); o.stop(audioCtx.currentTime + sus);
    }}

    btn.onclick = async () => {{
        if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        if(audioCtx.state === 'suspended') await audioCtx.resume();
        btn.disabled = true;
        let step = 1;
        const ms = 60 / {bpm} * 1000;

        const loop = setInterval(() => {{
            clock.innerText = step.toString().padStart(2, '0');

            chData.forEach(ch => {{
                const check = (n, r) => r.split(',').some(p => {{
                    if(p.includes('-')) {{ let [a,b] = p.split('-').map(Number); return n>=a && n<=b; }}
                    return Number(p) === n;
                }});

                if(check(step, ch.seq)) {{
                    play(ch.freq, ch.type, ch.sus, ch.tone);
                }}
            }});

            if(step >= 20) {{ clearInterval(loop); btn.disabled = false; }}
            step++;
        }}, ms);
    }};
</script>
"""

components.html(audio_engine_js, height=300)
