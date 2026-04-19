import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import math

# --- CONFIG & NEON STYLE ---
st.set_page_config(page_title="SYNAPSE CORE v3.0", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: #00e5ff; }
    .stApp { background: radial-gradient(circle, #101a24 0%, #050a0e 100%); }
    
    /* กล่องแสดงที่มาตัวเลข */
    .formula-card {
        background: rgba(0, 229, 255, 0.05);
        border: 1px solid #00e5ff;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.2);
    }
    
    /* สีสันตามสถานะ Gap */
    .gap-twin { color: #00ff41; font-weight: bold; text-shadow: 0 0 10px #00ff41; } /* บรรจบ */
    .gap-parallel { color: #ff007f; font-weight: bold; text-shadow: 0 0 10px #ff007f; } /* คู่ขนาน 4 */
    .gap-indie { color: #7000ff; font-weight: bold; } /* อิสระ */
    
    h1, h2, h3 { color: #ffffff; text-transform: uppercase; letter-spacing: 2px; }
    code { color: #ff7f50 !important; font-size: 1.1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- CORE LOGIC (ที่มาของความจริง) ---
def get_detailed_logic(dt):
    if dt is None: return None
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    
    # ลำดับวัน จันทร์=1 ... ศุกร์=5 ... อาทิตย์=7
    day_val = dt.weekday() + 1
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    
    is_waxing = pos <= 14.765
    m_num = int(pos) + 1 if is_waxing else int(pos - 14.765) + 1
    
    if is_waxing:
        res = math.sqrt((day_val**2) + (m_num**2))
        logic_desc = f"แรงผลักดัน (Vector): √({day_val}² + {m_num}²)"
        phase_text = f"ขึ้น {m_num} ค่ำ"
    else:
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        logic_desc = f"สัดส่วนทองคำ (Golden): ({day_val} × 1.618) / {m_num}"
        phase_text = f"แรม {m_num} ค่ำ"

    return {
        "res": round(res, 4), "phase": phase_text, "day_name": day_names[dt.weekday()],
        "day_val": day_val, "m_num": m_num, "formula": logic_desc, "is_waxing": is_waxing
    }

# --- FUNCTION: SCANNER ---
def scan_timeline(target_res, start_dt, days=180, direction="future"):
    data = []
    for i in range(days):
        current_date = start_dt + timedelta(days=i) if direction == "future" else start_dt - timedelta(days=i)
        d = get_detailed_logic(current_date)
        gap = abs(d['res'] - target_res)
        
        status = ""
        if gap < 0.5: status = "💎 บรรจบ (Meet)"
        elif 3.8 <= gap <= 4.2: status = "🌀 สะท้อน (Gap 4)"
        elif gap > 10.0: status = "🚩 แยกตัว (Away)"
        
        if status:
            data.append({"วันที่": current_date, "พิกัด": d['day_name'], "สถานะ": status, "Gap": round(gap, 4)})
    return pd.DataFrame(data)

# --- MAIN UI ---
st.title("🛰️ SYNAPSE : รหัสคู่ขนานแห่งความจริง")

# ส่วนที่ 1: ตรวจสอบพิกัดบุคคล
c1, c2 = st.columns(2)
with c1:
    dob1 = st.date_input("วันเกิดเจ้านาย (1)", value=date(1984, 5, 18))
    d1 = get_detailed_logic(dob1)
    if d1:
        st.markdown(f"""<div class="formula-card">
            <h3>👤 รหัสเจ้านาย: {d1['res']}</h3>
            <p>📍 {d1['day_name']} | {d1['phase']}</p>
            <p>🧬 <b>ที่มาตัวเลข:</b> <code>{d1['formula']}</code></p>
        </div>""", unsafe_allow_html=True)

with c2:
    dob2 = st.date_input("วันเกิดคู่สแกน (2)", value=date(1996, 8, 17))
    d2 = get_detailed_logic(dob2)
    if d2:
        st.markdown(f"""<div class="formula-card">
            <h3>👥 รหัสคู่สแกน: {d2['res']}</h3>
            <p>📍 {d2['day_name']} | {d2['phase']}</p>
            <p>🧬 <b>ที่มาตัวเลข:</b> <code>{d2['formula']}</code></p>
        </div>""", unsafe_allow_html=True)

# ส่วนที่ 2: วิเคราะห์ Gap ปัจจุบัน
if d1 and d2:
    gap = abs(d1['res'] - d2['res'])
    st.divider()
    st.markdown(f"<h2 style='text-align:center;'>ระยะห่างรหัส (GAP): {gap:.4f}</h2>", unsafe_allow_html=True)
    
    if 3.8 <= gap <= 4.2:
        st.markdown("<h1 style='text-align:center; color:#ff007f;'>🌀 รหัสคู่ขนาน (PARALLEL)</h1>", unsafe_allow_html=True)
        st.balloons()
    else:
        st.markdown(f"<p style='text-align:center;'>สถานะ: {'รหัสบรรจบ' if gap < 1 else 'รหัสอิสระ'}</p>", unsafe_allow_html=True)

# ส่วนที่ 3: ระบบทายย้อนหลัง & อนาคต
tab1, tab2 = st.tabs(["🔮 พยากรณ์ 180 วันข้างหน้า", "⏪ สแกนความจริงในอดีต"])

with tab1:
    st.write("ค้นหาจังหวะที่รหัสวันจะวิ่งมาทำมุมกับคุณ...")
    df_future = scan_timeline(d1['res'], date.today(), 180, "future")
    st.dataframe(df_future, use_container_width=True)

with tab2:
    check_date = st.date_input("เลือกวันสำคัญในอดีต", value=date(2024, 1, 1))
    d_past = get_detailed_logic(check_date)
    past_gap = abs(d1['res'] - d_past['res'])
    
    st.write(f"วิเคราะห์วันที่: {check_date.strftime('%d/%m/%Y')}")
    st.markdown(f"""<div class="formula-card">
        <b>รหัสวันนั้น: {d_past['res']}</b> | <b>Gap กับคุณ: {past_gap:.4f}</b><br>
        สูตรคำนวณวันนั้น: <code>{d_past['formula']}</code>
    </div>""", unsafe_allow_html=True)

st.caption(f"สโลแกน: 'อยู่นิ่งๆ ไม่เจ็บตัว' | SYNAPSE v3.0 | {date.today().year}")
