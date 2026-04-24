import streamlit as st
import datetime
from datetime import date, timedelta
import math
import hashlib

# =================================================================
# 1. SETUP & CONFIG
# =================================================================
st.set_page_config(page_title="SYNAPSE ULTIMATE", layout="wide")

if 'page' not in st.session_state: st.session_state.page = "HOME"
if 'main_color' not in st.session_state: st.session_state.main_color = "#00f3ff"
if 'sub_color' not in st.session_state: st.session_state.sub_color = "#ff00de"
if 'user' not in st.session_state: st.session_state.user = "AGENT_X"

# =================================================================
# 2. INTELLIGENCE ENGINE (สูตรคำนวณ 6 พิกัดของคุณต๊ะ)
# =================================================================
def get_synapse_report(dt):
    if dt is None: return None
    
    # พิกัด 1: วัน (อาทิตย์=7, จันทร์=1, ..., ศุกร์=5, เสาร์=6)
    day_map = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7}
    d_val = day_map[dt.weekday()]
    d_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    
    # พิกัด 2: วันที่
    dt_val = dt.day
    
    # พิกัด 3: เดือน
    m_val = dt.month
    m_names = ["", "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
    
    # พิกัด 4: ข้างขึ้นแรม (ลอจิก ± 7.5)
    ref = date(1900, 1, 1)
    diff = (dt - ref).days
    lunar_pos = (diff - 0.5) % 29.530589
    if lunar_pos <= 14.765:
        moon_num = int(lunar_pos) + 1
        phase_text = f"ขึ้น {moon_num} ค่ำ"
        l_logic = -7.5
        l_logic_txt = "ลบ 7.5"
    else:
        moon_num = int(lunar_pos - 14.765) + 1
        phase_text = f"แรม {moon_num} ค่ำ"
        l_logic = 7.5
        l_logic_txt = "บวก 7.5"

    # พิกัด 5: ปีนักษัตร
    z_names = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
    z_map = {"ชวด":1, "ฉลู":2, "ขาล":3, "เถาะ":4, "มะโรง":5, "มะเส็ง":6, "มะเมีย":7, "มะแม":8, "วอก":9, "ระกา":10, "จอ":11, "กุน":12}
    z_name = z_names[dt.year % 12]
    zv = z_map.get(z_name, 1)

    # พิกัด 6: ธาตุ และ ราศี (ดิน=1, น้ำ=2, ลม=3, ไฟ=4)
    m, d = dt.month, dt.day
    if (m == 4 and d >= 13) or (m == 5 and d <= 13): rasi, et, ev = "เมษ", "ไฟ", 4
    elif (m == 5 and d >= 14) or (m == 6 and d <= 14): rasi, et, ev = "พฤษภ", "ดิน", 1
    elif (m == 6 and d >= 15) or (m == 7 and d <= 15): rasi, et, ev = "เมถุน", "ลม", 3
    elif (m == 7 and d >= 16) or (m == 8 and d <= 16): rasi, et, ev = "กรกฎ", "น้ำ", 2
    elif (m == 8 and d >= 17) or (m == 9 and d <= 16): rasi, et, ev = "สิงห์", "ไฟ", 4
    elif (m == 9 and d >= 17) or (m == 10 and d <= 16): rasi, et, ev = "กันย์", "ดิน", 1
    elif (m == 10 and d >= 17) or (m == 11 and d <= 15): rasi, et, ev = "ตุลย์", "ลม", 3
    elif (m == 11 and d >= 16) or (m == 12 and d <= 15): rasi, et, ev = "พิจิก", "น้ำ", 2
    elif (m == 12 and d >= 16) or (m == 1 and d <= 14): rasi, et, ev = "ธนู", "ไฟ", 4
    elif (m == 1 and d >= 15) or (m == 2 and d <= 12): rasi, et, ev = "มังกร", "ดิน", 1
    elif (m == 2 and d >= 13) or (m == 3 and d <= 13): rasi, elem_text, elem_val = "กุมภ์", "ลม", 3
    else: rasi, et, ev = "มีน", "น้ำ", 2

    # สูตรคำนวณรหัสลับ
    base_sum = d_val + dt_val + moon_num + m_val + zv + ev
    final_code = (base_sum + l_logic) * 1.618

    # ส่งค่ากลับ (Keys ต้องตรงกับที่เรียกใช้ใน UI)
    return {
        "day": d_names[dt.weekday()],
        "day_val": d_val,
        "date": dt_val,
        "month": m_names[m_val],
        "month_val": m_val,
        "zodiac": z_name,
        "z_val": zv,
        "phase": phase_text,
        "l_logic_text": l_logic_txt,
        "elem": et,
        "e_val": ev,
        "rasi": rasi,
        "code": round(final_code, 4)
    }

# =================================================================
# 3. GLOBAL CSS
# =================================================================
st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden !important;}}
    .stApp {{background-color: #000; border: 1px solid {st.session_state.main_color};}}
    .neon-text {{color: {st.session_state.main_color}; text-shadow: 0 0 10px {st.session_state.main_color}; font-weight: bold;}}
    .stButton>button {{border: 1px solid {st.session_state.main_color}; background: transparent; color: white; border-radius: 10px;}}
    </style>
""", unsafe_allow_html=True)

# =================================================================
# 4. MAIN NAVIGATION
# =================================================================

# --- หน้าแรก HOME ---
if st.session_state.page == "HOME":
    st.markdown("<h1 class='neon-text' style='text-align:center;'>SYNAPSE HUB</h1>", unsafe_allow_html=True)
    st.write("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🎵 DJ STATION", use_container_width=True): 
            st.session_state.page = "1"; st.rerun()
    with c2:
        if st.button("🧠 INTELLIGENCE CENTER", use_container_width=True): 
            st.session_state.page = "3"; st.rerun()

# --- หน้า 1: DJ STATION (ตัวอย่าง) ---
elif st.session_state.page == "1":
    if st.button("⬅️ BACK"): st.session_state.page = "HOME"; st.rerun()
    st.write("### 🎧 DJ Station Mode")

# --- หน้า 3: INTELLIGENCE CENTER (ส่วนหลัก) ---
elif st.session_state.page == "3":
    if st.button("⬅️ BACK"): st.session_state.page = "HOME"; st.rerun()
    st.markdown("<h2 class='neon-text'>🧠 INTELLIGENCE ENGINE</h2>", unsafe_allow_html=True)
    
    # รับค่าวันที่ (1960 - 2026)
    target_dt = st.date_input("เลือกวันที่เพื่อสแกนพิกัด", 
                             value=date.today(),
                             min_value=date(1960,1,1),
                             max_value=date(2026,12,31))

    if st.button("RUN DECODER", use_container_width=True):
        res = get_synapse_report(target_dt)
        
        st.write("---")
        # รายงาน 7 หัวข้อ (แก้ Error บรรทัด 184 เรียบร้อย)
        st.markdown(f"""
        ### 📋 ผลการถอดรหัสพิกัด:
        * **วัน:** {res['day']} ({res['day_val']})
        * **วันที่:** {res['date']}
        * **เดือน:** {res['month']} ({res['month_val']})
        * **ปีนักษัตร:** {res['zodiac']} ({res['z_val']})
        * **ข้างขึ้น/แรม:** {res['phase']} ({res['l_logic_text']})
        * **ธาตุ:** {res['elem']} ({res['e_val']})
        * **ราศี:** {res['rasi']}
        """)
        
        st.markdown(f"""
            <div style="text-align:center; padding:20px; border:2px solid {st.session_state.main_color}; border-radius:15px; background:rgba(0,0,0,0.5);">
                <h1 style="color:{st.session_state.main_color}; margin:0;">CODE: {res['code']}</h1>
                <p style="color:gray;">LUNAR BALANCE 1.618</p>
            </div>
        """, unsafe_allow_html=True)
