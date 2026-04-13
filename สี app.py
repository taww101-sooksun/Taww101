import streamlit as st
import streamlit.components.v1 as components
import os
import random
import base64

# 1. จัดการคิวเพลง
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

# เตรียมเพลงสำหรับ 2 เครื่อง
b64_curr = get_audio_b64(music_files[idx])
next_idx = (idx + 1) % len(music_files)
b64_next = get_audio_b64(music_files[next_idx])

# 2. UI แบบ 2 เครื่อง
st.markdown("""
    <div style="text-align: center;">
        <h2 style='color:#00f2fe; text-shadow:0 0 10px #00f2fe; margin-bottom:0;'>🎧 SYNAPSE DJ DUO</h2>
        <p style='color:#555; font-size:12px;'>Deck A & Deck B | Crossfade 12s</p>
    </div>
""", unsafe_allow_html=True)

html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {{ background: #000; color: white; font-family: sans-serif; margin:0; padding:10px; }}
        .dj-container {{ display: flex; gap: 10px; justify-content: center; }}
        .deck {{
            flex: 1; border: 2px solid #333; border-radius: 15px; padding: 15px;
            background: #111; transition: 0.5s; text-align: center;
        }}
        .active-deck {{ border-color: #00f2fe; box-shadow: 0 0 15px #00f2fe; }}
        .next-deck {{ border-color: #ff007f; opacity: 0.6; }}
        .label {{ font-size: 10px; color: #555; font-weight: bold; }}
        .song-title {{ font-size: 12px; height: 30px; overflow: hidden; margin: 10px 0; color: #eee; }}
        .timer {{ font-size: 20px; font-family: monospace; color: #ff007f; }}
        #startBtn {{ 
            width: 100%; padding: 15px; background: #00f2fe; border: none; 
            border-radius: 10px; font-weight: bold; margin-top: 15px; 
        }}
    </style>
</head>
<body>
    <div class="dj-container">
        <div id="deckA" class="deck active-deck">
            <div class="label">DECK A</div>
            <div id="titleA" class="song-title">READY</div>
            <i class="fas fa-compact-disc fa-spin fa-3x" id="iconA" style="color: #00f2fe; display:none;"></i>
            <div id="timerA" class="timer">00:00</div>
        </div>

        <div id="deckB" class="deck next-deck">
            <div class="label">DECK B</div>
            <div id="titleB" class="song-title">WAITING...</div>
            <i class="fas fa-compact-disc fa-spin fa-3x" id="iconB" style="color: #ff007f; display:none;"></i>
            <div id="timerB" class="timer">00:00</div>
        </div>
    </div>

    <button id="startBtn" onclick="initDJ()">START DJ SYSTEM</button>

    <script>
        let ctx, deckA={{}}, deckB={{}};
        let currentDeck = 'A';
        let isFading = false;

        async function initDJ() {{
            ctx = new (window.AudioContext || window.webkitAudioContext)();
            document.getElementById('startBtn').style.display = 'none';
            document.getElementById('iconA').style.display = 'inline-block';
            document.getElementById('iconB').style.display = 'inline-block';
            
            // โหลดเพลงเข้า Deck
            deckA.buffer = await decode("{b64_curr}");
            deckB.buffer = await decode("{b64_next}");
            
            document.getElementById('titleA').innerText = "{music_files[idx]}";
            document.getElementById('titleB').innerText = "{music_files[next_idx]}";
            
            playDeckA();
        }}

        async function decode(b64) {{
            const res = await fetch("data:audio/mp3;base64," + b64);
            return await ctx.decodeAudioData(await res.arrayBuffer());
        }}

        function playDeckA() {{
            deckA.src = ctx.createBufferSource();
            deckA.src.buffer = deckA.buffer;
            deckA.gain = ctx.createGain();
            deckA.src.connect(deckA.gain).connect(ctx.destination);
            
            deckA.src.start(0);
            deckA.startTime = ctx.currentTime;
            
            monitor(deckA, 'A');
        }}

        function monitor(deck, type) {{
            const updater = setInterval(() => {{
                let rem = deck.buffer.duration - (ctx.currentTime - deck.startTime);
                let m = Math.floor(rem/60); let s = Math.floor(rem%60);
                document.getElementById('timer' + type).innerText = (m<10?'0':'')+m + ":" + (s<10?'0':'')+s;

                if (rem <= 12 && !isFading) {{
                    isFading = true;
                    crossfade();
                    clearInterval(updater);
                }}
            }}, 500);
        }}

        function crossfade() {{
            const dur = 12;
            const now = ctx.currentTime;
            
            // เริ่ม Deck B
            deckB.src = ctx.createBufferSource();
            deckB.src.buffer = deckB.buffer;
            deckB.gain = ctx.createGain();
            deckB.src.connect(deckB.gain).connect(ctx.destination);

            // Crossfade Logic
            deckA.gain.gain.linearRampToValueAtTime(1, now);
            deckA.gain.gain.linearRampToValueAtTime(0, now + dur);
            
            deckB.gain.gain.setValueAtTime(0, now);
            deckB.gain.gain.linearRampToValueAtTime(1, now + dur);

            deckB.src.start(now);
            deckB.startTime = now;

            // ปรับ UI
            document.getElementById('deckA').classList.replace('active-deck', 'next-deck');
            document.getElementById('deckB').classList.replace('next-deck', 'active-deck');

            setTimeout(() => {{
                deckA.src.stop();
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'next'}}, '*');
            }}, dur * 1000);
        }}
    </script>
</body>
</html>
"""

# 3. จัดการการเปลี่ยนเพลง
result = components.html(html_code, height=300)

if result == 'next':
    st.session_state.current_idx = (st.session_state.current_idx + 1) % len(music_files)
    st.rerun()
