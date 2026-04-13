import streamlit as st
import streamlit.components.v1 as components
import streamlit as st
import streamlit as st
import streamlit.components.v1 as components

# --- 1. SET PAGE CONFIG & HIDE STREAMLIT ELEMENTS ---
st.set_page_config(page_title="SYNAPSE LYRIC ENGINE", layout="centered", initial_sidebar_state="collapsed")

# CSS สำหรับลบความเป็น Streamlit และจัดการโลโก้
st.markdown("""
    <style>
    /* ซ่อน Header และ Footer ของ Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="stAppViewContainer"] {background-color: #000000;}
    
    /* จัดการโลโก้ให้ไม่มีกรอบและลอยอยู่ด้านบน */
    .logo-container {
        display: flex;
        justify-content: center;
        padding: 20px;
    }
    .main-logo {
        width: 120px; /* ปรับขนาดโลโก้ตรงนี้ */
        filter: drop-shadow(0 0 10px rgba(255, 75, 75, 0.5)); /* เพิ่มแสงเรืองรอบโลโก้ */
        border: none;
        background: transparent;
    }
    </style>
    
    <div class="logo-container">
        <img src="app/static/logo1.png" class="main-logo" onerror="this.src='https://via.placeholder.com/120?text=LOGO+NOT+FOUND'">
    </div>
    """, unsafe_allow_html=True)

# --- 2. HTML ENGINE (Lyric Synchronizer) ---
sync_lyrics_html = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: #000; color: #fff; font-family: sans-serif; overflow: hidden; }
        .lyric-display {
            height: 250px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            border: 1px solid #333;
            border-radius: 30px;
            background: radial-gradient(circle, #1a0505 0%, #000000 100%);
            box-shadow: 0 0 40px rgba(255, 75, 75, 0.1);
        }
        #active-lyric {
            font-size: 32px;
            font-weight: bold;
            color: #FF4B4B;
            text-shadow: 0 0 20px #FF4B4B;
            padding: 20px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .timer-text { font-family: monospace; color: #444; font-size: 10px; text-align: center; margin-top: 10px; }
        input[type="file"] { display: none; }
        .custom-file-upload {
            display: inline-block;
            padding: 8px 20px;
            cursor: pointer;
            background: #222;
            border-radius: 20px;
            font-size: 12px;
            color: #888;
            border: 1px solid #444;
        }
    </style>
</head>
<body>
    <div class="p-2">
        <div class="text-center mb-4">
            <label for="audio-upload" class="custom-file-upload">📂 LOAD MP3 SIGNAL</label>
            <input type="file" id="audio-upload" accept="audio/*" onchange="loadAudio(this.files[0])">
        </div>

        <div class="lyric-display">
            <div id="active-lyric">READY TO CONNECT</div>
        </div>

        <div class="flex gap-4 mt-6">
            <button onclick="playAudio()" class="flex-1 bg-red-600 hover:bg-red-700 py-4 rounded-2xl font-bold shadow-lg shadow-red-900/20">PLAY</button>
            <button onclick="pauseAudio()" class="flex-1 bg-zinc-900 hover:bg-zinc-800 py-4 rounded-2xl font-bold">PAUSE</button>
        </div>
        <div id="timer" class="timer-text">0.00</div>
    </div>

    <script>
        let audio = new Audio();
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
            { time: 120, text: "วันหนึ่งถ้าเธอมองย้อนกลับมา" },
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

        function loadAudio(file) { if (file) audio.src = URL.createObjectURL(file); }
        function playAudio() { audio.play(); }
        function pauseAudio() { audio.pause(); }

        audio.ontimeupdate = function() {
            let current = audio.currentTime;
            document.getElementById('timer').innerText = current.toFixed(2);
            let active = lyrics.filter(l => l.time <= current).pop();
            if (active) {
                let el = document.getElementById('active-lyric');
                if (el.innerText !== active.text) {
                    el.style.transform = "scale(0.9)";
                    el.style.opacity = 0;
                    setTimeout(() => {
                        el.innerText = active.text;
                        el.style.transform = "scale(1)";
                        el.style.opacity = 1;
                    }, 150);
                }
            }
        };
    </script>
</body>
</html>
"""

components.html(sync_lyrics_html, height=500)

st.set_page_config(page_title="SYNAPSE HUB", layout="centered")

st.markdown("""
    <div style='text-align: center;'>
        <h1 style='color: #FF4B4B; text-shadow: 0 0 15px #FF4B4B;'>📡 SYNAPSE HUB</h1>
        <p style='color: #888;'>ยินดีต้อนรับสู่ระบบควบคุม 4-1 | เลือกห้องใช้งานที่แถบด้านข้าง</p>
    </div>
    <hr style="border: 1px solid #333;">
    """, unsafe_allow_html=True)

st.info("💡 เลือกห้องทางด้านซ้ายเพื่อเริ่มงาน: ไม่ว่าจะรันวิดีโอ ผสมเพลง หรือคุมเนื้อเพลง")

# เพิ่มความเท่หน้าแรก
st.image("https://images.unsplash.com/photo-1550745165-9bc0b252726f?q=80&w=2070", caption="SYNAPSE CORE READY")

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

# --- 3. HTML / JAVASCRIPT ENGINE (โค้ดที่คุณส่งมา) ---
# ผมนำโค้ด HTML ของคุณมาใส่ในตัวแปรนี้
audio_engine_html = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #0d1117; color: #c9d1d9; font-family: sans-serif; }
        .lyrics-block pre { white-space: pre-wrap; word-wrap: break-word; }
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-thumb { background: #30363d; border-radius: 10px; }
    </style>
</head>
<body>
    <div class="max-w-full mx-auto bg-[#161b22] p-4 rounded-xl border border-[#30363d]">
        <div id="status-box" class="mb-4 p-3 bg-[#21262d] rounded-lg border border-[#30363d]">
            <p class="text-xs">STATUS: <span id="current-status" class="text-yellow-400">WAITING FOR FILES</span></p>
            <p class="text-xs">NOW PLAYING: <span id="current-song" class="text-blue-400">-</span></p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <input type="file" id="fileA" accept="audio/*" class="text-xs text-gray-400 file:bg-purple-600 file:text-white file:rounded-full file:border-0 file:px-4 file:py-1" onchange="loadAudio(this.files[0], 'A')">
            <input type="file" id="fileB" accept="audio/*" class="text-xs text-gray-400 file:bg-purple-600 file:text-white file:rounded-full file:border-0 file:px-4 file:py-1" onchange="loadAudio(this.files[0], 'B')">
        </div>

        <div class="space-y-2">
            <button id="start-btn" onclick="startPlayingA()" disabled class="w-full py-2 bg-green-600 text-white rounded-lg disabled:bg-gray-700">START CHANNEL A</button>
            <div class="flex items-center justify-between text-xs">
                <span>FADE TIME: <span id="fade-duration-value">10</span>s</span>
                <input type="range" id="fade-duration-input" min="1" max="10" value="10" step="0.5" oninput="document.getElementById('fade-duration-value').textContent = this.value" class="w-2/3">
            </div>
            <button id="crossfade-btn" onclick="startCrossfade()" disabled class="w-full py-2 bg-orange-600 text-white rounded-lg disabled:bg-gray-700">CROSSFADE TO CHANNEL B</button>
            <button id="vocal-btn" onclick="toggleVocalRemoval()" disabled class="w-full py-2 bg-blue-600 text-white rounded-lg disabled:bg-gray-700">VOCAL REMOVAL (KARAOKE)</button>
        </div>

        <div id="lyrics-container" class="mt-4 p-3 bg-[#0d1117] rounded-lg border border-[#333] h-40 overflow-y-auto hidden">
            <div id="lyrics-A" class="lyrics-block hidden"><p class="text-purple-400 text-xs">[CH A LYRICS]</p><pre class="text-xs text-gray-400">...Lyrics A...</pre></div>
            <div id="lyrics-B" class="lyrics-block hidden"><p class="text-purple-400 text-xs">[CH B LYRICS]</p><pre class="text-xs text-gray-400">...Lyrics B...</pre></div>
        </div>
    </div>

    <script>
        let audioContext, songABuffer, songBBuffer, songASource, songBSource, songAGain, songBGain;
        let isPlaying = false, currentPlaying = 'None', isVocalEffectActive = false, vocalEffectChainA, vocalEffectChainB;

        function initAudioContext() { if (!audioContext) audioContext = new (window.AudioContext || window.webkitAudioContext)(); }
        
        function updateStatus(status, song, colorClass = 'text-yellow-400') {
            document.getElementById('current-status').textContent = status;
            document.getElementById('current-status').className = colorClass;
            document.getElementById('current-song').textContent = song;
            currentPlaying = song;
            document.getElementById('start-btn').disabled = !(songABuffer && songBBuffer) || isPlaying;
            document.getElementById('crossfade-btn').disabled = !isPlaying || isVocalEffectActive;
            document.getElementById('vocal-btn').disabled = !isPlaying;
            document.getElementById('vocal-btn').textContent = isVocalEffectActive ? 'OFF VOCAL EFFECT' : 'ON VOCAL EFFECT';
            
            const container = document.getElementById('lyrics-container');
            if (isPlaying && song !== '-') {
                container.classList.remove('hidden');
                document.getElementById('lyrics-A').classList.toggle('hidden', song !== 'A');
                document.getElementById('lyrics-B').classList.toggle('hidden', song !== 'B');
            } else { container.classList.add('hidden'); }
        }

        function loadAudio(file, songKey) {
            if (!file) return;
            initAudioContext();
            updateStatus(`LOADING ${songKey}...`, currentPlaying);
            const reader = new FileReader();
            reader.onload = async (e) => {
                const buffer = await audioContext.decodeAudioData(e.target.result);
                if (songKey === 'A') songABuffer = buffer; else songBBuffer = buffer;
                updateStatus(`${songKey} READY`, currentPlaying, 'text-green-400');
            };
            reader.readAsArrayBuffer(file);
        }

        function playSong(buffer, startGain) {
            const source = audioContext.createBufferSource();
            source.buffer = buffer; source.loop = true;
            const gain = audioContext.createGain();
            gain.gain.setValueAtTime(startGain, audioContext.currentTime);
            source.connect(gain); gain.connect(audioContext.destination);
            source.start();
            return { source, gain };
        }

        function startPlayingA() {
            initAudioContext();
            if (songASource) songASource.stop(); if (songBSource) songBSource.stop();
            const a = playSong(songABuffer, 1.0); songASource = a.source; songAGain = a.gain;
            const b = playSong(songBBuffer, 0.0); songBSource = b.source; songBGain = b.gain;
            isPlaying = true; updateStatus('PLAYING', 'A', 'text-green-500');
        }

        function startCrossfade() {
            const dur = parseFloat(document.getElementById('fade-duration-input').value);
            const now = audioContext.currentTime;
            if (currentPlaying === 'A') {
                songAGain.gain.linearRampToValueAtTime(1.0, now);
                songAGain.gain.linearRampToValueAtTime(0.0, now + dur);
                songBGain.gain.linearRampToValueAtTime(0.0, now);
                songBGain.gain.linearRampToValueAtTime(1.0, now + dur);
                setTimeout(() => { 
                    songASource.stop(); const n = playSong(songABuffer, 0.0); 
                    songASource = n.source; songAGain = n.gain;
                    updateStatus('PLAYING', 'B', 'text-green-500'); 
                }, dur * 1000);
            } else {
                songBGain.gain.linearRampToValueAtTime(1.0, now);
                songBGain.gain.linearRampToValueAtTime(0.0, now + dur);
                songAGain.gain.linearRampToValueAtTime(0.0, now);
                songAGain.gain.linearRampToValueAtTime(1.0, now + dur);
                setTimeout(() => { 
                    songBSource.stop(); const n = playSong(songBBuffer, 0.0); 
                    songBSource = n.source; songBGain = n.gain;
                    updateStatus('PLAYING', 'A', 'text-green-500'); 
                }, dur * 1000);
            }
        }

        function toggleVocalRemoval() {
            const gain = (currentPlaying === 'A') ? songAGain : songBGain;
            isVocalEffectActive = !isVocalEffectActive;
            if (isVocalEffectActive) {
                gain.disconnect(audioContext.destination);
                const splitter = audioContext.createChannelSplitter(2);
                const merger = audioContext.createChannelMerger(2);
                const inverter = audioContext.createGain();
                inverter.gain.setValueAtTime(-1, audioContext.currentTime);
                gain.connect(splitter);
                splitter.connect(merger, 0, 0);
                splitter.connect(inverter, 1, 0);
                inverter.connect(merger, 0, 0);
                merger.connect(audioContext.destination);
                if (currentPlaying === 'A') vocalEffectChainA = { splitter, merger, inverter };
                else vocalEffectChainB = { splitter, merger, inverter };
                updateStatus('VOCAL REMOVAL: ON', currentPlaying, 'text-purple-400');
            } else {
                gain.disconnect(); gain.connect(audioContext.destination);
                updateStatus('PLAYING', currentPlaying, 'text-green-500');
            }
        }
    </script>
</body>
</html>
"""

# --- 4. RENDER COMPONENT ---
# ปรับความสูง (height) ให้พอดีกับหน้าจอ
components.html(audio_engine_html, height=600, scrolling=True)

# --- 5. FOOTER ---
st.markdown("""
    <div style='text-align: center; color: #444; font-size: 10px; margin-top: 20px;'>
        SYNAPSE ENGINE v2.1 | อยู่นิ่งๆ ไม่เจ็บตัว
    </div>
    """, unsafe_allow_html=True)
