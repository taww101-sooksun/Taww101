import streamlit as st
import streamlit.components.v1 as components
import os
import random

# 1. จัดการคิวเพลง (Shuffle แค่ครั้งแรกที่เปิดแอป)
if 'shuffled_list' not in st.session_state:
    files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    random.shuffle(files)
    st.session_state.shuffled_list = files
    st.session_state.current_idx = 0

music_files = st.session_state.shuffled_list
idx = st.session_state.current_idx

# เตรียมชื่อไฟล์เพลงปัจจุบันและเพลงถัดไป (ส่งแค่ชื่อ ไม่ส่ง Base64 แล้ว)
current_song_name = music_files[idx]
next_idx = (idx + 1) % len(music_files)
next_song_name = music_files[next_idx]

# 2. UI แบบ SYNAPSE DJ DUO
st.markdown(f"""
    <div style="text-align: center;">
        <h2 style='color:#00f2fe; text-shadow:0 0 10px #00f2fe; margin-bottom:0;'>🎧 SYNAPSE DJ DUO</h2>
        <p style='color:#555; font-size:12px;'>คิวที่: {idx + 1} / {len(music_files)} | "อยู่นิ่งๆ ไม่เจ็บตัว"</p>
    </div>
""", unsafe_allow_html=True)

# 3. ส่วนประกอบของเครื่องเล่น (HTML/JS)
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {{ background: #000; color: white; font-family: sans-serif; margin:0; padding:10px; overflow: hidden; }}
        .dj-container {{ display: flex; gap: 10px; justify-content: center; }}
        .deck {{
            flex: 1; border: 2px solid #333; border-radius: 15px; padding: 15px;
            background: #111; transition: 0.5s; text-align: center;
        }}
        .active-deck {{ border-color: #00f2fe; box-shadow: 0 0 15px #00f2fe; }}
        .next-deck {{ border-color: #ff007f; opacity: 0.5; }}
        .label {{ font-size: 10px; color: #555; font-weight: bold; }}
        .song-title {{ font-size: 12px; height: 36px; overflow: hidden; margin: 10px 0; color: #eee; line-height: 1.2; }}
        .timer {{ font-size: 20px; font-family: monospace; color: #ff007f; }}
        #startBtn {{ 
            width: 100%; padding: 15px; background: #00f2fe; border: none; 
            border-radius: 10px; font-weight: bold; margin-top: 15px; cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="dj-container">
        <div id="deckA" class="deck active-deck">
            <div class="label">DECK A (Playing)</div>
            <div id="titleA" class="song-title">{current_song_name}</div>
            <i class="fas fa-compact-disc fa-spin fa-3x" id="iconA" style="color: #00f2fe; margin: 10px 0;"></i>
            <div id="timerA" class="timer">00:00</div>
        </div>
        <div id="deckB" class="deck next-deck">
            <div class="label">DECK B (Next)</div>
            <div id="titleB" class="song-title">{next_song_name}</div>
            <i class="fas fa-compact-disc fa-spin fa-3x" id="iconB" style="color: #ff007f; margin: 10px 0;"></i>
            <div id="timerB" class="timer">--:--</div>
        </div>
    </div>
    <button id="startBtn" onclick="initDJ()">START STATION</button>

    <script>
        let ctx, deckA={{}}, deckB={{}};
        let isFading = false;

        async function decode(filename) {{
            try {{
                // ดึงไฟล์ผ่าน URL ตรงๆ (ประหยัดแรมกว่า Base64 มหาศาล)
                const res = await fetch("./" + filename);
                const arrayBuffer = await res.arrayBuffer();
                return await ctx.decodeAudioData(arrayBuffer);
            }} catch(e) {{
                console.error("Load error:", e);
                return null;
            }}
        }}

        async function initDJ() {{
            ctx = new (window.AudioContext || window.webkitAudioContext)();
            document.getElementById('startBtn').innerText = "LOADING PEAK DATA...";
            
            // โหลดเพลงเข้า Deck
            deckA.buffer = await decode("{current_song_name}");
            deckB.buffer = await decode("{next_song_name}");
            
            document.getElementById('startBtn').style.display = 'none';
            playDeckA();
        }}

        function playDeckA() {{
            if(!deckA.buffer) return;
            deckA.src = ctx.createBufferSource();
            deckA.src.buffer = deckA.buffer;
            deckA.gain = ctx.createGain();
            deckA.src.connect(deckA.gain).connect(ctx.destination);
            
            deckA.src.start(0);
            deckA.startTime = ctx.currentTime;
            isFading = false;
            
            monitor(deckA, 'A');
        }}

        function monitor(deck, type) {{
            const updater = setInterval(() => {{
                let rem = deck.buffer.duration - (ctx.currentTime - deck.startTime);
                let m = Math.floor(rem/60); let s = Math.floor(rem%60);
                document.getElementById('timer' + type).innerText = (m<10?'0':'')+m + ":" + (s<10?'0':'')+s;

                // ระบบ Auto-Crossfade 12 วินาทีสุดท้าย
                if (rem <= 12 && !isFading) {{
                    isFading = true;
                    crossfade();
                    clearInterval(updater);
                }}
            }}, 1000);
        }}

        function crossfade() {{
            const dur = 12;
            const now = ctx.currentTime;
            
            if(!deckB.buffer) return;
            deckB.src = ctx.createBufferSource();
            deckB.src.buffer = deckB.buffer;
            deckB.gain = ctx.createGain();
            deckB.src.connect(deckB.gain).connect(ctx.destination);

            // ค่อยๆ ลด Deck A และเพิ่ม Deck B
            deckA.gain.gain.linearRampToValueAtTime(1, now);
            deckA.gain.gain.linearRampToValueAtTime(0, now + dur);
            deckB.gain.gain.setValueAtTime(0, now);
            deckB.gain.gain.linearRampToValueAtTime(1, now + dur);

            deckB.src.start(now);
            deckB.startTime = now;

            // สลับสถานะ UI
            document.getElementById('deckA').classList.replace('active-deck', 'next-deck');
            document.getElementById('deckB').classList.replace('next-deck', 'active-deck');

            setTimeout(() => {{
                deckA.src.stop();
                // ส่งคำสั่งไป Python เพื่อเปลี่ยนคิวเพลงถัดไป
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'next'}}, '*');
            }}, dur * 1000);
        }}
    </script>
</body>
</html>
"""

# 4. รับค่าจาก JS เพื่อขยับคิวเพลง
result = components.html(html_code, height=300)

if result == 'next':
    st.session_state.current_idx = (st.session_state.current_idx + 1) % len(music_files)
    st.rerun()
