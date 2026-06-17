import streamlit as st
import os
import base64

# --- [ บรรทัดแรกสุดของไฟล์ ห้ามย้ายเด็ดขาด ] ---
st.set_page_config(page_title="SYNAPSE QUANTUM PLAYER", layout="centered")

# =========================================================
# 🎨 ปรับปรุง CSS ใหม่ทั้งหมด: บังคับทุกอย่างอยู่ตรงกลาง คุมโทนนีออน
# =========================================================
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    
    /* พื้นหลังดำลึก */
    .stApp {
        background-color: #030305 !important;
        color: #FFFFFF !important;
        border-top: 6px solid #ff0055; /* เส้นขอบบนสุดสีแดงนีออน */
    }
    
    /* หัวข้อเรืองแสงน้ำเงิน-ม่วง */
    .neon-title {
        color: #FFFFFF;
        text-shadow: 0 0 10px #00f3ff, 0 0 20px #bd00ff;
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 2px;
        margin-bottom: 5px;
    }
    
    /* ส่วนควบคุมการแสดงผลวงกลมและโลโก้ให้อยู่รวมกันตรงกลาง */
    .avatar-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 30px auto;
        position: relative;
        width: 200px;
        height: 200px;
    }

    /* วงกลมเรืองแสงเต้นตามจังหวะชีพจร (Pulse) เปลี่ยนสี นีออน 3 สี */
    .neon-pulse-circle {
        position: absolute;
        width: 100%;
        height: 100%;
        border-radius: 50%;
        border: 4px solid #00f3ff;
        box-shadow: 0 0 20px #00f3ff, inset 0 0 15px #00f3ff;
        animation: cyberPulse 2s infinite alternate ease-in-out;
        z-index: 1;
    }

    @keyframes cyberPulse {
        0% {
            transform: scale(0.95);
            border-color: #00f3ff;
            box-shadow: 0 0 15px #00f3ff, inset 0 0 10px #00f3ff;
        }
        50% {
            border-color: #bd00ff;
            box-shadow: 0 0 30px #bd00ff, inset 0 0 20px #bd00ff;
        }
        100% {
            transform: scale(1.05);
            border-color: #ff0055;
            box-shadow: 0 0 45px #ff0055, inset 0 0 25px #ff0055;
        }
    }

    /* รูปโลโก้ข้างในวงกลม บังคับให้อยู่กึ่งกลางพอดี ไม่หลุดเฟรม */
    .logo-core {
        position: absolute;
        width: 170px;
        height: 170px;
        border-radius: 50%;
        object-fit: cover;
        z-index: 2;
        border: 2px solid #050505;
        background-color: #0d0d11;
    }
    
    /* สัญลักษณ์ข้อความกรณีไม่มีรูป */
    .text-core {
        position: absolute;
        z-index: 2;
        font-size: 50px;
        margin: 0;
        animation: textGlow 2s infinite alternate;
    }
    
    @keyframes textGlow {
        0% { text-shadow: 0 0 10px #00f3ff; color: #00f3ff; }
        100% { text-shadow: 0 0 20px #ff0055; color: #ff0055; }
    }

    /* กล่องเครื่องเล่นเพลงด้านล่าง */
    .neon-box {
        background: #0d0d11;
        border: 2px solid #00f3ff;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.15);
        margin-top: 10px;
    }
    
    .neon-status {
        color: #00ff66;
        text-shadow: 0 0 8px #00ff66;
        font-family: monospace;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# ⚙️ ฟังก์ชันแปลงรูปภาพเป็น Base64 (ป้องกันรูปแตก แนะนำทำจริงรอด 100%)
# =========================================================
def get_base64_image(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

# ตรวจสอบคลังเพลง .mp3 ในโฟลเดอร์ปัจจุบัน
current_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()
song_list = sorted([f for f in os.listdir(current_dir) if f.lower().endswith(".mp3")])

# แสดงชื่อหัวข้อหลัก
st.markdown('<h1 class="neon-title" style="text-align:center;">SYNAPSE QUANTUM PLAYER</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#888; font-family:sans-serif;">📊 NEXT-GEN AUDIO RADAR | อยู่นิ่งๆ ไม่เจ็บตัว</p>', unsafe_allow_html=True)
st.write("---")

# =========================================================
# 🖼️ รวมร่าง: โลโก้ + กรอบวงกลมเรืองแสงเต้นได้ให้อยู่จุดเดียวกัน
# =========================================================
logo_file_path = os.path.join(current_dir, "logo1.png")
img_base64 = get_base64_image(logo_file_path)

# เริ่มต้นกล่องห่อหุ้มแกนกลาง
st.markdown('<div class="avatar-wrapper">', unsafe_allow_html=True)
st.markdown('<div class="neon-pulse-circle"></div>', unsafe_allow_html=True) # ตัววงกลมเรืองแสงที่เต้น

if img_base64:
    # ถ้ารูปภาพ logo1.png มีอยู่จริง จะถูกดึงมาครอบให้อยู่ตรงกลางวงกลมพอดีเป๊ะ ไม่หนีไปไหน
    st.markdown(f'<img src="data:image/png;base64,{img_base64}" class="logo-core">', unsafe_allow_html=True)
else:
    # หากไม่มีรูปภาพ จะแสดงแกนพลังงานข้อความเรืองแสงสลับสีแทน
    st.markdown('<h1 class="text-core">🧬</h1>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 📈 เส้นกราฟชีพจรเสียงวิ่งสด (HTML5 Canvas สีเขียวนีออน)
# =========================================================
pulse_graph_html = """
<div style="background:#050508; border:1px solid #222; border-radius:10px; padding:5px;">
    <canvas id="pulseCanvas" style="width:100%; height:60px;"></canvas>
</div>
<script>
    const canvas = document.getElementById('pulseCanvas');
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth;
    canvas.height = 60;
    
    let x = 0;
    ctx.strokeStyle = '#00ff66'; 
    ctx.lineWidth = 2;
    ctx.shadowBlur = 10;
    ctx.shadowColor = '#00ff66';
    
    function drawPulse() {
        ctx.fillStyle = 'rgba(5, 5, 8, 0.12)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.beginPath();
        ctx.moveTo(x, canvas.height / 2);
        
        let y = canvas.height / 2;
        if (Math.random() < 0.15) { 
            y = (Math.random() < 0.5) ? (10 + Math.random()*10) : (40 + Math.random()*10);
        } else {
            y = (canvas.height / 2) + (Math.random() * 4 - 2);
        }
        
        x += 3;
        if (x > canvas.width) x = 0;
        
        ctx.lineTo(x, y);
        ctx.stroke();
        requestAnimationFrame(drawPulse);
    }
    drawPulse();
</script>
"""

# =========================================================
# 🎛️ กล่องแผงควบคุมระบบเสียง
# =========================================================
if not song_list:
    st.error("❌ ไม่พบไฟล์ .mp3 ในเซิร์ฟเวอร์ กรุณาตรวจสอบคลังบน GitHub ของนาย")
else:
    st.markdown('<div class="neon-box">', unsafe_allow_html=True)
    
    selected_song = st.selectbox("🎵 ค้นพบสัญญาณเสียงในคลัง (SELECT TRACK):", song_list)
    
    if selected_song:
        st.markdown(f"📡 **FREQUENCY:** `STREAMING // {selected_song.upper()}`")
        st.markdown('<span class="neon-status">STATUS: TRANSMITTING SIGNAL...</span>', unsafe_allow_html=True)
        
        # แทรกตัวกราฟชีพจรสีเขียวนีออน
        import streamlit.components.v1 as components
        components.html(pulse_graph_html, height=75)
        
        # โหลดเสียงเพลงมาเล่นจริง
        song_bytes = open(os.path.join(current_dir, selected_song), "rb").read()
        st.audio(song_bytes, format="audio/mp3")
        
    st.markdown('</div>', unsafe_allow_html=True)

    # คลังรายชื่อแบบพับเก็บได้
    with st.expander("📂 ดูฐานข้อมูลคลังเพลงทั้งหมด"):
        for index, song in enumerate(song_list, start=1):
            st.write(f"`[{index:02d}]` -- {song}")
