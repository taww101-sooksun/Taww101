import streamlit as st
import os
import base64
import random

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="SYNAPSE COMMAND CENTER V.7", layout="centered")

def get_base64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except: return None
    return None

if 'song_index' not in st.session_state:
    st.session_state.song_index = 0

logo_b64 = get_base64("logo1.png")

# --- 2. ข้อมูลห้องและสีสัน ---
room_info = [
    {"name": "🔥 CORE ROOM", "color1": "#39FF14", "color2": "#00FFDD"},
    {"name": "🎧 R&B LOUNGE", "color1": "#FF00DE", "color2": "#7000FF"},
    {"name": "🎤 RAP ZONE", "color1": "#00F3FF", "color2": "#0051FF"},
    {"name": "🌌 QUANTUM", "color1": "#FF8C00", "color2": "#FF0000"},
    {"name": "🎸 ISAN INDIE", "color1": "#FFD700", "color2": "#FF5733"}
]

all_music = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

# --- 3. ฟังก์ชันหลักสำหรับเครื่องเล่นเพลง (เวอร์ชันแก้ทาง Auto-play) ---
def synapse_player(room_idx):
    info = room_info[room_idx]
    c1, c2 = info["color1"], info["color2"]
    
    if not all_music:
        st.warning("⚠️ ไม่พบไฟล์เพลง .mp3 ในคลัง")
        return

    st.session_state.song_index %= len(all_music)
    current_song = all_music[st.session_state.song_index]
    song_data = get_base64(current_song)

    if song_data:
        # ส่วนผสม JavaScript ที่ทำให้เล่นต่อเนื่องได้จริง
        html_code = f"""
        <div style="margin-top:10px;">
            <canvas id="canvas-{room_idx}" style="width:100%; height:110px; background:#000; border:1px solid {c1}44; border-radius:15px;"></canvas>
            <button id="btn-{room_idx}" style="width:100%; padding:15px; margin-top:10px; background:transparent; color:{c1}; border:2px solid {c1}; font-family:sans-serif; cursor:pointer; border-radius:10px; font-weight:bold; box-shadow: 0 0 15px {c1}33;">
                ACTIVATE {info["name"]} ⚡
            </button>
            <audio id="audio-{room_idx}" src="data:audio/mp3;base64,{song_data}"></audio>
            <p style="color:{c1}; text-align:center; font-size:12px; margin-top:8px; font-family:sans-serif;">
                NOW PLAYING: {current_song}
            </p>
        </div>
        <script>
            const audio = document.getElementById('audio-{room_idx}');
            const btn = document.getElementById('btn-{room_idx}');
            const canvas = document.getElementById('canvas-{room_idx}');
            const ctx = canvas.getContext('2d');
            let audioCtx, analyser, source, dataArray;

            // ฟังก์ชันเริ่มระบบเมื่อกดปุ่ม
            btn.onclick = function() {{
                if (!audioCtx) {{
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    analyser = audioCtx.createAnalyser();
                    source = audioCtx.createMediaElementSource(audio);
                    source.connect(analyser);
                    analyser.connect(audioCtx.destination);
                    analyser.fftSize = 256; 
                    dataArray = new Uint8Array(analyser.frequencyBinCount);
                    render();
                }}
                if (audio.paused) {{ 
                    audio.play(); 
                    btn.innerText = "SYSTEM ONLINE 🟢"; 
                    sessionStorage.setItem('synapse_autoplay', 'true'); // บันทึกว่าอนุญาตให้เล่นต่อเนื่อง
                }} else {{ 
                    audio.pause(); 
                    btn.innerText = "SYSTEM PAUSED 🔴"; 
                    sessionStorage.setItem('synapse_autoplay', 'false');
                }}
            }};

            // ระบบเช็คและเล่นอัตโนมัติเมื่อโหลดเพลงใหม่ (ถ้าเคยอนุญาตไว้)
            window.onload = function() {{
                if (sessionStorage.getItem('synapse_autoplay') === 'true') {{
                    setTimeout(() => {{
                        audio.play().then(() => {{
                            btn.innerText = "SYSTEM ONLINE 🟢";
                        }}).catch(e => console.log("Auto-play wait for click"));
                    }}, 800);
                }}
            }};

            function render() {{
                requestAnimationFrame(render);
                analyser.getByteFrequencyData(dataArray);
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                const bWidth = (canvas.width / dataArray.length) * 2;
                let x = 0;
                for (let i = 0; i < dataArray.length; i++) {{
                    let h = (dataArray[i] / 255) * canvas.height;
                    let grad = ctx.createLinearGradient(0, canvas.height, 0, canvas.height - h);
                    grad.addColorStop(0, "{c1}"); grad.addColorStop(1, "{c2}");
                    ctx.fillStyle = grad;
                    ctx.shadowBlur = 8; ctx.shadowColor = "{c1}";
                    ctx.fillRect(x, canvas.height - h, bWidth - 1, h);
                    x += bWidth;
                }}
            }}

            audio.onended = () => {{
                // ดีดไปเพลงถัดไปโดยกดปุ่ม NEXT ที่มี title="NEXT_TRIGGER"
                window.parent.document.querySelector('button[title="NEXT_TRIGGER"]').click();
            }};
        </script>
        """
        st.components.v1.html(html_code, height=260)

# --- 4. การแสดงผลหน้าจอหลัก ---
st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background-color: #000000 !important; }}
    .main-logo {{
        width: 80px; height: 80px; margin: 0 auto;
        background-image: url("data:image/png;base64,{logo_b64}");
        background-size: contain; background-repeat: no-repeat;
        filter: drop-shadow(0 0 15px #39FF14);
    }}
    </style>
    <div class="main-logo"></div>
""", unsafe_allow_html=True)

tabs = st.tabs([r["name"] for r in room_info])

for i, tab in enumerate(tabs):
    with tab:
        st.markdown(f"<h2 style='text-align:center; color:#fff; font-family:sans-serif;'>{room_info[i]['name']}</h2>", unsafe_allow_html=True)
        synapse_player(i)

# --- 5. ระบบควบคุมและรายชื่อเพลง ---
st.write("---")
st.markdown("<h3 style='color:#39FF14; text-align:center; font-family:sans-serif;'>🎵 GLOBAL PLAYLIST (52 TRACKS)</h3>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("⏮️ PREV"):
        st.session_state.song_index -= 1
        st.rerun()
with col2:
    if st.button("🎲 SHUFFLE"):
        st.session_state.song_index = random.randint(0, len(all_music)-1)
        st.rerun()
with col3:
    # ปุ่มสวรรค์ที่ JS จะมาช่วยกดให้
    if st.button("⏭️ NEXT", help="NEXT_TRIGGER"):
        st.session_state.song_index += 1
        st.rerun()

with st.expander("📂 เลือกเพลงจากคลังทั้งหมด", expanded=True):
    for idx, song in enumerate(all_music):
        is_current = (idx == st.session_state.song_index % len(all_music))
        label = f"🔥 {idx+1}. {song}" if is_current else f"🎼 {idx+1}. {song}"
        if st.button(label, key=f"btn_{idx}", use_container_width=True):
            st.session_state.song_index = idx
            st.rerun()

st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | SYNAPSE COMMAND CENTER V.7")
