import streamlit as st
from datetime import date, timedelta

# --- ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="SYNAPSE ULTIMATE SYSTEM", layout="wide")

# --- ฟังก์ชันคำนวณพิกัดพื้นฐาน 6 มิติ ---
def get_base_coordinates(dt):
    if dt is None: return None
    
    # 1. วัน (จันทร์-อาทิตย์)
    day_map = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7}
    d_val = day_map[dt.weekday()]
    d_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]

    # 2. ข้างขึ้นข้างแรม (เกณฑ์ดวงจันทร์ใกล้/ไกล)
    ref = date(1900, 1, 1)
    diff = (dt - ref).days
    lunar_pos = (diff - 0.5) % 29.530589
    if lunar_pos <= 14.765:
        moon_num = int(lunar_pos) + 1
        # ขึ้น = ลบ (ดวงจันทร์ไกล)
        phase_text, l_logic, l_symbol = f"ขึ้น {moon_num} ค่ำ", -7.5, "(-) ดวงจันทร์ไกล"
    else:
        moon_num = int(lunar_pos - 14.765) + 1
        # แรม = บวก (ดวงจันทร์ใกล้)
        phase_text, l_logic, l_symbol = f"แรม {moon_num} ค่ำ", 7.5, "(+) ดวงจันทร์ใกล้"

    # 3. ปีนักษัตร
    z_names = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
    z_map = {"ชวด":1, "ฉลู":2, "ขาล":3, "เถาะ":4, "มะโรง":5, "มะเส็ง":6, "มะเมีย":7, "มะแม":8, "วอก":9, "ระกา":10, "จอ":11, "กุน":12}
    z_name = z_names[dt.year % 12]
    zv = z_map.get(z_name, 1)

    # 4. ธาตุประจำพิกัด
    m, d = dt.month, dt.day
    if (m == 5 and d >= 14) or (m == 6 and d <= 14): et, ev = "ดิน", 1
    elif (m == 4 and d >= 13) or (m == 5 and d <= 13): et, ev = "ไฟ", 4
    elif (m == 7 and d >= 16) or (m == 8 and d <= 16): et, ev = "น้ำ", 2
    else: et, ev = "ลม", 3

    # ตีค่าตัวเลขตามขั้นตอน: (วัน+วันที่+ค่ำ+เดือน+นักษัตร+ธาตุ + ค่าดวงจันทร์) * 1.618
    base_sum = d_val + dt.day + moon_num + dt.month + zv + ev
    raw_code = (base_sum + l_logic) * 1.618

    return {
        "day_name": d_names[dt.weekday()], "day_val": d_val, "date": dt.day,
        "month": dt.month, "zodiac": z_name, "z_val": zv,
        "phase": phase_text, "l_logic": l_logic, "l_symbol": l_symbol,
        "elem": et, "e_val": ev, "raw_code": round(raw_code, 4), "year": dt.year
    }

# --- ฟังก์ชันตีความเกณฑ์ตัวเลข (0-9 หน้าสุด) ---
def interpret_result(value):
    first_digit = int(str(abs(value)).replace('.', '')[0])
    if first_digit in [0, 5]:
        return "⚖️ สมดุลคงที่ (ค่ากลาง)", "#00f3ff"
    elif 1 <= first_digit <= 4:
        return "⚠️ ไม่สู้ดี (ต้องระวัง)", "#ff4b4b"
    else: # 6-9
        return "🔥 ดีมาก (แนวโน้มพัฒนาสูง)", "#00ff00"

# --- ส่วนหน้าจอแอป ---
st.markdown("<h1 style='text-align:center; color:#00f3ff;'>🧬 SYNAPSE ULTIMATE SYSTEM</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["👤 วิเคราะห์บุคคล (Single)", "👥 วิเคราะห์คู่ขนาน (Parallel)"])

# -----------------------------------------------------------------
# TAB 1: บุคคล (บวกอายุ และสแกนไทม์ไลน์)
# -----------------------------------------------------------------
with tab1:
    u_dt = st.date_input("วันเกิดของคุณ (1960-2026)", value=date(1984, 5, 18), 
                         min_value=date(1960,1,1), max_value=date(2026,12,31), key="u1")
    
    if st.button("ประมวลผลพิกัดบุคคล", key="run_u1"):
        res = get_base_coordinates(u_dt)
        age = 2026 - res['year']
        
        # สูตร: (รหัสบุคคล + อายุปัจจุบัน) / 1.618
        personal_code = (res['raw_code'] + age) / 1.618
        status, color = interpret_result(personal_code)
        
        st.markdown(f"""
        <div style="border:2px solid {color}; padding:20px; border-radius:15px;">
            <h3>📊 ข้อมูลพิกัด: {res['day_name']}ที่ {res['date']} เดือน {res['month']}</h3>
            <p><b>ปีนักษัตร:</b> {res['zodiac']} | <b>ธาตุ:</b> {res['elem']}</p>
            <p><b>สถานะดวงจันทร์:</b> {res['phase']} <b style="color:yellow;">{res['l_symbol']}</b></p>
            <hr>
            <h2 style="color:{color};">PERSONAL CODE: {round(personal_code, 4)}</h2>
            <h4 style="color:{color};">เกณฑ์: {status}</h4>
        </div>
        """, unsafe_allow_html=True)

        # สแกนไทม์ไลน์ 365 วัน
        st.write("---")
        st.subheader("📅 ไทม์ไลน์บุคคล (อดีต 365 - อนาคต 365)")
        past, future = 0, 0
        for i in range(-365, 366):
            if i == 0: continue
            s_res = get_base_coordinates(u_dt + timedelta(days=i))
            if abs(s_res['raw_code'] - res['raw_code']) < 1.6:
                if i < 0: past += 1
                else: future += 1
        st.write(f"พบจุด Sync อดีต: **{past}** ครั้ง | อนาคต: **{future}** ครั้ง")

# -----------------------------------------------------------------
# TAB 2: คู่ขนาน (2 คน)
# -----------------------------------------------------------------
with tab2:
    st.markdown("### 🧬 ค้นหาจุดบรรจบของคน 2 คน")
    c1, c2 = st.columns(2)
    with c1:
        dt_a = st.date_input("วันเกิดคนที่ 1", value=date(1984, 5, 18), key="p1")
    with c2:
        dt_b = st.date_input("วันเกิดคนที่ 2", value=date(1996, 8, 17), key="p2")

    if st.button("คำนวณจุดบรรจบคู่ขนาน", key="run_p"):
        res_a = get_base_coordinates(dt_a)
        res_b = get_base_coordinates(dt_b)
        
        # ผลรวม 2 คนหาร 1.618
        res_code = (res_a['raw_code'] + res_b['raw_code']) / 1.618
        status_p, color_p = interpret_result(res_code)
        
        st.markdown(f"""
        <div style="text-align:center; padding:30px; border:3px solid gold; border-radius:20px; background:black;">
            <h2 style="color:gold;">CO-RESONANCE CODE</h2>
            <h1 style="font-size:60px; color:white;">{round(res_code, 4)}</h1>
            <h3 style="color:{color_p};">เกณฑ์หน้าสุด: {status_p}</h3>
        </div>
        """, unsafe_allow_html=True)

        # สแกนไทม์ไลน์คู่ขนาน
        st.write("---")
        st.subheader("⏳ สแกนไทม์ไลน์คู่ขนาน (730 วัน)")
        p_past, p_future = 0, 0
        for i in range(-365, 366):
            if i == 0: continue
            # สแกนหาความถี่ที่ตรงกับรหัสร่วม
            s_res = get_base_coordinates(date.today() + timedelta(days=i))
            if abs(s_res['raw_code'] - res_code) < 2.0:
                if i < 0: p_past += 1
                else: p_future += 1
        
        st.info(f"ในอดีต 1 ปี พลังงานคู่นี้เคย Sync กัน {p_past} ครั้ง | ในอนาคต 1 ปี จะ Sync กันอีก {p_future} ครั้ง")

        with st.expander("🔍 อธิบายขั้นตอนการคำนวณ"):
            st.markdown(f"""
            1. **ดึงพิกัดมิติ:** วัน + วันที่ + เดือน + นักษัตร + ธาตุ
            2. **จูนดวงจันทร์:** แรม (+) ใกล้โลก / ขึ้น (-) ไกลโลก
            3. **ค่าคงที่:** คูณ 1.618 เพื่อหาพิกัดสมดุลรายบุคคล
            4. **Fusion:** นำรหัส 2 คนมาบวกกันแล้วหาร 1.618 เพื่อหาค่ากลางคู่ขนาน
            5. **เกณฑ์ตัดสิน:** ใช้ตัวเลขหน้าสุด (0,5 = นิ่ง / 1-4 = ระวัง / 6-9 = ดีมาก)
            """)
