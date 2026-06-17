import streamlit as st
import os

# --- [ บรรทัดแรกสุดของไฟล์ ห้ามย้ายเด็ดขาด ] ---
st.set_page_config(page_title="SYNAPSE NEON HUB", layout="centered")

# =========================================================
# 🎨 ลูกเล่นแพรวพราว CSS Neon Animation + กรอบโลโก้เต้นได้
# =========================================================
st.markdown("""
    <style>
    header, footer, #MainMenu {visibility: hidden;}
    
    .stApp {
        background-color: #030305 !important;
        color: #FFFFFF !important;
        border-top: 6px solid #ff0055;
    }
    
    /* กรอบโลโก้เรืองแสงนีออน มีเอฟเฟกต์เต้นตุบๆ (Pulse) ตลอดเวลา */
    .logo-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 25px auto;
        width: 170px;
        height: 170px;
        background: #0d0d11;
        border-radius: 50%;
        border: 3px solid #00f3ff;
        box-shadow: 0 0 15px #00f3ff, inset 0 0 15px #00f3ff;
        animation: neonPulse 1.8s infinite alternate;
    }

    @keyframes neonPulse {
        0% {
            box-shadow: 0 0 10px #00f3ff, inset 0 0 10px #00f3ff;
            transform: scale(0.98);
            border-color: #00f3ff;
        }
        50% {
            border-color: #bd00ff;
            box-shadow: 0 0 25px #bd00ff, inset 0 0 15px #bd00ff;
        }
        100% {
            box-shadow: 0 0 35px #ff0055, inset 0 0 20px #ff0055;
            transform: scale(1.04);
            border-color: #ff0055;
        }
    }
    
    /* กล่องเครื่องเล่นสไตล์ไซไฟ */
    .neon-box {
        background: linear-gradient(135deg, #0d0d11 0%, #151522 100%);
        border: 2px solid #bd00ff;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 0 20px rgba(189, 0, 255, 0.2);
        margin-bottom: 20px;
    }
    
    .neon-title {
        color: #FFFFFF;
        text-shadow: 0 0 10px #bd00ff, 0 0 20px #00f3ff;
        font-family: 'Orbitron', sans-serif;
        letter-spacing: 3px;
    }
    
    .neon-status {
        color: #00ff66;
        text-shadow: 0 0 8px rgba(0, 255, 102, 0.8);
        font-family: monospace;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# ⚙️ ระบบจัดการไฟล์เพลง
# =========================================================
current_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else os.getcwd()
song_list = sorted([f for f in os.listdir(current_dir) if f.lower().endswith(".mp3")])

st.markdown('<h1 class="neon-title" style="text-align:center;">SYNAPSE QUANTUM PLAYER</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#888;">📊 NEXT-GEN AUDIO RADAR | อยู่นิ่งๆ ไม่เจ็บตัว</p>', unsafe_allow_html=True)
st.write("---")

# =========================================================
# 🖼️ หน้าจอแสดงผลกรอบโลโก้เรืองแสงแบบเต้นได้
# =========================================================
logo_path = os.path.join(current_dir, "logo1.png")

st.markdown('<div class="logo-container">', unsafe_allow_html=True)
if os.path.exists(logo_path):
    # ปรับสไตล์ให้รูปโลโก้ตัดเป็นทรงกลมเข้ากับกรอบที่เต้น
    st.markdown(f'<img src="data:image/png;base64,{st.image(logo_path, width=140)}" style="border-radius:50%;">', unsafe_allow_html=True)
else:
    # ถ้าไม่มีรูปโลโก้ จะขึ้นแกนพลังงานนีออนสลับสีไปมาตามจังหวะอนิเมชั่น
    st.markdown('<h1 style="margin:0; font-size:45px; font-family:monospace;">🧬</h1>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 📈 ลูกเล่นแพรวพราว: เส้นกราฟชีพจรเสียงวิ่งสด (HTML5 Canvas)
# =========================================================
pulse_graph_html = """
<div style="background:#050508; border:1px solid #333; border-radius:10px; padding:5px;">
    <canvas id="pulseCanvas" style="width:100%; height:80px;"></canvas>
</div>

<script>
    const canvas = document.getElementById('pulseCanvas');
    const ctx = canvas.getContext('2d');
    
    // ตั้งค่าขนาดบอร์ด
    canvas.width = canvas.offsetWidth;
    canvas.height = 80;
    
    let x = 0;
    ctx.strokeStyle = '#00ff66'; // เส้นชีพจรสีเขียวนีออน
    ctx.lineWidth = 2;
    ctx.shadowBlur = 8;
    ctx.shadowColor = '#00ff66';
    
    function drawPulse() {
        // เคลียร์หน้าจอทีละนิดเพื่อให้เห็นหางจางๆ
        ctx.fillStyle = 'rgba(5, 5, 8, 0.1)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.beginPath();
        ctx.moveTo(x, canvas.height / 2);
        
        // สุ่มสร้างคลื่นชีพจรแบบหยักหัวใจ (Heartbeat Pulse)
        let y = canvas.height / 2;
        if (Math.random() < 0.15) { 
            // จังหวะหัวใจเต้นแรง
            y = (Math.random() < 0.5) ? (15 + Math.random()*15) : (50 + Math.random()*15);
        } else {
            // จังหวะเคลื่อนไหวเบาๆ นิ่งๆ
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
# 🎛️ เครื่องเล่นและการตั้งค่าเล่นต่อเนื่อง
# =========================================================
if not song_list:
    st.error("❌ ไม่พบไฟล์ .mp3 ในเซิร์ฟเวอร์ กรุณาโยนไฟล์เพลงลง GitHub โฟลเดอร์เดียวกับโค้ดด้วยนะเพื่อน")
else:
    st.markdown('<div class="neon-box">', unsafe_allow_html=True)
    
    # รายการเลือกเพลง
    selected_song = st.selectbox("🎵 ค้นพบสัญญาณเสียงในคลัง (SELECT TRACK):", song_list)
    
    if selected_song:
        st.markdown(f"📡 **FREQUENCY:** `STREAMING // {selected_song.upper()}`")
        st.markdown('<span class="neon-status">STATUS: TRANSMITTING SIGNAL...</span>', unsafe_allow_html=True)
        
        # แสดงผลกราฟชีพจรเสียงเต้น
        import streamlit.components.v1 as components
        components.html(pulse_graph_html, height=95)
        
        # ตัวเล่นเสียง
        song_bytes = open(os.path.join(current_dir, selected_song), "rb").read()
        
        # บังคับเปิด HTML5 Audio Player แท้ๆ เพื่อให้รองรับฟังชั่นพื้นฐานของเบราว์เซอร์
        # ซึ่งเบราว์เซอร์บนมือถือหรือคอมส่วนใหญ่จะเล่นต่อให้อัตโนมัติเมื่อกด Play
        st.audio(song_bytes, format="audio/mp3")
        
    st.markdown('</div>', unsafe_allow_html=True)

    # แสดงคลังข้อมูลท้ายแอป
    with st.expander("📂 ดูฐานข้อมูลคลังเพลงทั้งหมด"):
        for index, song in enumerate(song_list, start=1):
            st.write(f"`[{index:02d}]` -- {song}")
