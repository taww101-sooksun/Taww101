import streamlit as st
from datetime import datetime, date

# --- CONFIG & UI ---
st.set_page_config(page_title="SYNAPSE v12: DESTINY MATH", layout="wide")
st.markdown("<style>.main { background-color: #0b1016; color: #f0f0f0; }</style>", unsafe_allow_html=True)

# --- FUNCTIONS ---
def get_lunar_value(date_obj):
    """คำนวณข้างขึ้นข้างแรมและแปลงเป็นค่าทางคณิตศาสตร์ตามที่พี่บาสกำหนด"""
    ref = date(2024, 1, 11)
    diff = (date_obj - ref).days
    age = diff % 29.53
    
    day_val = date_obj.weekday() + 1 # จันทร์=1, ..., อาทิตย์=7
    
    if age < 14.2: # ข้างขึ้น
        moon_num = int(age) + 1
        label = f"ขึ้น {moon_num} ค่ำ"
        if 1 <= moon_num <= 7:
            op, res_label = "บวก", "plus"
        else:
            op, res_label = "คูณ", "multiply"
    else: # ข้างแรม
        moon_num = int(age - 14.7) + 1
        label = f"แรม {moon_num} ค่ำ"
        if 1 <= moon_num <= 7:
            op, res_label = "ลบ", "minus"
        else:
            op, res_label = "หาร", "divide"
            
    return day_val, moon_num, op, label

def calculate_destiny(val, moon_num, op):
    """คำนวณผลลัพธ์ของแต่ละข้อมูล"""
    if op == "บวก": return val + moon_num
    if op == "คูณ": return val * moon_num
    if op == "ลบ": return val - moon_num
    if op == "หาร": return val / moon_num if moon_num != 0 else 0
    return 0

# --- SIDEBAR ---
st.sidebar.header("🔢 ป้อนข้อมูลสมการดวง")
d1 = st.sidebar.date_input("ข้อมูลที่ 1 (วันเกิดหลัก)", value=date(1984, 5, 18), min_value=date(1960, 1, 1))
d2 = st.sidebar.date_input("ข้อมูลที่ 2 (วันเกิดเปรียบเทียบ)", value=date(1996, 8, 17), min_value=date(1960, 1, 1))

# --- MAIN APP ---
st.title("🛰️ SYNAPSE v12: DESTINY CALCULATOR")
st.write(f"**ระบบคำนวณ:** วันหลัก {d1} vs วันเปรียบเทียบ {d2}")

# คำนวณข้อมูลชุดที่ 1
v1, m1, op1, lab1 = get_lunar_value(d1)
res1 = calculate_destiny(v1, m1, op1)

# คำนวณข้อมูลชุดที่ 2
v2, m2, op2, lab2 = get_lunar_value(d2)
res2 = calculate_destiny(v2, m2, op2)

st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 ข้อมูลที่ 1")
    st.info(f"วันทางสัปดาห์: **{v1}**")
    st.write(f"สถานะ: **{lab1}** (เงื่อนไข: {op1})")
    st.metric("ค่าสมการที่ 1", f"{res1:.2f}")

with col2:
    st.subheader("📊 ข้อมูลที่ 2")
    st.info(f"วันทางสัปดาห์: **{v2}**")
    st.write(f"สถานะ: **{lab2}** (เงื่อนไข: {op2})")
    st.metric("ค่าสมการที่ 2", f"{res2:.2f}")

# --- ส่วนสรุปผลลัพธ์รวม ---
st.divider()
st.subheader("🏆 ผลลัพธ์รวม (Summary)")

total_sum = res1 + res2
total_diff = res1 - res2
total_multi = res1 * res2
total_div = res1 / res2 if res2 != 0 else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("บวกกัน", f"{total_sum:.2f}")
c2.metric("ลบกัน", f"{total_diff:.2f}")
c3.metric("คูณกัน", f"{total_multi:.2f}")
c4.metric("หารกัน", f"{total_div:.2f}")

st.divider()
st.caption("สูตรคำนวณตามที่พี่บาสกำหนด: 1-7 (บวก/ลบ), 8-15 (คูณ/หาร) | อยู่นิ่งๆ ไม่เจ็บตัว")
