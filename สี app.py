import streamlit as st
import os
import base64

# --- 1. CONFIG ---
st.set_page_config(page_title="SYNAPSE 5-ROOMS AUTO-CYCLE", layout="centered")

def get_base64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except: return None
    return None

logo_b64 = get_base64("logo1.png")

# --- 2. GLOBAL STATE (ใช้ร่วมกันทุกห้อง) ---
if 'global_song_idx' not in st.session_state:
    st.session_state.global_song_idx = 0
if 'active_room' not in st.session_state:
    st.session_state.active_room = 0

room_info = [
    {"name": "🔥 CORE ROOM", "color1": "#39FF14", "color2": "#00FFDD"},
    {"name": "🎧 R&B LOUNGE", "color1": "#FF00DE", "color2": "#7000FF"},
    {"name": "🎤 RAP ZONE", "color1": "#00F3FF", "color2": "#0051FF"},
    {"name": "🌌 QUANTUM", "color1": "#FF8C00", "color2": "#FF0000"},
    {"name": "🎸 ISAN INDIE", "color1": "#FFD700", "color2": "#FF5733"}
]

# ดึงเพลงทั้งหมด
all_music = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

# --- 3. UI RENDER ---
# ใช้ st.tabs แต่เราจะบังคับเลือก tab ตาม active_room
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
                text-shadow: 0 0 10px {c1}, 0 0 20px {c1}; font-size: 1.4rem; margin-top:10px;
            }}
            </style>
            <div class="logo-img-{index}"></div>
            <h1 class="title-{index}">{info["name"]}</h1>
        """, unsafe_allow_html=True)

        if all_music:
            current_song_name = all_music[st.session_state.global_song_idx % len(all_music)]
            song_b64 = get_base64(current_song_name)
            
            if song_b64:
                # เครื่องเล่นแบบ Auto-Cycle Engine
                html_code = f"""
                <div style="margin-top:5px;">
                    <canvas id="canvas-{index}" style="width:100%; height:110px; background:#000; border:1px solid {c1}66; border-radius:15px;"></canvas>
                    <button id="btn-{index}" style="width:100%; padding:15px; margin-top:10px; background:transparent; color:{c1}; border:2px solid {c1}; font-family:'Orbitron'; cursor:pointer; border-radius:10px; font-weight:bold; box-shadow: 0 0 15px {c1}44;">
                        START SYNAPSE JOURNEY ⚡
                    </button>
                    <audio id="audio-{index}" src="data:audio/mp3;base64,{song_b64}"></audio>
                    <p style="color:{c1}; font-family:'Orbitron'; font-size:12px; text-align:center; margin-top:8px;">
                        TRACK: {current_song_name}
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

                    // เมื่อจบเพลง: สั่งให้ Streamlit เปลี่ยนทั้งเพลงและห้อง!
                    audio.onended = () => {{
                        window.parent.document.querySelector('button[title="NEXT_CYCLE"]').click();
                    }};
                </script>
                """
                st.components.v1.html(html_code, height=260)

# --- 4. ปุ่มควบคุมลับ (Hidden) สำหรับ Auto-Cycle ---
# ปุ่มนี้จะถูก JavaScript กดให้อัตโนมัติเมื่อเพลงจบ
if st.button("NEXT_CYCLE", key="NEXT_CYCLE", help="Invisible Auto-Next"):
    # เปลี่ยนเพลงถัดไป
    st.session_state.global_song_idx = (st.session_state.global_song_idx + 1) % len(all_music)
    # เปลี่ยนห้องถัดไป (0 -> 1 -> 2 -> 3 -> 4 -> 0)
    st.session_state.active_room = (st.session_state.active_room + 1) % 5
    st.rerun()

# --- 5. CONTROL PANEL (ด้านล่าง) ---
st.write("---")
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    if st.button("⏭️ SKIP TRACK"):
        st.session_state.global_song_idx += 1
        st.rerun()
with c2:
    if st.button("🎲 SHUFFLE"):
        st.session_state.global_song_idx = random.randint(0, len(all_music)-1)
        st.rerun()
with c3:
    # แสดงห้องปัจจุบัน
    st.markdown(f"<p style='text-align:right; color:#fff; font-family:Orbitron;'>ROOM: {st.session_state.active_room + 1}/5</p>", unsafe_allow_html=True)

st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | SYNAPSE AUTO-JOURNEY V.6")
