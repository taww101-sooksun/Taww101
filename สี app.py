import streamlit as st
import pandas as pd
from datetime import datetime
import itertools

# --- CONFIG & STYLE ---
st.set_page_config(page_title="SYNAPSE COMMAND CENTER v5", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #f63366; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCTIONS ---
def get_lunar_phase(date):
    """ฟังก์ชันคำนวณข้างขึ้นข้างแรมแบบคร่าวๆ (อิงรอบดวงจันทร์ 29.53 วัน)"""
    # วันอ้างอิงที่เป็นคืนเดือนดับ (New Moon)
    reference_date = datetime(2024, 1, 11) 
    diff = (date - reference_date).days
    lunar_age = diff % 29.530588853
    
    if lunar_age < 1: return "🌑 แรม 14-15 ค่ำ (มืดสนิท)"
    elif lunar_age < 7: return "🌙 ขึ้น 1-7 ค่ำ (เสี้ยวสว่าง)"
    elif lunar_age < 15: return "🌕 ขึ้น 8-15 ค่ำ (สว่างเต็มดวง)"
    elif lunar_age < 22: return "🌗 แรม 1-7 ค่ำ (เสี้ยวตัด)"
    else: return "🌘 แรม 8-13 ค่ำ (ใกล้จะมืด)"

def generate_18_gates(digits):
    """สร้างเลข 18 ประตูจากเลข 3 ตัว"""
    if len(digits) != 3: return [], []
    three_digits = [''.join(p) for p in itertools.permutations(digits)]
    two_digits_raw = list(itertools.combinations(digits, 2))
    two_digits = []
    for pair in two_digits_raw:
        two_digits.append(f"{pair[0]}{pair[1]}")
        two_digits.append(f"{pair[1]}{pair[0]}")
    return sorted(list(set(three_digits))), sorted(list(set(two_digits)))

# --- SIDEBAR: INPUT PANEL ---
st.sidebar.title("🛡️ CONTROL PANEL")
st.sidebar.write(f"**User:** Ta101 | ID: {datetime.now().strftime('%Y%m%d')}")

# 1. ส่วนกรอกวันที่
st.sidebar.header("📅 เลือกวันที่วิเคราะห์")
selected_date = st.sidebar.date_input("เลือกวันที่", value=datetime(2026, 4, 16))

# 2. ส่วนกรอกเลขหวย
st.sidebar.header("🔢 ข้อมูลตัวเลข")
lottery_input = st.sidebar.text_input("กรอกเลขที่เก็ง (3 ตัว)", value="785", max_chars=3)

# --- MAIN CONTENT ---
st.title("🛰️ SYNAPSE COMMAND CENTER")
st.write(f"สโลแกน: *'อยู่นิ่งๆ ไม่เจ็บตัว'*")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📊 ข้อมูลวันและจันทรคติ")
    thai_days = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    day_name = thai_days[selected_date.weekday()]
    lunar_status = get_lunar_phase(datetime.combine(selected_date, datetime.min.time()))
    
    # แสดงผลข้อมูลวัน
    st.info(f"📅 **วันที่:** {selected_date.strftime('%d/%m/%Y')}")
    st.info(f"☀️ **วันในสัปดาห์:** วัน{day_name}")
    st.warning(f"🌙 **ข้างขึ้นข้างแรม:** {lunar_status}")

with col2:
    st.markdown("### 🔢 วิเคราะห์ 18 ประตู")
    if lottery_input.isdigit() and len(lottery_input) == 3:
        t3, b2 = generate_18_gates(lottery_input)
        
        st.write("**3 ตัวบน (6 ประตู):**")
        st.success(" | ".join(t3))
        
        st.write("**2 ตัวบน-ล่าง (12 ประตู):**")
        st.success(" | ".join(b2))
    else:
        st.error("กรุณากรอกตัวเลขให้ครบ 3 หลัก")

# --- DATABASE SIMULATION ---
st.divider()
st.markdown("### 📝 บันทึกประวัติการวิเคราะห์")
if st.button("💾 บันทึกข้อมูลลง Command Center"):
    data_log = {
        "วันที่": selected_date,
        "วัน": day_name,
        "ข้างขึ้นข้างแรม": lunar_status,
        "เลขที่เก็ง": lottery_input
    }
    st.table(pd.DataFrame([data_log]))
    st.balloons()
    st.write("บันทึกความจริงเรียบร้อยแล้ว... 'เราไม่หลอกกัน'")

