import streamlit as st

# 1. ตั้งค่า Page และซ่อนองค์ประกอบของ Streamlit
st.set_page_config(page_title="Professional GPS Tracker", layout="wide")

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# 2. ใส่ Logo (ใช้ st.logo สำหรับเวอร์ชันใหม่ หรือ st.sidebar.image)
# ตรวจสอบว่าไฟล์ logo1.png อยู่ในโฟลเดอร์เดียวกับโค้ด
try:
    st.sidebar.image("logo1.png", use_container_width=True)
except:
    st.sidebar.warning("ไม่พบไฟล์ logo1.png กรุณาตรวจสอบชื่อไฟล์")

st.title("📍 ระบบระบุตำแหน่งระดับองค์กร")
# ... โค้ดส่วน GPS และแผนที่ของคุณต่อจากตรงนี้ ...
