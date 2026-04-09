import streamlit as st
import pandas as pd
from datetime import datetime, date
import itertools

# --- CONFIG & UI ---
st.set_page_config(page_title="SYNAPSE: THE TRUTH REVEALER", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b1016; color: #f0f0f0; }
    .stMetric { background-color: #1a222d; padding: 20px; border-radius: 15px; border: 1px solid #00ff41; box-shadow: 0 0 10px #00ff41; }
    h1, h2, h3 { color: #00ff41; text-shadow: 1px 1px #000; }
    .stAlert { background-color: #1a222d; border: 1px solid #00ff41; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- CORE LOGIC FUNCTIONS ---

def get_complete_data(dt):
    # 1. ข้อมูลจันทรคติ &คณิตศาสตร์ (Logic พี่บาส)
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1 # จันทร์=1, อาทิตย์=7
    
    if pos <= 14.765:
        m_num = int(pos) + 1
        l_label = f"ขึ้น {m_num} ค่ำ"
        op = "บวก (+)" if 1 <= m_num <= 7 else "คูณ (×)"
        op_char = "+" if 1 <= m_num <= 7 else "*"
    else:
        m_num = int(pos - 14.765) + 1
        l_label = f"แรม {m_num} ค่ำ"
        op = "ลบ (-)" if 1 <= m_num <= 7 else "หาร (÷)"
        op_char = "-" if 1 <= m_num <= 7 else "/"
    
    # คำนวณค่าพลังงาน
    if op_char == "+": res = day_val + m_num
    elif op_char == "*": res = day_val * m_num
    elif op_char == "-": res = day_val - m_num
    else: res = day_val / m_num if m_num != 0 else 0

    # 2. ราศี & ธาตุ (แบบไทย)
    d, m = dt.day, dt.month
    if (m == 4 and d >= 13) or (m == 5 and d <= 13): r, t = "เมษ", "ไฟ"
    elif (m == 5 and d >= 14) or (m == 6 and d <= 14): r, t = "พฤษภ", "ดิน"
    elif (m == 6 and d >= 15) or (m == 7 and d <= 15): r, t = "เมถุน", "ลม"
    elif (m == 7 and d >= 16) or (m == 8 and d <= 16): r, t = "กรกฎ", "น้ำ"
    elif (m == 8 and d >= 17) or (m == 9 and d <= 16): r, t = "สิงห์", "ไฟ"
    elif (m == 9 and d >= 17) or (m == 10 and d <= 16): r, t = "กันย์", "ดิน"
    elif (m == 10 and d >= 17) or (m == 11 and d <= 15): r, t = "ตุลย์", "ลม"
    elif (m == 11 and d >= 16) or (m == 12 and d <= 15): r, t = "พิจิก", "น้ำ"
    elif (m == 12 and d >= 16) or (m == 1 and d <= 14): r, t = "ธนู", "ไฟ"
    elif (m == 1 and d >= 15) or (m == 2 and d <= 12): r, t = "มังกร", "ดิน"
    elif (m == 2 and d >= 13) or (m == 3 and d <= 13): r, t = "กุมภ์", "ลม"
    else: r, t = "มีน", "น้ำ"

    # 3. ปีนักษัตร (ไทย)
    y_th = dt.year + 543
    z_list = ["ปีมะเส็ง", "ปีมะเมีย", "ปีมะแม", "ปีวอก", "ปีระกา", "ปีจอ", "ปีกุน", "ปีชวด", "ปีฉลู", "ปีขาล", "ปีเถาะ", "ปีมะโรง"]
    eff_y = y_th - 1 if (m < 4 or (m == 4 and d < 13)) else y_th
    animal = z_list[eff_y % 12]

    return {
        "day_val": day_val, "m_num": m_num, "op": op, "label": l_label, 
        "res": res, "r": r, "t": t, "animal": animal, "formula": f"{day_val} {op_char} {m_num}"
    }

# --- MAIN APP ---
st.title("🛰️ SYNAPSE: THE TRUTH REVEALER")
st.write("ระบบสแกนรหัสชีวิตแบบเปิด (Open Source Input) | ID: Ta101")

st.divider()

# ส่วนที่ให้ทุกคนกรอกเอง (ไม่มี Default ของใครทั้งนั้น)
st.subheader("📝 กรอกข้อมูลเพื่อสแกนความจริง")
c_in1, c_in2 = st.columns(2)

with c_in1:
    st.markdown("### 👤 บุคคลที่ 1")
    name1 = st.text_input("ชื่อ/ฉายา (1)", placeholder="ระบุชื่อ...")
    dob1 = st.date_input("วันเดือนปีเกิด (1)", 
                         value=None, 
                         min_value=date(1960, 1, 1), 
                         max_value=date(2026, 12, 31),
                         help="เลือกปี พ.ศ. ที่ต้องการสแกน")

with c_in2:
    st.markdown("### 👤 บุคคลที่ 2")
    name2 = st.text_input("ชื่อ/ฉายา (2)", placeholder="ระบุชื่อ...")
    dob2 = st.date_input("วันเดือนปีเกิด (2)", 
                         value=None, 
                         min_value=date(1960, 1, 1), 
                         max_value=date(2026, 12, 31),
                         help="เลือกปี พ.ศ. ที่ต้องการสแกน")

# ตรวจสอบว่ากรอกครบหรือยัง
if dob1 and dob2:
    d1 = get_complete_data(dob1)
    d2 = get_complete_data(dob2)

    st.divider()
    
    # แสดงผลลัพธ์แยกรายคน
    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        st.success(f"📌 ผลลัพธ์ของ {name1}")
        st.metric("รหัสพลังงาน", f"{d1['res']:.2f}")
        st.write(f"**ที่มา:** วันที่ {d1['day_val']} ({d1['op']}) กับ {d1['label']}")
        st.write(f"**สมการ:** `{d1['formula']}`")
        st.write(f"**ลักษณะ:** {d1['animal']} | ราศี{d1['r']} | ธาตุ{d1['t']}")

    with res_col2:
        st.warning(f"📌 ผลลัพธ์ของ {name2}")
        st.metric("รหัสพลังงาน", f"{d2['res']:.2f}")
        st.write(f"**ที่มา:** วันที่ {d2['day_val']} ({d2['op']}) กับ {d2['label']}")
        st.write(f"**สมการ:** `{d2['formula']}`")
        st.write(f"**ลักษณะ:** {d2['animal']} | ราศี{d2['r']} | ธาตุ{d2['t']}")

    # สรุปความสัมพันธ์
    st.divider()
    st.subheader("🔍 วิเคราะห์จุดเชื่อมโยง (The Truth Analysis)")
    
    gap = abs(d1['res'] - d2['res'])
    
    col_sum1, col_sum2 = st.columns([2, 1])
    with col_sum1:
        st.write(f"**1. ค่าความต่าง (Gap):** {gap:.2f}")
        if 3.8 <= gap <= 4.2:
            st.error("⚠️ ตรวจพบรหัสคู่ขนาน (Gap 4): โครงสร้างตัวเลขนี้คือรหัสเดียวกับเคสสำคัญในอดีต")
        else:
            st.info("✅ ไม่พบรหัสซ้ำซ้อน: โครงสร้างตัวเลขเป็นชุดใหม่")
            
        st.write(f"**2. การเข้ากันของธาตุ:** ธาตุ{d1['t']} กับ ธาตุ{d2['t']}")
        if d1['t'] == d2['t']: st.write("➡️ ธาตุเดียวกัน: ส่งเสริมกันได้ง่าย")
        else: st.write("➡️ ธาตุต่างชนิด: ต้องปรับตัวตามธรรมชาติของดิน น้ำ ลม ไฟ")

    with col_sum2:
        st.write("**ตารางสรุปเลข**")
        st.write(f"บวก: {d1['res']+d2['res']:.2f}")
        st.write(f"ลบ: {d1['res']-d2['res']:.2f}")
        st.write(f"คูณ: {d1['res']*d2['res']:.2f}")
        st.write(f"หาร: {d1['res']/d2['res'] if d2['res']!=0 else 0:.2f}")

else:
    st.info("💡 กรุณาเลือกวันเกิดของทั้ง 2 ท่านเพื่อเริ่มการสแกนความจริง")

st.divider()
st.caption("สโลแกน: 'อยู่นิ่งๆ ไม่เจ็บตัว' | ทุกตัวเลขมีที่มาและตรวจสอบได้ | พัฒนาโดย Ta101")
