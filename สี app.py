import streamlit as st

# ตั้งค่าหน้าเดียวจบที่ไฟล์หลัก
st.set_page_config(page_title="SYNAPSE HUB", layout="centered")

# ซ่อนติ่ง Streamlit
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="stAppViewContainer"] {background-color: #000000;}
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <div style='text-align: center;'>
        <img src="app/static/logo1.png" style="width:120px; filter: drop-shadow(0 0 10px rgba(255, 75, 75, 0.5));" onerror="this.src='https://via.placeholder.com/120?text=SYNAPSE'">
        <h1 style='color: #FF4B4B; text-shadow: 0 0 15px #FF4B4B; margin-top:20px;'>📡 SYNAPSE COMMAND CENTER</h1>
        <p style='color: #888;'>อยู่นิ่งๆ ไม่เจ็บตัว | ระบบควบคุม 4-1 พร้อมใช้งาน</p>
    </div>
    <hr style="border: 1px solid #333;">
    """, unsafe_allow_html=True)

st.info("💡 เลือกเมนูที่แถบด้านข้าง (Sidebar) เพื่อเข้าสู่ห้องทำงานต่างๆ")
st.image("https://images.unsplash.com/photo-1550745165-9bc0b252726f?q=80&w=2070", caption="SYNAPSE CORE READY")
