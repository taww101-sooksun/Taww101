import streamlit as st
import os 
import time
import base64
import hashlib
import pandas as pd
import math
from datetime import datetime, date, timedelta

# --- [ ส่วนที่ 1: สูตรคำนวณ "ความจริง" (Step-by-Step) ] ---
def get_step_by_step_data(dt):
    if dt is None: return None
    day_val = {0:1, 1:2, 2:3, 3:4, 4:5, 5:6, 6:7}[dt.weekday()]
    day_name = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"][dt.weekday()]
    date_val = dt.day
    ref = date(1900, 1, 1)
    diff = (dt - ref).days
    lunar_pos = (diff - 0.5) % 29.530589
    if lunar_pos <= 14.765:
        moon_num = int(lunar_pos) + 1
        l_logic = -7.5
        l_type = f"ขึ้น {moon_num} ค่ำ"
    else:
        moon_num = int(lunar_pos - 14.765) + 1
        l_logic = 7.5
        l_type = f"แรม {moon_num} ค่ำ"
    month_val = dt.month
    z_names = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
    z_map = {0:9, 1:10, 2:11, 3:12, 4:1, 5:2, 6:3, 7:4, 8:5, 9:6, 10:7, 11:8}
    zv = z_map[dt.year % 12]
    zn = z_names[dt.year % 12]
    m, d = dt.month, dt.day
    if (m == 5 and d >= 14) or (m == 6 and d <= 14): ev, en = 1, "ดิน"
    elif (m == 7 and d >= 16) or (m == 8 and d <= 16): ev, en = 2, "น้ำ"
    elif (m == 4 and d >= 13) or (m == 5 and d <= 13): ev, en = 4, "ไฟ"
    else: ev, en = 3, "ลม"
    return {
        "day": day_val, "day_n": day_name, "date": date_val, "moon": moon_num, 
        "l_logic": l_logic, "l_type": l_type, "month": month_val, "zv": zv, 
        "zn": zn, "ev": ev, "en": en, "year": dt.year
    }

def get_grade_info(val):
    s_val = str(abs(val)).replace('.', '').lstrip('0')
    digit = int(s_val[0]) if s_val else 0
    if digit in [0, 5]: return digit, "⚖️ สมดุลคงที่ (ค่ากลาง)", "#00f3ff"
    elif 1 <= digit <= 4: return digit, "⚠️ ไม่สู้ดี (ไม่ดีพอ)", "#ff4b4b"
    else: return digit, "🔥 ดีถึงดีมาก (พัฒนาได้)", "#00ff00"

# --- [ ส่วนที่ 2: ตั้งค่าหน้าจอและ UI ] ---
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")

if 'page' not in st.session_state: st.session_state.page = "HOME"
if 'main_color' not in st.session_state: st.session_state.main_color = "#00f3ff"

st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background: #000; border: 1px solid {st.session_state.main_color}; }}
    .neon-text {{ text-align: center; color: #fff; text-shadow: 0 0 10px {st.session_state.main_color}; font-weight: bold; }}
    .logic-box {{ background: rgba(255,255,255,0.05); border: 1px solid {st.session_state.main_color}; padding: 15px; border-radius: 10px; }}
    </style>
""", unsafe_allow_html=True)

# --- [ ระบบเปลี่ยนหน้า (Navigation) ] ---
if st.session_state.page != "HOME":
    if st.button("⬅️ กลับหน้าหลัก"):
        st.session_state.page = "HOME"; st.rerun()

# --- [ หน้าแรก: HUB กลาง ] ---
if st.session_state.page == "HOME":
    st.markdown("<h1 class='neon-text'>SYNAPSE HUB</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎵 1. DJ STATION", use_container_width=True): st.session_state.page = "1"; st.rerun()
        if st.button("🛰️ 2. TACTICAL RADAR", use_container_width=True): st.session_state.page = "2"; st.rerun()
        # ปุ่มเข้าห้องใหม่ที่แยกออกมา
        if st.button("🔢 11. STEP-BY-STEP (วิเคราะห์ความจริง)", use_container_width=True): 
            st.session_state.page = "11"; st.rerun()
            
    with col2:
        if st.button("⚡ 6. SENSOR UNIT", use_container_width=True): st.session_state.page = "6"; st.rerun()
        if st.button("🎨 10. COLOR MASTER", use_container_width=True): st.session_state.page = "10"; st.rerun()

# --- [ ห้องที่ 11: STEP-BY-STEP (แยกมาคนละห้องชัดเจน) ] ---
elif st.session_state.page == "11":
    st.markdown("<h2 class='neon-text'>🔢 SYNAPSE STEP-BY-STEP ANALYZER</h2>", unsafe_allow_html=True)
    
    tab_single, tab_parallel = st.tabs(["👤 วิเคราะห์บุคคล", "👥 วิเคราะห์คู่ขนาน"])

    with tab_single:
        u_birth = st.date_input("กรอกวันเกิดของคุณ", min_value=date(1960,1,1), max_value=date(2026,12,31), key="s_birth")
        if u_birth:
            d = get_step_by_step_data(u_birth)
            # แสดงที่มาของความจริง (ห้ามตัดออก)
            st.markdown("<div class='logic-box'>", unsafe_allow_html=True)
            st.write(f"1. วัน{d['day_n']}: `{d['day']}` | 2. วันที่: `{d['date']}` | 3. {d['l_type']}: `{d['moon']}`")
            st.write(f"4. เดือน: `{d['month']}` | 5. ปี{d['zn']}: `{d['zv']}` | 6. ธาตุ{d['en']}: `{d['ev']}`")
            
            base_sum = d['day'] + d['date'] + d['moon'] + d['month'] + d['zv'] + d['ev']
            raw_code = (base_sum + d['l_logic']) * 1.618
            days_alive = (date.today() - u_birth).days
            final_val = (raw_code + days_alive) / 1.618
            
            digit, grade, color = get_grade_info(final_val)
            st.markdown(f"<h1 style='color:{color}; text-align:center; font-size:60px;'>{round(final_val, 4)}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; color:{color};'>เลขหน้าคือ {digit} : {grade}</p></div>", unsafe_allow_html=True)

    with tab_parallel:
        # (โค้ดวิเคราะห์คู่ขนานของคุณ...)
        st.write("ระบบวิเคราะห์ความถี่ระหว่างบุคคล")

# --- (ห้องอื่นๆ 1, 2, 6, 10 ใส่โค้ดเดิมของคุณต่อได้เลยครับ) ---

st.caption("อ.ย.น. ิ. ้.ง ๆ .ไ.ม.่.เ.จ.็.บ.ต.ั.ว | Synapse Unit 11 แยกส่วนชัดเจน")
