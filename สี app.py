import streamlit as st
import streamlit.components.v1 as components
import os
import base64
import math
import time
import pandas as pd
from datetime import datetime, date, timedelta

# ==========================================
# 0. SYSTEM INITIALIZATION & FIREBASE MOCK
# ==========================================
# หมายเหตุ: ตรงนี้ให้คุณเชื่อมต่อ Firebase ของคุณตามที่ตั้งค่าไว้ใน Streamlit Secrets
# import firebase_admin
# from firebase_admin import db...

st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide", initial_sidebar_state="collapsed")

if 'song_index' not in st.session_state: st.session_state.song_index = 0
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#00f2fe"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# ==========================================
# 1. ADVANCED NEON UI SETTINGS (CSS)
# ==========================================
def apply_neon_theme():
    logo_b64 = "" # ใส่ Base64 ของ logo1.png ถ้ามี
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&family=Prompt:wght@300;700&display=swap');
        
        /* ลบ Streamlit Branding ออกทั้งหมด */
        header {{visibility: hidden !important;}}
        footer {{visibility: hidden !important;}}
        #MainMenu {{visibility: hidden !important;}}
        .stDeployButton {{display:none;}}
        
        /* พื้นหลังอวกาศ */
        .stApp {{
            background: radial-gradient(circle at center, #0a0a1a 0%, #000000 100%);
            color: white; font-family: 'Prompt', sans-serif;
        }}
        
        /* นีออนบ็อกซ์ */
        .neon-box {{
            border: 2px solid {st.session_state.theme_color};
            border-radius: 15px; padding: 15px;
            box-shadow: 0 0 15px {st.session_state.theme_color};
            background: rgba(0, 0, 0, 0.6); margin-bottom: 20px;
        }}
        
        /* โโลโก้เต้น Pulse */
        .logo-container {{ display: flex; justify-content: center; margin-bottom: 10px; }}
        .neon-logo {{
            width: 100px; height: 100px; border-radius: 50%;
            border: 2px solid #ff1744;
            animation: pulse-neon 1.5s infinite ease-in-out;
            background: url("data:image/png;base64,{logo_b64}") center/cover;
        }}
        @keyframes pulse-neon {{
            0% {{ transform: scale(1); box-shadow: 0 0 10px #ff1744; }}
            50% {{ transform: scale(1.1); box-shadow: 0 0 25px #00f2fe; }}
            100% {{ transform: scale(1); box-shadow: 0 0 10px #ff1744; }}
        }}

        /* ตัวหนังสือวิ้ง */
        .marquee-container {{
            background: rgba(255,0,0,0.1); border-y: 1px solid #ff1744;
            padding: 5px; overflow: hidden; white-space: nowrap; margin-bottom: 15px;
        }}
        .marquee-text {{
            display: inline-block; animation: scroll-text 15s linear infinite;
            color: #ff1744; font-weight: bold; text-shadow: 0 0 5px #ff1744;
        }}
        @keyframes scroll-text {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. QUANTUM TRUTH ENGINE (สูตรคำนวณ)
# ==========================================
def calculate_quantum_logic(dob):
    # ข้อมูลพื้นฐานดาราศาสตร์ไทย (1960-2026)
    days_th = ["อาทิตย์", "จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์"]
    zodiac_th = ["ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม", "วอก", "ระกา", "จอ", "กุน"]
    
    # 1. คำนวณวัน
    d_idx = (dob.weekday() + 1) % 7
    day_name = days_th[d_idx]
    
    # 2. คำนวณข้างขึ้นข้างแรม (Simplified Lunar)
    ref_new_moon = date(1900, 1, 1) # อ้างอิงเดือนดับ
    days_diff = (dob - ref_new_moon).days
    lunar_pos = days_diff % 29.53059
    if lunar_pos <= 14.765:
        phase_num = int(lunar_pos) + 1
        phase_text = f"ขึ้น {phase_num} ค่ำ"
        lunar_val = phase_num
    else:
        phase_num = int(lunar_pos - 14.765) + 1
        phase_text = f"แรม {phase_num} ค่ำ"
        lunar_val = -phase_num

    # 3. คำนวณปีนักษัตร
    z_idx = (dob.year + 12 - 4) % 12
    zodiac_name = zodiac_th[z_idx]
    z_val = z_idx + 1

    # 4. สมการความจริง (SYNAPSE EQUATION)
    # สูตร: Square Root ของ (วัน * ปี)^2 + (ดวงจันทร์)^2 หารด้วย Golden Ratio
    raw_score = math.sqrt(((d_idx+1) * z_val)**2 + (lunar_val**2))
    final_res = raw_score / 1.618

    return {
        "res": round(final_res, 4), "phase": phase_text, "zodiac": zodiac_name,
        "day": day_name, "d_val": d_idx+1, "z_val": z_val, "l_val": lunar_val
    }

# ==========================================
# 3. MAIN APP INTERFACE
# ==========================================
def main():
    apply_neon_theme()

    # --- Header & Logo ---
    st.markdown('<div class="logo-container"><div class="neon-logo"></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="marquee-container"><div class="marquee-text">⚡ ยินดีต้อนรับสู่ SYNAPSE COMMAND CENTER | ระบบสแกนพิกัดความถี่ชีวิตและสัญญาณ Agent เรียลไทม์ | อยู่นิ่งๆ ไม่เจ็บตัว ⚡</div></div>', unsafe_allow_html=True)

    # --- Navigation Tabs ---
    tabs = st.tabs(["🎵 STATION", "🛰️ RADAR", "🧬 TRUTH", "💬 CHAT", "⚙️ SET"])

    # -------------------
    # TAB 1: MUSIC STATION
    # -------------------
    with tabs[0]:
        music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
        if music_files:
            current_song = music_files[st.session_state.song_index]
            
            # HTML Player & 256 Visualizer
            html_code = f"""
            <div style="border: 2px solid #00f2fe; border-radius: 15px; padding: 10px; background: #000;">
                <video autoplay loop muted style="width:100%; border-radius:10px; object-fit: fill; height: 180px;">
                    <source src="https://www.w3schools.com/html/mov_bbb.mp4" type="video/mp4">
                </video>
                <canvas id="v-canvas" style="width:100%; height:60px; margin-top:5px;"></canvas>
                <audio id="audio-p" autoplay controls src=""></audio>
            </div>
            <script>
                // Logic Visualizer 256 & Auto-next จะถูกรันที่นี่
                // (ในตัวอย่างย่อส่วนเพื่อความรวดเร็ว แต่ระบบจริงจะส่ง Base64 เพลงเข้าไป)
            </script>
            """
            components.html(html_code, height=320)
            
            st.selectbox("📂 เลือกเพลงในคลัง:", music_files, index=st.session_state.song_index)
            c1, c2, c3 = st.columns(3)
            if c1.button("⏮️ BACK"): st.session_state.song_index -= 1; st.rerun()
            if c3.button("NEXT ⏭️"): st.session_state.song_index += 1; st.rerun()

    # -------------------
    # TAB 3: QUANTUM TRUTH (ห้องถอดรหัส)
    # -------------------
    with tabs[2]:
        st.markdown("### 🧬 ห้องถอดรหัสพิกัดชีวิต (1960-2026)")
        user_dob = st.date_input("กรุณาเลือกวันเกิดเพื่อถอดรหัส:", min_value=date(1960,1,1), max_value=date(2026,12,31))
        
        if user_dob:
            data = calculate_quantum_logic(user_dob)
            st.markdown(f"""
            <div class="neon-box">
                <h2 style="color:#00f2fe; text-align:center;">รหัสของคุณ: {data['res']}</h2>
                <hr style="border: 1px solid {st.session_state.theme_color}">
                <p><b>📍 วันที่เกิด:</b> {data['day']} (รหัสพลังงาน: {data['d_val']})</p>
                <p><b>🌙 สถานะดวงจันทร์:</b> {data['phase']} (อิทธิพลของน้ำในตัว: {data['l_val']})</p>
                <p><b>🐉 ปีนักษัตร:</b> {data['zodiac']} (แรงเหวี่ยงรอบปี: {data['z_val']})</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📖 เจาะลึกสูตรการคำนวณ (THE TRUTH)"):
                st.write(f"""
                **ทำไมต้องเป็นตัวเลขเหล่านี้?**
                1. **รหัสวัน ({data['d_val']}):** อ้างอิงจากลำดับดาวในระบบสุริยะที่ส่งผลต่อสนามแม่เหล็กโลกในวันนั้นๆ
                2. **รหัสดวงจันทร์ ({data['l_val']}):** คำนวณจากรอบ Synodic Month 29.53 วัน เพราะข้างขึ้น/แรม มีผลต่อระดับสารเคมีในสมอง
                3. **รหัสปี ({data['z_val']}):** รอบแรงดึงดูดของดาวพฤหัสบดีที่ครบรอบทุก 12 ปี (นักษัตร)
                
                **สมการที่ใช้:** $$Result = \\frac{{\\sqrt{{(Day \\times Year)^2 + (Lunar)^2}}}}{{1.618}}$$
                เราใช้ค่า **1.618 (Golden Ratio)** เพื่อทอนความถี่ให้กลับสู่จุดสมดุลของธรรมชาติ
                """)

    # -------------------
    # TAB 2: RADAR (GPS Real-time)
    # -------------------
    with tabs[1]:
        st.markdown("### 🛰️ แผนที่เรดาร์ดาวเทียม (Hybrid View)")
        # ส่วนนี้ใช้ Folium หรือ Components ในการดึง Google Hybrid
        st.info("📡 ระบบกำลังดึงพิกัดจาก GPS มือถือคุณ... (ความแม่นยำสูง)")
        # โค้ดแผนที่ดาวเทียมจะถูกใส่ที่นี่...

    # -------------------
    # TAB 5: SETTINGS
    # -------------------
    with tabs[4]:
        st.session_state.theme_color = st.color_picker("🎨 ปรับแต่งสีนีออนระบบ:", st.session_state.theme_color)
        if st.button("🚪 LOGOUT"): st.session_state.logged_in = False; st.rerun()

if __name__ == "__main__":
    # หน้า Login (Guard Room)
    if not st.session_state.logged_in:
        apply_neon_theme()
        st.markdown('<div class="logo-container"><div class="neon-logo"></div></div>', unsafe_allow_html=True)
        with st.form("login"):
            st.subheader("🔐 AGENT LOGIN")
            uid = st.text_input("AGENT ID")
            upw = st.text_input("PASSWORD", type="password")
            if st.form_submit_button("UNLOCK"):
                if uid == "Ta101" and upw == "1234": # ตัวอย่าง
                    st.session_state.logged_in = True
                    st.rerun()
    else:
        main()
