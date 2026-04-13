import streamlit as st
import streamlit.components.v1 as components
import os
import random

# --- 1. จัดการคิวเพลง ---
if 'shuffled_list' not in st.session_state:
    # สแกนหาเพลง .mp3 ทั้งหมด
    files = [f for f in os.listdir('.') if f.endswith(".mp3")]
    random.shuffle(files)
    st.session_state.shuffled_list = files
    st.session_state.current_idx = 0

music_files = st.session_state.shuffled_list
idx = st.session_state.current_idx

# เตรียมชื่อไฟล์
current_song = music_files[idx]
next_song = music_files[(idx + 1) % len(music_files)]

# --- 2. UI ---
st.title("🎧 SYNAPSE DJ DUO")
st.write(f"กำลังเล่น: {current_song}")

# --- 3. HTML/JS (ตัวแก้บั๊กตายเพลงแรก) ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body class="bg-black text-white p-4">
    <div class="flex gap-4 justify-center">
        <div id="deckA" class="border-2 border-cyan-400 p-6 rounded-xl text-center w-40">
            <p class="text-[10px] text-gray-500">DECK A</p>
            <i class="fas fa-compact-disc fa-spin fa-3x my-4 text-cyan-400"></i>
            <div id="timerA" class="text-xl font-mono text-pink-500">00:00</div>
        </div>
        <div id="deckB" class="border-2 border-gray-800 p-6 rounded-xl text-center w-40 opacity-50">
            <p class="text-[10px] text-gray-500">DECK B</p>
            <i class="fas fa-compact-disc fa-spin fa-3x my-4 text-pink-500"></i>
            <div id="timerB" class="text-xl font-mono">--:--</div>
        </div>
    </div>

    <button id="startBtn" onclick="initDJ()" class="w-full mt-6 bg-cyan-500 py-3 rounded-lg font-bold text-black">
        START STATION
    </button>

    <script>
        let ctx, deckA={{}}, deckB={{}}, isFading = false;

        async function decode(filename) {{
            try {{
                // เคล็ดลับ: ใช้ Path ตรงๆ ถ้าไฟล์อยู่ใน GitHub root
                // หรือถ้าไม่ได้ผล ให้ลองใช้ Base64 เฉพาะเพลงที่ "กำลังจะเล่น" เท่านั้น
                const response = await fetch(filename);
                const arrayBuffer = await response.arrayBuffer();
                return await ctx.decodeAudioData(arrayBuffer);
            }} catch (e) {{
                console.error("Error loading song:", e);
                // ถ้า fetch ไม่ติด ให้ส่งสัญญาณบอก Python
                return null;
            }}
        }}

        async function initDJ() {{
            ctx = new (window.AudioContext || window.webkitAudioContext)();
            document.getElementById('startBtn').innerText = "LOADING...";
            
            // โหลดเพลง
            deckA.buffer = await decode("{current_song}");
            deckB.buffer = await decode("{next_song}");
            
            if(!deckA.buffer) {{
                alert("หาไฟล์เพลงไม่เจอ หรือเบราว์เซอร์บล็อกการโหลดครับเพื่อน");
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
                if (rem > 0) {{
                    let m = Math.floor(rem/60); let s = Math.floor(rem%60);
                    document.getElementById('timerA').innerText = (m<10?'0':'')+m + ":" + (s<10?'0':'')+s;
                }}
                
                // 12 วินาทีสุดท้าย ทำ Crossfade
                if (rem <= 12 && !isFading) {{
                    isFading = true;
                    fadeToB();
                }}
            }}, 1000);
        }}

        function fadeToB() {{
            const now = ctx.currentTime;
            deckB.src = ctx.createBufferSource();
            deckB.src.buffer = deckB.buffer;
            deckB.gain = ctx.createGain();
            deckB.src.connect(deckB.gain).connect(ctx.destination);
            
            deckA.gain.gain.linearRampToValueAtTime(1, now);
            deckA.gain.gain.linearRampToValueAtTime(0, now + 12);
            deckB.gain.gain.setValueAtTime(0, now);
            deckB.gain.gain.linearRampToValueAtTime(1, now + 12);
            
            deckB.src.start(now);
            
            setTimeout(() => {{
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'next'}}, '*');
            }}, 12000);
        }}
    </script>
</body>
</html>
"""

result = components.html(html_code, height=350)
if result == 'next':
    st.session_state.current_idx = (st.session_state.current_idx + 1) % len(music_files)
    st.rerun()
