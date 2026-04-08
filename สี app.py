import streamlit as st
import pandas as pd
from datetime import datetime
import itertools

# --- CONFIG & UI ---
st.set_page_config(page_title="SYNAPSE 50-YEAR ANALYZER", layout="wide")
st.markdown("<style>.main { background-color: #0b0e14; color: #00ff41; }</style>", unsafe_allow_html=True)

# --- ADVANCED LOGIC FUNCTIONS ---

def get_thai_zodiac(year_th):
    """คำนวณปีนักษัตร (แบบไทย พ.ศ.)"""
    zodiac = ["ปีมะเมีย", "ปีมะแม", "ปีวอก", "ปีระกา", "ปีจอ", "ปีกุน", "ปีชวด", "ปีฉลู", "ปีขาล", "ปีเถาะ", "ปีมะโรง", "ปีมะเส็ง"]
    # อ้างอิงปี 2569 (มะเมีย)
    return zodiac[year_th % 12]

def get_zodiac_sign(day, month):
    """คำนวณราศี (แบบสากลที่นิยมในไทย)"""
    if (month == 3 and day >= 21) or (month == 4 and day <= 19): return "ราศีเมษ", "ไฟ"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20): return "ราศีพฤษภ", "ดิน"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 21): return "ราศีเมถุน", "ลม"
    elif (month == 6 and day >= 22) or (month == 7 and day <= 22): return "ราศีกรกฎ", "น้ำ"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22): return "ราศีสิงห์", "ไฟ"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22): return "ราศีกันย์", "ดิน"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 23): return "ราศีตุลย์", "ลม"
    elif (month == 10 and day >= 24) or (month == 11 and day <= 21): return "ราศีพิจิก", "น้ำ"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21): return "ราศีธนู", "ไฟ"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19): return "ราศีมังกร", "ดิน"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18): return "ราศีกุมภ์", "ลม"
    else: return "ราศีมีน", "น้ำ"

def get_lunar_phase_advanced(date):
    """คำนวณข้างขึ้นข้างแรม (ประมาณการจันทรคติ)"""
    ref_new_moon = datetime(2024, 1, 11) # วันเดือนดับอ้างอิง
    diff = (date - ref_new_moon).days
    lunar_age = diff % 29.53059
    
    if lunar_age < 1 or lunar_age > 28.5:
        return "🌑 แรม 14-15 ค่ำ (เดือนดับ)"
    elif lunar_age < 14.7:
        day_num = int(lunar_age + 1)
        return f"🌙 ขึ้น {day_num} ค่ำ"
    else:
        day_num = int(lunar_age - 14.7 + 1)
        return f"🌘 แรม {day_num} ค่ำ"

# --- MAIN APP ---
st.title("🛡️ SYNAPSE COMMAND CENTER: 50-YEAR ARCHIVE")
st.write("ID: Ta101 | สถิติ 50 ปี: ความจริงที่ไม่มีการหลอกลวง")

# Sidebar Input
st.sidebar.header("⚙️ ตั้งค่าการสแกน")
target_date = st.sidebar.date_input("เลือกวันที่ต้องการย้อนรอย", value=datetime(2026, 4, 16))
target_year_th = target_date.year + 543
my_num = st.sidebar.text_input("เลขเก็ง 3 ตัว", "785")

# --- EXECUTION ---
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📅 ข้อมูลโหราศาสตร์/สถิติ")
    thai_days = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    
    lunar = get_lunar_phase_advanced(datetime.combine(target_date, datetime.min.time()))
    zodiac_name, element = get_zodiac_sign(target_date.day, target_date.month)
    animal = get_thai_zodiac(target_year_th)
    
    st.info(f"**วันที่:** {target_date.strftime('%d/%m/%Y')} (วัน{thai_days[target_date.weekday()]})")
    st.success(f"**จันทรคติ:** {lunar}")
    st.warning(f"**นักษัตร:** {animal}")
    st.error(f"**ราศี:** {zodiac_name} (ธาตุ{element})")

with col2:
    st.markdown("### 🔢 วิเคราะห์ประตูมิติ (18 GATES)")
    if len(my_num) == 3:
        p3 = [''.join(p) for p in itertools.permutations(my_num)]
        p2 = [f"{a}{b}" for a, b in itertools.permutations(my_num, 2)]
        
        st.write("**3 ตัว (บน):**")
        st.code(" | ".join(p3))
        st.write("**2 ตัว (บน-ล่าง):**")
        st.code(" | ".join(p2))

# --- 50-YEAR ENGINE ---
st.divider()
st.markdown("### 🌀 ค้นหาจุดวนซ้ำ (Cycle Detection)")
st.write(f"วิเคราะห์ระยะห่าง 5, 10, 20, 30, 40, 50 ปี จากปี {target_year_th}")

history_data = []
for gap in [5, 10, 15, 20, 25, 30, 40, 50]:
    past_year = target_year_th - gap
    past_animal = get_thai_zodiac(past_year)
    history_data.append({
        "ระยะห่าง": f"{gap} ปี",
        "ปี พ.ศ.": past_year,
        "นักษัตร": past_animal,
        "สถานะ": "สแกนแล้ว"
    })

st.table(pd.DataFrame(history_data))

st.caption("ข้อมูลนี้ใช้เพื่อการวิเคราะห์ทางสถิติ 'อยู่นิ่งๆ ไม่เจ็บตัว' พัฒนาโดย Ta101")
