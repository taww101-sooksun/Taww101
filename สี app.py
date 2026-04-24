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
# --- ส่วนนี้วางต่อจากรายงานผล res = get_synapse_report(target_dt) ---

st.write("---")
st.markdown("<h3 class='neon-text'>📊 TIMELINE ANALYTICS (730 DAYS)</h3>", unsafe_allow_html=True)

# 1. คำนวณสถิติ ย้อนหลัง 365 วัน และ อนาคต 365 วัน
current_code = res['code']
past_matches = 0
future_matches = 0
timeline_data = []

# วงรอบการสแกน (730 วัน)
for i in range(-365, 366):
    scan_date = target_dt + timedelta(days=i)
    scan_res = get_synapse_report(scan_date)
    
# --- ส่วนวิเคราะห์เหตุการณ์จากรหัส ---
def interpret_event(code):
    suffix = code % 1  # ดึงค่าทศนิยมมาวิเคราะห์
    if code > 80:
        return "🔥 PEAK ACTION", "ช่วงเวลาแห่งการพุ่งทะยาน เหมาะกับการตัดสินใจใหญ่"
    elif suffix > 0.7:
        return "⚡ SHOCK TRIGGER", "ระวังเหตุการณ์ไม่คาดฝัน หรือการเปลี่ยนแปลงที่รวดเร็ว"
    elif 0.4 <= suffix <= 0.6:
        return "💎 GOLDEN SYNC", "พิกัดอยู่ในจุดสมดุลจักรวาล มีโอกาสพบเจอเรื่องดีๆ หรือโชคลาภ"
    else:
        return "🛡️ BARRIER MODE", "กาลเวลาหยุดนิ่งเพื่อการตั้งรับ ควรใช้ความรอบคอบเป็นพิเศษ"

# การแสดงผลในแอป
event_title, event_desc = interpret_event(res['code'])

st.markdown(f"""
    <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-top: 10px; border-left: 5px solid {st.session_state.main_color};">
        <h4 style="margin:0; color:white;">{event_title}</h4>
        <p style="margin:0; color:lightgray; font-size: 0.9rem;">{event_desc}</p>
    </div>
""", unsafe_allow_html=True)


# แสดงผลสถิติเป็น Metric
col_s1, col_s2, col_s3 = st.columns(3)
col_s1.metric("PAST SYNC (365d)", f"{past_matches} ครั้ง", "อดีต")
col_s2.metric("CURRENT CODE", current_code)
col_s3.metric("FUTURE SYNC (365d)", f"{future_matches} ครั้ง", "ทำนาย")

# 2. ส่วนคำอธิบายระบบ (Intelligence Briefing)
with st.expander("🔍 HOW IT WORKS? (ลอจิกการคำนวณทั้งหมด)"):
    st.markdown(f"""
    ### 🧠 ขั้นตอนการถอดรหัสพิกัดดิจิทัล
    รหัส **{current_code}** ที่คุณเห็น มาจากการรวบรวมค่าพิกัด 6 มิติ ดังนี้:
    
    1. **มิติวาร (วัน):** ดึงค่าพลังงานจากวันทั้ง 7 (จันทร์=1 ถึง อาทิตย์=7) ➜ **ค่าปัจจุบัน: {res['day_val']}**
    2. **มิติสุริยคติ (วันที่):** เลขวันที่ที่คุณเกิดหรือวันที่เลือก ➜ **ค่าปัจจุบัน: {res['date']}**
    3. **มิติจันทรคติ (ค่ำ):** คำนวณจากรอบดวงจันทร์ 29.53 วัน เพื่อหาข้างขึ้น/ข้างแรม ➜ **ค่าปัจจุบัน: {res['phase']}**
    4. **มิติรอบเดือน:** ลำดับของเดือน 1-12 ➜ **ค่าปัจจุบัน: {res['month_val']}**
    5. **มิติจักรราศี (ปีนักษัตร):** รอบปีนักษัตรทั้ง 12 ปี ➜ **ค่าปัจจุบัน: {res['z_val']} ({res['zodiac']})**
    6. **มิติธาตุสถิต:** พลังงานจากธาตุ ดิน(1), น้ำ(2), ลม(3), ไฟ(4) ตามช่วงเวลา ➜ **ค่าปัจจุบัน: {res['e_val']} ({res['elem']})**
    
    ---
    ### ⚙️ สูตรการประมวลผล (SYNAPSE FORMULA)
    ระบบจะนำค่าทั้ง 6 มิติมารวมกันเป็น **"ฐานพลังงาน"**
    * **ฐานรวม:** ({res['day_val']} + {res['date']} + {res['month_val']} + {res['z_val']} + {res['e_val']} + ค่ำ) = **{int(current_code/1.618 - (7.5 if "แรม" in res['phase'] else -7.5))}**
    * **ปรับสมดุลจันทรคติ:** หากเป็นข้างขึ้นจะ **ลบ 7.5** | หากเป็นข้างแรมจะ **บวก 7.5** (เพื่อหาจุดสมดุลน้ำขึ้น-น้ำลง)
    * **คูณค่า Golden Ratio (1.618):** เพื่อขยายสัญญาณพิกัดให้กลายเป็นรหัสลับที่ใช้เชื่อมต่อกับมิติอื่นๆ
    
    **สรุป:** รหัสนี้เปรียบเสมือน "ลายนิ้วมือของกาลเวลา" ที่บอกว่าคุณมีความสอดคล้องกับจักรวาลในช่วงเวลานั้นอย่างไร
    """)

if timeline_data:
    st.write("📍 **จุดเชื่อมโยงไทม์ไลน์ที่ใกล้เคียงที่สุด:**")
    st.table(timeline_data)


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
