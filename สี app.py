import streamlit as st
import os
import pandas as pd
import math
import time
import base64
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from streamlit_autorefresh import st_autorefresh
import hashlib

# --- [ 1. CONFIG หน้าจอ - ห้ามซ้ำ! ] ---
st.set_page_config(page_title="SYNAPSE HUB", layout="wide", initial_sidebar_state="collapsed")

# --- [ 2. ระบบเชื่อมต่อศูนย์บัญชาการ Firebase ] ---
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_credentials"])
        if "private_key" in fb_creds:
            fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {
            'databaseURL': st.secrets["firebase_db_url"]
        })
    except Exception as e:
        st.error(f"❌ ระบบเชื่อมต่อขัดข้อง: {e}")

db_ref = db.reference('/')

# --- [ 3. หัวใจคำนวณ: ระบบถอดรหัส Lunar ] ---
def get_detailed_logic(dt):
    if dt is None: return None
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
        formula, logic_type = f"√({day_val}² + {m_num}²)", "Vector Energy"
    else:
        m_num = int(pos - 14.765) + 1
        phase = f"แรม {m_num} ค่ำ"
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula, logic_type = f"({day_val} × 1.618) / {m_num}", "Golden Ratio"
    return {"res": round(res, 4), "phase": phase, "day_name": day_name, "day_val": day_val, "m_num": m_num, "formula": formula, "type": logic_type}


setup_ui()

# --- 2. การจัดการหน้าจอ (Navigation) ---
if 'page' not in st.session_state:
    st.session_state.page = "HOME"

# ฟังก์ชันย้อนกลับ
if st.session_state.page != "HOME":
    if st.button("⬅️ กลับหน้าหลัก"):
        st.session_state.page = "HOME"
        st.rerun()

# --- 3. เนื้อหาแต่ละหน้า ---

# [ หน้าแรก: ศูนย์รวม 10 แอป ]
if st.session_state.page == "HOME":
    # วาง LOGO แทนที่ติ่ง
    col_l, col_m, col_r = st.columns([1, 4, 1])
    with col_m:
        if os.path.exists("logo1.png"):
            st.image("logo1.png", use_container_width=True)
        else:
            st.markdown("<h1 class='neon-text'>SYNAPSE</h1>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center;'>ศูนย์ควบคุมระบบ: เลือกฟังก์ชันการใช้งาน</h3>", unsafe_allow_html=True)
    st.divider()

    # สร้าง Grid 10 แอป (แบ่งเป็น 2 คอลัมน์)
    c1, c2 = st.columns(2)

    with c1:
        if st.button("🎵 1. MUSIC PLAYER\nฟังเพลง MP3 จากคลังข้อมูล", use_container_width=True):
            st.session_state.page = "1"; st.rerun()
        st.caption("ความสามารถ: เล่นไฟล์เสียง 1.mp3 และระบบควบคุมเสียงผ่านหน้าเว็บ")

        if st.button("🧬 2. PERSONAL CODE\nค้นหาภาพจากดาวเทียม", use_container_width=True):
            st.session_state.page = "3"; st.rerun()
        st.caption("ความสามารถ: ดึงรูปภาพจากคลัง Unsplash ตามคำค้นหาที่ต้องการ")

        if st.button("🔮 3. DESTINY TIMELINE\nสร้างตัวอักษรเรืองแสง", use_container_width=True):
            st.session_state.page = "5"; st.rerun()
        st.caption("ความสามารถ: แปลงข้อความธรรมดาให้เป็นศิลปะนีออนวิ้งๆ")

        if st.button("💖 4. DESTINY CHECK\nตรวจดวงชะตาคู่ขนาน", use_container_width=True):
            st.session_state.page = "7"; st.rerun()
        st.caption("ความสามารถ: วิเคราะห์ดวงชะตาในมิติที่ 4 ผ่านระบบฐานข้อมูลชื่อ")

        if st.button("📝 5. SYSTEM LOG\nบันทึกข้อมูลการใช้งาน", use_container_width=True):
            st.session_state.page = "9"; st.rerun()
        st.caption("ความสามารถ: จดบันทึกข้อความและเหตุการณ์สำคัญลงในหน่วยความจำ")

    with c2:
        if st.button("💬 6. CHAT SYSTEM\nระบบสื่อสารอัจฉริยะ", use_container_width=True):
            st.session_state.page = "2"; st.rerun()
        st.caption("ความสามารถ: โต้ตอบผ่านข้อความกับระบบจัดการ AI")

        if st.button("🛰️ 7. PARALLEL SCANNER\nศูนย์รวมวิดีโอวงจรปิด", use_container_width=True):
            st.session_state.page = "4"; st.rerun()
        st.caption("ความสามารถ: เชื่อมต่อและฉายภาพวิดีโอจาก YouTube หรือ Link ตรง")

        if st.button("⚡ 8. SYNAPSE VIBRATION UNIT\nเวลาโลกแบบเรียลไทม์", use_container_width=True):
            st.session_state.page = "6"; st.rerun()
        st.caption("ความสามารถ: ตรวจสอบเวลาปัจจุบันในโซนต่างๆ ทั่วโลก")

        if st.button("🔢 9. DAILY CODE\nรหัสลับประจำวัน", use_container_width=True):
            st.session_state.page = "8"; st.rerun()
        st.caption("ความสามารถ: เจนรหัสตัวเลขนำโชคและรหัสรักษาความปลอดภัยรายวัน")

        if st.button("🎨 10. COLOR MASTER\nปรับแต่งธีมสีระบบ", use_container_width=True):
            st.session_state.page = "10"; st.rerun()
        st.caption("ความสามารถ: เปลี่ยนสีสันของ Interface เพื่อความสวยงามตามใจชอบ")

# ---     <    #         
        # ---         <
# --- [ ห้อง        </div>
    """, unsafe_allow_html=True)
    
    st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | Synapse Interface Control")


# (เพิ่ม elif ไปจนครบหน้า 10 ตามโครงเดิมได้เลยครับ...)
elif st.session_state.page == "1":
    import base64
    import os

    # 1. ฟังก์ชันดึงโลโก้ (ความจริงคือต้องมีไฟล์ logo1.png ในโฟลเดอร์)
    def get_base64_img(file_path):
        try:
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            return ""
        except: return ""

    logo_b64 = get_base64_img("logo1.png")

    # 2. CSS ปรับแต่งหน้าจอ (ซ่อนติ่ง + โลโก้ดิ้น)
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
        header, footer, #MainMenu {{visibility: hidden;}}
        .stApp {{ background-color: #000000; }}

        .logo-center {{
            display: block;
            margin: 0 auto;
            width: 120px; height: 120px;
            background-image: url("data:image/png;base64,{logo_b64}");
            background-size: contain; background-repeat: no-repeat;
            animation: pulse-ring 2s infinite alternate;
        }}
        @keyframes pulse-ring {{
            from {{ filter: drop-shadow(0 0 5px #00f3ff); transform: scale(1); }}
            to {{ filter: drop-shadow(0 0 20px #ff00de); transform: scale(1.05); }}
        }}
        .neon-text {{
            font-family: 'Orbitron', sans-serif;
            color: #fff; text-align: center;
            text-shadow: 0 0 10px #00f3ff;
            font-size: 1.5rem; margin-top: 10px;
        }}
        </style>
        <div class="logo-center"></div>
        <h1 class="neon-text">SYNAPSE MUSIC DECK</h1>
    """, unsafe_allow_html=True)

    # 3. เครื่องเล่นเพลงระบบ Mixer (HTML5 Canvas + Web Audio API)
    mixer_html = """
    <div style="background: #111; border: 2px solid #333; border-radius: 20px; padding: 20px; font-family: monospace; color: #00f3ff;">
        <canvas id="visualizer" style="width: 100%; height: 100px; background: #000; border-radius: 10px;"></canvas>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px;">
            <div style="border: 1px solid #ff00de; padding: 10px; border-radius: 10px;">
                <small style="color: #ff00de;">DECK A (Primary)</small>
                <input type="file" id="audioA" accept="audio/*" style="width: 100%; font-size: 10px; margin-top: 5px;">
            </div>
            <div style="border: 1px solid #00f3ff; padding: 10px; border-radius: 10px;">
                <small style="color: #00f3ff;">DECK B (Sub)</small>
                <input type="file" id="audioB" accept="audio/*" style="width: 100%; font-size: 10px; margin-top: 5px;">
            </div>
        </div>

        <div style="margin-top: 20px; text-align: center;">
            <button onclick="startMix()" style="width: 100%; padding: 10px; background:
