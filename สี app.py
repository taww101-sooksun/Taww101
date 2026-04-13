import streamlit as st
import streamlit.components.v1 as components
import os
import base64

def room_music():
    # --- เริ่มต้นการตั้งค่า Session State ---
    if 'song_index' not in st.session_state:
        st.session_state.song_index = 0

    # 1. โหลดรายชื่อเพลง
    music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลงในระบบ")
        return

    # 2. เตรียมข้อมูลเพลงปัจจุบัน
    current_song = music_files[st.session_state.song_index]
    with open(current_song, "rb") as f:
        audio_url = f"data:audio/mp3;base64,{base64.b64encode(f.read()).decode()}"

    # 3. สร้าง UI สไตล์ SYNAPSE (เลียนแบบรูปภาพที่คุณส่งมา)
    # เราจะใส่ Logic การเล่นต่อเนื่องไว้ใน JavaScript นี้เลย
    ui_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body {{ margin: 0; font-family: sans-serif; color: white; background: transparent; }}
            .player-card {{
                background: linear-gradient(180deg, rgba(139, 0, 255, 0.2) 0%, rgba(0, 0, 0, 0.8) 100%);
                border: 2px solid rgba(0, 242, 254, 0.5);
                border-radius: 20px; padding: 20px; width: 360px;
                box-shadow: 0 0 20px rgba(0, 242, 254, 0.3); text-align: center;
            }}
            .album-art {{
                width: 200px; height: 200px; margin: 0 auto 20px;
                background: #111; border-radius: 15px;
                border: 2px solid #ff007f; box-shadow: 0 0 15px #ff007f;
                display: flex; align-items: center; justify-content: center;
                overflow: hidden;
            }}
            .album-art img {{ width: 100%; height: 100%; object-fit: cover; }}
            .title {{ font-size: 18px; font-weight: bold; margin-bottom: 5px; color: #f0f0f0; }}
            .artist {{ font-size: 13px; color: #00f2fe; margin-bottom: 20px; }}
            .controls {{ display: flex; justify-content: space-around; align-items: center; margin-top: 20px; }}
            .btn {{ font-size: 24px; cursor: pointer; color: white; opacity: 0.8; transition: 0.2s; }}
            .btn:hover {{ opacity: 1; transform: scale(1.1); color: #00f2fe; }}
            .play-pause {{ font-size: 45px; }}
            
            /* แถบเล่นเพลง */
            #progress-bar {{ width: 100%; height: 4px; background: #333; margin: 15px 0; border-radius: 2px; }}
            #progress-fill {{ width: 0%; height: 100%; background: #00f2fe; border-radius: 2px; box-shadow: 0 0 10px #00f2fe; }}
        </style>
    </head>
    <body>
        <div class="player-card">
            <div class="album-art">
                <i class="fas fa-music fa-5x" style="color: #333;"></i>
            </div>
            <div class="title">{current_song}</div>
            <div class="artist">SYNAPSE | อยู่นิ่งๆ ไม่เจ็บตัว</div>
            
            <div id="progress-bar"><div id="progress-fill"></div></div>
            
            <div class="controls">
                <i class="fas fa-step-backward btn" onclick="send('prev')"></i>
                <i class="fas fa-play-circle btn play-pause" id="playIcon" onclick="togglePlay()"></i>
                <i class="fas fa-step-forward btn" onclick="send('next')"></i>
            </div>
        </div>

        <audio id="main-audio" src="{audio_url}" autoplay></audio>

        <script>
            const audio = document.getElementById('main-audio');
            const playIcon = document.getElementById('playIcon');
            const fill = document.getElementById('progress-fill');

            // ส่งคำสั่งกลับไปที่ Streamlit
            function send(cmd) {{
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: cmd}}, '*');
            }}

            function togglePlay() {{
                if(audio.paused) {{ audio.play(); playIcon.className = 'fas fa-pause-circle btn play-pause'; }}
                else {{ audio.pause(); playIcon.className = 'fas fa-play-circle btn play-pause'; }}
            }}

            audio.onended = () => send('next'); // จบแล้วไปเพลงถัดไป

            audio.ontimeupdate = () => {{
                const pct = (audio.currentTime / audio.duration) * 100;
                fill.style.width = pct + "%";
            }};
        </script>
    </body>
    </html>
    """

    # 4. แสดงผล UI และรับค่าการสั่งงาน
    # เราใช้ key เพื่อให้ค่ามันอัปเดต และรับผลจาก postMessage
    cmd = components.html(ui_html, height=450, key=f"player_{st.session_state.song_index}")

    # 5. Logic การเปลี่ยนเพลง (ฝั่ง Streamlit)
    # หมายเหตุ: ใน Streamlit version ใหม่ การเช็คค่าจาก components อาจต้องรันผ่าน Session State
    if cmd == 'next':
        st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
        st.rerun()
    elif cmd == 'prev':
        st.session_state.song_index = (st.session_state.song_index - 1) % len(music_files)
        st.rerun()

    # ส่วนของรายชื่อเพลง (เลือกได้เหมือนเดิม)
    st.write("---")
    with st.expander("📂 คลังเพลง SYNAPSE"):
        for i, f in enumerate(music_files):
            active = "🔹" if i == st.session_state.song_index else ""
            if st.button(f"{active} {f}", key=f"list_{i}", use_container_width=True):
                st.session_state.song_index = i
                st.rerun()
