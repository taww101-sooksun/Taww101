import streamlit as st
import pandas as pd
from datetime import datetime, date
import itertools
import random

# ==========================================
# 🛰️ SYNAPSE v18: THE ULTIMATE COMMAND CENTER
# ==========================================

st.set_page_config(page_title="SYNAPSE v18: MASTER CONTROL", layout="wide")

# --- UI STYLING ---
st.markdown("""
    <style>
    .main { background-color: #0b1016; color: #f0f0f0; }
    .stMetric { background-color: #1a222d; padding: 20px; border-radius: 15px; border: 1px solid #30363d; }
    h1, h2, h3 { color: #00ff41; text-shadow: 2px 2px #000; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #00ff41; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- CORE LOGIC FUNCTIONS ---

def get_lunar_data(dt):
    """คำนวณข้างขึ้นข้างแรมและตัวแปรทางคณิตศาสตร์"""
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
    year_th = dt.year + 543
    zodiac = ["ปีมะเส็ง", "ปีมะเมีย", "ปีมะแม", "ปีวอก", "ปีระกา", "ปีจอ", "ปีกุน", "ปีชวด", "ปีฉลู", "ปีขาล", "ปีเถาะ", "ปีมะโรง"]
    eff_y = year_th - 1 if (dt.month < 4 or (dt.month == 4 and dt.day < 13)) else year_th
    return zodiac[eff_y % 12]

# --- SIDEBAR: ALL USER INPUTS ---
st.sidebar.header("🕹️ แผงควบคุม (INPUT)")
menu = st.sidebar.selectbox("เลือกฟีเจอร์", ["📊 สแกนรหัสคู่ขนาน", "🎰 คำนวณหวยรัฐบาล", "🌀 ย้อนรอยสถิติ 50 ปี", "🔮 ไพ่ยิปซีพยากรณ์"])

st.sidebar.divider()
# พี่กรอกชื่อและวันเกิดตัวเองที่นี่
name_me = st.sidebar.text_input("ชื่อของคุณ", "บาส (Ta101)")
d_me = st.sidebar.date_input("วันเกิดของคุณ", value=date(1984, 5, 18))

# ข้อมูลผู้เปรียบเทียบ (จะกรอกเมื่อใช้โหมดสแกน)
if menu == "📊 สแกนรหัสคู่ขนาน":
    st.sidebar.divider()
    name_target = st.sidebar.text_input("ชื่อคนที่จะสแกน", "เป้าหมาย")
    d_target = st.sidebar.date_input("วันเกิดเป้าหมาย", value=date(1996, 8, 17))

# ข้อมูลตัวเลข (จะกรอกเมื่อใช้โหมดหวย)
if menu == "🎰 คำนวณหวยรัฐบาล":
    st.sidebar.divider()
    lotto_date = st.sidebar.date_input("งวดวันที่ต้องการคำนวณ", value=date.today())
    target_num = st.sidebar.text_input("เลขเก็ง 3 ตัว", "785", max_chars=3)

# --- PROCESSING ---
v1, m1, op1, lab1, res1 = get_lunar_data(d_me)

# --- MAIN INTERFACE ---
st.title(f"🛰️ SYNAPSE COMMANDER: {menu}")
st.write(f"ID: **Ta101** | วันปัจจุบัน: {datetime.now().strftime('%d/%m/%Y')}")

# ==========================================
# MODE 1: สแกนรหัสคู่ขนาน
# ==========================================
if menu == "📊 สแกนรหัสคู่ขนาน":
    v2, m2, op2, lab2, res2 = get_lunar_data(d_target)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"👤 {name_me}")
        st.info(f"{lab1} | {op1}")
        st.metric("ค่ากำลังดวงหลัก", f"{res1:.2f}")
    with col2:
        st.subheader(f"👤 {name_target}")
        st.warning(f"{lab2} | {op2}")
        st.metric("ค่ากำลังเปรียบเทียบ", f"{res2:.2f}")

    st.divider()
    st.subheader("📊 ตารางสรุป 4 ทิศทาง")
    r_plus, r_minus = res1 + res2, res1 - res2
    r_multi, r_div = res1 * res2, (res1 / res2 if res2 != 0 else 0)
    st.table(pd.DataFrame({
        "สมการ": ["บวก (+)", "ลบ (-)", "คูณ (×)", "หาร (÷)"],
        "ผลลัพธ์": [f"{r_plus:.2f}", f"{r_minus:.2f}", f"{r_multi:.2f}", f"{r_div:.2f}"]
    }))

    gap = abs(res1 - res2)
    if 3.8 <= gap <= 4.2:
        st.error(f"‼️ ตรวจพบรหัสคู่ขนาน (Gap {gap:.2f}) - มาทรงเดียวกับอดีต!")
        st.balloons()
    else: st.success(f"✅ ไม่พบรหัสคู่ขนานเดิม (Gap {gap:.2f})")

# ==========================================
# MODE 2: คำนวณหวยรัฐบาล
# ==========================================
elif menu == "🎰 คำนวณหวยรัฐบาล":
    v_l, m_l, op_l, lab_l, res_l = get_lunar_data(lotto_date)
    lotto_total = res1 + res_l
    
    st.subheader(f"📅 วิเคราะห์งวดวันที่ {lotto_date.strftime('%d/%m/%Y')}")
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.info(f"วันเกิดคุณ: {res1:.2f} + วันหวยออก: {res_l:.2f}")
        st.metric("ผลลัพธ์รวมรหัส", f"{lotto_total:.2f}")
    
    with col_l2:
        st.success("🎯 เลขสกัดจากรหัส SYNAPSE")
        s_num = str(abs(round(lotto_total, 2))).replace('.', '')[-2:]
        st.header(f"เลขท้าย: {s_num} - {s_num[::-1]}")

    if len(target_num) == 3:
        st.divider()
        st.subheader(f"🔢 ประตูมิติเลขเก็ง: {target_num}")
        p3 = sorted(set([''.join(p) for p in itertools.permutations(target_num)]))
        st.code(" | ".join(p3))

# ==========================================
# MODE 3: ย้อนรอยสถิติ 50 ปี
# ==========================================
elif menu == "🌀 ย้อนรอยสถิติ 50 ปี":
    st.subheader(f"สแกนรอบวงโคจรปีนักษัตร (อ้างอิงคุณ {name_me})")
    y_th = d_me.year + 543
    history = []
    for gap in [5, 10, 20, 30, 40, 50]:
        past_y = y_th - gap
        history.append({"ระยะ": f"ย้อน {gap} ปี", "พ.ศ.": past_y, "นักษัตร": get_thai_zodiac(date(past_y-543, 1, 1))})
    st.table(pd.DataFrame(history))

# ==========================================
# MODE 4: ไพ่ยิปซี
# ==========================================
elif menu == "🔮 ไพ่ยิปซีพยากรณ์":
    deck = {"The Sun": "ความสำเร็จ", "Wheel of Fortune": "โชคชะตาเปลี่ยน", "The Star": "ความหวัง"}
    if st.button("🃏 จิ้มเพื่อเปิดความจริง"):
        card = random.choice(list(deck.items()))
        st.balloons()
        st.header(f"ได้ไพ่: {card[0]}")
        st.info(f"ความหมาย: {card[1]}")

st.divider()
st.caption("สโลแกน: 'อยู่นิ่งๆ ไม่เจ็บตัว' | ความจริงอยู่ที่พี่กรอกเอง")
