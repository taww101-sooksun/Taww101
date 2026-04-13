import streamlit as st
import streamlit.components.v1 as components

# ซ่อน UI ของ Streamlit เพื่อความสมจริง
st.markdown("""
    <style>
    .stApp { background: #000; }
    header, footer { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# โค้ดหน้าตาแอปแบบในรูปภาพ
app_ui = """
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { 
            margin: 0; padding: 0; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(180deg, #2c1a4d 0%, #000 100%);
            color: white; overflow: hidden; height: 100vh;
        }
        
        /* พื้นหลังเบลอแบบในรูป */
        .bg-blur {
            position: absolute; width: 100%; height: 100%;
            background: url('https://img5.pic.in.th/file/secure-sv1/1000014503.jpg'); /* ใช้รูปปกของคุณ */
            background-size: cover; background-position: center;
            filter: blur(40px) brightness(0.5); z-index: -1;
        }

        .container {
            display: flex; flex-direction: column; align-items: center;
            padding: 20px; height: 100vh; box-sizing: border-box;
        }

        /* หน้าปกเพลงทรงกลม/เหลี่ยมมน */
        .album-art {
            width: 300px; height: 300px;
            border-radius: 20px;
            box-shadow: 0 10px 50px rgba(0,0,0,0.8);
            margin: 40px 0;
            background-image: url('https://img5.pic.in.th/file/secure-sv1/1000014503.jpg');
            background-size: cover; border: 1px solid rgba(255,255,255,0.1);
        }

        .song-details { text-align: left; width: 100%; padding-left: 20px; }
        .title { font-size: 24px; font-weight: bold; margin: 0; }
        .artist { color: rgba(255,255,255,0.6); font-size: 16px; margin-top: 5px; }

        /* แถบเล่นเพลง */
        .progress-container { width: 100%; margin: 30px 0; }
        .progress-bar {
            width: 100%; height: 4px; background: rgba(255,255,255,0.2);
            border-radius: 2px; position: relative;
        }
        .progress-fill { width: 35%; height: 100%; background: white; border-radius: 2px; }
        .time { display: flex; justify-content: space-between; font-size: 12px; margin-top: 8px; opacity: 0.6; }

        /* ปุ่มควบคุมสไตล์ Apple/Spotify */
        .controls {
            display: flex; justify-content: space-between; align-items: center;
            width: 100%; max-width: 350px; margin-top: 20px;
        }
        .btn-main { font-size: 25px; cursor: pointer; opacity: 0.8; transition: 0.2s; }
        .btn-main:hover { opacity: 1; transform: scale(1.1); }
        .play-pause {
            width: 70px; height: 70px; background: white; color: black;
            border-radius: 50%; display: flex; align-items: center; justify-content: center;
            font-size: 30px;
        }

        /* เมนูด้านล่างสุด */
        .bottom-nav {
            margin-top: auto; width: 100%;
            display: flex; justify-content: space-around;
            padding-bottom: 20px; font-size: 18px; color: rgba(255,255,255,0.5);
        }
        .bottom-nav i:hover { color: white; }
    </style>
</head>
<body>
    <div class="bg-blur"></div>
    <div class="container">
        <div style="width: 40px; height: 4px; background: rgba(255,255,255,0.3); border-radius: 2px;"></div>
        
        <div class="album-art"></div>

        <div class="song-details">
            <div class="title">สักวันหนึ่ง</div>
            <div class="artist">อยู่นิ่งๆ ไม่เจ็บตัว - SYNAPSE</div>
        </div>

        <div class="progress-container">
            <div class="progress-bar"><div class="progress-fill"></div></div>
            <div class="time"><span>0:05</span><span>2:49</span></div>
        </div>

        <div class="controls">
            <i class="fas fa-random btn-main" style="font-size: 18px;"></i>
            <i class="fas fa-step-backward btn-main"></i>
            <div class="play-pause btn-main"><i class="fas fa-pause"></i></div>
            <i class="fas fa-step-forward btn-main"></i>
            <i class="fas fa-redo btn-main" style="font-size: 18px;"></i>
        </div>

        <div class="bottom-nav">
            <i class="fas fa-sliders-h"></i>
            <i class="far fa-comment-dots"></i>
            <i class="fas fa-list"></i>
        </div>
    </div>
</body>
</html>
"""

# แสดงผลใน Streamlit (กว้าง 400 สูง 750 ให้เหมือนขนาดมือถือ)
components.html(app_ui, width=400, height=750)
