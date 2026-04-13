import streamlit as st
import streamlit.components.v1 as components

# --- 1. SET PAGE CONFIG ---
st.set_page_config(
    page_title="SYNAPSE AUDIO PRO",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. HEADER & STYLE ---
st.markdown("""
    <div style='text-align: center;'>
        <h1 style='color: #FF4B4B; text-shadow: 0 0 15px #FF4B4B; margin-bottom: 0px;'>📡 SYNAPSE AUDIO ENGINE</h1>
        <p style='color: #888;'>Professional Crossfade & Vocal Removal</p>
    </div>
    <hr style="border: 1px solid #333;">
    """, unsafe_allow_html=True)

sync_lyrics_html = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #000; color: #fff; font-family: sans-serif; }
        .lyric-box {
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            border: 2px solid #FF4B4B;
            border-radius: 20px;
            background: rgba(255, 0, 0, 0.05);
            box-shadow: 0 0 20px rgba(255, 75, 75, 0.2);
            margin: 20px 0;
        }
        #active-lyric {
            font-size: 28px;
            font-weight: bold;
            color: #FF4B4B;
            text-shadow: 0 0 15px #FF4B4B;
            padding: 20px;
            transition: all 0.2s ease-out;
        }
    </style>
</head>
<body>
    <div class="p-4">
        <input type="file" id="audio-upload" accept="audio/*" class="block w-full text-sm text-gray-500 mb-4" onchange="loadAudio(this.files[0])">
        
        <div class="lyric-box">
            <div id="active-lyric">📡 STANDBY...</div>
        </div>

        <div class="flex gap-2">
            <button onclick="playAudio()" class="flex-1 bg-red-600 hover:bg-red-700 py-3 rounded-lg font-bold">PLAY</button>
            <button onclick="pauseAudio()" class="flex-1 bg-gray-800 hover:bg-gray-700 py-3 rounded-lg font-bold">PAUSE</button>
        </div>
        <p id="timer" class="text-center mt-2 text-xs text-gray-500">0:00</p>
    </div>

    <script>
        let audio = new Audio();
        
        // 1. วางเนื้อเพลงตรงนี้
        const lyrics = [
            { time: 0, text: "📡 SYNAPSE 4-1: ปล่อยวาง" },
            { time: 10, text: "วันหนึ่งถ้าเธอมองย้อนกลับมา" },
            { time: 16, text: "อาจจะเห็นสิ่งที่เคยทำพังลงไป" },
            { time: 22, text: "แต่ถึงตอนนั้น ฉันคงเดินไกล" },
            { time: 28, text: "ทิ้งเรื่องของเราไว้ในอดีตคำที่เธอเคยให้" },
            { time: 38, text: "ขอบคุณถ้อยคำที่เคยทำฉันร้าว" },
            { time: 44, text: "คำที่ทำให้ใจฉันแทบไม่เหลืออะไร" },
            { time: 50, text: "คืนที่ร้องไห้จนไม่รู้จะไปทางไหน..." },
            { time: 56, text: "กลับกลายเป็นทางให้ฉันหันมาเจอแสงในตัวเอง" },
            { time: 65, text: "เคยนอนบนกองน้ำตาเป็นเดือนเป็นปีไม่มีใครรู้" },
            { time: 72, text: "หัวใจข้างในมันพังยับ มากแค่ไหนใครเลยจะมารู้" },
            { time: 80, text: "ยิ้มทั้งที่แผลยังสด" },
            { time: 85, text: "กอดตัวเองเพราะไม่มีใครอยู่" },
            { time: 92, text: "ถ้าเธอได้เห็นข้างในฉัน จะยังกล้ารักคนอย่างฉันไหม" },
            { time: 100, text: "ปล่อยวางความโลภที่เผาใจ... ทิ้งความโกรธที่ไม่มีวันพอ" },
            { time: 120, text: "วันหนึ่งถ้าเธมองย้อนกลับมา" },
            { time: 126, text: "อาจจะเห็นสิ่งที่เคยทำพังลงไป" },
            { time: 132, text: "แต่ถึงตอนนั้น ฉันคงเดินไกล" },
            { time: 140, text: "ทิ้งเรื่องของเราไว้ในอดีตคำที่เธอเคยให้" },
            { time: 155, text: "ขอบคุณถ้อยคำที่เคยทำฉันร้าว" },
            { time: 162, text: "คำที่ทำให้ใจฉันแทบไม่เหลืออะไร" },
            { time: 175, text: "คืนที่ร้องไห้จนไม่รู้จะไปทางไหน..." },
            { time: 185, text: "หันมาเจอแสงในตัวเอง..." },
            { time: 195, text: "ยิ้มทั้งที่แผลยังสด... กอดตัวเองเพราะไม่มีใครอยู่" },
            { time: 205, text: "ปล่อยวางความโลภที่เผาใจ... ทิ้งความโกรธที่ไม่มีวันพอ" },
            { time: 219, text: "--- 📡 END SIGNAL (3:39) ---" }
        ];

        function loadAudio(file) {
            if (file) audio.src = URL.createObjectURL(file);
        }

        function playAudio() { audio.play(); }
        function pauseAudio() { audio.pause(); }

        // 2. ส่วนที่ต้องใส่เพิ่ม: ฟังก์ชันเช็คเวลาเพื่อเปลี่ยนเนื้อเพลง
        audio.ontimeupdate = function() {
            let current = audio.currentTime;
            
            // อัปเดตตัวเลขเวลาข้างล่าง (เอาไว้ดูเพื่อปรับวินาทีให้ตรง)
            document.getElementById('timer').innerText = current.toFixed(2);

            // ค้นหาเนื้อเพลงบรรทัดที่ต้องโชว์
            let active = lyrics.filter(l => l.time <= current).pop();
            
            if (active) {
                let el = document.getElementById('active-lyric');
                if (el.innerText !== active.text) {
                    el.style.opacity = 0; // ทำ Effect จางลงก่อนเปลี่ยน
                    setTimeout(() => {
                        el.innerText = active.text;
                        el.style.opacity = 1; // สว่างขึ้นมาใหม่
                    }, 150);
                }
            }
        };
    </script>
</body>
</html>
"""

import streamlit.components.v1 as components
components.html(sync_lyrics_html, height=500)
