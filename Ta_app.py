import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SYNAPSE X - MOTION SENSOR", layout="centered")
st.markdown("<style>.stApp {background-color: #000; color: #FFD700;}</style>", unsafe_allow_html=True)

st.subheader("📳 REAL-TIME VIBRATION DETECTOR")
st.write("สถานะ: ตรวจจับการสั่นสะเทือนรอบตัว (หน่วย: G-Force)")

# JavaScript เพื่อดึงค่า Accelerometer จากมือถือโดยตรง
motion_js = """
<div style="background-color: #111; color: #FFD700; padding: 20px; border: 2px solid #FFD700; border-radius: 15px; font-family: monospace; text-align: center;">
    <div style="display: grid; grid-template-columns: 1fr; gap: 15px;">
        <div>
            <small>แรงสั่นสะเทือนรวม (Magnitude)</small>
            <h1 id="mag_val" style="font-size: 50px; color: #0f0;">0.000</h1>
            <p>G (m/s²)</p>
        </div>
        <hr style="border-color: #333;">
        <div style="display: flex; justify-content: space-around; font-size: 14px;">
            <div>แกน X: <span id="x_val">0</span></div>
            <div>แกน Y: <span id="y_val">0</span></div>
            <div>แกน Z: <span id="z_val">0</span></div>
        </div>
    </div>
    <p id="motion_info" style="margin-top: 15px; color: #888;">สถานะ: รอการขยับ...</p>
</div>

<script>
    let sensor = null;
    
    async function startMotion() {
        // ขอสิทธิ์สำหรับ iOS (ถ้ามี)
        if (typeof DeviceMotionEvent.requestPermission === 'function') {
            const permission = await DeviceMotionEvent.requestPermission();
            if (permission !== 'granted') {
                document.getElementById('motion_info').innerText = "❌ ถูกปฏิเสธสิทธิ์";
                return;
            }
        }

        window.addEventListener('devicemotion', (event) => {
            const acc = event.accelerationIncludingGravity;
            if (!acc) return;

            let x = acc.x || 0;
            let y = acc.y || 0;
            let z = acc.z || 0;

            // คำนวณแรงรวม (Magnitude)
            let magnitude = Math.sqrt(x*x + y*y + z*z) / 9.80665; // หารด้วยแรงโน้มถ่วงโลกเพื่อให้ค่านิ่งที่ ~1.0 เมื่อวางเฉยๆ

            document.getElementById('x_val').innerText = x.toFixed(3);
            document.getElementById('y_val').innerText = y.toFixed(3);
            document.getElementById('z_val').innerText = z.toFixed(3);
            document.getElementById('mag_val').innerText = magnitude.toFixed(4);

            if (magnitude > 1.05 || magnitude < 0.95) {
                document.getElementById('mag_val').style.color = "#f00";
                document.getElementById('motion_info').innerText = "⚠️ ตรวจพบแรงสั่นสะเทือน!";
            } else {
                document.getElementById('mag_val').style.color = "#0f0";
                document.getElementById('motion_info').innerText = "🟢 สถานะนิ่ง (ความจริงคงที่)";
            }
        });
    }

    startMotion();
</script>
"""

components.html(motion_js, height=300)

st.write("**ความจริงหน้างาน:**")
st.write("1. วางมือถือบนพื้นที่นิ่งที่สุด ค่าจะเข้าใกล้ **1.0000 G** (แรงโน้มถ่วงโลก)")
st.write("2. ลองเคาะโต๊ะเบาๆ หรือเดินใกล้ๆ มือถือ ตัวเลขจะดีดทันที")
st.write("3. นี่คือค่าดิบจากเซนเซอร์ **Accelerometer** ไม่มีการแต่งตัวเลขครับ")
