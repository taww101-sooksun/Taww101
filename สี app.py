import streamlit as st
import pandas as pd
from datetime import datetime, date
import itertools

# --- CONFIG & UI ---
st.set_page_config(page_title="SYNAPSE: UNIVERSAL ANALYZER", layout="wide")
st.markdown("<style>.main { background-color: #0b1016; color: #f0f0f0; }</style>", unsafe_allow_html=True)

# --- ศาสตร์แห่งธาตุและการสมพงษ์ ---
MATCHING = {
    "ดิน": ["ดิน", "ไฟ", "น้ำ"],
    "น้ำ": ["น้ำ", "ดิน", "ลม"],
    "ไฟ": ["ไฟ", "ดิน", "ลม"],
    "ลม": ["ลม", "ไฟ", "น้ำ"]
}

# --- FUNCTIONS ---
def get_thai_astrology(date_obj):
    day, month = date_obj.day, date_obj.month
    year_th = date_obj.year + 543
    # ราศี & ธาตุ
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
    # ปีนักษัตร
    z_list = ["ปีมะเส็ง", "ปีมะเมีย", "ปีมะแม", "ปีวอก", "ปีระกา", "ปีจอ", "ปีกุน", "ปีชวด", "ปีฉลู", "ปีขาล", "ปีเถาะ", "ปีมะโรง"]
    eff_y = year_th - 1 if (month < 4 or (month == 4 and day < 13)) else year_th
    return r, t, z_list[eff_y % 12]

def calculate_lunar(date_obj):
    ref = date(2024, 1, 11)
    diff = (date_obj - ref).days
    age = diff % 29.53
    if age < 1 or age > 28.5: return "🌑 แรม 14-15 ค่ำ (มืดสนิท)"
    elif age < 14.2: return f"🌙 ขึ้น {int(age)+1} ค่ำ (ข้างขึ้น)"
    elif age < 15.8: return "🌕 ขึ้น 15 ค่ำ (เต็มดวง)"
    else: return f"🌘 แรม {int(age-14.7)+1} ค่ำ (ข้างแรม)"

# --- SIDEBAR: UNIVERSAL INPUT ---
st.sidebar.header("🧭 ตั้งค่าข้อมูล")
st.sidebar.write("ใส่ข้อมูลของคนสองคนที่ต้องการเปรียบเทียบ")

name1 = st.sidebar.text_input("ชื่อคนแรก/วันหลัก", "คนแรก")
date1 = st.sidebar.date_input(f"วันเกิด {name1}", value=date(2000, 1, 1))

name2 = st.sidebar.text_input("ชื่อคนที่สอง/วันเปรียบเทียบ", "คนที่สอง")
date2 = st.sidebar.date_input(f"วันเกิด {name2}", value=date(2000, 1, 1))

st.sidebar.divider()
lottery_mode = st.sidebar.checkbox("โหมดวิเคราะห์เลขหวย", value=True)
if lottery_mode:
    lottery_num = st.sidebar.text_input("เลข 3 ตัวที่เก็งไว้", "785", max_chars=3)

# --- MAIN APP ---
st.title("🛰️ SYNAPSE: DESTINY COMMANDER")
st.write(f"**วันปัจจุบัน:** {datetime.now().strftime('%d/%m/%Y')} | **BY:** Ta101")

# ส่วนที่ 1: การคำนวณระยะห่าง
st.divider()
st.subheader("⏱️ ระยะห่างระหว่างทั้งสองคน")
delta = abs((date2 - date1).days)
y = delta // 365
m = (delta % 365) // 30
d = (delta % 365) % 30
st.info(f"ทั้งสองคนเกิดห่างกันเป็นเวลา: **{delta:,} วัน** | หรือ **{y} ปี {m} เดือน {d} วัน**")

# ส่วนที่ 2: ข้อมูลรายบุคคล
col1, col2 = st.columns(2)
thai_days = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]

r1, t1, a1 = get_thai_astrology(date1)
r2, t2, a2 = get_thai_astrology(date2)

with col1:
    st.markdown(f"### 📌 ข้อมูลคุณ {name1}")
    st.success(f"**วัน{thai_days[date1.weekday()]}** ที่ {date1.strftime('%d/%m/%Y')}")
    st.write(f"- ราศี: {r1} | {a1}")
    st.write(f"- ธาตุ: {t1} | {calculate_lunar(date1)}")

with col2:
    st.markdown(f"### 🔍 ข้อมูลคุณ {name2}")
    st.warning(f"**วัน{thai_days[date2.weekday()]}** ที่ {date2.strftime('%d/%m/%Y')}")
    st.write(f"- ราศี: {r2} | {a2}")
    st.write(f"- ธาตุ: {t2} | {calculate_lunar(date2)}")

# ส่วนที่ 3: บทสรุปสมพงษ์
st.divider()
st.subheader("🔮 บทสรุปความสมพงษ์ (Compatibility)")
if t2 in MATCHING[t1]:
    st.balloons()
    st.success(f"✅ **สมพงษ์กัน:** คุณ {name1} (ธาตุ{t1}) และ คุณ {name2} (ธาตุ{t2}) เป็นคู่ที่ส่งเสริมกันอย่างดีเยี่ยม")
else:
    st.error(f"❌ **ไม่สมพงษ์กัน:** คุณ {name1} (ธาตุ{t1}) และ คุณ {name2} (ธาตุ{t2}) เป็นธาตุที่ขัดแย้งกัน ควรใช้ความอดทนต่อกัน")

# ส่วนที่ 4: วิเคราะห์เลข (ถ้าเปิดโหมด)
if lottery_mode and len(lottery_num) == 3:
    st.divider()
    st.subheader(f"🔢 วิเคราะห์ 18 ประตูจากเลข {lottery_num}")
    p3 = sorted(set([''.join(p) for p in itertools.permutations(lottery_num)]))
    p2 = sorted(set([f"{a}{b}" for a, b in itertools.permutations(lottery_num, 2)]))
    c_a, c_b = st.columns(2)
    with c_a: st.code(" | ".join(p3))
    with c_b: st.code(" | ".join(p2))

st.divider()
st.caption("สโลแกน: 'อยู่นิ่งๆ ไม่เจ็บตัว' | พัฒนาโดย Ta101 เพื่อคนไทยทุกคน")
