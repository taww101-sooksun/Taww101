import streamlit as st
from datetime import datetime

# หัวข้อแอปและสไตล์แบบที่คุณชอบ (Dark Mode / Neon)
st.set_page_config(page_title="Cosmic Balance Calculator", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #00ff00; }
    h1 { color: #ff00ff; text-shadow: 2px 2px #000000; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌌 Cosmic Balance & Lunar Calc")
st.subheader("อยู่นิ่งๆ ไม่เจ็บตัว - สูตรสมดุลจักรวาล")

# 1. ส่วนรับข้อมูล (Input)
# ให้ผู้ใช้เลือกแค่วันที่ ส่วนที่เหลือแอปจะคิดให้เอง
selected_date = st.date_input("เลือกวันที่ต้องการคำนวณ", datetime.now())

# 2. Logic การดึงค่าวัน (1-7)
# Monday = 1, Sunday = 7
day_of_week = selected_date.isoweekday()
day_name_th = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"][day_of_week-1]

# 3. ส่วนจำลองการคำนวณข้างขึ้นข้างแรม (Lunar Logic)
# หมายเหตุ: การคำนวณข้างขึ้นข้างแรมไทยให้แม่นยำต้องใช้สมรการดาราศาสตร์
# ในที่นี้คือตัวอย่างการวาง UI ให้คุณนำไปเชื่อมต่อกับสูตรหวยของคุณ
st.write(f"📅 วันที่เลือกตรงกับ: **วัน{day_name_th}** (รหัสจักรวาล: {day_of_week})")

# ช่องให้เลือกข้างขึ้น/แรม (หรือคุณจะใช้ Library คำนวณอัตโนมัติมาเสริมทีหลังได้)
col1, col2 = st.columns(2)
with col1:
    lunar_mode = st.selectbox("ประเภทพลังงาน", ["ข้างแรม (+)", "ข้างขึ้น (-)"])
with col2:
    lunar_step = st.number_input("ค่ำ (1-15)", min_value=1, max_value=15, value=8)

# 4. สูตรคำนวณ "สมดุลจักรวาล" ของคุณ
PHI = 1.618
balance_point = lunar_step - 7.5

if "ข้างขึ้น" in lunar_mode:
    lunar_modifier = -balance_point
else:
    lunar_modifier = balance_point

# สมการหลัก
result = (day_of_week * PHI) + lunar_modifier

# 5. แสดงผลลัพธ์
st.divider()
st.markdown(f"### 🎯 เลขสมดุลจักรวาลวันนี้: **{abs(result):.4f}**")

# เทคนิคดึงเลขไปซื้อหวย
final_num = str(round(abs(result) * 100))
st.info(f"💡 แนวทางเลขจากสมการ: {final_num[:2]} , {final_num[-2:]}")
