import streamlit as st
import os
import random
import base64

# --- 1. SET UP & THEME ---
st.set_page_config(page_title="SYNAPSE COMMAND CENTER V2", layout="wide")

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#39FF14" # เขียวนีออนเริ่มต้น
if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#000000"

# --- Sidebar ปรับแต่งสี ---
with st.sidebar:
    if os.path.exists("logo1.png"):
        st.image("logo1.png", use_container_width=True)
    st.markdown("### 🎨 System Tuning")
    st.session_state.theme_color = st.color_picker("Neon Color", st.session_state.theme_color)
    st.write("---")
    st.markdown('**สโลแกน:** \n*"อยู่นิ่งๆ ไม่เจ็บตัว"*')

# --- 2. ฟังก์ชันแปลงรูปเป็น Base64 สำหรับ CSS ---
def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

logo_b64 = get_base64("logo1.png")

# --- 3. CSS DYNAMIC THEME ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background-color: {st.session_state.bg_color} !important; }}

    /* Logo ตรงกลางแบบมี Animation */
    .block-container::before {{
        content: "";
        position: absolute;
        top: 10px; left: 50%;
        transform: translateX(-50%);
        width: 80px; height: 80px;
        background-image: url("data:image/png;base64,{logo_b64}");
        background-size: contain; background-repeat: no-repeat;
        z-index: 999;
        filter: drop-shadow(0 0 10px {st.session_state.theme_color});
        animation: pulse 2s infinite alternate;
    }}
    @keyframes pulse {{
        from {{ transform: translateX(-50%) scale(1); opacity: 0.8; }}
        to {{ transform: translateX(-50%) scale(1.1); opacity: 1; }}
    }}

    .neon-title {{
        font-family: 'Orbitron', sans-serif;
        color: #fff; text-align: center;
        text-shadow: 0 0 15px {st.session_state.theme_color};
        font-size: 2rem; margin-top: 80px;
    }}
    </style>
    <h1 class="neon-title">SYNAPSE COMMAND CENTER</h1>
    """, unsafe_allow_html=True)

# --- 4. ระบบจัดการไฟล์เพลง ---
music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

if music_files:
    if 'song_index' not in st.session_state:
        st.session_state.song_index = 0
    
    current_song = music_files[st.session_state.song_index]
    
    # ส่วนแสดงชื่อเพลงวิ่ง
    st.markdown(f"""
        <div style="overflow:hidden; white-space:nowrap; background:rgba(0,0,0,0.5); border:1px solid {st.session_state.theme_color}; border-radius:10px; padding:10px;">
            <p style="display:inline-block; padding-left:100%; animation: marquee 15s linear infinite; color:{st.session_state.theme_color}; font-family:'Orbitron';">
                NOW PLAYING: {current_song} •--• NEXT TRACK UP SOON 
            </p>
        </div>
        <style>@keyframes marquee {{ 0% {{transform: translate(0,0);}} 100% {{transform: translate(-100%,0);}} }}</style>
    """, unsafe_allow_html=True)

    # กะขนาดคอลัมน์ [ซ้าย: ปก/วิดีโอ , ขวา: คลังเพลง]
    col_main, col_list = st.columns([2, 1])

    with col_main:
        # ดึงไฟล์วิดีโอหรือรูปที่ชื่อตรงกับเพลงมาโชว์
        base_name = os.path.splitext(current_song)[0]
        if os.path.exists(base_name + ".mp4"):
            st.video(base_name + ".mp4", loop=True, autoplay=True, muted=True)
        elif os.path.exists(base_name + ".jpg"):
            st.image(base_name + ".jpg", use_container_width=True)
        else:
            st.info("💡 Tip: ตั้งชื่อรูป .jpg ให้เหมือนชื่อเพลง .mp3 เพื่อโชว์ปกแบบอัตโนมัติ")

    with col_list:
        st.markdown(f"<h3 style='font-size:14px; color:{st.session_state.theme_color}'>🎧 PLAYLIST</h3>", unsafe_allow_html=True)
        with st.container(height=300):
            for i, song in enumerate(music_files):
                btn_label = f"▶️ {song}" if i == st.session_state.song_index else f"▪️ {song}"
                if st.button(btn_label, key=f"s_{i}"):
                    st.session_state.song_index = i
                    st.rerun()

    # --- 5. หัวใจหลัก: Mixer & Visualizer Engine ---
    # เราจะส่งชื่อไฟล์เพลงปัจจุบันเข้าไปใน JavaScript เพื่อเล่น
    html_mixer = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .vis-box {{ height: 120px; background: #000; border: 1px solid {st.session_state.theme_color}; border-radius: 15px; }}
        </style>
    </head>
    <body>
        <canvas id="canvas" class="vis-box" style="width:100%"></canvas>
        <script>
            let audioCtx, analyser, source, dataArray;
            let songUrl = "./{current_song}";

            async function startAudio() {{
                if(!audioCtx) {{
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    analyser = audioCtx.createAnalyser();
                    analyser.fftSize = 64;
                    dataArray = new Uint8Array(analyser.frequencyBinCount);
                    
                    const res = await fetch(songUrl);
                    const buffer = await audioCtx.decodeAudioData(await res.arrayBuffer());
                    
                    source = audioCtx.createBufferSource();
                    source.buffer = buffer;
                    
                    // ระบบ Fade In (10 วินาทีตามที่อาจารย์ชอบ)
                    let gain = audioCtx.createGain();
                    gain.gain.setValueAtTime(0, audioCtx.currentTime);
                    gain.gain.linearRampToValueAtTime(1, audioCtx.currentTime + 10);
                    
                    source.connect(gain).connect(analyser).connect(audioCtx.destination);
                    source.start(0);
                    
                    source.onended = () => {{ window.parent.document.querySelector('button[title="⏭️ เพลงถัดไป"]').click(); }};
                    draw();
                }}
            }}

            function draw() {{
                requestAnimationFrame(draw);
                analyser.getByteFrequencyData(dataArray);
                const canvas = document.getElementById('canvas');
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = '#000';
                ctx.fillRect(0,0,canvas.width, canvas.height);
                const bWidth = (canvas.width / dataArray.length) * 2;
                for(let i=0; i<dataArray.length; i++) {{
                    let h = (dataArray[i]/255) * canvas.height;
                    ctx.fillStyle = '{st.session_state.theme_color}';
                    ctx.shadowBlur = 10; ctx.shadowColor = '{st.session_state.theme_color}';
                    ctx.fillRect(i*bWidth, canvas.height-h, bWidth-2, h);
                }}
            }}
            // เริ่มอัตโนมัติเมื่อ User คลิกที่ไหนก็ได้ในหน้าจอ
            window.onclick = () => {{ startAudio(); }};
        </script>
    </body>
    </html>
    """
    st.components.v1.html(html_mixer, height=150)

    # ปุ่มควบคุมเสริมด้านล่าง
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⏭️ เพลงถัดไป"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()
    with c2:
        if st.button("🎲 สุ่มเพลง"):
            st.session_state.song_index = random.randint(0, len(music_files) - 1)
            st.rerun()
    with c3:
        st.markdown(f"<p style='font-size:10px; text-align:right;'>อยู่นิ่งๆ ไม่เจ็บตัว CORE V2</p>", unsafe_allow_html=True)

else:
    st.error("ไม่พบไฟล์เพลง .mp3 ครับอาจารย์")
