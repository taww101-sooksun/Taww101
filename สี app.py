html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ background: #000; color: white; font-family: sans-serif; margin: 0; padding: 5px; overflow: hidden; }}
        
        /* สไตล์เนื้อเพลง/ชื่อเพลงไหล */
        .lyrics-zone {{
            height: 60px; margin-bottom: 15px; overflow: hidden; position: relative;
            background: linear-gradient(180deg, transparent, rgba(0,242,254,0.1), transparent);
            border-radius: 10px; display: flex; align-items: center; justify-content: center;
        }}
        .scrolling-text {{
            white-space: nowrap; position: absolute; font-weight: bold; color: #00f2fe;
            text-shadow: 0 0 10px #00f2fe; font-size: 18px;
            animation: scroll-left 15s linear infinite;
        }}
        @keyframes scroll-left {{
            0% {{ transform: translateX(100%); }}
            100% {{ transform: translateX(-100%); }}
        }}

        /* ปรับ Deck ไม่ให้กองรวมกัน */
        .dj-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
        .deck {{
            border: 1.5px solid #333; border-radius: 12px; padding: 12px 5px;
            background: #111; text-align: center; min-height: 100px;
        }}
        .active {{ border-color: #00f2fe; box-shadow: 0 0 12px rgba(0,242,254,0.4); }}
        .timer {{ font-size: 22px; font-family: 'Courier New', monospace; color: #ff007f; margin-top: 10px; }}
        .song-label {{ font-size: 10px; color: #666; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
        
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
            <div id="titleA" class="song-label" style="color:#aaa;">{current_song_name}</div>
            <div id="timerA" class="timer">00:00</div>
        </div>
        <div id="deckB" class="deck">
            <div class="song-label">DECK B</div>
            <div id="titleB" class="song-label" style="color:#aaa;">{next_song_name}</div>
            <div id="timerB" class="timer">--:--</div>
        </div>
    </div>

    <button id="startBtn" onclick="initDJ()">TAP TO START SYSTEM</button>

    <script>
        // ... (Logic การเล่นเพลงเหมือนเดิม แต่ปรับการแสดงผลเวลา) ...
        function updateTimerDisplay(rem, type) {{
            if (rem < 0) rem = 0;
            let m = Math.floor(rem / 60);
            let s = Math.floor(rem % 60);
            // แก้ปัญหาเลขซ้อนกัน โดยบังคับฟอร์แมต 00:00
            document.getElementById('timer' + type).innerText = 
                String(m).padStart(2, '0') + ":" + String(s).padStart(2, '0');
        }}
        // ในส่วน setInterval ให้เรียกใช้ updateTimerDisplay(rem, 'A') แทนการเขียน format เอง
    </script>
</body>
</html>
"""
