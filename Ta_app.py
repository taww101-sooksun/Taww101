import streamlit as st
import os
from datetime import datetime, date

# ==========================================
# 1. การตั้งค่าหน้าตาแอปและชุดสี (Theme Customization)
# ==========================================
st.set_page_config(
    page_title="SYNAPSE QUANTUM SYSTEM.บักมรๆๆ",
    page_icon="🔮",
    layout="centered"
)

# ปรับพื้นหลังดำเงา (Glossy Dark) คุมโทนเข้มสะท้อนแสง ตัดกับข้อความชัดเจน
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ฉากหลังหลัก ดำเงาไล่เฉด */
    .stApp {
        background: linear-gradient(135deg, #050508 0%, #0B0F19 100%);
    }
    
    /* ปรับแต่งข้อความหลัก */
    h1, h2, h3, h4 {
        color: #00E5FF !important;
        font-weight: bold;
        text-shadow: 0px 0px 10px rgba(0, 229, 255, 0.3);
    }
    
    /* ปุ่มกดสไตล์นีออนเด่นชัด */
    .stButton>button {
        background-color: #FF1744;
        color: white !important;
        border-radius: 8px;
        border: 2px solid #00E5FF;
        font-weight: bold;
        width: 100%;
        box-shadow: 0px 4px 15px rgba(255, 23, 68, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #00E5FF;
        color: #050508 !important;
        border: 2px solid #FF1744;
    }
    
    /* กล่องข้อความสไตล์ Glossy ดำเงา ขอบสว่างชัดเจน */
    .quantum-box {
        border: 2px solid #00E5FF;
        padding: 22px;
        border-radius: 12px;
        background: rgba(18, 24, 36, 0.85);
        box-shadow: inset 0 0 10px rgba(0, 229, 255, 0.2), 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
    }
    .daily-box {
        border: 2px solid #FFD600;
        padding: 22px;
        border-radius: 12px;
        background: rgba(26, 26, 16, 0.85);
        box-shadow: inset 0 0 10px rgba(255, 214, 0, 0.2), 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
    }
    
    /* ปรับสีตัวอักษรทั่วไปให้อ่านง่ายบนพื้นหลังดำ */
    p, span, label {
        color: #E0E6ED !important;
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
    # เปลี่ยนตัวแปรเริ่มต้นให้ปลอดภัย
    my_date = st.date_input("วันเดือนปีเกิดของคุณ", value=date(2000, 1, 1), min_value=date(1950, 1, 1), key="my_bday")

st.markdown("### 🔍 2. เลือกฟังก์ชันที่ต้องการคำนวณ")
tab1, tab2, tab3 = st.tabs(["📆 เช็กคลื่นวันและแรงดึงดูดดวงจันทร์", "🧬 ถอดรหัสส่วนบุคคล (1.1618)", "💑 ตรวจสอบดวงสมพงษ์"])

# --- แยกส่วนตัวเลขวันเกิดไว้ใช้ส่วนกลาง ---
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
    target_date = st.date_input("เลือกวันที่ต้องการตรวจสอบ", date.today())
    
    btn_daily = st.button("คำนวณพลังงานประจำวัน", key="btn_daily")
    
    if btn_daily:
        td = target_date.day
        tm = target_date.month
        ty = target_date.year
        
        # 🌟 แก้ไขจุด Error ตรงนี้: เปลี่ยนจาก datetime เป็น date เพื่อให้ลบกันได้จริง
        days_diff = abs((target_date - date(2026, 1, 1)).days)
        lunar_position = round((days_diff % 29.53), 2)
        
        # คำนวณรหัสวันผสมฐานอดีต
        daily_sum = past_code + td + tm + ty + int(lunar_position)
        daily_code = sum_digits(daily_sum)
        
        st.markdown("<div class='daily-box'>", unsafe_allow_html=True)
        st.markdown(f"### 📊 รหัสพลังงานประจำวันของคุณวันนี้คือเลข: **{daily_code}**")
        st.write(f"🌙 ตำแหน่งดวงจันทร์ในรอบวงจรเสี้ยวเวลาปัจจุบัน: **{lunar_position} / 29.53 วัน**")
        
        # เพิ่มรายละเอียดการวิเคราะห์เชิงลึกตัวเลขความถี่สถิติ
        st.markdown("#### 📈 บทวิเคราะห์มิติคลื่นความถี่พลังงานร่วม")
        lunar_percentage = round((lunar_position / 29.53) * 100, 1)
        st.write(f"- **ผลกระทบจากแรงดึงดูดดวงจันทร์:** ปัจจุบันอยู่ที่ {lunar_percentage}% ของรอบวงจร ซึ่งส่งผลโดยตรงต่อระดับน้ำในร่างกายและกระแสประสาท (มวลน้ำและแรงกดอากาศแปรผันตามแรงดึงดูด)")
        
        st.markdown("**🔢 วิธีคำนวณและที่มาของตัวเลข:**")
        st.write(f"1. คำนวณรอบวงจรดวงจันทร์อ้างอิงจากรอบวงโคจรสากล `29.53` วัน ได้ค่าตำแหน่งสะท้อนพลังงานเท่ากับ `{lunar_position}`")
        st.write(f"2. นำรหัสอดีตของคุณ ({past_code}) + วันที่เช็ก ({td}) + เดือน ({tm}) + ปี ค.ศ. ({ty}) + ปรับฐานเศษดวงจันทร์ ({int(lunar_position)})")
        st.write(f"สูตรประมวลผลจริง: `({past_code} + {td} + {tm} + {ty} + {int(lunar_position)}) = {daily_sum}` เมื่อบดเศษเหลือหลักเดียวได้ผลลัพธ์เป็นค่าความถี่ประจำวันตัวเลข **{daily_code}**")
        
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
        # สูตรสัดส่วนทองคำ
        raw_parallel = (past_code * future_code * 1.1618) + 7
        parallel_code = sum_digits(raw_parallel)
        
        st.markdown("<div class='quantum-box'>", unsafe_allow_html=True)
        st.markdown("<h2>🌌 รหัสควอนตัมส่วนบุคคลของคุณ</h2>", unsafe_allow_html=True)
        
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric(label="🧬 รหัสอดีต (Past)", value=past_code)
        with col_res2:
            st.metric(label="🚀 รหัสอนาคต (Future)", value=future_code)
        with col_res3:
            st.metric(label="🌀 รหัสคู่ขนานทองคำ (Parallel)", value=parallel_code)
            
        st.markdown("#### 📖 รายละเอียดเชิงลึกและที่มาของสูตรคำนวณ")
        st.markdown(f"""
        * **รหัสอดีต ({past_code}):** คำนวณจาก `({d} + {m}) = {d+m}` ย่อยจนเหลือเลขหลักเดียว สะท้อนโครงสร้างฐานข้อมูลทางกายภาพและจิตใต้สำนึกดั้งเดิม
        * **รหัสอนาคต ({future_code}):** คำนวณจาก `({d} + {m} + {y}) = {d+m+y}` ย่อยเหลือเลขหลักเดียว สะท้อนแรงเหวี่ยงของเป้าหมายและวิถีการตัดสินใจเชิงตรรกะที่คุณเลือกเดิน
        * **รหัสควอนตัมคู่ขนานทองคำ ({parallel_code}):** ประมวลผลร่วมกับค่าคงที่อัตราส่วนทองคำสากล **`1.1618`** ซึ่งเป็นตัวเลขที่พบในสถาปัตยกรรมธรรมชาติและการแตกตัวของโมเลกุล 
        
        **สมการวิเคราะห์:**  
        $$\mu = (Past \\times Future \\times 1.1618) + 7$$
        แทนค่าจริงลงในระบบ: `({past_code} × {future_code} × 1.1618) + 7 = {round(raw_parallel, 4)}` เมื่อย่อยเลขทั้งหมดรวมกันจนเหลือหลักเดียวจะได้ค่าคงที่ **{parallel_code}** ตัวเลขนี้บ่งบอกถึงระดับความถี่สมองที่ทำงานได้อย่างเต็มประสิทธิภาพที่สุดเมื่อเราปิดสวิตช์เรื่องกวนใจภายนอก แล้วเลือกที่จะตั้งมั่น **"อยู่นิ่ง ๆ"** เพื่อเซ็ตระบบความคิดใหม่ครับ
        """)
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# TAB 3: ตรวจสอบดวงสมพงษ์
# ==========================================
with tab3:
    st.markdown("#### คำนวณรหัสความถี่ร่วมกับบุคคลอื่น")
    partner_date = st.date_input("วันเดือนปีเกิดของคู่สมพงษ์", value=date(2000, 1, 1), min_value=date(1950, 1, 1), key="partner_bday")
    btn_match = st.button("เริ่มต้นคำนวณรหัสสมพงษ์", key="btn_match")
    
    if btn_match:
        pd = partner_date.day
        pm = partner_date.month
        py = partner_date.year
        partner_future = sum_digits(pd + pm + py)
        
        match_score = sum_digits(future_code + partner_future)
        
        st.markdown("<div class='quantum-box'>", unsafe_allow_html=True)
        st.markdown("<h2>💑 ผลการวิเคราะห์โครงข่ายคู่ขนาน</h2>", unsafe_allow_html=True)
        st.write(f"### ค่าพลังงานความสมพงษ์ร่วมกัน: **{match_score}**")
        
        # เพิ่มรายละเอียดความหมายเชิงสถิติตัวเลขคู่สัมพันธ์
        st.markdown("#### 🧬 รายละเอียดแมทริกซ์ความสัมพันธ์")
        st.write(f"- **ฐานพลังงานส่วนบุคคล:** รหัสฝั่งคุณ ({future_code}) ทำปฏิกิริยากับรหัสฝั่งคู่ประสาน ({partner_future})")
        st.write(f"- **สมการรวมเศษราก:** `({future_code} + {partner_future}) = {future_code + partner_future}` ลดรูปตัวเลขเหลือแกนหลักเดียวคือ **{match_score}**")
        
        st.write("---")
        if match_score in [1, 3, 9]:
            st.success("🔥 **ระดับความสมพงษ์: สูงมาก** พลังงานเหนี่ยวนำไปในทิศทางเดียวกันอย่างรุนแรง ช่วยผลักดันในเรื่องการคิดวิเคราะห์ เป็นคู่คิดคู่ขนานที่พร้อมเติบโต")
        elif match_score in [2, 4, 6, 8]:
            st.info("🤝 **ระดับความสมพงษ์: ปานกลาง** เป็นคลื่นความถี่แบบเกื้อกูลและรักษาสมดุลซึ่งกันและกัน ความสัมพันธ์เสถียร นิ่งสงบ พึ่งพาอาศัยกันได้ในระยะยาว")
        else:
            st.warning("⚡ **ระดับความสมพงษ์: แรงสะท้อน** เส้นความถี่ตัดกันบ่อยครั้ง มีโอกาสเกิดแรงต้านหรือความเห็นไม่ตรงกันได้ง่าย ในสถานการณ์นี้การใช้ความนิ่งและไม่ปะทะจะช่วยรักษาความสมดุลได้ดีที่สุด")
        st.markdown("</div>", unsafe_allow_html=True)

# สโลแกนปิดท้ายแอป
st.markdown("<center style='color:#7F8C8D; font-size:12px;'>SYNAPSE PROJECT CORE SYSTEM © 2026 | \"อยู่นิ่งๆ ไม่เจ็บตัว\"</center>", unsafe_allow_html=True)
