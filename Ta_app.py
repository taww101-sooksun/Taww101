import streamlit as st
from datetime import datetime, timedelta
import time
import streamlit as st

# 1. ส่วนลบติ้งทุกอย่าง (รวมถึงมุมขวาล่างด้วย JavaScript) ทำได้จริงแน่นอน
st.markdown(
    """
    <style>
    /* ซ่อนเมนูสามขีดและฟุตเตอร์ด้านบน/ล่างแบบปกติก่อน */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppToolbar {display: none !important;}
    </style>
    
    <iframe src="about:blank" style="display:none;" id="js-injector"></iframe>
    <script>
        const injectJS = () => {
            // ค้นหา Element ของปุ่มมุมขวาล่างที่แอบอยู่ในระบบหลักของ Streamlit
            const streamlitDoc = window.parent.document;
            
            // ดักซ่อนปุ่ม Manage App และปุ่มตัวช่วยทั้งหมด
            const badges = streamlitDoc.querySelectorAll('[data-testid="stStatusWidget"], [class*="viewerBadge"], button[title="View source code"]');
            badges.forEach(el => el.style.setProperty('display', 'none', 'important'));
            
            // ค้นหาและทำลายโครงสร้างของกล่องมุมขวาล่างที่เหลืออยู่
            const footerToolbar = streamlitDoc.querySelector('.stAppToolbar, [class*="ViewerBadge"]');
            if(footerToolbar) {
                footerToolbar.style.setProperty('display', 'none', 'important');
            }
        };
        
        // สั่งให้ทำงานทันทีที่โหลดเว็บ และเช็กซ้ำทุกๆ 1 วินาทีกันมันโผล่กลับมา
        setTimeout(injectJS, 100);
        setInterval(injectJS, 1000);
    </script>
    """,
    unsafe_allow_html=True
)

# 2. ส่วนใส่โลโก้ต่อกันเลย จัดให้อยู่ตรงกลาง
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("logo1.png", use_container_width=True)
    except Exception:
        st.info("📌 อย่าลืมอัปโหลดไฟล์ logo1.png ไว้คู่กับไฟล์โค้ดนี้บน GitHub นะครับ")

# เริ่มเนื้อหาเว็บแอปของคุณต่อจากตรงนี้
st.title("ระบบ Command Center")

# ตั้งค่าหน้าจอเบื้องต้น
st.set_page_config(page_title="SYNAPSE X - TIME", layout="centered")
st.markdown("<style>.stApp {background-color: #000; color: #FFD700;}</style>", unsafe_allow_html=True)

# ส่วนแสดงผลนาฬิกา
st.subheader("🕒 SYSTEM MASTER CLOCK")
time_placeholder = st.empty()  # สร้างพื้นที่ว่างไว้ให้อัปเดตเวลา

# ลูปเพื่อให้เวลาเดินต่อเนื่องระดับเสี้ยววินาที
while True:
    # ดึงเวลาไทยจริง (UTC+7) พร้อมไมโครวินาที (Microseconds)
    thai_now = datetime.utcnow() + timedelta(hours=7)
    
    # แสดงผลเวลา: ชั่วโมง:นาที:วินาที.เสี้ยววินาที (3 หลัก)
    current_time = thai_now.strftime("%H:%M:%S.%f")[:-3]
    
    # อัปเดตตัวเลขบนหน้าจอ
    time_placeholder.markdown(f"""
        <div style="text-align: center; border: 2px solid #FFD700; padding: 20px; border-radius: 10px;">
            <h1 style="font-family: 'Courier New', Courier, monospace; font-size: 60px; color: #FFD700; margin: 0;">
                {current_time}
            </h1>
            <p style="color: #FFD700; letter-spacing: 5px;">THAILAND REAL-TIME</p>
        </div>
    """, unsafe_allow_html=True)
    
    # หน่วงเวลาเล็กน้อยเพื่อให้ระบบไม่ทำงานหนักเกินไป แต่ยังเห็นเสี้ยววินาทีเดินลื่นๆ
    time.sleep(0.01)
