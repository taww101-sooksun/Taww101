import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import math
import os
import base64
import time
from datetime import datetime, date

# --- [ 1. CONFIG & UI NEON STYLE ] ---
st.set_page_config(page_title="SYNAPSE X - THE ULTIMATE TRUTH", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp { background-color: #000; color: #00ff41; font-family: 'Courier New', monospace; }
    .neon-title { font-family: 'Orbitron', sans-serif; color: #fff; text-align: center; text-shadow: 0 0 10px #ff00de, 0 0 20px #00f3ff; letter-spacing: 3px; }
    .logic-box { background-color: #101a24; padding: 15px; border-left: 5px solid #00ff41; border-radius: 10px; margin-bottom: 20px; color: #f0f0f0; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- [ 2. LOGIC ENGINE: COSMIC DECODER ] ---
def get_detailed_logic(dt):
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    day_name = day_names[dt.weekday()]

    if pos <= 14.765:
        m_num = int(pos) + 1
        phase = f"ขึ้น {m_num} ค่ำ"
        res = math.sqrt((day_val**2) + (m_num**2))
        formula = f"√({day_val}² + {m_num}²)"
        logic_type = "แรงผลักดัน (Vector Energy)"
    else:
        m_num = int(pos - 14.765) + 1
        phase = f"แรม {m_num} ค่ำ"
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula = f"({day_val} × 1.618) / {m_num}"
        logic_type = "สมดุลสัดส่วนทองคำ (Golden Ratio)"
    return {"res": round(res, 4), "phase": phase, "day_name": day_name, "formula": formula, "type": logic_type}

# --- [ 3. SIDEBAR NAVIGATION ] ---
st.sidebar.markdown("<h2 class='neon-title'>SYNAPSE X</h2>", unsafe_allow_html=True)
st.sidebar.write(f"ID: **Ta101 / Bas**")
menu = st.sidebar.radio("เลือกโหมดการทำงาน", ["🛰️ RADAR & SENSORS", "🧬 COSMIC DECODER", "🎧 NEON MIXER V5"])
st.sidebar.divider()
st.sidebar.write('สโลแกน: **"อยู่นิ่งๆ ไม่เจ็บตัว"**')

# ==========================================
# 🛰️ MODE 1: RADAR & SENSORS (GPS, SOUND, MOTION)
# ==========================================
if menu == "🛰️ RADAR & SENSORS":
    st.markdown("<h1 class='neon-title'>REAL-TIME SENSORS</h1>", unsafe_allow_html=True)
    
    # รวม JS Sensors ทั้งหมด (GPS, Battery, Audio, Motion)
    all_sensors_js = """
    <div style="background: #111; color: #00ff41; padding: 20px; border: 2px solid #00ff41; border-radius: 20px; font-family: monospace;">
        <div id="status" style="color: #00ffff; text-align:center;">🛰️ ระบบเซนเซอร์ออนไลน์</div>
        <hr border="1" color="#333">
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top:10px;">
            <div style="background:#000; padding:10px; border-radius:10px;">
                <small>📍 GPS พิกัด</small>
                <div id="gps">- / -</div>
            </div>
            <div style="background:#000; padding:10px; border-radius:10px;">
                <small>🔋 แบตเตอรี่</small>
                <div id="bat">--%</div>
            </div>
        </div>

        <div style="margin-top:15px; background:#000; padding:15px; border-radius:10px;">
            <canvas id="scope" style="width:100%; height:80px;"></canvas>
            <div style="display:flex; justify-content:space-around; margin-top:10px;">
                <div>🔊 <span id="vol">0</span> dB</div>
                <div>📡 <span id="hz">0</span> Hz</div>
                <div>📳 <span id="vib">0.00</span> G</div>
            </div>
        </div>
        
        <button id="start" style="width: 100%; padding: 15px; margin-top: 15px; background: #00ff41; color: #000; border: none; border-radius: 10px; font-weight: bold; cursor: pointer;">เปิดใช้งานระบบสแกนความจริง</button>
    </div>

    <script>
        const btn = document.getElementById('start');
        btn.onclick = async () => {
            btn.style.display = 'none';
            // GPS
            navigator.geolocation.watchPosition(p => {
                document.getElementById('gps').innerText = p.coords.latitude.toFixed(4) + ", " + p.coords.longitude.toFixed(4);
            });
            // Battery
            const bat = await navigator.getBattery();
            const upBat = () => { document.getElementById('bat').innerText = (bat.level*100).toFixed(0) + "%"; };
            upBat(); bat.addEventListener('levelchange', upBat);
            
            // Audio & Visualizer
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const ac = new AudioContext();
            const ana = ac.createAnalyser();
            ac.createMediaStreamSource(stream).connect(ana);
            const data = new Uint8Array(ana.frequencyBinCount);
            
            // Motion
            window.addEventListener('devicemotion', e => {
                let a = e.accelerationIncludingGravity;
                let g = Math.sqrt(a.x*a.x + a.y*a.y + a.z*a.z) / 9.8;
                document.getElementById('vib').innerText = g.toFixed(2);
            });

            const canvas = document.getElementById('scope');
            const ctx = canvas.getContext('2d');
            function draw() {
                requestAnimationFrame(draw);
                ana.getByteFrequencyData(data);
                ctx.clearRect(0,0,canvas.width,canvas.height);
                let sum = 0;
                for(let i=0; i<data.length; i++) {
                    sum += data[i];
                    ctx.fillStyle = '#00ff41';
                    ctx.fillRect(i*2, canvas.height - data[i]/2, 1, data[i]/2);
                }
                document.getElementById('vol').innerText = Math.round(sum/data.length);
            }
            draw();
        };
    </script>
    """
    components.html(all_sensors_js, height=450)
    st.info("💡 ทุกค่ามาจากฮาร์ดแวร์มือถือโดยตรง 'อยู่นิ่งๆ ไม่เจ็บตัว' ความจริงจะปรากฏครับ")

# ==========================================
# 🧬 MODE 2: COSMIC DECODER (V.SCANNER)
# ==========================================
elif menu == "🧬 COSMIC DECODER":
    st.markdown("<h1 class='neon-title'>COSMIC SCANNER</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        dob1 = st.date_input("👤 วันเกิดบุคคลที่ 1", value=date(1996, 8, 17), key="d1")
    with col2:
        dob2 = st.date_input("👤 วันเกิดบุคคลที่ 2", value=date.today(), key="d2")

    if dob1 and dob2:
        d1 = get_detailed_logic(dob1)
        d2 = get_detailed_logic(dob2)
        
        st.divider()
        c_a, c_b = st.columns(2)
        c_a.metric("รหัสบุคคลที่ 1", d1['res'])
        c_b.metric("รหัสบุคคลที่ 2", d2['res'])
        
        gap = abs(d1['res'] - d2['res'])
        st.markdown(f"<h2 style='text-align:center;'>GAP ANALYZER: {gap:.4f}</h2>", unsafe_allow_html=True)
        
        if 3.5 <= gap <= 4.5:
            st.error("⚠️ ตรวจพบรหัสคู่ขนาน (Parallel Connection) - มีพันธะเชื่อมโยงสูง!")
            st.balloons()
        else:
            st.success("✅ พิกัดอิสระ - พลังงานสมดุล")

# ==========================================
# 🎧 MODE 3: NEON MIXER V5 (AUTO-MIX ENGINE)
# ==========================================
else:
    st.markdown("<h1 class='neon-title'>NEON AUTO-MIXER</h1>", unsafe_allow_html=True)
    
    mixer_html = """
    <div style="background: rgba(0,0,0,0.9); padding: 20px; border: 2px solid #ff00de; border-radius: 20px; text-align: center;">
        <canvas id="mixScope" style="width:100%; height:120px; background:#000; border-radius:10px; margin-bottom:15px;"></canvas>
        <div style="display:flex; justify-content:space-between; gap:10px;">
            <div id="deckA" style="flex:1; border:1px solid #ff00de; padding:10px; border-radius:10px;">
                <small style="color:#ff00de;">DECK A</small>
                <input type="file" id="inA" style="font-size:10px; width:100%;">
                <div id="timeA" style="font-family:monospace; margin-top:5px;">00:00</div>
            </div>
            <div id="deckB" style="flex:1; border:1px solid #00f3ff; padding:10px; border-radius:10px;">
                <small style="color:#00f3ff;">DECK B</small>
                <input type="file" id="inB" style="font-size:10px; width:100%;">
                <div id="timeB" style="font-family:monospace; margin-top:5px;">00:00</div>
            </div>
        </div>
        <button id="playMix" style="width:100%; padding:15px; margin-top:20px; background:linear-gradient(45deg, #ff00de, #00f3ff); border:none; border-radius:10px; font-weight:bold; cursor:pointer; color:#fff;">🔥 START AUTO-MIX</button>
    </div>

    <script>
        let ac, ana, sA, sB, gA, gB;
        document.getElementById('playMix').onclick = async () => {
            if(!ac) ac = new AudioContext();
            ana = ac.createAnalyser();
            
            const load = async (id) => {
                const f = document.getElementById(id).files[0];
                return ac.decodeAudioData(await f.arrayBuffer());
            };
            
            const bA = await load('inA'); const bB = await load('inB');
            
            sA = ac.createBufferSource(); sA.buffer = bA; sA.loop = true;
            gA = ac.createGain(); sA.connect(gA).connect(ana).connect(ac.destination);
            
            sB = ac.createBufferSource(); sB.buffer = bB; sB.loop = true;
            gB = ac.createGain(); gB.gain.value = 0; sB.connect(gB).connect(ana).connect(ac.destination);
            
            sA.start(); sB.start();
            
            // Simple Auto-Crossfade
            setInterval(() => {
                let now = ac.currentTime;
                if(gA.gain.value > 0) {
                    gA.gain.linearRampToValueAtTime(0, now + 5);
                    gB.gain.linearRampToValueAtTime(1, now + 5);
                } else {
                    gB.gain.linearRampToValueAtTime(0, now + 5);
                    gA.gain.linearRampToValueAtTime(1, now + 5);
                }
            }, 15000);
        };
    </script>
    """
    components.html(mixer_html, height=500)

st.divider()
st.caption(f"SYNAPSE X CORE V26.4 | 'อยู่นิ่งๆ ไม่เจ็บตัว' | {date.today()}")
