import streamlit as st
from datetime import datetime

# 1. ตั้งค่าสไตล์แบบอาจารย์ต๊ะ (Dark Mode Neon)
st.set_page_config(page_title="Cosmic Logic Decoder", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #00ff00; }
    h1 { color: #ff00ff; text-shadow: 2px 2px #000000; text-align: center; }
    .stMetric { background-color: #1e2130; border-radius: 10px; padding: 15px; border: 1px solid #00ff00; }
    .stExpander { background-color: #161b22; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌌 Cosmic Logic Decoder")
st.write("<center>อยู่นิ่งๆ ไม่เจ็บตัว - ระบบถอดรหัสสมดุลจักรวาล</center>", unsafe_allow_html=True)
st.write("---")

# 2. ส่วนรับข้อมูล (Input)
col1, col2 = st.columns(2)
with col1:
    selected_date = st.date_input("📅 เลือกวันที่", datetime.now())
with col2:
    lunar_mode = st.selectbox("🌓 พลังงานจันทรคติ", ["ข้างแรม (+)", "ข้างขึ้น (-)"])

lunar_step = st.slider("🌙 วันทางจันทรคติ (ค่ำ)", 1, 15, 8)

# 3. Logic การคำนวณและดึงข้อมูลพื้นฐาน
PHI = 1.618
day_of_week = selected_date.isoweekday() # 1=จันทร์, 7=อาทิตย์
day_name_th = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"][day_of_week-1]

# คำนวณปีนักษัตรไทย (แบบเทียบเคียงปี พ.ศ.)
thai_year = selected_date.year + 543
zodiac_list = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
current_zodiac = zodiac_list[thai_year % 12]

# คำนวณค่าสมดุล
balance_point = lunar_step - 7.5
if "ข้างขึ้น" in lunar_mode:
    lunar_modifier = -balance_point
else:
    lunar_modifier = balance_point

result = (day_of_week * PHI) + lunar_modifier

# 4. ส่วนการแสดงผล (Output)
st.write(f"### 📋 ข้อมูลพื้นฐานประจำวัน")
st.markdown(f"""
- **วันที่คำนวณ:** {selected_date.strftime('%d/%m/%Y')} (วัน{day_name_th})
- **ปีนักษัตร:** {current_zodiac}
- **สถานะ:** {lunar_mode} {lunar_step} ค่ำ
""")

st.write("### 🎯 ผลลัพธ์ตัวเลขประจำวัน")
st.metric(label="Cosmic Daily Index", value=f"{abs(result):.4f}")

# 5. ส่วนโชว์สูตร (The Magic Logic)
st.write("---")
with st.expander("📝 เปิดเผยขั้นตอนการคำนวณ (Logic Breakdown)", expanded=True):
    st.markdown("#### สมการความสมดุล:")
    st.latex(r"Result = (Day \times \Phi) + (Lunar_{Offset})")
    
    st.markdown(f"""
    **ขั้นตอนที่ 1: ฐานพลังงานวัน (Day Base)**
    - วัน{day_name_th} (รหัส {day_of_week}) × 1.618 = **{day_of_week * PHI:.3f}**
    
    **ขั้นตอนที่ 2: ค่าเบี่ยงเบนจันทรคติ (Lunar Offset)**
    - {lunar_mode} {lunar_step} ค่ำ (เทียบจุดสมดุล 7.5)
    - ค่าพลังงานดวงจันทร์: **{lunar_modifier}**
    
    **ขั้นตอนที่ 3: สรุปมวลรวมตัวเลข**
    - ({day_of_week} × 1.618) + ({lunar_modifier}) = **{result:.4f}**
    """)
    
    # สกัดเลขเด่นออกมาโชว์
    raw_num = str(abs(result)).replace('.', '')
    st.success(f"**ตัวเลขเด่นที่ถอดรหัสได้:** {raw_num[1:3]} , {raw_num[2:4]} , {raw_num[-2:]}")

st.info("💡 หมายเหตุ: การคำนวณนี้เป็นเพียงการหาค่าสถิติเชิงคณิตศาสตร์ตามกฎสมดุลจักรวาล")
