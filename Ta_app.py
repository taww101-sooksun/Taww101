import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import math

# --- CONFIG & UI ---
st.set_page_config(page_title="SYNAPSE: THE COMPLETE TRUTH", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050a0e; color: #00ff41; }
    .logic-box { 
        background-color: #101a24; 
        padding: 15px; 
        border-left: 5px solid #00ff41; 
        border-radius: 10px;
        margin-bottom: 20px;
        color: #f0f0f0;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.5);
    }
    .stMetric { background-color: #0e161f; border: 1px solid #00ff41; border-radius: 10px; }
    h1, h2, h3 { color: #00ff41; font-family: 'Courier New', Courier, monospace; }
    .guide-text { color: #a0a0a0; font-size: 0.9rem; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

# --- CORE LOGIC (ฟังก์ชันคำนวณ) ---
def get_detailed_logic(dt):
    # 1. ข้อมูลพื้นฐานทางดาราศาสตร์
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    day_name = day_names[dt.weekday()]

    # 2. คำนวณตาม Logic (ความจริงทางคณิตศาสตร์)
    if pos <= 14.765:
        m_num = int(pos) + 1
        phase = f"ขึ้น {m_num} ค่ำ"
        res = math.sqrt((day_val**2) + (m_num**2))
        formula = f"√({day_val}² + {m_num}²)"
        logic_type = "แรงผลักดัน (Vector Energy)"
    else:
        m_num = int(pos - 14.765) + 1
        phase = f"แรม {m_num} ค่ำ"
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula = f"({day_val} × 1.618) / {m_num}"
        logic_type = "สมดุลสัดส่วนทองคำ (Golden Ratio)"

    return {
        "res": round(res, 4), "phase": phase, "day_name": day_name,
        "day_val": day_val, "m_num": m_num, "formula": formula, "type": logic_type
    }

# --- FUTURE SCANNER (ฟังก์ชันพยากรณ์อนาคต) ---
def scan_destiny(target_res, days=180):
    future_data = []
    start_date = date.today()
    
    for i in range(days):
        current_date = start_date + timedelta(days=i)
        d = get_detailed_logic(current_date)
        current_gap = abs(d['res'] - target_res)
        
        status = ""
        if current_gap < 0.5: 
            status = "💎 วันที่รหัสบรรจบ (เจอ/รวมตัว)"
        elif 3.8 <= current_gap <= 4.2: 
            status = "🌀 วันที่สัญญาณสะท้อน (ดึงดูดสูง)"
        elif current_gap > 10.0: 
            status = "🚩 วันที่รหัสแยกตัว (จาก/อิสระ)"
        
        if status:
            future_data.append({
                "วันที่": current_date.strftime('%d/%m/%Y'),
                "พิกัดวัน": d['day_name'],
                "สถานะ": status,
                "ค่า Gap": round(current_gap, 4)
            })
            
    return pd.DataFrame(future_data)

# --- MAIN INTERFACE ---
st.title("🛰️ SYNAPSE: สแกนพิกัดรหัสคู่ขนาน")
st.write("ระบบวิเคราะห์ความถี่รหัสชีวิตรายบุคคลด้วยสมการ Quantum | ID: Ta101")

st.divider()

# ส่วนการกรอกข้อมูล
c1, c2 = st.columns(2)
with c1:
    st.subheader("👤 บุคคลที่ 1 (ตัวตั้งต้น)")
    dob1 = st.date_input("เลือกวันเกิด (1)", value=None, min_value=date(1960,1,1), max_value=date(2026,12,31), key="u1")
with c2:
    st.subheader("👤 บุคคลที่ 2 (คู่สแกน)")
    dob2 = st.date_input("เลือกวันเกิด (2)", value=None, min_value=date(1960,1,1), max_value=date(2026,12,31), key="u2")

if dob1 and dob2:
    d1 = get_detailed_logic(dob1)
    d2 = get_detailed_logic(dob2)

    # แสดงผลลัพธ์รายบุคคล
    res_a, res_b = st.columns(2)
    with res_a:
        st.metric("รหัสประจำตัว (1)", d1['res'])
        st.markdown(f"""<div class="logic-box"><b>📍 พิกัด:</b> {d1['day_name']} ({d1['phase']})<br><b>🧬 สูตร:</b> <code>{d1['formula']}</code><br><b>⚙️ ระบบ:</b> {d1['type']}</div>""", unsafe_allow_html=True)

    with res_b:
        st.metric("รหัสประจำตัว (2)", d2['res'])
        st.markdown(f"""<div class="logic-box"><b>📍 พิกัด:</b> {d2['day_name']} ({d2['phase']})<br><b>🧬 สูตร:</b> <code>{d2['formula']}</code><br><b>⚙️ ระบบ:</b> {d2['type']}</div>""", unsafe_allow_html=True)

    # --- การวิเคราะห์ Gap ปัจจุบัน ---
    st.divider()
    gap = abs(d1['res'] - d2['res'])
    st.subheader(f"🔍 ผลการวิเคราะห์ Gap ปัจจุบัน: {gap:.4f}")
    
    progress_val = min(gap / 15.0, 1.0) 
    st.progress(progress_val)

    if gap < 1.0:
        st.warning("🔮 **ระดับ: รหัสแฝด (Twin Code)**")
    elif 3.5 <= gap <= 4.5:
        st.error("⚠️ **ระดับ: รหัสคู่ขนาน (Parallel Connection)**")
        st.balloons()
    elif 7.0 <= gap <= 9.0:
        st.info("🌀 **ระดับ: รหัสส่งเสริม (Supporting Code)**")
    else:
        st.success("✅ **ระดับ: รหัสอิสระ (Independent Energy)**")

    # --- ส่วนที่เพิ่มใหม่: พยากรณ์พิกัดเวลาในอนาคต ---
    st.divider()
    st.subheader("🗓️ พยากรณ์พิกัดเวลา (180 วันข้างหน้า)")
    st.write(f"ค้นหาจังหวะชีวิตที่สอดคล้องกับรหัสประจำตัว: **{d1['res']}**")
    
    timeline_df = scan_destiny(d1['res'])
    
    if not timeline_df.empty:
        st.dataframe(timeline_df, use_container_width=True, hide_index=True)
    else:
        st.info("ยังไม่พบพิกัดที่สอดคล้องในช่วง 180 วันนี้")

    # --- คัมภีร์อ่านค่า ---
    st.divider()
    with st.expander("📖 คัมภีร์ถอดรหัสความจริง", expanded=False):
        st.markdown("""
        * **วันที่จะเจอ (รหัสบรรจบ):** คือวันที่รหัสจักรวาลวิ่งมาทับกับรหัสคุณพอดี
        * **วันที่จะจาก (รหัสแยกตัว):** คือวันที่พลังงานดีดตัวออกจากกันจนเป็นอิสระ
        * **สัญญาณสะท้อน:** วันที่เกิดแรงดึงดูดประหลาด (Gap 4) มักมีเรื่องไม่คาดคิดเกิดขึ้น
        """)

else:
    st.info("🛰️ ระบบ Standby... กรุณากรอกข้อมูลวันเกิดเพื่อเริ่มการสแกนรหัสชีวิต")

st.divider()
st.caption(f"สโลแกน: 'อยู่นิ่งๆ ไม่เจ็บตัว' | SYNAPSE CORE v2.1 | {date.today().year}")
