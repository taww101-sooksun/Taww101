import streamlit as st
import pandas as pd
from datetime import datetime, date
import math # เรียกใช้เครื่องมือคณิตศาสตร์ขั้นสูง

# --- CONFIG & UI ---
st.set_page_config(page_title="SYNAPSE QUANTUM", layout="wide")

# UI สไตล์ Hacker / Command Center
st.markdown("""
    <style>
    .main { background-color: #050a0e; color: #00ff41; }
    .stMetric { background-color: #0e161f; border: 2px solid #00ff41; border-radius: 10px; }
    h1, h2, h3 { color: #00ff41; font-family: 'Courier New', Courier, monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- THE QUANTUM CALCULATOR (หัวใจการคำนวณ) ---

def quantum_calculation(dt):
    # 1. ข้อมูลจันทรคติ (พื้นฐานเดิมของพี่บาส)
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    
    # 2. สูตรคำนวณใหม่ (Quantum Mode)
    if pos <= 14.765:
        m_num = int(pos) + 1
        phase_label = f"ขึ้น {m_num} ค่ำ"
        # สูตรข้างขึ้น: ใช้รากที่สองของผลรวมกำลังสอง (Pythagorean logic)
        res = math.sqrt((day_val**2) + (m_num**2))
        formula_text = f"√({day_val}² + {m_num}²)"
    else:
        m_num = int(pos - 14.765) + 1
        phase_label = f"แรม {m_num} ค่ำ"
        # สูตรข้างแรม: ใช้ค่าลอการิทึมหรือการหารสัดส่วนทองคำ (Golden Ratio)
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula_text = f"({day_val} × Φ) / {m_num}"

    # 3. ข้อมูลธาตุและราศี (ความจริงทางสถิติ)
    d, m = dt.day, dt.month
    zodiac_map = [
        (1, 15, "มังกร", "ดิน"), (2, 13, "กุมภ์", "ลม"), (3, 14, "มีน", "น้ำ"),
        (4, 13, "เมษ", "ไฟ"), (5, 14, "พฤษภ", "ดิน"), (6, 15, "เมถุน", "ลม"),
        (7, 16, "กรกฎ", "น้ำ"), (8, 17, "สิงห์", "ไฟ"), (9, 17, "กันย์", "ดิน"),
        (10, 17, "ตุลย์", "ลม"), (11, 16, "พิจิก", "น้ำ"), (12, 16, "ธนู", "ไฟ")
    ]
    r, t = "มีน", "น้ำ"
    for mo, da, name, ele in zodiac_map:
        if m == mo and d >= da: r, t = name, ele

    return {
        "res": round(res, 4), "label": phase_label, 
        "formula": formula_text, "zodiac": r, "element": t, "day": day_val
    }

# --- APP INTERFACE ---
st.title("🛰️ SYNAPSE QUANTUM MATRIX v20")
st.write("เครื่องคำนวณรหัสชีวิตผ่านสมการคณิตศาสตร์และดาราศาสตร์ | ID: Ta101")

st.divider()

# รับค่าจากผู้ใช้ (ไม่มี Default)
c1, c2 = st.columns(2)
with c1:
    name1 = st.text_input("ชื่อผู้สแกน (1)", placeholder="ระบุชื่อ...")
    dob1 = st.date_input("วันเกิด (1)", value=None, min_value=date(1960,1,1), max_value=date(2026,12,31))

with c2:
    name2 = st.text_input("ชื่อผู้สแกน (2)", placeholder="ระบุชื่อ...")
    dob2 = st.date_input("วันเกิด (2)", value=None, min_value=date(1960,1,1), max_value=date(2026,12,31))

if dob1 and dob2:
    res1 = quantum_calculation(dob1)
    res2 = quantum_calculation(dob2)

    st.divider()
    
    # แสดงผลลัพธ์
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader(f"📟 รหัสชีวิต: {name1}")
        st.metric("Quantum Value", res1['res'])
        st.write(f"🧬 **สมการที่ใช้:** `{res1['formula']}`")
        st.write(f"🌒 **สถานะ:** {res1['label']}")
        st.write(f"🔮 **พื้นดวง:** ราศี{res1['zodiac']} (ธาตุ{res1['element']})")

    with col_b:
        st.subheader(f"📟 รหัสชีวิต: {name2}")
        st.metric("Quantum Value", res2['res'])
        st.write(f"🧬 **สมการที่ใช้:** `{res2['formula']}`")
        st.write(f"🌒 **สถานะ:** {res2['label']}")
        st.write(f"🔮 **พื้นดวง:** ราศี{res2['zodiac']} (ธาตุ{res2['element']})")

    st.divider()
    # วิเคราะห์ Gap (ความจริงที่พี่ค้นพบ)
    gap = abs(res1['res'] - res2['res'])
    st.subheader(f"🔍 บทวิเคราะห์รหัสคู่ขนาน (Gap Analysis: {gap:.4f})")
    
    if 3.5 <= gap <= 4.5:
        st.error("‼️ ตรวจพบสัญญาณสะท้อนรหัสคู่ขนาน! (รหัสชีวิตมีการซ้อนทับกันสูง)")
        st.write("โครงสร้างรหัสนี้มักดึงดูดเหตุการณ์หรือความสัมพันธ์ในอดีตให้กลับมาฉายซ้ำ")
    else:
        st.success("✅ รหัสเป็นอิสระต่อกัน: โครงสร้างพลังงานมีความต่างกันอย่างสมดุล")

else:
    st.info("💡 ระบบ Standby... กรุณากรอกวันเกิดทั้ง 2 ฝ่ายเพื่อเริ่มการคำนวณ")

st.divider()
st.caption("สโลแกน: 'อยู่นิ่งๆ ไม่เจ็บตัว' | ระบบคำนวณอัตโนมัติโดย SYNAPSE CORE")
