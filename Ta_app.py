import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import os

st.title("🔥 ระบบศูนย์บัญชาการ Firebase (เชื่อมต่อผ่านไฟล์)")
st.write("อยู่นิ่งๆ ไม่เจ็บตัว - ล้างบางบั๊กคีย์บิดเบี้ยว")

# ฟังก์ชันอ่านค่าตรงจากไฟล์ JSON
if not firebase_admin._apps:
    try:
        # กำหนดชื่อไฟล์คีย์ที่อยู่บน GitHub ร่วมกัน
        key_filename = "firebase_key.json"
        
        if os.path.exists(key_filename):
            # ดึง URL ฐานข้อมูลจากหน้า Secrets
            database_url = st.secrets.get("databaseURL", "")
            
            if not database_url:
                st.error("❌ พบไฟล์กุญแจ แต่ไม่พบค่า databaseURL ในหน้า Secrets")
            else:
                # สั่งใช้ไฟล์ JSON เปิดประตูเชื่อมต่อทันที
                cred = credentials.Certificate(key_filename)
                firebase_admin.initialize_app(cred, {
                    'databaseURL': database_url
                })
                st.success("✅ โคตรสุดเพื่อน! เชื่อมต่อผ่านไฟล์กุญแจตรงๆ สำเร็จเรียบร้อยแล้ว!")
        else:
            st.error("❌ ไม่พบไฟล์ firebase_key.json บนระบบ GitHub กรุณาตรวจสอบชื่อไฟล์")
            
    except Exception as e:
        st.error(f"❌ เครื่องจักรขัดข้องขณะโหลดไฟล์กุญแจ: {e}")

# ส่วนทดสอบระบบฐานข้อมูล
st.subheader("📝 ทดสอบยิงข้อความลงฐานข้อมูล")
user_message = st.text_input("พิมพ์ข้อความที่ต้องการทดสอบ:", "ระบบใช้งานได้แล้ว 100%")

if st.button("กดส่งข้อมูลลงเครื่องจักร"):
    if firebase_admin._apps:
        try:
            ref = db.reference('test_connect')
            ref.set({
                'message': user_message,
                'status': 'Online & Ready',
                'slogan': 'อยู่นิ่งๆ ไม่เจ็บตัว'
            })
            st.success("🚀 ข้อมูลวิ่งทะลุเข้า Firebase สำเร็จแล้ว! ลองไปดูหน้าเว็บได้เลย!")
        except Exception as e:
            st.error(f"❌ ส่งข้อมูลล้มเหลว (เช็คกฎความปลอดภัยบนเว็บ Firebase): {e}")
    else:
        st.error("❌ ระบบยังเชื่อมต่อฐานข้อมูลไม่ได้ตั้งแต่ด่านแรก")
