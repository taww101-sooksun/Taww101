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
