import streamlit as st
import os

# ตั้งค่าหน้าจอให้กว้างที่สุดและซ่อนเมนู Streamlit ทั้งหมด
st.set_page_config(page_title="SYNAPSE", layout="wide")

# 1. ลบ Logo/Menu ของ Streamlit และใส่ CSS สำหรับ UI ทั้งหมด (ปรับปรุงใหม่)
st.markdown("""
    <style>
    /* ลบส่วนเกินของ Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding: 0px;}

    /* พื้นหลังและธีมหลัก */
    body {
        background-color: var(--bg-color, #000);
        color: var(--text-color, #fff);
        font-family: 'Arial', sans-serif;
        overflow-x: hidden;
    }

    /* โครงสร้างส่วนบน (Slogan + Logo) แบบบาลานซ์ */
    .top-section {
        display: flex;
        justify-content: space-around; /* จัดวางให้กระจายตัวบาลานซ์ */
        align-items: center;
        padding: 40px 10px;
        text-align: center;
    }

    .slogan {
        font-size: 20px;
        font-weight: bold;
        text-shadow: 2px 2px 10px var(--neon-color, #ff00ea);
        width: 150px; /* กำหนดความกว้างคงที่ */
    }

    .logo-placeholder {
        width: 200px;
        height: 200px;
        border-radius: 50%;
        border: 2px solid var(--neon-color, #ff00ea);
        background-color: var(--card-bg, rgba(0,0,0,0.8));
        box-shadow: 0 0 15px var(--neon-color, #ff00ea);
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 24px;
        font-weight: bold;
        overflow: hidden;
    }

    .logo-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    /* ตัวหนังสือวิ่ง */
    .marquee-container {
        background: rgba(255,255,255,0.1);
        padding: 10px 0;
        margin-bottom: 30px;
    }

    /* เครื่องเล่นเพลงคู่ A-B (ปรับปรุง Layout ใหม่) */
    .dual-player {
        display: flex;
        justify-content: center;
        gap: 20px;
        padding: 20px;
        flex-wrap: wrap; /* ให้เครื่องเล่นแสดงผลต่อกันบนมือถือ */
    }

    .player-box {
        border: 2px solid var(--neon-color, #ff00ea);
        border-radius: 20px;
        padding: 20px;
        width: 350px;
        background: var(--card-bg, rgba(0,0,0,0.8));
        box-shadow: 0 0 20px var(--neon-color, #ff00ea);
        text-align: center;
    }

    .btn-neon {
        background: transparent;
        border: 1px solid var(--neon-color, #ff00ea);
        color: var(--neon-color, #ff00ea);
        padding: 10px 20px;
        margin: 5px;
        border-radius: 10px;
        cursor: pointer;
        transition: 0.3s;
    }

    .btn-neon:hover {
        background: var(--neon-color, #ff00ea);
        color: white;
    }

    /* ตัวหนังสือใหญ่เล็กผสมกัน */
    .special-text {
        font-size: 18px;
    }
    .large-text {
        font-size: 24px;
        font-weight: bold;
        color: var(--neon-color, #ff00ea);
    }
    </style>
""", unsafe_allow_html=True)

# 2. จัดเตรียมไฟล์เพลง (ดึงไฟล์ .mp3 จากหน้าเดียวกับ .py)
# ข้อความพิเศษ (ใหญ่เล็กผสมกัน)
special_text = '<p class="special-text">ยินดีต้อนรับสู่ <span class="large-text">SYNAPSE</span> ศูนย์บัญชาการ<br>อยู่นิ่งๆ ไม่เจ็บตัว</p>'
# ชื่อเพลงวิ่ง (ตัวอย่าง)
track_marquee = '🎧 กำลังเล่น: เพลงที่ 1 - Synthwave Paradise | <span class="large-text">SYNAPSE</span> อยู่นิ่งๆ ไม่เจ็บตัว | ...'

# HTML Structure & JavaScript
st.markdown(f"""
    <div class="top-section">
        <div class="slogan">SYNAPSE</div>
        <div class="logo-placeholder" id="logoCircle">
            <img src="app/static/logo1.png" class="logo-img" id="logoImg" onerror="this.src='https://via.placeholder.com/200?text=LOGO+1';">
        </div>
        <div class="slogan">อยู่นิ่งๆ<br>ไม่เจ็บตัว</div>
    </div>

    <canvas id="visualizer" style="width: 100%; height: 100px; background: transparent;"></canvas>

    <div class="marquee-container" style="text-align: center;">
        {special_text}
    </div>

    <div class="marquee-container">
        <marquee scrollamount="8" style="font-size: 16px;">
            {track_marquee}
        </marquee>
    </div>

    <div class="dual-player">
        <div class="player-box" id="boxA">
            <h3>Player A</h3>
            <div id="timeA">00:00</div>
            <button class="btn-neon" onclick="playMusic('A')">PLAY</button>
            <input type="range" min="0" max="1" step="0.1" value="0.5" onchange="setVol('A', this.value)"> Vol
        </div>
        <div class="player-box" id="boxB">
            <h3>Player B</h3>
            <div id="timeB">00:00</div>
            <button class="btn-neon" onclick="playMusic('B')">PLAY</button>
            <input type="range" min="0" max="1" step="0.1" value="0.5" onchange="setVol('B', this.value)"> Vol
        </div>
    </div>

    <script>
    // *ส่วนนี้จะเป็นโค้ด JavaScript เต็มรูปแบบที่จะจัดการ Visualizer และ Crossfade*
    // **ตัวอย่าง Logic เพื่อให้เห็นภาพ (จะใส่เต็มในไฟล์ py จริง)**
    // var audioA = new Audio('song1.mp3'); // ระบบต้องโหลดไฟล์เพลง
    // var canvas = document.getElementById('visualizer');
    // ... logic เพื่อดึงคลื่นเสียงมาวาด ...
    </script>
""", unsafe_allow_html=True)

# 4. สำหรับสโลแกนใน Streamlit sidebar (ถ้าอยากใช้เพิ่ม)
# st.sidebar.write("SYNAPSE Command")
