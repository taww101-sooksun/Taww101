import datetime
import math

def get_synapse_report(dt):
    if dt is None: return None
    
    # --- 1. แปลงค่าวัน (คุณต๊ะใช้ ศุกร์=5) ---
    # มาตรฐานคุณต๊ะ: อาทิตย์=7, จันทร์=1, อังคาร=2, พุธ=3, พฤหัส=4, ศุกร์=5, เสาร์=6
    # (โค้ดดึงวัน: จันทร์=0...อาทิตย์=6)
    day_map = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7}
    day_val = day_map[dt.weekday()]
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    
    # --- 2. ค่าวันที่ตรงๆ ---
    date_val = dt.day
    
    # --- 3. ค่าเดือน (1-12) ---
    month_val = dt.month
    month_names = ["", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน", 
                   "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
    
    # --- 4. คำนวณข้างขึ้นแรม และหาค่าค่ำ (moon_num) ---
    ref_date = datetime.date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_pos = (diff - 0.5) % 29.530589
    
    if lunar_pos <= 14.765:
        moon_num = int(lunar_pos) + 1
        phase_text = f"ขึ้น {moon_num} ค่ำ"
        lunar_logic = -7.5  # ขึ้น ลบ 7.5
        is_waxing = True
    else:
        moon_num = int(lunar_pos - 14.765) + 1
        phase_text = f"แรม {moon_num} ค่ำ"
        lunar_logic = 7.5   # แรม บวก 7.5
        is_waxing = False

    # --- 5. คำนวณปีนักษัตร (ชวด=1, ฉลู=2...) ---
    # ปีชวดเริ่มที่รอบปี 1900, 1912, 1924...
    zodiac_names = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
    zodiac_val_map = {"ชวด":1, "ฉลู":2, "ขาล":3, "เถาะ":4, "มะโรง":5, "มะเส็ง":6, "มะเมีย":7, "มะแม":8, "วอก":9, "ระกา":10, "จอ":11, "กุน":12}
    zodiac_name = zodiac_names[dt.year % 12]
    zodiac_val = zodiac_val_map[zodiac_name]

    # --- 6. วิเคราะห์ราศี และธาตุ (ดิน=1, น้ำ=2, ลม=3, ไฟ=4) ---
    m, d = dt.month, dt.day
    if (m == 4 and d >= 13) or (m == 5 and d <= 13): rasi, elem_text, elem_val = "เมษ", "ไฟ", 4
    elif (m == 5 and d >= 14) or (m == 6 and d <= 14): rasi, elem_text, elem_val = "พฤษภ", "ดิน", 1
    elif (m == 6 and d >= 15) or (m == 7 and d <= 15): rasi, elem_text, elem_val = "เมถุน", "ลม", 3
    elif (m == 7 and d >= 16) or (m == 8 and d <= 16): rasi, elem_text, elem_val = "กรกฎ", "น้ำ", 2
    elif (m == 8 and d >= 17) or (m == 9 and d <= 16): rasi, elem_text, elem_val = "สิงห์", "ไฟ", 4
    elif (m == 9 and d >= 17) or (m == 10 and d <= 16): rasi, elem_text, elem_val = "กันย์", "ดิน", 1
    elif (m == 10 and d >= 17) or (m == 11 and d <= 15): rasi, elem_text, elem_val = "ตุลย์", "ลม", 3
    elif (m == 11 and d >= 16) or (m == 12 and d <= 15): rasi, elem_text, elem_val = "พิจิก", "น้ำ", 2
    elif (m == 12 and d >= 16) or (m == 1 and d <= 14): rasi, elem_text, elem_val = "ธนู", "ไฟ", 4
    elif (m == 1 and d >= 15) or (m == 2 and d <= 12): rasi, elem_text, elem_val = "มังกร", "ดิน", 1
    elif (m == 12 and d >= 13) or (m == 3 and d <= 13): rasi, elem_text, elem_val = "กุมภ์", "ลม", 3
    else: rasi, elem_text, elem_val = "มีน", "น้ำ", 2

    # --- 7. คำนวณรหัสลับ (สูตรคุณต๊ะ 6 พิกัด) ---
    # [วัน + วันที่ + ค่ำ + เดือน + ปีนักษัตร + ธาตุ]
    base_sum = day_val + date_val + moon_num + month_val + zodiac_val + elem_val
    final_code = (base_sum + lunar_logic) * 1.618

    return {
        "report": f"""
        * **วัน:** {day_names[dt.weekday()]} ({day_val})
        * **วันที่:** {date_val}
        * **เดือน:** {month_names[month_val]} ({month_val})
        * **ปีนักษัตร:** {zodiac_name} ({zodiac_val})
        * **ข้างขึ้น/แรม:** {phase_text} ({'ลบ 7.5' if is_waxing else 'บวก 7.5'})
        * **ธาตุ:** {elem_text} ({elem_val})
        * **ราศี:** {rasi}
        """,
        "code": round(final_code, 4)
    }

# --- ส่วน UI ของหน้า 3 ---
elif st.session_state.page == "3":
    st.markdown("<h2 class='neon-text'>🧠 INTELLIGENCE ENGINE</h2>", unsafe_allow_html=True)
    
    # ช่องกรอกแค่วันเดือนปี
    input_date = st.date_input("เลือกวันที่เพื่อสแกนพิกัด (1960 - 2026)", 
                               value=datetime.date.today(),
                               min_value=datetime.date(1960, 1, 1),
                               max_value=datetime.date(2026, 12, 31))

    if st.button("RUN FULL SCAN", use_container_width=True):
        data = get_synapse_report(input_date)
        
        st.write("---")
        st.markdown(data["report"])
        st.markdown(f"""
            <div style="text-align:center; padding:20px; border:2px solid var(--primary); border-radius:15px; background:black;">
                <h1 style="color:cyan; margin:0;">CODE: {data['code']}</h1>
                <p style="color:gray; margin:0;">SYNAPSE LOGIC v1.618</p>
            </div>
        """, unsafe_allow_html=True)
