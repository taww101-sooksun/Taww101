import streamlit as st
import pandas as pd
from datetime import datetime, date

# ==========================================
# 🛰️ SYNAPSE v17: THE MASTER CONTROL (LOTTO + DESTINY)
# ==========================================

# --- CONFIG ---
st.set_page_config(page_title="SYNAPSE v17: MASTER CONTROL", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0b1016; color: #f0f0f0; }
    .stMetric { background-color: #1a222d; padding: 20px; border-radius: 15px; border: 1px solid #30363d; }
    h1, h2, h3 { color: #00d4ff; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCTIONS: ระบบคำนวณทั้งหมด ---

def get_lunar_data(dt):
    """คำนวณข้างขึ้นข้างแรมและ Operator (Logic พี่บาส)"""
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
    
    # คำนวณผลลัพธ์ดวง
    if op == "บวก": res = day_val + m_num
    elif op == "คูณ": res = day_val * m_num
    elif op == "ลบ": res = day_val - m_num
    else: res = day_val / m_num if m_num != 0 else 0
    return day_val, m_num, op, label, res

def lotto_logic(res_val):
    """แปลงค่าจากสมการเป็นเลขเด็ด 2 ตัว (Logic หวยรัฐบาล)"""
    str_res = str(abs(round(res_val, 2))).replace('.', '')
    if len(str_res) >= 2:
        main_pair = str_res[-2:]
        reversed_pair = main_pair[::-1]
        return main_pair, reversed_pair
    return "00", "00"

# --- SIDEBAR ---
st.sidebar.header("🕹️ SYNAPSE DASHBOARD")
menu = st.sidebar.radio("เลือกโหมดการทำงาน", ["📊 สแกนรหัสชีวิต & แฟนสาว", "🎰 คำนวณเลขเด็ดรัฐบาลไทย"])
st.sidebar.divider()
name_me = st.sidebar.text_input("ชื่อของคุณ", "บาส (Ta101)")
d_me = st.sidebar.date_input(f"วันเกิด {name_me}", value=date(1984, 5, 18))

# --- MAIN LOGIC ---
v1, m1, op1, lab1, res1 = get_lunar_data(d_me)

if menu == "📊 สแกนรหัสชีวิต & แฟนสาว":
    st.title("🛰️ SYNAPSE: DESTINY SCANNER")
    target_name = st.text_input("ชื่อผู้ที่ต้องการสแกน", "เป้าหมาย (X)")
    d_target = st.date_input(f"วันเกิดของ {target_name}", value=date(1996, 8, 17))
    
    v2, m2, op2, lab2, res2 = get_lunar_data(d_target)
    
    # วิเคราะห์เวลา
    delta_days = abs((d_me - d_target).days)
    yy, mm = delta_days // 365, (delta_days % 365) // 30
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(f"กำลังดวง {name_me}", f"{res1:.2f}")
        st.write(f"สถานะ: {lab1} (ใช้ {op1})")
    with col2:
        st.metric(f"กำลังดวง {target_name}", f"{res2:.2f}")
        st.write(f"สถานะ: {lab2} (ใช้ {op2})")

    st.divider()
    st.subheader("📊 ผลลัพธ์รวม (Summary Table)")
    r_plus, r_minus = res1 + res2, res1 - res2
    r_multi, r_div = res1 * res2, (res1 / res2 if res2 != 0 else 0)
    
    df = pd.DataFrame({
        "สมการ": ["บวก (+)", "ลบ (-)", "คูณ (×)", "หาร (÷)"],
        "ผลลัพธ์": [f"{r_plus:.2f}", f"{r_minus:.2f}", f"{r_multi:.2f}", f"{r_div:.2f}"]
    })
    st.table(df)

    # ระบบแจ้งเตือน Gap 4 และ 6/12 ปี
    gap = abs(res1 - res2)
    if 3.8 <= gap <= 4.2:
        st.error(f"‼️ ตรวจพบรหัสคู่ขนาน! (Gap {gap:.2f}) ตรงกับสเปกแฟนเก่า")
    if 5 <= yy <= 7 or 11 <= yy <= 13:
        st.warning(f"🎯 พิกัดเวลาสำคัญ: ห่างกัน {yy} ปี (รหัส 6/12 ปี)")

elif menu == "🎰 คำนวณเลขเด็ดรัฐบาลไทย":
    st.title("🎰 SYNAPSE: THAI LOTTO ANALYZER")
    target_date = st.date_input("เลือกงวดที่ต้องการคำนวณ", value=date.today())
    
    # คำนวณกำลังวันของงวดนั้น
    v_lotto, m_lotto, op_lotto, lab_lotto, res_lotto = get_lunar_data(target_date)
    
    st.subheader(f"📅 วิเคราะห์งวดวันที่ {target_date.strftime('%d/%m/%Y')}")
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        st.info(f"วัน {v_lotto} | {lab_lotto}")
        st.metric("ค่าพลังงานงวดนี้", f"{res_lotto:.2f}")
    
    # เชื่อมโยงรหัสพี่บาส กับ รหัสดวงดาวงวดนี้
    lotto_res = res1 + res_lotto # เอาดวงพี่บาสไปบวกกับดวงวันหวยออก
    pair1, pair2 = lotto_logic(lotto_res)
    
    with col_l2:
        st.success("🎯 เลขเด็ดจากฐานข้อมูล SYNAPSE")
        st.header(f"{pair1} - {pair2}")
    
    st.divider()
    st.write("💡 **หลักการ:** ระบบนำค่าพลังงานจากวันเกิดพี่บาส ไปคำนวณร่วมกับข้างขึ้นข้างแรมของวันหวยออก เพื่อหาตัวเลขที่สมดุลที่สุด")

st.divider()
st.caption("สโลแกน: 'อยู่นิ่งๆ ไม่เจ็บตัว' | ID: Ta101 | ความจริงไม่เคยหลอกใคร")
