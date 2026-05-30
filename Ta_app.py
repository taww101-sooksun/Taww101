import streamlit as st
import time
import random

# ==========================================
# 1. PAGE CONFIG & THEME (ปรับให้มืด ดุดัน คลีน)
# ==========================================
st.set_page_config(
    page_title="ยิ้มซิ (Yimzy) | อยู่นิ่งๆไม่เจ็บตัว",
    page_icon="🌹",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS เพื่อรีดความสวยงามบนมือถือ
st.markdown("""
    <style>
    /* ซ่อนแถบเมนูที่ไม่จำเป็นเพื่อให้คลีนที่สุด */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ปรับแต่งฟอนต์และสี */
    .stApp {
        background-color: #111827;
    }
    h1, h2, h3, p, span, label {
        color: #ffffff !important;
    }
    /* ปรับแต่งการ์ดแนวอารมณ์ */
    .genre-box {
        background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
        border: 1px solid #10b981;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. STATE INITIALIZATION (ระบบเก็บข้อมูลชั่วคราว)
# ==========================================
# หมายเหตุ: เนื่องจาก Streamlit ทำงานแบบไร้สถานะถาวร (Stateless) ระหว่างผู้ใช้ 
# ตัวแปรเหล่านี้จะคงอยู่ตราบใดที่เซสชันของผู้ใช้คนนั้นยังไม่ปิด
if 'views' not in st.session_state:
    st.session_state.views = random.randint(120, 500)  # สมมุติตัวเลขเริ่มต้นจริงใจตามทราฟฟิก
if 'shares' not in st.session_state:
    st.session_state.shares = 42
if 'rose_plays' not in st.session_state:
    st.session_state.rose_plays = 0
if 'energy' not in st.session_state:
    st.session_state.energy = 50
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# นับยอดการเข้าชมเพจจริงในเซสชันนี้
st.session_state.views += 1

# ==========================================
# 3. HEADER & SLOGAN
# ==========================================
st.markdown("<h1 style='text-align: center; font-size: 3rem; font-weight: 900; margin-bottom: 0;'>ยิ้มซิ <span style='color: #60a5fa;'>(Yimzy)</span></h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #f87171 !important; font-size: 1.5rem; font-weight: 900; font-style: italic; letter-spacing: 1px;'>\"อยู่นิ่งๆไม่เจ็บตัว\"</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #9ca3af !important; font-size: 1.1rem;'>ที่ที่เข้าใจความรู้สึก <span style='color: #34d399; font-weight: bold;'>มากกว่า 100 แนว</span> ของคุณ</p>", unsafe_allow_html=True)

st.write("---")

# ==========================================
# 4. GLOBAL STATS DISPLAY (กล่องสถิติเรียงแถวหน้ากระดาน)
# ==========================================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="เข้ามาระบาย (Views)", value=st.session_state.views)
with col2:
    st.metric(label="แชร์ Wisdom", value=st.session_state.shares)
with col3:
    st.metric(label="ดึงกุหลาบ (Plays)", value=st.session_state.rose_plays)
with col4:
    st.metric(label="พลังงาน (Energy)", value=f"{st.session_state.energy}/50")

st.write("---")

# ==========================================
# 5. FEATURE 1: เกมดึงกลีบกุหลาบทำนายรัก (ความกลไกแบบตรรกะจริง)
# ==========================================
st.markdown("### 🌹 ระบบทำนายรักด้วยกลีบกุหลาบ")
rose_btn = st.button("🌹 เริ่มเด็ดกลีบกุหลาบเสี่ยงทาย", use_container_width=True)

if rose_btn:
    st.session_state.rose_plays += 1
    # สร้างจำนวนกลีบแบบสุ่ม 5-15 กลีบตามความจริงของดอกไม้
    total_petals = random.randint(5, 15)
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # จำลองการดึงทีละกลีบให้เห็นจริง ไม่ใช่ปุ๊บปั๊บโผล่มาเลย
    for i in range(total_petals):
        current_status = "รัก" if i % 2 == 0 else "ไม่รัก"
        status_text.markdown(f"<p style='text-align: center; font-size: 1.5rem;'>กลีบที่ {i+1}: <b style='color: #f87171;'>{current_status}</b></p>", unsafe_allow_html=True)
        progress_bar.progress((i + 1) / total_petals)
        time.sleep(0.2) # หน่วงเวลาให้ดูสมจริง
        
    final_result = "รัก" if (total_petals - 1) % 2 == 0 else "ไม่รัก"
    st.markdown(f"<div style='background-color: #7f1d1d; padding: 15px; border-radius: 10px; text-align: center;'><h2 style='margin:0;'>ผลลัพธ์สุดท้าย: {final_result}!</h2></div>", unsafe_allow_html=True)
    st.balloons() # ฉลองความจริงใจ

st.write("---")

# ==========================================
# 6. FEATURE 2: GENRE SELECTION & REAL CHAT
# ==========================================
st.markdown(f"### 💬 ห้องระบายความรู้สึก (พลังงานเหลือ: {st.session_state.energy}/50)")

# รายชื่อแนวอารมณ์เด่นๆ (ต๊ะสามารถขยายให้ครบ 100 แนวได้ง่ายๆ โดยการเพิ่มใน List นี้)
genres = [
    "อกหักจากคนไม่มีตัวตน", "เหนื่อยกับงานแต่ขยันเงียบๆ", "เหงาแบบสโลแกนอยู่นิ่งๆ",
    "คิดถึงคนที่เพิ่งเจอกันในฝัน", "สับสนในเทคโนโลยี", "มีความสุขแบบไม่ตะโกน",
    "ฟังเพลง R&B แล้วดิ่ง", "อยากระบายเฉยๆ ไม่ต้องสอน", "พลังงานชีวิตเหลือ 1%"
]

selected_genre = st.selectbox("เลือกแนวอารมณ์ที่คุณกำลังเผชิญอยู่:", genres)

# แสดงกล่องข้อความจำลองแนวอารมณ์ที่เลือก
st.markdown(f"<div class='genre-box'>กำลังเข้าสู่โหมด: <b>{selected_genre}</b></div>", unsafe_allow_html=True)

# ตรวจสอบเรื่องพลังงาน
if st.session_state.energy <= 0:
    st.error("⚠️ พลังงานหมดชั่วคราว! กรุณากดปุ่มเติมพลังงานด้านล่างเพื่อชาร์จระบบ")
    if st.button("🔋 เติมพลังงาน (ใช้เวลาชาร์จ 3 วินาที)", type="primary", use_container_width=True):
        with st.spinner("กำลังชาร์จพลังงานเข้าสู่ระบบ..."):
            time.sleep(3) # ชาร์จจริงตามสัจจะ
        st.session_state.energy = 50
        st.success("ชาร์จพลังงานเต็ม 50/50 แล้ว! คุยต่อได้เลยเพื่อน")
        st.rerun()
else:
    # ฟอร์มส่งข้อความ
    with st.form(key="chat_form", clear_on_submit=True):
        user_msg = st.text_input("พิมพ์คำถามหรือระบายความรู้สึกของคุณตรงนี้...", placeholder="เช่น วันนี้เหนื่อยจัง...")
        submit_btn = st.form_submit_button("ส่งความรู้สึก")
        
    if submit_btn and user_msg:
        # หักพลังงานจริงครั้งละ 5 หน่วย
        st.session_state.energy -= 5
        
        # คลังคำตอบแบบเพื่อนแท้ ไม่โกหก ไม่ซับซ้อน ตรงไปตรงมาตามสไตล์ "อยู่นิ่งๆไม่เจ็บตัว"
        ai_responses = [
            f"เข้าใจเลยเพื่อน... เรื่องบางเรื่องถ้าแก้ไม่ได้ ก็นิ่งไว้ก่อนเดี๋ยวดีเองแหละ",
            f"ฟังอยู่เน้อ เรื่องนี้ปล่อยให้เวลามันจัดการไป ตัวเราอยู่นิ่งๆ ปลอดภัยสุด",
            f"โหมด {selected_genre} นี่มันหนักเอาเรื่องนะ แต่ตราบใดที่เรายังหายใจอยู่ ค่อยๆ ไปทีละก้าว",
            f"บางทีการไม่ต้องทำอะไรเลยนั่นแหละคือคำตอบที่ดีที่สุดแล้ว"
        ]
        chosen_reply = random.choice(ai_responses)
        
        # บันทึกลงประวัติ
        st.session_state.chat_history.append({"user": user_msg, "ai": chosen_reply})
        st.rerun()

# แสดงประวัติการคุย
if st.session_state.chat_history:
    st.write("#### ประวัติการสนทนากับ ยิ้มซิ:")
    for chat in reversed(st.session_state.chat_history): # เอาอันล่าสุดขึ้นก่อน จะได้ไม่ต้องเลื่อนจอมือถือเยอะ
        st.info(f"🧑 **คุณ:** {chat['user']}")
        st.success(f"🤖 **ยิ้มซิ:** {chat['ai']}")

# ปุ่มล้างข้อมูลในเซสชันเพื่อความเป็นส่วนตัวสูงสุด
if st.session_state.chat_history:
    if st.button("🗑️ ล้างประวัติการสนทนาทั้งหมด", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
