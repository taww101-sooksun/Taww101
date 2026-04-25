import streamlit as st
import os
import base64
import random

# --- 1. CONFIG & SYSTEM ---
st.set_page_config(page_title="SYNAPSE COMMAND CENTER V.7", layout="centered")

def get_base64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except: return None
    return None

logo_b64 = get_base64("logo1.png")

# --- 2. GLOBAL STATE ---
if 'global_song_idx' not in st.session_state:
    st.session_state.global_song_idx = 0
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False

room_info = [
    {"name": "🔥 CORE ROOM", "color1": "#39FF14", "color2": "#00FFDD"},
    {"name": "🎧 R&B LOUNGE", "color1": "#FF00DE", "color2": "#7000FF"},
    {"name": "🎤 RAP ZONE", "color1": "#00F3FF", "color2": "#0051FF"},
    {"name": "🌌 QUANTUM", "color1": "#FF8C00", "color2": "#FF0000"},
    {"name": "🎸 ISAN INDIE", "color1": "#FFD700", "color2": "#FF5733"}
]

all_music = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

# --- 3. UI RENDER (5 ROOMS) ---
tabs = st.tabs([r["name"] for r in room_info])

for index, tab in enumerate(tabs):
    with tab:
        info = room_info[index]
        c1, c2 = info["color1"], info["color2"]
        
        st.markdown(f"""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
            header, footer, #MainMenu {{visibility: hidden;}}
            .stApp {{ background-color: #000000 !important; }}
            .logo-img-{index} {{
                width: 70px; height: 70px; margin: 0 auto;
                background-image: url("data:image/png;base64,{logo_b64}");
                background-size: contain; background-repeat: no-repeat;
                filter: drop-shadow(0 0 15px {c1});
                animation: pulse 2s infinite alternate;
            }}
            @keyframes pulse {{ from {{ transform: scale(1); }} to {{ transform: scale(1.1); }} }}
            .title-{index} {{
                font-family: 'Orbitron', sans-serif; color: #fff; text-align: center;
                text-shadow: 0 0 10px {c1}; font-size: 1.4rem; margin-top:10px;
            }}
            </style>
            <div class="logo-img-{index}"></div>
            <h1 class="title-{index}">{info["name"]}</h1>
        """, unsafe_allow_html=True)

        if all_music:
            current_song_name = all_music[st.session_state.global_song_idx % len(all_music)]
            song_b64 = get_base64(current_song_name)
            
            if song_b64:
                html_code = f"""
                <div style="margin-top:5px;">
                    <canvas id="canvas-{index}" style="width:100%; height:110px; background:#000; border:1px solid {c1}44; border-radius:15px;"></canvas>
                    <button id="btn-{index}" style="width:100%; padding:15px; margin-top:10px; background:transparent; color:{c1}; border:2px solid {c1}; font-family:'Orbitron'; cursor:pointer; border-radius:10px; font-weight:bold; box-shadow: 0 0 15px {c1}33;">
                        ACTIVATE {info["name"]} ⚡
                    </button>
                    <audio id="audio-{index}" src="data:audio/mp3;base64,{song_b64}"></audio>
                    <p style="color:{c1}; font-family:'Orbitron'; font-size:12px; text-align:center; margin-top:8px;">
                        NOW PLAYING: {current_song_name}
                    </p>
                </div>
                <script>
                    const audio = document.getElementById('audio-{index}');
                    const btn = document.getElementById('btn-{index}');
                    const canvas = document.getElementById('canvas-{index}');
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
                        if (audio.paused) {{ audio.play(); btn.innerText = "SYSTEM ONLINE 🟢"; }}
                        else {{ audio.pause(); btn.innerText = "SYSTEM PAUSED 🔴"; }}
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
                        // สั่งเปลี่ยนเพลงและเปลี่ยนห้องอัตโนมัติ
                        window.parent.document.querySelector('button[title="AUTO_NEXT"]').click();
                    }};
                </script>
                """
                st.components.v1.html(html_code, height=260)

# --- 4. ปุ่มลับสำหรับระบบอัตโนมัติ ---
if st.button("AUTO_NEXT", key="AUTO_NEXT", help="Invisible Trigger"):
    st.session_state.global_song_idx = (st.session_state.global_song_idx + 1) % len(all_music)
    # สั่งให้เปลี่ยนหน้าไปห้องถัดไป (Optional: ถ้าอาจารย์อยากให้อยู่หน้าเดิมก็ตัดบรรทัดนี้ออกได้)
    # st.rerun() 

# --- 5. คลังเพลง 52 เพลง (โชว์รายชื่อทั้งหมด) ---
st.write("---")
st.markdown("<h3 style='font-family:Orbitron; color:#39FF14; text-align:center;'>🎵 GLOBAL PLAYLIST (52 TRACKS)</h3>", unsafe_allow_html=True)

# สร้างปุ่มควบคุมหลัก
col_a, col_b = st.columns(2)
with col_a:
    if st.button("⏭️ SKIP TO NEXT"):
        st.session_state.global_song_idx += 1
        st.rerun()
with col_b:
    if st.button("🎲 SHUFFLE ALL"):
        st.session_state.global_song_idx = random.randint(0, len(all_music)-1)
        st.rerun()

# แสดงรายชื่อเพลงทั้งหมดให้อาจารย์จิ้มเลือก
with st.container():
    st.markdown("""
        <style>
        .song-list-container {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #333;
            padding: 10px;
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.expander("📂 ดูรายชื่อเพลงทั้งหมดและเลือกเล่น", expanded=True):
        for i, song in enumerate(all_music):
            # เน้นสีเพลงที่กำลังเล่นอยู่
            is_current = (i == st.session_state.global_song_idx % len(all_music))
            label = f"▶️ {i+1}. {song}" if is_current else f"▪️ {i+1}. {song}"
            
            if st.button(label, key=f"select_{i}", use_container_width=True):
                st.session_state.global_song_idx = i
                st.rerun()

                st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | SYNAPSE OMNI-PLAY V.7")import streamlit as st
import os
import base64
import random

# --- 1. CONFIG & SYSTEM ---
st.set_page_config(page_title="SYNAPSE COMMAND CENTER V.7", layout="centered")

def get_base64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except: return None
    return None

logo_b64 = get_base64("logo1.png")

# --- 2. GLOBAL STATE ---
if 'global_song_idx' not in st.session_state:
    st.session_state.global_song_idx = 0
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False

room_info = [
    {"name": "🔥 CORE ROOM", "color1": "#39FF14", "color2": "#00FFDD"},
    {"name": "🎧 R&B LOUNGE", "color1": "#FF00DE", "color2": "#7000FF"},
    {"name": "🎤 RAP ZONE", "color1": "#00F3FF", "color2": "#0051FF"},
    {"name": "🌌 QUANTUM", "color1": "#FF8C00", "color2": "#FF0000"},
    {"name": "🎸 ISAN INDIE", "color1": "#FFD700", "color2": "#FF5733"}
]

all_music = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

# --- 3. UI RENDER (5 ROOMS) ---
tabs = st.tabs([r["name"] for r in room_info])

for index, tab in enumerate(tabs):
    with tab:
        info = room_info[index]
        c1, c2 = info["color1"], info["color2"]
        
        st.markdown(f"""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
            header, footer, #MainMenu {{visibility: hidden;}}
            .stApp {{ background-color: #000000 !important; }}
            .logo-img-{index} {{
                width: 70px; height: 70px; margin: 0 auto;
                background-image: url("data:image/png;base64,{logo_b64}");
                background-size: contain; background-repeat: no-repeat;
                filter: drop-shadow(0 0 15px {c1});
                animation: pulse 2s infinite alternate;
            }}
            @keyframes pulse {{ from {{ transform: scale(1); }} to {{ transform: scale(1.1); }} }}
            .title-{index} {{
                font-family: 'Orbitron', sans-serif; color: #fff; text-align: center;
                text-shadow: 0 0 10px {c1}; font-size: 1.4rem; margin-top:10px;
            }}
            </style>
            <div class="logo-img-{index}"></div>
            <h1 class="title-{index}">{info["name"]}</h1>
        """, unsafe_allow_html=True)

        if all_music:
            current_song_name = all_music[st.session_state.global_song_idx % len(all_music)]
            song_b64 = get_base64(current_song_name)
            
            if song_b64:
                html_code = f"""
                <div style="margin-top:5px;">
                    <canvas id="canvas-{index}" style="width:100%; height:110px; background:#000; border:1px solid {c1}44; border-radius:15px;"></canvas>
                    <button id="btn-{index}" style="width:100%; padding:15px; margin-top:10px; background:transparent; color:{c1}; border:2px solid {c1}; font-family:'Orbitron'; cursor:pointer; border-radius:10px; font-weight:bold; box-shadow: 0 0 15px {c1}33;">
                        ACTIVATE {info["name"]} ⚡
                    </button>
                    <audio id="audio-{index}" src="data:audio/mp3;base64,{song_b64}"></audio>
                    <p style="color:{c1}; font-family:'Orbitron'; font-size:12px; text-align:center; margin-top:8px;">
                        NOW PLAYING: {current_song_name}
                    </p>
                </div>
                <script>
                    const audio = document.getElementById('audio-{index}');
                    const btn = document.getElementById('btn-{index}');
                    const canvas = document.getElementById('canvas-{index}');
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
                        if (audio.paused) {{ audio.play(); btn.innerText = "SYSTEM ONLINE 🟢"; }}
                        else {{ audio.pause(); btn.innerText = "SYSTEM PAUSED 🔴"; }}
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
                        // สั่งเปลี่ยนเพลงและเปลี่ยนห้องอัตโนมัติ
                        window.parent.document.querySelector('button[title="AUTO_NEXT"]').click();
                    }};
                </script>
                """
                st.components.v1.html(html_code, height=260)

# --- 4. ปุ่มลับสำหรับระบบอัตโนมัติ ---
if st.button("AUTO_NEXT", key="AUTO_NEXT", help="Invisible Trigger"):
    st.session_state.global_song_idx = (st.session_state.global_song_idx + 1) % len(all_music)
    # สั่งให้เปลี่ยนหน้าไปห้องถัดไป (Optional: ถ้าอาจารย์อยากให้อยู่หน้าเดิมก็ตัดบรรทัดนี้ออกได้)
    # st.rerun() 

# --- 5. คลังเพลง 52 เพลง (โชว์รายชื่อทั้งหมด) ---
st.write("---")
st.markdown("<h3 style='font-family:Orbitron; color:#39FF14; text-align:center;'>🎵 GLOBAL PLAYLIST (52 TRACKS)</h3>", unsafe_allow_html=True)

# สร้างปุ่มควบคุมหลัก
col_a, col_b = st.columns(2)
with col_a:
    if st.button("⏭️ SKIP TO NEXT"):
        st.session_state.global_song_idx += 1
        st.rerun()
with col_b:
    if st.button("🎲 SHUFFLE ALL"):
        st.session_state.global_song_idx = random.randint(0, len(all_music)-1)
        st.rerun()

# แสดงรายชื่อเพลงทั้งหมดให้อาจารย์จิ้มเลือก
with st.container():
    st.markdown("""
        <style>
        .song-list-container {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #333;
            padding: 10px;
            border-radius: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.expander("📂 ดูรายชื่อเพลงทั้งหมดและเลือกเล่น", expanded=True):
        for i, song in enumerate(all_music):
            # เน้นสีเพลงที่กำลังเล่นอยู่
            is_current = (i == st.session_state.global_song_idx % len(all_music))
            label = f"▶️ {i+1}. {song}" if is_current else f"▪️ {i+1}. {song}"
            
            if st.button(label, key=f"select_{i}", use_container_width=True):
                st.session_state.global_song_idx = i
                st.rerun()
              b st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | SYNAPSE OMNI-PLAY V.7")🎵 MUSIC PLAYER


ModuleNotFoundError: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:
File "/mount/src/taww101/ส
   
