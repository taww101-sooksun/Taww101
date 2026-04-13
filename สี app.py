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

current_song_name = music_files[idx]
next_song_name = music_files[(idx + 1) % len(music_files)]

# 2. UI ด้านบน
st.markdown(f"<h2 style='text-align:center; color:#00f2fe;'>🎧 SYNAPSE DJ STATION</h2>", unsafe_allow_html=True)

# 3. HTML/JS (แก้จุดปีกกาที่เป็น CSS ให้เป็น {{ }})
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ background: #000; color: white; font-family: sans-serif; margin: 0; padding: 5px; overflow: hidden; }}
        
        .lyrics-zone {{
            height: 50px; margin-bottom: 10px; overflow: hidden; position: relative;
            background: linear-gradient(90deg, transparent, rgba(0,242,254,0.1), transparent);
            border-radius: 10px; display: flex; align-items: center;
        }}
        
        .scrolling-text {{
            white-space: nowrap; position: absolute; font-weight: bold; color: #00f2fe;
            text-shadow: 0 0 10px #00f2fe; font-size: 16px;
            animation: scroll-left 15s linear infinite;
        }}
        
        @keyframes scroll-left {{
            0% {{ transform: translateX(100%); }}
            100% {{ transform: translateX(-100%); }}
        }}

        .dj-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
        
        .deck {{
            border: 1.5px solid #333; border-radius: 12px; padding: 15px 5px;
            background: #111; text-align: center;
        }}
        
        .active {{ border-color: #00f2fe; box-shadow: 0 0 15px rgba(0,242,254,0.5); }}
        
        .timer {{ font-size: 24px; font-family: monospace; color: #ff007f; margin-top: 5px; }}
        
        .song-label {{ font-size: 10px; color: #666; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; padding: 0 5px; }}
        
        #startBtn {{ 
            width: 100%; padding: 12px; background: #00f2fe; border: none; 
            border-radius: 8px; font-weight: bold; margin-top: 15px; color: #000;
        }}
    </style>
</head>
<body>
    <div class="lyrics-zone">
        <div class="scrolling-text">🎵 กำลังเล่น: {current_song_name} — SYNAPSE STATION — "อยู่นิ่งๆ ไม่เจ็บตัว" 🎵</div>
    </div>

    <div class="dj-grid">
        <div id="deckA" class="deck active">
            <div class="song-label">DECK A</div>
            <div class="song-label" style="color:#00f2fe;">{current_song_name}</div>
            <div id="timerA" class="timer">00:00</div>
        </div>
        <div id="deckB" class="deck">
            <div class="song-label">DECK B</div>
            <div class="song-label" style="color:#ff007f;">{next_song_name}</div>
            <div id="timerB" class="timer">--:--</div>
        </div>
    </div>

    <button id="startBtn" onclick="initDJ()">TAP TO START SYSTEM</button>

    <script>
        // ใส่ Logic การเล่นเพลงและ Fetch ไฟล์ที่คุณมีอยู่ตรงนี้
        // อย่าลืมเปลี่ยนจาก Base64 เป็น Fetch ตามที่คุยกันเพื่อความลื่นไหล
        function initDJ() {{
            alert("ระบบ SYNAPSE พร้อมรันเพลง: {current_song_name}");
            // โค้ดเล่นเพลงของคุณ...
        }}
    </script>
</body>
</html>
"""

# 4. แสดงผลแอป
result = components.html(html_code, height=350)
