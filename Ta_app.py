import streamlit as st
import os
from datetime import datetime

# ==========================================
# 1. การตั้งค่าหน้าตาแอปและชุดสี (Theme Customization)
# ==========================================
st.set_page_config(
    page_title="SYNAPSE QUANTUM NUMEROLOGY",
    page_icon="🔮",
    layout="centered"
)

# ใช้ CSS เพื่อลบปุ่ม/เมนู และ Footer ติ่งของ Streamlit ออกให้หมดตามที่บาสต้องการ
# พร้อมปรับแต่งสีสันให้ดูพรีเมียม (พื้นหลังเข้ม ตัวหนังสือชัดเจน ขอบหนาตามสไตล์บาส)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .reportview-container {
        background: #0B0F19;
    }
    h1, h2, h3 {
        color: #00E5FF !important;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #FF1744;
        color: white;
        border-radius: 8px;
        border: 2px solid #00E5FF;
        font-weight: bold;
        width: 100%;
    }
    .quantum-box {
        border: 4px solid #00E5FF;
        padding: 20px;
        border-radius: 12px;
        background-color: #121824;
        margin-bottom: 20px;
    }
    .matrix-title {
        color: #FFD600;
        font-size: 20px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. ส่วนแสดงโลโก้ (ดึงไฟล์ logo1.png จากโฟลเดอร์เดียวกัน)
# ==========================================
st.title("🔮 SYNAPSE COMMAND CENTER")
st.subheader("ระบบวิเคราะห์ถอดรหัสควอนตัมและแพทเทิร์นตัวเลขวันเกิด")

logo_path = "logo1.png"
if os.path.exists(logo_path):
    st.image(logo_path, use_container_width=True)
else:
    st.info("💡 ระบบเตรียมพร้อมรับไฟล์ 'logo1.png' เพื่อแสดงผลที่หน้าแรก")

st.write("---")

# ==========================================
# 3. ส่วนรับข้อมูลจากผู้ใช้งาน
# ==========================================
st.markdown("### 📅 กรอกข้อมูลวันเดือนปีเกิดเพื่อถอดรหัส")

# รับวันเกิดของตัวเอง
col1, col2 = st.columns(2)
with col1:
    my_date = st.date_input("วันเดือนปีเกิดของคุณ", min_value=datetime(1950, 1, 1))
with col2:
    my_time = st.time_input("เวลาเกิดของคุณ (ถ้ามี)", value=None)

# รับวันเกิดของคู่สมพงษ์
partner_check = st.checkbox("ต้องการคำนวณรหัสสมพงษ์ร่วมกับคู่รัก/บุคคลอื่น")
partner_date = None
if partner_check:
    partner_date = st.date_input("วันเดือนปีเกิดของคู่สมพงษ์", min_value=datetime(1950, 1, 1))

# ปุ่มกดคำนวณ
btn_calculate = st.button("เริ่มต้นถอดรหัสควอนตัมแมทริกซ์")

# ==========================================
# 4. ฟังก์ชันและสูตรการคำนวณทางคณิตศาสตร์ (Logic)
# ==========================================
def sum_digits(number):
    """ฟังก์ชันย่อยสำหรับการบวกเลขทีละหลักจนเหลือเลขหลักเดียว (1-9)"""
    while number > 9:
        number = sum(int(digit) for digit in str(number))
    return number

if btn_calculate:
    # แยกส่วนตัวเลขจากวันเกิด (ปี ค.ศ.)
    d = my_date.day
    m = my_date.month
    y = my_date.year
    
    # 🌟 สูตรที่ 1: รหัสอดีต (ฐานจิตใต้สำนึก)
    # วิธีคิด: เอาเลขวันเกิด + เลขเดือนเกิด แล้วลดรูปให้เหลือหลักเดียว
    past_code = sum_digits(d + m)
    
    # 🌟 สูตรที่ 2: รหัสอนาคต (เส้นทางพลังงานชีวิต)
    # วิธีคิด: เอาเลขวัน + เดือน + ปี ค.ศ. มารวมกันทั้งหมด แล้วลดรูปให้เหลือหลักเดียว
    future_code = sum_digits(d + m + y)
    
    # 🌟 สูตรที่ 3: รหัสควอนตัมคู่ขนาน (มิติจิตภาพและพลังที่ซ่อนอยู่)
    # วิธีคิด: เอา (รหัสอดีต x รหัสอนาคต) คูณด้วยตัวเลขเวลาเกิด หรือค่าคงที่ความถี่ควอนตัม (เลข 7) แล้วลดรูป
    parallel_code = sum_digits((past_code * future_code) + 7)
    
    # แสดงผลลัพธ์การคำนวณส่วนบุคคล
    st.markdown("<div class='quantum-box'>", unsafe_allow_html=True)
    st.markdown("## 🌌 ผลการถอดรหัสควอนตัมส่วนบุคคล", unsafe_allow_html=True)
    
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric(label="🧬 รหัสอดีต (Past)", value=past_code)
    with col_res2:
        st.metric(label="🚀 รหัสอนาคต (Future)", value=future_code)
    with col_res3:
        st.metric(label="🌀 รหัสคู่ขนาน (Parallel)", value=parallel_code)
        
    # --- บทบรรยายที่มาของสูตรและวิธีการคำนวณอย่างละเอียด ---
    st.markdown("### 📖 คำบรรยายวิธีคำนวณและที่มาของตัวเลข")
    
    st.markdown(f"""
    * **รหัสอดีต ({past_code}):** คำนวณมาจาก **(วันเกิด + เดือนเกิด)** $\rightarrow$ สรุปสูตรคือ: `({d} + {m}) = {d+m}` แล้วนำมาบวกทีละหลักจนเหลือเลขตัวเดียว ตัวเลขนี้แสดงถึงฐานพลังงานดั้งเดิม สิ่งที่ติดตัวมาแต่กำเนิด และกรรมเก่าในอดีตที่คอยส่งผลต่อจิตใต้สำนึกของคุณ
    * **รหัสอนาคต ({future_code}):** คำนวณมาจาก **(วันเกิด + เดือนเกิด + ปีเกิด ค.ศ.)** $\rightarrow$ สรุปสูตรคือ: `({d} + {m} + {y}) = {d+m+y}` แล้วลดรูปเหลือหลักเดียว ตัวเลขนี้คือเส้นทางที่ชีวิตกำลังขับเคลื่อนไปข้างหน้า เป้าหมายที่แท้จริง และบทเรียนในอนาคตที่ใจคุณต้องเติบโตไปเผชิญ
    * **รหัสควอนตัมคู่ขนาน ({parallel_code}):** คำนวณมาจากสูตรความถี่ปฏิสัมพันธ์ **[(รหัสอดีต $\\times$ รหัสอนาคต) + ค่าคงที่ความถี่สากล 7]** $\rightarrow$ สรุปสูตรคือ: `({past_code} \\times {future_code}) + 7 = {(past_code * future_code) + 7}` ตัวเลขนี้แสดงถึงแรงดึงดูดในมิติคู่ขนาน สิ่งที่เกิดขึ้นเมื่ออดีตและอนาคตมาบรรจบกัน เป็นพลังงานสมองหรือคลื่นความถี่จิตที่ช่วยเยียวยาและนำทางเมื่อคุณตกอยู่ในสภาวะนิ่ง
    """)
    st.markdown("</div>", unsafe_allow_html=True)

    # ==========================================
    # 5. ส่วนคำนวณความสมพงษ์ (Compatibility Match)
    # ==========================================
    if partner_check and partner_date:
        pd = partner_date.day
        pm = partner_date.month
        py = partner_date.year
        
        partner_future = sum_digits(pd + pm + py)
        
        # 🌟 สูตรสมพงษ์: เอาความถี่อนาคตของทั้งสองคนมารวมกัน
        match_score = sum_digits(future_code + partner_future)
        
        st.markdown("<div class='quantum-box'>", unsafe_allow_html=True)
        st.markdown("## 💑 ผลการวิเคราะห์รหัสสมพงษ์โครงข่ายคู่ขนาน", unsafe_allow_html=True)
        st.write(f"รหัสอนาคตของคุณคือ **{future_code}** | รหัสอนาคตของคู่สมพงษ์คือ **{partner_future}**")
        st.write(f"### ค่าพลังงานความสมพงษ์ร่วมกัน: **{match_score}**")
        
        # คำอธิบายสูตรสมพงษ์
        st.markdown("📊 **วิธีคำนวณรหัสสมพงษ์:**")
        st.write(f"นำรหัสอนาคตของคุณ ({future_code}) มารวมกับรหัสอนาคตของคู่ ({partner_future}) สรุปสูตรคือ `({future_code} + {partner_future}) = {future_code + partner_future}` จากนั้นลดรูปเป็นเลขหลักเดียวเพื่อหาค่าตัดผ่านของเส้นทางชีวิตว่าเข้ากันได้ดีเพียงใด")
        
        # คำทำนายตามตัวเลขผลลัพธ์
        if match_score in [1, 3, 9]:
            st.success("🔥 **ระดับความสมพงษ์: สูงมาก (พลังงานส่งเสริมกัน)** พลักดันให้อนาคตรุ่งเรือง เป็นคู่คิดที่พากันก้าวหน้า")
        elif match_score in [2, 4, 6, 8]:
            st.info("🤝 **ระดับความสมพงษ์: ปานกลาง (พลังงานเกื้อกูล)** เน้นความมั่นคง อยู่ด้วยกันแบบเรื่อยๆ พึ่งพาอาศัยกันได้ดี")
        else:
            st.warning("⚡ **ระดับความสมพงษ์: แรงสะท้อน (ต้องปรับตัว)** มีเส้นควอนตัมตัดกันบ่อย อาจมีความเห็นขัดแย้งกันบ่อยครั้ง ต้องใช้ความนิ่งเพื่อสยบความเคลื่อนไหว")
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.balloons()

# แสดงสโลแกนท้ายแอปอย่างสวยงาม
st.markdown("<center style='color:#7F8C8D; font-size:12px;'>SYNAPSE PROJECT CORE SYSTEM © 2026 | \"อยู่นิ่งๆ ไม่เจ็บตัว\"</center>", unsafe_allow_html=True)
