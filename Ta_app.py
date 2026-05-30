import streamlit as st

st.set_page_config(page_title="Yimzy Login", page_icon="📱", layout="centered")

# สไตล์ดุดันตามคอนเซปต์
st.markdown("""
    <style>
    .stApp { background-color: #111827; }
    h2, p, label { color: white !important; }
    </style>
""", unsafe_allow_html=True)

st.title("📱 ระบบเข้าสู่ระบบ ยิ้มซิ")
st.markdown("<p style='color: #f87171 !important; font-style: italic;'>\"อยู่นิ่งๆ ไม่เจ็บตัว ปลอดภัยด้วยระบบ OTP\"</p>", unsafe_allow_html=True)

# ตรวจสอบสถานะการล็อกอิน
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_phone' not in st.session_state:
    st.session_state.user_phone = ""

if not st.session_state.logged_in:
    # ----------------------------------------
    # ขั้นตอนที่ 1: กรอกเบอร์โทรศัพท์เพื่อขอ OTP
    # ----------------------------------------
    st.subheader("ลงทะเบียน / เข้าสู่ระบบ")
    phone_number = st.text_input("กรอกเบอร์โทรศัพท์ของคุณ (เช่น +66812345678)", placeholder="+66xxxxxxxxx")
    
    # ปุ่มจำลองการทำงานฝั่งกุญแจ Firebase (ในความเป็นจริงต๊ะต้องเอาโค้ด JS ของ Firebase มาแปะเพิ่ม)
    # แต่ตรงนี้คือตรรกะที่หน้าจอ Streamlit จะจัดการต่อ
    if st.button("📲 ส่งรหัส OTP", use_container_width=True):
        if phone_number.startswith("+66") and len(phone_number) >= 11:
            st.session_state.user_phone = phone_number
            st.success(f"ระบบส่งรหัส OTP ไปยังเบอร์ {phone_number} แล้ว (จำลองสถานะ)")
            st.toast("ส่ง SMS สำเร็จ!")
        else:
            st.error("❌ กรุณากรอกเบอร์โทรศัพท์ให้ถูกต้องในรูปแบบสากล (มี +66 นำหน้า)")

    # ----------------------------------------
    # ขั้นตอนที่ 2: กรอกรหัส OTP ยืนยัน
    # ----------------------------------------
    if st.session_state.user_phone:
        st.write("---")
        otp_code = st.text_input("กรอกรหัส OTP 6 หลักที่ได้รับทาง SMS", max_chars=6, type="password")
        
        if st.button("✅ ยืนยันรหัสเข้าสู่ระบบ", type="primary", use_container_width=True):
            # ตั้งเงื่อนไขจำลอง (หรือตรวจสอบจริงกับ Firebase)
            if otp_code == "123456" or len(otp_code) == 6:  # สมมุติค่า หรือให้ผ่านถ้ากรอกครบ 6 หลักในขั้นพัฒนา
                st.session_state.logged_in = True
                st.success("🔓 ยืนยันตัวตนสำเร็จ!")
                st.rerun()
            else:
                st.error("❌ รหัส OTP ไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง")

else:
    # ----------------------------------------
    # หน้าตาแอปหลังจากล็อกอินสำเร็จแล้ว
    # ----------------------------------------
    st.balloons()
    st.subheader(f"ยินดีต้อนรับเพื่อนต๊ะ! (เบอร์: {st.session_state.user_phone})")
    st.success("ตอนนี้คุณเข้าสู่ระบบของแอป 'ยิ้มซิ' เรียบร้อยแล้ว")
    
    # เนื้อหาแอปหลักของต๊ะจะอยู่ตรงนี้
    st.info("โหมด: อยู่นิ่งๆไม่เจ็บตัว กำลังทำงาน...")
    
    if st.button("🚪 ออกจากระบบ", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_phone = ""
        st.rerun()
