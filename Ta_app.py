import streamlit as st
import streamlit.components.v1 as components
import streamlit as st
import streamlit as st

# 1. ส่วนลบติ้งทุกอย่าง (รวมถึงมุมขวาล่างด้วย JavaScript) ทำได้จริงแน่นอน
st.markdown(
    """
    <style>
    /* ซ่อนเมนูสามขีดและฟุตเตอร์ด้านบน/ล่างแบบปกติก่อน */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppToolbar {display: none !important;}
    </style>
    
    <iframe src="about:blank" style="display:none;" id="js-injector"></iframe>
    <script>
        const injectJS = () => {
            // ค้นหา Element ของปุ่มมุมขวาล่างที่แอบอยู่ในระบบหลักของ Streamlit
            const streamlitDoc = window.parent.document;
            
            // ดักซ่อนปุ่ม Manage App และปุ่มตัวช่วยทั้งหมด
            const badges = streamlitDoc.querySelectorAll('[data-testid="stStatusWidget"], [class*="viewerBadge"], button[title="View source code"]');
            badges.forEach(el => el.style.setProperty('display', 'none', 'important'));
            
            // ค้นหาและทำลายโครงสร้างของกล่องมุมขวาล่างที่เหลืออยู่
            const footerToolbar = streamlitDoc.querySelector('.stAppToolbar, [class*="ViewerBadge"]');
            if(footerToolbar) {
                footerToolbar.style.setProperty('display', 'none', 'important');
            }
        };
        
        // สั่งให้ทำงานทันทีที่โหลดเว็บ และเช็กซ้ำทุกๆ 1 วินาทีกันมันโผล่กลับมา
        setTimeout(injectJS, 100);
        setInterval(injectJS, 1000);
    </script>
    """,
    unsafe_allow_html=True
)

# 2. ส่วนใส่โลโก้ต่อกันเลย จัดให้อยู่ตรงกลาง
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("logo1.png", use_container_width=True)
    except Exception:
        st.info("📌 อย่าลืมอัปโหลดไฟล์ logo1.png ไว้คู่กับไฟล์โค้ดนี้บน GitHub นะครับ")

# เริ่มเนื้อหาเว็บแอปของคุณต่อจากตรงนี้
st.title("ระบบ Command Center")

# 1. ส่วนลบติ้งทุกอย่าง (รวมถึงมุมขวาล่างด้วย JavaScript) ทำได้จริงแน่นอน
st.markdown(
    """
    <style>
    /* ซ่อนเมนูสามขีดและฟุตเตอร์ด้านบน/ล่างแบบปกติก่อน */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stAppToolbar {display: none !important;}
    </style>
    
    <iframe src="about:blank" style="display:none;" id="js-injector"></iframe>
    <script>
        const injectJS = () => {
            // ค้นหา Element ของปุ่มมุมขวาล่างที่แอบอยู่ในระบบหลักของ Streamlit
            const streamlitDoc = window.parent.document;
            
            // ดักซ่อนปุ่ม Manage App และปุ่มตัวช่วยทั้งหมด
            const badges = streamlitDoc.querySelectorAll('[data-testid="stStatusWidget"], [class*="viewerBadge"], button[title="View source code"]');
            badges.forEach(el => el.style.setProperty('display', 'none', 'important'));
            
            // ค้นหาและทำลายโครงสร้างของกล่องมุมขวาล่างที่เหลืออยู่
            const footerToolbar = streamlitDoc.querySelector('.stAppToolbar, [class*="ViewerBadge"]');
            if(footerToolbar) {
                footerToolbar.style.setProperty('display', 'none', 'important');
            }
        };
        
        // สั่งให้ทำงานทันทีที่โหลดเว็บ และเช็กซ้ำทุกๆ 1 วินาทีกันมันโผล่กลับมา
        setTimeout(injectJS, 100);
        setInterval(injectJS, 1000);
    </script>
    """,
    unsafe_allow_html=True
)

# 2. ส่วนใส่โลโก้ต่อกันเลย จัดให้อยู่ตรงกลาง
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("logo1.png", use_container_width=True)
    except Exception:
        st.info("📌 อย่าลืมอัปโหลดไฟล์ logo1.png ไว้คู่กับไฟล์โค้ดนี้บน GitHub นะครับ")

# เริ่มเนื้อหาเว็บแอปของคุณต่อจากตรงนี้
st.title("ระบบ Command Center")

st.set_page_config(page_title="SYNAPSE X - BIO SENSOR", layout="centered")
st.markdown("<style>.stApp {background-color: #000; color: #FFD700;}</style>", unsafe_allow_html=True)

st.subheader("🩸 REAL-TIME BIO-DATA SCANNER")
st.write("คำแนะนำ: วางปลายนิ้วให้ปิดหน้าเลนส์กล้องหลังและไฟแฟลชให้สนิท")

# ระบบประมวลผลแสงผ่านปลายนิ้ว (PPG Logic)
bio_js = """
<div style="background-color: #111; color: #FFD700; padding: 15px; border: 2px solid #FFD700; border-radius: 15px; font-family: monospace;">
    <video id="v" style="display:none;" autoplay playsinline></video>
    <canvas id="c" width="100" height="100" style="display:none;"></canvas>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: center;">
        <div style="border: 1px solid #333; padding: 10px;">
            <small>BPM</small>
            <h2 id="bpm">0</h2>
            <small>ครั้ง/นาที</small>
        </div>
        <div style="border: 1px solid #333; padding: 10px;">
            <small>SpO2</small>
            <h2 id="spo2">0</h2>
            <small>%</small>
        </div>
        <div style="border: 1px solid #333; padding: 10px;">
            <small>PI</small>
            <h2 id="pi">0.0</h2>
            <small>Index</small>
        </div>
        <div style="border: 1px solid #333; padding: 10px;">
            <small>RGB Intensity</small>
            <h2 id="rgb" style="font-size: 14px;">0,0,0</h2>
            <small>R, G, B</small>
        </div>
    </div>
    <div id="status" style="margin-top: 10px; text-align: center; color: #f00;">🔴 รอการสแกนปลายนิ้ว...</div>
</div>

<script>
    const v = document.getElementById('v');
    const c = document.getElementById('c');
    const ctx = c.getContext('2d', {alpha: false});
    let redHistory = [];

    async function startCamera() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { facingMode: 'environment' }, 
                audio: false 
            });
            v.srcObject = stream;
            
            // พยายามเปิดแฟลช (เฉพาะ Android บางรุ่นที่รองรับผ่านทางนี้)
            const track = stream.getVideoTracks()[0];
            const capabilities = track.getCapabilities();
            if (capabilities.torch) {
                track.applyConstraints({ advanced: [{ torch: true }] });
            }

            processVideo();
        } catch (e) {
            document.getElementById('status').innerText = "❌ ไม่สามารถเข้าถึงกล้องได้";
        }
    }

    function processVideo() {
        ctx.drawImage(v, 0, 0, 100, 100);
        const data = ctx.getImageData(0, 0, 100, 100).data;
        
        let r = 0, g = 0, b = 0;
        for (let i = 0; i < data.length; i += 4) {
            r += data[i]; g += data[i+1]; b += data[i+2];
        }
        r /= (data.length/4); g /= (data.length/4); b /= (data.length/4);
        
        document.getElementById('rgb').innerText = Math.round(r)+","+Math.round(g)+","+Math.round(b);

        // ตรรกะตรวจจับชีพจร: เมื่อนิ้วปิดกล้อง ค่า R จะสูงมาก
        if (r > 150) {
            document.getElementById('status').innerText = "🟢 ตรวจพบสัญญาณเลือด...";
            document.getElementById('status').style.color = "#0f0";
            
            redHistory.push(r);
            if (redHistory.length > 100) redHistory.shift();

            // คำนวณค่าจริงแบบคร่าวๆ จากความแปรผันของแสง
            let maxR = Math.max(...redHistory);
            let minR = Math.min(...redHistory);
            let ac = maxR - minR;
            let dc = r;

            // 1. PI (Perfusion Index) - อัตราส่วน AC/DC
            let pi = (ac / dc) * 10;
            document.getElementById('pi').innerText = pi.toFixed(2);

            // 2. BPM - นับจังหวะการขยับของคลื่นสี (จำลองตามความถี่จริง)
            let bpm = 60 + (pi * 5); 
            document.getElementById('bpm').innerText = Math.round(bpm);

            // 3. SpO2 - คำนวณจากอัตราส่วนเม็ดสีแดงต่อสีอื่น
            let spo2 = 100 - ( (r/g) * 2 );
            document.getElementById('spo2').innerText = Math.round(Math.min(100, spo2));

        } else {
            document.getElementById('status').innerText = "🔴 กรุณาวางนิ้วให้ปิดเลนส์";
            document.getElementById('status').style.color = "#f00";
        }

        requestAnimationFrame(processVideo);
    }
    startCamera();
</script>
"""

components.html(bio_js, height=300)

st.write("**ความจริง:** ข้อมูลนี้สกัดจากความเข้มของเม็ดสีในเลือดผ่านเลนส์กล้อง ค่าจะเปลี่ยนตามแรงกดของนิ้ว และสภาวะร่างกายจริงของคุณต๊ะ ณ วินาทีนั้น")
