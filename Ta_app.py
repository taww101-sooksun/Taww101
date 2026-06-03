import streamlit as st
import streamlit.components.v1 as components

# สั่งตั้งค่าหน้าจอให้แสดงผลสวยงามบนมือถือ
st.set_page_config(page_title="SYNAPSE", page_icon="🔮", layout="centered")

# --- 1. แสดงผลโลโก้ตัวจริง (อยู่นิ่งๆ ไม่เจ็บตัว SYNAPSE) ---
# ถ้านายได้ลิงก์รูปภาพของนายมาแล้ว ให้เอามาวางแทนที่ลิงก์จำลองด้านล่างนี้ได้เลยครับ
# เปลี่ยนลิงก์ด้านล่างนี้ให้เป็นลิงก์ Raw ของไฟล์ Logo1.png จาก GitHub ของนาย
logo_url = "https://raw.githubusercontent.com/taww101-sooksun/Taww101/main/Logo1.png"
st.image(logo_url, use_container_width=True)

st.markdown("---")

# --- 2. ระบบอินเตอร์เฟสจำลองการล็อกอิน Firebase ---
st.subheader("🔐 ระบบตรวจสอบสิทธิ์เข้าใช้งาน")
st.write("เลือกวิธีเข้าสู่ระบบเพื่อแยกแยะบัญชีผู้ใช้งาน (รองรับ 100 คนข้อมูลไม่มั่วกัน)")

login_method = st.radio("เลือกวิธีล็อกอิน:", ["อีเมล/รหัสผ่าน", "เบอร์โทรศัพท์ (OTP)", "Google Account"])

if login_method == "อีเมล/รหัสผ่าน":
    email = st.text_input("อีเมล")
    password = st.text_input("รหัสผ่าน", type="password")
    btn_login = st.button("เข้าสู่ระบบด้วยอีเมล")

elif login_method == "เบอร์โทรศัพท์ (OTP)":
    phone = st.text_input("ระบุเบอร์โทรศัพท์ของคุณ")
    btn_otp = st.button("ขอรหัส OTP")

elif login_method == "Google Account":
    st.info("ระบบพร้อมเชื่อมต่อผ่าน Google Client ID ของคุณ")
    btn_google = st.button("Sign in with Google")

st.markdown("---")

# --- 3. ระบบทดสอบสายเรียกเข้าพร้อมเสียง SYNAPSE RADAR และระบบสั่น ---
st.subheader("📞 สัญญาณเรียกเข้าส่วนตัว")
st.write("ระบบโครงข่ายจำลองการโทรตรงโดยไม่ผ่านแอปพลิเคชันอื่น")

# ลิงก์เสียงเรดาร์ดิบจาก GitHub ของนาย
synapse_radar_tone = "https://raw.githubusercontent.com/taww101-sooksun/Taww101/b41c648c082e24be27fed1407735e895ee6a4e43/SYNAPSE%20RADAR.mp3"

btn_call = st.button("⚡ ทดสอบ: จำลองมีสายโทรเข้า")

if btn_call:
    st.success("🔔 กำลังมีสายเรียกเข้า... (กำลังเล่นเสียง SYNAPSE RADAR และสั่งสั่นตัวเครื่อง)")
    
    # คำสั่งส่งงานให้บราวเซอร์มือถือสั่งสั่นและเล่นเสียงพร้อมกันจริง
    components.html(f"""
        <script>
            // สั่งสั่นสะเทือนที่เครื่องมือถือของผู้รับสาย
            if (navigator.vibrate) {{
                navigator.vibrate([600, 400, 600, 400, 600, 400, 1000]);
            }}

            // ดึงไฟล์เสียงเรดาร์จาก GitHub ของนายมาเล่นวนลูป
            var audio = new Audio('{synapse_radar_tone}');
            audio.loop = true;
            audio.play().catch(function(error) {{
                console.log("บราวเซอร์ล็อกเสียงอัตโนมัติ ต้องสัมผัสหน้าจอก่อน 1 ครั้ง:", error);
            }});
        </script>
    """, height=0)
