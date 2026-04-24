import streamlit as st
import datetime
import math
import hashlib
from datetime import date, timedelta

# =================================================================
# 1. SETUP & CONFIG (ป้องกัน Error บรรทัดแรกๆ)
# =================================================================
st.set_page_config(page_title="SYNAPSE ULTIMATE", layout="wide")

if 'page' not in st.session_state: st.session_state.page = "HOME"
if 'main_color' not in st.session_state: st.session_state.main_color = "#00f3ff"
if 'sub_color' not in st.session_state: st.session_state.sub_color = "#ff00de"

# =================================================================
# 2. INTELLIGENCE ENGINE (ลอจิกถอดรหัสของคุณต๊ะ)
# =================================================================
def get_synapse_report(dt):
    if dt is None: return None
    
    # พิกัด 1: วัน (คุณต๊ะใช้ ศุกร์=5) -> จันทร์=1, ..., ศุกร์=5, เสาร์=6, อาทิตย์=7
    day_map = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7}
    day_val = day_map[dt.weekday()]
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    
    # พิกัด 2: วันที่
    date_val = dt.day
    
    # พิกัด 3: เดือน (1-12)
    month_val = dt.month
    month_names = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", 
                   "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    
    # พิกัด 4: ข้างขึ้นแรม (คำนวณจากรอบ 29.53)
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_pos = (diff - 0.5) % 29.530589
    if lunar_pos <= 14.765:
        moon_num = int(lunar_pos) + 1
        phase_text = f"ขึ้น {moon_num} ค่ำ"
        lunar_logic = -7.5  # ขึ้น ลบ 7.5
    else:
        moon_num = int(lunar_pos - 14.765) + 1
        phase_text = f"แรม {moon_num} ค่ำ"
        lunar_logic = 7.5   # แรม บวก 7.5

    # พิกัด 5: ปีนักษัตร (ชวด=1, ฉลู=2...)
    zodiac_names = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
    zodiac_val_map = {"ชวด":1, "ฉลู":2, "ขาล":3, "เถาะ":4, "มะโรง":5, "มะเส็ง":6, "มะเมีย":7, "มะแม":8, "วอก":9, "ระกา":10, "จอ":11, "กุน":12}
    zodiac_name = zodiac_names[dt.year % 12]
    z_val = zodiac_val_map[zodiac_name]

    # พิกัด 6: ธาตุ และ ราศี (ดิน=1, น้ำ=2, ลม=3, ไฟ=4)
    m, d = dt.month, dt.day
    if (m == 4 and d >= 13) or (m == 5 and d <= 13): rasi, e_text, e_val = "เมษ", "ไฟ", 4
    elif (m == 5 and d >= 14) or (m == 6 and d <= 14): rasi, e_text, e_val = "พฤษภ", "ดิน", 1
    elif (m == 6 and d >= 15) or (m == 7 and d <= 15): rasi, e_text, e_val = "เมถุน", "ลม", 3
    elif (m == 7 and d >= 16) or (m == 8 and d <= 16): rasi, e_text, e_val = "กรกฎ", "น้ำ", 2
    elif (m == 8 and d >= 17) or (m == 9 and d <= 16): rasi, e_text, e_val = "สิงห์", "ไฟ", 4
    elif (m == 9 and d >= 17) or (m == 10 and d <= 16): rasi, e_text, e_val = "กันย์", "ดิน", 1
    elif (m == 10 and d >= 17) or (m == 11 and d <= 15): rasi, e_text, e_val = "ตุลย์", "ลม", 3
    elif (m == 11 and d >= 16) or (m == 12 and d <= 15): rasi, e_text, e_val = "พิจิก", "น้ำ", 2
    elif (m == 12 and d >= 16) or (m == 1 and d <= 14): rasi, e_text, e_val = "ธนู", "ไฟ", 4
    elif (m == 1 and d >= 15) or (m == 2 and d <= 12): rasi, e_text, e_val = "มังกร", "ดิน", 1
    elif (m == 2 and d >= 13) or (m == 3 and d <= 13): rasi, e_text, e_val = "กุมภ์", "ลม", 3
    else: rasi, e_text, e_val = "มีน", "น้ำ", 2

    # --- คำนวณรหัสผลลัพธ์ (สูตรคุณต๊ะ) ---
    base_sum = day_val + date_val + moon_num + month_val + z_val + e_val
    final_code = (base_sum + lunar_logic) * 1.618

    return {
        "day": day_names[dt.weekday()], "date": date_val, "month": month_names[month_val],
        "zodiac": zodiac_name, "phase": phase_text, "elem": e_text, "rasi": rasi, "code": round(final_code, 4)
    }

# =================================================================
# 3. NAVIGATION (หน้าจอหลัก)
# =================================================================

# --- [ ส่วนจัดการ NAVIGATION: เช็กย่อหน้าให้ตรงกัน ] ---

# 1. หน้า HOME
if st.session_state.page == "HOME":
    st.markdown(f"<h1 class='neon-text' style='color:{st.session_state.main_color};'>SYNAPSE HUB</h1>", unsafe_allow_html=True)
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎵 1. DJ STATION", use_container_width=True): 
            st.session_state.page = "1"
            st.rerun()
    with col2:
        if st.button("🧠 3. INTELLIGENCE CENTER", use_container_width=True): 
            st.session_state.page = "3"
            st.rerun()

# 2. หน้า 1: DJ STATION
elif st.session_state.page == "1":
    if st.button("⬅️ กลับ"): 
        st.session_state.page = "HOME"
        st.rerun()
    st.write("### 🎧 DJ Station Mode")
    # ใส่โค้ดส่วนหน้า 1 ของคุณต๊ะตรงนี้

# 3. หน้า 3: INTELLIGENCE CENTER (ส่วนที่คุณต๊ะ Error บรรทัด 79)
elif st.session_state.page == "3":
    if st.button("⬅️ กลับหน้าหลัก"): 
        st.session_state.page = "HOME"
        st.rerun()
    
    st.markdown("<h2 style='text-align:center;'>🧠 INTELLIGENCE ENGINE</h2>", unsafe_allow_html=True)
    
    # ช่องกรอกแค่วันที่ (1960-2026)
    input_dt = st.date_input("เลือกวันที่เพื่อสแกนพิกัด", 
                            value=datetime.date.today(),
                            min_value=datetime.date(1960,1,1),
                            max_value=datetime.date(2026,12,31))

    if st.button("RUN FULL DECODER", use_container_width=True):
        # ดึงข้อมูลจากฟังก์ชันคำนวณ (เรียกใช้ get_synapse_report)
        res = get_synapse_report(input_dt) 
        
        st.write("---")
        # แสดงผล 7 หัวข้อที่คุณต๊ะต้องการ
        st.markdown(f"""
        ### 📋 รายงานพิกัดดิจิทัล:
        * **วัน:** {res['day']} ({res['day_val']})
        * **วันที่:** {res['date']}
        * **เดือน:** {res['month']} ({res['month_val']})
        * **ปีนักษัตร:** {res['zodiac']} ({res['z_val']})
        * **ข้างขึ้น/แรม:** {res['phase']} ({res['l_logic_text']})
        * **ธาตุ:** {res['elem']} ({res['e_val']})
        * **ราศี:** {res['rasi']}
        """)
        
        # แสดงรหัสผลลัพธ์
        st.markdown(f"""
            <div style="text-align:center; padding:20px; border:2px solid {st.session_state.main_color}; border-radius:15px; background:black;">
                <h1 style="color:{st.session_state.main_color}; margin:0;">CODE: {res['code']}</h1>
                <p style="color:gray;">LUNAR BALANCE 1.618</p>
            </div>
        """, unsafe_allow_html=True)
 
