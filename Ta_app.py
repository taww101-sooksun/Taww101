import streamlit as st
import os
from datetime import datetime

# ==========================================
# 1. การตั้งค่าหน้าตาแอปและชุดสี (Theme Customization)
# ==========================================
st.set_page_config(
    page_title="SYNAPSE QUANTUM SYSTEM",
    page_icon="🔮",
    layout="centered"
)

# ลบติ่งและปุ่ม Streamlit ออกทั้งหมด คุมโทนสีเข้ม ขอบหนาชัดเจน
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
    .daily-box {
        border: 4px solid #FFD600;
        padding: 20px;
        border-radius: 12px;
        background-color: #1A1A10;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. ส่วนแสดงโลโก้
# ==========================================
st.title("🔮 SYNAPSE COMMAND CENTER")
st.subheader("ระบบวิเคราะห์ถอดรหัสคณิตศาสตร์ควอนตัม & พลังงานดวงจันทร์")

logo_path = "logo1.png"
if os.path.exists(logo_path):
    st.image(logo_path, use_container_width=True)

st.write("---")

# ==========================================
# 3. ฟังก์ชันการบดเลข (ลดรูปเหลือหลักเดียว 1-9)
# ==========================================
def sum_digits(number):
    # แปลงเป็นจำนวนเต็มบวกก่อนบดเลข
    number = abs(int(str(number).replace('.', '')))
    while number > 9:
        number = sum(int(digit) for digit in str(number))
    return number

# ==========================================
# 4. หน้าต่างรับข้อมูล (Input)
# ==========================================
st.markdown("### 📅 1. กรอกข้อมูลวันเกิดของคุณ")
col1, col2 = st.columns(2)
with col1:
    my_date = st.date_input("วันเดือนปีเกิดของคุณ", min_value=datetime(1950, 1, 1), key="my_bday")

st.markdown("### 🔍 2. เลือกฟังก์ชันที่ต้องการคำนวณ")
tab1, tab2, tab3 = st.tabs(["📆 เช็กคลื่นวันและแรงดึงดูดดวงจันทร์", "🧬 ถอดรหัสส่วนบุคคล (1.1618)", "💑 ตรวจสอบดวงสมพงษ์"])

# --- แยกส่วนตัวเลขวันเกิดของบาสไว้ใช้ส่วนกลาง ---
d = my_date.day
m = my_date.month
y = my_date.year
past_code = sum_digits(d + m)
future_code = sum_digits(d + m + y)

# ==========================================
# TAB 1: คำนวณตัวเลขประจำวัน + วงจรดวงจันทร์ 29.53
# ==========================================
with tab1:
    st.markdown("#### ตรวจสอบคลื่นความถี่ของวัน ร่วมกับอิทธิพลรอบวงจรดวงจันทร์ `29.53` วัน")
    target_date = st.date_input("เลือกวันที่ต้องการตรวจสอบ", datetime.now())
    
    btn_daily = st.button("คำนวณพลังงานประจำวัน", key="btn_daily")
    
    if btn_daily:
        td = target_date.day
        tm = target_date.month
        ty = target_date.year
        
        # 🌟 สูตรดวงจันทร์: คำนวณความแตกต่างของวันเพื่อหาเศษส่วนในรอบวงจรดวงจันทร์ 29.53 วัน
        days_diff = abs((target_date - datetime(2026, 1, 1)).days)
        lunar_position = round((days_diff % 29.53), 2)
        
        # คำนวณรหัสวันผสมฐานอดีตของบาส
        daily_sum = past_code + td + tm + ty + int(lunar_position)
        daily_code = sum_digits(daily_sum)
        
        st.markdown("<div class='daily-box'>", unsafe_allow_html=True)
        st.markdown(f"### 📊 รหัสพลังงานประจำวันของคุณวันนี้คือเลข: **{daily_code}**")
        st.write(f"🌙 ตำแหน่งดวงจันทร์ในรอบวงจรเสี้ยวเวลาปัจจุบัน: **{lunar_position} / 29.53 วัน**")
        
        # อธิบายสูตรคำนวณชัดเจนตามความจริง
        st.markdown("**🔢 วิธีคำนวณและที่มาของตัวเลข:**")
        st.write(f"1. คำนวณรอบวงจรดวงจันทร์อ้างอิงจากรอบวงโคจรสากล `29.53` วัน ได้ค่าตำแหน่งที่สะท้อนพลังงานน้ำขึ้นน้ำลงเท่ากับ `{lunar_position}`")
        st.write(f"2. นำรหัสอดีตของคุณ ({past_code}) + วันที่เช็ก ({td}) + เดือน ({tm}) + ปี ค.ศ. ({ty}) + ปรับฐานเศษดวงจันทร์ ({int(lunar_position)}) "
                 f"$\rightarrow$ สรุปสูตรคือ `({past_code} + {td} + {tm} + {ty} + {int(lunar_position)}) = {daily_sum}` บดตัวเลขเหลือหลักเดียวได้ **{daily_code}**")
        
        st.write("---")
        st.markdown("**🔔 คำแนะนำและการปฏิบัติตัวสำหรับวันนี้:**")
        
        if daily_code in [1, 5, 9]:
            st.success("🚀 **[วันแห่งการพุ่งชนและสร้างสรรค์]** พลังงานเปิดทางโล่ง เหมาะแก่การลงมือทำโปรเจกต์ใหม่ ๆ เขียนโค้ด ลุยงานช่าง ไอเดียจะแล่นฉิวครับ")
        elif daily_code in [2, 4, 7]:
            st.warning("🛡️ **[วันแห่งสติ - อยู่นิ่ง ๆ ไม่เจ็บตัว]** วันนี้กระแสพลังงานภายนอกและแรงดึงดูดผันผวนสูง หากมีเรื่องขัดใจวิ่งเข้ามาชน ให้ใช้ความนิ่งสยบความเคลื่อนไหว รักษาใจตัวเองไว้ในที่ตั้งดีที่สุดครับ")
        else:
            st.info("🤝 **[วันแห่งการปรับสมดุลและเก็บข้อมูล]** พลังงานระดับกลาง เหมาะกับการทำงานเงียบ ๆ ตรวจเช็กความเรียบร้อยของระบบ หรือแกะเนื้อเพลงเรื่อย ๆ ค่อยเป็นค่อยไปครับ")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 2: ถอดรหัสส่วนบุคคล + รหัสสัดส่วนทองคำ 1.1618
# ==========================================
with tab2:
    btn_personal = st.button("ถอดรหัสควอนตัม 3 มิติ (ใช้ฐาน 1.1618)", key="btn_personal")
    
    if btn_personal:
        # 🌟 สูตรสัดส่วนทองคำ: นำ (รหัสอดีต x รหัสอนาคต x ค่าสัดส่วนทองคำ 1.1618) + 7 เพื่อหาจุดตัดที่สมบูรณ์ที่สุดในมิติคู่ขนาน
        raw_parallel = (past_code * future_code * 1.1618) + 7
        parallel_code = sum_digits(raw_parallel)
        
        st.markdown("<div class='quantum-box'>", unsafe_allow_html=True)
        st.markdown("## 🌌 รหัสควอนตัมส่วนบุคคลของคุณ")
        
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric(label="🧬 รหัสอดีต (Past)", value=past_code)
        with col_res2:
            st.metric(label="🚀 รหัสอนาคต (Future)", value=future_code)
        with col_res3:
            st.metric(label="🌀 รหัสคู่ขนานทองคำ (Parallel)", value=parallel_code)
            
        st.markdown("#### 📖 รายละเอียดและที่มาของสูตรคำนวณ")
        st.markdown(f"""
        * **รหัสอดีต ({past_code}):** สูตรคือ `({d} + {m}) = {d+m}` สรุปเป็นเลขตัวเดียว คือฐานพลังงานจิตใต้สำนึกดั้งเดิมของคุณ
        * **รหัสอนาคต ({future_code}):** สูตรคือ `({d} + {m} + {y}) = {d+m+y}` สรุปเป็นเลขตัวเดียว คือทิศทางและเป้าหมายชีวิตข้างหน้าที่คุณเลือกเดิน
        * **รหัสควอนตัมคู่ขนานทองคำ ({parallel_code}):** คำนวณโดยดึงค่าคงที่รหัสสัดส่วนทองคำสากล **`1.1618`** มาร่วมคำนวณเพื่อหาความสมดุล $\rightarrow$ สูตรคือ `({past_code} \\times {future_code} \\times 1.1618) + 7 = {round(raw_parallel, 4)}` จากนั้นนำมาบดตัวเลขทั้งหมดรวมกันจนเหลือหลักเดียว ตัวเลขนี้คือคลื่นความถี่สมองซีกขวาที่จะทำงานได้ชัดเจนที่สุดเวลาที่คุณตั้งใจ **"อยู่นิ่ง ๆ"** เพื่อเยียวยาจิตใจและมองหาทางออกครับ
        """)
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 3: ตรวจสอบดวงสมพงษ์
# ==========================================
with tab3:
    st.markdown("#### คำนวณรหัสความถี่ร่วมกับบุคคลอื่น")
    partner_date = st.date_input("วันเดือนปีเกิดของคู่สมพงษ์", min_value=datetime(1950, 1, 1), key="partner_bday")
    btn_match = st.button("เริ่มต้นคำนวณรหัสสมพงษ์", key="btn_match")
    
    if btn_match:
        pd = partner_date.day
        pm = partner_date.month
        py = partner_date.year
        partner_future = sum_digits(pd + pm + py)
        
        match_score = sum_digits(future_code + partner_future)
        
        st.markdown("<div class='quantum-box'>", unsafe_allow_html=True)
        st.markdown("## 💑 ผลการวิเคราะห์โครงข่ายคู่ขนาน")
        st.write(f"### ค่าพลังงานความสมพงษ์ร่วมกัน: **{match_score}**")
        
        st.markdown("**🔢 วิธีคำนวณ:**")
        st.write(f"นำรหัสอนาคตของคุณ ({future_code}) + รหัสอนาคตของคู่ ({partner_future}) $\rightarrow$ สูตรคือ `({future_code} + {partner_future}) = {future_code + partner_future}` บดเหลือเลขตัวเดียว")
        
        if match_score in [1, 3, 9]:
            st.success("🔥 **ระดับความสมพงษ์: สูงมาก** พลังงานส่งเสริม พลักดันให้อนาคตรุ่งเรือง เป็นคู่คิดพากันก้าวหน้า")
        elif match_score in [2, 4, 6, 8]:
            st.info("🤝 **ระดับความสมพงษ์: ปานกลาง** พลังงานเกื้อกูล อยู่ด้วยกันแบบเรื่อยๆ มั่นคง พึ่งพากันได้")
        else:
            st.warning("⚡ **ระดับความสมพงษ์: แรงสะท้อน** มีเส้นควอนตัมตัดกันบ่อย อาจขัดแย้งกันบ่อย ต้องใช้ความนิ่งเข้าสู้")
        st.markdown("</div>", unsafe_allow_html=True)

# สโลแกนปิดท้ายแอป
st.markdown("<center style='color:#7F8C8D; font-size:12px;'>SYNAPSE PROJECT CORE SYSTEM © 2026 | \"อยู่นิ่งๆ ไม่เจ็บตัว\"</center>", unsafe_allow_html=True)
