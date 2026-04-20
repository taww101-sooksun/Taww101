import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import math
import firebase_admin
from firebase_admin import credentials, db

# --- 1. INITIALIZE FIREBASE (เชื่อมต่อฐานข้อมูลความจริง) ---
if not firebase_admin._apps:
    try:
        # ดึงค่าจาก st.secrets ที่เจ้านายวางไว้แล้ว
        cred_dict = dict(st.secrets["firebase_credentials"])
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': st.secrets["firebase_db_url"]
        })
    except Exception as e:
        st.error(f"Firebase Connect Error: {e}")

# --- 2. CONFIG & STYLING (สไตล์ Dark Neon) ---
st.set_page_config(page_title="SYNAPSE X : THE TRUTH ENGINE", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050a0e; color: #00ff41; }
    .logic-box { 
        background-color: #101a24; padding: 15px; border-left: 5px solid #00ff41; 
        border-radius: 10px; margin-bottom: 20px; color: #f0f0f0;
    }
    h1, h2, h3 { color: #00ff41; text-shadow: 0 0 10px rgba(0, 255, 65, 0.3); }
    .stMetric { background-color: #0e161f; border: 1px solid #00ff41; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. CORE LOGIC (สูตรที่ไม่มั่ว: 7.5 & Golden Ratio) ---
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
    
    # จุดสมดุล 7.5 ที่เจ้านายบอก
    balance_point = m_num - 7.5
    
    if is_waxing:
        res = math.sqrt((day_val**2) + (m_num**2))
        formula = f"√({day_val}² + {m_num}²)"
        type_text = "Vector (ขึ้น)"
    else:
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula = f"({day_val} × 1.618) / {m_num}"
        type_text = "Golden Ratio (แรม)"

    return {
        "res": round(res, 4), "phase": f"{'ขึ้น' if is_waxing else 'แรม'} {m_num} ค่ำ",
        "day": day_names[dt.weekday()], "formula": formula, "type": type_text,
        "balance": round(balance_point, 2)
    }

# ฟังก์ชันบันทึกความจริงลง Firebase
def save_to_firebase(tag, data):
    try:
        ref = db.reference(f'/synapse_logs/{tag}')
        data['timestamp'] = str(datetime.now())
        ref.push(data)
    except:
        pass

# --- 4. MAIN INTERFACE ---
st.title("🛰️ SYNAPSE X : ระบบสแกนความจริง")
st.write(f"ID: Ta101 | พิกัดปัจจุบัน: {date.today()} | คติ: 'อยู่นิ่งๆ ไม่เจ็บตัว'")

# ส่วนรับข้อมูล
with st.expander("👤 ตั้งค่ารหัสตัวตน (สแกนหลัก)", expanded=True):
    user_dob = st.date_input("เลือกวันเกิดของคุณ", value=date(1996, 8, 17), key="main_dob")

if user_dob:
    u_data = get_synapse_logic(user_dob)
    my_code = u_data['res']
    
    col1, col2, col3 = st.columns(3)
    col1.metric("รหัสประจำตัว", my_code)
    col2.metric("พิกัดจันทรคติ", u_data['phase'])
    col3.metric("จุดสมดุล (7.5)", u_data['balance'])

    # --- ฟังก์ชันสแกนคู่ขนาน (Real-time Scan) ---
    st.divider()
    st.subheader("🔍 สแกนพิกัดคู่ขนาน (เทียบรหัสบุคคล/วัน)")
    target_date = st.date_input("เลือกวันที่ต้องการสแกนพิกัด", date.today())
    
    if target_date:
        t_data = get_synapse_logic(target_date)
        gap = abs(my_code - t_data['res'])
        
        st.write(f"**พิกัดวันที่เช็ค:** {t_data['day']} ({t_data['phase']}) | รหัสวัน: {t_data['res']}")
        
        if gap < 0.5:
            st.success(f"💎 **พิกัดบรรจบ (Gap: {gap:.4f})** - ความจริงมาบรรจบกัน")
            save_to_firebase("match", {"user_code": my_code, "target_date": str(target_date), "gap": gap})
        elif 3.8 <= gap <= 4.2:
            st.warning(f"🌀 **พิกัดสะท้อน (Gap: {gap:.4f})** - แรงดึงดูดกงจักร")
            save_to_firebase("reflect", {"user_code": my_code, "target_date": str(target_date), "gap": gap})
        else:
            st.info(f"อิสระ (Gap: {gap:.4f})")

    # --- ฟังก์ชันสแกน 365 วัน (Timeline Scan) ---
    st.divider()
    st.subheader("🗓️ สแกนวงจรล่วงหน้า 180 วัน")
    
    scan_results = []
    for i in range(180):
        d_check = date.today() + timedelta(days=i)
        logic = get_synapse_logic(d_check)
        g = abs(my_code - logic['res'])
        
        status = ""
        if g < 0.5: status = "💎 บรรจบ"
        elif 3.8 <= g <= 4.2: status = "🌀 สะท้อน"
        
        if status:
            scan_results.append({
                "วันที่": d_check.strftime("%d/%m/%Y"),
                "สถานะ": status,
                "Gap": round(g, 4),
                "รหัสวัน": logic['res']
            })
    
    if scan_results:
        st.dataframe(pd.DataFrame(scan_results), use_container_width=True)
    else:
        st.write("ไม่พบพิกัดพิเศษในช่วง 180 วันนี้")

st.divider()
st.caption("SYNAPSE CORE v3.5 | Powered by Firebase | 'ความจริงที่พิสูจน์ได้ด้วยตัวเลข'")
