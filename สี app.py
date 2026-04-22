import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import math
import firebase_admin
from firebase_admin import credentials, db
import base64
import os
import json

# ==========================================
# 1. FIREBASE AUTHENTICATION (ความจริงที่ปลอดภัย)
# ==========================================
if not firebase_admin._apps:
    try:
        if "firebase_credentials" in st.secrets:
            cred_dict = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_db_url"]
            })
        else:
            st.warning("⚠️ ตรวจพบ: ระบบ Firebase ยังไม่ได้ตั้งค่า Secrets (อยู่นิ่งๆ เพื่อความปลอดภัย)")
    except Exception as e:
        st.error(f"❌ Firebase Error: {e}")

# ==========================================
# 2. CORE ENGINE: SYNAPSE LOGIC v4.2
# ==========================================
def get_synapse_logic(dt):
    if dt is None: return None
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    
    # คำนวณจันทรคติอัตโนมัติ
    is_waxing = pos <= 14.765
    m_num = int(pos) + 1 if is_waxing else int(pos - 14.765) + 1
    
    # --- สูตรเด็ดเจ้านาย: จุดสมดุล 7.5 ---
    balance_point = m_num - 7.5
    
    # สูตรคำนวณตาม Logic ขึ้น/แรม (ไม่มั่ว)
    if is_waxing:
        res = math.sqrt((day_val**2) + (m_num**2))
        formula = f"√({day_val}² + {m_num}²)"
        logic_type = "Vector Force (พลังงานรวมตัว)"
    else:
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula = f"({day_val} × 1.618) / {m_num}"
        logic_type = "Golden Ratio (พลังงานกระจายตัว)"

    return {
        "res": round(res, 4),
        "phase": f"{'ขึ้น' if is_waxing else 'แรม'} {m_num} ค่ำ",
        "day": day_names[dt.weekday()],
        "formula": formula,
        "type": logic_type,
        "balance": round(balance_point, 2),
        "pos": round(pos, 2)
    }

# ==========================================
# 3. UI/UX CONFIG & ASSETS
# ==========================================
st.set_page_config(page_title="SYNAPSE : GLOBAL COMMAND", layout="wide")

# ระบบจัดการหน้าจอ (Session State)
if 'page' not in st.session_state:
    st.session_state.page = "main"
if 'user_res' not in st.session_state:
    st.session_state.user_res = 0.0

def change_page(p_name):
    st.session_state.page = p_name
    st.rerun()

# CSS จัดเต็ม (Dark Neon Theme)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .stApp { background-color: #050a0e; color: #00ff41; font-family: 'Courier New', monospace; }
    .main-title { font-family: 'Orbitron', sans-serif; color: #00ff41; text-align: center; text-shadow: 0 0 15px #00ff41; }
    
    /* Neon Cards */
    .neon-card {
        background: rgba(16, 26, 36, 0.9);
        border: 1px solid #00ff41;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.2);
        margin-bottom: 20px;
    }
    
    /* Hide Streamlit elements */
    header, footer, #MainMenu {visibility: hidden;}
    
    .stMetric { background: #0e161f; border-radius: 10px; border-bottom: 3px solid #00ff41; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 4. PAGE: MAIN COMMAND CENTER (ระบบสแกน)
# ==========================================
if st.session_state.page == "main":
    st.markdown("<h1 class='main-title'>🛰️ SYNAPSE COMMAND CENTER</h1>", unsafe_allow_html=True)
    st.write("<center><i>'อยู่นิ่งๆ ไม่เจ็บตัว' | ระบบสแกนพิกัดความถี่ชีวิต v4.2</i></center>", unsafe_allow_html=True)
    
    st.divider()

    # --- ส่วนที่ 1: ข้อมูลผู้ใช้งาน ---
    with st.container():
        st.subheader("👤 บุคคลที่ 1 (ตัวตั้งต้น)")
        c1, c2 = st.columns([2, 1])
        with c1:
            u_dob = st.date_input("ระบุวันเดือนปีเกิด (ค.ศ.)", value=None, min_value=date(1940, 1, 1))
        with c2:
            if st.button("🎧 OPEN MUSIC DECK", use_container_width=True):
                change_page("music")

    if u_dob:
        u = get_synapse_logic(u_dob)
        st.session_state.user_res = u['res']
        
        # แสดง Metric
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("รหัสประจำตัว", u['res'])
        m2.metric("พิกัดจันทรคติ", u['phase'])
        m3.metric("จุดสมดุล 7.5", u['balance'])
        m4.metric("วัน", u['day'])

        with st.expander("📝 รายละเอียดสมการ"):
            st.code(f"Logic: {u['type']}\nFormula: {u['formula']}\nPos: {u['pos']}")

        st.divider()

        # --- ส่วนที่ 2: ระบบสแกนคู่ขนาน ---
        st.subheader("🔍 วิเคราะห์ Gap ปัจจุบัน (เทียบพิกัดวัน/บุคคล)")
        target_date = st.date_input("เลือกวันที่หรือวันเกิดบุคคลที่ 2", date.today())
        
        if target_date:
            t = get_synapse_logic(target_date)
            gap = abs(u['res'] - t['res'])
            
            st.markdown(f"<div class='neon-card'><b>พิกัดวันนี้:</b> {t['day']} ({t['phase']}) | <b>รหัส:</b> {t['res']}</div>", unsafe_allow_html=True)
            
            # การแจ้งเตือนพิกัด
            if gap < 0.5:
                st.success(f"💎 **พิกัดบรรจบ (Gap: {gap:.4f})**")
                st.balloons()
            elif 3.8 <= gap <= 4.2:
                st.warning(f"🌀 **พิกัดสะท้อน Gap 4 (Gap: {gap:.4f})**")
            elif gap > 10.0:
                st.error(f"🚩 **พิกัดแยกตัว (Gap: {gap:.4f})**")
            else:
                st.info(f"อิสระ (Gap: {gap:.4f})")

        # --- ส่วนที่ 3: ระบบสแกนล่วงหน้า 365 วัน ---
        st.divider()
        st.subheader("🗓️ ตารางพยากรณ์พิกัดพิเศษ (365 วัน)")
        
        days_to_scan = st.slider("ขอบเขตการสแกน (วัน)", 30, 365, 180)
        
        scan_data = []
        for i in range(days_to_scan):
            d_check = date.today() + timedelta(days=i)
            l = get_synapse_logic(d_check)
            g = abs(u['res'] - l['res'])
            
            status = ""
            if g < 0.5: status = "💎 บรรจบ (Meet)"
            elif 3.8 <= g <= 4.2: status = "🌀 สะท้อน (Reflect)"
            elif g > 12.0: status = "🚩 แยก (Detach)"
            
            if status:
                scan_data.append({
                    "Date": d_check.strftime("%d/%m/%Y"),
                    "Day": l['day'],
                    "Status": status,
                    "Gap": round(g, 4),
                    "Code": l['res']
                })
        
        if scan_data:
            df = pd.DataFrame(scan_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # บันทึกความจริงลง Firebase
            if st.button("📤 บันทึก Log สแกนลง Cloud"):
                try:
                    ref = db.reference('/synapse_scans')
                    ref.push({
                        'user': u['res'],
                        'scan_date': str(date.today()),
                        'results_count': len(scan_data)
                    })
                    st.toast("บันทึกสำเร็จ!")
                except: st.error("Firebase Connection Lost")
        else:
            st.write("ไม่พบจุดบรรจบพิกัดในช่วงที่เลือก")

# ==========================================
# 5. PAGE: MUSIC DECK (เครื่องเล่นเพลง)
# ==========================================
elif st.session_state.page == "music":
    st.markdown("<h1 class='main-title'>🎵 SYNAPSE MUSIC DECK</h1>", unsafe_allow_html=True)
    
    # HTML5 & JavaScript Mixer
    music_html = f"""
    <div style="background:#0a0e14; border:2px solid #00ff41; border-radius:20px; padding:30px; font-family:sans-serif; color:#00ff41;">
        <canvas id="visualizer" style="width:100%; height:120px; background:#000; border-radius:10px; margin-bottom:20px;"></canvas>
        
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:20px;">
            <div style="border:1px solid #ff00de; padding:15px; border-radius:10px;">
                <label style="color:#ff00de;">DECK A (Primary)</label><br>
                <input type="file" id="audA" accept="audio/*" style="margin-top:10px; color:#fff;">
                <audio id="pA" loop></audio>
                <div style="margin-top:10px;">
                    <button onclick="pA.play()" style="background:#ff00de; border:none; color:white; padding:5px 15px; border-radius:5px; cursor:pointer;">PLAY</button>
                    <button onclick="pA.pause()" style="background:#333; border:none; color:white; padding:5px 15px; border-radius:5px; cursor:pointer;">PAUSE</button>
                </div>
            </div>
            <div style="border:1px solid #00f3ff; padding:15px; border-radius:10px;">
                <label style="color:#00f3ff;">DECK B (Ambient)</label><br>
                <input type="file" id="audB" accept="audio/*" style="margin-top:10px; color:#fff;">
                <audio id="pB" loop></audio>
                <div style="margin-top:10px;">
                    <button onclick="pB.play()" style="background:#00f3ff; border:none; color:white; padding:5px 15px; border-radius:5px; cursor:pointer;">PLAY</button>
                    <button onclick="pB.pause()" style="background:#333; border:none; color:white; padding:5px 15px; border-radius:5px; cursor:pointer;">PAUSE</button>
                </div>
            </div>
        </div>
        
        <div style="margin-top:30px; text-align:center;">
            <label>CROSSFADER (A <-> B)</label><br>
            <input type="range" id="fader" min="0" max="100" value="50" style="width:80%; accent-color:#00ff41;">
        </div>
    </div>

    <script>
        const pA = document.getElementById('pA');
        const pB = document.getElementById('pB');
        const fader = document.getElementById('fader');
        
        document.getElementById('audA').onchange = function(e) {{ pA.src = URL.createObjectURL(this.files[0]); }};
        document.getElementById('audB').onchange = function(e) {{ pB.src = URL.createObjectURL(this.files[0]); }};
        
        fader.oninput = function() {{
            pA.volume = (100 - this.value) / 100;
            pB.volume = this.value / 100;
        }};

        // Visualizer Logic
        const canvas = document.getElementById('visualizer');
        const ctx = canvas.getContext('2d');
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const src = audioCtx.createMediaElementSource(pA);
        const analyzer = audioCtx.createAnalyser();
        src.connect(analyzer);
        analyzer.connect(audioCtx.destination);
        analyzer.fftSize = 256;
        const bufferLength = analyzer.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        function draw() {{
            requestAnimationFrame(draw);
            analyzer.getByteFrequencyData(dataArray);
            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            let barWidth = (canvas.width / bufferLength) * 2.5;
            let x = 0;
            for(let i=0; i<bufferLength; i++) {{
                let bh = dataArray[i]/2;
                ctx.fillStyle = 'rgb(0,' + (bh+100) + ', 65)';
                ctx.fillRect(x, canvas.height-bh, barWidth, bh);
                x += barWidth + 1;
            }}
        }}
        draw();
    </script>
    """
    st.components.v1.html(music_html, height=500)

    if st.button("⬅️ BACK TO COMMAND CENTER"):
        change_page("main")

# ==========================================
# 6. FOOTER (คติประจำใจ)
# ==========================================
st.divider()
st.caption(f"SYNAPSE v4.2 | Logic by Ta101 | 'อยู่นิ่งๆ ไม่เจ็บตัว' | {date.today().year}")
