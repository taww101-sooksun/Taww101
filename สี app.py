import streamlit as st
import streamlit.components.v1 as components
import os
import random
import base64

# 1. จัดการคิวเพลงใน Session State
if 'shuffled_list' not in st.session_state:
    files = [f for f in os.listdir('.') if f.endswith(".mp3")]
    random.shuffle(files)
    st.session_state.shuffled_list = files
    st.session_state.current_idx = 0

music_files = st.session_state.shuffled_list
idx = st.session_state.current_idx

def get_audio_b64(filename):
    with open(filename, "rb") as f:
        return base64.b64encode(f.read()).decode()

# โหลดเฉพาะเพลงที่ต้องเล่นตอนนี้ (เพลงเดียวพอ เพื่อไม่ให้กองรวมกัน)
b64_curr = get_audio_b64(music_files[idx])
# เพลงถัดไปจะถูกส่งไปแค่ชื่อก่อน แล้วให้ JS ไปขอตอนจะ Fade
next_idx = (idx + 1) % len(music_files)
b64_next = get_audio_b64(music_files[next_idx])

# 2. UI แบบแยก Deck ชัดเจน
st.markdown(f"<h3 style='text-align:center; color:#00f2fe;'>🎧 SYNAPSE DJ STATION</h3>", unsafe_allow_html=True)

html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ background: #000; color: white; font-family: sans-serif; text-align: center; }}
        .container {{ display: flex; gap: 10px; justify-content: center; }}
        .deck {{ flex: 1; border: 2px solid #333; border-radius: 15px; padding: 10px; background: #111; }}
        .active {{ border-color: #00f2fe; box-shadow: 0 0 10px #00f2fe; }}
        .song-name {{ font-size: 10px; color: #888; height: 30px; }}
        #startBtn {{ width: 100%; padding: 15px; background: #00f2fe; border: none; border-radius: 10px; font-weight: bold; margin-top: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div id="deckA" class="deck active">
            <div class="song-name">{music_files[idx]}</div>
            <div id="timerA" style="font-size: 20px; color: #ff007f;">00:00</div>
        </div>
        <div id="deckB" class="deck">
            <div class="song-name">{music_files[next_idx]}</div>
            <div id="timerB" style="font-size: 20px;">--:--</div>
        </div>
    </div>
    <button id="startBtn" onclick="initDJ()">เริ่มสถานีเพลง (Start)</button>

    <script>
        let ctx, currS, nextS, currG, nextG, currB, nextB;
        let isFading = false;

        async function initDJ() {{
            ctx = new (window.AudioContext || window.webkitAudioContext)();
            document.getElementById('startBtn').innerText = "DECODING...";
            
            // โหลดเพลงปัจจุบันเข้า Deck A
            currB = await decode("{b64_curr}");
            // โหลดเพลงถัดไปเข้า Deck B รอไว้เลย (แต่ยังไม่เล่น)
            nextB = await decode("{b64_next}");
            
            document.getElementById('startBtn').style.display = 'none';
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
            currS.start(0);
            currS.startTime = ctx.currentTime;

            setInterval(() => {{
                let rem = currS.buffer.duration - (ctx.currentTime - currS.startTime);
                let m = Math.floor(rem/60); let s = Math.floor(rem%60);
                document.getElementById('timerA').innerText = (m<10?'0':'')+m + ":" + (s<10?'0':'')+s;

                // เมื่อเหลือ 12 วินาที สั่ง Crossfade
                if (rem <= 12 && !isFading) {{
                    isFading = true;
                    startCrossfade();
                }}
            }}, 1000);
        }}

        function startCrossfade() {{
            const now = ctx.currentTime;
            nextS = ctx.createBufferSource();
            nextS.buffer = nextB;
            nextG = ctx.createGain();
            nextS.connect(nextG).connect(ctx.destination);

            // Crossfade 12 วินาที
            currG.gain.linearRampToValueAtTime(1, now);
            currG.gain.linearRampToValueAtTime(0, now + 12);
            nextG.gain.setValueAtTime(0, now);
            nextG.gain.linearRampToValueAtTime(1, now + 12);

            nextS.start(now);
            document.getElementById('deckA').classList.remove('active');
            document.getElementById('deckB').classList.add('active');

            setTimeout(() => {{
                currS.stop();
                // ส่งค่ากลับไป Python เพื่อเปลี่ยนเพลงใน Session State
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'next'}}, '*');
            }}, 12000);
        }}
    </script>
</body>
</html>
"""

# 3. ส่วนรับคำสั่งเปลี่ยนเพลง
result = components.html(html_code, height=250)
if result == 'next':
    st.session_state.current_idx = (st.session_state.current_idx + 1) % len(music_files)
    st.rerun()
