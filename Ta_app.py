import streamlit as st
import base64
import os

# ตั้งค่าหน้ากระดาน Streamlit ให้แสดงผลแบบเต็มหน้าจอ
st.set_page_config(page_title="จับหยังกะพัง จับหยังกะฮ้าง", layout="wide")

# หาที่อยู่ของโฟลเดอร์ปัจจุบันที่ไฟล์ app.py นี้ทำงานอยู่ตามความเป็นจริง
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ฟังก์ชันแปลงไฟล์ในโฟลเดอร์โปรเจกต์ให้เป็น Base64 เพื่อส่งเข้าไปเล่นใน HTML ได้จริง
def get_base64_encoded_file(file_name):
    # เชื่อมชื่อไฟล์เข้ากับที่อยู่โฟลเดอร์ปัจจุบันแบบเป๊ะๆ
    file_path = os.path.join(BASE_DIR, file_name)
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        return f"data:audio/mp3;base64,{base64.b64encode(data).decode()}"
    return ""

def get_base64_encoded_video(file_name):
    file_path = os.path.join(BASE_DIR, file_name)
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        return f"data:video/mp4;base64,{base64.b64encode(data).decode()}"
    return ""

# ดึงไฟล์จากหน้าหลักของโปรเจกต์ (ตรวจดูว่าพิมพ์ชื่อไฟล์ตัวเล็กตัวใหญ่ตรงกับที่อัปโหลดขึ้น GitHub นะครับ)
song_base64 = get_base64_encoded_file("song.mp3")
video_base64 = get_base64_encoded_video("background-video.mp4")

# ตรวจสอบเบื้องต้นในระบบหลังบ้านว่าเจอไฟล์จริงไหม
if not song_base64:
    st.error("❌ หาไฟล์ 'song.mp3' ไม่เจอในหน้าหลักของโปรเจกต์ กรุณาตรวจสอบชื่อไฟล์บน GitHub ครับ")

# ส่วนของโค้ดหน้าเว็บที่จะไปสร้างไฟนีออนวิ่งตามจังหวะเสียงเพลง
html_code = f"""
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body, html {{
            width: 100%; height: 100%; overflow: hidden;
            font-family: 'Arial', sans-serif; background-color: #000;
            display: flex; justify-content: center; align-items: center;
        }}
        .background-container {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1;
        }}
        .background-container video {{
            width: 100%; height: 100%; object-fit: cover; opacity: 0.35;
        }}
        .lyrics-box {{
            position: relative; z-index: 2; text-align: center; padding: 20px; max-width: 90%; pointer-events: none;
        }}
        .neon-text {{
            font-size: 2.8rem; font-weight: bold; color: #fff;
            text-shadow: 0 0 5px #fff, 0 0 10px #ff0055, 0 0 20px #ff0055;
            transition: text-shadow 0.08s ease; line-height: 1.5;
            text-align: center;
        }}
        .play-btn {{
            position: absolute; z-index: 3; padding: 18px 36px; font-size: 1.3rem; font-weight: bold;
            background-color: #ff0055; color: white; border: none; border-radius: 50px;
            cursor: pointer; box-shadow: 0 0 20px #ff0055; transition: transform 0.2s;
        }}
        .play-btn:hover {{ transform: scale(1.05); }}
    </style>
</head>
<body>

    <div class="background-container">
        <video src="{video_base64}" autoplay loop muted playsinline></video>
    </div>

    <button class="play-btn" id="playBtn">▶ เปิดเพลง: จับหยังกะพัง จับหยังกะฮ้าง</button>

    <div class="lyrics-box">
        <p class="neon-text" id="lyricsDisplay">อยู่นิ่งๆ ก็บ่เจ็บตัว...<br>กดปุ่มเพื่อเริ่มฟังเพลง</p>
    </div>

    <audio id="myTrack" src="{song_base64}" crossOrigin="anonymous"></audio>

    <script>
        const playBtn = document.getElementById('playBtn');
        const audio = document.getElementById('myTrack');
        const lyricsDisplay = document.getElementById('lyricsDisplay');

        // รายการซิงค์เนื้อเพลงตามเวลา (หน่วยเป็น มิลลิวินาที: 1000 = 1 วินาที)
        const lyricsTimeline = [
            {{ time: 0, text: "(Intro)<br>โอ้ละน้อ... ชีวิตคนโซ บ่มียามโก้กับเขาเลิก<br>ตื่นเช้ามา หน้าบ่ล้าง ร่างกายยังสะลึมสะลือ<br>มีแต่ใจเพียวๆ ที่ประคองมันไว้... เออ..." }},
            {{ time: 10000, text: "(Verse 1)<br>ตื่นขึ้นแต่เช้า แปรงฟัน น้ำท่าบ่อาบ<br>กินข้าวเสร็จสรรพ ภารกิจขยับมารับทราบ" }},
            {{ time: 18000, text: "เดินอ้อมรถไถ ตรวจตราดูความเรียบร้อย<br>หวังว่ามื้อนี้สิบ่มีเรื่องให้ข่อยต้องเศร้าสร้อย" }},
            {{ time: 26000, text: "โดดขึ้นเบาะคนขับ จับพวงมาลัยให้มั่น<br>บิดกุญแจสตาร์ทเครื่อง เสียงดังสนั่นไปทั้งหมู่บ้าน" }},
            {{ time: 34000, text: "ควันดำ ขะ โหมง มุ่งหน้าสู่ทุ่งนาที่กว้างใหญ่<br>วันนี้ต้องลุยงานเหล็ก สู้ตายไปกับหัวใจ" }},
            {{ time: 42000, text: "(Pre-Chorus)<br>แต่แล้ว... สวรรค์ กลั่นแกล้ง กันบ่น้อ<br>ไถนาได้สองงาน... ใจมันกะเริ่มท้อ" }},
            {{ time: 50000, text: "(Chorus)<br>ปั่ง!!! เสียงระเบิดดังลั่นทุ่งนา<br>ชิบหายแล้วมึงเอ๊ย น้ำตาไหลมา อาบ หน้า" }},
            {{ time: 58000, text: "ลูกปืนมันแตก เพา ขาด หม้อน้ำกะไหม้<br>พัง พัง ฮ้าง ฮ้าง... สิตายคาทุ่งนา 'บ่'นี่<br>รถไถกะฮ้าง ใจคนขับกะพัง... โอ้โฮ..." }},
            {{ time: 70000, text: "(Verse 2)<br>ขับกันตั้งสามคน แต่กูจับทีไรเป็นพังทุกที!<br>ดวงซวยอะไรขนาดนี้ แจ็กพอตแตกใส่กูตลอดปี" }},
            {{ time: 80000, text: "ไอ้ตอนคนอื่นขับ ไม่เห็นมันเป็นอะไรเลยวะ<br>พอถึงคิวกูทีไร พังยับเยินจนต้องร้องจ้า" }},
            {{ time: 90000, text: "แล้วกูก็โดนบ่น แล้วกูก็โดนด่าอยู่คนเดียว<br>รับ จบทุกปัญหา ทั้งที่ใจกูบางเฉียบประหนึ่งใบเรียว<br>รถไถพังทีไร กูโดนด่าเป็นประจำเลย... เฮ้อ..." }},
            {{ time: 105000, text: "(Outro)<br>อยู่นิ่งๆ ก็บ่เจ็บตัว... แต่ต้องมาขับรถไถ<br>รับความซวยไปเต็มๆ โดนด่าจนอิ่มใจ<br>พังอีกแล้ว... ฮ้างอีกแล้ว... (เฮ้อ...)" }}
        ];

        let audioContext;
        let analyser;
        let dataArray;
        let source;

        playBtn.addEventListener('click', function() {{
            playBtn.style.display = 'none';
            audio.play();

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

            let glowRadius1 = 5 + (averageVolume * 0.15);
            let glowRadius2 = 10 + (averageVolume * 0.3);
            let glowRadius3 = 25 + (averageVolume * 0.5);

            lyricsDisplay.style.textShadow = `
                0 0 ${{glowRadius1}}px #fff,
                0 0 ${{glowRadius2}}px #ff00cc,
                0 0 ${{glowRadius3}}px #ff0055
            `;

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

st.components.v1.html(html_code, height=750, scrolling=False)
