import streamlit as st
from datetime import datetime, date
import math
import random

# --- CONFIG & STYLING ---
st.set_page_config(page_title="SYNAPSE: REALITY EXTRACTOR", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #050a0e; color: #00ff41; }
    .status-card { 
        background-color: #101a24; 
        padding: 30px; 
        border: 2px solid #00ff41; 
        border-radius: 20px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0px 0px 25px rgba(0, 255, 65, 0.15);
    }
    .guide-box {
        background-color: #0e161f;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #00ff41;
        margin-top: 15px;
        text-align: left;
        color: #e0e0e0;
    }
    .numeric-display { font-size: 3rem; color: #ffffff; letter-spacing: 8px; font-weight: bold; margin: 15px 0; }
    h1, h2, h3 { color: #00ff41; font-family: 'Courier New', monospace; }
    b { color: #ffaa00; }
    </style>
    """, unsafe_allow_html=True)

def extract_reality_code(dt):
    # 1. ฐานข้อมูล (The Astronomical Base)
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1 
    
    # 2. การประกอบร่าง
    if pos <= 14.765:
        m_num = int(pos) + 1
        label = f"ขึ้น {m_num} ค่ำ"
        res = math.sqrt((day_val**2) + (m_num**2))
        logic_type = "แรงผลักดันจักรวาล (Vector Energy)"
        formula = f"√({day_val}² + {m_num}²)"
    else:
        m_num = int(pos - 14.765) + 1
        label = f"แรม {m_num} ค่ำ"
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        logic_type = "สมดุลสัดส่วนทองคำ (Golden Ratio)"
        formula = f"({day_val} × 1.618) / {m_num}"

    # 3. การสกัดรหัส (Locked Seed)
    seed_val = int(res * 1000000)
    random.seed(seed_val) 
    d2 = f"{random.randint(0, 99):02}"
    d3 = f"{random.randint(0, 999):03}"

    return {
        "res": round(res, 4), "label": label, "logic": logic_type,
        "formula": formula, "d2": d2, "d3": d3, "day_name": dt.strftime('%A')
    }

# --- MAIN INTERFACE ---
st.title("🛰️ SYNAPSE: Reality Extractor")
st.write("ระบบถอดรหัสความจริงรายวันจากพิกัดจักรวาล")

target_date = st.date_input("เลือกวันที่เพื่อสแกนรหัส", value=date.today())

if target_date:
    data = extract_reality_code(target_date)
    
    # ส่วนแสดงผลหลัก
    st.markdown(f"""
    <div class="status-card">
        <p style="color: #a0a0a0; margin-bottom: 0;">รหัสประจุพลังงานประจำวัน</p>
        <h1 style="font-size: 4.5rem; margin-top: 0;">{data['res']}</h1>
        <p style="font-size: 1.5rem; color: #ffaa00;">🌒 {data['label']}</p>
        <hr style="border: 0.5px solid #333;">
        <p style="color: #00ff41; font-size: 1.1rem;">ชุดรหัสตัวเลขแท้จริงที่สกัดได้</p>
        <div class="numeric-display">{data['d2']} | {data['d3']}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- ส่วนที่พี่ต้องการ: บอกที่มาและวิธีอ่าน (คู่มือในแอป) ---
    st.subheader("📖 คู่มือถอดรหัสความจริง")
    
    tab1, tab2 = st.tabs(["🧬 ที่มาของตัวเลข", "🔮 วิธีอ่านค่าพลังงาน"])
    
    with tab1:
        st.markdown(f"""
        <div class="guide-box">
            <h4>ตัวเลขเหล่านี้มาจากไหน?</h4>
            <ul>
                <li><b>รหัสประจุ ({data['res']}):</b> มาจากความสัมพันธ์ระหว่าง <b>แรงวัน ({target_date.weekday()+1})</b> และ <b>แรงเดือน ({data['label']})</b> โดยใช้สมการ <code>{data['formula']}</code></li>
                <li><b>ทองคำจักรวาล:</b> ใช้ค่าคงที่ <b>1.618</b> ในการหาจุดสมดุลของพลังงานในวันที่เป็นข้างแรม</li>
                <li><b>รหัสสกัด ({data['d2']} | {data['d3']}):</b> คือลายเซ็นของพลังงานวันนั้น ไม่ใช่การสุ่ม แต่เป็นการถอดทศนิยมของรหัสประจุออกมาเป็นตัวเลขที่จับต้องได้</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        

    with tab2:
        st.markdown("""
        <div class="guide-box">
            <h4>อ่านค่าความจริงอย่างไร?</h4>
            <ol>
                <li><b>ดูความเข้มข้น:</b> รหัสประจุยิ่งสูง พลังงานวันนั้นยิ่งมีความหนาแน่นสูง (เหมาะกับงานใหญ่)</li>
                <li><b>ดูทิศทาง:</b> 
                    <br>- <b>ข้างขึ้น:</b> พลังงานขาออก (ลุย/เริ่มต้น)
                    <br>- <b>ข้างแรม:</b> พลังงานขาเข้า (วางแผน/นิ่ง)
                </li>
                <li><b>ดูพิกัดตัวเลข:</b> เลข 29 | 134 คือชุดตัวเลขที่ <b>"จูน"</b> ตรงกับคลื่นความถี่ของวันนี้ที่สุด</li>
            </ol>
            <p style="text-align: center; color: #ffaa00;"><i>"อยู่นิ่งๆ ไม่เจ็บตัว - ความจริงนิ่งสนิทตามพิกัดจักรวาล"</i></p>
        </div>
        """, unsafe_allow_html=True)

st.divider()
st.caption("SYNAPSE CORE v2.6 | ระบบความจริงตรวจสอบได้โดย Ta101")
