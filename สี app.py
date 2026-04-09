import streamlit as st
import pandas as pd
from datetime import datetime, date
import streamlit as st
from datetime import datetime, date
import random

# --- CONFIG & UI ---
st.set_page_config(page_title="SYNAPSE v13: FUTURE SCANNER", layout="wide")
st.markdown("<style>.main { background-color: #0b1016; color: #f0f0f0; }</style>", unsafe_allow_html=True)

# --- LOGIC FUNCTIONS ---
def get_lunar_data(date_obj):
    ref_date = date(1900, 1, 1)
    diff = (date_obj - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = date_obj.weekday() + 1
    if pos <= 14.765:
        m_num = int(pos) + 1
        op = "บวก" if 1 <= m_num <= 7 else "คูณ"
    else:
        m_num = int(pos - 14.765) + 1
        op = "ลบ" if 1 <= m_num <= 7 else "หาร"
    return day_val, m_num, op

def run_math(v, m, op):
    if op == "บวก": return v + m
    if op == "คูณ": return v * m
    if op == "ลบ": return v - m
    return v / m if m != 0 else 0

# --- SIDEBAR ---
st.sidebar.header("🛸 FUTURE RADAR")
my_birth = st.sidebar.date_input("วันเกิดพี่บาส (วันหลัก)", value=date(1984, 5, 18))
target_name = st.sidebar.text_input("ชื่อคนที่จะสแกน", "สาวนิรนาม")
target_birth = st.sidebar.date_input(f"วันเกิดของ {target_name}", value=date(1996, 8, 17))

# --- MAIN APP ---
st.title("🛰️ SYNAPSE v13: FUTURE SCANNER")
st.write(f"**สถานะระบบ:** กำลังตรวจสอบรหัสคู่ขนาน... | **ID:** Ta101")

# คำนวณค่าของพี่บาส (ตัวตั้ง)
v_me, m_me, op_me = get_lunar_data(my_birth)
res_me = run_math(v_me, m_me, op_me)

# คำนวณค่าของเป้าหมาย
v_t, m_t, op_t = get_lunar_data(target_birth)
res_t = run_math(v_t, m_t, op_t)

# ส่วนการแสดงผลวิเคราะห์
st.divider()
col1, col2 = st.columns(2)
with col1:
    st.subheader("📌 รหัสพี่บาส")
    st.info(f"วัน {v_me} | {op_me} {m_me} = **{res_me:.2f}**")

with col2:
    st.subheader(f"📌 รหัสคุณ {target_name}")
    st.warning(f"วัน {v_t} | {op_t} {m_t} = **{res_t:.2f}**")

# --- ระบบ SCANNER (ตรวจจับรหัสแฝด) ---
st.divider()
st.subheader("🔮 ผลการสแกนรหัสคู่ขนาน (DNA Analysis)")

sum_val = res_me + res_t
diff_val = res_me - res_t
multi_val = res_me * res_t
div_val = res_me / res_t if res_t != 0 else 0

# วิเคราะห์ตามสถิติที่พี่บาสพบ (Gap 4 และเลข 18, 22)
gap = abs(res_me - res_t)
is_parallel = False
if 3.5 <= gap <= 4.5: # ตรวจพบ Gap 4 ที่พี่เจอ
    is_parallel = True

st.write("---")
c1, c2, c3, c4 = st.columns(4)
c1.metric("บวก", f"{sum_val:.2f}")
c2.metric("ลบ", f"{diff_val:.2f}")
c3.metric("คูณ", f"{multi_val:.2f}")
c4.metric("หาร", f"{div_val:.2f}")

if is_parallel:
    st.balloons()
    st.success(f"‼️ **ตรวจพบรหัสคู่ขนาน!** ค่า Gap ห่างกัน {gap:.2f} (ใกล้เคียง 4) คนนี้มีรหัสชีวิตแบบเดียวกับอดีตที่พี่เคยเจอ!")
    st.info("คำแนะนำ: 'อยู่นิ่งๆ ไม่เจ็บตัว' ดูท่าทีไปก่อน เพราะคนนี้รหัสแรงเหมือนเดิม!")
else:
    st.write("🔍 ผลการคำนวณอยู่ในเกณฑ์ใหม่ ไม่ซ้ำกับรหัสอดีต")

st.divider()
st.caption("พัฒนาโดย Ta101 | 'ความจริงอยู่ที่ปลายนิ้ว' ")

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
