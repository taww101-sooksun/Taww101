import streamlit as st
import os 
import time
import base64
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from folium.features import DivIcon
from streamlit_folium import st_folium
from math import radians, cos, sin, asin, sqrt
import pytz
from timezonefinder import TimezoneFinder
from datetime import datetime, date, timedelta
import math
import random
import hashlib
import pandas as pd
from streamlit_js_eval import get_geolocation 

# =================================================================
# 1. SETUP & CONFIG (ต้องอยู่บนสุด)
# =================================================================
st.set_page_config(page_title="SYNAPSE ULTIMATE", layout="wide")

# ระบบจัดการสถานะ (State)
if 'main_color' not in st.session_state: st.session_state.main_color = "#00f3ff"
if 'sub_color' not in st.session_state: st.session_state.sub_color = "#ff00de"
if 'page' not in st.session_state: st.session_state.page = "HOME"
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# =================================================================
# 2. GLOBAL CSS (ลบติ่ง + เชื่อมสีทุกห้อง)
# =================================================================
st.markdown(f"""
    <style>
    /* ลบ Header/Footer Streamlit */
    header, footer, #MainMenu {{visibility: hidden !important; height: 0px !important;}}
    .stDeployButton {{display: none !important;}}
    
    :root {{
        --primary: {st.session_state.main_color};
        --secondary: {st.session_state.sub_color};
    }}

    .stApp {{
        background-color: #000 !important;
        border: 2px solid var(--primary);
    }}

    /* ปุ่มทุกปุ่มในระบบ */
    .stButton>button {{
        border: 1px solid var(--primary) !important;
        background: rgba(0,0,0,0.5) !important;
        color: white !important;
        box-shadow: 0 0 10px var(--primary);
        border-radius: 12px !important;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        border-color: var(--secondary) !important;
        box-shadow: 0 0 20px var(--secondary) !important;
    }}

    .neon-text {{
        color: var(--primary) !important;
        text-shadow: 0 0 10px var(--primary), 0 0 20px var(--secondary) !important;
        text-align: center; font-weight: bold;
    }}
    </style>
""", unsafe_allow_html=True)

# =================================================================
# 3. HELPER FUNCTIONS
# =================================================================
def get_base64_data(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

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

# =================================================================
# 4. LOGIN SYSTEM
# =================================================================
if not st.session_state.logged_in:
    st.markdown("<h2 class='neon-text'>REGISTER AGENT</h2>", unsafe_allow_html=True)
    new_user = st.text_input("รหัส AGENT:", placeholder="เช่น ต๊ะ101").strip()
    if st.button("ACTIVATE SYSTEM", use_container_width=True):
        if new_user:
            st.session_state.user = new_user
            st.session_state.logged_in = True
            st.rerun()
    st.stop()

# =================================================================
# 5. NAVIGATION & PAGES
# =================================================================

# --- ปุ่มย้อนกลับ (แสดงทุกหน้ายกเว้น HOME) ---
if st.session_state.page != "HOME":
    if st.button("⬅️ BACK TO MAIN"):
        st.session_state.page = "HOME"
        st.rerun()

# --- [ หน้าแรก: 4 ปุ่มหลัก ] ---
if st.session_state.page == "HOME":
    st.markdown("<h1 class='neon-text'>SYNAPSE HUB</h1>", unsafe_allow_html=True)
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎵 1. DJ STATION (MUSIC)", use_container_width=True): st.session_state.page = "1"; st.rerun()
        if st.button("💬 2. CHAT & RADAR", use_container_width=True): st.session_state.page = "2"; st.rerun()
    with col2:
        if st.button("🧠 3. INTELLIGENCE (LUNAR/LOGS)", use_container_width=True): st.session_state.page = "3"; st.rerun()
        if st.button("🎨 4. COLOR MASTER", use_container_width=True): st.session_state.page = "10"; st.rerun()

# --- [ หน้า 1: DJ STATION ] ---
elif st.session_state.page == "1":
    st.markdown("<h2 class='neon-text'>🎧 DJ STATION</h2>", unsafe_allow_html=True)
    st.write("ระบบเล่นเพลง Deck A/B พร้อม Visualizer")
    # (โค้ดเพลงที่คุณต๊ะมีอยู่แล้ว)

# --- [ หน้า 2: CHAT & RADAR ] ---
elif st.session_state.page == "2":
    st.markdown("<h2 class='neon-text'>🛰️ TACTICAL UNIT</h2>", unsafe_allow_html=True)
    # (โค้ดแผนที่และแชตที่คุณต๊ะมีอยู่แล้ว)

# --- [ หน้า 3: INTELLIGENCE CENTER (รวม 3-9) ] ---
# --- [ ห้องรวมมิติ: SYNAPSE INTELLIGENCE CENTER (ยุบรวม 3-9) ] ---
elif st.session_state.page == "3":
    # ส่วนหัวและปุ่มย้อนกลับ
    col_h1, col_h2 = st.columns([4, 1])
    with col_h1:
        st.markdown("<h2 class='neon-text'>🧠 INTELLIGENCE CENTER</h2>", unsafe_allow_html=True)
    with col_h2:
        if st.button("⬅️ HOME", use_container_width=True):
            st.session_state.page = "HOME"
            st.rerun()

    # สร้าง Tabs เพื่อแยกรายละเอียดงาน
    tab_lunar, tab_destiny, tab_sensor, tab_code, tab_log = st.tabs([
        "🌙 LUNAR & GAP", 
        "🔮 DESTINY SCAN", 
        "📡 BIO-SENSORS", 
        "🔢 DAILY PIN", 
        "📝 SYSTEM LOG"
    ])

    # --- 1. รายละเอียด LUNAR & GAP (เดิมคือ 3, 4) ---
    with tab_lunar:
        st.markdown("### 🌙 การถอดรหัสพิกัดดวงดาว")
        st.write("วิเคราะห์รหัสประจำตัวจากฐานวันเกิดและจันทรคติ (Lunar Cycle)")
        
        c1, c2 = st.columns(2)
        with c1:
            d1_input = st.date_input("วันเกิด AGENT 1", value=date(1995,1,1), key="ic_d1")
        with c2:
            d2_input = st.date_input("วันเกิด AGENT 2 (เปรียบเทียบ)", value=date(1995,1,1), key="ic_d2")
        
        if d1_input:
            res1 = get_detailed_logic(d1_input)
            res2 = get_detailed_logic(d2_input)
            gap = abs(res1['res'] - res2['res'])
            
            st.markdown(f"""
                <div style="background:rgba(0,243,255,0.1); border:1px solid var(--primary); padding:20px; border-radius:15px;">
                    <h3 style="color:var(--primary);">RESULT: {res1['res']}</h3>
                    <p><b>พิกัด:</b> วัน{res1['day_name']} | {res1['phase']}</p>
                    <p><b>ลอจิกที่ใช้:</b> {res1['type']} ({res1['formula']})</p>
                    <hr style="border-color:var(--primary);">
                    <h4 style="color:var(--secondary);">GAP ANALYZER: {gap:.4f}</h4>
                    <small>*ค่า Gap คือความต่างของคลื่นความถี่ระหว่างบุคคล*</small>
                </div>
            """, unsafe_allow_html=True)

    # --- 2. รายละเอียด DESTINY SCAN (เดิมคือ 5, 7) ---
    with tab_destiny:
        st.markdown("### 🔮 สแกนชะตาและไทม์ไลน์")
        mode = st.radio("เลือกฟังก์ชัน:", ["ไทม์ไลน์ 180 วัน (เพชร/ธรรม/กระจก)", "สแกนชื่อคู่ขนาน"], horizontal=True)
        
        if mode == "ไทม์ไลน์ 180 วัน (เพชร/ธรรม/กระจก)":
            st.write("ระบบจะสแกนหา 'วันบรรจบ' ที่รหัสของคุณตรงกับรหัสจักรวาล")
            # ลอจิกสแกน 180 วัน
            my_code = get_detailed_logic(d1_input)['res']
            future_data = []
            for i in range(180):
                t_date = date.today() + timedelta(days=i)
                t_res = get_detailed_logic(t_date)
                t_gap = abs(t_res['res'] - my_code)
                
                status = ""
                if t_gap < 0.5: status = "💎 พิกัดเพชร (โอกาสใหญ่)"
                elif 3.8 <= t_gap <= 4.2: status = "🌀 พิกัดธรรม (ดึงดูด)"
                elif t_gap > 10.0: status = "🪞 พิกัดกระจก (อิสระ)"
                
                if status:
                    future_data.append({"วันที่": t_date, "วัน": t_res['day_name'], "พิกัด": status, "Gap": round(t_gap, 4)})
            
            if future_data:
                st.table(future_data)
            else:
                st.info("ไม่พบพิกัดพิเศษในช่วงนี้")

        else:
            st.write("วิเคราะห์ความเข้ากันได้จากค่า Unicode ของชื่อ")
            n1 = st.text_input("ชื่อ AGENT 1", key="ic_n1")
            n2 = st.text_input("ชื่อ AGENT 2", key="ic_n2")
            if n1 and n2:
                s1, s2 = sum(ord(c) for c in n1), sum(ord(c) for c in n2)
                sync = 100 - (abs(s1 - s2) % 100)
                st.metric("SYNC LEVEL", f"{sync}%")

    # --- 3. รายละเอียด BIO-SENSORS (เดิมคือ 6) ---
    with tab_sensor:
        st.markdown("### 📡 ระบบตรวจจับสัญญาณกายภาพ")
        st.write("เชื่อมต่อเซนเซอร์จากอุปกรณ์เพื่อดึงค่าจริง (Vibration & Bio-data)")
        
        # ใส่ Component สำหรับวัดเสียง/แรงสั่น (ใช้โค้ดเดิมที่คุณต๊ะมีได้เลย)
        st.warning("⚠️ โปรดอนุญาตการเข้าถึงเซนเซอร์บนอุปกรณ์ของคุณ")
        c_v1, c_v2 = st.columns(2)
        c_v1.metric("VIBRATION", "1.002 G", "Normal")
        c_v2.metric("SOUND LEVEL", "45 dB", "-2%")

    # --- 4. รายละเอียด DAILY PIN (เดิมคือ 8) ---
    with tab_code:
        st.markdown("### 🔢 รหัสรักษาความปลอดภัยรายวัน")
        st.write("รหัสผ่านที่เจนเนอเรทจาก วันที่ + ชื่อ AGENT + SHA-256")
        
        u_name = st.session_state.get('user', 'GUEST')
        raw = f"{date.today()}_{u_name}_SYNAPSE"
        h = hashlib.sha256(raw.encode()).hexdigest()
        
        st.markdown(f"""
            <div style="text-align:center; padding:30px; background:black; border:2px dashed var(--primary); border-radius:20px;">
                <h1 style="letter-spacing: 10px; color:white;">{h[:6].upper()}</h1>
                <p style="color:var(--primary);">รหัสลับของคุณประจำวันนี้</p>
            </div>
        """, unsafe_allow_html=True)

    # --- 5. รายละเอียด SYSTEM LOG (เดิมคือ 9) ---
    with tab_log:
        st.markdown("### 📝 บันทึกความจำระบบ (Memory Log)")
        with st.form("ic_log", clear_on_submit=True):
            note = st.text_area("บันทึกเหตุการณ์วันนี้:")
            if st.form_submit_button("COMMIT TO FIREBASE"):
                if note:
                    db.reference(f'system_logs/{st.session_state.user}').push({
                        'text': note, 'ts': time.time(), 'dt': str(datetime.now())
                    })
                    st.success("บันทึกลงฐานข้อมูลแล้ว")
        
        # แสดงประวัติ 3 รายการล่าสุด
        st.write("---")
        logs = db.reference(f'system_logs/{st.session_state.user}').limit_to_last(3).get()
        if logs:
            for k, v in reversed(logs.items()):
                st.caption(f"📅 {v['dt']}")
                st.info(v['text'])


# --- [ หน้า 10: COLOR MASTER ] ---
elif st.session_state.page == "10":
    st.markdown("<h2 class='neon-text'>🎨 COLOR MASTER</h2>", unsafe_allow_html=True)
    st.session_state.main_color = st.color_picker("สีหลักระบบ", st.session_state.main_color)
    st.session_state.sub_color = st.color_picker("สีรองระบบ", st.session_state.sub_color)
    if st.button("🔥 UPDATE ALL DIMENSIONS", use_container_width=True):
        st.rerun()
