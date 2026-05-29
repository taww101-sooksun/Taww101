import streamlit as st
import base64

# ==========================================
# ส่วนที่ 1: การตั้งค่าหน้าจอและ CSS (Cyberpunk Neon)
# ==========================================

st.set_page_config(page_title="Synapse Neon Video Deck", layout="centered")

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_base64 = get_base64_image("logo1.png")
logo_html_link = f"data:image/png;base64,{logo_base64}" if logo_base64 else ""

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    .stApp {{ background-color: #000; }}

    .neon-title {{
        font-family: 'Orbitron', sans-serif;
        color: #fff;
        text-align: center;
        text-shadow: 0 0 10px #ff00de, 0 0 20px #00f3ff;
        font-size: 1.6rem;
        margin-top: 40px; /* ขยับขึ้นมาด้านบนเนื่องจากย้ายโลโก้ออกไปแล้ว */
        letter-spacing: 6px;
        animation: text-flicker 2s infinite;
    }}
    @keyframes text-flicker {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.8; }}
    }}

    /* สโลแกนแสงนีออนวิ้งๆ วิ่งสลับสี */
    .neon-slogan {{
        text-align: center; 
        color: #fff; 
        font-size: 13px; 
        font-family: "Orbitron", sans-serif; 
        letter-spacing: 4px;
        margin-top: 20px;
        text-shadow: 0 0 5px #ff00de, 0 0 10px #ff00de, 0 0 20px #00f3ff;
        animation: slogan-wink 1s infinite alternate;
    }}

    @keyframes slogan-wink {{
        0%, 100% {{ text-shadow: 0 0 5px #ff00de, 0 0 10px #ff00de, 0 0 20px #ff00de; color: #fff; }}
        50% {{ text-shadow: 0 0 8px #00f3ff, 0 0 15px #00f3ff, 0 0 25px #00f3ff; color: #e0ffff; }}
        82% {{ text-shadow: none; color: #555; }}
        85% {{ text-shadow: 0 0 8px #00f3ff; color: #fff; }}
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="neon-title">อยู่นิ้งๆไม่เจ็บตัว</h1>', unsafe_allow_html=True)

# ==========================================
# ส่วนที่ 2: HTML/JS - ระบบเล่นวิดีโอพร้อมโลโก้ในกรอบ
# ==========================================

html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background: transparent; color: white; overflow: hidden; font-family: 'Inter', sans-serif; }}
        .neon-card {{ border: 2px solid #333; background: rgba(0,0,0,0.9); box-shadow: 0 0 30px rgba(255,0,222,0.2); }}
        
        /* กรอบหน้าจอ Video Player */
        .video-container {{
            position: relative;
            width: 100%;
            height: 220px;
            background: #050505;
            border-radius: 15px;
            border: 2px solid #222;
            overflow: hidden;
        }}
        .video-box {{ 
            width: 100%; 
            height: 100%; 
            object-fit: contain;
        }}
        .video-active {{ border-color: #00f3ff; box-shadow: 0 0 15px rgba(0,243,255,0.3); }}
        
        /* โลโก้ในกรอบเครื่องเล่น (ขวาบน) พร้อมแสง Neon หมุนสลับสี */
        .player-logo {{
            position: absolute;
            top: 12px;
            right: 12px;
            width: 45px;
            height: 45px;
            background-image: url("{logo_html_link}");
            background-size: contain;
            background-repeat: no-repeat;
            z-index: 10;
            pointer-events: none; /* เพื่อไม่ให้บังการกดปุ่มของวิดีโอ */
            filter: drop-shadow(0 0 6px #ff00de);
            animation: logo-glow 4s infinite alternate;
            opacity: 0.85; /* ให้มีความโปร่งแสงเนียนไปกับตัววิดีโอ */
        }}

        @keyframes logo-glow {{
            0% {{ filter: drop-shadow(0 0 6px #ff00de); transform: scale(1); }}
            50% {{ filter: drop-shadow(0 0 14px #00f3ff); transform: scale(1.05); }}
            100% {{ filter: drop-shadow(0 0 6px #ff8c00); transform: scale(1); }}
        }}
        
        .deck {{ padding: 15px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); background: rgba(255,255,255,0.02); }}
        
        .btn-main {{ 
            background: linear-gradient(45deg, #ff00de, #00f3ff);
            color: white; font-weight: bold; padding: 12px; border-radius: 10px;
            text-transform: uppercase; letter-spacing: 2px; transition: 0.3s;
            box-shadow: 0 0 15px rgba(255,0,222,0.4);
