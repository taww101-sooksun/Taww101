import streamlit as st
import os
import random
import base64

# --- 1. CONFIG & THEME ---
st.set_page_config(page_title="SYNAPSE 5-ROOMS", layout="centered")

def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

logo_b64 = get_base64("logo1.png")

# --- 2. สร้าง 5 ห้อง (Tabs) ---
room_names = ["🔥 CORE ROOM", "🎧 R&B LOUNGE", "🎤 RAP ZONE", "🌌 QUANTUM", "🎸 ISAN INDIE"]
room_folders = ["room1", "room2", "room3", "room4", "room5"] # ชื่อโฟลเดอร์ที่เก็บเพลง
colors = ["#39FF14", "#FF00DE", "#00F3FF", "#FF8C00", "#FFD700"]

tabs = st.tabs(room_names)

for index, tab in enumerate(tabs):
    with tab:
        current_color = colors[index]
        current_folder = room_folders[index]
        
        # สร้างโฟลเดอร์ให้อัตโนมัติถ้ายังไม่มี (ป้องกัน Error)
        if not os.path.exists(current_folder):
            os.makedirs(current_folder)

        st.markdown(f"""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
            header, footer, #MainMenu {{visibility: hidden;}}
            .stApp {{ background-color: #000000 !important; }}
            .logo-center-{index} {{ display: flex; justify-content: center; margin-top: 10px; }}
            .logo-img-{index} {{
                width: 80px; height: 80px;
                background-image: url("data:image/png;base64,{logo_b64}");
                background-size: contain; background-repeat: no-repeat;
                filter: drop-shadow(0 0 10px {current_color});
                animation: pulse 2s infinite alternate;
            }}
            @keyframes pulse {{ from {{ transform: scale(1); }} to {{ transform: scale(1.05); }} }}
            .title-{index} {{
                font-family: 'Orbitron', sans-serif; color: #fff; text-align: center;
                text-shadow: 0 0 10px {current_color}; font-size: 1.5rem; margin-bottom: 20px;
            }}
            </style>
            <div class="logo-center-{index}"><div class="logo-img-{index}"></div></div>
            <h1 class="title-{index}">{room_names[index]}</h1>
        """, unsafe_allow_html=True)

        # สแกนเพลงเฉพาะในโฟลเดอร์ของห้องนั้นๆ
        music_files = sorted([f for f in os.listdir(current_folder) if f.lower().endswith(".mp3")])
        
        if music_files:
            song_key = f"song_room_{index}"
            if song_key not in st.session_state:
                st.session_state[song_key] = 0
            
            # ชี้ไปที่ไฟล์เพลงในโฟลเดอร์ย่อย
            current_song_name = music_files[st.session_state[song_key] % len(music_files)]
            current_song_path = os.path.join(current_folder, current_song_name)

            st.markdown(f"""
                <div style="border: 1px solid {current_color}; border-radius:10px; padding:5px; background:rgba(0,0,0,0.5);">
                    <marquee style="color:{current_color}; font-family:'Orbitron';">
                        ROOM: {room_names[index]} | FILE: {current_song_name}
                    </marquee>
                </div>
            """, unsafe_allow_html=True)

            # เครื่องเล่นและกราฟเสียง (ดึงเพลงจากโฟลเดอร์ห้อง)
            html_player = f"""
            <div style="margin-top:15px;">
                <canvas id="canvas-{index}" style="width:100%; height:80px; background:#000; border:1px solid {current_color}; border-radius:10px;"></canvas>
                <button id="btn-{index}" style="width:100%; padding:15px; margin-top:10px; background:transparent; color:{current_color}; border:2px solid {current_color}; font-family:'Orbitron'; cursor:pointer; border-radius:10px; box-shadow: 0 0 10px {current_color};">
                    ENTER {room_names[index]} ⚡
                </button>
                <audio id="audio-{index}" src="./{current_song_path}" crossorigin="anonymous"></audio>
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
                        analyser.fftSize = 64;
                        dataArray = new Uint8Array(analyser.frequencyBinCount);
                        render();
                    }}
                    if (audio.paused) {{ 
                        audio.play();
                        btn.innerText = "SYSTEM ACTIVE 🟢";
                    }} else {{
                        audio.pause();
                        btn.innerText = "SYSTEM PAUSED 🔴";
                    }}
                }};

                function render() {{
                    requestAnimationFrame(render);
                    analyser.getByteFrequencyData(dataArray);
                    ctx.fillStyle = "#000";
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    const bWidth = (canvas.width / dataArray.length) * 2;
                    for (let i = 0; i < dataArray.length; i++) {{
                        let h = (dataArray[i] / 255) * canvas.height;
                        ctx.fillStyle = "{current_color}";
                        ctx.fillRect(i * bWidth, canvas.height - h, bWidth - 2, h);
                    }}
                }}
                audio.onended = () => {{ window.parent.document.querySelector('button[title="NEXT_{index}"]').click(); }};
            </script>
            """
            st.components.v1.html(html_player, height=180)

            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"⏭️ NEXT TRACK", key=f"NEXT_{index}"):
                    st.session_state[song_key] += 1
                    st.rerun()
            with c2:
                # แสดงจำนวนเพลงที่มีในห้องนั้น
                st.markdown(f"<p style='text-align:right; color:{current_color}; font-size:12px;'>TOTAL: {len(music_files)} TRACKS</p>", unsafe_allow_html=True)
        else:
            st.warning(f"ยังไม่มีเพลงใน {current_folder} ครับอาจารย์")

st.markdown("---")
st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | SYNAPSE MULTI-ROOM SYSTEM V.2")
