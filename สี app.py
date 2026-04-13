import streamlit as st
import os
import streamlit.components.v1 as components

# --- 1. SETUP UI & CONFIG ---
st.set_page_config(page_title="SYNAPSE SUPER APP", layout="wide")

def setup_ui():
    st.markdown("""
        <style>
        /* ลบ Header, Footer และเมนูเดิมของ Streamlit */
        header, footer, #MainMenu {visibility: hidden;}
        .stApp { background: #000; color: #00f2fe; }
        
        /* คุมขนาดรูปใน Sidebar ให้คงที่ */
        [data-testid="stSidebar"] img {
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100px;
        }

        /* สไตล์ปุ่มเมนูหน้าหลัก */
        .stButton>button {
            border-radius: 15px;
            border: 1px solid #00f2fe;
            background: rgba(0, 242, 254, 0.1);
            color: white;
            height: 80px;
            font-size: 16px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background: #00f2fe;
            color: #000;
            box-shadow: 0 0 20px #00f2fe;
        }
        
        .neon-text {
            text-align: center;
            color: #fff;
            text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

setup_ui()

# --- 2. SIDEBAR (ย้ายเครื่องเล่นมาไว้ที่นี่เพื่อให้เพลงไม่ดับเวลาเปลี่ยนหน้า) ---
with st.sidebar:
    if os.path.exists("logo1.png"):
        st.image("logo1.png") 
    else:
        st.markdown("<h2 style='text-align:center;'>SYNAPSE</h2>", unsafe_allow_html=True)
    
    st.divider()
    
    # --- เครื่องเล่นเพลงแบบ Global (เล่นต่อเนื่อง) ---
    st.markdown("### 🎧 Global Player")
    player_sidebar_html = """
    <div id="mini-player" style="background:#111; padding:10px; border-radius:10px; border:1px solid #00f2fe;">
        <input type="file" id="side-upload" multiple accept="audio/*" style="display:none" onchange="handleSideFiles(this.files)">
        <button onclick="document.getElementById('side-upload').click()" style="width:100%; background:#00f2fe; color:#000; border:none; padding:5px; border-radius:5px; cursor:pointer; font-weight:bold;">➕ LOAD MUSIC</button>
        <div id="side-track" style="font-size:10px; color:#fff; margin-top:5px; white-space:nowrap; overflow:hidden;">Ready...</div>
        
        <div style="margin-top:10px;">
            <label style="font-size:10px;">KARAOKE STRENGTH</label>
            <input type="range" min="0" max="100" value="0" style="width:100%" oninput="updateKaraoke(this.value)">
        </div>
    </div>

    <script>
        let sCtx, sAnalyser, sAudio = new Audio(), sSource, sFilter;
        let sPlaylist = [];
        let sIndex = 0;

        function initSideAudio() {
            if (!sCtx) {
                sCtx = new (window.AudioContext || window.webkitAudioContext)();
                sAnalyser = sCtx.createAnalyser();
                sSource = sCtx.createMediaElementSource(sAudio);
                
                // ใช้ Notch Filter เพื่อเจาะจงตัดย่านเสียงร้อง
                sFilter = sCtx.createBiquadFilter();
                sFilter.type = "notch"; 
                sFilter.frequency.value = 1000; // ย่านเสียงคน
                sFilter.Q.value = 0; // เริ่มต้นที่ 0 (ไม่ตัด)

                sSource.connect(sFilter);
                sFilter.connect(sAnalyser);
                sAnalyser.connect(sCtx.destination);
            }
        }

        function handleSideFiles(files) {
            initSideAudio();
            sPlaylist = Array.from(files);
            if(sPlaylist.length > 0) playSide(0);
        }

        function playSide(i) {
            sIndex = i;
            const file = sPlaylist[sIndex];
            sAudio.src = URL.createObjectURL(file);
            document.getElementById('side-track').innerText = file.name;
            sAudio.play();
        }

        function updateKaraoke(val) {
            if(sFilter) {
                // ยิ่งเลื่อนมาก Q ยิ่งสูง = ตัดย่านเสียงกลางแคบและแรงขึ้น
                sFilter.Q.value = val / 10; 
            }
        }
        
        sAudio.onended = () => {
            sIndex = (sIndex + 1) % sPlaylist.length;
            playSide(sIndex);
        };
    </script>
    """
    components.html(player_sidebar_html, height=200)

    st.divider()
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = "HOME"
        st.rerun()


with st.sidebar:
    # แสดงโลโก้ตลอดเวลา
    if os.path.exists("logo1.png"):
        st.image("logo1.png") 
    else:
        st.markdown("<h2 style='text-align:center;'>SYNAPSE</h2>", unsafe_allow_html=True)
    
    st.divider()
    
    # ปุ่มกลับหน้าหลักใน Sidebar
    if st.button("🏠 กลับหน้าหลัก", use_container_width=True):
        st.session_state.page = "HOME"
        st.rerun()
    
    st.markdown("<p style='text-align:center;font-size:10px;'>อยู่นิ่งๆ ไม่เจ็บตัว</p>", unsafe_allow_html=True)

# --- 3. เนื้อหาแต่ละหน้า ---

# [ หน้าแรก: CENTRAL HUB ]
    if st.session_state.page == "HOME":
    st.markdown("<h1 class='neon-text'>CENTRAL HUB</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>เลือกฟังก์ชันการใช้งาน</h3>", unsafe_allow_html=True)
    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🎵 1. MUSIC PLAYER\nCrossfade & Karaoke", use_container_width=True):
            st.session_state.page = "1"; st.rerun()
        if st.button("🖼️ 3. IMAGE SEARCH", use_container_width=True):
            st.session_state.page = "3"; st.rerun()
        if st.button("✨ 5. NEON GENERATOR", use_container_width=True):
            st.session_state.page = "5"; st.rerun()
        if st.button("💖 7. DESTINY CHECK", use_container_width=True):
            st.session_state.page = "7"; st.rerun()
        if st.button("📝 9. SYSTEM LOG", use_container_width=True):
            st.session_state.page = "9"; st.rerun()

    with c2:
        if st.button("💬 2. CHAT SYSTEM", use_container_width=True):
            st.session_state.page = "2"; st.rerun()
        if st.button("🎬 4. VIDEO HUB", use_container_width=True):
            st.session_state.page = "4"; st.rerun()
        if st.button("🌍 6. WORLD CLOCK", use_container_width=True):
            st.session_state.page = "6"; st.rerun()
        if st.button("🔢 8. DAILY CODE", use_container_width=True):
            st.session_state.page = "8"; st.rerun()
        if st.button("🎨 10. COLOR MASTER", use_container_width=True):
            st.session_state.page = "10"; st.rerun()

# [ หน้า 1: MUSIC PLAYER ]
elif st.session_state.page == "1":
    # --- ปุ่มกลับหน้าหลัก (เอาคืนมาให้แล้วครับ) ---
    if st.button("⬅️ กลับหน้าหลัก"):
        st.session_state.page = "HOME"
        st.rerun()

    st.markdown("<h2 class='neon-text'>🎵 SYNAPSE AUDIO PRO</h2>", unsafe_allow_html=True)
    st.info("💡 ความพิเศษ: Crossfade 10s | ตัดเสียงร้อง | Visualizer อัจฉริยะ")

    player_html = """
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { background: transparent; color: #00f2fe; font-family: sans-serif; }
            .player-container { background: rgba(15, 23, 42, 0.9); border: 2px solid #00f2fe; border-radius: 24px; padding: 25px; box-shadow: 0 0 30px rgba(0, 242, 254, 0.3); }
            .visual-box { width: 100%; height: 150px; background: #000; border-radius: 15px; margin-bottom: 20px; border: 1px solid #1e293b; }
            .btn-neon { background: #00f2fe; color: #000; padding: 10px 20px; border-radius: 50px; font-weight: bold; transition: 0.3s; cursor: pointer; }
            .btn-neon:hover { box-shadow: 0 0 15px #00f2fe; transform: translateY(-2px); }
            .control-btn { font-size: 24px; color: #00f2fe; cursor: pointer; opacity: 0.8; }
            .control-btn:hover { opacity: 1; }
            input[type="range"] { accent-color: #00f2fe; width: 100%; }
        </style>
    </head>
    <body>
        <div class="player-container">
            <canvas id="visualizer" class="visual-box"></canvas>

            <div id="track-name" class="text-xl font-bold mb-1 truncate text-white">READY TO SCAN...</div>
            <div id="status-msg" class="text-xs text-cyan-500 mb-4 uppercase tracking-widest">System Online</div>

            <input type="file" id="upload" multiple accept="audio/*" class="hidden" onchange="handleUpload(this.files)">
            <div class="flex justify-between items-center mb-6">
                <button class="btn-neon" onclick="document.getElementById('upload').click()">➕ เพิ่มเพลง</button>
                <div class="flex space-x-6 items-center">
                    <span class="control-btn" onclick="prev()">⏮️</span>
                    <span id="play-trigger" class="text-5xl cursor-pointer" onclick="toggleMain()">▶️</span>
                    <span class="control-btn" onclick="next()">⏭️</span>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-4 mt-4 border-t border-gray-700 pt-4">
                <div>
                    <label class="text-xs block mb-1">CROSSFADE (10s)</label>
                    <div id="cf-indicator" class="text-cyan-400 font-mono text-sm">AUTO-SYNC ON</div>
                </div>
                <div>
                    <label class="text-xs block mb-1">KARAOKE MODE</label>
                    <input type="range" min="0" max="1" step="0.1" value="0" oninput="setKaraoke(this.value)">
                </div>
            </div>
        </div>

        <script>
            let context, analyser, source, karaokeNode;
            let audio = new Audio();
            let playlist = [];
            let index = 0;
            let isPlaying = false;

            function initContext() {
                if (!context) {
                    context = new (window.AudioContext || window.webkitAudioContext)();
                    analyser = context.createAnalyser();
                    source = context.createMediaElementSource(audio);
                    
                    // ระบบตัดเสียงร้อง (Invert Phase Logic แบบจำลอง)
                    karaokeNode = context.createGain();
                    
                    source.connect(analyser);
                    analyser.connect(karaokeNode);
                    karaokeNode.connect(context.destination);
                    
                    drawVisual();
                }
            }

            function handleUpload(files) {
                initContext();
                playlist = Array.from(files);
                if(playlist.length > 0) playTrack(0);
            }

            function playTrack(i) {
                index = i;
                const file = playlist[index];
                audio.src = URL.createObjectURL(file);
                document.getElementById('track-name').innerText = file.name;
                audio.play();
                isPlaying = true;
                document.getElementById('play-trigger').innerText = "⏸️";
            }

            // ระบบ Crossfade 10 วินาทีก่อนจบ
            audio.ontimeupdate = () => {
                let timeLeft = audio.duration - audio.currentTime;
                if (timeLeft <= 10 && timeLeft > 0.5 && playlist.length > 1) {
                    document.getElementById('cf-indicator').innerText = "CROSSFADING...";
                    audio.volume = timeLeft / 10;
                } else {
                    audio.volume = 1;
                    document.getElementById('cf-indicator').innerText = "AUTO-SYNC ON";
                }
            };

            audio.onended = () => next();

            function toggleMain() {
                initContext();
                if(audio.paused) { audio.play(); isPlaying=true; document.getElementById('play-trigger').innerText="⏸️"; }
                else { audio.pause(); isPlaying=false; document.getElementById('play-trigger').innerText="▶️"; }
            }

            function next() { index = (index + 1) % playlist.length; playTrack(index); }
            function prev() { index = (index - 1 + playlist.length) % playlist.length; playTrack(index); }

            function setKaraoke(val) {
                // ปรับระดับเสียงกลางเพื่อจำลองการตัดเสียงร้อง
                if(karaokeNode) karaokeNode.gain.value = 1 - (val * 0.5);
            }

            function drawVisual() {
                const canvas = document.getElementById('visualizer');
                const ctx = canvas.getContext('2d');
                analyser.fftSize = 128;
                const bufferLength = analyser.frequencyBinCount;
                const dataArray = new Uint8Array(bufferLength);

                function render() {
                    requestAnimationFrame(render);
                    analyser.getByteFrequencyData(dataArray);
                    ctx.fillStyle = '#000';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    let barWidth = (canvas.width / bufferLength) * 2.5;
                    let x = 0;
                    for(let i=0; i<bufferLength; i++) {
                        let h = dataArray[i] / 2;
                        ctx.fillStyle = `hsl(${200 + i}, 100%, 50%)`;
                        ctx.fillRect(x, canvas.height - h, barWidth, h);
                        x += barWidth + 1;
                    }
                }
                render();
            }
        </script>
    </body>
    </html>
    """
    components.html(player_html, height=550, scrolling=True)
                
