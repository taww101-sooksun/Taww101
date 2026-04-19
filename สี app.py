import streamlit as st
import base64
import os

# --- CONFIG & HIDE UI ---
st.set_page_config(page_title="SYNAPSE X COMMAND CENTER", layout="wide")

# ระบบเลือกธีมสี
if 'bg_mode' not in st.session_state:
    st.session_state.bg_mode = "rainbow"

def set_bg(mode): st.session_state.bg_mode = mode

# กำหนดค่าสีตามโหมด
if st.session_state.bg_mode == "rainbow":
    current_style = "background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff); background-size: 1200% 1200%; animation: RainbowFlow 10s ease infinite;"
    theme_color = "#00FFFF"
elif st.session_state.bg_mode == "coral":
    current_style = "background-color: #FF7F50;"
    theme_color = "#FF7F50"
else:
    current_style = "background-color: #000000;"
    theme_color = "#AFEEEE"

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_base64 = get_base64_image("logo1.png")
logo_url = f"data:image/png;base64,{logo_base64}"

# --- CSS FULL PACK (วิ้ง+Glow+Rainbow) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    header, footer, #MainMenu {{visibility: hidden;}}
    
    @keyframes RainbowFlow {{ 0%{{background-position:0% 50%}} 50%{{background-position:100% 50%}} 100%{{background-position:0% 50%}} }}
    .stApp {{ {current_style} transition: all 0.5s ease; }}
    
    /* โลโก้ดิ้นและเรืองแสง */
    .logo-container {{ display: flex; justify-content: center; margin-bottom: 20px; }}
    .logo-img {{ 
        width: 400px; 
        filter: drop-shadow(0 0 20px {theme_color});
        animation: logoPulse 4s ease-in-out infinite; 
    }}
    @keyframes logoPulse {{ 
        0%, 100% {{ filter: drop-shadow(0 0 15px {theme_color}); transform: scale(1); }} 
        50% {{ filter: drop-shadow(0 0 50px {theme_color}); transform: scale(1.03); }} 
    }}

    /* ตัวหนังสือวิ้งๆ Cinematic */
    .shimmer-text {{
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        font-weight: bold;
        font-size: 2.5rem;
        background: linear-gradient(90deg, rgba(255,255,255,0.1), #fff, rgba(255,255,255,0.1));
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 3s linear infinite;
        margin-bottom: 10px;
   }
    @keyframes shine {{ to {{ background-position: 200% center; }} }}

    /* ปรับแต่ง Dropdown */
    .stSelectbox {{ color: white !important; }}
    
    /* เครื่องเล่นเพลงสีรุ้ง */
    .stAudio {{
        background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
        background-size: 1200% 1200%;
        animation: RainbowFlow 15s ease infinite;
        border-radius: 50px;
        padding: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DISPLAY ---
# 1. โลโก้
st.markdown(f'<div class="logo-container"><img src="{logo_url}" class="logo-img"></div>', unsafe_allow_html=True)

# 2. ตัวหนังสือวิ้ง
st.markdown('<div class="shimmer-text">SYNAPSE X COMMAND CENTER</div>', unsafe_allow_html=True)

# 3. เลือกเพลง
audio_files = [f for f in os.listdir('.') if f.endswith(('.mp3', '.wav'))]
selected_track = st.selectbox("เลือกเพลงที่จะเล่น", audio_files if audio_files else ["ไม่มีไฟล์เพลงในโฟลเดอร์"])

# 4. กราฟเสียงแบบจัดเต็ม (Visualizer 60 แท่ง)
if audio_files:
    # อ่านไฟล์เพลงเพื่อส่งเข้า JS
    with open(selected_track, "rb") as f:
        audio_data = base64.b64encode(f.read()).decode()

    visualizer_html = f"""
    <div style="display: flex; justify-content: center; align-items: flex-end; height: 100px; gap: 2px; margin-bottom: 20px;">
        <canvas id="vis" width="800" height="100" style="width: 100%; max-width: 600px;"></canvas>
    </div>
    <script>
    const can = document.getElementById('vis');
    const ctx = can.getContext('2d');
    const barCount = 60;
    
    function draw() {{
        ctx.clearRect(0, 0, can.width, can.height);
        for (let i = 0; i < barCount; i++) {{
            const h = Math.random() * 80 + 10; // จำลองความสูง (ตัวจริงจะเต้นตามเบส)
            let grad = ctx.createLinearGradient(0, can.height, 0, 0);
            grad.addColorStop(0, '{theme_color}');
            grad.addColorStop(1, '#FFFFFF');
            ctx.fillStyle = grad;
            
            // วาดแท่งหัวมน
            const x = i * (can.width / barCount);
            const w = (can.width / barCount) - 2;
            ctx.beginPath();
            ctx.roundRect(x, can.height - h, w, h, 5);
            ctx.fill();
        }}
        setTimeout(() => requestAnimationFrame(draw), 100);
    }}
    draw();
    </script>
    """
    st.components.v1.html(visualizer_html, height=120)

    # 5. ตัวเครื่องเล่นสีรุ้ง
    st.audio(open(selected_track, 'rb').read(), format='audio/mp3')

# 6. ปุ่มเปลี่ยนธีม
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1: st.button("💎 Turquoise", on_click=set_bg, args=("turquoise",), use_container_width=True)
with col2: st.button("🧡 Coral", on_click=set_bg, args=("coral",), use_container_width=True)
with col3: st.button("🌈 Rainbow", on_click=set_bg, args=("rainbow",), use_container_width=True)

# 7. คำแนะนำ
with st.expander("คำแนะนำการบันทึกหน้าจอเพื่อลง YouTube"):
    st.write("- เปิด Full Screen (F11)")
    # Render 180°C or 10% example in thought, but here is for video settings
    st.write("- ใช้ OBS ตั้งค่า Bitrate 15,000 kbps เพื่อให้สีรุ้งเนียนกริบ")
