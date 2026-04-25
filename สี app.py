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
