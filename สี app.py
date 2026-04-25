import streamlit as st
from datetime import date, timedelta

# --- 1. ฟังก์ชันดึงเลขฐาน (ห้ามเอาออก โชว์ที่มาความจริง) ---
def get_step_by_step_data(dt):
    if dt is None: return None
    day_val = {0:1, 1:2, 2:3, 3:4, 4:5, 5:6, 6:7}[dt.weekday()]
    day_name = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"][dt.weekday()]
    date_val = dt.day
    ref = date(1900, 1, 1)
    diff = (dt - ref).days
    lunar_pos = (diff - 0.5) % 29.530589
    if lunar_pos <= 14.765:
        moon_num = int(lunar_pos) + 1
        l_logic = -7.5
        l_type = f"ขึ้น {moon_num} ค่ำ"
    else:
        moon_num = int(lunar_pos - 14.765) + 1
        l_logic = 7.5
        l_type = f"แรม {moon_num} ค่ำ"
    month_val = dt.month
    z_names = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
    z_map = {0:9, 1:10, 2:11, 3:12, 4:1, 5:2, 6:3, 7:4, 8:5, 9:6, 10:7, 11:8}
    zv = z_map[dt.year % 12]
    z_name = z_names[dt.year % 12]
    m, d = dt.month, dt.day
    if (m == 5 and d >= 14) or (m == 6 and d <= 14): ev, en = 1, "ดิน"
    elif (m == 7 and d >= 16) or (m == 8 and d <= 16): ev, en = 2, "น้ำ"
    elif (m == 4 and d >= 13) or (m == 5 and d <= 13): ev, en = 4, "ไฟ"
    else: ev, en = 3, "ลม"
    return {
        "day": day_val, "day_n": day_name, "date": date_val, "moon": moon_num, 
        "l_logic": l_logic, "l_type": l_type, "month": month_val, "zv": zv, 
        "zn": z_name, "ev": ev, "en": en, "year": dt.year
    }

def get_grade_info(val):
    s_val = str(abs(val)).replace('.', '').lstrip('0')
    digit = int(s_val[0]) if s_val else 0
    if digit in [0, 5]: return digit, "⚖️ สมดุลคงที่ (ค่ากลาง)", "#00f3ff"
    elif 1 <= digit <= 4: return digit, "⚠️ ไม่สู้ดี (ไม่ดีพอ)", "#ff4b4b"
    else: return digit, "🔥 ดีถึงดีมาก (พัฒนาได้)", "#00ff00"

# --- 2. หน้าจอแอป ---
st.set_page_config(page_title="SYNAPSE STEP-BY-STEP", layout="wide")
st.title("🔢 SYNAPSE STEP-BY-STEP (1960-2026)")

tab1, tab2 = st.tabs(["👤 วิเคราะห์บุคคล", "👥 วิเคราะห์คู่ขนาน"])

# --- 👤 TAB 1: วิเคราะห์บุคคล ---
with tab1:
    u_birth = st.date_input("กรอกวันเกิดของคุณ", value=None, min_value=date(1960,1,1), max_value=date(2026,12,31), key="single")
    if u_birth:
        d = get_step_by_step_data(u_birth)
        
        st.markdown("### 🛠 กระดานแยกพิกัดตัวเลข")
        st.write(f"1. วัน{d['day_n']}: `{d['day']}` | 2. วันที่: `{d['date']}` | 3. {d['l_type']}: `{d['moon']}`")
        st.write(f"4. เดือน: `{d['month']}` | 5. ปี{d['zn']}: `{d['zv']}` | 6. ธาตุ{d['en']}: `{d['ev']}`")
        
        st.write("---")
        base_sum = d['day'] + d['date'] + d['moon'] + d['month'] + d['zv'] + d['ev']
        raw_code = (base_sum + d['l_logic']) * 1.618
        days_alive = (date.today() - u_birth).days
        final_val = (raw_code + days_alive) / 1.618
        
        st.write(f"**ขั้นตอนที่ 1 (บวกฐาน):** `{d['day']}+{d['date']}+{d['moon']}+{d['month']}+{d['zv']}+{d['ev']} = {base_sum}`")
        st.write(f"**ขั้นตอนที่ 2 (คูณ 1.618):** `({base_sum} + {d['l_logic']}) x 1.618 = {round(raw_code, 2)}`")
        st.write(f"**ขั้นตอนที่ 3 (บวกวันชีวิต/หาร):** `({round(raw_code, 2)} + {days_alive}) / 1.618 = {round(final_val, 4)}`")

        digit, grade, color = get_grade_info(final_val)
        st.markdown(f"""<div style="background:#000; padding:20px; border:4px solid {color}; border-radius:15px; text-align:center;">
            <h1 style="color:{color}; font-size:60px;">{round(final_val, 4)}</h1>
            <h2 style="color:{color};">เลขหน้าคือ {digit} : {grade}</h2>
        </div>""", unsafe_allow_html=True)

        # --- 🕒 สแกนไทม์ไลน์บุคคล ---
        st.write("---")
        st.subheader("🕒 รายงานการบรรจบของพิกัดบุคคล (730 วัน)")
        t_past, t_future = st.tabs(["🗓️ อดีต 365 วัน", "🗓️ อนาคต 365 วัน"])
        
        with t_past:
            past_results = []
            for i in range(-365, 0):
                scan_date = date.today() + timedelta(days=i)
                sd = get_step_by_step_data(scan_date)
                s_sum = sd['day'] + sd['date'] + sd['moon'] + sd['month'] + sd['zv'] + sd['ev']
                s_code = (s_sum + sd['l_logic']) * 1.618
                s_digit, _, _ = get_grade_info(s_code)
                if s_digit == digit:
                    past_results.append({"วันที่": scan_date.strftime("%d/%m/%Y"), "รหัส": round(s_code, 2), "เลขหน้า": s_digit})
            st.table(past_results[:10] if past_results else "ไม่พบข้อมูล")

        with t_future:
            future_results = []
            for i in range(1, 366):
                scan_date = date.today() + timedelta(days=i)
                sd = get_step_by_step_data(scan_date)
                s_sum = sd['day'] + sd['date'] + sd['moon'] + sd['month'] + sd['zv'] + sd['ev']
                s_code = (s_sum + sd['l_logic']) * 1.618
                s_digit, _, _ = get_grade_info(s_code)
                if s_digit == digit:
                    future_results.append({"วันที่": scan_date.strftime("%d/%m/%Y"), "รหัส": round(s_code, 2), "เลขหน้า": s_digit})
            st.table(future_results[:10] if future_results else "ไม่พบข้อมูล")

# --- 👥 TAB 2: วิเคราะห์คู่ขนาน ---
with tab2:
    col1, col2 = st.columns(2)
    with col1: birth_a = st.date_input("วันเกิดคนที่ 1", value=None, key="ba", min_value=date(1960,1,1))
    with col2: birth_b = st.date_input("วันเกิดคนที่ 2", value=None, key="bb", min_value=date(1960,1,1))
    
    if birth_a and birth_b:
        d1 = get_step_by_step_data(birth_a)
        d2 = get_step_by_step_data(birth_b)
        r1 = ((d1['day'] + d1['date'] + d1['moon'] + d1['month'] + d1['zv'] + d1['ev']) + d1['l_logic']) * 1.618
        r2 = ((d2['day'] + d2['date'] + d2['moon'] + d2['month'] + d2['zv'] + d2['ev']) + d2['l_logic']) * 1.618
        
        resonance = (r1 + r2) / 1.618
        digit_p, grade_p, color_p = get_grade_info(resonance)
        
        st.write(f"**ขั้นตอนการรวม:** `({round(r1, 2)} + {round(r2, 2)}) / 1.618 = {round(resonance, 4)}`")
        st.markdown(f"""<div style="background:#000; padding:20px; border:4px solid gold; border-radius:15px; text-align:center;">
            <h1 style="color:white; font-size:60px;">{round(resonance, 4)}</h1>
            <h2 style="color:{color_p};">เลขหน้าคือ {digit_p} : {grade_p}</h2>
        </div>""", unsafe_allow_html=True)

        # --- 🕒 สแกนไทม์ไลน์คู่ขนาน ---
        st.write("---")
        st.subheader("⏳ จุด Sync คู่ขนานในอนาคต (365 วัน)")
        p_future = []
        for i in range(1, 366):
            target = date.today() + timedelta(days=i)
            td = get_step_by_step_data(target)
            t_code = ((td['day'] + td['date'] + td['moon'] + td['month'] + td['zv'] + td['ev']) + td['l_logic']) * 1.618
            t_digit, _, _ = get_grade_info(t_code)
            if t_digit == digit_p:
                p_future.append({"วันที่": target.strftime("%d/%m/%Y"), "พิกัดวันนั้น": round(t_code, 2)})
        st.table(p_future[:10] if p_future else "ไม่พบข้อมูล")
