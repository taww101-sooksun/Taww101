import streamlit as st
import base64
import os

# ==========================================
# 1. การตั้งค่าหน้าจอและ Logic ระบบสี
# ==========================================
st.set_page_config(page_title="Synapse Studio Mixer", layout="centered")

# สร้าง Session State สำหรับเก็บโหมดสี
if 'bg_mode' not in st.session_state:
    st.session_state.bg_mode = "turquoise"

# ฟังก์ชันเปลี่ยนโหมดสี
def set_bg(mode):
    st.session_state.bg_mode = mode

# ==========================================
# 2. CSS & Animations (รวม Rainbow Flow ที่คุณให้มา)
# ==========================================
rainbow_css = ""
current_style = ""

if st.session_state.bg_mode == "rainbow":
    current_style = """
        background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
        background-size: 1200% 1200%;
        animation: RainbowFlow 10s ease infinite;
    """
    theme_color = "#FFFFFF" # สีขาวเพื่อให้ตัดกับรุ้ง
elif st.session_state.bg_mode == "coral":
    current_style = "background-color: #FF7F50;"
    theme_color = "#FF7F50"
else:
    current_style = "background-color: #000000; border: 1px solid #AFEEEE;"
    theme_color = "#AFEEEE"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    header, footer, #MainMenu {{visibility: hidden;}}
    
    /* ตัวคุมการวิ่งของสี (Keyframes) ที่คุณส่งมา */
    @keyframes RainbowFlow {{
        0%{{background-position:0% 50%}}
        50%{{background-position:100% 50%}}
        100%{{background-position:0% 50%}}
    }}

    .stApp {{
        {current_style}
        transition: all 0.5s ease;
    }}

    /* จัดสมดุล Header */
    .header-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        padding-top: 40px;
        margin-bottom: 30px;
    }}

    .logo-img {{
        width: 110px;
        margin-bottom: 25px; /* เว้นระยะไม่ให้บังตัวหนังสือ */
        filter: drop-shadow(0 0 10px {theme_color});
    }}

    .neon-title {{
        font-family: 'Orbitron', sans-serif;
        color: #fff;
        text-shadow: 0 0 15px {theme_color};
        font-size: 1.8rem;
        letter-spacing: 5px;
        margin: 0;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. ส่วนหัวและปุ่มเปลี่ยนสี (UI)
# ==========================================
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_base64 = get_base64_image("logo1.png")
logo_url = f"data:image/png;base64,{logo_base64}" if logo_base64 else ""

st.markdown(f"""
    <div class="header-container">
        <img src="{logo_url}" class="logo-img">
        <h1 class="neon-title">SYNAPSE STUDIO</h1>
        <p style="color:#fff; font-size:12px; margin-top:10px; opacity:0.8;">อยู่นิ่งๆ ไม่เจ็บตัว</p>
    </div>
    """, unsafe_allow_html=True)

# ปุ่มกดเปลี่ยนสี
col_btn1, col_btn2, col_btn3 = st.columns(3)
with col_btn1:
    st.button("💎 Turquoise", on_click=set_bg, args=("turquoise",), use_container_width=True)
with col_btn2:
    st.button("🧡 Coral", on_click=set_bg, args=("coral",), use_container_width=True)
with col_btn3:
    st.button("🌈 Rainbow", on_click=set_bg, args=("rainbow",), use_container_width=True)

# ==========================================
# 4. ระบบดึงเพลงจากโฟลเดอร์เดียวกัน
# ==========================================
audio_files = [f for f in os.listdir('.') if f.endswith(('.mp3', '.wav', '.ogg'))]

col_a, col_b = st.columns(2)
with col_a:
    track_a = st.selectbox("DECK A", audio_files if audio_files else ["No file"])
with col_b:
    track_b = st.selectbox("DECK B", audio_files if audio_files else ["No file"])

def to_base64(file):
    try:
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

data_a = to_base64(track_a) if track_a in audio_files else ""
data_b = to_base64(track_b) if track_b in audio_files else ""

# ==========================================
# 5. HTML Mixer (ปรับตามสีที่เลือก)
# ==========================================
html_mixer = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .mixer-bg {{ background: rgba(0,0,0,0.85); border: 2px solid {theme_color}; border-radius: 20px; padding: 20px; }}
        .btn-mix {{ border: 1px solid {theme_color}; color: {theme_color}; width: 100%; padding: 10px; border-radius: 10px; font-weight: bold; font-size: 12px; }}
        .btn-mix:hover {{ background: {theme_color}; color: #000; }}
        .vis {{ height: 80px; background: #000; border-radius: 8px; margin-bottom: 15px; border: 1px solid #333; }}
    </style>
</head>
<body class="bg-transparent text-white">
    <div class="mixer-bg">
        <canvas id="canvas" class="vis w-full"></canvas>
        <div class="grid grid-cols-2 gap-4 mb-4">
            <button onclick="play()" class="btn-mix">LOAD & START</button>
            <button onclick="fade()" class="btn-mix">CROSSFADE</button>
        </div>
        <div class="text-[10px] text-center opacity-50">SYNAPSE COMMAND CENTER ACTIVE</div>
    </div>

    <script>
        let ctx, ana, sA, sB, gA, gB, isP=false, cur='A';
        async function play() {{
            if(!ctx) {{ ctx = new AudioContext(); ana = ctx.createAnalyser(); draw(); }}
            if(isP) return;
            const dec = async (b) => ctx.decodeAudioData(Uint8Array.from(atob(b), c => c.charCodeAt(0)).buffer);
            sA = ctx.createBufferSource(); sA.buffer = await dec("{data_a}");
            gA = ctx.createGain(); sA.connect(gA).connect(ana).connect(ctx.destination);
            sB = ctx.createBufferSource(); sB.buffer = await dec("{data_b}");
            gB = ctx.createGain(); gB.gain.value = 0; sB.connect(gB).connect(ana).connect(ctx.destination);
            sA.start(0); sB.start(0); isP = true;
        }}
        function fade() {{
            const n = ctx.currentTime;
            if(cur==='A') {{ gA.gain.linearRampToValueAtTime(0,n+3); gB.gain.linearRampToValueAtTime(1,n+3); cur='B'; }}
            else {{ gB.gain.linearRampToValueAtTime(0,n+3); gA.gain.linearRampToValueAtTime(1,n+3); cur='A'; }}
        }}
        function draw() {{
            requestAnimationFrame(draw);
            const can = document.getElementById('canvas'), c = can.getContext('2d');
            const f = new Uint8Array(ana.frequencyBinCount); ana.getByteFrequencyData(f);
            c.clearRect(0,0,can.width,can.height);
            f.forEach((v, i) => {{ c.fillStyle='{theme_color}'; c.fillRect(i*3, can.height-v/3, 2, v/3); }});
        }}
    </script>
</body>
</html>
"""

st.components.v1.html(html_mixer, height=250)
