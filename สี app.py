import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import math
import os
import base64

# --- 1. CONFIG & CSS (ลบติ่ง + โลโก้ดิ้น + ตัวหนังสือวิ่ง) ---
st.set_page_config(page_title="SYNAPSE : THE TRUTH", layout="wide")

def get_base64_img(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

logo_data = get_base64_img("logo1.png")

st.markdown(f"""
    <style>
    /* ลบติ่ง Streamlit */
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background-color: #000000; color: #00ff41; font-family: monospace; }}
    
    /* โลโก้ดิ้นได้ (Pulse Animation) */
    .logo-box {{
        display: block; margin: 0 auto; width: 120px; height: 120px;
        background-image: url("data:image/png;base64,{logo_data}");
        background-size: contain; background-repeat: no-repeat;
        animation: pulse 1.5s infinite alternate;
    }}
    @keyframes pulse {{
        from {{ filter: drop-shadow(0 0 2px #00ff41); transform: scale(1); }}
        to {{ filter: drop-shadow(0 0 15px #00ff41); transform: scale(1.05); }}
    }}

    /* ตัวหนังสือวิ่ง (Neon Marquee) */
    .marquee {{
        width: 100%; overflow: hidden; white-space: nowrap;
        background: #111; color: #00ff41; padding: 5px 0;
        border-top: 1px solid #00ff41; border-bottom: 1px solid #00ff41;
        margin: 10px 0;
    }}
    .marquee span {{ display: inline-block; animation: marquee 15s linear infinite; }}
    @keyframes marquee {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}

    .formula-note {{ background: #0e161f; padding: 10px; border-left: 3px solid #ff00de; font-size: 0.85rem; color: #ccc; }}
    </style>
    <div class="logo-box"></div>
    <div class="marquee"><span>🛰️ SYNAPSE CORE ONLINE : กำลังเชื่อมต่อพิกัดดาราศาสตร์... ระบบถอดรหัสความจริง 365 วัน พร้อมทำงาน...</span></div>
""", unsafe_allow_html=True)

# --- 2. CORE LOGIC (สูตรคำนวณที่อธิบายได้จริง) ---
def calculate_synapse(dt):
    if dt is None: return None
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    # หาตำแหน่งดวงจันทร์ (ตำแหน่งที่อยู่ในรอบ 29.5 วัน)
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1 # จันทร์=1, อาทิตย์=7
    
    is_waxing = pos <= 14.765
    m_num = int(pos) + 1 if is_waxing else int(pos - 14.765) + 1
    
    # คำอธิบายสูตรตามหลักเจ้านาย
    if is_waxing:
        # สูตรพีทาโกรัส: หาความสั้นสะเทือนในแนวทแยง (Vector)
        res = math.sqrt((day_val**2) + (m_num**2))
        formula = f"√({day_val}² + {m_num}²)"
        explanation = f"ฐานวัน ({day_val}) และข้างขึ้น ({m_num}) รวมพลังงานแบบ Vector"
    else:
        # สูตร Golden Ratio: หาจุดสมดุลความถี่ช่วงแรม
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula = f"({day_val} × 1.618) / {m_num}"
        explanation = f"ฐานวัน ({day_val}) คูณค่าฟี (1.618) หารด้วยค่าข้างแรม ({m_num}) เพื่อหาจุดสัดส่วนทองคำ"

    return {
        "res": round(res, 4), "phase": f"{'ขึ้น' if is_waxing else 'แรม'} {m_num} ค่ำ",
        "day": ["จันทร์","อังคาร","พุธ","พฤหัสบดี","ศุกร์","เสาร์","อาทิตย์"][dt.weekday()],
        "formula": formula, "explanation": explanation, "balance": round(m_num - 7.5, 2)
    }

# --- 3. MAIN INTERFACE ---
st.title("🛰️ SYNAPSE : ระบบวัดค่ารหัสชีวิต")

# เลือกช่วงวันที่ตามที่เจ้านายต้องการ
user_dob = st.date_input("👤 ระบุวันเกิดของคุณ (1960 - 2026)", 
                         value=None, 
                         min_value=date(1960, 1, 1), 
                         max_value=date(2026, 12, 31))

if user_dob:
    u = calculate_synapse(user_dob)
    my_code = u['res']
    
    col1, col2, col3 = st.columns(3)
    col1.metric("รหัสของคุณ", my_code)
    col2.metric("พิกัดจันทรคติ", u['phase'])
    col3.metric("จุดสมดุล (7.5)", u['balance'])
    
    st.markdown(f"""<div class="formula-note">
        <b>ที่มาตัวเลข:</b> {u['explanation']}<br>
        <b>สมการทางคณิตศาสตร์:</b> <code>{u['formula']}</code>
    </div>""", unsafe_allow_html=True)

    st.divider()

    # --- 4. เครื่องวัดคู่ขนาน & สแกน 365 วัน (อดีต/อนาคต) ---
    st.subheader("🔍 เครื่องสแกนพิกัดคู่ขนาน 730 วัน (อดีต 365 + อนาคต 365)")
    
    results = []
    base_date = date.today()
    # สแกนย้อนหลัง 365 และอนาคต 365
    for i in range(-365, 366):
        d_check = base_date + timedelta(days=i)
        l = calculate_synapse(d_check)
        gap = abs(my_code - l['res'])
        
        status = ""
        if gap < 0.5: status = "💎 บรรจบ"
        elif 3.8 <= gap <= 4.2: status = "🌀 สะท้อน"
        
        if status:
            results.append({
                "วันที่": d_check.strftime("%d/%m/%Y"),
                "สถานะ": status,
                "Gap": round(gap, 4),
                "รหัสวัน": l['res'],
                "ที่มา": l['formula']
            })

    if results:
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)
        st.info("💡 ตัวเลข Gap เกิดจาก: |รหัสคุณ - รหัสวันนั้น| เพื่อหาจุดที่ความถี่ตรงกัน")
    else:
        st.write("ไม่พบพิกัดพิเศษในช่วง 2 ปีนี้")

# --- 5. ระบบ MUSIC DECK & รายชื่อเพลง ---
st.divider()
st.subheader("🎵 SYNAPSE MUSIC DECK")

# ดึงรายชื่อเพลงจากโฟลเดอร์ปัจจุบัน (ไฟล์ .mp3, .wav)
music_files = [f for f in os.listdir('.') if f.endswith(('.mp3', '.wav'))]

if music_files:
    st.write(f"พบเพลงในระบบทั้งหมด: {len(music_files)} เพลง")
    selected_song = st.selectbox("เลือกเพลงที่จะเล่น", music_files)
    
    # แสดงลิสต์เพลงทั้งหมดแบบตาราง
    with st.expander("📂 ดูรายชื่อเพลงทั้งหมดในเครื่อง"):
        st.table(pd.DataFrame(music_files, columns=["ชื่อไฟล์เพลง"]))
    
    # เครื่องเล่นเพลง
    if selected_song:
        audio_file = open(selected_song, 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/mp3')
else:
    st.warning("📂 ไม่พบไฟล์เพลง (.mp3) ในโฟลเดอร์เดียวกับโปรแกรม")

st.caption(f"SYNAPSE v5.0 | ID: Ta101 | 'อยู่นิ่งๆ ไม่เจ็บตัว' | {date.today().year}")
