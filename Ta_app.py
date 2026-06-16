import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

st.title("🔥ระบบทดสอบเชื่อมต่อ Firebase")
st.write("อยู่นิ่งๆ ไม่เจ็บตัว - ศูนย์บัญชาการจำลอง")

# 1. ตรวจสอบและตั้งค่า Firebase (ดึงค่าจาก Secrets ตรงๆ)
if not firebase_admin._apps:
    try:
        # แปลงค่า [textkey] จากสตรีมลิตให้อยู่ในรูป dictionary ทันที ไม่ต้องสั่ง loads ซ้ำ
        cred_dict = dict(st.secrets["textkey"])
        
        # แก้ปัญหารหัสอักขระ \n บิดเบี้ยวให้กลับมาขึ้นบรรทัดใหม่จริงตามฟอร์แมตใบรับรอง
        if "private_key" in cred_dict:
            cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
            
        database_url = st.secrets["databaseURL"]
        
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': database_url
        })
        st.success("✅ เชื่อมต่อ Firebase สำเร็จแล้วเพื่อน!")
    except Exception as e:
        st.error(f"❌ ระบบเชื่อมต่อฐานข้อมูลขัดข้อง: {e}")

# 2. ฟังก์ชันทดสอบการรับ-ส่งข้อมูลจริง
st.subheader("📝 ลองส่งข้อมูลลงฐานข้อมูล")
user_message = st.text_input("พิมพ์ข้อความที่ต้องการทดสอบ:", "สวัสดี Firebase")

if st.button("กดส่งข้อมูล"):
    try:
        # อ้างอิงพิกัดไปที่โฟลเดอร์ทดสอบในฐานข้อมูล
        ref = db.reference('test_connect')
        ref.set({
            'message': user_message,
            'status': 'Online',
            'slogan': 'อยู่นิ่งๆ ไม่เจ็บตัว'
        })
        st.success("🚀 ส่งข้อมูลเข้าฐานข้อมูลสำเร็จจริง! ลองเปิดดูในหน้าเว็บ Firebase ได้เลย")
    except Exception as e:
        st.error(f"❌ ไม่สามารถส่งข้อมูลได้: {e}")
