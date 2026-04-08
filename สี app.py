import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- CONFIG & UI ---
st.set_page_config(page_title="SYNAPSE v15: OMNI-SCANNER", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0b1016; color: #f0f0f0; }
    .stMetric { background-color: #1a222d; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# --- CORE FUNCTIONS ---
def get_lunar_data(date_obj):
    """คำนวณข้างขึ้นข้างแรมแบบละเอียดเพื่อหาตัวเลขและเงื่อนไข (Logic พี่บาส)"""
    ref_date = date(1900, 1, 1)
    diff = (date_obj - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    
    day_val = date_obj.weekday() + 1 # จันทร์=1 ... อาทิตย์=7
    
    if pos <= 14.765: # ข้างขึ้น
        m_num = int(pos) + 1
        label = f"ขึ้น {m_num} ค่ำ"
        op = "บวก" if 1 <= m_num <= 7 else "คูณ"
    else: # ข้างแรม
        m_num = int(pos - 14.765) + 1
        label = f"แรม {m_num} ค่ำ"
        op = "ลบ" if 1 <= m_num <= 7 else "หาร"
    return day_val, m_num, op, label

def run_math_logic(v, m, op):
    """ประมวลผลตามเงื่อนไขที่พี่บาสกำหนด"""
    if op == "บวก": return v + m
    if op == "คูณ": return v * m
    if op == "ลบ": return v - m
    return v / m if m != 0 else 0

def get_time_gap_analysis(d1, d2):
    """คำนยณระยะห่างเวลา (ปี/เดือน/วัน)"""
    delta = abs((d1 - d2).days)
    yy = delta // 365
    mm = (delta % 365) // 30
    dd = (delta % 365) % 30
    direction = "ก่อนหน้า" if d2 < d1 else "ภายหลัง"
    return delta, yy, mm, dd, direction

# --- SIDEBAR: DATA INPUT ---
st.sidebar.header("📡 SYNAPSE COMMAND CENTER")
name_me = st.sidebar.text_input("ชื่อของคุณ", "บาส (Ta101)")
d_me = st.sidebar.date_input(f"วันเกิด {name_me}", value=date(1984, 5, 18))

st.sidebar.divider()
name_target = st.sidebar.text_input("ชื่อผู้ที่ต้องการสแกน", "เป้าหมาย")
d_target = st.sidebar.date_input(f"วันเกิดของ {name_target}", value=date(1996, 8, 17))

# --- CALCULATION PROCESS ---
v1, m1, op1, lab1 = get_lunar_data(d_me)
res1 = run_math_logic(v1, m1, op1)

v2, m2, op2, lab2 = get_lunar_data(d_target)
res2 = run_math_logic(v2, m2, op2)

t_days, t_yy, t_mm, t_dd, t_dir = get_time_gap_analysis(d_me, d_target)

# --- MAIN INTERFACE ---
st.title("🛰️ SYNAPSE v15: THE OMNI-SCANNER")
st.write(f"ระบบวิเคราะห์ความสมบูรณ์แบบของตัวเลข | ผู้ใช้งาน: **{name_me}**")

# Section 1: Individual Data
st.divider()
col_a, col_b = st.columns(2)
with col_a:
    st.subheader(f"👤 {name_me}")
    st.info(f"วันสัปดาห์: **{v1}** | {lab1}")
    st.write(f"ตัวดำเนินการ: **{op1}**")
    st.metric("ค่ากำลังดวงหลัก", f"{res1:.2f}")

with col_b:
    st.subheader(f"👤 {name_target}")
    st.warning(f"วันสัปดาห์: **{v2}** | {lab2}")
    st.write(f"ตัวดำเนินการ: **{op2}**")
    st.metric("ค่ากำลังเปรียบเทียบ", f"{res2:.2f}")

# Section 2: Mathematical Summary (ตารางที่พี่บาสต้องการ)
st.divider()
st.subheader("📊 ตารางวิเคราะห์ผลลัพธ์รวม (Mathematical Summary)")
res_plus = res1 + res2
res_minus = res1 - res2
res_multi = res1 * res2
res_div = res1 / res2 if res2 != 0 else 0

summary_df = pd.DataFrame({
    "เงื่อนไขการรวมข้อมูล": ["บวกกัน (+)", "ลบกัน (-)", "คูณกัน (×)", "หารกัน (÷)"],
    "ผลลัพธ์สุดท้าย": [f"{res_plus:.2f}", f"{res_minus:.2f}", f"{res_multi:.2f}", f"{res_div:.2f}"]
})
st.table(summary_df)

# Section 3: Parallel & Time Analysis
st.divider()
st.subheader("🔮 วิเคราะห์รหัสคู่ขนานและวงโคจรเวลา")

# คำนวณรหัส Gap 4 (อดีตแฟนสาวทั้ง 2)
gap_num = abs(res1 - res2)
is_parallel = 3.8 <= gap_num <= 4.2

# เช็กพิกัดเวลา 6 ปี และ 12 ปี
is_time_hit = (5 <= t_yy <= 7) or (11 <= t_yy <= 13)

c1, c2 = st.columns([2, 1])
with c1:
    # แสดงผลวิเคราะห์ Gap
    if is_parallel:
        st.error(f"‼️ ตรวจพบรหัสคู่ขนาน: ค่าห่างกัน {gap_num:.2f} (พิกัด Gap 4)")
        st.write("คนนี้มีโครงสร้างตัวเลขแบบเดียวกับ 'อดีต' ที่พี่เคยเจอมา รูปแบบอาจจะวนลูปเดิม")
        st.balloons()
    else:
        st.success(f"✅ ไม่พบรหัสคู่ขนาน: ค่าห่างกัน {gap_num:.2f} (รหัสใหม่)")

    # แสดงผลวิเคราะห์เวลา
    st.write("---")
    if is_time_hit:
        st.warning(f"🎯 พิกัดเวลาสำคัญ: คนนี้เกิด {t_dir} พี่บาส {t_yy} ปี (เข้าข่ายรหัส 6/12 ปี)")
    else:
        st.write(f"ระยะห่างเวลา: {t_yy} ปี {t_mm} เดือน {t_dd} วัน ({t_dir}คุณ)")

with c2:
    st.metric("GAP ตัวเลข", f"{gap_num:.2f}")
    st.metric("ระยะห่าง (วัน)", f"{t_days:,}")

st.divider()
st.caption("สโลแกน: 'อยู่นิ่งๆ ไม่เจ็บตัว' | พัฒนาโดย Ta101 | 'ความจริงไม่เคยหลอกใคร'")
