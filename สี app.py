import streamlit as st
import pandas as pd
from datetime import datetime, date

# ==========================================
# 🛰️ SYNAPSE v15.2: THE OMNI-REVEALER
# ==========================================

st.set_page_config(page_title="SYNAPSE v15.2: THE OMNI-REVEALER", layout="wide")

# --- ส่วนตกแต่งหน้าตา ---
st.markdown("""
    <style>
    .main { background-color: #0b1016; color: #f0f0f0; }
    .stMetric { background-color: #1a222d; padding: 20px; border-radius: 15px; border: 1px solid #4f4f4f; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: รับข้อมูล (Input) ---
st.sidebar.header("📡 กรอกข้อมูลเพื่อสแกนรหัส")
name_me = st.sidebar.text_input("ชื่อของคุณ", "บาส (Ta101)")
d_me = st.sidebar.date_input(f"วันเกิด {name_me}", value=date(1984, 5, 18))

st.sidebar.divider()
name_target = st.sidebar.text_input("ชื่อคนที่จะสแกน (อนาคต/อดีต)", "เป้าหมาย")
d_target = st.sidebar.date_input(f"วันเกิดของ {name_target}", value=date(1996, 8, 17))

# ==========================================
# 1️⃣ คำนวณรหัสชีวิตชุดที่ 1 (ของพี่บาส)
# ==========================================
ref_date = date(1900, 1, 1)
diff1 = (d_me - ref_date).days
lunar_cycle = 29.530589
pos1 = (diff1 - 0.5) % lunar_cycle
v1 = d_me.weekday() + 1 # จันทร์=1-อาทิตย์=7

if pos1 <= 14.765: # ข้างขึ้น
    m1 = int(pos1) + 1
    lab1 = f"ขึ้น {m1} ค่ำ"
    op1 = "บวก" if 1 <= m1 <= 7 else "คูณ"
else: # ข้างแรม
    m1 = int(pos1 - 14.765) + 1
    lab1 = f"แรม {m1} ค่ำ"
    op1 = "ลบ" if 1 <= m1 <= 7 else "หาร"

# ผลลัพธ์ดวงหลัก
if op1 == "บวก": res1 = v1 + m1
elif op1 == "คูณ": res1 = v1 * m1
elif op1 == "ลบ": res1 = v1 - m1
else: res1 = v1 / m1 if m1 != 0 else 0

# ==========================================
# 2️⃣ คำนวณรหัสชีวิตชุดที่ 2 (ของเป้าหมาย)
# ==========================================
diff2 = (d_target - ref_date).days
pos2 = (diff2 - 0.5) % lunar_cycle
v2 = d_target.weekday() + 1

if pos2 <= 14.765: # ข้างขึ้น
    m2 = int(pos2) + 1
    lab2 = f"ขึ้น {m2} ค่ำ"
    op2 = "บวก" if 1 <= m2 <= 7 else "คูณ"
else: # ข้างแรม
    m2 = int(pos2 - 14.765) + 1
    lab2 = f"แรม {m2} ค่ำ"
    op2 = "ลบ" if 1 <= m2 <= 7 else "หาร"

# ผลลัพธ์ดวงเปรียบเทียบ
if op2 == "บวก": res2 = v2 + m2
elif op2 == "คูณ": res2 = v2 * m2
elif op2 == "ลบ": res2 = v2 - m2
else: res2 = v2 / m2 if m2 != 0 else 0

# ==========================================
# 3️⃣ สรุปผลลัพธ์รวม (ตารางที่พี่บาสต้องการ)
# ==========================================
plus_val = res1 + res2
minus_val = res1 - res2
multi_val = res1 * res2
div_val = res1 / res2 if res2 != 0 else 0

# ==========================================
# 4️⃣ วิเคราะห์ระยะห่างเวลา (Time Analysis)
# ==========================================
delta_days = abs((d_me - d_target).days)
yy = delta_days // 365
mm = (delta_days % 365) // 30
dd = (delta_days % 365) % 30
direction = "ก่อนหน้าคุณ" if d_target < d_me else "หลังคุณ"

# ==========================================
# 🚀 การแสดงผลหน้าแอป (UI)
# ==========================================
st.title("🛰️ SYNAPSE v15.2: THE OMNI-REVEALER")
st.write(f"ระบบวิเคราะห์ความจริงเชิงลึก | ผู้สร้าง: **Ta101**")

st.divider()
c1, c2 = st.columns(2)
with c1:
    st.subheader(f"👤 {name_me}")
    st.info(f"วัน {v1} | {lab1} (ใช้ {op1})")
    st.metric("ค่าสมการหลัก", f"{res1:.2f}")

with c2:
    st.subheader(f"👤 {name_target}")
    st.warning(f"วัน {v2} | {lab2} (ใช้ {op2})")
    st.metric("ค่าสมการเปรียบเทียบ", f"{res2:.2f}")

st.divider()
st.subheader("📊 ตารางสรุปผลลัพธ์รวม (Mathematical Summary)")
df = pd.DataFrame({
    "เงื่อนไขการรวมข้อมูล": ["บวกกัน (+)", "ลบกัน (-)", "คูณกัน (×)", "หารกัน (÷)"],
    "ผลลัพธ์สุดท้าย": [f"{plus_val:.2f}", f"{minus_val:.2f}", f"{multi_val:.2f}", f"{div_val:.2f}"]
})
st.table(df)

st.divider()
st.subheader("🔮 วิเคราะห์รหัสคู่ขนานและวงโคจรเวลา")

# เช็ค Gap 4 ที่พี่บาสเจอ
gap = abs(res1 - res2)
is_gap4 = 3.8 <= gap <= 4.2

# เช็กพิกัด 6 ปี และ 12 ปี
is_cycle = (5 <= yy <= 7) or (11 <= yy <= 13)

col_out1, col_out2 = st.columns([2,1])
with col_out1:
    if is_gap4:
        st.error(f"‼️ ตรวจพบรหัสคู่ขนาน! ค่าห่างกัน {gap:.2f} (พิกัด Gap 4 เหมือนแฟนเก่า)")
        st.balloons()
    else:
        st.success(f"✅ ไม่พบรหัสคู่ขนานเดิม (รหัสห่าง {gap:.2f})")
    
    st.write("---")
    if is_cycle:
        st.warning(f"🎯 พิกัดเวลาสำคัญ: ห่างกัน {yy} ปี (เข้าข่ายรหัส 6/12 ปี)")
    else:
        st.write(f"ระยะห่างเวลา: {yy} ปี {mm} เดือน {dd} วัน ({direction})")

with col_out2:
    st.metric("GAP ตัวเลข", f"{gap:.2f}")
    st.metric("รวมระยะห่างวัน", f"{delta_days:,} วัน")

st.divider()
st.caption("สโลแกน: 'อยู่นิ่งๆ ไม่เจ็บตัว' | ID: Ta101/102 | ความจริงเปิดเผยที่นี่")
