import streamlit as st
import streamlit.components.v1 as components
import streamlit as st

# 1. วางโลโก้ SYNAPSE ไว้บนสุดของหน้าจอ (ดึงจากลิงก์ที่นายให้มาได้เลย)
logo_url = "https://i.ibb.co/L95x82t/SYNAPSE-Transparent.png"
st.image(logo_url, width=150) # ปรับขนาดความกว้างตามใจชอบ

st.title("SOOKSUN CALL")
st.write("ยินดีต้อนรับเข้าสู่ระบบจัดการสายเรียกเข้า")

# ... ตามด้วยโค้ดระบบล็อกอิน Firebase และปุ่มโทรเสียงเรดาร์ที่เราทำไว้ด้านบน ...

st.title("SOOKSUN CALL - ระบบทดสอบเสียงเรียกเข้า")
st.write("ดึงไฟล์เสียง SYNAPSE RADAR โดยตรงจาก GitHub ของนายมาใช้งาน")

# 1. ประกาศตัวแปรลิงก์ดิบ (Raw Link) ที่เปลี่ยนใหม่แล้ว
synapse_radar_tone = "https://raw.githubusercontent.com/taww101-sooksun/Taww101/b41c648c082e24be27fed1407735e895ee6a4e43/SYNAPSE%20RADAR.mp3"

# 2. ทำปุ่มกดจำลองสถานการณ์การโทรเข้า
btn_call = st.button("📞 จำลองสายเข้า (เสียง SYNAPSE RADAR)")

# 3. ส่วนควบคุม JavaScript เพื่อสั่งให้มือถือสั่นและเล่นเสียงพร้อมกัน
if btn_call:
    st.success("🔔 กำลังมีสายเรียกเข้า... (เปิดเสียง SYNAPSE RADAR.mp3)")
    
    components.html(f"""
        <script>
            // สั่งสั่นสะเทือนที่ตัวเครื่องมือถือ (สั่นยาว วางเว้น เป็นจังหวะตึกๆ)
            if (navigator.vibrate) {{
                navigator.vibrate([600, 400, 600, 400, 600, 400, 1000]);
            }}

            // เล่นเสียงเรียกเข้าเรดาร์จาก GitHub วนลูปไปเรื่อยๆ จนกว่าจะรับสาย
            var audio = new Audio('{synapse_radar_tone}');
            audio.loop = true;
            audio.play().catch(function(error) {{
                console.log("บราวเซอร์บล็อกการเล่นเสียงอัตโนมัติ ต้องมีการปฏิสัมพันธ์ก่อน:", error);
            }});
        </script>
    """, height=0)
