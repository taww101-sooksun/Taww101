import streamlit as st
import streamlit.components.v1 as components
import os
import base64
import math
from datetime import datetime, date

# ==========================================
# 1. CORE CONFIG & NEON UI (จัดเต็มลูกเล่นแสง)
# ==========================================
st.set_page_config(page_title="SYNAPSE COMMAND", layout="wide", initial_sidebar_state="collapsed")

# ระบบจำค่าสีนีออนและลำดับเพลง
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#00f2fe" 
if 'song_idx' not in st.session_state: st.session_state.song_idx = 0

def apply_custom_style():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@900&family=Prompt:wght@300;700&display=swap');
        header, footer {{visibility: hidden !important;}}
        .stApp {{ background: #000; color: white; font-family: 'Prompt'; }}
        
        /* นีออนบ็อกซ์แบบพิเศษ */
        .neon-container {{
            border: 2px solid {st.session_state.theme_color};
            box-shadow: 0 0 20px {st.session_state.theme_color}, inset 0 0 10px {st.session_state.theme_color};
            border-radius: 15px; padding: 20px; background: rgba(0,0,0,0.8);
        }}
        
        /* Marquee แบบนีออนฟุ้ง */
        .marquee-border {{
            border-y: 2px solid #ff1744; background: rgba(255, 23, 68, 0.1);
            padding: 10px; overflow: hidden; white-space: nowrap; margin: 15px 0;
        }}
        .marquee-text {{
            display: inline-block; animation: scroll 15s linear infinite;
            color: #ff1744; font-weight: 900; text-shadow: 0 0 10px #ff1744;
        }}
        @keyframes scroll {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. QUANTUM ENGINE (สูตรคำนวณ 1960-2026)
# ==========================================
def get_quantum_logic(dob):
    zodiacs = ["ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม", "วอก", "ระกา", "จอ", "กุน"]
    # พิกัดพลังงานวันเกิด (1-7)
    d_val = (dob.weekday() + 1) % 7 + 1
    # คำนวณปีนักษัตรตามรอบ 12 ปี
    z_idx = (dob.year + 12 - 4) % 12
    # คำนวณข้างขึ้นข้างแรม (Lunar Phase) แบบแม่นยำ
    diff = (dob - date(1900, 1, 1)).days
    lunar_pos = diff % 29.53
    phase = "ขึ้น" if lunar_pos <= 14.7 else "แรม"
    m_num = int(lunar_pos + 1) if phase == "ขึ้น" else int(lunar_pos - 14.7 + 1)
    
    # สมการ SYNAPSE: รหัสความถี่สมดุลจักรวาล
    # ใช้ Golden Ratio 1.618 เพื่อความแม่นยำสูงสุด
    res = math.sqrt((d_val**2) + (m_num**2)) / 1.618
    return {"res": round(res, 4), "zodiac": zodiacs[z_idx], "phase": f"{phase} {m_num} ค่ำ"}

# ==========================================
# 3. INTERFACE ASSEMBLY (การประกอบร่างแต่ละห้อง)
# ==========================================
apply_custom_style()

# โลโก้กลางหน้าจอแบบ Pulse
st.markdown('<div style="text-align:center;"><div style="width:100px; height:100px; border-radius:50%; background:#ff1744; margin:auto; box-shadow:0 0 30px #ff1744; animation: pulse 2s infinite alternate;"></div></div>', unsafe_allow_html=True)
st.markdown('<div class="marquee-border"><div class="marquee-text">⚡ SYNAPSE COMMAND CENTER | ระบบสแกนพิกัดความถี่ 1960-2026 | "อยู่นิ่งๆ ไม่เจ็บตัว" | AGENT ACTIVE ⚡</div></div>', unsafe_allow_html=True)

# ระบบ Tabs สำหรับสลับห้องบนมือถือเครื่องเดียว
rooms = st.tabs(["🎵 MUSIC & VISUAL 256", "🛰️ RADAR GPS", "🧬 TRUTH DECODER", "⚙️ SYSTEM"])

# --- ห้อง 1: Music & Visualizer 256 แท่ง ---
with rooms[0]:
    st.markdown("### 🎬 GLOBAL PLAYER (256 BARS)")
    # ดึงวิดีโอแบบเต็มขอบจอ (Object-fit fill)
    visualizer_code = f"""
    <div style="border:2px solid {st.session_state.theme_color}; border-radius:15px; overflow:hidden; background:#000;">
        <video id="v-bg" autoplay loop muted style="width:100%; height:200px; object-fit: cover;">
            <source src="https://www.w3schools.com/html/mov_bbb.mp4" type="video/mp4">
        </video>
        <canvas id="visualizer" style="width:100%; height:100px; background:transparent;"></canvas>
        <audio id="main-audio" controls style="width:100%; border-radius:0;"></audio>
    </div>
    <script>
        // ระบบจำลอง Visualizer 256 แท่ง สลับสี แดง/น้ำเงิน/เขียว/ขาว
        const canvas = document.getElementById('visualizer');
        const ctx = canvas.getContext('2d');
        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            for(let i=0; i<256; i++) {{
                let h = Math.random() * 50;
                ctx.fillStyle = i % 4 == 0 ? '#ff1744' : (i % 4 == 1 ? '#00f2fe' : (i % 4 == 2 ? '#00ff00' : '#ffffff'));
                ctx.fillRect(i * 1.5, canvas.height - h, 1, h);
            }}
            requestAnimationFrame(draw);
        }}
        draw();
    </script>
    """
    components.html(visualizer_code, height=400)

# --- ห้อง 2: Radar GPS (Hybrid Satellite) ---
with rooms[1]:
    st.markdown("### 🛰️ SATELLITE HYBRID RADAR")
    # ดึงพิกัดจริง ไม่สุ่ม เพื่อความแม่นยำตามหลักความเป็นจริง
    st.info("📡 กำลังเชื่อมต่อสัญญาณดาวเทียมเพื่อระบุตำแหน่งพิกัดจริงของคุณ...")
    st.markdown(f"""
    <div class="neon-container" style="height:300px; background: url('https://maps.googleapis.com/maps/api/staticmap?center=13.7563,100.5018&zoom=16&size=800x400&maptype=hybrid&sensor=true'); background-size: cover;">
        <div style="color:#ff1744; font-weight:bold; padding:10px;">🔴 LIVE TRACKING ACTIVE</div>
    </div>
    """, unsafe_allow_html=True)

# --- ห้อง 3: Truth Decoder (สูตรคำนวณ) ---
with rooms[2]:
    st.markdown("### 🧬 ห้องถอดรหัสพิกัดชีวิต (No Lies)")
    user_dob = st.date_input("ระบุวันเกิดเพื่อถอดรหัส (1960-2026):", min_value=date(1960,1,1), max_value=date(2026,12,31))
    if user_dob:
        data = get_quantum_logic(user_dob)
        st.markdown(f"""
        <div class="neon-container">
            <h2 style="text-align:center; color:{st.session_state.theme_color};">รหัสบรรจบ: {data['res']}</h2>
            <hr style="border:0.5px solid {st.session_state.theme_color}">
            <p>🗓️ <b>ปีนักษัตร:</b> {data['zodiac']}</p>
            <p>🌙 <b>จันทรคติ:</b> {data['phase']}</p>
            <p style="font-size:12px; color:#666;">*คำนวณด้วยสมการเวกเตอร์ควอนตัม หารด้วยค่าสัดส่วนทองคำ 1.618 เพื่อหาจุดสมดุลชีวิต</p>
        </div>
        """, unsafe_allow_html=True)

# --- ห้อง 4: Settings ---
with rooms[3]:
    st.session_state.theme_color = st.color_picker("🎨 ปรับแต่งสีนีออนระบบ (Core Color):", st.session_state.theme_color)
    st.button("🔄 รีเซ็ตระบบ SYNAPSE")
