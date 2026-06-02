import streamlit as st

# โค้ดสำหรับซ่อนติ้งทุกอย่าง รวมมุมขวาล่างด้วย
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ซ่อนปุ่มเครื่องหมายคำถาม และปุ่ม Manage App มุมขวาล่าง */
    .viewerBadge_container__1QSob,
    [data-testid="stActionButton"],
    button[title="View source code"],
    .stAppToolbar,
    div[data-testid="stStatusWidget"] {
        display: none !important;
    }
    
    /* ดักซ่อนปุ่มมุมขวาล่างแบบเด็ดขาด */
    iframe + div {display: none !important;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)


import streamlit as st

# 1. ส่วนเคลียร์พื้นที่ (ซ่อนติ้งทุกอย่างตามที่เราคุยกัน)
hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QSob,
    [data-testid="stActionButton"],
    button[title="View source code"],
    .stAppToolbar,
    div[data-testid="stStatusWidget"] {
        display: none !important;
    }
    iframe + div {display: none !important;}
    </style>
"""
st.markdown(hide_style, unsafe_allow_html=True)

# 2. ส่วนใส่โลโก้ต่อกันเลย (จัดให้โลโก้เด่นอยู่ตรงกลางหน้าเว็บ)
col1, col2, col3 = st.columns([1, 2, 1])  # แบ่งคอลัมน์เพื่อบีบให้รูปอยู่ตรงกลาง

with col2:
    try:
        # ใส่ชื่อไฟล์รูปของคุณตรงนี้ (ปรับความกว้าง width ได้ตามใจชอบ)
        st.image("logo1.png", use_container_width=True) 
    except Exception:
        # กรณีรันในเครื่องแล้วยังไม่มีไฟล์รูป จะได้ไม่ขึ้นหน้าจอเออร์เรอร์สีแดงให้ตกใจ
        st.info("📌 อย่าลืมอัปโหลดไฟล์ logo1.png ขึ้น GitHub ในโฟลเดอร์เดียวกับโค้ดนี้ด้วยนะ")

# 3. เริ่มเขียนเนื้อหาแอปของคุณต่อจากตรงนี้ได้เลย...
st.title("ยินดีต้อนรับเข้าสู่ระบบ")




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


