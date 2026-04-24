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

# --- หน้า 3: INTELLIGENCE CENTER ---
elif st.session_state.page == "3":
    if st.button("⬅️ BACK"): 
        st.session_state.page = "HOME"
        st.rerun()
        
    st.markdown("<h2 class='neon-text'>🧠 INTELLIGENCE ENGINE</h2>", unsafe_allow_html=True)
    
    # 1. รับค่าวันที่จากผู้ใช้
    input_dt = st.date_input("ระบุวันที่เพื่อสแกนพิกัด", value=date.today(),
                            min_value=date(1960,1,1), max_value=date(2026,12,31))

    # 2. เริ่มการทำงานเมื่อกดปุ่มเท่านั้น
    if st.button("RUN DECODER & ANALYTICS", use_container_width=True):
        
        # ป้องกัน Error โดยการสแกนหาค่า res ก่อน
        res = get_synapse_report(input_dt)
        
        if res is not None:
            # ดึงรหัสมาเก็บไว้ในตัวแปร (ตอนนี้ปลอดภัยแล้วเพราะอยู่ในปุ่มกด)
            current_code = res['code']
            
            # --- [ ส่วนวิเคราะห์สัญลักษณ์เหตุการณ์ ] ---
            suffix = current_code % 1
            if current_code > 80: 
                symbol, event, desc = "🔥", "PEAK ACTION", "ช่วงเวลาพลังงานพุ่งพล่าน เหมาะกับการรุกหรือตัดสินใจใหญ่"
            elif suffix > 0.7: 
                symbol, event, desc = "⚡", "SHOCK TRIGGER", "ระวังเหตุการณ์ฉับพลัน หรือการเปลี่ยนแปลงกะทันหัน"
            elif 0.4 <= suffix <= 0.6: 
                symbol, event, desc = "💎", "GOLDEN SYNC", "พิกัดสมดุลจักรวาล มีเกณฑ์พบเจอโชคลาภหรือโอกาสดี"
            else: 
                symbol, event, desc = "🛡️", "BARRIER MODE", "พลังงานหน่วงตัว เน้นการตั้งรับและความรอบคอบ"

            # --- [ ส่วนแสดงรายงาน 7 หัวข้อ ] ---
            st.write("---")
            st.markdown(f"### 📋 รายงานวิเคราะห์วันที่: {input_dt}")
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.markdown(f"""
                * **วัน:** {res['day']} ({res['day_val']})
                * **วันที่:** {res['date']}
                * **เดือน:** {res['month']} ({res['month_val']})
                """)
            with col_res2:
                st.markdown(f"""
                * **ปีนักษัตร:** {res['zodiac']} ({res['z_val']})
                * **ข้างขึ้น/แรม:** {res['phase']}
                * **ธาตุ/ราศี:** {res['elem']} / {res['rasi']}
                """)

            # --- [ ส่วนแสดงรหัสลับ (Big Box) ] ---
            st.markdown(f"""
                <div style="text-align:center; padding:25px; border:3px solid {st.session_state.main_color}; border-radius:20px; background:rgba(0,0,0,0.6); box-shadow: 0 0 15px {st.session_state.main_color};">
                    <h1 style="font-size:70px; margin:0;">{symbol}</h1>
                    <h1 style="color:{st.session_state.main_color}; margin:0; font-family: monospace;">CODE: {current_code}</h1>
                    <h3 style="color:white; margin:10px 0;">สถานะ: {event}</h3>
                    <p style="color:#cccccc; font-style: italic;">{desc}</p>
                </div>
            """, unsafe_allow_html=True)

            # --- [ ส่วนคำนวณสถิติ 730 วัน (Time Scanner) ] ---
            st.write("")
            st.markdown("### 📊 TIMELINE ANALYTICS (730 DAYS)")
            
            with st.spinner("กำลังสแกนหาจุดเชื่อมโยงในไทม์ไลน์..."):
                past_sync = 0
                future_sync = 0
                for i in range(-365, 366):
                    if i == 0: continue
                    scan_date = input_dt + timedelta(days=i)
                    scan_res = get_synapse_report(scan_date)
                    if scan_res and abs(scan_res['code'] - current_code) < 1.2:
                        if i < 0: past_sync += 1
                        else: future_sync += 1
                
                col_s1, col_s2 = st.columns(2)
                col_s1.metric("PAST SYNC (อดีต)", f"{past_sync} ครั้ง", delta="จุดเชื่อมโยง", delta_color="off")
                col_s2.metric("FUTURE SYNC (อนาคต)", f"{future_sync} ครั้ง", delta="จุดพยากรณ์", delta_color="normal")

            # --- [ ส่วน Intelligence Briefing (อธิบายลอจิก) ] ---
            with st.expander("🔍 ระบบนี้ทำงานอย่างไร? (EXPLANTION FOR AGENT)"):
                st.markdown(f"""
                #### ที่มาของเลขพิกัด {current_code}
                1. **Data Source (ต้นทาง):** ดึงค่าจากมิติ **วาร (Day)**, **สุริยคติ (Date)**, **จันทรคติ (Phase)**, **นักษัตร (Year)** และ **ธาตุสถิต (Element)**
                2. **Summation (การรวม):** นำเลขทั้ง 6 จุดมาบวกรวมกันเพื่อหาค่าพลังงานพื้นฐาน
                3. **Harmonic Balance (สมดุล):** ใช้ค่า **±7.5** (ครึ่งรอบจันทรคติ) เพื่อชดเชยแรงดึงดูดของข้างขึ้นข้างแรม
                4. **The Golden Ratio (1.618):** คูณด้วยค่าอัตราส่วนทองคำ เพื่อหาจุดที่พิกัดนี้สั่นสะเทือนในระดับเสถียรที่สุด
                5. **Symmetry Matching:** สแกนย้อนหลังและล่วงหน้า 365 วัน เพื่อเปรียบเทียบว่ารหัสที่ "เหมือนกัน" เคยนำไปสู่เหตุการณ์ใดในอดีต และมีโอกาสเกิดอะไรขึ้นในอนาคต
                """)
        else:
            st.error("ไม่สามารถโหลดข้อมูลพิกัดได้ กรุณาลองใหม่อีกครั้ง")
