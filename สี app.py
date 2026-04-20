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

# --- [ หัวใจคำนวณ: ระบบถอดรหัส Lunar ] ---
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
# --- ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="SYNAPSE HUB", layout="wide")

if 'primary_color' not in st.session_state:
    st.session_state.primary_color = "#00f3ff"
if 'page' not in st.session_state:
    st.session_state.page = "HOME"

# --- ระบบเชื่อมต่อ Firebase ---
def init_system():
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            if "\\n" in fb_creds["private_key"]:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ Firebase Connect Error: {e}")

init_system()

# --- ฉีดสไตล์ CSS (Global) ---
st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background: #000; color: #fff; }}
    .neon-text {{ color: {st.session_state.primary_color}; text-shadow: 0 0 10px {st.session_state.primary_color}; font-weight: bold; text-align: center; }}
    .stButton>button {{ border: 1px solid {st.session_state.primary_color} !important; border-radius: 15px; background: rgba(0,0,0,0); color: {st.session_state.primary_color}; }}
    </style>
""", unsafe_allow_html=True)
# --- ปุ่มย้อนกลับ (แสดงทุกหน้ายกเว้น Home) ---
if st.session_state.page != "HOME":
    if st.button("⬅️ BACK TO COMMAND CENTER"):
        st.session_state.page = "HOME"
        st.rerun()

# --- หน้าแรก: ศูนย์รวม 10 แอป ---
if st.session_state.page == "HOME":
    st.markdown("<h1 class='neon-text'>SYNAPSE COMMAND CENTER</h1>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎵 1. MUSIC MIXER", use_container_width=True): st.session_state.page = "1"; st.rerun()
        if st.button("🛰️ 2. TACTICAL RADAR", use_container_width=True): st.session_state.page = "2"; st.rerun()
        if st.button("🧬 3. CODE DECODER", use_container_width=True): st.session_state.page = "3"; st.rerun()
    with col2:
        if st.button("🔮 4. DESTINY SCAN", use_container_width=True): st.session_state.page = "4"; st.rerun()
        if st.button("🔊 5. SONIC SENSOR", use_container_width=True): st.session_state.page = "5"; st.rerun()
        if st.button("🎨 10. SYSTEM THEME", use_container_width=True): st.session_state.page = "10"; st.rerun()

# --- หน้า 1: MUSIC MIXER ---
elif st.session_state.page == "1":
    st.subheader("🎵 OMNI-MIXER UNIT")
    # ใส่โค้ด Mixer HTML ที่เจ้านายมีได้เลย
    st.info("ระบบกำลังดึงคลังเพลง...")

# --- หน้า 3: CODE DECODER ---
elif st.session_state.page == "3":
    st.markdown("<h2 class='neon-text'>🧬 PERSONAL CODE</h2>", unsafe_allow_html=True)
    dob = st.date_input("เลือกวันเกิด", value=date.today())
    if dob:
        res = get_detailed_logic(dob)
        st.metric("YOUR REALITY CODE", res['res'])
        st.write(f"ประเภท: {res['type']}")

# --- หน้า 10: THEME MASTER ---
elif st.session_state.page == "10":
    st.subheader("🎨 ADJUST SYSTEM COLOR")
    color = st.color_picker("เลือกสีนีออนหลักของแอป", st.session_state.primary_color)
    if st.button("SAVE COLOR"):
        st.session_state.primary_color = color
        st.rerun()
# --- [ หน้าที่ 3: ระบบสแกนภาพและค้นหาข้อมูล (IMAGE SEARCH) ] ---
elif st.session_state.page == "3":
    st.markdown("<h2 class='neon-text'>📸 SATELLITE & IMAGE SCANNER</h2>", unsafe_allow_html=True)
    query = st.text_input("ระบุรหัสค้นหาภาพ (เช่น Space, Cyberpunk, Forest)", placeholder="SEARCH...")
    if query:
        # ใช้ Unsplash API แบบง่ายในการดึงรูป
        st.image(f"https://source.unsplash.com/featured/?{query}", use_container_width=True, caption=f"DATA FETCHED: {query}")
    st.caption("ระบบดึงภาพจากฐานข้อมูลคลาวด์แบบ Real-time")

# --- [ หน้าที่ 4: ศูนย์รวมวิดีโอ (VIDEO HUB) ] ---
elif st.session_state.page == "4":
    st.markdown("<h2 class='neon-text'>🎬 CCTV & VIDEO COMMAND</h2>", unsafe_allow_html=True)
    v_url = st.text_input("กรอก URL วิดีโอ (YouTube/Direct Link)", value="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    if v_url:
        st.video(v_url)
    st.write("---")
    st.caption("🛰️ เชื่อมต่อสัญญาณถ่ายทอดสดจากเครือข่าย")

# --- [ หน้าที่ 5: บันทึกระบบ (SYSTEM LOG) ] ---
elif st.session_state.page == "5":
    st.markdown("<h2 class='neon-text'>📝 MISSION LOG</h2>", unsafe_allow_html=True)
    # ระบบจดบันทึกเก็บเข้า Firebase หรือ Local
    log_entry = st.text_area("บันทึกเหตุการณ์วันนี้...", height=150)
    if st.button("SAVE TO DATABASE"):
        if log_entry:
            db.reference(f'logs/{st.session_state.user}').push({
                'entry': log_entry,
                'ts': time.time()
            })
            st.success("บันทึกข้อมูลลงฐานข้อมูลลับเรียบร้อย")
    
    # ดึง Log เก่ามาโชว์
    logs = db.reference(f'logs/{st.session_state.user}').limit_to_last(5).get()
    if logs:
        st.write("📂 บันทึกล่าสุด:")
        for lid in reversed(list(logs.keys())):
            st.code(f"[{datetime.fromtimestamp(logs[lid]['ts']).strftime('%Y-%m-%d %H:%M')}] {logs[lid]['entry']}")

# --- [ หน้าที่ 6: เวลาโลก (WORLD CLOCK) ] ---
elif st.session_state.page == "6":
    st.markdown("<h2 class='neon-text'>🌍 GLOBAL CHRONOMETER</h2>", unsafe_allow_html=True)
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.metric("THAILAND (GMT+7)", datetime.now().strftime("%H:%M:%S"))
    with col_t2:
        st.metric("UTC/GMT", datetime.utcnow().strftime("%H:%M:%S"))
    
    # ระบบสแกนเข็มทิศ (Compass Simulation)
    st.markdown("""
        <div style="border: 2px solid #00f3ff; border-radius: 50%; width: 200px; height: 200px; margin: 0 auto; display: flex; align-items: center; justify-content: center;">
            <div style="color:#00f3ff; font-family:Orbitron; animation: spin 4s linear infinite;">N</div>
        </div>
        <style> @keyframes spin { 100% { transform: rotate(360deg); } } </style>
    """, unsafe_allow_html=True)

# --- [ หน้าที่ 7: ตรวจดวงชะตาคู่ขนาน (DESTINY CHECK) ] ---
elif st.session_state.page == "7":
    st.markdown("<h2 class='neon-text'>💖 DESTINY PARALLEL SCANNER</h2>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: dob1 = st.date_input("วันเกิดของคุณ", key="d1")
    with c2: dob2 = st.date_input("วันเกิดคู่กรณี", key="d2")
    
    if st.button("START SCANNING..."):
        r1 = get_detailed_logic(dob1)
        r2 = get_detailed_logic(dob2)
        gap = abs(r1['res'] - r2['res'])
        st.write(f"ผลต่างพิกัด: **{gap:.4f}**")
        if gap < 1.0: st.success("💎 สภาวะ: พิกัดเพชร (บรรจบ/ใกล้ชิด)")
        elif 3.8 <= gap <= 4.2: st.info("🌀 สภาวะ: พิกัดธรรม (สะท้อน/ดึงดูด)")
        else: st.warning("🪞 สภาวะ: พิกัดกระจก (อิสระ/แยกตัว)")

# --- [ หน้าที่ 8: รหัสลับประจำวัน (DAILY CODE) ] ---
elif st.session_state.page == "8":
    st.markdown("<h2 class='neon-text'>🔢 DAILY REALITY CODE</h2>", unsafe_allow_html=True)
    today = date.today()
    d_code = get_detailed_logic(today)
    st.metric("TODAY'S GLOBAL CODE", d_code['res'])
    st.info(f"สมการที่ใช้: {d_code['formula']}")
    st.write(f"ช่วงพลังงาน: {d_code['type']}")

# --- [ หน้าที่ 9: ระบบความปลอดภัย (SECURITY LOG) ] ---
elif st.session_state.page == "9":
    st.markdown("<h2 class='neon-text'>🛡️ ACCESS CONTROL</h2>", unsafe_allow_html=True)
    st.write("ตรวจสอบรายชื่อ Agent ที่ออนไลน์อยู่...")
    try:
        active_agents = db.reference('users').get()
        if active_agents:
            for agent in active_agents.keys():
                st.write(f"🟢 AGENT: {agent} (ONLINE)")
    except:
        st.error("ไม่สามารถดึงข้อมูลสถานะได้")

# --- [ หน้าที่ 10: ปรับแต่งธีมสี (COLOR MASTER) ] ---
elif st.session_state.page == "10":
    st.markdown("<h2 class='neon-text'>🎨 UI CUSTOMIZATION</h2>", unsafe_allow_html=True)
    new_color = st.color_picker("เลือกสีนีออนที่คุณชอบ:", st.session_state.primary_color)
    if st.button("APPLY THEME"):
        st.session_state.primary_color = new_color
        st.success(f"ระบบเปลี่ยนสีเป็น {new_color} เรียบร้อย!")
        st.rerun()
