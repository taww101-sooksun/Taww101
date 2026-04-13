import streamlit as st
import streamlit.components.v1 as components
import os
import random
import base64

# 1. จัดการคิวเพลงด้วย Session State
if 'shuffled_list' not in st.session_state:
    files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    random.shuffle(files)
    st.session_state.shuffled_list = files
    st.session_state.current_idx = 0

music_files = st.session_state.shuffled_list
idx = st.session_state.current_idx

def get_audio_b64(filename):
    with open(filename, "rb") as f:
        return base64.b64encode(f.read()).decode()

# ดึงเพลงปัจจุบัน และเพลงถัดไป (แค่ 2 เพลงพอ ไม่โหลดทั้ง 70)
b64_curr = get_audio_b64(music_files[idx])
next_idx = (idx + 1) % len(music_files)
b64_next = get_audio_b64(music_files[next_idx])

# 2. UI สไตล์ SYNAPSE
st.markdown(f"""
    <div style="text-align: center;">
        <h2 style='color:#00f2fe; text-shadow:0 0 10px #00f2fe; margin-bottom:0;'>✨ SYNAPSE STATION</h2>
        <p style='color:#555; font-size:12px;'>อยู่นิ่งๆ ไม่เจ็บตัว | คลังเพลง: {len(music_files)} เพลง</p>
    </div>
""", unsafe_allow_html=True)

html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {{ background: #000; color: white; font-family: sans-serif; display: flex; justify-content: center; }}
        .player-box {{
            border: 2px solid #ff007f; border-radius: 20px; padding: 20px; width: 320px;
            background: rgba(0,0,0,0.8); box-shadow: 0 0 20px #ff007f; text-align: center;
        }}
        .song-title {{ color: #00f2fe; font-size: 16px; font-weight: bold; margin: 15px 0; min-height: 40px; }}
        #timer {{ font-size: 24px; color: #ff007f; font-family: 'Courier New', monospace; }}
    </style>
</head>
<body>
    <div class="player-box">
        <div id="title" class="song-title">รอยืนยันสัญญาณ...</div>
        <i class="fas fa-compact-disc fa-spin fa-4x" style="color: #ff007f;"></i>
        <div id="timer">00:00</div>
        <div id="status" style="font-size:10px; color:#444; margin-top:10px;">READY</div>
        <button id="startBtn" onclick="start()" style="width:100%; padding:12px; margin-top:15px; background:#00f2fe; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">START STATION</button>
    </div>

    <script>
        let ctx, currS, nextS, currG, nextG, currB, nextB;
        let isFading = false;

        async function start() {{
            ctx = new (window.AudioContext || window.webkitAudioContext)();
            document.getElementById('startBtn').style.display = 'none';
            document.getElementById('status').innerText = "DECODING...";
            
            currB = await decode("{b64_curr}");
            nextB = await decode("{b64_next}");
            play();
        }}

        async function decode(b64) {{
            const res = await fetch("data:audio/mp3;base64," + b64);
            return await ctx.decodeAudioData(await res.arrayBuffer());
        }}

        function play() {{
            currS = ctx.createBufferSource();
            currS.buffer = currB;
            currG = ctx.createGain();
            currS.connect(currG).connect(ctx.destination);
            
            document.getElementById('title').innerText = "{music_files[idx]}";
            document.getElementById('status').innerText = "PLAYING NOW";
            
            currS.start(0);
            currS.t = ctx.currentTime;
            isFading = false;

            const check = setInterval(() => {{
                let rem = currS.buffer.duration - (ctx.currentTime - currS.t);
                let m = Math.floor(rem/60); let s = Math.floor(rem%60);
                document.getElementById('timer').innerText = (m<10?'0':'')+m + ":" + (s<10?'0':'')+s;

                if (rem <= 12 && !isFading) {{
                    isFading = true;
                    fade();
                    clearInterval(check);
                }}
            }}, 500);
        }}

        function fade() {{
            const dur = 12;
            const now = ctx.currentTime;
            document.getElementById('status').innerText = "CROSSFADING (12s)...";

            nextS = ctx.createBufferSource();
            nextS.buffer = nextB;
            nextG = ctx.createGain();
            nextS.connect(nextG).connect(ctx.destination);

            currG.gain.linearRampToValueAtTime(1, now);
            currG.gain.linearRampToValueAtTime(0, now + dur);
            nextG.gain.setValueAtTime(0, now);
            nextG.gain.linearRampToValueAtTime(1, now + dur);

            nextS.start(now);
            nextS.t = now;

            setTimeout(() => {{
                currS.stop();
                // สั่ง Streamlit ให้ขยับ Queue และโหลดเพลงใหม่
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'next'}}, '*');
            }}, dur * 1000);
        }}
    </script>
</body>
</html>
"""

# 3. จัดการการเปลี่ยนเพลง (Python Side)
result = components.html(html_code, height=350)

if result == 'next':
    st.session_state.current_idx = (st.session_state.current_idx + 1) % len(music_files)
    st.rerun()
