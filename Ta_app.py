import streamlit as st
import os
import base64
import random
import json

# =========================================================
# 1. CONFIG & SYSTEM THEME CONTROLLER (DYNAMIC NEON UI)
# =========================================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER V.7", layout="centered")

def get_base64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except: return None
    return None

logo_b64 = get_base64("logo1.png")

# =========================================================
# 2. GLOBAL STATE CONFIGURATION
# =========================================================
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

# Ensure we sort the music to have a deterministic order
all_music = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

# =========================================================
# 3. NAVIGATION & UI RENDER (5 ROOMS & NEON GRAF)
# =========================================================
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
                # สร้าง HTML/JS สำหรับกราฟนีออนของห้องนั้นๆ
                html_code = f"""
                <div style="margin-top:5px;">
                    <canvas id="canvas-{index}" width="300" height="110" style="width:100%; height:110px; background:#000; border:1px solid {c1}44; border-radius:15px;"></canvas>
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
                        // สั่งเชื่อมต่อระบบเสียงครั้งแรกเมื่อกด ACTIVATE
                        if (!audioCtx) {{
                            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                            analyser = audioCtx.createAnalyser();
                            source = audioCtx.createMediaElementSource(audio);
                            source.connect(analyser);
                            analyser.connect(audioCtx.destination);
                            analyser.fftSize = 256; 
                            dataArray = new Uint8Array(analyser.frequencyBinCount);
                            renderWave(); // สั่งให้กราฟนีออนเริ่มวาดทันที
                        }}
                        
                        if (audio.paused) {{ 
                            audio.play(); 
                            btn.innerText = "SYSTEM ONLINE 🟢"; 
                        }} else {{ 
                            audio.pause(); 
                            btn.innerText = "SYSTEM PAUSED 🔴"; 
                        }}
                    }};

                    // ฟังก์ชันวาดกราฟนีออน
                    function renderWave() {{
                        requestAnimationFrame(renderWave);
                        if (!analyser) return; // Prevent errors if analyser isn't set up yet
                        analyser.getByteFrequencyData(dataArray);
                        ctx.clearRect(0, 0, canvas.width, canvas.height);
                        
                        const bWidth = (canvas.width / dataArray.length) * 2.5;
                        let x = 0;
                        
                        for (let i = 0; i < dataArray.length; i++) {{
                            let h = (dataArray[i] / 255) * canvas.height;
                            let grad = ctx.createLinearGradient(0, canvas.height, 0, canvas.height - h);
                            // ใส่สีเฉพาะตัวนีออนตามห้องนั้นๆ
                            grad.addColorStop(0, "{c1}"); 
                            grad.addColorStop(1, "{c2}");
                            ctx.fillStyle = grad;
                            
                            ctx.shadowBlur = 10; 
                            ctx.shadowColor = "{c1}";
                            ctx.fillRect(x, canvas.height - h, bWidth - 1, h);
                            x += bWidth;
                        }}
                    }}
                    
                    audio.onended = () => {{
                        // สั่งเปลี่ยนเพลงและเปลี่ยนห้องอัตโนมัติโดยใช้ปุ่มลับ AUTO_NEXT
                        window.parent.document.querySelector('button[title="AUTO_NEXT"]').click();
                    }};
                </script>
                """
                st.components.v1.html(html_code, height=260)

# =========================================================
# 4. ปุ่มลับสำหรับระบบอัตโนมัติ (AUTO_NEXT TRIGGER)
# =========================================================
# We need to make this button accessible even though it's "invisible"
if st.button("AUTO_NEXT", key="AUTO_NEXT_BUTTON", help="Invisible Trigger", use_container_width=True):
    st.session_state.global_song_idx = (st.session_state.global_song_idx + 1) % len(all_music)
    st.rerun() 
# We need to render the hidden trigger so JS can find it. The title "AUTO_NEXT" is used by querySelector.
st.markdown('<button title="AUTO_NEXT" style="display:none;"></button>', unsafe_allow_html=True)

# =========================================================
# 5. GLOBAL PLAYLIST (จัดระเบียบคลังเพลง 52 เพลง)
# =========================================================
st.write("---")
st.markdown("<h3 style='font-family:Orbitron; color:#39FF14; text-align:center;'>🎶 GLOBAL PLAYLIST (52 TRACKS)</h3>", unsafe_allow_html=True)

# สร้างปุ่มควบคุมหลัก
col_a, col_b = st.columns(2)
with col_a:
    if st.button("⏭️ SKIP TO NEXT", key="skip_all"):
        st.session_state.global_song_idx += 1
        st.rerun()
with col_b:
    if st.button("🎲 SHUFFLE ALL", key="shuffle_all"):
        st.session_state.global_song_idx = random.randint(0, len(all_music)-1)
        st.rerun()

# แสดงรายชื่อเพลงทั้งหมดให้อาจารย์จิ้มเลือกได้จริง (ไม่ฟ้อง Error)
with st.container():
    st.markdown("""
        <style>
        .song-list-container {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #333;
            padding: 10px;
            border-radius: 10px;
            background: rgba(10, 10, 10, 0.9);
        }
        .song-item {
            font-family: sans-serif;
            font-size: 14px;
            padding: 8px 12px;
            color: #ddd;
            border-bottom: 1px solid #222;
        }
        .current-song {
            color: #39FF14;
            font-weight: bold;
            background: rgba(57, 255, 20, 0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.expander("📂 ดูรายชื่อเพลงทั้งหมดและเลือกเล่น", expanded=True):
        st.markdown('<div class="song-list-container">', unsafe_allow_html=True)
        for i, song in enumerate(all_music):
            is_current = (i == st.session_state.global_song_idx % len(all_music))
            
            # เน้นสีเพลงที่กำลังเล่นอยู่
            if is_current:
                st.markdown(f'<div class="song-item current-song">▶️ {i+1}. {song}</div>', unsafe_allow_html=True)
            else:
                # ให้กดปุ่มที่รายชื่อเพื่อเลือกเพลงนั้นมาเล่น
                if st.button(f"▪️ {i+1}. {song}", key=f"select_{i}", use_container_width=True):
                    st.session_state.global_song_idx = i
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Final caption, with the music player label separated to avoid potential syntax issues with emojis and trailing text.
st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | SYNAPSE OMNI-PLAY V.7")
st.caption("🎵 MUSIC PLAYER")
