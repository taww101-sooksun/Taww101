import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import math

# --- CONFIG & STYLING ---
st.set_page_config(page_title="SYNAPSE : FULL CYCLE SCANNER", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050a0e; color: #00e5ff; }
    .stApp { background: linear-gradient(180deg, #050a0e 0%, #101a24 100%); }
    
    /* Neon Formula Card */
    .formula-box {
        background: rgba(0, 229, 255, 0.03);
        border-left: 5px solid #00e5ff;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Data Table Styling */
    .stDataFrame { border: 1px solid rgba(0, 229, 255, 0.2); border-radius: 10px; }
    
    h1, h2, h3 { color: #ffffff; text-shadow: 0 0 10px rgba(0, 229, 255, 0.5); }
    .highlight { color: #ff7f50; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- CORE LOGIC (สูตรที่ไม่มั่ว) ---
def get_synapse_logic(dt):
    if dt is None: return None
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    
    is_waxing = pos <= 14.765
    m_num = int(pos) + 1 if is_waxing else int(pos - 14.765) + 1
    
    if is_waxing:
        res = math.sqrt((day_val**2) + (m_num**2))
        formula = f"√({day_val}² + {m_num}²)"
        type_text = "Vector Energy (ขึ้น)"
    else:
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula = f"({day_val} × 1.618) / {m_num}"
        type_text = "Golden Ratio (แรม)"

    return {
        "res": round(res, 4), "phase": f"{'ขึ้น' if is_waxing else 'แรม'} {m_num} ค่ำ",
        "day": day_names[dt.weekday()], "formula": formula, "type": type_text
    }

def run_scanner(target_res, base_date, days, mode="future"):
    results = []
    for i in range(days + 1):
        current_date = base_date + timedelta(days=i) if mode == "future" else base_date - timedelta(days=i)
        d = get_synapse_logic(current_date)
        gap = abs(target_res - d['res'])
        
        status = "อิสระ"
        if gap < 0.5: status = "💎 บรรจบ"
        elif 3.8 <= gap <= 4.2: status = "🌀 สะท้อน (Gap 4)"
        elif gap > 10.0: status = "🚩 แยกตัว"
        
        if status != "อิสระ":
            results.append({
                "วันที่": current_date.strftime("%d/%m/%Y"),
                "วัน": d['day'],
                "สถานะพิกัด": status,
                "Gap": round(gap, 4),
                "รหัสวันนั้น": d['res']
            })
    return pd.DataFrame(results)

# --- MAIN INTERFACE ---
st.title("🛰️ SYNAPSE : ระบบสแกนวงจรชีวิต 365 วัน")
st.write("ตรวจสอบพิกัดรหัสย้อนหลังและล่วงหน้า 1 ปี เพื่อหาจังหวะที่ 'ตรง' กับคุณ")

# 1. ข้อมูลตั้งต้น
with st.container():
    st.subheader("👤 ข้อมูลผู้ใช้งาน")
    user_dob = st.date_input("เลือกวันเดือนปีเกิดของคุณ", value=None, min_value=date(1920,1,1))

if user_dob:
    user_data = get_synapse_logic(user_dob)
    st.markdown(f"""
        <div class="formula-box">
            <span style='font-size: 1.2rem;'>รหัสประจำตัวของคุณคือ: <b style='color:#00e5ff;'>{user_data['res']}</b></span><br>
            พิกัด: {user_data['day']} ({user_data['phase']}) | ระบบ: {user_data['type']}<br>
            ที่มาตัวเลข: <code>{user_data['formula']}</code>
        </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 2. ส่วนควบคุมการสแกน
    st.subheader("🔍 ตั้งค่าขอบเขตการสแกน")
    c1, c2 = st.columns(2)
    with c1:
        past_range = st.slider("สแกนย้อนหลัง (วัน)", 0, 365, 180)
    with c2:
        future_range = st.slider("สแกนไปข้างหน้า (วัน)", 0, 365, 180)

    # 3. ผลการสแกน
    tab_past, tab_future = st.tabs([f"⏪ อดีต ({past_range} วัน)", f"🔮 อนาคต ({future_range} วัน)"])

    with tab_past:
        df_p = run_scanner(user_data['res'], date.today(), past_range, "past")
        if not df_p.empty:
            st.write(f"พบพิกัดที่น่าสนใจในอดีต {len(df_p)} จุด")
            st.dataframe(df_p, use_container_width=True)
        else:
            st.write("ไม่พบพิกัดพิเศษในช่วงวันที่เลือก")

    with tab_future:
        df_f = run_scanner(user_data['res'], date.today(), future_range, "future")
        if not df_f.empty:
            st.write(f"พบพิกัดที่น่าสนใจในอนาคต {len(df_f)} จุด")
            st.dataframe(df_f, use_container_width=True)
        else:
            st.write("ไม่พบพิกัดพิเศษในช่วงวันที่เลือก")
            
else:
    st.info("💡 กรุณาระบุวันเกิดของคุณเพื่อเริ่มการสแกนพิกัดย้อนหลังและอนาคต")

st.caption("สโลแกน: 'อยู่นิ่งๆ ไม่เจ็บตัว' | SYNAPSE ENGINE v3.2")
