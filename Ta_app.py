import streamlit as st
import base64

# ==========================================
# ส่วนที่ 1: การตั้งค่าหน้าจอและ CSS (Cyberpunk Neon)
# ==========================================

st.set_page_config(page_title="Synapse Neon Video Deck", layout="centered")

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_base64 = get_base64_image("logo1.png")
logo_html_link = f"data:image/png;base64,{logo_base64}" if logo_base64 else ""

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    .stApp {{ background-color: #000; }}

    /* Logo ตรงกลางพร้อมแสง Neon หมุนสลับสี */
    .block-container::before {{
        content: "";
        position: absolute;
        top: 10px; left: 50%;
        transform: translateX(-50%);
        width: 100px; height: 100px;
        background-image: url("{logo_html_link}");
        background-size: contain;
        background-repeat: no-repeat;
        z-index: 999;
        filter: drop-shadow(0 0 10px #ff00de);
        animation: logo-glow 4s infinite alternate;
    }}

    @keyframes logo-glow {{
        0% {{ filter: drop-shadow(0 0 10px #ff00de); transform: translateX(-50%) scale(1); }}
        50% {{ filter: drop-shadow(0 0 25px #00f3ff); transform: translateX(-50%) scale(1.1); }}
        100% {{ filter: drop-shadow(0 0 10px #ff8c00); transform: translateX(-50%) scale(1); }}
    }}

    .neon-title {{
        font-family: 'Orbitron', sans-serif;
        color: #fff;
        text-align: center;
        text-shadow: 0 0 10px #ff00de, 0 0 20px #00f3ff;
        font-size: 1.6rem;
        margin-top: 200px;
        letter-spacing: 6px;
        animation: text-flicker 2s infinite;
    }}
    @keyframes text-flicker {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.8; }}
    }}

    /* สโลแกนแสงนีออนวิ้งๆ วิ่งสลับสี */
    .neon-slogan {{
        text-align: center; 
        color: #fff; 
        font-size: 13px; 
        font-family: "Orbitron", sans-serif; 
        letter-spacing: 4px;
        margin-top: 20px;
        text-shadow: 0 0 5px #ff00de, 0 0 10px #ff00de, 0 0 20px #00f3ff;
        animation: slogan-wink 1s infinite alternate;
    }}

    @keyframes slogan-wink {{
        0%, 100% {{ text-shadow: 0 0 5px #ff00de, 0 0 10px #ff00de, 0 0 20px #ff00de; color: #fff; }}
        50% {{ text-shadow: 0 0 8px #00f3ff, 0 0 15px #00f3ff, 0 0 25px #00f3ff; color: #e0ffff; }}
        82% {{ text-shadow: none; color: #555; }}
        85% {{ text-shadow: 0 0 8px #00f3ff; color: #fff; }}
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="neon-title">อยู่นิ้งๆไม่เจ็บตัว</h1>', unsafe_allow_html=True)

# ==========================================
# ส่วนที่ 2: HTML/JS - ระบบเล่นวิดีโอ (Video Player Deck)
# ==========================================

html_code = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: transparent; color: white; overflow: hidden; font-family: 'Inter', sans-serif; }
        .neon-card { border: 2px solid #333; background: rgba(0,0,0,0.9); box-shadow: 0 0 30px rgba(255,0,222,0.2); }
        
        /* กรอบหน้าจอ Video Player */
        .video-box { 
            width: 100%; 
            height: 220px; 
            background: #050505; 
            border-radius: 15px; 
            border: 2px solid #222; 
            object-fit: contain;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
        }
        .video-active { border-color: #00f3ff; box-shadow: 0 0 15px rgba(0,243,255,0.3); }
        
        .deck { padding: 15px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); background: rgba(255,255,255,0.02); }
        
        .btn-main { 
            background: linear-gradient(45deg, #ff00de, #00f3ff);
            color: white; font-weight: bold; padding: 12px; border-radius: 10px;
            text-transform: uppercase; letter-spacing: 2px; transition: 0.3s;
            box-shadow: 0 0 15px rgba(255,0,222,0.4);
            cursor: pointer;
        }
        .btn-main:hover { transform: scale(1.02); box-shadow: 0 0 25px rgba(0,243,255,0.6); }
        
        .progress-bar { height: 6px; background: #222; border-radius: 10px; overflow: hidden; cursor: pointer; }
        .progress-inner { height: 100%; width: 0%; background: linear-gradient(90deg, #ff00de, #00f3ff); }
    </style>
</head>
<body>
    <div class="max-w-md mx-auto p-4 neon-card rounded-3xl">
        
        <!-- ส่วนแสดงผลวิดีโอ -->
        <div class="relative mb-4">
            <video id="videoPlayer" class="video-box" preload="metadata"></video>
        </div>

        <!-- แผงควบคุมควบคุมไฟล์ -->
        <div class="deck mb-4">
            <div class="flex justify-between text-[11px] mb-2">
                <span id="playStatus" class="text-cyan-400 font-bold tracking-widest">VIDEO DECK READY</span>
                <span id="timeLabel" class="font-mono text-gray-400">00:00 / 00:00</span>
            </div>
            
            <input type="file" id="videoFile" class="hidden" accept="video/mp4, video/webm, video/ogg" onchange="handleVideoFile(this.files[0])">
            <div class="flex gap-2 items-center mb-2">
                <button onclick="document.getElementById('videoFile').click()" class="text-[10px] border border-cyan-500 text-cyan-400 px-3 py-1.5 rounded hover:bg-cyan-950 transition">LOAD VIDEO</button>
                <div id="fileName" class="text-[12px] truncate text-gray-400 flex-1">No Video Loaded</div>
            </div>
            
            <!-- แถบเล่นวิดีโอ (กดคลิกเพื่อข้ามเวลาได้) -->
            <div class="progress-bar mt-3" onclick="seekVideo(event)">
                <div id="progressBar" class="progress-inner"></div>
            </div>
        </div>

        <!-- ปุ่มหลักสำหรับ เล่น / หยุด -->
        <button id="playBtn" onclick="togglePlay()" class="btn-main w-full">▶ PLAY VIDEO</button>

        <div id="status" class="text-[10px] text-center mt-3 text-gray-600 uppercase tracking-widest">System Online</div>
    </div>

    <script>
        const video = document.getElementById('videoPlayer');
        const playBtn = document.getElementById('playBtn');
        const progressBar = document.getElementById('progressBar');
        const timeLabel = document.getElementById('timeLabel');
        const fileName = document.getElementById('fileName');
        const playStatus = document.getElementById('playStatus');
        const statusText = document.getElementById('status');

        // ฟังก์ชันรับไฟล์วิดีโอเข้าเครื่องเล่น
        function handleVideoFile(file) {
            if (!file) return;
            
            fileName.innerText = "Loading Video...";
            const fileURL = URL.createObjectURL(file);
            video.src = fileURL;
            video.load();
            
            fileName.innerText = file.name;
            statusText.innerText = "Video Loaded Successfully";
            playStatus.innerText = "READY TO PLAY";
            
            // รีเซ็ตปุ่มและแถบเวลา
            playBtn.innerText = "▶ PLAY VIDEO";
            progressBar.style.width = "0%";
            video.classList.remove('video-active');
        }

        // ฟังก์ชันเล่น/หยุดวิดีโอ
        function togglePlay() {
            if (!video.src) {
                alert("อาจารย์ครับ รบกวนโหลดวิดีโอก่อนกดเล่นครับ!");
                return;
            }

            if (video.paused) {
                video.play();
                playBtn.innerText = "⏸ PAUSE VIDEO";
                playStatus.innerText = "NOW PLAYING";
                statusText.innerText = "Playing";
                video.classList.add('video-active');
            } else {
                video.pause();
                playBtn.innerText = "▶ RESUME VIDEO";
                playStatus.innerText = "PAUSED";
                statusText.innerText = "Paused";
                video.classList.remove('video-active');
            }
        }

        // อัปเดตแถบเวลาและเวลาตัวเลขแบบ Real-time
        video.ontimeupdate = function() {
            if (!video.duration) return;
            
            const current = video.currentTime;
            const duration = video.duration;
            const percentage = (current / duration) * 100;
            
            progressBar.style.width = percentage + "%";
            
            let curM = Math.floor(current / 60), curS = Math.floor(current % 60);
            let durM = Math.floor(duration / 60), durS = Math.floor(duration % 60);
            
            timeLabel.innerText = 
                (curM < 10 ? '0' : '') + curM + ":" + (curS < 10 ? '0' : '') + curS + " / " +
                (durM < 10 ? '0' : '') + durM + ":" + (durS < 10 ? '0' : '') + durS;
        };

        // เมื่อวิดีโอเล่นจบตัว
        video.onended = function() {
            playBtn.innerText = "▶ PLAY VIDEO";
            playStatus.innerText = "FINISHED";
            statusText.innerText = "End of Video";
            video.classList.remove('video-active');
        };

        // สามารถกดที่แถบความคืบหน้าเพื่อข้ามเวลา (Seek) ไปจุดที่ต้องการได้
        function seekVideo(event) {
            if (!video.duration) return;
            const bar = event.currentTarget;
            const clickX = event.offsetX;
            const width = bar.offsetWidth;
            const percentage = clickX / width;
            video.currentTime = percentage * video.duration;
        }
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=450)

# แสดงสโลแกนวิ้งๆ นีออนปิดท้ายแบบเก๋ๆ
st.markdown('<div class="neon-slogan">อยู่นิ่งๆ ไม่เจ็บตัว | VIDEO CONSOLE v7.0</div>', unsafe_allow_html=True)
