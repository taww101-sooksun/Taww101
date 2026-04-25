import streamlit as st
from datetime import date, timedelta

# --- ฟังก์ชันดึงเลขฐาน (โชว์ให้เห็นว่ามาจากไหน) ---
def get_step_by_step_data(dt):
    if dt is None: return None
    
    # 1. วันเกิด (จันทร์-อาทิตย์)
    day_val = {0:1, 1:2, 2:3, 3:4, 4:5, 5:6, 6:7}[dt.weekday()]
    day_name = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"][dt.weekday()]
    
    # 2. วันที่ตรงๆ
    date_val = dt.day

    # 3. ข้างขึ้นข้างแรม
    ref = date(1900, 1, 1)
    diff = (dt - ref).days
    lunar_pos = (diff - 0.5) % 29.530589
    if lunar_pos <= 14.765:
        moon_num = int(lunar_pos) + 1
        l_logic = -7.5
        l_type = f"ขึ้น {moon_num} ค่ำ (ไกลโลก)"
    else:
        moon_num = int(lunar_pos - 14.765) + 1
        l_logic = 7.5
        l_type = f"แรม {moon_num} ค่ำ (ใกล้โลก)"

    # 4. เดือน
    month_val = dt.month

    # 5. ปีนักษัตร
    z_names = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
    z_map = {0:9, 1:10, 2:11, 3:12, 4:1, 5:2, 6:3, 7:4, 8:5, 9:6, 10:7, 11:8}
    zv = z_map[dt.year % 12]
    z_name = z_names[dt.year % 12]

    # 6. ธาตุ
    m, d = dt.month, dt.day
    if (m == 5 and d >= 14) or (m == 6 and d <= 14): ev, en = 1, "ดิน"
    elif (m == 7 and d >= 16) or (m == 8 and d <= 16): ev, en = 2, "น้ำ"
    elif (m == 4 and d >= 13) or (m == 5 and d <= 13): ev, en = 4, "ไฟ"
    else: ev, en = 3, "ลม"

    return {
        "day": day_val, "day_n": day_name, "date": date_val, 
        "moon": moon_num, "l_logic": l_logic, "l_type": l_type,
        "month": month_val, "zv": zv, "zn": z_name, 
        "ev": ev, "en": en, "year": dt.year
    }

def get_grade_info(val):
    s_val = str(abs(val)).replace('.', '').lstrip('0')
    digit = int(s_val[0]) if s_val else 0
    if digit in [0, 5]: return digit, "⚖️ สมดุลคงที่ (ค่ากลาง)", "#00f3ff"
    elif 1 <= digit <= 4: return digit, "⚠️ ไม่สู้ดี (ไม่ดีพอ)", "#ff4b4b"
    else: return digit, "🔥 ดีถึงดีมาก (พัฒนาได้)", "#00ff00"

# --- หน้าจอแอป ---
st.title("🔢 SYNAPSE STEP-BY-STEP")

u_birth = st.date_input("กรอกวันเกิดของคุณ", value=None, min_value=date(1960,1,1), max_value=date(2026,12,31))

if u_birth:
    d = get_step_by_step_data(u_birth)
    today = date.today()
    
    # คำนวณจำนวนวันที่ใช้ชีวิตมาทั้งหมด (แทนการใช้แค่อายุปี)
    days_alive = (today - u_birth).days
    
    st.markdown("### ⚙️ ขั้นตอนการประมวลผล (พิกัดไหลเวียน)")
    
    # Step 1 & 2 เหมือนเดิม (หาค่าพื้นฐานตัวตน)
    base_sum = d['day'] + d['date'] + d['moon'] + d['month'] + d['zv'] + d['ev']
    raw_code = (base_sum + d['l_logic']) * 1.618
    
    # Step 3 เปลี่ยนจาก "อายุ" เป็น "จำนวนวันชีวิต (Days Flow)"
    # สมมติอายุปัจจุบัน 42 ปี = ประมาณ 15,330 วัน
    final_val = (raw_code + days_alive) / 1.618
    
    st.write(f"**Step 1:** ผลรวมพิกัด 6 มิติ = `{base_sum}`")
    st.write(f"**Step 2:** จูนจันทร์และขยายด้วย 1.618 ➔ `{round(raw_code, 4)}`")
    st.write(f"**Step 3:** บวกพิกัดวันชีวิตที่ใช้มา ({days_alive} วัน) แล้วหาร 1.618")
    st.info(f"สูตร: ({round(raw_code, 2)} + {days_alive}) ÷ 1.618 = **{round(final_val, 4)}**")
if birth_a and birth_b:
    st.write("---")
    st.subheader("🧬 การประมวลผลมิติคู่ขนาน (Parallel Step)")
    
    # ดึงเลขฐานของทั้ง 2 คน
    d1 = get_step_by_step_data(birth_a)
    d2 = get_step_by_step_data(birth_b)
    
    # คำนวณรหัสพื้นฐาน (Raw Code) ของแต่ละคนก่อน
    sum1 = d1['day'] + d1['date'] + d1['moon'] + d1['month'] + d1['zv'] + d1['ev']
    raw1 = (sum1 + d1['l_logic']) * 1.618
    
    sum2 = d2['day'] + d2['date'] + d2['moon'] + d2['month'] + d2['zv'] + d2['ev']
    raw2 = (sum2 + d2['l_logic']) * 1.618
    
    # โชว์ตารางเปรียบเทียบเลขฐาน
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"**👤 พิกัดคนที่ 1**\n- เลขรวมฐาน: `{sum1}`\n- จูนจันทร์: `{d1['l_logic']}`\n- **รหัสบุคคล: {round(raw1, 2)}**")
    with col_b:
        st.markdown(f"**👤 พิกัดคนที่ 2**\n- เลขรวมฐาน: `{sum2}`\n- จูนจันทร์: `{d2['l_logic']}`\n- **รหัสบุคคล: {round(raw2, 2)}**")
    
    st.write("---")
    # ขั้นตอนการรวม (Fusion)
    parallel_sum = raw1 + raw2
    resonance_code = parallel_sum / 1.618
    
    st.markdown("### ⚙️ ขั้นตอนการรวมพิกัด")
    st.write(f"**Step 1 (Fusion):** นำรหัสทั้งคู่มาบวกกัน ➔ `{round(raw1, 2)} + {round(raw2, 2)} = {round(parallel_sum, 2)}`")
    st.write(f"**Step 2 (Resonance):** หารด้วยค่าสมดุลทองคำ ➔ `{round(parallel_sum, 2)} ÷ 1.618 = {round(resonance_code, 4)}`")
    
    # วัดเกณฑ์เลขหน้าสุด
    digit_p, grade_p, color_p = get_grade_info(resonance_code)
    
    st.markdown(f"""
    <div style="background:#000; padding:25px; border:4px solid gold; border-radius:20px; text-align:center;">
        <h3 style="color:gold; margin:0;">CO-RESONANCE CODE</h3>
        <h1 style="color:white; font-size:65px; margin:10px 0;">{round(resonance_code, 4)}</h1>
        <h2 style="color:{color_p};">เลขหน้าสุดคือ {digit_p} : {grade_p}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # ตารางอนาคต (365 วัน) - โชว์ว่ารหัสนี้จะไป Sync กับวันไหน
    st.write("🗓️ **จุดนัดพบในอนาคต (วันที่รหัสโลกตรงกับรหัสคู่ขนานคุณ):**")
    p_future = []
    for i in range(1, 366):
        target = date.today() + timedelta(days=i)
        td = get_step_by_step_data(target)
        t_sum = td['day'] + td['date'] + td['moon'] + td['month'] + td['zv'] + td['ev']
        t_code = (t_sum + td['l_logic']) * 1.618
        
        t_digit, _, _ = get_grade_info(t_code)
        if t_digit == digit_p:
            p_future.append({"วันที่": target.strftime("%d/%m/%Y"), "พิกัดวันนั้น": round(t_code, 2)})
    
    if p_future:
        st.table(p_future[:5]) # โชว์ 5 วันสำคัญในอนาคต

    # สรุปผลด้วยเกณฑ์ 0-9 หน้าสุด
    digit, grade, color = get_grade_info(final_val)
    st.markdown(f"""
    <div style="background:#000; padding:20px; border:4px solid {color}; border-radius:15px; text-align:center;">
        <h1 style="color:{color}; font-size:60px;">{round(final_val, 4)}</h1>
        <h2 style="color:{color};">เลขหน้าคือ {digit} : {grade}</h2>
        <p style="color:#888;">*พิกัดนี้จะเปลี่ยนไปในทุกๆ 24 ชม. ตามการหมุนของโลก</p>
    </div>
    """, unsafe_allow_html=True)

    d = get_step_by_step_data(u_birth)
    
    st.markdown("### 🛠 กระดานแยกพิกัดตัวเลข (Raw Data)")
    st.markdown(f"""
    1. **พิกัดวัน:** วัน{d['day_n']} = `{d['day']}`
    2. **พิกัดวันที่:** วันที่ {d['date']} = `{d['date']}`
    3. **พิกัดดวงจันทร์:** {d['l_type']} = `{d['moon']}` (ปรับค่า: `{d['l_logic']}`)
    4. **พิกัดเดือน:** เดือน {d['month']} = `{d['month']}`
    5. **พิกัดนักษัตร:** ปี{d['zn']} = `{d['zv']}`
    6. **พิกัดธาตุ:** ธาตุ{d['en']} = `{d['ev']}`
    """)
    
    st.write("---")
    st.markdown("### ⚙️ ขั้นตอนการประมวลผล")
    
    # ขั้นตอนที่ 1
    base_sum = d['day'] + d['date'] + d['moon'] + d['month'] + d['zv'] + d['ev']
    st.write(f"**Step 1:** นำเลขทั้ง 6 มาบวกกัน ➔ `{d['day']} + {d['date']} + {d['moon']} + {d['month']} + {d['zv']} + {d['ev']} = {base_sum}`")
    
    # ขั้นตอนที่ 2
    raw_code = (base_sum + d['l_logic']) * 1.618
    st.write(f"**Step 2:** ปรับค่าสมดุลจันทร์ ({d['l_logic']}) แล้วคูณ 1.618 ➔ `({base_sum} + {d['l_logic']}) × 1.618 = {round(raw_code, 4)}`")
    
    # ขั้นตอนที่ 3
    age = 2026 - d['year']
    final_val = (raw_code + age) / 1.618
    st.write(f"**Step 3:** บวกอายุปัจจุบัน ({age}) แล้วหาร 1.618 ➔ `({round(raw_code, 2)} + {age}) ÷ 1.618 = {round(final_val, 4)}`")

    # สรุปผล
    digit, grade, color = get_grade_info(final_val)
    st.markdown(f"""
    <div style="background:#000; padding:20px; border:4px solid {color}; border-radius:15px; text-align:center; margin-top:20px;">
        <h1 style="color:{color}; font-size:60px; margin:0;">{round(final_val, 4)}</h1>
        <h2 style="color:{color};">เลขหน้าสุดคือ {digit} : {grade}</h2>
    </div>
    """, unsafe_allow_html=True)
