import streamlit as st
import base64
import os
import json

# 1. ตั้งค่าหน้าจอ Streamlit แบบกว้าง
st.set_page_config(page_title="จับหยังกะพัง จับหยังกะฮ้าง - Custom", layout="wide")

st.title("🎵 ระบบปรับแต่งเพลงและเนื้อเพลงนีออนวิ่งตามจังหวะ")
st.write("คุณสามารถอัปโหลดไฟล์วิดีโอ เพลง และแก้เนื้อเพลงพร้อมเวลาได้ที่แถบด้านซ้ายมือเลยเพื่อน!")

# --- ส่วนของการจัดการข้อมูล (Sidebar Control Panel) ---
st.sidebar.header("🛠️ แผงควบคุมและตั้งค่า")

# 2. ฟังก์ชันช่วยแปลงไฟล์อัปโหลดเป็น Base64 (ดึงจากหน่วยความจำได้โดยตรง ไม่ต้องบันทึกลงเครื่อง)
def get_base64_from_upload(uploaded_file, file_type):
    if uploaded_file is not None:
        bytes_data = uploaded_file.read()
        encoded = base64.b64encode(bytes_data).decode()
        return f"data:{file_type};base64,{encoded}"
    return ""

# ช่องอัปโหลดไฟล์เพลงและวิดีโอ
uploaded_video = st.sidebar.file_uploader("1. อัปโหลดวิดีโอพื้นหลัง (.mp4)", type=["mp4"])
uploaded_song = st.sidebar.file_uploader("2. อัปโหลดไฟล์เพลง (.mp3)", type=["mp3"])

# เนื้อเพลงเริ่มต้น (Default JSON)
default_lyrics = [
    {"time": 0, "text": "(Intro)<br>อยู่นิ่งๆ ก็บ่เจ็บตัว... แต่ทำไมรถไถมันพัง"},
    {"time": 5000, "text": "(Verse 1)<br>ตื่นเช้ามาจับอะไรก็ฮ้าง จับอะไรก็พัง"},
    {"time": 12000, "text": "คนอื่นขับไม่เป็นไร พอเราจับปุ๊บพังปั๊บ!"}
]

st.sidebar.subheader("3. แก้ไขเนื้อเพลงและเวลา (JSON format)")
st.sidebar.caption("แก้เวลาหน่วยเป็นมิลลิวินาที (1000 = 1 วินาที) และข้อความได้ตามใจชอบ")

# กล่องข้อความให้ผู้ใช้พิมพ์แก้ JSON เนื้อเพลงได้เองบนหน้าเว็บ
lyrics_json_string = st.sidebar.text_area(
    "โครงสร้างเนื้อเพลง:",
    value=json.dumps(default_lyrics, ensure_ascii=False, indent=2),
    height=300
)

# ตรวจสอบความถูกต้องของ JSON ที่ผู้ใช้กรอก
try:
    lyrics_data = json.loads(lyrics_json_string)
    # แปลงเป็น string เพื่อโยนเข้าสคริปต์ JavaScript ได้อย่างปลอดภัย
    lyrics_timeline_js = json.dumps(lyrics_data, ensure_ascii=False)
except Exception as e:
    st.sidebar.error(f"❌ รูปแบบ JSON ไม่ถูกต้อง กรุณาเช็คเครื่องหมายปีกกาหรือลูกน้ำ: {e}")
    lyrics_timeline_js = json.dumps(default_lyrics, ensure_ascii=False)

# --- ส่วนการแปลงไฟล์และตั้งค่าเริ่มต้นตามจริง ---
video_base64 = get_base64_from_upload(uploaded_video, "video/mp4")
song_base64 = get_base64_from_upload(uploaded_song, "audio/mp3")

# แจ้งเตือนสถานะเพื่อให้ผู้ใช้รู้ว่าระบบพร้อมทำงานไหม (ตามจริง ไม่มีการหลอก)
if not video_base64:
    st.info("💡 ตอนนี้ใช้ 'วิดีโอตัวอย่างสีดำ' อยู่ กรุณาอัปโหลดไฟล์วิดีโอของคุณที่แถบซ้ายมือ")
if not song_base64:
    st.warning("⚠️ ยังไม่มีเพลงทำงาน กรุณาอัปโหลดไฟล์ .mp3 ที่แถบซ้ายมือเพื่อเริ่มเล่น")

# --- โครงสร้าง HTML & JavaScript (ที่ดึงข้อมูลจาก Streamlit มาใช้แบบ Dynamic) ---
html_code = f"""
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body, html {{
            width: 100%; height: 100%; overflow: hidden;
            font-family: 'Arial', sans-serif; background-color: #111;
            display: flex; justify-content: center; align-items: center;
        }}
        .background-container {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1;
        }}
        .background-container video {{
            width: 100%; height: 100%; object-fit: cover; opacity: 0.4;
        }}
        .lyrics-box {{
            position: relative; z-index: 2; text-align: center; padding: 20px; max-width: 90%; pointer-events: none;
        }}
        .neon-text {{
            font-size: 2.8rem; font-weight: bold; color: #fff;
            text-shadow: 0 0 5px #fff, 0 0 10px #00fff2, 0 0 20px #00fff2;
            transition: text-shadow 0.08s ease; line-height: 1.5;
            text-align: center;
        }}
        .play-btn {{
            position: absolute; z-index: 3; padding: 18px 36px; font-size: 1.3rem; font-weight: bold;
            background-color: #00fff2; color: #000; border: none; border-radius: 50px;
            cursor: pointer; box-shadow: 0 0 20px #00fff2; transition: transform 0.2s;
        }}
        .play-btn:hover {{ transform: scale(1.05); }}
    </style>
</head>
<body>

    <div class="background-container">
        <video id="bgVideo" src="{video_base64}" loop muted playsinline></video>
    </div>

    <button class="play-btn" id="playBtn">▶ เริ่มเล่นเพลงและวิดีโอพื้นหลัง</button>

    <div class="lyrics-box">
        <p class="neon-text" id="lyricsDisplay">ระบบพร้อมแล้ว<br>กรุณากดปุ่มเพื่อเริ่มเล่น</p>
    </div>

    <audio id="myTrack" src="{song_base64}" crossOrigin="anonymous"></audio>

    <script>
        const playBtn = document.getElementById('playBtn');
        const audio = document.getElementById('myTrack');
        const video = document.getElementById('bgVideo');
        const lyricsDisplay = document.getElementById('lyricsDisplay');

        // ดึงข้อมูล Timeline เนื้อเพลงที่ผู้ใช้พิมพ์แก้จากตัวแปรหน้าเว็บ Streamlit โดยตรง
        const lyricsTimeline = {lyrics_timeline_js};

        let audioContext;
        let analyser;
        let dataArray;
        let source;

        playBtn.addEventListener('click', function() {{
            // สั่งเล่นทั้งเพลงและวิดีโอพร้อมกันเมื่อกดปุ่ม
            playBtn.style.display = 'none';
            audio.play().catch(e => console.log("Audio play error:", e));
            video.play().catch(e => console.log("Video play error:", e));

            if (!audioContext) {{
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                analyser = audioContext.createAnalyser();
                source = audioContext.createMediaElementSource(audio);
                source.connect(analyser);
                analyser.connect(audioContext.destination);
                
                analyser.fftSize = 32; 
                const bufferLength = analyser.frequencyBinCount;
                dataArray = new Uint8Array(bufferLength);
                
                updateVisuals();
            }}
        }});

        function updateVisuals() {{
            requestAnimationFrame(updateVisuals);
            if (!analyser) return;
            
            analyser.getByteFrequencyData(dataArray);
            
            let total = 0;
            for (let i = 0; i < dataArray.length; i++) {{
                total += dataArray[i];
            }}
            let averageVolume = total / dataArray.length; 

            // เอฟเฟกต์ไฟนีออนเต้นตามจังหวะเสียงเบส/ความดังจริง
            let glowRadius1 = 5 + (averageVolume * 0.15);
            let glowRadius2 = 10 + (averageVolume * 0.3);
            let glowRadius3 = 25 + (averageVolume * 0.5);

            lyricsDisplay.style.textShadow = `
                0 0 ${{glowRadius1}}px #fff,
                0 0 ${{glowRadius2}}px #00fff2,
                0 0 ${{glowRadius3}}px #00e1ff
            `;

            // ดึงเวลาปัจจุบันของเพลงมาตรวจสอบเทียบกับ Timeline
            let currentTimeMs = audio.currentTime * 1000;
            let currentText = "";
            for (let i = 0; i < lyricsTimeline.length; i++) {{
                if (currentTimeMs >= lyricsTimeline[i].time) {{
                    currentText = lyricsTimeline[i].text;
                }}
            }}
            if(currentText !== "") {{
                lyricsDisplay.innerHTML = currentText;
            }}
        }}
    </script>
</body>
</html>
"""

# แสดงหน้าเว็บเครื่องเล่นเพลงซิงค์เนื้อเพลง
st.components.v1.html(html_code, height=650, scrolling=False)
