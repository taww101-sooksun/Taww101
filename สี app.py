import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- CONFIG & UI ---
st.set_page_config(page_title="SYNAPSE v14: DESTINY SCANNER", layout="wide")
st.markdown("<style>.main { background-color: #0b1016; color: #f0f0f0; }</style>", unsafe_allow_html=True)

# --- FUNCTIONS ---
def get_lunar_value(date_obj):
    """คำนวณข้างขึ้นข้างแรมตามหลักการที่พี่บาสกำหนด"""
    # จุดอ้างอิงใหม่เพื่อให้ค่าใกล้เคียงความจริงที่สุด
    ref = date(2024, 1, 11)
    diff = (date_obj - ref).days
    age = diff % 29.53
    
    day_val = date_obj.weekday() + 1 # จันทร์=1 ... อาทิตย์=7
    
    if age < 14.2: # ข้างขึ้น
        moon_num = int(age) + 1
        label = f"ขึ้น {moon_num} ค่ำ"
        op = "บวก" if 1 <= moon_num <= 7 else "คูณ"
    else: # ข้างแรม
        moon_num = int(age - 14.7) + 1
        label = f"แรม {moon_num} ค่ำ"
        op = "ลบ" if 1 <= moon_num <= 7 else "หาร"
            
    return day_val, moon_num, op, label

def calculate_destiny(val, moon_num, op):
    """คำนวณผลลัพธ์ตามสูตร 1-7 (บวก/ลบ) และ 8-15 (คูณ/หาร)"""
    if op == "บวก": return val + moon_num
    if op == "คูณ": return val * moon_num
    if op == "ลบ": return val - moon_num
    if op == "หาร": return val / moon_num if moon_num != 0 else 0
    return 0

# --- SIDEBAR ---
st.sidebar.header("📡 DESTINY COMMAND CENTER")
name_me = st.sidebar.text_input("ชื่อของคุณ", "บาส (Ta101)")
d1 = st.sidebar.date_input(f"วันเกิด {name_me}", value=date(1984, 5, 18), min_value=date(1960, 1, 1))

st.sidebar.divider()
name_target = st.sidebar.text_input("ชื่อเป้าหมาย (แฟนเก่า/แฟนใหม่)", "เป้าหมาย")
d2 = st.sidebar.date_input(f"วันเกิด {name_target}", value=date(1996, 8, 17), min_value=date(1960, 1, 1))

# --- CALCULATION ---
v1, m1, op1, lab1 = get_lunar_value(d1)
res1 = calculate_destiny(v1, m1, op1)

v2, m2, op2, lab2 = get_lunar_value(d2)
res2 = calculate_destiny(v2, m2, op2)

# --- MAIN APP ---
st.title("🛰️ SYNAPSE v14: ULTIMATE DESTINY SCANNER")
st.write(f"วิเคราะห์รหัสชีวิตระหว่าง **{name_me}** และ **{name_target}**")

st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"📊 ข้อมูล {name_me}")
    st.info(f"วันทางสัปดาห์: **{v1}** | {lab1}")
    st.write(f"เงื่อนไขคำนวณ: **{op1}**")
    st.metric("ค่ากำลังดวงหลัก", f"{res1:.2f}")

with col2:
    st.subheader(f"📊 ข้อมูล {name_target}")
    st.warning(f"วันทางสัปดาห์: **{v2}** | {lab2}")
    st.write(f"เงื่อนไขคำนวณ: **{op2}**")
    st.metric("ค่ากำลังเปรียบเทียบ", f"{res2:.2f}")

# --- ผลลัพธ์รวม (Summary Table) ---
st.divider()
st.subheader("🏆 ผลลัพธ์รวม (The Destiny Result)")

t_sum = res1 + res2
t_diff = res1 - res2
t_multi = res1 * res2
t_div = res1 / res2 if res2 != 0 else 0

# แสดงผลแบบตารางที่พี่บาสต้องการ
res_df = pd.DataFrame({
    "สมการ": ["บวก (+)", "ลบ (-)", "คูณ (×)", "หาร (÷)"],
    "ผลลัพธ์สุดท้าย": [f"{t_sum:.2f}", f"{t_diff:.2f}", f"{t_multi:.2f}", f"{t_div:.2f}"]
})
st.table(res_df)

# --- ระบบ SCANNER ตรวจสอบรหัสคู่ขนาน ---
st.divider()
st.subheader("🔮 ระบบตรวจจับรหัสคู่ขนาน (Parallel DNA)")

# คำนวณ GAP ที่พี่บาสค้นเจอ (Gap 4)
gap_value = abs(res1 - res2)
# ตั้งช่วงความคลาดเคลื่อนไว้เล็กน้อย (3.8 - 4.2)
is_parallel = 3.8 <= gap_value <= 4.2

c1, c2 = st.columns([2, 1])

with c1:
    if is_parallel:
        st.error("‼️ ตรวจพบรหัสคู่ขนาน (Parallel Found!)")
        st.write(f"รหัสของ **{name_target}** มีค่าส่วนต่างห่างจากพี่บาส **{gap_value:.2f}** (พิกัด Gap 4)")
        st.write("⚠️ **วิเคราะห์:** คนนี้มีรหัสชีวิตแบบเดียวกับ 'อดีต' ที่พี่เคยเจอมา รูปแบบความสัมพันธ์อาจจะซ้ำรอยเดิม")
        st.balloons()
    else:
        st.success("✅ ไม่พบรหัสคู่ขนาน (Unique Soul Found)")
        st.write(f"ค่าส่วนต่างอยู่ที่ **{gap_value:.2f}** ซึ่งอยู่นอกพิกัดรหัสอดีต")
        st.write("✨ **วิเคราะห์:** คนนี้มีโครงสร้างตัวเลขใหม่ มีแนวโน้มที่จะได้รับประสบการณ์ใหม่ๆ")

with c2:
    st.metric("ค่า GAP ปัจจุบัน", f"{gap_value:.2f}")

st.divider()
st.caption("สโลแกน: 'อยู่นิ่งๆ ไม่เจ็บตัว' | พัฒนาโดย Ta101 (ID: 101/102)")
