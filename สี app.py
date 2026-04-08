import streamlit as st
import pandas as pd
from datetime import datetime
import itertools

# --- CONFIG ---
st.set_page_config(page_title="SYNAPSE: PERSONAL FORTUNE & STATS", layout="wide")
st.markdown("<style>.main { background-color: #0b1016; color: #f0f0f0; }</style>", unsafe_allow_html=True)

# --- DATA DICTIONARY (โหราศาสตร์) ---
ELEMENTS = {
    "ไฟ": "🔥 กระตือรือร้น ใจร้อน กล้าหาญ (เหมาะกับเลข 3, 7, 8)",
    "ดิน": "🌍 มั่นคง อดทน ละเอียด (เหมาะกับเลข 2, 5, 0)",
    "ลม": "💨 ปราดเปรียว รวดเร็ว ชอบอิสระ (เหมาะกับเลข 4, 6)",
    "น้ำ": "💧 อ่อนโยน ปรับตัวเก่ง มีเสน่ห์ (เหมาะกับเลข 1, 9)"
}

# --- FUNCTIONS ---
def get_horoscope_details(date):
    day = date.day
    month = date.month
    year_th = date.year + 543
    
    # 1. ราศี & ธาตุ
    if (month == 4 and day >= 13) or (month == 5 and day <= 13): r, t = "เมษ", "ไฟ"
    elif (month == 5 and day >= 14) or (month == 6 and day <= 14): r, t = "พฤษภ", "ดิน"
    elif (month == 6 and day >= 15) or (month == 7 and day <= 15): r, t = "เมถุน", "ลม"
    elif (month == 7 and day >= 16) or (month == 8 and day <= 16): r, t = "กรกฎ", "น้ำ"
    elif (month == 8 and day >= 17) or (month == 9 and day <= 16): r, t = "สิงห์", "ไฟ"
    elif (month == 9 and day >= 17) or (month == 10 and day <= 16): r, t = "กันย์", "ดิน"
    elif (month == 10 and day >= 17) or (month == 11 and day <= 15): r, t = "ตุลย์", "ลม"
    elif (month == 11 and day >= 16) or (month == 12 and day <= 15): r, t = "พิจิก", "น้ำ"
    elif (month == 12 and day >= 16) or (month == 1 and day <= 14): r, t = "ธนู", "ไฟ"
    elif (month == 1 and day >= 15) or (month == 2 and day <= 12): r, t = "มังกร", "ดิน"
    elif (month == 2 and day >= 13) or (month == 3 and day <= 13): r, t = "กุมภ์", "ลม"
    else: r, t = "มีน", "น้ำ"
    
    # 2. ปีนักษัตร
    zodiac_animals = ["ปีมะเมีย", "ปีมะแม", "ปีวอก", "ปีระกา", "ปีจอ", "ปีกุน", "ปีชวด", "ปีฉลู", "ปีขาล", "ปีเถาะ", "ปีมะโรง", "ปีมะเส็ง"]
    animal = zodiac_animals[year_th % 12]
    
    return r, t, animal

# --- APP LAYOUT ---
st.title("🛡️ SYNAPSE COMMAND CENTER v6")
st.write("ระบบวิเคราะห์ดวงชะตาและสถิติกราฟชีวิต (ย้อนหลัง 50 ปี)")

# ส่วนรับข้อมูลวันเกิด
st.sidebar.header("👤 ข้อมูลส่วนบุคคล")
birth_date = st.sidebar.date_input("เลือกวัน/เดือน/ปีเกิด", 
                                  value=datetime(1990, 1, 1),
                                  min_value=datetime(1970, 1, 1),
                                  max_value=datetime.now())

st.sidebar.divider()
lottery_num = st.sidebar.text_input("เลขมงคลประจำตัว (3 ตัว)", "785")

# --- EXECUTION ---
rasi, that, naksat = get_horoscope_details(birth_date)
thai_days = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
weekday = thai_days[birth_date.weekday()]

# ส่วนแสดงดวงชะตา
st.subheader(f"✨ พื้นฐานดวงชะตาของ {weekday} ที่ {birth_date.strftime('%d/%m/%Y')}")

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("ราศี", rasi)
    st.write(f"**ปีนักษัตร:** {naksat}")
with c2:
    st.metric("ธาตุเจ้าเรือน", that)
    st.caption(ELEMENTS[that])
with c3:
    st.metric("กำลังวันเกิด", weekday)
    st.write("ใช้สำหรับเลือกเลขนำโชคประจำวัน")

# ส่วนคำนวณข้างขึ้นข้างแรมวันเกิด
st.divider()
st.write("### 🌒 สภาพท้องฟ้าในวันเกิดของคุณ")
# (ใช้ฟังก์ชันคำนวณจันทรคติที่เคยให้ไป)
ref_new_moon = datetime(2024, 1, 11)
diff = (birth_date - ref_new_moon).days
lunar_age = diff % 29.53
lunar_text = "🌑 แรม 14-15 ค่ำ (เดือนดับ)" if lunar_age < 1 else f"🌕 ข้างขึ้น/ข้างแรม (วัฏจักร {lunar_age:.1f})"
st.info(f"วันเกิดของคุณตรงกับสภาวะ: **{lunar_text}**")

# ส่วนวิเคราะห์เลข 18 ประตู
st.divider()
st.write(f"### 🔢 วิเคราะห์เลขมงคลจากฐานดวง {lottery_num}")
p3 = [''.join(p) for p in itertools.permutations(lottery_num)]
st.success(" | ".join(p3))

st.caption("ข้อมูลนี้รันตามหลักสถิติและความจริง 'อยู่นิ่งๆ ไม่เจ็บตัว' | พัฒนาโดย Ta101")
