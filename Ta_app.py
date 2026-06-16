import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import base64
import json

st.title("🔥 ระบบศูนย์บัญชาการ Firebase (สมบูรณ์แบบ)")
st.write("อยู่นิ่งๆ ไม่เจ็บตัว - ระบบตรวจจับอัตโนมัติ")

# ฟังก์ชันอัจฉริยะ ตรวจจับและดึงค่ากุญแจเชื่อมต่อ
def initialize_firebase_hub():
    if firebase_admin._apps:
        return True
        
    try:
        # 1. ทดลองดึงค่าผ่านระบบเซฟตี้แบบ Base64 ก่อน
        if "firebase_base64" in st.secrets:
            b64_data = st.secrets["firebase_base64"]
            decoded_bytes = base64.b64decode(b64_data)
            cred_dict = json.loads(decoded_bytes.decode("utf-8"))
            st.info("🔄 กำลังเชื่อมต่อผ่านระบบท่อส่งข้อมูล Base64...")
            
        # 2. ถ้าไม่มี ให้สลับไปดึงค่าจากระบบข้อความปกติ (textkey)
        elif "textkey" in st.secrets:
            cred_dict = dict(st.secrets["textkey"])
            if "private_key" in cred_dict:
                cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
            st.info("🔄 กำลังเชื่อมต่อผ่านระบบโครงสร้าง TOML (textkey)...")
            
        else:
            st.error("❌ ไม่พบกุญแจเชื่อมต่อในระบบ Secrets กรุณาตรวจสอบการตั้งชื่อคีย์")
            return False

        # ดึง URL ของฐานข้อมูล
        database_url = st.secrets.get("databaseURL", "")
        if not database_url:
            st.error("❌ ไม่พบค่า databaseURL ในหน้า Secrets")
            return False

        # สั่งรันระบบเชื่อมต่อเข้าฐานข้อมูล
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': database_url
        })
        return True

    except Exception as e:
        st.error(f"❌ เครื่องจักรขัดข้องขณะโหลดคีย์ความปลอดภัย: {e}")
        return False

# เรียกใช้งานฟังก์ชันเชื่อมต่อหลังบ้าน
is_connected = initialize_firebase_hub()

if is_connected:
    st.success("✅ ปาฏิหาริย์เกิดขึ้นจริง! เชื่อมต่อฐานข้อมูลสำเร็จแล้วเพื่อน!")

# -----------------------------------------------------------------
# ส่วนหน้าต่างทดสอบส่งข้อมูลจริง (Realtime Database)
st.subheader("📝 ทดสอบยิงข้อความลงฐานข้อมูล")
user_message = st.text_input("พิมพ์ข้อความที่ต้องการทดสอบ:", "ระบบออนไลน์ 100%")

if st.button("กดส่งข้อมูลลงเครื่องจักร"):
    if is_connected:
        try:
            ref = db.reference('test_connect')
            ref.set({
                'message': user_message,
                'status': 'Online & Ready',
                'slogan': 'อยู่นิ่งๆ ไม่เจ็บตัว'
            })
            st.success("🚀 ข้อมูลวิ่งทะลุเข้า Firebase สำเร็จแล้ว! ลองเปิดหน้าเว็บดูได้เลย")
        except Exception as e:
            st.error(f"❌ ส่งข้อมูลล้มเหลว (เช็คกฎควมปลอดภัยในเว็บ): {e}")
    else:
        st.error("❌ พังตั้งแต่ด่านแรก ระบบยังไม่เชื่อมต่อฐานข้อมูล")
