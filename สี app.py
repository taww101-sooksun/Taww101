import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import math
import os
import base64
import firebase_admin
from firebase_admin import credentials, db

# --- 1. SETTING & CSS (ลบติ่ง + โลโก้ดิ้น + หนังสือวิ่ง) ---
st.set_page_config(page_title="SYNAPSE COMMAND", layout="wide")

# ลบส่วนเกิน Streamlit ให้แอปดูเป็นระบบส่วนตัว
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    .stApp { background-color: #000000; color: #00ff41; font-family: 'Courier New', monospace; }
    
    /* โลโก้ดิ้นได้ */
    .logo-pulse {
        display: block; margin: 0 auto; width: 100px; height: 100px;
        background-color: #00ff41; clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%); /* รูปทรง Diamond */
        animation: pulse 2s infinite alternate;
    }
    @keyframes pulse { from { opacity: 0.5; transform: scale(0.9); } to { opacity: 1; transform: scale(1.1); } }

    /* ตัวหนังสือวิ่ง */
    .marquee {
        width: 100%; overflow: hidden; background: #0a0e14; color: #00ff41; 
        padding: 10px; border: 1px solid #00ff41; margin: 10px 0;
    }
    .marquee-text { display: inline-block; animation: marquee 15s linear infinite; }
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    </style>
    <div class="logo-pulse"></div>
    <div class="marquee"><div class="marquee-text">🛰️ SYNAPSE SYSTEM ONLINE : ปรับพิกัดฐานวันศุกร์ = 5 สำเร็จ... ตรวจสอบความถูกต้องของเลขรหัสชีวิต...</div></div>
""", unsafe_allow_html=True)

# --- 2. CORE LOGIC (สูตรที่ไม่คลาดเคลื่อน) ---
def get_verified_logic(dt):
    if dt is None: return None
    
    # [1] ฐานวันที่อ้างอิง (เพื่อหาจำนวนวันที่ผ่านไปจริง)
    ref_date = date(1900, 1, 1)
    diff_days = (dt - ref_date).days
    
    # [2] คำนวณพิกัดจันทรคติ (Lunar Cycle 29.53 วัน)
    lunar_pos = (diff_days - 0.5) % 29.530589
    is_waxing = lunar_pos <= 14.765
    # ค่า "ค่ำ" (m_num)
    m_num = int(lunar_pos) + 1 if is_waxing else int(lunar_pos - 14.765) + 1
    
    # [3] ฐานวัน (เจ้านายกำหนด: ศุกร์=5)
    # Python weekday(): จันทร์=0, ..., ศุกร์=4, เสาร์=5, อาทิตย์=6
    # ดังนั้นต้อง +1 เพื่อให้ จันทร์=1 และ ศุกร์=5 ตรงตามที่เจ้านายสั่ง
    day_val = dt.weekday() + 1 
    
    # [4] การบวกลบเลขรหัส (ตามกฎความจริง)
    if is_waxing:
        # สูตร Vector: ใช้ทฤษฎีแรงดึงดูดรวมตัว
        # ที่มา: √(วัน² + ค่ำ²)
        res = math.sqrt((day_val**2) + (m_num**2))
        formula = f"√({day_val}² + {m_num}²)"
        explain = f"ช่วงข้างขึ้น: นำค่าวัน ({day_val}) และค่าค่ำ ({m_num}) มาหาแรงเหวี่ยงหนีศูนย์กลาง"
    else:
        # สูตร Ratio: ใช้กฎสัดส่วนทองคำกระจายตัว
        # ที่มา: (วัน * 1.618) / ค่ำ
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula = f"({day_val} × 1.618) ÷ {m_num}"
        explain = f"ช่วงข้างแรม: นำค่าวัน ({day_val}) ปรับค่าฟี (1.618) แล้วหารด้วยความถี่แรม ({m_num})"

    return {
        "res": round(res, 4),
        "phase": f"{'ขึ้น' if is_waxing else 'แรม'} {m_num} ค่ำ",
        "formula": formula,
        "explain": explain,
        "day_name": ["จันทร์","อังคาร","พุธ","พฤหัสบดี","ศุกร์","เสาร์","อาทิตย์"][dt.weekday()]
    }

# --- 3. UI: COMMAND CENTER ---
st.title("🛡️ SYNAPSE COMMAND : ระบบวิเคราะห์ความจริง")

user_dob = st.date_input("👤 กรอกวันเกิดเพื่อสแกนรหัส (1960-2026)", 
                         value=date(1984, 5, 18), # 18 พ.ค. 1984
                         min_value=date(1960,1,1), 
                         max_value=date(2026,12,31))

if user_dob:
    u = get_verified_logic(user_dob)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("รหัสประจำตัวคุณ", u['res'])
        st.write(f"📅 **ฐานวัน:** {u['day_name']} (ค่าเลข = {user_dob.weekday()+1})")
    with col2:
        st.metric("พิกัดดวงจันทร์", u['phase'])
        st.write(f"🌙 **ตำแหน่ง:** {u['explain']}")

    st.info(f"🧬 **สูตรคำนวณที่ใช้:** {u['formula']} | ยืนยันพิกัดศุกร์=5 สำเร็จ")

    # --- 4. เครื่องวัดคู่ขนาน (อดีต 365 + อนาคต 365) ---
    st.divider()
    st.subheader("🔍 เครื่องสแกนพิกัดคู่ขนาน 730 วัน")
    
    special_points = []
    today = date.today()
    for i in range(-365, 366):
        d = today + timedelta(days=i)
        l = get_logic_data = get_verified_logic(d)
        gap = abs(u['res'] - l['res'])
        
        status = ""
        if gap < 0.5: status = "💎 บรรจบ"
        elif 3.8 <= gap <= 4.2: status = "🌀 สะท้อน"
        
        if status:
            special_points.append({
                "วันที่": d.strftime("%d/%m/%Y"),
                "สถานะ": status,
                "Gap": round(gap, 4),
                "รหัสวัน": l['res'],
                "สูตรที่มา": l['formula']
            })

    if special_points:
        st.dataframe(pd.DataFrame(special_points), use_container_width=True)
    else:
        st.write("ไม่พบพิกัดพิเศษในช่วง 2 ปีนี้ (อยู่นิ่งๆ ไม่เจ็บตัว)")

# --- 5. รายชื่อเพลงจากเครื่อง + กราฟเสียง ---
st.divider()
st.subheader("🎵 SYNAPSE AUDIO & LIST")
songs = [f for f in os.listdir('.') if f.endswith(('.mp3', '.wav'))]

if songs:
    st.write(f"📂 รายชื่อเพลงในระบบ (Total: {len(songs)})")
    st.table(pd.DataFrame(songs, columns=["File Name"]))
    
    sel = st.selectbox("เลือกเพลงเล่นเพื่อดูคลื่นความถี่", songs)
    # กราฟคลื่นเสียงจำลอง
    freq_data = pd.DataFrame(np.random.randn(30, 1), columns=['Frequency'])
    st.line_chart(freq_data, color="#ff00de")
    
    with open(sel, "rb") as f:
        st.audio(f.read())
else:
    st.warning("ไม่พบไฟล์เพลงในโฟลเดอร์")

st.caption(f"SYNAPSE v6.5 | 'อยู่นิ่งๆ ไม่เจ็บตัว' | {date.today().year}")
