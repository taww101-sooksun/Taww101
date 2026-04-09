import streamlit as st
import pandas as pd
from datetime import datetime, date
import math

# --- CONFIG & UI ---
st.set_page_config(page_title="SYNAPSE: TRANSPARENT LOGIC", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050a0e; color: #00ff41; }
    .logic-box { 
        background-color: #101a24; 
        padding: 15px; 
        border-left: 5px solid #00ff41; 
        border-radius: 5px;
        margin-bottom: 20px;
        color: #f0f0f0;
    }
    .stMetric { background-color: #0e161f; border: 1px solid #00ff41; }
    h1, h2, h3 { color: #00ff41; }
    </style>
    """, unsafe_allow_html=True)

def get_detailed_logic(dt):
    # 1. ข้อมูลพื้นฐาน
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    day_name = day_names[dt.weekday()]

    # 2. คำนวณตาม Logic
    if pos <= 14.765:
        m_num = int(pos) + 1
        phase = f"ขึ้น {m_num} ค่ำ"
        # สูตร: Pythagorean Theorem (หาแรงผลักดัน)
        res = math.sqrt((day_val**2) + (m_num**2))
        logic_desc = f"ใช้สูตร **'แรงผลักดัน (Vector)'**: นำค่าวันเกิด ({day_val}) และค่าข้างขึ้น ({m_num}) มาหาจุดตัดของพลังงานด้วยทฤษฎีพีทาโกรัส"
        formula = f"√({day_val}² + {m_num}²)"
    else:
        m_num = int(pos - 14.765) + 1
        phase = f"แรม {m_num} ค่ำ"
        # สูตร: Golden Ratio Balance (หาความสมดุล)
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        logic_desc = f"ใช้สูตร **'สัดส่วนทองคำ (Golden Ratio)'**: นำค่าวันเกิด ({day_val}) คูณค่าคงที่จักรวาล (1.618) แล้วปรับสมดุลด้วยค่าข้างแรม ({m_num})"
        formula = f"({day_val} × 1.618) / {m_num}"

    return {
        "res": round(res, 4), "phase": phase, "day_name": day_name,
        "day_val": day_val, "m_num": m_num, "logic_desc": logic_desc, "formula": formula
    }

# --- MAIN INTERFACE ---
st.title("🛰️ SYNAPSE: ระบบสแกนรหัสโปร่งใส")
st.write("ตรวจสอบที่มาของรหัสชีวิตได้ทุกทศนิยม | ความจริงไม่ต้องมีใครโกหก")

st.divider()

# รับข้อมูล
c1, c2 = st.columns(2)
with c1:
    dob1 = st.date_input("เลือกวันเกิดผู้สแกน", value=None, min_value=date(1960,1,1), key="d1")
with c2:
    dob2 = st.date_input("เลือกวันเกิดเป้าหมาย", value=None, min_value=date(1960,1,1), key="d2")

if dob1 and dob2:
    data1 = get_detailed_logic(dob1)
    data2 = get_detailed_logic(dob2)

    # แสดงผลลัพธ์พร้อมคำอธิบายสูตร
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("📟 ข้อมูลชุดที่ 1")
        st.metric("ค่ารหัสที่ได้", data1['res'])
        
        # กล่องอธิบายให้ผู้ใช้เห็นภาพ
        st.markdown(f"""
        <div class="logic-box">
            <b>📍 ที่มาของตัวเลข:</b><br>
            • วันเกิด: {data1['day_name']} (ค่าดัชนี = {data1['day_val']})<br>
            • จันทรคติ: {data1['phase']} (ค่าตัวแปร = {data1['m_num']})<br><br>
            <b>🧬 วิธีคำนวณ:</b><br>
            {data1['logic_desc']}<br>
            <b>สมการ:</b> <code>{data1['formula']}</code>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.subheader("📟 ข้อมูลชุดที่ 2")
        st.metric("ค่ารหัสที่ได้", data2['res'])
        
        st.markdown(f"""
        <div class="logic-box">
            <b>📍 ที่มาของตัวเลข:</b><br>
            • วันเกิด: {data2['day_name']} (ค่าดัชนี = {data2['day_val']})<br>
            • จันทรคติ: {data2['phase']} (ค่าตัวแปร = {data2['m_num']})<br><br>
            <b>🧬 วิธีคำนวณ:</b><br>
            {data2['logic_desc']}<br>
            <b>สมการ:</b> <code>{data2['formula']}</code>
        </div>
        """, unsafe_allow_html=True)

    # --- ส่วนการวิเคราะห์ Gap (แทนที่ของเดิม) ---
st.divider()
gap = abs(res1['res'] - res2['res'])

st.subheader(f"🔍 การวิเคราะห์พิกัดคู่ขนาน (Gap: {gap:.4f})")

# สร้างแถบความต่าง (Progress Bar) เพื่อให้เห็นภาพ
# สมมติว่า Gap สูงสุดที่น่าสนใจคือ 15
progress_val = min(gap / 15.0, 1.0) 
st.progress(progress_val)

if gap < 1.0:
    st.warning("🔮 **ระดับ: รหัสแฝด (Twin Code)**")
    st.write("ค่า Gap ต่ำมาก พลังงานของทั้งคู่แทบจะเป็นชุดเดียวกัน มักมีความคิดหรือการตัดสินใจที่คล้ายกันโดยไม่ได้นัดหมาย")

elif 3.5 <= gap <= 4.5:
    st.error("⚠️ **ระดับ: รหัสคู่ขนาน (Parallel Connection)**")
    st.write("ตรวจพบสัญญาณสะท้อน! พลังงานห่างกันในสัดส่วน 'รหัสเลข 4' ซึ่งอ้างอิงถึงโครงสร้างความสัมพันธ์ที่มีพันธะต่อกันสูง")
    st.balloons()

elif 7.0 <= gap <= 9.0:
    st.info("🌀 **ระดับ: รหัสส่งเสริม (Supporting Code)**")
    st.write("เป็นค่าความต่างที่ช่วยเติมเต็มส่วนที่ขาด พลังงานไม่ทับซ้อนกัน แต่ช่วยผลักดันซึ่งกันและกันได้ดี")

else:
    st.success("✅ **ระดับ: รหัสอิสระ (Independent Energy)**")
    st.write("พลังงานมีความเป็นตัวของตัวเองสูง ไม่มีการดึงดูดหรือขัดแย้งในเชิงโครงสร้างรหัส เป็นความสัมพันธ์ที่เริ่มจากศูนย์ได้ดี")

st.divider()
st.caption("สโลแกน: 'อยู่นิ่งๆ ไม่เจ็บตัว' | คำนวณโดย SYNAPSE CORE v20.1")
