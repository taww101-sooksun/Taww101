import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time

st.title("🔥 Firebase Connection Tester")

# 1. ฟังก์ชันเชื่อมต่อ (ตรวจสอบว่ามี App รันอยู่หรือยัง)
if not firebase_admin._apps:
    try:
        # ดึงค่าจาก st.secrets
        fb_config = {
            "type": "service_account",
            "project_id": st.secrets["project_id"],
            "private_key": st.secrets["private_key"].replace('\\n', '\n'),
            "client_email": st.secrets["client_email"],
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        cred = credentials.Certificate(fb_config)
        # ใส่ URL ของฐานข้อมูลพี่ตรงนี้
        database_url = "https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/"
        
        firebase_admin.initialize_app(cred, {'databaseURL': database_url})
        st.success("✅ เชื่อมต่อ Firebase สำเร็จ!")
    except Exception as e:
        st.error(f"❌ เชื่อมต่อล้มเหลว: {e}")
        st.stop()

# 2. ปุ่มทดสอบเขียนข้อมูล
st.subheader("ส่งข้อมูลทดสอบ")
test_msg = st.text_input("พิมพ์ข้อความเพื่อทดสอบ", "Hello Synapse!")

if st.button("🚀 ยิงข้อมูลไป Firebase"):
    try:
        ref = db.reference('test_connection')
        ref.update({
            'last_test': time.ctime(),
            'message': test_msg,
            'status': 'Online'
        })
        st.balloons()
        st.success("✨ ข้อมูลถูกส่งไปที่ Realtime Database เรียบร้อยแล้ว!")
        st.info("พี่ลองเข้าไปดูในหน้า Firebase Console ตรงหัวข้อ 'Realtime Database' ว่ามีคำว่า 'test_connection' ขึ้นมาไหม")
    except Exception as e:
        st.error(f"❌ ส่งข้อมูลไม่สำเร็จ: {e}")
