import streamlit as st
import base64

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="จับหยังกะพัง จับหยังกะฮ้าง - Custom", layout="wide")

# สไตล์ CSS ตกแต่ง Sidebar เล็กน้อย
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #111111; color: white; }
    h1, h2, h3 { color: #ff0055 !important; }
    </style>
""", unsafe_allowed_index=True)

# 2. ส่วนควบคุมใน Sidebar (อัปโหลดและแก้ไขข้อมูล)
st.sidebar.title("🎵 ตั้งค่าโปรเจกต์")
st.sidebar.subheader("อยู่นิ่งๆ ไม่เจ็บตัว แต่ถ้าอยากทำกะจัดมา!")

# อัปโหลดวิดีโอพื้นหลัง
bg_video = st.sidebar.file_uploader("1. อัปโหลดวิดีโอพื้นหลัง (MP4)", type=["mp4"])
# อัปโหลดเพลง
bg_audio = st.sidebar.file_uploader("2. อัปโหลดไฟล์เพลง (MP3)", type=["mp3"])

# ส่วนแก้ไขเนื้อเพลง
st.sidebar.subheader("📝 แก้ไขข้อความ/เนื้อเพลง")
text_line_1 = st.sidebar.text_input("ข้อความบรรทัดที่ 1", "จับหยังกะพัง จับหยังกะฮ้างงงงงงงง")
text_line_2 = st.sidebar.text_input("ข้อความบรรทัดที่ 2", "อยู่นิ่งๆ ก็บ่เจ็บตัว... แต่ต้องมาขับรถไถรับความซวย!")

# ปรับความเร็วตัวอักษรวิ่ง
marquee_speed = st.sidebar.slider("🏃 ความเร็วตัวอักษรวิ่ง (วินาทีต่อรอบ ยิ่งน้อยยิ่งวิ่งไว)", min_value=5, max_value=30, value=15)

# 3. ฟังก์ชันแปลงไฟล์ที่อัปโหลดเป็น Base64
def convert_to_base64(uploaded_file, file_type):
    if uploaded_file is not None:
        bytes_data = uploaded_file.read()
        base64_data = base64.b64encode(bytes_data).decode()
        return f"data:{file_type};base64,{base64_data}"
    return ""

video_base64 = convert_to_base64(bg_video, "video/mp4")
audio_base64 = convert_to_base64(bg_audio, "audio/mp3")

# 4. ส่วนแสดงผลหลัก
st.title("🎬 ระบบแสดงผลเอฟเฟกต์ไฟนีออนวิ่ง")

# ตัวแปรช่วยเช็คสถานะ
ready_to_play = True

if not video_base64:
    st.info("💡 คำแนะนำ: อัปโหลดวิดีโอ MP4 ที่ Sidebar ด้านซ้ายเพื่อแสดงพื้นหลัง (ตอนนี้ใช้พื้นหลังดำไปก่อน)")
if not audio_base64:
    st.warning("⚠️ กรุณาอัปโหลดไฟล์เพลง MP3 ที่ Sidebar ด้านซ้ายเพื่อเปิดระบบเสียงและไฟวิ่งตามจังหวะ")
    ready_to_play = False

# โครงสร้าง HTML + CSS + JS (ทำงานบน Browser ของผู้ใช้จริง)
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
            position: relative;
        }}
        
        /* วิดีโอพื้นหลัง */
        .background-container {{
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1;
        }}
        .background-container video {{
            width: 100%; height: 100%; object-fit: cover; opacity: 0.4;
        }}

        /* โซนตัวอักษรวิ่ง (Marquee Container) */
        .marquee-box {{
            position: relative; z-index: 2; width: 100%; overflow: hidden;
            white-space: nowrap; pointer-events: none;
        }}

        /* เอฟเฟกต์อักษรวิ่งข้ามจอ */
        .marquee-content {{
            display: inline-block;
            padding-left: 100%;
            animation: marqueeAnimation {marquee_speed}s linear infinite;
        }}

        .neon-text {{
            font-size: 3.5rem; font-weight: bold; color: #fff;
            text-shadow: 0 0 5px #fff, 0 0 10px #ff0055, 0 0 20px #ff0055;
            transition: text-shadow 0.05s ease;
        }}

        @keyframes marqueeAnimation {{
            0% {{ transform: translate3d(0, 0, 0); }}
            100% {{ transform: translate3d(-100%, 0, 0); }}
        }}

        /* ปุ่มกด */
        .play-btn {{
            position: absolute; z-index: 3; padding: 20px 40px; font-size: 1.5rem; font-weight: bold;
            background-color: #ff0055; color: white; border: none; border-radius: 50px;
            cursor: pointer; box-shadow: 0 0 25px #ff0055; transition: transform 0.2s;
            top: 50%; left: 50%; transform: translate(-50%, -50%);
        }}
        .play-btn:hover {{ transform: translate(-50%, -50%) scale(1.05); }}
    </style>
</head>
<body>

    <!-- เล่นวิดีโออัตโนมัติถ้ามีการอัปโหลดมา -->
    <div class="background-container">
        {f'<video src="{video_base64}" autoplay loop muted playsinline></video>' if video_base64 else ''}
    </div>

    <!-- ปุ่มเริ่มทำงาน -->
    {"<button class='play-btn' id='playBtn'>▶ เริ่มเล่นเพลง & เปิดไฟวิ่ง</button>" if ready_to_play else "<div style='color:white; z-index:3; font-size:1.2rem;'>คอยแป๊บนะ... อัปโหลดเพลงก่อนถึงจะกดเล่นได้</div>"}

    <!-- ตัวอักษรวิ่งหนีไปด้านซ้าย -->
    <div class="marquee-box">
        <div class="marquee-content" id="neonContainer">
            <span class="neon-text" id="lyricsDisplay">
                {text_line_1} &nbsp;&nbsp;&nbsp;&nbsp; || &nbsp;&nbsp;&nbsp;&nbsp; {text_line_2}
            </span>
        </div>
    </div>

    <!-- ไฟล์เสียง -->
    <audio id="myTrack" src="{audio_base64}" crossOrigin="anonymous"></audio>

    <script>
        const playBtn = document.getElementById('playBtn');
        const audio = document.getElementById('myTrack');
        const lyricsDisplay = document.getElementById('lyricsDisplay');

        let audioContext;
        let analyser;
        let dataArray;
        let source;

        if(playBtn) {{
            playBtn.addEventListener('click', function() {{
                playBtn.style.display = 'none';
                audio.play();

                // สร้าง Web Audio API เพื่อดึงความถี่เสียงมาทำไฟกระพริบจริง
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
        }}

        // ฟังก์ชันคำนวณความดังเสียงแบบ Real-time เพื่อสั่งให้แสงนีออนวาบตามเบส
        function updateVisuals() {{
            requestAnimationFrame(updateVisuals);
            if (!analyser) return;
            
            analyser.getByteFrequencyData(dataArray);
            
            let total = 0;
            for (let i = 0; i < dataArray.length; i++) {{
                total += dataArray[i];
            }}
            let averageVolume = total / dataArray.length; 

            // ปรับแต่งรัศมีนีออนตามความดังของเพลงขนะนั้นๆ
            let glowRadius1 = 5 + (averageVolume * 0.2);
            let glowRadius2 = 10 + (averageVolume * 0.4);
            let glowRadius3 = 25 + (averageVolume * 0.7);

            lyricsDisplay.style.textShadow = `
                0 0 ${{glowRadius1}}px #fff,
                0 0 ${{glowRadius2}}px #ff00cc,
                0 0 ${{glowRadius3}}px #ff0055
            `;
        }}
    </script>
</body>
</html>
"""

# แสดงผลกระดาน HTML
st.components.v1.html(html_code, height=600, scrolling=False)
