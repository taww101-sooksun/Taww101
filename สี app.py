import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import math
import firebase_admin
from firebase_admin import credentials, db

# --- 1. การเชื่อมต่อความจริง (FIREBASE) ---
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(dict(st.secrets["firebase_credentials"]))
        firebase_admin.initialize_app(cred, {
            'databaseURL': st.secrets["firebase_db_url"]
        })
    except:
        pass # ถ้าเชื่อมไม่ได้ให้แอปยังทำงานต่อได้ (ไม่เจ็บตัว)

# --- 2. CONFIG & STYLE ---
st.set_page_config(page_title="SYNAPSE", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #050a0e; color: #00ff41; }
    .stMetric { background-color: #101a24; border: 1px solid #00ff41; border-radius: 10px; }
    h1, h2, h3 { color: #00ff41; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC สูตรหลัก (ที่เจ้านายวางไว้) ---
def get_logic(dt):
    if dt is None: return None
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    
    is_waxing = pos <= 14.765
    m_num = int(pos) + 1 if is_waxing else int(pos - 14.765) + 1
    
    if is_waxing:
        res = math.sqrt((day_val**2) + (m_num**2))
        type_text = "Vector (ขึ้น)"
    else:
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        type_text = "Ratio (แรม)"

    return {"res": round(res, 4), "phase": f"{'ขึ้น' if is_waxing else 'แรม'} {m_num} ค่ำ", "type": type_text}

# --- 4. หน้าจอหลัก ---
st.title("🛰️ SYNAPSE : สแกนพิกัดรหัสชีวิต")

# ช่องให้ผู้ใช้กรอกเอง (อิสระตามความจริง)
user_dob = st.date_input("📅 ระบุวันเดือนปีเกิดของคุณ", value=None)

if user_dob:
    u = get_logic(user_dob)
    my_code = u['res']
    
    col1, col2 = st.columns(2)
    col1.metric("รหัสประจำตัว", my_code)
    col2.metric("พิกัดจันทรคติ", u['phase'])

    st.divider()
    
    # สแกน 180 วัน (แบบที่เจ้านายชอบ)
    st.subheader("🗓️ ผลการสแกนพิกัด 180 วันข้างหน้า")
    
    results = []
    for i in range(180):
        d_check = date.today() + timedelta(days=i)
        l = get_logic(d_check)
        gap = abs(my_code - l['res'])
        
        status = ""
        if gap < 0.5: status = "💎 บรรจบ"
        elif 3.8 <= gap <= 4.2: status = "🌀 สะท้อน"
        
        if status:
            results.append({
                "วันที่": d_check.strftime("%d/%m/%Y"),
                "สถานะ": status,
                "Gap": round(gap, 4),
                "รหัสวัน": l['res']
            })
            # บันทึกข้อมูลพิกัดพิเศษลง Firebase อัตโนมัติ
            try:
                db.reference('/logs').push({
                    'user_code': my_code,
                    'found_date': str(d_check),
                    'status': status,
                    'timestamp': str(datetime.now())
                })
            except: pass

    if results:
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.write("ช่วงนี้รหัสเป็นอิสระ... 'อยู่นิ่งๆ ไม่เจ็บตัว'")

else:
    st.info("💡 กรุณาระบุวันเกิดเพื่อเริ่มการถอดรหัส")
