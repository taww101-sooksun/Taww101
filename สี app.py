import streamlit as st
import datetime
from datetime import date, timedelta
import streamlit as st
import datetime
from datetime import date, timedelta

# --- ล็อคขอบเขตเวลาตามคำสั่งคุณต๊ะ ---
MIN_DATE = date(1960, 1, 1)
MAX_DATE = date(2026, 12, 31)

def get_synapse_report(dt):
    if dt is None: return None
    # (ฟังก์ชันคำนวณเหมือนเดิม แต่ดัก Error ช่วงวันที่)
    if dt < MIN_DATE or dt > MAX_DATE: return None
    
    day_map = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7}
    d_val = day_map[dt.weekday()]
    d_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    
    ref = date(1900, 1, 1)
    diff = (dt - ref).days
    lunar_pos = (diff - 0.5) % 29.530589
    if lunar_pos <= 14.765:
        moon_num = int(lunar_pos) + 1
        phase_text, l_logic = f"ขึ้น {moon_num} ค่ำ", -7.5
    else:
        moon_num = int(lunar_pos - 14.765) + 1
        phase_text, l_logic = f"แรม {moon_num} ค่ำ", 7.5

    z_names = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
    z_map = {"ชวด":1, "ฉลู":2, "ขาล":3, "เถาะ":4, "มะโรง":5, "มะเส็ง":6, "มะเมีย":7, "มะแม":8, "วอก":9, "ระกา":10, "จอ":11, "กุน":12}
    z_name = z_names[dt.year % 12]
    zv = z_map.get(z_name, 1)

    m, d = dt.month, dt.day
    if (m == 5 and d >= 14) or (m == 6 and d <= 14): et, ev = "ดิน", 1
    elif (m == 4 and d >= 13) or (m == 5 and d <= 13): et, ev = "ไฟ", 4
    else: et, ev = "ลม", 3

    base_sum = d_val + dt.day + moon_num + dt.month + zv + ev
    final_code = (base_sum + l_logic) * 1.618

    return {
        "day": d_names[dt.weekday()], "day_val": d_val, "date": dt.day,
        "month": dt.month, "zodiac": z_name, "z_val": zv,
        "phase": phase_text, "elem": et, "e_val": ev, "code": round(final_code, 4)
    }

st.set_page_config(page_title="SYNAPSE 1960-2026", layout="wide")
st.title("🧠 Synapse High-Speed Math (1960-2026)")

tab1, tab2 = st.tabs(["👤 ข้อมูลบุคคล", "👥 ข้อมูลคู่ขนาน"])

with tab1:
    user_dt = st.date_input("เลือกวันเกิดของคุณ (1960-2026)", 
                           value=date(2000, 1, 1),
                           min_value=MIN_DATE, max_value=MAX_DATE)
    if st.button("ประมวลผลพิกัด"):
        res = get_synapse_report(user_dt)
        st.success(f"รหัสพิกัดของคุณคือ: {res['code']}")
        # (เพิ่มส่วนสแกนอดีต-อนาคตตามโค้ดก่อนหน้าได้เลยครับ)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        dt_a = st.date_input("วันเกิดคนที่ 1", value=date(1980, 1, 1), 
                            min_value=MIN_DATE, max_value=MAX_DATE, key="a")
    with col2:
        dt_b = st.date_input("วันเกิดคนที่ 2", value=date(1990, 1, 1), 
                            min_value=MIN_DATE, max_value=MAX_DATE, key="b")
    
    if st.button("คำนวณคู่ขนาน"):
        ra = get_synapse_report(dt_a)
        rb = get_synapse_report(dt_b)
        res_code = (ra['code'] + rb['code']) / 1.618
        st.warning(f"CO-RESONANCE CODE: {round(res_code, 4)}")

# =================================================================
# 1. HIGH-SPEED MATHEMATICS ENGINE (ตัวคำนวณหลัก)
# =================================================================
def get_synapse_report(dt):
    if dt is None: return None
    
    # พิกัดฐาน (Base Coordinates)
    day_map = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7}
    d_val = day_map[dt.weekday()]
    d_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    
    # พิกัดจันทรคติ (Lunar Balance ±7.5)
    ref = date(1900, 1, 1)
    diff = (dt - ref).days
    lunar_pos = (diff - 0.5) % 29.530589
    if lunar_pos <= 14.765:
        moon_num = int(lunar_pos) + 1
        phase_text, l_logic = f"ขึ้น {moon_num} ค่ำ", -7.5
    else:
        moon_num = int(lunar_pos - 14.765) + 1
        phase_text, l_logic = f"แรม {moon_num} ค่ำ", 7.5

    # พิกัดจักรราศี & นักษัตร
    z_names = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
    z_map = {"ชวด":1, "ฉลู":2, "ขาล":3, "เถาะ":4, "มะโรง":5, "มะเส็ง":6, "มะเมีย":7, "มะแม":8, "วอก":9, "ระกา":10, "จอ":11, "กุน":12}
    z_name = z_names[dt.year % 12]
    zv = z_map.get(z_name, 1)

    # พิกัดธาตุ (Element Matrix)
    m, d = dt.month, dt.day
    if (m == 5 and d >= 14) or (m == 6 and d <= 14): et, ev = "ดิน", 1
    elif (m == 4 and d >= 13) or (m == 5 and d <= 13): et, ev = "ไฟ", 4
    elif (m == 7 and d >= 16) or (m == 8 and d <= 16): et, ev = "น้ำ", 2
    else: et, ev = "ลม", 3

    # สูตร Golden Ratio (1.618)
    # [วัน + วันที่ + ค่ำ + เดือน + ปี + ธาตุ] 
    base_sum = d_val + dt.day + moon_num + dt.month + zv + ev
    final_code = (base_sum + l_logic) * 1.618

    return {
        "day": d_names[dt.weekday()], "day_val": d_val, "date": dt.day,
        "month": dt.month, "zodiac": z_name, "z_val": zv,
        "phase": phase_text, "elem": et, "e_val": ev, "code": round(final_code, 4)
    }

# =================================================================
# 2. INTERFACE & NAVIGATION
# =================================================================
st.set_page_config(page_title="SYNAPSE ULTIMATE", layout="wide")

# CSS ตกแต่งให้ดูไฮเทค
st.markdown("""
    <style>
    .report-card { background: #0e1117; padding: 25px; border-radius: 15px; border: 1px solid #00f3ff; margin-bottom: 20px; }
    .gold-card { background: #0e1117; padding: 25px; border-radius: 15px; border: 1px solid gold; margin-bottom: 20px; }
    .neon-text { color: #00f3ff; text-shadow: 0 0 10px #00f3ff; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;' class='neon-text'>🧬 SYNAPSE INTELLIGENCE SYSTEM</h1>", unsafe_allow_html=True)
st.write("<p style='text-align:center;'>ระบบคำนวณพิกัดมิติคู่ขนานด้วยลอจิกคณิตศาสตร์ความเร็วสูง 1.618</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["👤 วิเคราะห์พิกัดบุคคล", "👥 วิเคราะห์คู่ขนาน (Resonance)"])

# -----------------------------------------------------------------
# TAB 1: วิเคราะห์พิกัดบุคคล
# -----------------------------------------------------------------
with tab1:
    col_in1, col_in2 = st.columns([1, 2])
    with col_in1:
        u_dt = st.date_input("เลือกวันที่ต้องการสแกน (วันเกิด/วันสำคัญ)", value=date.today())
        run_single = st.button("RUN SINGLE DECODER", use_container_width=True)
    
    if run_single:
        res = get_synapse_report(u_dt)
        with col_in2:
            st.markdown(f"""
            <div class='report-card'>
                <h2 class='neon-text'>PERSONAL CODE: {res['code']}</h2>
                <p><b>ถอดรหัสพิกัด 6 มิติ:</b></p>
                <ul>
                    <li>พิกัดวาร: {res['day']} ({res['day_val']})</li>
                    <li>สุริยคติ: วันที่ {res['date']} เดือน {res['month']}</li>
                    <li>จันทรคติ: {res['phase']} (สมดุลดวงจันทร์)</li>
                    <li>นักษัตร: ปี{res['zodiac']} (พลังงาน {res['z_val']})</li>
                    <li>ธาตุสถิต: ธาตุ{res['elem']} (มิติ {res['e_val']})</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        # สแกนไทม์ไลน์ 730 วัน
        st.write("---")
        st.subheader("📊 TIMELINE SCANNER (อดีต - อนาคต)")
        past, future = 0, 0
        for i in range(-365, 366):
            if i == 0: continue
            s_res = get_synapse_report(u_dt + timedelta(days=i))
            if abs(s_res['code'] - res['code']) < 1.3:
                if i < 0: past += 1
                else: future += 1
        
        c1, c2 = st.columns(2)
        c1.metric("อดีตที่เคย Sync (365 วัน)", f"{past} ครั้ง")
        c2.metric("อนาคตที่จะ Sync (365 วัน)", f"{future} ครั้ง")
        
        with st.expander("🔍 ที่มาของตัวเลข (Intelligence Briefing)"):
            st.write(f"เลข {res['code']} มาจากการรวมพิกัดทั้ง 6 มิติ แล้วปรับด้วยค่าความต่างของข้างขึ้นข้างแรม (±7.5) จากนั้นคูณด้วย 1.618 (Golden Ratio) เพื่อหาค่าจุดสมดุลของร่างกายและ DNA ในมิติกาลเวลา")

# -----------------------------------------------------------------
# TAB 2: วิเคราะห์คู่ขนาน (Resonance)
# -----------------------------------------------------------------
with tab2:
    st.markdown("### 🧬 ค้นหาจุดบรรจบของคน 2 คน")
    c_p1, c_p2 = st.columns(2)
    with c_p1:
        dt_a = st.date_input("วันเกิด/พิกัด คนที่ 1", value=date(1990,1,1), key="a")
    with c_p2:
        dt_b = st.date_input("วันเกิด/พิกัด คนที่ 2", value=date(1995,1,1), key="b")
    
    if st.button("RUN RESONANCE MATCHING", use_container_width=True):
        res_a = get_synapse_report(dt_a)
        res_b = get_synapse_report(dt_b)
        
        # สูตร: (A + B) / 1.618
        res_code = (res_a['code'] + res_b['code']) / 1.618
        
        st.markdown(f"""
            <div class='gold-card' style='text-align:center;'>
                <h3 style='color:gold;'>CO-RESONANCE CODE</h3>
                <h1 style='font-size:60px;'>{round(res_code, 4)}</h1>
                <p>นี่คือรหัสจุดบรรจบคู่ขนานที่จูนด้วยสัดส่วนทองคำ</p>
            </div>
        """, unsafe_allow_html=True)

        # สแกนหาจุด Sync ร่วมกันในอนาคต
        st.write("---")
        st.subheader("📅 พยากรณ์วันบรรจบพิกัดร่วม (Next 365 Days)")
        future_dates = []
        for i in range(1, 366):
            target_dt = date.today() + timedelta(days=i)
            s_res = get_synapse_report(target_dt)
            # หาจุดที่วันที่ในอนาคต มีรหัสใกล้เคียงกับรหัสคู่ขนานของเรา
            if abs(s_res['code'] - res_code) < 1.5:
                future_dates.append({"วันที่": target_dt.strftime("%d/%m/%Y"), "รหัสวัน": s_res['code']})
        
        if future_dates:
            st.write(f"พบจุด Sync ร่วมกันทั้งหมด {len(future_dates)} วัน ในปีหน้า:")
            st.table(future_dates[:10]) # โชว์ 10 วันแรก
        
        with st.expander("📚 ลอจิกการคำนวณคู่ขนาน"):
            st.markdown(f"""
            1. **FUSION:** นำรหัสพิกัดเดี่ยวของทั้งคู่มารวมกันเพื่อหาค่าพลังงานรวม
            2. **STABILIZER:** หารด้วย **1.618** เพื่อบีบอัดพลังงานให้กลับมาอยู่ในจุดที่สมดุลที่สุดตามสัดส่วนธรรมชาติ (ไม่ได้หาร 2 แบบค่าเฉลี่ยทั่วไป)
            3. **SYNC:** วันที่ปรากฏในตาราง คือวันที่ 'มิติกาลเวลา' มีแรงสั่นสะเทือนตรงกับ 'รหัสร่วม' ของคุณทั้งคู่ เหมาะสำหรับทำกิจกรรมสำคัญร่วมกัน
            """)

# FOOTER
st.write("---")
st.markdown("<p style='text-align:center; color:gray;'>High-Speed Math Algorithm | Golden Ratio 1.618 | Synapse Engine v.Ultimate</p>", unsafe_allow_html=True)
