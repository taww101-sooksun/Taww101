import streamlit as st
import base64
import os

st.set_page_config(page_title="SYNAPSE REAL-TIME", layout="wide")

# --- CSS & THEME ---
theme_color = "#00FFFF" # สีหลักของ SYNAPSE
st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background-color: #000; }}
    .shimmer-text {{
        text-align: center; font-family: 'Orbitron', sans-serif; font-weight: bold;
        font-size: 2rem; color: {theme_color}; text-shadow: 0 0 20px {theme_color};
    }}
    </style>
""", unsafe_allow_html=True)

# --- MUSIC LOGIC ---
audio_files = [f for f in os.listdir('.') if f.endswith(('.mp3', '.wav'))]
selected_track = st.selectbox("เลือกเพลงเพื่อประมวลผลจริง", audio_files)

if selected_track:
    # แปลงไฟล์เป็น Base64 เพื่อส่งเข้า JavaScript
    with open(selected_track, "rb") as f:
        audio_base64 = base64.b64encode(f.read()).decode()

    # --- JAVASCRIPT: THE ENGINE ---
    # ส่วนนี้คือของจริงครับ มันจะสร้าง AudioContext เพื่อดึงคลื่นเสียงมาวาดกราฟ
    visual_code = f"""
    <div style="text-align: center;">
        <canvas id="canvas" width="800" height="250" style="width: 100%; border-bottom: 2px solid {theme_color};"></canvas>
        <br><br>
        <audio id="audioPlayer" controls style="width: 80%; filter: hue-rotate(180deg);"></audio>
    </div>

    <script>
    const audio = document.getElementById('audioPlayer');
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');

    // โหลดเพลงจาก Base64
    audio.src = "data:audio/mp3;base64,{audio_base64}";

    let audioCtx, analyser, source;

    // ต้องมีการคลิกก่อน Web Audio ถึงจะทำงาน (กฎของ Browser)
    audio.onplay = () => {{
        if (!audioCtx) {{
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioCtx.createAnalyser();
            source = audioCtx.createMediaElementSource(audio);
            source.connect(analyser);
            analyser.connect(audioCtx.destination);
            analyser.fftSize = 256; // ความละเอียดของกราฟ
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
            const barHeight = dataArray[i] / 1.5;
            
            // ไล่เฉดสีให้วิ้งๆ
            ctx.fillStyle = "rgb(" + (barHeight + 100) + ", 50, 255)";
            
            // วาดแท่งกราฟ (เต้นตามจริง!)
            ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
            x += barWidth + 1;
        }}
    }}
    </script>
    """
    st.markdown('<div class="shimmer-text">REAL-TIME FREQUENCY SCANNER</div>', unsafe_allow_html=True)
    st.components.v1.html(visual_code, height=400)
