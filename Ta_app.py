import streamlit as st
import streamlit.components.v1 as components

st.title("SOOKSUN CALL - ระบบทดสอบเสียงเรียกเข้า")
st.write("ดึงไฟล์เสียงโดยตรงจาก GitHub ของนายมาใช้งาน")

# 1. ประกาศตัวแปรลิงก์ดิบ (Raw Link) ที่แปลงแล้ว
evening_tone = "https://raw.githubusercontent.com/taww101-sooksun/Taww101/7904d735c8527a34c54f36d6cfaa318e96eba352/test_evening.mp3"
morning_tone = "https://raw.githubusercontent.com/taww101-sooksun/Taww101/7904d735c8527a34c54f36d6cfaa318e96eba352/test_morning.mp3"

# 2. ทำปุ่มกดจำลองสถานการณ์การโทรเข้า
col1, col2 = st.columns(2)

with col1:
    btn_morning = st.button("📞 จำลองสายเข้า (เสียงเช้า)")
with col2:
    btn_evening = st.button("🌙 จำลองสายเข้า (เสียงเย็น)")

# 3. ส่วนควบคุม JavaScript เพื่อสั่งให้มือถือเล่นเสียงและสั่นพร้อมกัน
selected_tone = None

if btn_morning:
    st.success("กำลังเรียกเข้าด้วยเสียง: test_morning.mp3")
    selected_tone = morning_tone

elif btn_evening:
    st.warning("กำลังเรียกเข้าด้วยเสียง: test_evening.mp3")
    selected_tone = evening_tone

# ถ้ามีการกดปุ่ม ให้ส่งคำสั่ง JavaScript ไปจัดการที่ตัวเครื่องมือถือทันที
if selected_tone:
    components.html(f"""
        <script>
            // สั่งสั่นสะเทือนที่ตัวเครื่องมือถือ (สั่นยาว วางเว้น เป็นจังหวะ)
            if (navigator.vibrate) {{
                navigator.vibrate([600, 400, 600, 400, 600, 400, 1000]);
            }}

            // เล่นเสียงเรียกเข้าจาก GitHub วนลูปไปเรื่อยๆ
            var audio = new Audio('{selected_tone}');
            audio.loop = true;
            audio.play().catch(function(error) {{
                console.log("บราวเซอร์บล็อกการเล่นเสียงอัตโนมัติ ต้องมีการกดปุ่มจากผู้ใช้ก่อน:", error);
            }});
        </script>
    """, height=0)
