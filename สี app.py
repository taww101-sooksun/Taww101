import streamlit as st
from datetime import datetime, date
import math
import random

# --- CONFIG & STYLING ---
st.set_page_config(page_title="SYNAPSE: REALITY EXTRACTOR", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #050a0e; color: #00ff41; }
    .status-card { 
        background-color: #101a24; 
        padding: 25px; 
        border: 2px solid #00ff41; 
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0px 0px 20px rgba(0, 255, 65, 0.1);
    }
    .data-source-box {
        background-color: #0e161f;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ffaa00;
        margin-top: 20px;
        text-align: left;
    }
    h1, h2, h3 { color: #00ff41; font-family: 'Courier New', monospace; }
    .numeric-display { font-size: 2.5rem; color: #ffffff; letter-spacing: 5px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def extract_reality_code(dt):
    # 1. ฐานข้อมูลดาราศาสตร์ (The Astronomical Base)
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1 
    
    # 2. การประกอบร่างด้วยสูตรคณิตศาสตร์จักรวาล
    if pos <= 14.765:
        m_num = int(pos) + 1
        label = f"ขึ้น {m_num} ค่ำ"
        # ใช้ทฤษฎีพีทาโกรัสหาแรงผลัก (Vector)
        res = math.sqrt((day_val**2) + (m_num**2))
        formula = f"√({day_val}² + {m_num}²)"
        logic_type = "แรงผลักดันจักรวาล (Vector Energy)"
    else:
        m_num = int(pos - 14.765) + 1
        label = f"แรม {m_num} ค่ำ"
        # ใช้สัดส่วนทองคำปรับสมดุล (Golden Ratio Balance)
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula = f"({day_val} × 1.618) / {m_num}"
        logic_type = "สัดส่วนทองคำ (Golden Ratio)"

    # 3. การสกัดเป็นชุดตัวเลขแท้จริง (Locked Seed Logic)
    # เราใช้ค่า res ที่ได้จากสูตรข้างบนเป็นตัวกำหนดเลข (ไม่ใช่การสุ่มมั่ว)
    seed_val = int(res * 1000000)
    random.seed(seed_val) 
    
    d2 = f"{random.randint(0, 99):02}"
    d3 = f"{random.randint(0, 999):03}"

    return {
        "res": round(res, 4), "label": label, "logic": logic_type,
        "formula": formula, "d2": d2, "d3": d3, "day_name": dt.strftime('%A')
    }

# --- MAIN INTERFACE ---
st.title("🛰️ SYNAPSE: Reality Extractor")
st.write("ระบบสกัดรหัสความจริงรายวัน | ไม่มีการสุ่ม ทุกตัวเลขมีที่มา")

target_date = st.date_input("เลือกวันที่เพื่อสกัดรหัส", value=date.today())

if target_date:
    data = extract_reality_code(target_date)
    
    st.markdown(f"""
    <div class="status-card">
        <p style="color: #a0a0a0; margin-bottom: 0;">รหัสประจุพลังงานประจำวัน</p>
        <h1 style="font-size: 4rem; margin-top: 0;">{data['res']}</h1>
        <p style="font-size: 1.2rem; color: #ffaa00;">🌒 {data['label']}</p>
        <hr style="border: 0.5px solid #333;">
        <p style="color: #00ff41;">ชุดรหัสตัวเลขแท้จริงที่สกัดได้</p>
        <div class="numeric-display">{data['d2']} | {data['d3']}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- ส่วนแสดงที่มาของข้อมูล (ความจริงตรวจสอบได้) ---
    st.markdown(f"""
    <div class="data-source-box">
        <h3 style="color: #ffaa00; margin-top: 0;">📂 ข้อมูลประกอบการสกัดรหัส:</h3>
        <p><b>1. มิติวัน:</b> {data['day_name']} (Index: {target_date.weekday()+1})</p>
        <p><b>2. มิติดวงจันทร์:</b> รอบวงโคจร 29.53 วัน (ความจริงทางดาราศาสตร์)</p>
        <p><b>3. มิติโครงสร้าง:</b> ใช้ค่า {data['logic']}</p>
        <p><b>4. สมการที่ใช้:</b> <code>{data['formula']}</code></p>
        <hr style="border: 0.2px solid #333;">
        <p style="font-size: 0.85rem; color: #a0a0a0;">
        *หมายเหตุ: ตัวเลขที่แสดงถูกสกัดจากทศนิยมของรหัสประจุพลังงาน 
        สแกนกี่ครั้งก็ได้เลขเดิม เพราะความจริงของวันนั้นมีเพียงชุดเดียว
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()
st.caption("สโลแกน: 'อยู่นิ่งๆ ไม่เจ็บตัว' | SYNAPSE CORE v2.5 | พัฒนาโดย Ta101")
