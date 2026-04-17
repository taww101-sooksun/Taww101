import streamlit as st
import os
import base64

# --- 1. CONFIG ---
st.set_page_config(page_title="SYNAPSE 5-ROOMS HD", layout="centered")

def get_base64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except: return None
    return None

logo_b64 = get_base64("logo1.png")

# --- 2. ตั้งค่าชื่อห้องและเฉดสี (Gradients) ---
# ผมตั้งค่าคู่สี Gradient ไว้ให้แต่ละห้องต่างกันนะครับ
room_info = [
    {"name": "🔥 CORE ROOM", "color1": "#39FF14", "color2": "#00FFDD", "keywords": []},
    {"name": "🎧 R&B LOUNGE", "color1": "#FF00DE", "color2": "#7000FF", "keywords": ["r&b", "soul", "slow"]},
    {"name": "🎤 RAP ZONE", "color1": "#00F3FF", "color2": "#0051FF", "keywords": ["rap", "hiphop", "beat"]},
    {"name": "🌌 QUANTUM", "color1": "#FF8C00", "color2": "#FF0000", "keywords": ["space", "quantum", "synth"]},
    {"name": "🎸 ISAN INDIE", "color1": "#FFD700", "color2": "#FF5733", "keywords": ["isan", "indie", "หมอลำ"]}
]

all_music = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
tabs = st.tabs([r["name"] for r in room_info])

for index, tab in enumerate(tabs):
    with tab:
        info = room_info[index]
        c1, c2 = info["color1"], info["color2"]
        
        if index == 0: room_music = all_music
        else: room_music = [f for f in all_music if any(k in f.lower() for k in info["keywords"])]

        st.markdown(f"""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
            header, footer, #MainMenu {{visibility: hidden;}}
            .stApp {{ background-color: #000000 !important; }}
            .logo-img-{index} {{
                width: 80px; height: 80px; margin: 0 auto;
                background-image: url("data:image/png;base64,{logo_b64}");
                background-size: contain; background-repeat: no-repeat;
                filter: drop-shadow(0 0 15px {c1});
                animation: pulse 2s infinite alternate;
            }}
            @keyframes pulse {{ from {{ transform: scale(1); }} to {{ transform: scale(1.08); }} }}
            .title-{index} {{
                font-family: 'Orbitron', sans-serif; color: #fff; text-align: center;
                text-shadow: 0 0 15px {c1}; font-size: 1.5rem;
            }}
            </style>
            <div class="logo-img-{index}"></div>
            <h1 class="title-{index}">{info["name"]}</h1>
        """, unsafe_allow_html=True)

        if room_music:
            song_key = f"room_idx_{index}"
            if song_key not in st.session_state: st.session_state[song_key] = 0
            
            current_song_name = room_music[st.session_state[song_key] % len(room_music)]
            song_b64 = get_base64(current_song_name)
            
            if song_b64:
                # เครื่องเล่นแบบ High-Def Visualizer
                html_code = f"""
                <div style="margin-top:10px;">
                    <canvas id="canvas-{index}" style="width:100%; height:120px; background:#000; border:1px solid {c1}44; border-radius:15px;"></canvas>
                    <button id="btn-{index}" style="width:100%; padding:18px; margin-top:10px; background:transparent; color:{c1}; border:2px solid {c1}; font-family:'Orbitron'; cursor:pointer; border-radius:12px; font-weight:bold; box-shadow: 0 0 20px {c1}44;">
                        ACTIVATE SYSTEM ⚡
                    </button>
                    <audio id="audio-{index}" src="data:audio/mp3;base64,{song_b64}"></audio>
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
                            // เพิ่มความละเอียดตรงนี้ (256 = ละเอียดมาก)
                            analyser.fftSize = 256; 
                            dataArray = new Uint8Array(analyser.frequencyBinCount);
                            render();
                        }}
                        if (audio.paused) {{ audio.play(); btn.innerText = "PLAYING IN {info['name']}"; btn.style.boxShadow = "0 0 30px {c1}"; }}
                        else {{ audio.pause(); btn.innerText = "SYSTEM PAUSED"; }}
                    }};

                    function render() {{
                        requestAnimationFrame(render);
                        analyser.getByteFrequencyData(dataArray);
                        ctx.clearRect(0, 0, canvas.width, canvas.height);
                        
                        const bWidth = (canvas.width / dataArray.length) * 1.5;
                        let x = 0;

                        for (let i = 0; i < dataArray.length; i++) {{
                            let h = (dataArray[i] / 255) * canvas.height;
                            
                            // สร้าง Gradient สำหรับแต่ละแท่ง
                            let gradient = ctx.createLinearGradient(0, canvas.height, 0, canvas.height - h);
                            gradient.addColorStop(0, "{c1}");
                            gradient.addColorStop(1, "{c2}");
                            
                            ctx.fillStyle = gradient;
                            // ใส่ความเรืองแสงให้แท่งกราฟ
                            ctx.shadowBlur = 5;
                            ctx.shadowColor = "{c1}";
                            
                            // วาดแท่งกราฟแบบมนๆ นิดหนึ่ง
                            ctx.fillRect(x, canvas.height - h, bWidth - 1, h);
                            x += bWidth;
                        }}
                    }}
                    audio.onended = () => {{ window.parent.document.querySelector('button[title="NEXT_{index}"]').click(); }};
                </script>
                """
                st.components.v1.html(html_code, height=250)

            c1_btn, c2_btn = st.columns(2)
            with c1_btn:
                if st.button(f"⏭️ NEXT TRACK", key=f"NEXT_{index}"):
                    st.session_state[song_key] += 1
                    st.rerun()
            with c2_btn:
                st.markdown(f"<p style='text-align:right; color:{c1}; font-family:Orbitron;'>TRACK: {st.session_state[song_key] % len(room_music) + 1}/{len(room_music)}</p>", unsafe_allow_html=True)
            
            with st.expander(f"🎼 TRACKLIST ({current_song_name})"):
                for s_idx, s_name in enumerate(room_music):
                    if st.button(f"{s_idx+1}. {s_name}", key=f"btn_{index}_{s_idx}"):
                        st.session_state[song_key] = s_idx
                        st.rerun()
        else:
            st.info(f"ห้องนี้ยังไม่มีเพลงครับ")

st.markdown("---")
st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | SYNAPSE HD-VISUALIZER V.5")
