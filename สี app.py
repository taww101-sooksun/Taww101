import streamlit as st
import streamlit.components.v1 as components

# ตั้งค่าหน้าจอให้มืดสนิทตามสไตล์แอปเพลง
st.markdown("<style>.stApp {background-color: #0d1117;}</style>", unsafe_allow_html=True)

app_ui = """
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { color: white; font-family: 'Helvetica', sans-serif; background: transparent; margin: 0; padding: 10px; }
        
        /* สไตล์รายการเพลงในลิสต์ */
        .song-item {
            display: flex; align-items: center; padding: 12px;
            background: rgba(255, 255, 255, 0.05);
            margin-bottom: 8px; border-radius: 12px; transition: 0.3s;
        }
        .song-item:hover { background: rgba(255, 255, 255, 0.1); }
        .song-icon { 
            width: 45px; height: 45px; background: #2a2d3e; 
            display: flex; align-items: center; justify-content: center; 
            border-radius: 8px; margin-right: 15px; color: #8b00ff;
        }
        .song-info { flex-grow: 1; }
        .song-title { font-size: 14px; font-weight: bold; margin-bottom: 4px; }
        .song-sub { font-size: 11px; color: #888; }

        /* Mini Player ด้านล่างที่เลียนแบบรูปภาพ */
        .mini-player {
            position: fixed; bottom: 10px; left: 10px; right: 10px;
            height: 60px; border-radius: 30px;
            background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%); /* ไล่สีม่วง-น้ำเงิน */
            display: flex; align-items: center; padding: 0 20px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.5);
        }
        .player-circle {
            width: 40px; height: 40px; border-radius: 50%;
            background: rgba(255,255,255,0.2);
            display: flex; align-items: center; justify-content: center;
            margin-right: 12px;
        }
        .controls { margin-left: auto; display: flex; gap: 15px; font-size: 20px; }
    </style>
</head>
<body>

    <div style="display: flex; gap: 20px; margin-bottom: 20px; font-weight: bold; font-size: 18px; border-bottom: 2px solid #ff007f; width: fit-content; padding-bottom: 5px;">
        เพลง <span style="color: #888; font-weight: normal;">เพลย์ลิสต์</span>
    </div>

    <div class="song-item">
        <div class="song-icon"><i class="fas fa-music"></i></div>
        <div class="song-info">
            <div class="song-title">ความจริงของเธอคือการ...</div>
            <div class="song-sub"><unknown> - Download</div>
        </div>
        <i class="fas fa-ellipsis-v" style="color:#555"></i>
    </div>

    <div class="song-item">
        <div class="song-icon"><i class="fas fa-music"></i></div>
        <div class="song-info">
            <div class="song-title">การเดินทางที่ไม่มีใครเข้าใจ</div>
            <div class="song-sub">MyAudioEditor</div>
        </div>
        <i class="fas fa-ellipsis-v" style="color:#555"></i>
    </div>

    <div class="mini-player">
        <div class="player-circle"><i class="fas fa-wave-square"></i></div>
        <div style="font-size: 13px;">กำลังเล่น: การเดินทางข...</div>
        <div class="controls">
            <i class="fas fa-pause-circle"></i>
            <i class="fas fa-list"></i>
        </div>
    </div>

</body>
</html>
"""

components.html(app_ui, height=500)
