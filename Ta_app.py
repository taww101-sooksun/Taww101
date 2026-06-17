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
