import streamlit as st
import pandas as pd
from datetime import datetime, date

# ==========================================
# 🛰️ SYNAPSE v16: THE INFINITY SCANNER
# ==========================================

# --- การตั้งค่าหน้าจอ (UI CONFIG) ---
st.set_page_config(page_title="SYNAPSE v16: THE INFINITY SCANNER", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0b1016; color: #f0f0f0; }
    .stMetric { background-color: #1a222d; padding: 25px; border-radius: 15px; border: 1px solid #30363d; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    h1, h2, h3 { color: #00d4ff; }
    .stTable { background-color: #1a222d; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNCTIONS: ระบบคำนวณเบื้องหลัง ---

def get_true_zodiac(dt):
    """คำนวณปีนักษัตรให้ตรงตามความจริง (ไทย)"""
    year_th = dt.year + 543
    z_list = ["ปีมะเส็ง", "ปีมะเมีย", "ปีมะแม", "ปีวอก", "ปีระกา", "ปีจอ", "ปีกุน", "ปีชวด", "ปีฉลู", "ปีขาล", "ปีเถาะ", "ปีมะโรง"]
    # ปรับช่วงเปลี่ยนปี (ประมาณเมษายน)
    eff_y = year_th - 1 if (dt.month < 4 or (dt.month == 4 and dt.day < 13)) else year_th
    return z_list[eff_y % 12]

def get_full_lunar_logic(dt):
    """คำนวณข้างขึ้นข้างแรมและ Operator ตาม Logic พี่บาส"""
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    
    day_val = dt.weekday() + 1 # จันทร์=1 ... อาทิตย์=7
    
    if pos <= 14.765: # ช่วงข้างขึ้น
        m_num = int(pos) + 1
        label = f"ขึ้น {m_num} ค่ำ"
        op = "บวก" if 1 <= m_num <= 7 else "คูณ"
    else: # ช่วงข้างแรม
        m_num = int(pos - 14.765) + 1
        label = f"แรม {m_num} ค่ำ"
        op = "ลบ" if 1 <= m_num <= 7 else "หาร"
    
    # คำนวณค่าพลังส่วนบุคคล
    if op == "บวก": res = day_val + m_num
    elif op == "คูณ": res = day_val * m_num
    elif op == "ลบ": res = day_val - m_num
    else: res = day_val / m_num if m_num != 0 else 0
        
    return day_val, m_num, op, label, res

# --- SIDEBAR: แผงควบคุมข้อมูล ---
st.sidebar.header("📡 ศูนย์ควบคุม SYNAPSE")
st.sidebar.write("ID: **Ta101** | CODENAME: **BAS**")
st.sidebar.divider()

name_me = st.sidebar.text_input("ชื่อของคุณ", "บาส (Ta101)")
d_me = st.sidebar.date_input(f"วันเกิด {name_me}", value=date(1984, 5, 18))

st.sidebar.divider()
name_target = st.sidebar.text_input("ชื่อผู้ที่ต้องการสแกน", "เป้าหมาย (X)")
d_target = st.sidebar.date_input(f"วันเกิดของ {name_target}", value=date(1996, 8, 17))

# --- ประมวลผลข้อมูล (PROCESSING) ---
v1, m1, op1, lab1, res1 = get_full_lunar_logic(d_me)
v2, m2, op2, lab2, res2 = get_full_lunar_logic(d_target)

# วิเคราะห์ระยะห่างเวลา
delta_days = abs((d_me - d_target).days)
yy = delta_days // 365
mm = (delta_days % 365) // 30
dd = (delta_days % 365) % 30
direction = "เกิดก่อนคุณ" if d_target < d_me else "เกิดหลังคุณ"

# --- การแสดงผลหลัก (MAIN UI) ---
st.title("🛰️ SYNAPSE v16: THE INFINITY SCANNER")
st.write(f"วิเคราะห์ความสัมพันธ์เชิงสถิติและรหัสชีวิตขนาน | รันระบบเมื่อ: {datetime.now().strftime('%H:%M:%S')}")

# ส่วนที่ 1: ข้อมูลเจาะลึกรายบุคคล
st.divider()
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"👤 {name_me}")
    st.write(f"นักษัตร: **{get_true_zodiac(d_me)}**")
    st.info(f"วัน {v1} | {lab1}")
    st.write(f"สูตรที่ใช้: **{v1} {op1} {m1}**")
    st.metric("ค่ากำลังดวงหลัก", f"{res1:.2f}")

with col2:
    st.subheader(f"👤 {name_target}")
    st.write(f"นักษัตร: **{get_true_zodiac(d_target)}**")
    st.warning(f"วัน {v2} | {lab2}")
    st.write(f"สูตรที่ใช้: **{v2} {op2} {m2}**")
    st.metric("ค่ากำลังเปรียบเทียบ", f"{res2:.2f}")

# ส่วนที่ 2: ตารางสรุปผลลัพธ์รวม (ที่พี่บาสต้องการ)
st.divider()
st.subheader("📊 ตารางสรุปผลลัพธ์ (Mathematical Summary)")

val_plus = res1 + res2
val_minus = res1 - res2
val_multi = res1 * res2
val_div = res1 / res2 if res2 != 0 else 0

summary_data = {
    "สมการเชื่อมโยง": ["บวกกัน (+)", "ลบกัน (-)", "คูณกัน (×)", "หารกัน (÷)"],
    "ผลลัพธ์สุดท้าย": [f"{val_plus:.2f}", f"{val_minus:.2f}", f"{val_multi:.2f}", f"{val_div:.2f}"]
}
st.table(pd.DataFrame(summary_data))

# ส่วนที่ 3: ระบบตรวจจับรหัสคู่ขนาน (DNA & Time Scanner)
st.divider()
st.subheader("🔮 วิเคราะห์รหัสคู่ขนานและวงโคจรเวลา")

# 1. ตรวจจับ Gap 4 (อดีตแฟนสาว)
gap_found = abs(res1 - res2)
is_parallel = 3.8 <= gap_found <= 4.2

# 2. ตรวจจับพิกัด 6 ปี และ 12 ปี
is_time_hit = (5 <= yy <= 7) or (11 <= yy <= 13)

c_res1, c_res2 = st.columns([2, 1])
with c_res1:
    if is_parallel:
        st.error(f"‼️ ตรวจพบรหัสคู่ขนาน: ค่าห่างกัน {gap_found:.2f} (พิกัด Gap 4)")
        st.write("📢 **คำเตือน:** รหัสนี้ตรงกับสถิติแฟนเก่าที่พี่เจอมา รูปแบบชีวิตมีโอกาสวนลูปเดิม")
        st.balloons()
    else:
        st.success(f"✅ ไม่พบรหัสคู่ขนาน: ค่าห่างกัน {gap_found:.2f}")
        st.write("✨ **วิเคราะห์:** คนนี้มีโครงสร้างตัวเลขใหม่ ไม่ซ้ำรอยรหัสอดีต")
    
    st.write("---")
    if is_time_hit:
        st.warning(f"🎯 พิกัดเวลาสำคัญ: คนนี้{direction} {yy} ปี (เข้าข่ายรหัส 6/12 ปี)")
    else:
        st.write(f"ระยะห่างเวลา: {yy} ปี {mm} เดือน {dd} วัน ({direction})")

with c_res2:
    st.metric("GAP ตัวเลข", f"{gap_found:.2f}")
    st.metric("ห่างกันทั้งหมด (วัน)", f"{delta_days:,}")

st.divider()
st.caption("สโลแกน: 'อยู่นิ่งๆ ไม่เจ็บตัว' | พัฒนาโดย Ta101 | 'ความจริงอยู่ที่การพิสูจน์'")
