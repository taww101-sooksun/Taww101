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
import hashlib
import random

# --- [ 1. CONFIG หน้าจอ - ห้ามซ้ำ! ] ---
st.set_page_config(page_title="SYNAPSE HUB", layout="wide", initial_sidebar_state="collapsed")

# --- [ 2. ระบบเชื่อมต่อศูนย์บัญชาการ Firebase ] ---
if not firebase_admin._apps:
    try:
        if "firebase_credentials" in st.secrets:
            fb_creds = dict(st.secrets["firebase_credentials"])
            if "private_key" in fb_creds:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets.get("firebase_db_url", "")
            })
    except Exception as e:
        pass # ปิด Error ไว้เพื่อไม่ให้กวนใจเวลาเทสระบบออฟไลน์

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

# --- [ 4. ตั้งค่า UI (CSS สไตล์ Neon) ] ---
def setup_ui():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
        .neon-text {
            font-family: 'Orbitron', sans-serif; color: #fff; text-align: center;
            text-shadow: 0 0 10px #00f3ff, 0 0 20px #00f3ff; font-size: 2.5rem; margin-top: 10px;
        }
        .neon-sub { color: #ff00de; text-align: center; text-shadow: 0 0 5px #ff00de; }
    </style>
    """, unsafe_allow_html=True)

setup_ui()

# --- [ 5. การจัดการหน้าจอ (Navigation) ] ---
if 'page' not in st.session_state:
    st.session_state.page = "HOME"

# ปุ่มย้อนกลับ (แสดงทุกหน้ายกเว้นหน้าแรก)
if st.session_state.page != "HOME":
    if st.button("⬅️ กลับศูนย์บัญชาการ (HOME)"):
        st.session_state.page = "HOME"
        st.rerun()
    st.divider()

# ==========================================
# 🚀 เนื้อหาแต่ละหน้า (PAGES)
# ==========================================

if st.session_state.page == "HOME":
    st.markdown("<h1 class='neon-text'>SYNAPSE HUB</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='neon-sub'>ศูนย์ควบคุมระบบ: เลือกฟังก์ชันการใช้งาน</h3>", unsafe_allow_html=True)
    st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | Synapse Interface Control")
    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🎵 1. MUSIC PLAYER\nระบบควบคุมเสียง", use_container_width=True): st.session_state.page = "1"; st.rerun()
        if st.button("🧬 2. PERSONAL CODE\nค้นหาภาพและข้อมูล", use_container_width=True): st.session_state.page = "2"; st.rerun()
        if st.button("🔮 3. DESTINY TIMELINE\nข้อความเรืองแสง", use_container_width=True): st.session_state.page = "3"; st.rerun()
        if st.button("💖 4. DESTINY CHECK\nตรวจชะตาคู่ขนาน", use_container_width=True): st.session_state.page = "4"; st.rerun()
        if st.button("📝 5. SYSTEM LOG\nบันทึกข้อมูล", use_container_width=True): st.session_state.page = "5"; st.rerun()
    with c2:
        if st.button("💬 6. CHAT SYSTEM\nระบบสื่อสาร AI", use_container_width=True): st.session_state.page = "6"; st.rerun()
        if st.button("🛰️ 7. PARALLEL SCANNER\nวิดีโอ & สแกนเนอร์", use_container_width=True): st.session_state.page = "7"; st.rerun()
        if st.button("⚡ 8. SYNAPSE VIBRATION\nเวลาโลกเรียลไทม์", use_container_width=True): st.session_state.page = "8"; st.rerun()
        if st.button("🔢 9. DAILY CODE\nรหัสลับประจำวัน", use_container_width=True): st.session_state.page = "9"; st.rerun()
        if st.button("🎨 10. COLOR MASTER\nปรับแต่งธีม", use_container_width=True): st.session_state.page = "10"; st.rerun()

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


# --- PAGE 2: PERSONAL CODE (Image Search) ---
elif st.session_state.page == "2":
    st.markdown("<h2 class='neon-text'>🧬 PERSONAL CODE</h2>", unsafe_allow_html=True)
    st.write("ระบบดึงภาพจำลองจากฐานข้อมูล (พิมพ์คำค้นหาเป็นภาษาอังกฤษ)")
    search_query = st.text_input("ค้นหาภาพ (เช่น space, cyber, neon):", "cyberpunk")
    if st.button("สแกนภาพ"):
        st.image(f"https://source.unsplash.com/800x400/?{search_query}", caption=f"ผลลัพธ์ภาพสำหรับ: {search_query}")

# --- PAGE 3: DESTINY TIMELINE (Neon Text Generator) ---
elif st.session_state.page == "3":
    st.markdown("<h2 class='neon-text'>🔮 DESTINY TIMELINE</h2>", unsafe_allow_html=True)
    user_text = st.text_input("พิมพ์ข้อความของคุณที่นี่:", "SYNAPSE")
    color = st.color_picker("เลือกสีนีออน:", "#00f3ff")
    if user_text:
        st.markdown(f"""
        <div style="text-align: center; margin-top: 50px; padding: 50px; background-color: #111; border-radius: 20px;">
            <h1 style="font-family: 'Orbitron', sans-serif; color: #fff; text-shadow: 0 0 10px {color}, 0 0 40px {color}; font-size: 4rem;">
                {user_text}
            </h1>
        </div>
        """, unsafe_allow_html=True)

# --- PAGE 4: DESTINY CHECK (ดวงชะตา & Lunar Logic) ---
elif st.session_state.page == "4":
    st.markdown("<h2 class='neon-text'>💖 DESTINY CHECK</h2>", unsafe_allow_html=True)
    bdate = st.date_input("เลือกวันเกิดของคุณ:")
    if st.button("ประมวลผลดวงชะตา"):
        res = get_detailed_logic(bdate)
        st.success(f"พลังงานหลักของคุณคือ: **{res['type']}**")
        st.info(f"วัน{res['day_name']} | ดวงจันทร์: {res['phase']}")
        st.write(f"ค่าพลังงานสัมบูรณ์: `{res['res']}` (อ้างอิงสูตร: {res['formula']})")

# --- PAGE 5: SYSTEM LOG (บันทึกข้อมูล) ---
elif st.session_state.page == "5":
    st.markdown("<h2 class='neon-text'>📝 SYSTEM LOG</h2>", unsafe_allow_html=True)
    if 'logs' not in st.session_state: st.session_state.logs = []
    
    new_log = st.text_input("บันทึกเหตุการณ์ใหม่:")
    if st.button("SAVE LOG"):
        if new_log:
            st.session_state.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {new_log}")
            st.success("บันทึกสำเร็จ!")
            
    st.write("--- ประวัติการบันทึก ---")
    for log in reversed(st.session_state.logs):
        st.code(log)

# --- PAGE 6: CHAT SYSTEM ---
elif st.session_state.page == "6":
    st.markdown("<h2 class='neon-text'>💬 SYNAPSE AI CHAT</h2>", unsafe_allow_html=True)
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "สวัสดี! ระบบ SYNAPSE พร้อมรับคำสั่ง"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["content"])

    if prompt := st.chat_input("ป้อนข้อความ..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.write(prompt)
        # Mock AI Response
        reply = f"ระบบได้รับข้อความ: '{prompt}' (นี่คือข้อความตอบกลับอัตโนมัติ)"
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"): st.write(reply)

# --- PAGE 7: PARALLEL SCANNER (Video) ---
elif st.session_state.page == "7":
    st.markdown("<h2 class='neon-text'>🛰️ PARALLEL SCANNER</h2>", unsafe_allow_html=True)
    st.write("เชื่อมต่อสัญญาณวิดีโอ (ใส่ลิงก์ YouTube หรือไฟล์ MP4)")
    vid_url = st.text_input("Video URL:", "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    if vid_url:
        try:
            st.video(vid_url)
        except:
            st.error("ลิงก์ไม่รองรับ หรือเกิดข้อผิดพลาดในการโหลด")

# --- PAGE 8: SYNAPSE VIBRATION (World Time) ---
elif st.session_state.page == "8":
    st.markdown("<h2 class='neon-text'>⚡ SYNAPSE VIBRATION</h2>", unsafe_allow_html=True)
    import pytz
    
    col1, col2, col3 = st.columns(3)
    zones = [("🇹🇭 BKK", "Asia/Bangkok"), ("🇯🇵 TYO", "Asia/Tokyo"), ("🇬🇧 LON", "Europe/London")]
    for col, (label, tz_str) in zip([col1, col2, col3], zones):
        with col:
            tz = pytz.timezone(tz_str)
            tz_time = datetime.now(tz)
            st.metric(label=label, value=tz_time.strftime("%H:%M:%S"), delta=tz_time.strftime("%Y-%m-%d"))

# --- PAGE 9: DAILY CODE ---
elif st.session_state.page == "9":
    st.markdown("<h2 class='neon-text'>🔢 DAILY SECRETS CODE</h2>", unsafe_allow_html=True)
    today_str = datetime.now().strftime("%Y-%m-%d")
    hash_code = hashlib.md5(today_str.encode()).hexdigest()[:8].upper()
    
    st.info(f"วันที่อ้างอิง: {today_str}")
    st.markdown(f"""
        <div style='text-align: center; border: 2px dashed #ff00de; padding: 20px; border-radius: 10px;'>
            <h3>รหัสผ่านเซิร์ฟเวอร์ประจำวัน</h3>
            <h1 style='color: #00f3ff; font-family: monospace;'>{hash_code}</h1>
        </div>
    """, unsafe_allow_html=True)

# --- PAGE 10: COLOR MASTER ---
elif st.session_state.page == "10":
    st.markdown("<h2 class='neon-text'>🎨 COLOR MASTER</h2>", unsafe_allow_html=True)
    st.write("ระบบนี้กำลังอยู่ในช่วงพัฒนา... (เร็วๆ นี้คุณจะสามารถเปลี่ยนสีพื้นหลังได้ทั้งแอป)")
    
    bg_color = st.color_picker("จำลองเลือกสีพื้นหลัง", "#000000")
    if bg_color != "#000000":
        st.markdown(f"""
        <style>
            .stApp {{ background-color: {bg_color}; }}
        </style>
        """, unsafe_allow_html=True)
        st.success("เปลี่ยนสีพื้นหลังชั่วคราวสำเร็จ!")
