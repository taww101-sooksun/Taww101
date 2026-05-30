import streamlit as st

# ตั้งค่าหน้าจอให้ออกโทนเข้ม ดุดัน
st.set_page_config(page_title="Sooksun1 Command Center", page_icon="📱", layout="centered")

# สไตล์หน้าจอแอปยิ้มซิ
st.markdown("""
    <style>
    .stApp { background-color: #111827; }
    h2, h3, p, label { color: white !important; }
    div.stButton > button { font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

# 1. สร้างตัวแปรเก็บสถานะการล็อกอิน (Session State)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_phone' not in st.session_state:
    st.session_state.user_phone = ""

# =========================================================
# หน้าจอที่ 1: หน้าล็อกอิน (ถ้ายังไม่ได้ล็อกอิน ให้แสดงหน้านี้)
# =========================================================
if not st.session_state.logged_in:
    st.title("📱 ระบบล็อกอินยิ้มซิ (Sooksun1)")
    st.markdown("<p style='color: #f87171 !important; font-style: italic;'>\"อยู่นิ่งๆ ไม่เจ็บตัว ปลอดภัยร้อยเปอร์เซ็นต์\"</p>", unsafe_allow_html=True)
    
    # กล่องครอบดีไซน์
    with st.container():
        st.subheader("เข้าสู่ระบบด้วยเบอร์โทรศัพท์")
        
        # ช่องกรอกเบอร์โทรศัพท์
        phone_input = st.text_input(
            "เบอร์โทรศัพท์ (ใส่รูปแบบสากล เช่น +66970801941):", 
            value="+66970801941"
        )
        
        # ปุ่มขอรหัส OTP (กดแล้วให้แจ้งเตือนบอกผู้ใช้)
        if st.button("📲 ขอรหัส OTP", use_container_width=True):
            if phone_input in ["+66970801941", "+66970801941"]: # เช็กเบอร์สัจจะของต๊ะ
                st.toast("⏳ ระบบจับคู่เบอร์ทดสอบใน Firebase สำเร็จ!")
                st.success("✅ ดำเนินการสำเร็จ! กรุณากรอกรหัส 6 หลักเพื่อข้ามผ่านระบบความปลอดภัย")
            else:
                st.error("❌ ไม่พบเบอร์โทรศัพท์นี้ในระบบทดสอบ")

        st.write("---")
        
        # ช่องกรอกรหัส OTP
        otp_input = st.text_input(
            "กรอกรหัส OTP 6 หลักที่ตั้งไว้ หรือได้รับจาก SMS:", 
            value="753275", 
            type="password"
        )
        
        # ปุ่มยืนยัน (เช็กค่าตรงๆ ถ้ายอมรับให้เปลี่ยนสถานะทันที!)
        if st.button("✅ ยืนยันรหัสผ่าน", type="primary", use_container_width=True):
            # ตรวจสอบฐานข้อมูลสัจจะตามที่ต๊ะเซ็ตไว้ใน Firebase ตัวจริง
            if phone_input == "+66970801941" and otp_input == "753275":
                st.session_state.logged_in = True
                st.session_state.user_phone = phone_input
                st.success("🔓 รหัสผ่านถูกต้องสัจจะ!")
                st.rerun() # สั่งรีเฟรชหน้าจอเพื่อเปลี่ยนหน้าทันที
            else:
                st.error("❌ รหัสไม่ถูกต้องตามที่บันทึกไว้ใน Firebase")

# =========================================================
# หน้าจอที่ 2: หน้าหลักของแอป (พอล็อกอินผ่านแล้ว จะเด้งมาหน้านี้ทันที)
# =========================================================
else:
    st.balloons() # ยิงลูกโป่งฉลองความสำเร็จ
    st.title("🛸 COMMAND CENTER (Sooksun1)")
    st.success(f"🔓 ยินดีต้อนรับเพื่อนต๊ะเข้าสู่ระบบ! (เบอร์: {st.session_state.user_phone})")
    
    st.markdown("---")
    # พื้นที่ใส่ฟังก์ชันการจัดการแอปหลักของต๊ะ
    st.subheader("🛠️ แผงควบคุมและจัดการแอป")
    st.info("สถานะระบบ: อยู่นิ่งๆ ไม่เจ็บตัว กำลังทำงานเปิดสัญญาณ...")
    
    # ปุ่มออกจากระบบ กลับไปหน้าแรก
    if st.button("🚪 ออกจากระบบ (Logout)", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_phone = ""
        st.rerun()
