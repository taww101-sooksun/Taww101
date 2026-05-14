import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import math

# --- CONFIG & UI ---
st.set_page_config(page_title="SYNAPSE: THE UNIFIED TRUTH", layout="wide")

# ปรับแต่ง Theme ให้ดูเป็น Cyber-Logic
st.markdown("""
    <style>
    .main { background-color: #050a0e; color: #00ff41; }
    .stApp { background: linear-gradient(180deg, #050a0e 0%, #0a1118 100%); }
    .logic-box { 
        background-color: #101a24; 
        padding: 20px; 
        border-left: 5px solid #00ff41; 
        border-radius: 12px;
        margin-bottom: 20px;
        color: #f0f0f0;
        box-shadow: 0 4px 15px rgba(0,255,65,0.1);
    }
    .metric-card {
        text-align: center;
        padding: 20px;
        border: 1px solid #00ff41;
        border-radius: 15px;
        background: rgba(0, 255, 65, 0.05);
    }
    h1, h2, h3 { color: #00ff41; font-family: 'Courier New', Courier, monospace; }
    code { color: #ff7f50; }
    </style>
    """, unsafe_allow_html=True)

# --- CORE ENGINE (ฟังก์ชันวิเคราะห์ความจริง) ---
def get_logic_core(dt):
    if dt is None: return None
    
    # 1. ฐานข้อมูลวันและเวลา
    ref_date = date(1900, 1, 1)
    diff_days = (dt - ref_date).days
    day_val = dt.weekday() + 1
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    
    # 2. คำนวณดิถีพระจันทร์ (Real Lunar Cycle)
    lunar_cycle = 29.530589
    pos = (diff_days - 0.5) % lunar_cycle
    is_waxing = pos <= 14.765
    m_num = int(pos) + 1 if is_waxing else int(pos - 14.765) + 1
    phase_text = f"{'ขึ้น' if is_waxing else 'แรม'} {m_num} ค่ำ"
    
    # 3. คำนวณรหัสผลลัพธ์ (The Resulting Code)
    if is_waxing:
        res = math.sqrt((day_val**2) + (m_num**2))
        formula = f"√({day_val}² + {m_num}²)"
        p_type = "Vector Energy (แรงผลักดัน)"
    else:
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula = f"({day_val} × 1.618) / {m_num}"
        p_type = "Golden Ratio (สมดุลทองคำ)"
        
    # 4. ข้อมูลเสริม (ธาตุและนักษัตร)
    thai_year = dt.year + 543
    zodiacs = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
    elements = {1: "ดิน", 2: "น้ำ", 3: "ไฟ", 4: "ลม", 5: "ทอง", 6: "น้ำ", 7: "ดิน"}
    
    return {
        "res": round(res, 4), "phase": phase_text, "day_name": day_names[dt.weekday()],
        "zodiac": zodiacs[thai_year % 12], "element": elements.get(day_val),
        "formula": formula, "type": p_type, "diff": diff_days
    }

# --- SCANNER ENGINE (ระบบสแกนหาช่วงเวลา) ---
def run_synapse_scan(target_res, base_date, range_days, direction="future"):
    scan_results = []
    for i in range(range_days + 1):
        curr_date = base_date + timedelta(days=i) if direction == "future" else base_date - timedelta(days=i)
        d = get_logic_core(curr_date)
        gap = abs(target_res - d['res'])
        
        status = ""
        if gap < 0.5: status = "💎 บรรจบ (Perfect Match)"
        elif 3.8 <= gap <= 4.2: status = "🌀 สะท้อน (Resonance)"
        elif gap > 10.0: status = "🚩 แยกตัว (Independence)"
        
        if status:
            scan_results.append({
                "วันที่": curr_date.strftime("%d/%m/%Y"),
                "วัน/เฟส": f"{d['day_name']} ({d['phase']})",
                "สถานะพิกัด": status,
                "Gap": round(gap, 4),
                "รหัสวัน": d['res']
            })
    return pd.DataFrame(scan_results)

# --- MAIN INTERFACE ---
st.title("🛰️ SYNAPSE : ระบบรวมศูนย์ความจริง")
st.write("การรวมสมการ Quantum Logic และพิกัดดาราศาสตร์เพื่อถอดรหัสรอยเท้าพลังงาน")

# ส่วนที่ 1: วิเคราะห์รหัสบุคคล
st.divider()
c1, c2 = st.columns([1, 1])

with c1:
    st.subheader("👤 ข้อมูลพื้นฐาน")
    user_dob = st.date_input("ระบุวันเกิดของคุณ", value=None, min_value=date(1940,1,1))
    
with c2:
    if user_dob:
        u = get_logic_core(user_dob)
        st.markdown(f"""
            <div class="metric-card">
                <small>รหัสประจำตัวของคุณ</small>
                <h1 style="font-size: 50px; margin: 0;">{u['res']}</h1>
                <code>{u['formula']}</code>
            </div>
        """, unsafe_allow_html=True)

if user_dob:
    u = get_logic_core(user_dob)
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("พิกัดวัน", u['day_name'], u['phase'])
    col_b.metric("ธาตุพื้นฐาน", u['element'])
    col_c.metric("ปีนักษัตร", u['zodiac'])

    # ส่วนที่ 2: ระบบสแกนวงจร (Timeline Scanner)
    st.divider()
    st.subheader("🔍 ระบบสแกนหาจังหวะชีวิต (Timeline Scanner)")
    
    past_days = st.slider("ย้อนหลัง (วัน)", 0, 365, 90)
    future_days = st.slider("ล่วงหน้า (วัน)", 0, 365, 180)
    
    t_past, t_future = st.tabs(["⏪ ตรวจสอบรอยเท้าในอดีต", "🔮 พยากรณ์พิกัดในอนาคต"])
    
    with t_past:
        df_past = run_synapse_scan(u['res'], date.today(), past_days, "past")
        if not df_past.empty:
            st.dataframe(df_past, use_container_width=True, hide_index=True)
        else:
            st.info("ไม่พบจุดบรรจบที่สำคัญในช่วงอดีตที่เลือก")
            
    with t_future:
        df_future = run_synapse_scan(u['res'], date.today(), future_days, "future")
        if not df_future.empty:
            st.dataframe(df_future, use_container_width=True, hide_index=True)
        else:
            st.info("ยังไม่พบพิกัดที่สอดคล้องในช่วงเวลาข้างหน้า")

    # ส่วนที่ 3: คัมภีร์อ่านค่า
    with st.expander("📖 ความหมายของสถานะพิกัด"):
        st.markdown("""
        *   **💎 บรรจบ:** วันที่ค่าพลังงานภายนอกตรงกับรหัสคุณ (Gap ใกล้ 0) เหมาะกับการตัดสินใจเรื่องสำคัญ
        *   **🌀 สะท้อน:** วันที่เกิดแรงเหวี่ยงของตัวเลข (Gap ใกล้ 4) มักเกิดเหตุการณ์ไม่คาดฝันหรือการพบเจอโดยบังเอิญ
        *   **🚩 แยกตัว:** วันที่พลังงานผลักออกจากกัน เหมาะกับการอยู่เงียบๆ หรือยุติปัญหาที่ค้างคา
        """)

else:
    st.info("กรุณาระบุวันเกิด เพื่อให้ระบบเชื่อมต่อฐานข้อมูลความจริง")

st.divider()
st.caption(f"สโลแกน: 'อยู่นิ่งๆ ไม่เจ็บตัว' | SYNAPSE INTEGRATED v4.0 | {date.today().year}")
