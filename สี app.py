import streamlit as st
from datetime import datetime

# 1. สไตล์แบบอาจารย์ต๊ะ (Dark Neon)
st.set_page_config(page_title="Cosmic Auto-Decoder", layout="centered")
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #00ff00; }
    h1 { color: #ff00ff; text-shadow: 2px 2px #000000; text-align: center; }
    .stMetric { background-color: #1e2130; border-radius: 10px; padding: 15px; border: 1px solid #00ff00; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌌 Cosmic Auto-Decoder")
st.write("<center>ระบบถอดรหัสวันที่และสมดุลจันทรคติอัตโนมัติ</center>", unsafe_allow_html=True)

# 2. ส่วนรับข้อมูลเพียงอย่างเดียว
selected_date = st.date_input("📅 กรอก วัน/เดือน/ปี ที่ต้องการเช็ค", datetime.now())

# 3. Logic คำนวณอัตโนมัติ
# A. วันในสัปดาห์
day_of_week = selected_date.isoweekday()
day_name_th = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"][day_of_week-1]

# B. ปีนักษัตร (ไทย)
thai_year = selected_date.year + 543
zodiac_list = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
current_zodiac = zodiac_list[thai_year % 12]

# C. คำนวณข้างขึ้นข้างแรมอัตโนมัติ (Approximate Lunar Phase)
def get_lunar_phase(date):
    # อ้างอิงวันที่ 6 ม.ค. 2000 เป็นวันแรม 15 ค่ำ (New Moon)
    reference_date = datetime(2000, 1, 6)
    diff = (date - reference_date.date()).days
    lunar_cycle = 29.530588853
    phase_pos = (diff % lunar_cycle) / lunar_cycle # ค่า 0.0 - 1.0
    
    # แปลงเป็นวันที่ในรอบเดือน (1-29)
    current_pos = phase_pos * 29.53
    
    if current_pos <= 14.76: # ข้างขึ้น
        step = round(current_pos if current_pos >= 1 else 1)
        return "ข้างขึ้น (-)", step, -1
    else: # ข้างแรม
        step = round(current_pos - 14.76 if (current_pos - 14.76) >= 1 else 1)
        return "ข้างแรม (+)", step, 1

lunar_label, lunar_step, lunar_sign = get_lunar_phase(selected_date)

# D. สูตรสมดุลจักรวาล
PHI = 1.618
balance_point = lunar_step - 7.5
lunar_modifier = balance_point * lunar_sign if lunar_sign == 1 else -balance_point
result = (day_of_week * PHI) + lunar_modifier

# 4. แสดงผลโชว์เพื่อน
st.write("---")
st.subheader(f"🔍 วิเคราะห์วันที่: {selected_date.strftime('%d/%m/%Y')}")

col1, col2, col3 = st.columns(3)
col1.metric("วัน", day_name_th)
col2.metric("ปีนักษัตร", current_zodiac)
col3.metric("จันทรคติ", f"{lunar_label} {lunar_step} ค่ำ")

st.write("### 🎯 เลขรหัสจักรวาลที่ได้")
st.metric(label="Cosmic Index", value=f"{abs(result):.4f}")

# 5. โชว์ที่มา (เน้นเช็ควันเกิด/เช็คดวง)
with st.expander("📝 ขั้นตอนการถอดรหัส (สำหรับตรวจสอบ)"):
    st.latex(r"Result = (Day \times 1.618) \pm (Lunar_{Balance})")
    st.markdown(f"""
    **วิเคราะห์ตามหลักการ:**
    1. **ฐานวัน:** วัน{day_name_th} ({day_of_week}) × 1.618 = **{day_of_week * PHI:.3f}**
    2. **แรงดึงดูดดวงจันทร์:** {lunar_label} {lunar_step} ค่ำ (ค่าเบี่ยงเบนจากจุดสมดุล: {lunar_modifier:.2f})
    3. **สรุป:** ค่าความสั่นสะเทือนประจำวันคือ **{result:.4f}**
    """)
    
    raw_num = str(abs(result)).replace('.', '')
    st.success(f"**ตัวเลขเด่นที่ถอดรหัสได้:** {raw_num[1:3]} , {raw_num[2:4]}")

st.info("💡 สามารถใช้เช็คข้อมูลย้อนหลังวันเกิด หรือวันที่สำคัญเพื่อหาค่าพลังงานตัวเลขได้")
