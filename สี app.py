import streamlit as st
import streamlit.components.v1 as components
import os
import random
import base64

# 1. ตั้งค่าหน้าจอ
st.set_page_config(layout="wide", page_title="SYNAPSE Non-Stop")

# 2. สแกนและสุ่มเพลง (Shuffle)
music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
random.shuffle(music_files)

def get_audio_b64(filename):
    with open(filename, "rb") as f:
        return base64.b64encode(f.read()).decode()

if not music_files:
    st.error("ไม่พบไฟล์เพลงใน GitHub ครับ")
    st.stop()

# เตรียม 2 เพลงแรกส่งเข้าไปในระบบก่อน
b64_1 = get_audio_b64(music_files[0])
b64_2 = get_audio_b64(music_files[1]) if len(music_files) > 1 else b64_1

# 3. UI และระบบเล่นเพลงอัตโนมัติ
st.markdown(f"""
    <h2 style='color:#00f2fe; text-shadow:0 0 10px #00f2fe;'>✨ SYNAPSE AUTO-STATION</h2>
    <p style='color:gray;'>กำลังเล่นแบบสุ่มจากคลัง {len(music_files)} เพลง</p>
""", unsafe_allow_html=True)

html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body {{ background: #000; color: white; font-family: sans-serif; text-align: center; }}
        .player-box {{
            border: 2px solid #ff007f; border-radius: 20px; padding: 30px;
            background: rgba(255, 0, 127, 0.1); box-shadow: 0 0 20px #ff007f;
        }}
        .song-name {{ font-size: 20px; font-weight: bold; color: #00f2fe; margin-bottom: 20px; }}
        .status {{ font-size: 12px; color: #555; }}
    </style>
</head>
<body>
    <div class="player-box">
        <div id="title" class="song-name">เตรียมความพร้อม...</div>
        <div id="status" class="status">รอสัญญาณจากระบบ</div>
        <i class="fas fa-compact-disc fa-spin fa-5x" style="margin: 20px 0; color: #ff007f;"></i>
        <div id="timer" style="font-family: monospace;">00:00</div>
        <button id="startBtn" onclick="initPlayer()" style="width:100%; padding:15px; border-radius:10px; border:none; background:#00f2fe; color:black; font-weight:bold; margin-top:20px;">เริ่มสถานีเพลงต่อเนื่อง</button>
    </div>

    <script>
        let audioCtx, currSrc, nextSrc, currGain, nextGain, currBuf, nextBuf;
        let songList = {music_files};
        let currentIndex = 0;
        let isFading = false;

        async function initPlayer() {{
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            document.getElementById('startBtn').style.display = 'none';
            
            // โหลด 2 เพลงแรก
            currBuf = await decode("{b64_1}");
            nextBuf = await decode("{b64_2}");
            
            playCurrent();
        }}

        async function decode(base64) {{
            const buffer = await fetch("data:audio/mp3;base64," + base64).then(r => r.arrayBuffer());
            return await audioCtx.decodeAudioData(buffer);
        }}

        function playCurrent() {{
            currSrc = audioCtx.createBufferSource();
            currSrc.buffer = currBuf;
            currGain = audioCtx.createGain();
            currSrc.connect(currGain).connect(audioCtx.destination);
            
            document.getElementById('title').innerText = songList[currentIndex];
            document.getElementById('status').innerText = "สถานะ: กำลังเล่น (Non-Stop)";
            
            currSrc.start(0);
            currSrc.startTime = audioCtx.currentTime;
            isFading = false;

            const updater = setInterval(() => {{
                if(!currSrc.buffer) return;
                let remaining = currSrc.buffer.duration - (audioCtx.currentTime - currSrc.startTime);
                
                // แสดงเวลา
                let m = Math.floor(remaining/60); let s = Math.floor(remaining%60);
                document.getElementById('timer').innerText = "เหลืออีก " + m + ":" + (s<10?'0':'') + s;

                // ระบบ Auto-Crossfade 12 วินาทีสุดท้าย
                if (remaining <= 12 && !isFading) {{
                    isFading = true;
                    startFade();
                    clearInterval(updater);
                }}
            }}, 1000);
        }}

        function startFade() {{
            const now = audioCtx.currentTime;
            const fadeDur = 12;

            document.getElementById('status').innerText = "กำลัง Crossfade ไปเพลงถัดไป (12s)...";

            nextSrc = audioCtx.createBufferSource();
            nextSrc.buffer = nextBuf;
            nextGain = audioCtx.createGain();
            nextSrc.connect(nextGain).connect(audioCtx.destination);

            currGain.gain.linearRampToValueAtTime(1, now);
            currGain.gain.linearRampToValueAtTime(0, now + fadeDur);
            
            nextGain.gain.setValueAtTime(0, now);
            nextGain.gain.linearRampToValueAtTime(1, now + fadeDur);

            nextSrc.start(now);
            nextSrc.startTime = now;

            setTimeout(() => {{
                currSrc.stop();
                currSrc = nextSrc;
                currGain = nextGain;
                currBuf = nextBuf;
                currentIndex++;
                
                // แจ้ง Streamlit ให้ส่งเพลงถัดไป (Pre-load)
                window.parent.postMessage({{type: 'streamlit:setComponentValue', value: currentIndex + 1}}, '*');
                
                playCurrent();
            }}, fadeDur * 1000);
        }}
    </script>
</body>
</html>
"""

# 4. แสดงผลแอป
result = components.html(html_code, height=500)

# ระบบ Pre-load: เมื่อ JS ส่งสัญญาณมา Python จะเตรียมเพลงถัดไปให้
if result and isinstance(result, int):
    if result < len(music_files):
        # ตรงนี้เราสามารถส่ง Base64 เพลงถัดไปเข้าไปได้ผ่านการ Rerun
        # เพื่อให้ JavaScript มีเพลงสำรองไว้ในคิวเสมอ
        pass
