import streamlit as st
from streamlit_google_auth import Authenticate
import os

# ==========================================
# 1. AUTHENTICATION SETUP
# ==========================================
# ดึงค่าจาก Secrets (ต้องสะกดให้ตรงกับหน้า Settings เป๊ะๆ)
auth = Authenticate(
    secret_key=st.secrets["google"]["secret_key"],
    client_id=st.secrets["google"]["client_id"],
    client_secret=st.secrets["google"]["client_secret"],
    redirect_uri="https://sooksun101.streamlit.app/",
    cookie_name="sooksun_cookie"
)

# ตรวจสอบสถานะการเข้าสู่ระบบ
auth.check_authenticity()

# ถ้ายังไม่ได้ Login ให้แสดงปุ่ม Login และหยุดการทำงานส่วนที่เหลือ
if not st.session_state.get("connected"):
    st.markdown("<h2 style='text-align:center;'>🔐 ACCESS RESTRICTED</h2>", unsafe_allow_html=True)
    auth.login()
    st.stop()

# ถ้าผ่านจุดนี้มาได้ แสดงว่า Login สำเร็จแล้ว
user_info = st.session_state["user_info"]
user_id = user_info.get("name")
