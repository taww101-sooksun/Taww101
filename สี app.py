import streamlit as st
import streamlit.components.v1 as components
import os
import random

# 1. จัดการคิวเพลง
if 'shuffled_list' not in st.session_state:
    files = [f for f in os.listdir('.') if f.endswith(".mp3")]
    random.shuffle(files)
    st.session_state.shuffled_list = files
    st.session_state.current_idx = 0

music_files = st.session_state.shuffled_list
idx = st.session_state.current_idx

current_song = music_files[idx]
next_song = music_files[(idx + 1) % len(music_files)]

# 2. UI หัวข้อ
st.markdown(f"<h3 style='text-align:center; color:#00f2fe; margin-bottom:0;'>🎧 SYNAPSE DJ STATION</h3>", unsafe_allow_html=True)

# 3. HTML/JS (ฉบับสมบูรณ์: แก้ชื่อไฟล์ภาษาไทย + ระบบเล่นเพลง)
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ background: #000; color: white; font-family: sans-serif; margin: 0; padding: 5px; overflow: hidden; }}
        .lyrics-zone {{
            height: 45px; margin-bottom: 10px; overflow: hidden; position: relative;
            background: linear-gradient(90deg, transparent, rgba(0,242,254,0.1), transparent);
            border-radius: 10px; display: flex; align-items: center;
        }}
        .scrolling-text {{
            white-space: nowrap; position: absolute; font-weight: bold; color: #00f2fe;
            text-shadow: 0 0 10px #00f2fe; font-size: 16px; animation: scroll-left 15s linear infinite;
        }}
        @keyframes scroll-left {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
        .dj-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
        .deck {{ border: 1.5px solid #333; border-radius: 12px; padding: 15px 5px; background: #111; text-align: center; transition: 0.5s; }}
        .active {{ border-color: #00f2fe; box-shadow: 0 0 15px rgba(0,242,254,0.5); }}
        .timer {{ font-size: 24px; font-family: monospace; color: #ff007f; margin-top: 5px; }}
        .song-label {{ font-size: 10px; color: #666; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; padding: 0 5px; }}
        #startBtn {{ width: 100%; padding: 15px; background: #00f2fe; border: none; border-radius: 10px; font-weight: bold; margin-top: 15px; cursor: pointer; color: #000; }}
    </style>
</head>
<body>
    <div class="lyrics-zone">
        <div class="scrolling-text">🎵 กำลังเล่น: {current_song} — SYNAPSE STATION — "อยู่นิ่งๆ ไม่เจ็บตัว" 🎵</div>
    </div>

    <div class="dj-grid">
        <div id="deckA" class="deck active">
            <div class="song-label">DECK A (PLAY)</div>
            <div class="song-label" style="color:#00f2fe;">{current_song}</div>
            <div id="timerA" class="timer">00:00</div>
        </div>
        <div id="deckB" class="deck" style="opacity: 0.5;">
            <div class="song-label">DECK B (NEXT)</div>
            <div class="song-label" style="color:#ff007f;">{next_song}</div>
            <div id="timerB" class="timer">--:--</div>
        </div>
    </div>

    <button id="startBtn" onclick="initDJ()">TAP TO START SYSTEM</button>

    <script>
        let ctx, deckA={{}}, deckB={{}}, isFading = false;

        async function decode(filename) {{
            try {{
                // แก้ปัญหาไฟล์ภาษาไทยด้วย encodeURIComponent
                const res = await fetch("./" + encodeURIComponent(filename));
                const arrayBuffer = await res.arrayBuffer();
                return await ctx.decodeAudioData(arrayBuffer);
            }} catch(e) {{ 
                console.error("Load error", e);
                return null; 
            }}
        }}

        async function initDJ() {{
            ctx = new (window.AudioContext || window.webkitAudioContext)();
            document.getElementById('startBtn').innerText = "LOADING PEAK DATA...";
            
            // โหลดทั้งสองเพลงเข้าหน่วยความจำ
            deckA.buffer = await decode("{current_song}");
            deckB.buffer = await decode("{next_song}");
            
            if (!deckA.buffer) {{
                document.getElementById('startBtn').innerText = "หาไฟล์ไม่เจอ หรือโหลดไม่ได้";
                return;
            }}

            document.getElementById('startBtn').style.display = 'none';
            play();
        }}

        function play() {{
            deckA.src = ctx.createBufferSource();
            deckA.src.buffer = deckA.buffer;
            deckA.gain = ctx.createGain();
            deckA.src.connect(deckA.gain).connect(ctx.destination);
            
            deckA.src.start(0);
            deckA.startTime = ctx.currentTime;

            setInterval(() => {{
                let rem = deckA.buffer.duration - (ctx.currentTime - deckA.startTime);
                if(rem > 0) {{
                    let m = Math.floor(rem/60); let s = Math.floor(rem%60);
                    document.getElementById('timerA').innerText = String(m).padStart(2,'0')+":"+String(s).padStart(2,'0');
                }}

                // Crossfade 12 วินาทีสุดท้าย
                if (rem <= 12 && !isFading) {{
                    isFading = true;
                    fade();
                }}
            }}, 1000);
        }}

        function fade() {{
            const now = ctx.currentTime;
            if(!deckB.buffer) return;
            
            deckB.src = ctx.createBufferSource();
            deckB.src.buffer = deckB.buffer;
            deckB.gain = ctx.createGain();
            deckB.src.connect(deckB.gain).connect(ctx.destination);

            deckA.gain.gain.linearRampToValueAtTime(1, now);
            deckA.gain.gain.linearRampToValueAtTime(0, now + 12);
            deckB.gain.gain.setValueAtTime(0, now);
            deckB.gain.gain.linearRampToValueAtTime(1, now + 12);

            deckB.src.start(now);
            document.getElementById('deckB').style.opacity = "1";
            document.getElementById('deckB').classList.add('active');

            setTimeout(() => {{
                // ส่งคำสั่งไป Python เพื่อเปลี่ยนเพลงในลำดับถัดไป
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'next'}}, '*');
            }}, 12000);
        }}
    </script>
</body>
</html>
"""

# 4. รับค่าเปลี่ยนเพลง
result = components.html(html_code, height=350)

if result == 'next':
    st.session_state.current_idx = (st.session_state.current_idx + 1) % len(music_files)
    st.rerun()
