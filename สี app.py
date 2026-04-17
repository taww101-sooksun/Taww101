import streamlit as st
import os
import base64
import random

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="SYNAPSE COMMAND CENTER V.7", layout="wide")

def get_base64(file_path):
    if not os.path.isfile(file_path):
        return None
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return None

# Initialize Session State
if 'song_index' not in st.session_state:
    st.session_state.song_index = 0
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False

# --- 2. ข้อมูลห้องและไฟล์เพลง ---
room_info = [
    {"name": "🔥 CORE ROOM", "color1": "#39FF14", "color2": "#00FFDD"},
    {"name": "🎧 R&B LOUNGE", "color1": "#FF00DE", "color2": "#7000FF"},
    {"name": "🎤 RAP ZONE", "color1": "#00F3FF", "color2": "#0051FF"},
    {"name": "🌌 QUANTUM", "color1": "#FF8C00", "color2": "#FF0000"},
    {"name": "🎸 ISAN INDIE", "color1": "#FFD700", "color2": "#FF5733"}
]

# ดึงรายชื่อเพลง
all_music = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

# --- 3. ฟังก์ชันเครื่องเล่นเพลง (Auto-play & Visualizer) ---
def synapse_player(room_idx):
    info = room_info[room_idx]
    c1, c2 = info["color1"], info["color2"]
    
    if not all_music:
        st.warning("⚠️ ไม่พบไฟล์เพลง .mp3")
        return

    current_idx = st.session_state.song_index % len(all_music)
    current_song = all_music[current_idx]
    song_data = get_base64(current_song)

    if song_data:
        html_code = f"""
        <div style="margin-top:10px; font-family: 'Courier New', monospace;">
            <canvas id="canvas-{room_idx}" style="width:100%; height:120px; background:#000; border:1px solid {c1}44; border-radius:10px;"></canvas>
            
            <div style="display: flex; gap: 10px; margin-top: 10px;">
                <button id="btn-play-{room_idx}" style="flex: 2; padding: 15px; background: transparent; color: {c1}; border: 2px solid {c1}; cursor: pointer; border-radius: 8px; font-weight: bold; text-transform: uppercase;">
                    INITIALIZE {info["name"]} ⚡
                </button>
            </div>

            <audio id="audio-{room_idx}" src="data:audio/mp3;base64,{song_data}"></audio>
            <p style="color:{c1}; text-align:center; font-size:13px; margin-top:10px; letter-spacing: 1px;">
                >> SYSTEM_LOADING: {current_song}
            </p>
        </div>

        <script>
            const audio = document.getElementById('audio-{room_idx}');
            const btnPlay = document.getElementById('btn-play-{room_idx}');
            const canvas = document.getElementById('canvas-{room_idx}');
            const ctx = canvas.getContext('2d');
            let audioCtx, analyser, source, dataArray;

            function initAudio() {{
                if (!audioCtx) {{
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    analyser = audioCtx.createAnalyser();
                    source = audioCtx.createMediaElementSource(audio);
                    source.connect(analyser);
                    analyser.connect(audioCtx.destination);
                    analyser.fftSize = 128;
                    dataArray = new Uint8Array(analyser.frequencyBinCount);
                    render();
                }}
            }}

            btnPlay.onclick = function() {{
                initAudio();
                if (audio.paused) {{
                    audio.play();
                    btnPlay.innerText = "SYSTEM ONLINE 🟢";
                    btnPlay.style.boxShadow = "0 0 15px {c1}";
                    sessionStorage.setItem('synapse_active', 'true');
                }} else {{
                    audio.pause();
                    btnPlay.innerText = "SYSTEM PAUSED 🔴";
                    btnPlay.style.boxShadow = "none";
                    sessionStorage.setItem('synapse_active', 'false');
                }}
            }};

            // ระบบตรวจสอบ Auto-play จาก Session
            window.onload = function() {{
                if (sessionStorage.getItem('synapse_active') === 'true') {{
                    setTimeout(() => {{
                        initAudio();
                        audio.play().then(() => {{
                            btnPlay.innerText = "SYSTEM ONLINE 🟢";
                        }}).catch(e => console.log("Waiting for user interaction"));
                    }}, 500);
                }}
            }};

            function render() {{
                requestAnimationFrame(render);
                analyser.getByteFrequencyData(dataArray);
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                const bWidth = (canvas.width / dataArray.length) * 2.5;
                let x = 0;
                for (let i = 0; i < dataArray.length; i++) {{
                    let h = (dataArray[i] / 255) * canvas.height;
                    ctx.fillStyle = "{c1}";
                    ctx.fillRect(x, canvas.height - h, bWidth - 2, h);
                    x += bWidth;
                }}
            }}

            // หัวใจสำคัญ: เมื่อจบเพลง ให้ส่งสัญญาณไปกดปุ่ม Next ของ Streamlit
            audio.onended = () => {{
                const buttons = window.parent.document.querySelectorAll('button');
                for (let btn of buttons) {{
                    if (btn.innerText.includes("NEXT")) {{
                        btn.click();
                        break;
                    }}
                }}
            }};
        </script>
        """
        st.components.v1.html(html_code, height=280)

# --- 4. การแสดงผล UI ---
logo_b64 = get_base64("logo1.png")
st.markdown(f"""
    <style>
    header, footer, #MainMenu {{visibility: hidden;}}
    .stApp {{ background-color: #000000 !important; }}
    .main-logo {{
        width: 100px; height: 100px; margin: 0 auto;
        background-image: url("data:image/png;base64,{logo_b64 if logo_b64 else ''}");
        background-size: contain; background-repeat: no-repeat;
        filter: drop-shadow(0 0 10px #39FF14);
    }}
    /* ปรับแต่ง Tab */
    .stTabs [data-baseweb="tab-list"] {{ background-color: transparent; }}
    .stTabs [data-baseweb="tab"] {{ color: #555; }}
    .stTabs [data-baseweb="tab-highlight"] {{ background-color: #39FF14; }}
    </style>
    <div class="main-logo"></div>
""", unsafe_allow_html=True)

tabs = st.tabs([r["name"] for r in room_info])

for i, tab in enumerate(tabs):
    with tab:
        synapse_player(i)

# --- 5. CONTROL PANEL ---
st.write("---")
col1, col2, col3 = st.columns([1,2,1])

with col1:
    if st.button("⏮️ PREV", use_container_width=True):
        st.session_state.song_index -= 1
        st.rerun()

with col2:
    if st.button("🎲 SHUFFLE SYSTEM", use_container_width=True):
        st.session_state.song_index = random.randint(0, len(all_music)-1)
        st.rerun()

with col3:
    # ปุ่มนี้สำคัญมาก ห้ามเปลี่ยนชื่อ เพราะ JS ใช้ชื่อ "NEXT" ในการค้นหาปุ่มเพื่อกด Auto-play
    if st.button("⏭️ NEXT", use_container_width=True):
        st.session_state.song_index += 1
        st.rerun()

# --- 6. PLAYLIST ---
with st.expander("📂 QUANTUM DATABASE (TRACK LIST)", expanded=False):
    selected_song = st.selectbox("SEARCH TRACK", all_music, index=st.session_state.song_index % len(all_music))
    if st.button("EXECUTE LOAD ⚡"):
        st.session_state.song_index = all_music.index(selected_song)
        st.rerun()

st.caption("SYNAPSE COMMAND CENTER V.7 | READY FOR OPERATION")
