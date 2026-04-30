import streamlit as st
import pandas as pd
from datetime import datetime, date
import math

# --- CONFIG & UI ---
st.set_page_config(page_title="SYNAPSE: THE TRUTH REVEALED", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050a0e; color: #00ff41; }
    .logic-box { 
        background-color: #101a24; 
        padding: 20px; 
        border-left: 5px solid #00ff41; 
        border-radius: 10px;
        margin-bottom: 20px;
        color: #f0f0f0;
    }
    .math-highlight { color: #00ff41; font-family: 'Courier New', monospace; font-weight: bold; }
    h1, h2, h3 { color: #00ff41; font-family: 'Courier New', Courier, monospace; }
    </style>
    """, unsafe_allow_html=True)

def get_detailed_logic(dt):
    # 1. ฐานข้อมูลเวลา (Data Origin)
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    
    # 2. รอบดวงจันทร์ (Lunar Cycle) - ค่าคงที่จริงทางดาราศาสตร์
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    
    # 3. ฐานวัน (Day Base) - จันทร์=1 ถึง อาทิตย์=7
    day_val = dt.weekday() + 1
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    day_name = day_names[dt.weekday()]

    # 4. การคำนวณแยกส่วน (Processing)
    if pos <= 14.765: # ช่วงข้างขึ้น
        m_num = int(pos) + 1
        phase = f"ขึ้น {m_num} ค่ำ"
        res = math.sqrt((day_val**2) + (m_num**2)) # สูตรพีทาโกรัสหาแรงลัพธ์ (Vector)
        formula = f"√({day_val}² + {m_num}²)"
        logic_type = "แรงผลักดัน (Vector Energy)"
    else: # ช่วงข้างแรม
        m_num = int(pos - 14.765) + 1
        phase = f"แรม {m_num} ค่ำ"
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1) # สัดส่วนทองคำ (Phi)
        formula = f"({day_val} × 1.618) / {m_num}"
        logic_type = "สมดุลสัดส่วนทองคำ (Golden Ratio)"

    return {
        "res": round(res, 4), "phase": phase, "day_name": day_name,
        "day_val": day_val, "m_num": m_num, "formula": formula, 
        "type": logic_type, "diff_days": diff
    }

# --- MAIN INTERFACE ---
st.title("🛰️ SYNAPSE : ระบบถอดรหัสความจริงดิจิทัล")
st.write("วิเคราะห์โครงสร้างตัวเลขจากวงโคจรดาราศาสตร์ 1950 - 2026")

st.divider()

# รับข้อมูล
dob = st.date_input("📅 เลือกวันเกิดที่ต้องการตรวจสอบความจริง", 
                   value=date(1990,1,1), 
                   min_value=date(1950,1,1), 
                   max_value=date(2026,12,31))

if dob:
    d = get_detailed_logic(dob)
    
    # แสดงผลรหัสหลัก
    st.metric(label="ค่าความสั่นสะเทือน (Resonance ID)", value=d['res'])
    
    # --- ส่วนการอธิบายที่มา (The Breakdown) ---
    st.subheader("🕵️ เจาะลึกที่มาของตัวเลข (Manual Breakdown)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="logic-box">
            <h3>1. ฐานข้อมูลเวลา (Time Origin)</h3>
            <ul>
                <li><b>นับจากจุดอ้างอิง:</b> 01/01/1900</li>
                <li><b>จำนวนวันที่ผ่านไป:</b> <span class="math-highlight">{d['diff_days']:,} วัน</span></li>
                <li><b>รอบดวงจันทร์:</b> <span class="math-highlight">29.53 วัน</span> (Synodic Month)</li>
                <li><b>ตำแหน่งปัจจุบัน:</b> วัน{d['day_name']} (ค่าพลังงาน = {d['day_val']})</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="logic-box">
            <h3>2. สภาวะจันทรคติ (Lunar State)</h3>
            <ul>
                <li><b>สถานะ:</b> {d['phase']}</li>
                <li><b>อิทธิพล:</b> {'แรงดึงดูดรวมตัว (Vector)' if 'ขึ้น' in d['phase'] else 'แรงกระจายสมดุล (Golden Ratio)'}</li>
                <li><b>สัดส่วนทองคำ:</b> <span class="math-highlight">1.618 (Phi)</span></li>
                <li><b>ค่าคงที่วงโคจร:</b> {d['m_num']}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # แสดงสมการความจริง
    st.markdown(f"""
    <div style="text-align:center; padding:30px; background:#001a00; border:2px dashed #00ff41; border-radius:15px;">
        <h2 style="margin:0;">🧮 สมการความจริง: <span style="color:#ffffff;">{d['formula']}</span></h2>
        <p style="color:#00ff41; margin-top:10px;">= {d['res']} (พิกัด {d['type']})</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    
    # คำอธิบายเพิ่มเติมสำหรับคนใช้งาน
    with st.expander("📝 ทำไมต้องใช้ตัวเลขเหล่านี้?"):
        st.write("""
        1. **29.53 (Lunar Cycle):** คือคาบการโคจรของดวงจันทร์รอบโลกที่ทำให้เกิดข้างขึ้นข้างแรมจริงๆ ซึ่งส่งผลต่อระดับน้ำและแรงดึงดูดในร่างกายมนุษย์
        2. **1.618 (Golden Ratio):** คือสัดส่วนที่สวยงามที่สุดในจักรวาล พบได้ตั้งแต่ในดอกไม้ไปจนถึงทางช้างเผือก เราใช้เพื่อหาจุดสมดุลของชีวิต
        3. **1950 - 2026:** ระบบรองรับข้อมูลย้อนหลังกว่า 70 ปี เพื่อให้ครอบคลุมถึงยุคบรรพบุรุษ จนถึงอนาคตอันใกล้
        """)

else:
    st.info("💡 กรุณาเลือกวันเกิดเพื่อเริ่มการถอดรหัส")

st.divider()
st.caption("สโลแกน: 'อยู่นิ่งๆ ไม่เจ็บตัว' | SYNAPSE ENGINE v20.3 | BASED ON RAW TRUTH")
