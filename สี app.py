import streamlit as st  # แก้จาก Import เป็น import
import streamlit.components.v1 as components
import os
import random

# 1. จัดการคิวเพลง (ใช้ Session State ล็อกลำดับไว้)
if 'shuffled_list' not in st.session_state:
    files = [f for f in os.listdir('.') if f.endswith(".mp3")]
    random.shuffle(files)
    st.session_state.shuffled_list = files
    st.session_state.current_idx = 0

music_files = st.session_state.shuffled_list
idx = st.session_state.current_idx

current_song = music_files[idx]
next_song = music_files[(idx + 1) % len(music_files)]

# 2. UI
st.markdown(f"<h3 style='text-align:center; color:#00f2fe; margin-bottom:10px;'>🎧 SYNAPSE DJ STATION</h3>", unsafe_allow_html=True)

# 3. HTML/JS (ฉบับแก้เลขซ้อน + ชื่อไทย)
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ background: #000; color: white; font-family: sans-serif; margin: 0; padding: 10px; overflow: hidden; }}
        .lyrics-zone {{
            height: 45px; margin-bottom: 15px; overflow: hidden; position: relative;
            background: linear-gradient(90deg, transparent, rgba(0,242,254,0.1), transparent);
            border-radius: 10px; display: flex; align-items: center; border: 1px solid #222;
        }}
        .scrolling-text {{
            white-space: nowrap; position: absolute; font-weight: bold; color: #00f2fe;
            text-shadow: 0 0 10px #00f2fe; font-size: 16px; animation: scroll-left 20s linear infinite;
        }}
        @keyframes scroll-left {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
        .dj-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
        .deck {{ border: 2px solid #333; border-radius: 15px; padding: 20px 5px; background: #111; text-align: center; transition: 0.5s; }}
        .active {{ border-color: #00f2fe; box-shadow: 0 0 20px rgba(0,242,254,0.4); }}
        .timer {{ font-size: 28px; font-family: 'Courier New', monospace; color: #ff007f; margin-top: 10px; text-shadow: 0 0 5px #ff007f; }}
        .song-label {{ font-size: 11px; color: #666; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; padding: 0 5px; }}
        #startBtn {{ width: 100%; padding: 18px; background: #00f2fe; border: none; border-radius: 12px; font-weight: bold; margin-top: 20px; cursor: pointer; color: #000; font-size: 16px; }}
    </style>
</head>
<body>
    <div class="lyrics-zone">
        <div class="scrolling-text">🎵 กำลังเล่น: {current_song} — "อยู่นิ่งๆ ไม่เจ็บตัว" 🎵</div>
    </div>

    <div class="dj-grid">
        <div id="deckA" class="deck active">
            <div class="song-label">DECK A (PLAYING)</div>
            <div class="song-label" style="color:#00f2fe;">{current_song}</div>
            <div id="timerA" class="timer">00:00</div>
        </div>
        <div id="deckB" class="deck" style="opacity: 0.4;">
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
                const safePath = "./" + encodeURIComponent(filename);
                const res = await fetch(safePath);
                if(!res.ok) throw new Error("404");
                const arrayBuffer = await res.arrayBuffer();
                return await ctx.decodeAudioData(arrayBuffer);
            }} catch(e) {{ 
                console.error("Fail:", filename);
                return null; 
            }}
        }}

        async function initDJ() {{
            ctx = new (window.AudioContext || window.webkitAudioContext)();
            document.getElementById('startBtn').innerText = "SYNAPSE IS LOADING...";
            
            deckA.buffer = await decode("{current_song}");
            deckB.buffer = await decode("{next_song}");
            
            if (!deckA.buffer) {{
                document.getElementById('startBtn').innerText = "ERROR: หาไฟล์ไม่เจอ!";
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
                    document.getElementById('timerA').innerText = 
                        (m < 10 ? '0' : '') + m + ":" + (s < 10 ? '0' : '') + s;
                }}

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
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'next'}}, '*');
            }}, 12000);
        }}
    </script>
</body>
</html>
"""

result = components.html(html_code, height=380)

if result == 'next':
    st.session_state.current_idx = (st.session_state.current_idx + 1) % len(music_files)
    st.rerun()
