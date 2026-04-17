import streamlit as st
import os
import base64
import random

# --- 1. CONFIG & SYSTEM ---
st.set_page_config(page_title="SYNAPSE COMMAND CENTER V.7.1", layout="centered")

def get_base64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except: return None
    return None

# ตรวจสอบตัวแปรระบบ
if 'global_song_idx' not in st.session_state:
    st.session_state.global_song_idx = 0
if 'current_room' not in st.session_state:
    st.session_state.current_room = "NONE" # เริ่มต้นยังไม่เข้าห้องไหน

logo_b64 = get_base64("logo1.png")

# --- 2. ข้อมูลห้องและสีสัน ---
room_info = {
    "CORE": {"name": "🔥 CORE ROOM", "color1": "#39FF14", "color2": "#00FFDD"},
    "RNB": {"name": "🎧 R&B LOUNGE", "color1": "#FF00DE", "color2": "#7000FF"},
    "RAP": {"name": "🎤 RAP ZONE", "color1": "#00F3FF", "color2": "#0051FF"},
    "QUANTUM": {"name": "🌌 QUANTUM", "color1": "#FF8C00", "color2": "#FF0000"},
    "ISAN": {"name": "🎸 ISAN INDIE", "color1": "#FFD700", "color2": "#FF5733"}
}

all_music = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

# --- 3. ฟังก์ชันเครื่องเล่นเพลง (ปรับปรุงใหม่) ---
def synapse_player(room_key):
    info = room_info[room_key]
    c1, c2 = info["color1"], info["color2"]
    
    if not all_music:
        st.warning("⚠️ ไม่พบไฟล์เพลง .mp3 ในคลัง")
        return

    st.session_state.global_song_idx %= len(all_music)
    current_song = all_music[st.session_state.global_song_idx]
    song_data = get_base64(current_song)

    if song_data:
        html_code = f"""
        <div style="margin-top:10px; font-family: sans-serif; background:#111; padding:15px; border-radius:20px; border:2px solid {c1};">
            <canvas id="canvas" style="width:100%; height:110px; background:#000; border-radius:10px;"></canvas>
            
            <div style="background:rgba(0,0,0,0.8); border:1px solid {c1}; border-radius:8px; margin-top:12px; overflow:hidden;">
                <marquee scrollamount="6" style="color:{c1}; font-size:18px; padding:8px; font-weight:bold;">
                    NOW PLAYING 🎵 {current_song} | {info['name']} | SYNAPSE OMNI-PLAY ⚡
                </marquee>
            </div>

            <button id="activate-btn" style="width:100%; padding:18px; margin-top:12px; background:transparent; color:{c1}; border:2px solid {c1}; cursor:pointer; border-radius:12px; font-weight:bold; text-transform:uppercase;">
                START SYSTEM ⚡
            </button>
            <audio id="main-audio" src="data:audio/mp3;base64,{song_data}"></audio>
        </div>

        <script>
            const audio = document.getElementById('main-audio');
            const btn = document.getElementById('activate-btn');
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');
            let audioCtx, analyser, source, dataArray;

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
                    sessionStorage.setItem('synapse_autoplay', 'true');
                }} else {{ 
                    audio.pause(); 
                    btn.innerText = "SYSTEM PAUSED 🔴"; 
                    sessionStorage.setItem('synapse_autoplay', 'false');
                }}
            }};

            window.onload = function() {{
                if (sessionStorage.getItem('synapse_autoplay') === 'true') {{
                    setTimeout(() => {{
                        audio.play().then(() => {{ btn.innerText = "SYSTEM ONLINE 🟢"; }})
                        .catch(e => console.log("Blocked"));
                    }}, 1000);
                }}
            }};

            function render() {{
                requestAnimationFrame(render);
                analyser.getByteFrequencyData(dataArray);
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                for (let i = 0; i < dataArray.length; i++) {{
                    let h = (dataArray[i] / 255) * canvas.height;
                    ctx.fillStyle = "{c1}";
                    ctx.fillRect(i * 3, canvas.height - h, 2, h);
                }}
            }}

            audio.onended = () => {{
                window.parent.document.querySelector('button[title="AUTO_NEXT_TRIGGER"]').click();
            }};
        </script>
        """
        st.components.v1.html(html_code, height=350)

# --- 4. หน้าจอหลักและการเลือกห้อง ---
st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background-color: #000000 !important; }}
    .main-logo {{ width: 80px; margin: 0 auto; filter: drop-shadow(0 0 10px #39FF14); }}
    </style>
    <div style="text-align:center;"><img src="data:image/png;base64,{logo_b64}" class="main-logo"></div>
""", unsafe_allow_html=True)

# สร้างปุ่มเลือกห้องแบบเท่ๆ
st.markdown("<h2 style='text-align:center; color:#fff;'>SELECT ROOM</h2>", unsafe_allow_html=True)
c1, c2, c3, c4, c5 = st.columns(5)
with c1: 
    if st.button("CORE"): st.session_state.current_room = "CORE"
with c2: 
    if st.button("R&B"): st.session_state.current_room = "RNB"
with c3: 
    if st.button("RAP"): st.session_state.current_room = "RAP"
with c4: 
    if st.button("QTUM"): st.session_state.current_room = "QUANTUM"
with c5: 
    if st.button("ISAN"): st.session_state.current_room = "ISAN"

# แสดงเฉพาะห้องที่เลือก
if st.session_state.current_room != "NONE":
    room_key = st.session_state.current_room
    st.markdown(f"<h3 style='text-align:center; color:{room_info[room_key]['color1']};'>{room_info[room_key]['name']}</h3>", unsafe_allow_html=True)
    synapse_player(room_key)
    if st.button("❌ LEAVE ROOM"):
        st.session_state.current_room = "NONE"
        st.rerun()

# --- 5. ระบบควบคุมส่วนกลาง ---
if st.button("AUTO_NEXT", key="AUTO_NEXT", help="AUTO_NEXT_TRIGGER"):
    st.session_state.global_song_idx += 1
    st.rerun()

st.write("---")
with st.expander("📂 GLOBAL TRACKLIST (52)"):
    for idx, song in enumerate(all_music):
        if st.button(f"🎼 {idx+1}. {song}", key=f"track_{idx}", use_container_width=True):
            st.session_state.global_song_idx = idx
            st.rerun()

st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | SYNAPSE V.7.1")
