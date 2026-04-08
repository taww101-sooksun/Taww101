import streamlit as st
import pandas as pd
from datetime import datetime, date
import itertools

# --- CONFIG & UI ---
st.set_page_config(page_title="SYNAPSE v8: TIME & DESTINY", layout="wide")
st.markdown("<style>.main { background-color: #0b1016; color: #f0f0f0; }</style>", unsafe_allow_html=True)

# --- ศาสตร์แห่งธาตุ ---
ELEMENTS = {
    "ไฟ": "🔥 กระตือรือร้น ใจร้อน กล้าหาญ (เลขเด่น: 3, 7, 8)",
    "ดิน": "🌍 มั่นคง อดทน ละเอียด (เลขเด่น: 2, 5, 0)",
    "ลม": "💨 ปราดเปรียว รวดเร็ว ชอบอิสระ (เลขเด่น: 4, 6)",
    "น้ำ": "💧 อ่อนโยน ปรับตัวเก่ง มีเสน่ห์ (เลขเด่น: 1, 9)"
}

# --- FUNCTIONS ---
def get_thai_astrology(date_obj):
    day = date_obj.day
    month = date_obj.month
    year_th = date_obj.year + 543
    
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
    
    # 2. ปีนักษัตรไทย
    zodiac_list = ["ปีมะเส็ง", "ปีมะเมีย", "ปีมะแม", "ปีวอก", "ปีระกา", "ปีจอ", "ปีกุน", "ปีชวด", "ปีฉลู", "ปีขาล", "ปีเถาะ", "ปีมะโรง"]
    eff_year = year_th - 1 if (month < 4 or (month == 4 and day < 13)) else year_th
    animal = zodiac_list[eff_year % 12]
    
    return r, t, animal

def calculate_lunar(date_obj):
    ref_new_moon = date(2024, 1, 11)
    diff = (date_obj - ref_new_moon).days
    lunar_age = diff % 29.53059
    if lunar_age < 1 or lunar_age > 28.5: return "🌑 แรม 14-15 ค่ำ (มืดสนิท)", "error"
    elif lunar_age < 14.2: return f"🌙 ขึ้น {int(lunar_age)+1} ค่ำ (ข้างขึ้น)", "success"
    elif lunar_age < 15.8: return "🌕 ขึ้น 15 ค่ำ (เต็มดวง)", "success"
    else: return f"🌘 แรม {int(lunar_age-14.7)+1} ค่ำ (ข้างแรม)", "warning"

# --- SIDEBAR ---
st.sidebar.header("👤 ข้อมูลวิเคราะห์")
date1 = st.sidebar.date_input("วันที่ 1 (วันหลัก/วันเกิด)", value=date(1984, 5, 18))
date2 = st.sidebar.date_input("วันที่ 2 (วันที่เปรียบเทียบ)", value=date(1996, 8, 17))
lottery_num = st.sidebar.text_input("เลขเก็งวิเคราะห์ (3 ตัว)", "785", max_chars=3)

# --- MAIN APP ---
st.title("🛰️ SYNAPSE COMMAND CENTER v8")
st.write("**ID:** Ta101 | **สโลแกน:** 'อยู่นิ่งๆ ไม่เจ็บตัว'")

# ส่วนที่ 1: การวัดระยะห่างระหว่างวัน
st.divider()
st.subheader("⏱️ ระบบคำนวณระยะห่างเวลา")
delta = abs((date2 - date1).days)
years = delta // 365
remaining_days = delta % 365
st.info(f"ห่างกันทั้งหมด: **{delta:,}** วัน (ประมาณ {years} ปี {remaining_days} วัน)")

# ส่วนที่ 2: วิเคราะห์ 2 วันพร้อมกัน
st.divider()
col_left, col_right = st.columns(2)

thai_days = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]

with col_left:
    st.markdown(f"### 📅 ข้อมูลวันที่ 1")
    r1, t1, a1 = get_thai_astrology(date1)
    l_text1, l_type1 = calculate_lunar(date1)
    st.write(f"**วัน{thai_days[date1.weekday()]}** | ราศี{r1} | {a1}")
    st.write(f"ธาตุ: {t1} | {l_text1}")

with col_right:
    st.markdown(f"### 📅 ข้อมูลวันที่ 2")
    r2, t2, a2 = get_thai_astrology(date2)
    l_text2, l_type2 = calculate_lunar(date2)
    st.write(f"**วัน{thai_days[date2.weekday()]}** | ราศี{r2} | {a2}")
    st.write(f"ธาตุ: {t2} | {l_text2}")

# ส่วนที่ 3: วิเคราะห์เลข 18 ประตู
st.divider()
st.subheader(f"🔢 ชุดเลข 18 ประตู (จากเลข {lottery_num})")
if lottery_num.isdigit() and len(lottery_num) == 3:
    p3 = sorted(set([''.join(p) for p in itertools.permutations(lottery_num)]))
    p2 = sorted(set([f"{a}{b}" for a, b in itertools.permutations(lottery_num, 2)]))
    
    c1, c2 = st.columns(2)
    with c1:
        st.write("**3 ตัว (6 ประตู):**")
        st.code(" | ".join(p3))
    with c2:
        st.write("**2 ตัว (12 ประตู):**")
        st.code(" | ".join(p2))

st.divider()
st.caption("ความจริงสำคัญที่สุด... 'ไม่โกหก' ตามหลักการของ Ta101")
