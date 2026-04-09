import streamlit as st
import pandas as pd
from datetime import datetime, date
import itertools
import random

# --- CONFIG & UI ---
st.set_page_config(page_title="SYNAPSE v19.2: FULL RANGE SCANNER", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b1016; color: #f0f0f0; }
    .stMetric { background-color: #1a222d; padding: 20px; border-radius: 15px; border: 1px solid #00ff41; }
    h1, h2, h3 { color: #00ff41; text-shadow: 1px 1px #000; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #00ff41; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- CORE LOGIC ---
def get_lunar_data(dt):
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

# --- SIDEBAR ---
st.sidebar.header("🕹️ SYNAPSE COMMAND")
app_mode = st.sidebar.selectbox("🎯 เมนูหลัก", ["🔍 สแกนรหัสคู่ขนาน", "🎰 คำนวณเลขเด็ด", "🔮 ไพ่ยิปซี"])

# --- MAIN APP ---
st.title(f"🛰️ SYNAPSE: {app_mode}")

if app_mode == "🔍 สแกนรหัสคู่ขนาน":
    st.write("📍 ปรับปรุง: รองรับการสแกนข้อมูลตั้งแต่ปี 1960 - 2026 เรียบร้อยแล้ว")
    
    col1, col2 = st.columns(2)
    
    # กำหนดช่วงวันที่ให้กว้าง (1960 - 2026+)
    min_d = date(1960, 1, 1)
    max_d = date(2026, 12, 31)
    
    with col1:
        st.subheader("👤 ข้อมูลฝั่งที่ 1")
        name1 = st.text_input("ชื่อ (1)", "คุณ A")
        # ใส่ min_value และ max_value เพื่อปลดล็อกช่วงปี
        dob1 = st.date_input("เลือกวันเกิด (1)", 
                            value=date(1984, 5, 18), 
                            min_value=min_d, 
                            max_value=max_d)
        
    with col2:
        st.subheader("👤 ข้อมูลฝั่งที่ 2")
        name2 = st.text_input("ชื่อ (2)", "คุณ B")
        dob2 = st.date_input("เลือกวันเกิด (2)", 
                            value=date(1996, 8, 17), 
                            min_value=min_d, 
                            max_value=max_d)

    # ประมวลผลรหัส
    v1, m1, op1, lab1, res1 = get_lunar_data(dob1)
    v2, m2, op2, lab2, res2 = get_lunar_data(dob2)

    st.divider()
    c1, c2 = st.columns(2)
    c1.metric(f"รหัส {name1}", f"{res1:.2f}")
    c2.metric(f"รหัส {name2}", f"{res2:.2f}")

    st.divider()
    st.subheader("📊 ตารางผลลัพธ์คณิตศาสตร์")
    df = pd.DataFrame({
        "สมการ": ["บวก (+)", "ลบ (-)", "คูณ (×)", "หาร (÷)"],
        "ผลลัพธ์": [f"{res1+res2:.2f}", f"{res1-res2:.2f}", f"{res1*res2:.2f}", f"{res1/res2 if res2!=0 else 0:.2f}"]
    })
    st.table(df)

    gap = abs(res1 - res2)
    if 3.8 <= gap <= 4.2:
        st.error(f"‼️ ตรวจพบรหัสคู่ขนาน! (Gap {gap:.2f})")
        st.balloons()
    else:
        st.success(f"✅ ไม่พบรหัสซ้ำเดิม (Gap {gap:.2f})")

elif app_mode == "🎰 คำนวณเลขเด็ด":
    u_dob = st.date_input("วันเกิดของคุณ", value=date(1984, 5, 18), min_value=date(1960, 1, 1))
    l_date = st.date_input("งวดหวยออก", value=date.today())
    _, _, _, _, r_u = get_lunar_data(u_dob)
    _, _, _, _, r_l = get_lunar_data(l_date)
    res = r_u + r_l
    st.metric("รหัสโชคลาภ", f"{res:.2f}")
    pair = str(abs(round(res, 2))).replace('.', '')[-2:]
    st.success(f"🎯 เลขเด่น: {pair} - {pair[::-1]}")

st.divider()
st.caption("สโลแกน: 'อยู่นิ่งๆ ไม่เจ็บตัว' | Ta101 | ช่วงปีปัจจุบัน: 2026")
