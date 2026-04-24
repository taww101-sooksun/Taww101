import streamlit as st
import datetime
from datetime import date, timedelta

# =================================================================
# 1. SETUP & CONFIG (ส่วนตั้งค่า)
# =================================================================
st.set_page_config(page_title="SYNAPSE ULTIMATE", layout="wide")

if 'page' not in st.session_state: st.session_state.page = "HOME"
if 'main_color' not in st.session_state: st.session_state.main_color = "#00f3ff"

# =================================================================
# 2. INTELLIGENCE ENGINE (ฟังก์ชันคำนวณ - ต้องอยู่นอกสุด)
# =================================================================
def get_synapse_report(dt):
    if dt is None: return None
    
    # พิกัด 1-3: วัน/วันที่/เดือน
    day_map = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7}
    d_val = day_map[dt.weekday()]
    d_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    m_val = dt.month
    
    # พิกัด 4: ข้างขึ้นแรม
    ref = date(1900, 1, 1)
    diff = (dt - ref).days
    lunar_pos = (diff - 0.5) % 29.530589
    if lunar_pos <= 14.765:
        moon_num = int(lunar_pos) + 1
        phase_text, l_logic, l_txt = f"ขึ้น {moon_num} ค่ำ", -7.5, "ลบ 7.5"
    else:
        moon_num = int(lunar_pos - 14.765) + 1
        phase_text, l_logic, l_txt = f"แรม {moon_num} ค่ำ", 7.5, "บวก 7.5"

    # พิกัด 5: ปีนักษัตร
    z_names = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
    z_map = {"ชวด":1, "ฉลู":2, "ขาล":3, "เถาะ":4, "มะโรง":5, "มะเส็ง":6, "มะเมีย":7, "มะแม":8, "วอก":9, "ระกา":10, "จอ":11, "กุน":12}
    z_name = z_names[dt.year % 12]
    zv = z_map.get(z_name, 1)

    # พิกัด 6: ธาตุ (ดิน=1, น้ำ=2, ลม=3, ไฟ=4)
    m, d = dt.month, dt.day
    if (m == 5 and d >= 14) or (m == 6 and d <= 14): rasi, et, ev = "พฤษภ", "ดิน", 1
    elif (m == 4 and d >= 13) or (m == 5 and d <= 13): rasi, et, ev = "เมษ", "ไฟ", 4
    else: rasi, et, ev = "อื่นๆ", "ลม", 3

    # สูตรคำนวณ
    base_sum = d_val + dt.day + moon_num + m_val + zv + ev
    final_code = (base_sum + l_logic) * 1.618

    return {
        "day": d_names[dt.weekday()], "day_val": d_val, "date": dt.day,
        "month": m_val, "month_val": m_val, "zodiac": z_name, "z_val": zv,
        "phase": phase_text, "l_logic_text": l_txt, "elem": et, "e_val": ev,
        "rasi": rasi, "code": round(final_code, 4)
    }

# =================================================================
# 3. NAVIGATION (ส่วนควบคุมหน้าจอ)
# =================================================================

# --- หน้า HOME ---
if st.session_state.page == "HOME":
    st.markdown(f"<h1 style='color:{st.session_state.main_color}; text-align:center;'>SYNAPSE HUB</h1>", unsafe_allow_html=True)
    if st.button("🧠 3. INTELLIGENCE CENTER", use_container_width=True):
        st.session_state.page = "3"
        st.rerun()

# --- หน้า 3: INTELLIGENCE CENTER ---
elif st.session_state.page == "3":
    if st.button("⬅️ BACK"):
        st.session_state.page = "HOME"
        st.rerun()
    
    st.markdown("<h2 style='text-align:center;'>🧠 INTELLIGENCE ENGINE</h2>", unsafe_allow_html=True)
    
    input_dt = st.date_input("ระบุวันที่ (1960-2026)", value=date.today(),
                            min_value=date(1960,1,1), max_value=date(2026,12,31))

    if st.button("RUN DECODER & ANALYTICS", use_container_width=True):
        res = get_synapse_report(input_dt)
        
        if res:
            cur_code = res['code']
            # วิเคราะห์สัญลักษณ์
            suffix = cur_code % 1
            if cur_code > 80: sym, evt = "🔥", "PEAK ACTION"
            elif suffix > 0.7: sym, evt = "⚡", "SHOCK TRIGGER"
            elif 0.4 <= suffix <= 0.6: sym, evt = "💎", "GOLDEN SYNC"
            else: sym, evt = "🛡️", "BARRIER MODE"

            # แสดงผล 7 หัวข้อ
            st.write("---")
            st.markdown(f"""
            ### 📋 ข้อมูลพิกัด: {res['day']} ที่ {res['date']}/{res['month']}
            * **พิกัดวัน:** {res['day']} ({res['day_val']})
            * **พิกัดเดือน:** {res['month']}
            * **พิกัดนักษัตร:** {res['zodiac']} ({res['z_val']})
            * **พิกัดข้างขึ้นแรม:** {res['phase']} ({res['l_logic_text']})
            * **พิกัดธาตุ:** {res['elem']} ({res['e_val']})
            * **ราศี:** {res['rasi']}
            """)

            st.markdown(f"""
                <div style="text-align:center; padding:20px; border:2px solid {st.session_state.main_color}; border-radius:15px; background:black;">
                    <h1 style="font-size:60px; margin:0;">{sym}</h1>
                    <h2 style="color:{st.session_state.main_color}; margin:0;">CODE: {cur_code}</h2>
                    <p style="color:white;">สถานะ: {evt}</p>
                </div>
            """, unsafe_allow_html=True)

            # สถิติ 730 วัน
            st.write("---")
            st.markdown("### 📊 TIMELINE ANALYTICS (730 DAYS)")
            past_sync, future_sync = 0, 0
            for i in range(-365, 366):
                if i == 0: continue
                s_res = get_synapse_report(input_dt + timedelta(days=i))
                if abs(s_res['code'] - cur_code) < 1.2:
                    if i < 0: past_sync += 1
                    else: future_sync += 1
            
            c1, c2 = st.columns(2)
            c1.metric("อดีตที่เคยเกิดเหตุ", f"{past_sync} ครั้ง")
            c2.metric("อนาคตที่จะเกิดเหตุ", f"{future_sync} ครั้ง")

            with st.expander("🔍 อธิบายที่มาของเลข"):
                st.write(f"เลข {cur_code} มาจากการรวมพิกัดทั้ง 6 จุด แล้วปรับสมดุลด้วยค่า ±7.5 ตามแรงดึงดูดดวงจันทร์ ก่อนคูณด้วย 1.618 เพื่อหาค่าคงที่ของเหตุการณ์ครับ")
