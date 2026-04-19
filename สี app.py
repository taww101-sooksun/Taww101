import streamlit as st
import os
import base64

# --- CONFIG & UI HIDING ---
st.set_page_config(page_title="SYNAPSE X REAL-TIME", layout="wide")

def get_base64_bin(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

# ซ่อน Streamlit UI เดิมๆ เพื่อความคลีน
hide_ui = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {padding-top: 2rem; background-color: #000000;}
    
    /* Animation โลโก้ดิ้นได้ */
    @keyframes bounce {
        0%, 100% { transform: translateY(0); filter: drop-shadow(0 0 10px #00ffff); }
        50% { transform: translateY(-15px); filter: drop-shadow(0 0 30px #00ffff); }
    }
    .logo-container {
        display: flex;
        justify-content: center;
        animation: bounce 3s ease-in-out infinite;
        margin-bottom: 20px;
    }

    /* ตัวหนังสือวิ้งๆ */
    .shimmer-text {
        text-align: center;
        font-weight: bold;
        font-size: 2.5rem;
        font-family: 'Orbitron', sans-serif;
        background: linear-gradient(90deg, #AFEEEE, #FFFFFF, #FF7F50);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 2s linear infinite;
        margin-top: 10px;
    }
    @keyframes shine {
        to { background-position: 100% center; }
    }
    </style>
"""
st.markdown(hide_ui, unsafe_allow_html=True)

# --- LOGIC: ดึงไฟล์เพลง ---
song_files = [f for f in os.listdir('.') if f.endswith(('.mp3', '.wav'))]

# --- UI DISPLAY ---
# 1. โลโก้ดิ้นได้ (150px ตามสั่ง)
logo_data = get_base64_bin("logo1.png")
if logo_data:
    st.markdown(f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_data}" width="150">
        </div>
    """, unsafe_allow_html=True)

# 2. ตัวหนังสือวิ้ง
st.markdown('<div class="shimmer-text">SYNAPSE อยู่นิ้งๆไม่เจ็บตัว</div>', unsafe_allow_html=True)

# 3. ส่วนเลือกเพลงและระบบประมวลผลจริง
if song_files:
    selected_song = st.selectbox("เลือกเพลงที่จะเล่น (ประมวลผลกราฟจริง)", song_files)
    
    # อ่านไฟล์เพลงเพื่อส่งเข้า JavaScript
    with open(selected_song, "rb") as f:
        audio_base64 = base64.b64encode(f.read()).decode()

    # --- HTML & JS: REAL-TIME VISUALIZER ENGINE ---
    # ส่วนนี้จะใช้ Web Audio API เพื่อดึงค่าความถี่จริงจากเพลง
    visual_code = f"""
    <div style="text-align: center;">
        <canvas id="canvas" width="1000" height="300" style="width: 100%; max-width: 800px;"></canvas>
        <br>
        <audio id="audioPlayer" controls style="width: 100%; border-radius: 100px; background: #fff;"></audio>
    </div>

    <script>
    const audio = document.getElementById('audioPlayer');
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');

    audio.src = "data:audio/mp3;base64,{audio_base64}";

    let audioCtx, analyser, source;

    audio.onplay = () => {{
        if (!audioCtx) {{
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioCtx.createAnalyser();
            source = audioCtx.createMediaElementSource(audio);
            source.connect(analyser);
            analyser.connect(audioCtx.destination);
            analyser.fftSize = 1024; 
            draw();
        }}
    }};

    function draw() {{
        requestAnimationFrame(draw);
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        analyser.getByteFrequencyData(dataArray);

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        const barWidth = (canvas.width / bufferLength) * 2.5;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {{
            const barHeight = dataArray[i] * 0.8;
            
            // ไล่เฉดสีรุ้ง (Rainbow Bar)
            const hue = i * 360 / bufferLength;
            ctx.fillStyle = `hsl(${{hue}}, 100%, 50%)`;
            
            // วาดแท่งกราฟ (เต้นตามจังหวะจริง!)
            ctx.fillRect(x, canvas.height - barHeight, barWidth - 1, barHeight);
            x += barWidth;
        }}
    }}
    </script>
    """
    st.components.v1.html(visual_code, height=500)
else:
    st.info("ไม่พบไฟล์ .mp3 ในโฟลเดอร์นี้")

# --- ข้อแนะนำการบันทึกวิดีโอลง YouTube ---
st.markdown("---")
with st.expander("🎥 คำแนะนำการบันทึกหน้าจอเพื่อลง YouTube"):
    st.write("""
    1. **กดปุ่ม Play:** กราฟจะยังไม่เต้นจนกว่าจะกดเล่นเพลง (กฎของ Browser)
    2. **OBS Studio:** ใช้ Window Capture และตั้งค่า Bitrate 15,000-20,000 kbps เพื่อให้สีรุ้งเนียนกริบ
    3. **Full Screen:** กด F11 ใน Browser ก่อนเริ่มบันทึกเพื่อให้ภาพเต็มตาที่สุด
    """)
