import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import math

# --- CONFIG & NEON STYLE ---
st.set_page_config(page_title="SYNAPSE : GLOBAL SCANNER", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #00e5ff; }
    .stApp { background: radial-gradient(circle, #101a24 0%, #050a0e 100%); }
    .formula-card {
        background: rgba(0, 229, 255, 0.05);
        border: 1px solid #00e5ff;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.2);
    }
    h1, h2, h3 { color: #ffffff; text-transform: uppercase; letter-spacing: 2px; text-shadow: 0 0 10px #00e5ff; }
    code { color: #ff7f50 !important; font-size: 1.1rem; background: #262730; padding: 2px 5px; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- CORE LOGIC (สูตรความจริง) ---
def get_detailed_logic(dt):
    if dt is None: return None
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    
    is_waxing = pos <= 14.765
    m_num = int(pos) + 1 if is_waxing else int(pos - 14.765) + 1
    
    if is_waxing:
        res = math.sqrt((day_val**2) + (m_num**2))
        logic_desc = f"แรงผลักดัน (Vector): √({day_val}² + {m_num}²)"
        phase_text = f"ขึ้น {m_num} ค่ำ"
    else:
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        logic_desc = f"สัดส่วนทองคำ (Golden): ({day_val} × 1.618) / {m_num}"
        phase_text = f"แรม {m_num} ค่ำ"

    return {
        "res": round(res, 4), "phase": phase_text, "day_name": day_names[dt.weekday()],
        "day_val": day_val, "m_num": m_num, "formula": logic_desc
    }

# --- MAIN UI ---
st.title("🛰️ SYNAPSE : ระบบสแกนพิกัดรหัสชีวิต")
st.write("ป้อนวันเดือนปีเกิดเพื่อถอดรหัสความจริงตามหลักคณิตศาสตร์และดาราศาสตร์")

# ส่วนการกรอกข้อมูลแบบอิสระ
col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 ข้อมูลบุคคลที่ 1")
    # ตั้งค่า value=None เพื่อให้ผู้ใช้เลือกเอง
    dob1 = st.date_input("ระบุวันเกิด (1)", value=None, min_value=date(1920,1,1), max_value=date.today(), key="user1")

with col2:
    st.subheader("👤 ข้อมูลบุคคลที่ 2")
    dob2 = st.date_input("ระบุวันเกิด (2)", value=None, min_value=date(1920,1,1), max_value=date.today(), key="user2")

# เริ่มการคำนวณเมื่อมีการกรอกข้อมูลครบ
if dob1 and dob2:
    d1 = get_detailed_logic(dob1)
    d2 = get_detailed_logic(dob2)
    
    # แสดงรายละเอียดที่มาของตัวเลข
    r1, r2 = st.columns(2)
    with r1:
        st.markdown(f"""<div class="formula-card">
            <h3>รหัสประจำตัว: {d1['res']}</h3>
            <p>📍 {d1['day_name']} | {d1['phase']}</p>
            <p>🧬 <b>สูตรคำนวณ:</b> <code>{d1['formula']}</code></p>
        </div>""", unsafe_allow_html=True)
    
    with r2:
        st.markdown(f"""<div class="formula-card">
            <h3>รหัสประจำตัว: {d2['res']}</h3>
            <p>📍 {d2['day_name']} | {d2['phase']}</p>
            <p>🧬 <b>สูตรคำนวณ:</b> <code>{d2['formula']}</code></p>
        </div>""", unsafe_allow_html=True)

    # วิเคราะห์ Gap
    gap = abs(d1['res'] - d2['res'])
    st.divider()
    st.markdown(f"<h2 style='text-align:center;'>ผลการวิเคราะห์ช่องว่าง (GAP): {gap:.4f}</h2>", unsafe_allow_html=True)
    
    if 3.8 <= gap <= 4.2:
        st.markdown("<h1 style='text-align:center; color:#ff007f;'>🌀 รหัสคู่ขนาน (PARALLEL)</h1>", unsafe_allow_html=True)
        st.balloons()
    elif gap < 1.0:
        st.markdown("<h1 style='text-align:center; color:#00ff41;'>💎 รหัสบรรจบ (SYNC)</h1>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='text-align:center; color:#a0a0a0;'>รหัสอยู่ในสถานะอิสระต่อกัน</p>", unsafe_allow_html=True)

else:
    st.warning("⚠️ โปรดระบุวันเกิดของทั้งสองคนเพื่อเริ่มต้นการสแกน")

st.divider()
st.caption(f"สโลแกน: 'อยู่นิ่งๆ ไม่เจ็บตัว' | SYNAPSE ENGINE v3.1")
