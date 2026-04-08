import streamlit as st
import pandas as pd
from datetime import datetime
import itertools
from datetime import date

d1 = date(1984, 5, 18)
d2 = date(1996, 8, 17)
delta = d2 - d1

print(f"ห่างกันทั้งหมด: {delta.days} วัน")

# --- CONFIG & UI ---
st.set_page_config(page_title="SYNAPSE v7: MASTER COMMAND", layout="wide")
st.markdown("<style>.main { background-color: #0b1016; color: #f0f0f0; }</style>", unsafe_allow_html=True)

# --- ศาสตร์แห่งธาตุ ---
ELEMENTS = {
    "ไฟ": "🔥 กระตือรือร้น ใจร้อน กล้าหาญ (เลขเด่น: 3, 7, 8)",
    "ดิน": "🌍 มั่นคง อดทน ละเอียด (เลขเด่น: 2, 5, 0)",
    "ลม": "💨 ปราดเปรียว รวดเร็ว ชอบอิสระ (เลขเด่น: 4, 6)",
    "น้ำ": "💧 อ่อนโยน ปรับตัวเก่ง มีเสน่ห์ (เลขเด่น: 1, 9)"
}

# --- FUNCTIONS ---
def get_thai_astrology(date):
    day = date.day
    month = date.month
    year_th = date.year + 543
    
    # 1. ราศี & ธาตุ (นับแบบไทย)
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
    
    # 2. ปีนักษัตรไทย (สูตรคำนวณจาก พ.ศ.)
    # พ.ศ. 2527 หาร 12 เหลือเศษ 7 (ถ้าใช้สูตรไทยมาตรฐาน เศษ 7 คือปีชวด)
    zodiac_list = ["ปีมะเส็ง", "ปีมะเมีย", "ปีมะแม", "ปีวอก", "ปีระกา", "ปีจอ", "ปีกุน", "ปีชวด", "ปีฉลู", "ปีขาล", "ปีเถาะ", "ปีมะโรง"]
    
    # เช็คช่วงสงกรานต์เหมือนเดิม
    eff_year = year_th - 1 if (month < 4 or (month == 4 and day < 13)) else year_th
    animal = zodiac_list[eff_year % 12]
    
    return r, t, animal

def calculate_lunar(date):
    """คำนวณข้างขึ้นข้างแรมแบบละเอียด"""
    ref_new_moon = datetime(2024, 1, 11).date()
    diff = (date - ref_new_moon).days
    lunar_age = diff % 29.53059
    
    if lunar_age < 1 or lunar_age > 28.5:
        return "🌑 แรม 14-15 ค่ำ (เดือนดับ/มืดสนิท)", "error"
    elif lunar_age < 14.2:
        return f"🌙 ขึ้น {int(lunar_age)+1} ค่ำ (ข้างขึ้น)", "success"
    elif lunar_age < 15.8:
        return "🌕 ขึ้น 15 ค่ำ (พระจันทร์เต็มดวง)", "success"
    else:
        return f"🌘 แรม {int(lunar_age-14.7)+1} ค่ำ (ข้างแรม)", "warning"

# --- SIDEBAR ---
st.sidebar.header("👤 ข้อมูลส่วนบุคคล (ย้อนหลัง 50 ปี)")
user_date = st.sidebar.date_input("เลือกวันที่/วันเกิด", 
                                 value=datetime(2026, 4, 16),
                                 min_value=datetime(1970, 1, 1))
lottery_num = st.sidebar.text_input("เลขเก็งวิเคราะห์ (3 ตัว)", "785", max_chars=3)

# --- MAIN APP ---
st.title("🛰️ SYNAPSE COMMAND CENTER v7")
st.write("**สถานะระบบ:** ออนไลน์ | **ID:** Ta101 | **สโลแกน:** 'อยู่นิ่งๆ ไม่เจ็บตัว'")

# ดึงข้อมูลโหราศาสตร์
rasi, that, naksat = get_thai_astrology(user_date)
lunar_text, lunar_type = calculate_lunar(user_date)
thai_days = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
day_name = thai_days[user_date.weekday()]

# ส่วนแสดงผลข้อมูล
st.divider()
st.subheader(f"📅 วิเคราะห์วันที่ {user_date.strftime('%d/%m/%Y')} (วัน{day_name})")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("ราศี", rasi)
    st.write(f"**ปีนักษัตร:** {naksat}")
with col2:
    st.metric("ธาตุ", that)
    st.caption(ELEMENTS[that])
with col3:
    st.metric("กำลังวัน", day_name)
    st.write("เลขประจำวันพฤหัสคือ **5**")

# แสดงข้างขึ้นข้างแรม
st.write("### 🌒 สภาพข้างขึ้นข้างแรม")
if lunar_type == "success": st.success(lunar_text)
elif lunar_type == "warning": st.warning(lunar_text)
else: st.error(lunar_text)

# วิเคราะห์ 18 ประตู
st.divider()
st.subheader(f"🔢 ชุดเลข 18 ประตู (จากเลข {lottery_num})")
if lottery_num.isdigit() and len(lottery_num) == 3:
    p3 = [''.join(p) for p in itertools.permutations(lottery_num)]
    p2_raw = list(itertools.combinations(lottery_num, 2))
    p2 = []
    for pair in p2_raw:
        p2.append(f"{pair[0]}{pair[1]}"); p2.append(f"{pair[1]}{pair[0]}")
    
    c_a, c_b = st.columns(2)
    with c_a:
        st.write("**3 ตัวตรง/สลับ (6 ประตู):**")
        st.code(" | ".join(sorted(set(p3))))
    with c_b:
        st.write("**2 ตัว บน-ล่าง (12 ประตู):**")
        st.code(" | ".join(sorted(set(p2))))
else:
    st.error("กรุณากรอกเลขให้ครบ 3 หลัก")

st.divider()
st.caption("ระบบรันข้อมูลตามความจริง 'ไม่โกหก' ตามหลักการของ Ta101")
