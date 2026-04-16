import streamlit as st
from datetime import datetime

# 1. ตั้งค่าหน้าตาแอป (สไตล์อาจารย์ต๊ะ - Neon Dark Mode)
st.set_page_config(page_title="Cosmic Decoder", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #00ff00; }
    h1 { color: #ff00ff; text-shadow: 2px 2px #000000; text-align: center; }
    .stMetric { background-color: #1e2130; border-radius: 10px; padding: 15px; border: 1px solid #00ff00; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌌 Cosmic Logic Decoder")
st.write("<center>อยู่นิ่งๆ ไม่เจ็บตัว - ระบบคำนวณตัวเลขตามสมดุลจักรวาล</center>", unsafe_allow_html=True)
st.write("---")

# 2. ส่วนรับข้อมูล (Input)
col_a, col_b = st.columns(2)
with col_a:
    selected_date = st.date_input("📅 เลือกวันที่ต้องการถอดรหัส", datetime.now())
with col_b:
    lunar_mode = st.selectbox("🌓 ประเภทพลังงาน", ["ข้างแรม (+)", "ข้างขึ้น (-)"])

lunar_step = st.slider("🌙 วันทางจันทรคติ (ค่ำ)", 1, 15, 8)

# 3. ส่วนการคำนวณ (Logic)
PHI = 1.618
day_of_week = selected_date.isoweekday() # จันทร์=1, อาทิตย์=7
day_name_th = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"][day_of_week-1]

# หาจุดสมดุลที่ 7.5
balance_point = lunar_step - 7.5

if "ข้างขึ้น" in lunar_mode:
    lunar_modifier = -balance_point
else:
    lunar_modifier = balance_point

# สมการหลักของอาจารย์ต๊ะ
result = (day_of_week * PHI) + lunar_modifier

# 4. ส่วนแสดงผลลัพธ์ (Output)
st.write("### 🎯 ผลลัพธ์ตัวเลขประจำวัน")
st.metric(label="Cosmic Daily Index", value=f"{abs(result):.4f}")

# 5. ส่วนโชว์ของ (ขั้นตอนการคำนวณ - ใส่ตรงนี้ตามที่ต้องการ)
st.write("---")
with st.expander("📝 เปิดเผยขั้นตอนการคำนวณ (Logic Breakdown)", expanded=True):
    st.markdown("#### การหาค่าตัวเลขนี้อ้างอิงจาก 3 เสาหลักของความสมดุล")
    
    # โชว์สูตรแบบคณิตศาสตร์
    st.latex(r"Numeric_{Result} = (Day \times \Phi) + (Lunar_{Offset})")
    
    st.markdown(f"""
    **ขั้นตอนที่ 1: การกำหนดค่าพื้นฐานของวัน (Day Base)**
    * วันนี้คือวัน: **{day_name_th}** (รหัสลำดับที่ {day_of_week})
    * คำนวณร่วมกับค่าความสมดุลจักรวาล ($\Phi$): {day_of_week} × 1.618 = **{day_of_week * PHI:.3f}**
    
    **ขั้นตอนที่ 2: การปรับค่าความเบี่ยงเบนทางจันทรคติ (Lunar Offset)**
    * สถานะดวงจันทร์: {lunar_mode} {lunar_step} ค่ำ
    * หาจุดสมดุล (Balance Point 7.5): {lunar_step} - 7.5 = {balance_point}
    * ค่าพลังงานที่ส่งผลต่อตัวเลข: **{lunar_modifier}**
    
    **ขั้นตอนที่ 3: สรุปมวลรวมตัวเลข (Final Synthesis)**
    * นำค่าจากขั้นตอนที่ 1 และ 2 มาผสานรวมกัน
    * ({day_of_week} × 1.618) + ({lunar_modifier}) = **{result:.4f}**
    """)

    # ดึงเลขเด่นออกมาโชว์
    raw_num = str(abs(result)).replace('.', '')
    st.success(f"**ตัวเลขเด่นที่ถอดรหัสได้:** {raw_num[1:3]} , {raw_num[2:4]}")

st.info("💡 หมายเหตุ: ข้อมูลนี้เป็นการคำนวณเชิงคณิตศาสตร์เพื่อหาค่าความสมดุลประจำวัน")
