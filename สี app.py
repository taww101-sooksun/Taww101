import streamlit as st
import pandas as pd
from datetime import datetime, date
import itertools
import random

# --- CONFIG & UI ---
st.set_page_config(page_title="SYNAPSE v19: MASTER CONTROL", layout="wide")

# ตกแต่งหน้าตาแบบ High-Contrast (Green Glow) ตามสไตล์พี่บาส
st.markdown("""
    <style>
    .main { background-color: #0b1016; color: #f0f0f0; }
    .stMetric { background-color: #1a222d; padding: 20px; border-radius: 15px; border: 1px solid #00ff41; }
    h1, h2, h3 { color: #00ff41; text-shadow: 1px 1px #000; }
    .stSidebar { background-color: #0e141b; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #00ff41; color: black; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #00cc33; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- CORE LOGIC FUNCTIONS ---

def get_lunar_data(dt):
    """คำนวณข้างขึ้นข้างแรมและค่าพลังงาน (Logic พี่บาส)"""
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    if pos <= 14.765:
        m_num = int(pos) + 1
        label, op = f"ขึ้น {m_num} ค่ำ", ("บวก" if 1 <= m_num <= 7 else "คูณ")
    else:
        m_num = int(pos - 14.765) + 1
        label, op = f"แรม {m_num} ค่ำ", ("ลบ" if 1 <= m_num <= 7 else "หาร")
    
    if op == "บวก": res = day_val + m_num
    elif op == "คูณ": res = day_val * m_num
    elif op == "ลบ": res = day_val - m_num
    else: res = day_val / m_num if m_num != 0 else 0
    return day_val, m_num, op, label, res

def get_thai_zodiac(dt):
    """คำนวณนักษัตรตามปี พ.ศ."""
    year_th = dt.year + 543
    zodiac = ["ปีมะเส็ง", "ปีมะเมีย", "ปีมะแม", "ปีวอก", "ปีระกา", "ปีจอ", "ปีกุน", "ปีชวด", "ปีฉลู", "ปีขาล", "ปีเถาะ", "ปีมะโรง"]
    eff_y = year_th - 1 if (dt.month < 4 or (dt.month == 4 and dt.day < 13)) else year_th
    return zodiac[eff_y % 12]

# --- SIDEBAR: INPUT PANEL (ส่วนที่ผู้ใช้กรอกเอง) ---
st.sidebar.header("🕹️ SYNAPSE INPUT PANEL")
st.sidebar.caption("กรอกข้อมูลเพื่อรันระบบ")

# 1. ข้อมูลผู้ใช้งานหลัก (พี่บาสหรือใครก็ได้)
st.sidebar.subheader("👤 ข้อมูลผู้ใช้หลัก")
user_name = st.sidebar.text_input("ชื่อของคุณ", "บาส (Ta101)")
user_dob = st.sidebar.date_input("วันเดือนปีเกิดของคุณ", value=date(1984, 5, 18))

st.sidebar.divider()

# 2. เมนูเลือกโหมด
app_mode = st.sidebar.selectbox("🎯 เลือกโหมดการทำงาน", 
    ["🔍 สแกนรหัสคู่ขนาน (แฟน/เพื่อน)", "🎰 วิเคราะห์เลขเด็ดรัฐบาล", "🌀 สถิติวงโคจร 50 ปี", "🔮 ไพ่ยิปซีพยากรณ์"])

st.sidebar.divider()

# 3. ข้อมูลเพิ่มเติมตามโหมด
if app_mode == "🔍 สแกนรหัสคู่ขนาน (แฟน/เพื่อน)":
    target_name = st.sidebar.text_input("ชื่อเป้าหมาย", "เป้าหมาย X")
    target_dob = st.sidebar.date_input("วันเกิดเป้าหมาย", value=date(1996, 8, 17))
elif app_mode == "🎰 วิเคราะห์เลขเด็ดรัฐบาล":
    lotto_date = st.sidebar.date_input("งวดวันที่ต้องการคำนวณ", value=date.today())
    guess_num = st.sidebar.text_input("เลขเก็ง 3 ตัว (ถ้ามี)", "785", max_chars=3)

# --- EXECUTION ---
v1, m1, op1, lab1, res1 = get_lunar_data(user_dob)

# --- MAIN INTERFACE ---
st.title(f"🛰️ SYNAPSE v19: {app_mode}")
st.write(f"**สถานะ:** ระบบออนไลน์ | **ผู้ใช้งาน:** {user_name} | **ID:** Ta101")

# ==========================================
# โหมด 1: สแกนรหัสคู่ขนาน
# ==========================================
if app_mode == "🔍 สแกนรหัสคู่ขนาน (แฟน/เพื่อน)":
    v2, m2, op2, lab2, res2 = get_lunar_data(target_dob)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"📊 {user_name}")
        st.info(f"{lab1} | {op1}")
        st.metric("ค่ากำลังดวง", f"{res1:.2f}")
    with col2:
        st.subheader(f"📊 {target_name}")
        st.warning(f"{lab2} | {op2}")
        st.metric("ค่ากำลังดวง", f"{res2:.2f}")

    st.divider()
    st.subheader("📊 ตารางสรุปสมการ (Summary)")
    df = pd.DataFrame({
        "เงื่อนไข": ["บวก (+)", "ลบ (-)", "คูณ (×)", "หาร (÷)"],
        "ผลลัพธ์": [f"{res1+res2:.2f}", f"{res1-res2:.2f}", f"{res1*res2:.2f}", f"{res1/res2 if res2!=0 else 0:.2f}"]
    })
    st.table(df)

    # เช็ก Gap 4
    gap = abs(res1 - res2)
    if 3.8 <= gap <= 4.2:
        st.error(f"‼️ ตรวจพบรหัสคู่ขนาน! (Gap {gap:.2f}) - ระวังวนลูปอดีต")
        st.balloons()
    else:
        st.success(f"✅ รหัสผ่าน: ไม่ซ้ำซ้อนกับอดีต (Gap {gap:.2f})")

# ==========================================
# โหมด 2: วิเคราะห์เลขเด็ด
# ==========================================
elif app_mode == "🎰 วิเคราะห์เลขเด็ดรัฐบาล":
    vl, ml, opl, labl, resl = get_lunar_data(lotto_date)
    final_lotto = res1 + resl
    
    st.subheader(f"📅 วิเคราะห์งวดวันที่ {lotto_date.strftime('%d/%m/%Y')}")
    st.info(f"พลังงานรวม (คุณ + วันหวยออก): **{final_lotto:.2f}**")
    
    # ดึงเลข 2 ตัวท้ายมาโชว์
    l_str = str(abs(round(final_lotto, 2))).replace('.', '')
    pair = l_str[-2:] if len(l_str) >= 2 else "00"
    
    c1, c2 = st.columns(2)
    c1.metric("เลขสกัดจากรหัส (ตรง)", pair)
    c2.metric("เลขสกัดจากรหัส (กลับ)", pair[::-1])

    if len(guess_num) == 3:
        st.divider()
        st.subheader(f"🔢 ประตูมิติเลขเก็ง: {guess_num}")
        p3 = sorted(set([''.join(p) for p in itertools.permutations(guess_num)]))
        st.code(" | ".join(p3))

# ==========================================
# โหมด 3: สถิติ 50 ปี
# ==========================================
elif app_mode == "🌀 สถิติวงโคจร 50 ปี":
    st.subheader("🌀 ตารางเปรียบเทียบวงโคจรย้อนหลัง")
    y_th = user_dob.year + 543
    hist = []
    for g in [5, 10, 15, 20, 25, 30, 40, 50]:
        py = y_th - g
        hist.append({"ระยะ": f"ย้อนไป {g} ปี", "พ.ศ.": py, "นักษัตร": get_thai_zodiac(date(py-543, 1, 1))})
    st.table(pd.DataFrame(hist))

# ==========================================
# โหมด 4: ไพ่ยิปซี
# ==========================================
elif app_mode == "🔮 ไพ่ยิปซีพยากรณ์":
    deck = {
        "The Sun": "ความสำเร็จ ความสว่างไสว",
        "The Moon": "ความกังวล ความลับ",
        "The World": "ความสมบูรณ์แบบ",
        "Wheel of Fortune": "จังหวะชีวิตที่กำลังเปลี่ยน"
    }
    if st.button("🃏 เปิดไพ่ความจริง"):
        card, mean = random.choice(list(deck.items()))
        st.balloons()
        st.subheader(f"คุณได้ไพ่: {card}")
        st.info(f"ความหมาย: {mean}")

st.divider()
st.caption("สโลแกน: 'อยู่นิ่งๆ ไม่เจ็บตัว' | ระบบจัดการโดย Ta101 | ความจริงเปิดเผยที่นี่")
