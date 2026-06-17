import streamlit as st
import os
import base64

# --- [ บรรทัดแรกสุดของไฟล์ ห้ามย้ายเด็ดขาด ] ---
st.set_page_config(page_title="SYNAPSE QUANTUM PLAYER", layout="centered")

# =========================================================
# 🎨 ปรับปรุง CSS ใหม่หมดจด: บังคับให้อยู่กึ่งกลางหน้าจอ ไม่แยกห่างกัน
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
    
    /* จัดระเบียบคอนเทนเนอร์หลักให้กระชับ ไม่ห่างเกินไป */
    .main-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        width: 100%;
        margin: 0 auto;
    }

    /* หัวข้อเรืองแสงน้ำเงิน-ม่วง */
    .neon-title {
        color: #FFFFFF;
        text-shadow: 0 0 10px #00f3ff, 0 0 20px #bd00ff;
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 2px;
        margin-top: 10px;
        margin-bottom: 2px;
        font-size: 28px;
    }
    
    /* 🧬 รวมวงกลมและโลโก้ด้วย Flexbox ป้องกันการหล่นไปกองที่ขอบล่าง */
    .avatar-box {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 180px;
        height: 180px;
        margin: 20px auto;
        border-radius: 50%;
        position: relative;
        /* วงกลมเรืองแสงเต้นสลับสี แดง น้ำเงิน ม่วง นีออน */
        border: 4px solid #00f3ff;
        box-shadow: 0 0 15px #00f3ff, inset 0 0 10px #00f3ff;
        animation: cyberPulse 2s infinite alternate ease-in-out;
    }

    @keyframes cyberPulse {
        0% {
            transform: scale(0.96);
            border-color: #00f3ff;
            box-shadow: 0 0 15px #00f3ff, inset 0 0 10px #00f3ff;
        }
        50% {
            border-color: #bd00ff;
            box-shadow: 0 0 25px #bd00ff, inset 0 0 15px #bd00ff;
        }
        100% {
            transform: scale(1.04);
            border-color: #ff0055;
            box-shadow: 0 0 35px #ff0055, inset 0 0 20px #ff0055;
        }
    }

    /* บังคับรูปโลโก้ logo1.png ให้อยู่กึ่งกลางของวงกลมเรืองแสงพอดีเป๊ะ */
    .logo-inside {
        width: 154px;
        height: 154px;
        border-radius: 50%;
        object-fit: cover;
        background-color: #0d0d11;
        border: 2px solid #030305;
    }
    
    .text-inside {
        font-size: 50px;
        margin: 0;
        text-shadow: 0 0 15px #00f3ff;
    }

    /* กล่องแผงควบคุมเพลงด้านล่าง */
    .neon-player-panel {
        background: #0d0d11;
        border: 2px solid #00f3ff;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.15);
        width: 100%;
        margin-top: 15px;
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
# ⚙️ ระบบดึงรูปภาพและไฟล์เพลง
# =========================================================
def get_base64_image(img_path):
    if os.path.exists(img_path):
        with open(img_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return None

current_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()
song_list = sorted([f for f in os.listdir(current_dir) if f.lower().endswith(".mp3")])

# =========================================================
# 🖥️ หน้าจอแสดงผลหลัก (จัดกลุ่มให้อยู่รวมกัน)
# =========================================================
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# 1. ส่วนหัวข้อแอป
st.markdown('<h1 class="neon-title">SYNAPSE QUANTUM PLAYER</h1>', unsafe_allow_html=True)
st.markdown('<p style="color:#888; font-family:sans-serif; margin-bottom:5px;">📊 NEXT-GEN AUDIO RADAR | อยู่นิ่งๆ ไม่เจ็บตัว</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 2. ส่วนวงกลมเรืองแสง + โลโก้ รวมร่างกันตรงกลาง (ไม่ห่างกันแล้ว)
logo_file_path = os.path.join(current_dir, "logo1.png")
img_base64 = get_base64_image(logo_file_path)

if img_base64:
    # นำรูปโลโก้ใส่เข้าไปฝังในกล่องวงกลมเรืองแสงโดยตรง
    st.markdown(f"""
        <div class="avatar-box">
            <img src="data:image/png;base64,{img_base64}" class="logo-inside">
        </div>
    """, unsafe_allow_html=True)
else:
    # กรณีไม่มีรูปภาพ ให้แสดงอีโมจิเรืองแสงในวงกลมแทน
    st.markdown("""
        <div class="avatar-box">
            <span class="text-inside">🧬</span>
        </div>
    """, unsafe_allow_html=True)

# =========================================================
# 📈 เส้นกราฟชีพจรเสียงวิ่งสด (HTML5 Canvas สีเขียวนีออน)
# =========================================================
pulse_graph_html = """
<div style="background:#050508; border:1px solid #222; border-radius:8px; padding:3px;">
    <canvas id="pulseCanvas" style="width:100%; height:50px;"></canvas>
</div>
<script>
    const canvas = document.getElementById('pulseCanvas');
    const ctx = canvas.getContext('2d');
    canvas.width = canvas.offsetWidth;
    canvas.height = 50;
    
    let x = 0;
    ctx.strokeStyle = '#00ff66'; 
    ctx.lineWidth = 2;
    ctx.shadowBlur = 8;
    ctx.shadowColor = '#00ff66';
    
    function drawPulse() {
        ctx.fillStyle = 'rgba(5, 5, 8, 0.15)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.beginPath();
        ctx.moveTo(x, canvas.height / 2);
        
        let y = canvas.height / 2;
        if (Math.random() < 0.15) { 
            y = (Math.random() < 0.5) ? (8 + Math.random()*8) : (35 + Math.random()*8);
        } else {
            y = (canvas.height / 2) + (Math.random() * 3 - 1.5);
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
# 🎛️ กล่องแผงควบคุมระบบเสียงด้านล่างถัดลงมาพอดีๆ
# =========================================================
if not song_list:
    st.error("❌ ไม่พบไฟล์ .mp3 ในเซิร์ฟเวอร์ กรุณาตรวจสอบคลังบน GitHub ของนาย")
else:
    st.markdown('<div class="neon-player-panel">', unsafe_allow_html=True)
    
    selected_song = st.selectbox("🎵 เลือกสัญญาณเสียงในคลัง (SELECT TRACK):", song_list)
    
    if selected_song:
        st.markdown(f"📡 **FREQUENCY:** `STREAMING // {selected_song.upper()}`")
        st.markdown('<span class="neon-status">STATUS: TRANSMITTING SIGNAL...</span>', unsafe_allow_html=True)
        
        # แทรกตัวกราฟชีพจรสีเขียวนีออน
        import streamlit.components.v1 as components
        components.html(pulse_graph_html, height=65)
        
        # เครื่องเล่นเพลงของ Streamlit
        song_bytes = open(os.path.join(current_dir, selected_song), "rb").read()
        st.audio(song_bytes, format="audio/mp3")
        
    st.markdown('</div>', unsafe_allow_html=True)

    # คลังรายชื่อแบบพับเก็บได้
    with st.expander("📂 ดูฐานข้อมูลคลังเพลงทั้งหมด"):
        for index, song in enumerate(song_list, start=1):
            st.write(f"`[{index:02d}]` -- {song}")
