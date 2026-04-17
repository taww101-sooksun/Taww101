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

# --- 2. ตั้งค่าชื่อห้องและเงื่อนไขการกรองเพลง ---
room_info = [
    {"name": "🔥 CORE ROOM", "color": "#39FF14", "keywords": []}, # ห้องหลัก รวมทุกเพลง
    {"name": "🎧 R&B LOUNGE", "color": "#FF00DE", "keywords": ["r&b", "soul", "slow"]},
    {"name": "🎤 RAP ZONE", "color": "#00F3FF", "keywords": ["rap", "hiphop", "beat"]},
    {"name": "🌌 QUANTUM", "color": "#FF8C00", "keywords": ["space", "quantum", "synth"]},
    {"name": "🎸 ISAN INDIE", "color": "#FFD700", "keywords": ["isan", "indie", "หมอลำ"]}
]

# สแกนเพลงทั้งหมด 52 เพลงจากหน้าแรก
all_music = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

tabs = st.tabs([r["name"] for r in room_info])

for index, tab in enumerate(tabs):
    with tab:
        info = room_info[index]
        current_color = info["color"]
        
        # กรองเพลงเข้าห้องตาม Keyword (ถ้าเป็นห้องแรกให้โชว์หมดเลย)
        if index == 0:
            room_music = all_music
        else:
            room_music = [f for f in all_music if any(k in f.lower() for k in info["keywords"])]

        # CSS ประจำห้อง
        st.markdown(f"""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
            header, footer, #MainMenu {{visibility: hidden;}}
            .stApp {{ background-color: #000000 !important; }}
            .logo-img-{index} {{
                width: 80px; height: 80px; margin: 0 auto;
                background-image: url("data:image/png;base64,{logo_b64}");
                background-size: contain; background-repeat: no-repeat;
                filter: drop-shadow(0 0 10px {current_color});
                animation: pulse 2s infinite alternate;
            }}
            @keyframes pulse {{ from {{ transform: scale(1); }} to {{ transform: scale(1.05); }} }}
            .title-{index} {{
                font-family: 'Orbitron', sans-serif; color: #fff; text-align: center;
                text-shadow: 0 0 10px {current_color}; font-size: 1.5rem;
            }}
            </style>
            <div class="logo-img-{index}"></div>
            <h1 class="title-{index}">{info["name"]}</h1>
        """, unsafe_allow_html=True)

        if room_music:
            song_key = f"room_idx_{index}"
            if song_key not in st.session_state:
                st.session_state[song_key] = 0
            
            current_song = room_music[st.session_state[song_key] % len(room_music)]

            st.markdown(f"""
                <div style="border: 1px solid {current_color}; border-radius:10px; padding:8px; background:rgba(0,0,0,0.5); text-align:center;">
                    <marquee style="color:{current_color}; font-family:'Orbitron'; font-size:14px;">
                        {info["name"]} | NOW PLAYING: {current_song}
                    </marquee>
                </div>
            """, unsafe_allow_html=True)

            # เครื่องเล่นและกราฟเสียง
            html_code = f"""
            <div style="margin-top:15px;">
                <canvas id="canvas-{index}" style="width:100%; height:90px; background:#000; border:1px solid {current_color}; border-radius:10px;"></canvas>
                <button id="btn-{index}" style="width:100%; padding:18px; margin-top:10px; background:transparent; color:{current_color}; border:2px solid {current_color}; font-family:'Orbitron'; cursor:pointer; border-radius:10px; font-weight:bold;">
                    ACTIVATE {info["name"]} ⚡
                </button>
                <audio id="audio-{index}" src="./{current_song}" crossorigin="anonymous"></audio>
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
                    if (audio.paused) {{ audio.play(); btn.innerText = "PLAYING..."; }}
                    else {{ audio.pause(); btn.innerText = "PAUSED"; }}
                }};

                function render() {{
                    requestAnimationFrame(render);
                    analyser.getByteFrequencyData(dataArray);
                    ctx.fillStyle = "#000"; ctx.fillRect(0, 0, canvas.width, canvas.height);
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
            st.components.v1.html(html_code, height=200)

            # ปุ่มควบคุม
            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"⏭️ NEXT TRACK", key=f"NEXT_{index}"):
                    st.session_state[song_key] += 1
                    st.rerun()
            with c2:
                st.markdown(f"<p style='text-align:right; color:{current_color};'>TRACKS: {len(room_music)}</p>", unsafe_allow_html=True)
            
            # รายชื่อเพลงในห้องนั้นๆ
            with st.expander(f"📁 LIST IN {info['name']}"):
                for s_idx, s_name in enumerate(room_music):
                    if st.button(f"{s_idx+1}. {s_name}", key=f"btn_{index}_{s_idx}"):
                        st.session_state[song_key] = s_idx
                        st.rerun()
        else:
            st.info(f"ห้องนี้ยังไม่มีเพลงที่ตรงกับเงื่อนไขครับ (ใส่คำว่า {info['keywords']} ในชื่อไฟล์)")

st.markdown("---")
st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | SYNAPSE OMNI-ROOM V.3")
