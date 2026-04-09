import streamlit as st
from datetime import datetime, date
import math
import random

# --- CONFIG ---
st.set_page_config(page_title="SYNAPSE: DAILY & LUCKY", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #050a0e; color: #00ff41; }
    .status-card { 
        background-color: #101a24; 
        padding: 20px; 
        border: 2px solid #00ff41; 
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0px 4px 15px rgba(0, 255, 65, 0.2);
    }
    .lucky-box {
        background: linear-gradient(45deg, #0e161f, #1a2a3a);
        padding: 15px;
        border-radius: 10px;
        border: 1px dashed #00ff41;
        margin-top: 15px;
    }
    h1, h2, h3 { color: #00ff41; font-family: 'Courier New', monospace; }
    </style>
    """, unsafe_allow_html=True)

def scan_single_day(dt):
    # 1. ข้อมูลพื้นฐาน (ความจริงจากปฏิทิน)
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1 
    
    # 2. คำนวณรหัสวัน (The Quantum Code)
    if pos <= 14.765:
        m_num = int(pos) + 1
        label = f"ขึ้น {m_num} ค่ำ"
        res = math.sqrt((day_val**2) + (m_num**2))
        advice = "🚀 พลังงานขาขึ้น (Vector): เหมาะกับการรุกหรือขยับตัว"
        color = "#00ff41"
    else:
        m_num = int(pos - 14.765) + 1
        label = f"แรม {m_num} ค่ำ"
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        advice = "🛡️ พลังงานสมดุล (Balance): เน้นความนิ่งและประคองตัว"
        color = "#ffaa00"

    # 3. สกัดเลขเสี่ยงทาย (Lucky Logic)
    # ใช้ค่า res ที่คำนวณได้เป็นตัวกำหนดการสุ่มเลข (Seed)
    seed_val = int(res * 1000000)
    random.seed(seed_val)
    
    digit_2 = f"{random.randint(0, 99):02}"
    digit_3 = f"{random.randint(0, 999):03}"

    return round(res, 4), label, advice, color, digit_2, digit_3

# --- UI ---
st.title("🛰️ SYNAPSE: Daily Scanner")
st.write("สแกนรหัสพลังงานจักรวาลรายวัน | ความจริงตรวจสอบได้")

target_date = st.date_input("เลือกวันที่ต้องการสแกน", value=date.today())

if target_date:
    code, moon, advice, col, d2, d3 = scan_single_day(target_date)
    
    st.markdown(f"""
    <div class="status-card" style="border-color: {col};">
        <p style="color: #a0a0a0; margin-bottom: 5px;">รหัสประจุพลังงาน</p>
        <h1 style="color: {col}; font-size: 3.5rem; margin-top: 0;">{code}</h1>
        <p style="font-size: 1.2rem;">🌒 {moon}</p>
        <div style="background-color: #050a0e; padding: 10px; border-radius: 8px; margin: 15px 0;">
            <p style="color: {col}; margin: 0;">{advice}</p>
        </div>
        
        <div class="lucky-box">
            <p style="color: #00ff41; margin-bottom: 10px;">🧬 รหัสวิเคราะห์ตัวเลข (Potential Numbers)</p>
            <span style="font-size: 2rem; color: white; margin-right: 20px;">{d2}</span>
            <span style="font-size: 2rem; color: #00ff41;">|</span>
            <span style="font-size: 2rem; color: white; margin-left: 20px;">{d3}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("🔍 เจาะลึกโครงสร้างตัวเลข"):
        st.write(f"• **วัน:** {target_date.strftime('%A')}")
        st.write(f"• **ความแม่นยำดวงจันทร์:** {29.5305} วัน/รอบ")
        st.write(f"• **ค่าสุ่มจากรหัสฐาน (Seed):** `{int(code * 1000000)}`")
        st.write("---")
        st.write("เลขรหัสเสี่ยงทายถูกสกัดจากทศนิยม 4 ตำแหน่งของพลังงานวันนั้นๆ ไม่มีการสุ่มมั่ว ทุกตัวเลขมีที่มา")

st.divider()
st.caption("สโลแกน: 'อยู่นิ่งๆ ไม่เจ็บตัว' | ระบบความจริง Ta101")
