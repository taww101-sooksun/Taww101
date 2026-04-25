import streamlit as st
from datetime import date, timedelta

# --- 1. ENGINE: คำนวณพิกัดพื้นฐาน (วัน/วันที่/ค่ำ/เดือน/ปี/ธาตุ) ---
def get_raw_coordinate(dt):
    if dt is None: return None
    # แปลงข้อมูลเป็นตัวเลขตามลำดับที่คุณต๊ะกำหนด
    d_val = {0:1, 1:2, 2:3, 3:4, 4:5, 5:6, 6:7}[dt.weekday()] # วันศุกร์=5
    date_val = dt.day # วันที่ตรงๆ
    month_val = dt.month # เดือน
    
    # ข้างขึ้นข้างแรม (แรม=บวก/ใกล้, ขึ้น=ลบ/ไกล)
    ref = date(1900, 1, 1)
    diff = (dt - ref).days
    lunar_pos = (diff - 0.5) % 29.530589
    if lunar_pos <= 14.765:
        moon_num = int(lunar_pos) + 1
        l_logic = -7.5 # ขึ้น = ลบ
        l_type = "ขึ้น"
    else:
        moon_num = int(lunar_pos - 14.765) + 1
        l_logic = 7.5 # แรม = บวก
        l_type = "แรม"

    # ปีนักษัตร (1-12)
    z_map = {0:9, 1:10, 2:11, 3:12, 4:1, 5:2, 6:3, 7:4, 8:5, 9:6, 10:7, 11:8}
    zv = z_map[dt.year % 12]

    # ธาตุ (ดิน=1, น้ำ=2, ลม=3, ไฟ=4)
    m, d = dt.month, dt.day
    if (m == 5 and d >= 14) or (m == 6 and d <= 14): ev = 1
    elif (m == 7 and d >= 16) or (m == 8 and d <= 16): ev = 2
    elif (m == 4 and d >= 13) or (m == 5 and d <= 13): ev = 4
    else: ev = 3

    # ผลรวมพิกัด * 1.618
    base_sum = d_val + date_val + moon_num + month_val + zv + ev
    raw_code = (base_sum + l_logic) * 1.618
    return {"code": raw_code, "year": dt.year, "desc": f"วัน:{d_val}, วันที่:{date_val}, {l_type}:{moon_num}, เดือน:{month_val}, นักษัตร:{zv}, ธาตุ:{ev}"}

# --- 2. ENGINE: ตีความเกณฑ์เลขหน้าสุด (0-9) ---
def get_interpretation(val):
    # ดึงเลขตัวแรกสุดที่ไม่ใช่ 0 หรือจุด
    s_val = str(abs(val)).replace('.', '').lstrip('0')
    digit = int(s_val[0]) if s_val else 0
    
    if digit in [0, 5]: return digit, "⚖️ สมดุลคงที่ (ค่ากลาง)", "#00f3ff"
    elif 1 <= digit <= 4: return digit, "⚠️ ไม่สู้ดี (ไม่ดีพอ)", "#ff4b4b"
    else: return digit, "🔥 ดีถึงดีมาก (มีแนวโน้มพัฒนา)", "#00ff00"

# --- 3. UI: ส่วนแสดงผล ---
st.title("🔢 SYNAPSE PARALLEL DECODER (1960-2026)")

tab1, tab2 = st.tabs(["👤 วิเคราะห์บุคคล", "👥 วิเคราะห์คู่ขนาน"])

# --- หน้าบุคคล ---
with tab1:
    u_birth = st.date_input("ระบุวันเกิดของคุณ", value=None, min_value=date(1960,1,1), max_value=date(2026,12,31), key="u_input")
    if u_birth:
        data = get_raw_coordinate(u_birth)
        age = 2026 - data['year']
        
        # สูตร: (รหัสพิกัด + อายุ) / 1.618
        final_p_code = (data['code'] + age) / 1.618
        digit, grade, color = get_interpretation(final_p_code)
        
        st.markdown(f"""
        <div style="background:#111; padding:20px; border:2px solid {color}; border-radius:15px; text-align:center;">
            <p>รหัสพิกัด: {round(data['code'], 2)} | อายุ: {age}</p>
            <h1 style="color:{color}; font-size:50px;">{round(final_p_code, 4)}</h1>
            <h2 style="color:{color};">เลขหน้าคือ {digit}: {grade}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # สแกน อดีต/อนาคต
        st.write("---")
        st.subheader("🕒 รายงานไทม์ไลน์บุคคล (730 วัน)")
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("🗓️ **อดีต 365 วัน**")
            past_events = []
            for i in range(-365, 0):
                target = date.today() + timedelta(days=i)
                t_data = get_raw_coordinate(target)
                t_digit, _, _ = get_interpretation(t_data['code'])
                if t_digit == digit:
                    past_events.append({"วันที่": target.strftime("%d/%m/%Y"), "รหัส": round(t_data['code'], 2)})
            st.table(past_events[:5])
            
        with col_b:
            st.write("🗓️ **อนาคต 365 วัน**")
            future_events = []
            for i in range(1, 366):
                target = date.today() + timedelta(days=i)
                t_data = get_raw_coordinate(target)
                t_digit, _, _ = get_interpretation(t_data['code'])
                if t_digit == digit:
                    future_events.append({"วันที่": target.strftime("%d/%m/%Y"), "รหัส": round(t_data['code'], 2)})
            st.table(future_events[:5])

# --- หน้าคู่ขนาน ---
with tab2:
    st.write("### 🧬 ค้นหาจุดบรรจบของคน 2 คน")
    c1, c2 = st.columns(2)
    with c1: birth_a = st.date_input("วันเกิดคนที่ 1", value=None, key="p1", min_value=date(1960,1,1))
    with c2: birth_b = st.date_input("วันเกิดคนที่ 2", value=None, key="p2", min_value=date(1960,1,1))
    
    if birth_a and birth_b:
        res_a = get_raw_coordinate(birth_a)
        res_b = get_raw_coordinate(birth_b)
        
        # สูตร: (A + B) / 1.618
        p_code = (res_a['code'] + res_b['code']) / 1.618
        p_digit, p_grade, p_color = get_interpretation(p_code)
        
        st.markdown(f"""
        <div style="background:#000; padding:25px; border:3px solid gold; border-radius:20px; text-align:center;">
            <h3 style="color:gold;">CO-RESONANCE CODE</h3>
            <h1 style="color:white; font-size:60px;">{round(p_code, 4)}</h1>
            <h2 style="color:{p_color};">เลขหน้าคือ {p_digit}: {p_grade}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # สแกนไทม์ไลน์คู่ขนาน
        st.write("---")
        st.subheader("⏳ จุด Sync คู่ขนานในอนาคต (365 วัน)")
        p_future = []
        for i in range(1, 366):
            target = date.today() + timedelta(days=i)
            t_data = get_raw_coordinate(target)
            t_digit, _, _ = get_interpretation(t_data['code'])
            if t_digit == p_digit:
                p_future.append({"วันที่": target.strftime("%d/%m/%Y"), "สถานะ": "พลังงานบรรจบ"})
        st.table(p_future[:5])
