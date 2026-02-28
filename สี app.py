import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="SYNAPSE X - HEART SENSOR", layout="centered")
st.markdown("<style>.stApp {background-color: #000; color: #FFD700;}</style>", unsafe_allow_html=True)

st.subheader("💓 HEART RATE MONITOR (1 MINUTE)")
st.write("สถานะ: วางมือถือแนบหน้าอกให้นิ่งที่สุด")

# JavaScript สำหรับตรวจจับจังหวะการสั่น (Pulse)
heart_js = """
<div style="background-color: #111; color: #FFD700; padding: 20px; border: 2px solid #FFD700; border-radius: 15px; font-family: monospace; text-align: center;">
    <div id="setup_ui">
        <button onclick="startHeartScan()" style="background: #FFD700; color: #000; padding: 15px 30px; border: none; border-radius: 10px; font-weight: bold; cursor: pointer;">เริ่มวัดค่า (1 นาที)</button>
    </div>
    
    <div id="scan_ui" style="display: none;">
        <h2 id="timer">60</h2>
        <p>วินาทีที่เหลือ</p>
        <div style="font-size: 40px; color: #f00; margin: 10px 0;">❤️ <span id="pulse_count">0</span></div>
        <p>จังหวะที่ตรวจพบ</p>
        <div style="width: 100%; background: #333; height: 10px; border-radius: 5px;">
            <div id="progress" style="width: 0%; background: #0f0; height: 100%; border-radius: 5px; transition: width 1s linear;"></div>
        </div>
    </div>
    
    <div id="result_ui" style="display: none;">
        <h1 style="color: #0f0;">✅ หาค่าสำเร็จ!</h1>
        <p>อัตราการเต้นของหัวใจประมาณ</p>
        <h1 id="final_bpm" style="font-size: 60px;">--</h1>
        <p>BPM (ครั้งต่อนาที)</p>
        <button onclick="location.reload()" style="background: #444; color: #fff; padding: 5px 15px; border: none; border-radius: 5px;">วัดใหม่</button>
    </div>
</div>

<script>
    let timeLeft = 60;
    let pulseCount = 0;
    let lastMagnitude = 0;
    let isScanning = false;
    let threshold = 0.02; // ค่าความไวต่อแรงสั่นหัวใจ (ปรับได้)

    async function startHeartScan() {
        if (typeof DeviceMotionEvent.requestPermission === 'function') {
            const permission = await DeviceMotionEvent.requestPermission();
            if (permission !== 'granted') return;
        }

        document.getElementById('setup_ui').style.display = 'none';
        document.getElementById('scan_ui').style.display = 'block';
        isScanning = true;

        window.addEventListener('devicemotion', (event) => {
            if (!isScanning) return;
            const acc = event.acceleration; // ใช้ acceleration แบบไม่รวมแรงโน้มถ่วงเพื่อความนิ่ง
            if (!acc) return;

            let x = acc.x || 0;
            let y = acc.y || 0;
            let z = acc.z || 0;
            let mag = Math.sqrt(x*x + y*y + z*z);

            // ตรวจจับจุดสูงสุดของการสั่น (Peak Detection)
            if (mag > threshold && lastMagnitude <= threshold) {
                pulseCount++;
                document.getElementById('pulse_count').innerText = pulseCount;
            }
            lastMagnitude = mag;
        });

        const interval = setInterval(() => {
            timeLeft--;
            document.getElementById('timer').innerText = timeLeft;
            document.getElementById('progress').style.width = ((60 - timeLeft) / 60 * 100) + '%';

            if (timeLeft <= 0) {
                clearInterval(interval);
                isScanning = false;
                showResult();
            }
        }, 1000);
    }

    function showResult() {
        document.getElementById('scan_ui').style.display = 'none';
        document.getElementById('result_ui').style.display = 'block';
        document.getElementById('final_bpm').innerText = pulseCount;
    }
</script>
"""

components.html(heart_js, height=400)

st.write("**คำแนะนำยุทธวิธี:**")
st.write("1. นอนหงาย หรือนั่งพิงให้นิ่งที่สุด (ตามสโลแกน **อยู่นิ่งๆ**)")
st.write("2. วางมือถือไว้กลางหน้าอก (ตรงตำแหน่งหัวใจ)")
st.write("3. ห้ามขยับตัวหรือพูดขณะวัดค่า เพื่อให้เซนเซอร์อ่านค่าแรงสั่นจากหัวใจได้สัตย์จริง")
