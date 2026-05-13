import streamlit as st
import streamlit.components.v1 as components
import os
import base64

# ฟังก์ชันช่วยแปลงไฟล์ (ต้องมีอยู่ในโค้ดหลักของคุณ)
def get_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

# สมมติค่าตัวแปรเบื้องต้น
primary_neon = "#00FFCC"

if "page" not in st.session_state:
    st.session_state.page = "1"

if st.session_state.page == "1":
    st.markdown("<h2 style='color:#00FFCC; font-family:monospace;'>🎧 SYNAPSE DJ STATION V.3</h2>", unsafe_allow_html=True)
    
    all_songs = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
    
    if not all_songs:
        st.warning("⚠️ ไม่พบไฟล์ .mp3 ในระบบ")
    else:
        col_sel_a, col_sel_b = st.columns(2)
        with col_sel_a:
            song_a = st.selectbox("💿 DECK A (LEFT)", ["-- Select --"] + all_songs, key="sa")
        with col_sel_b:
            song_b = st.selectbox("💿 DECK B (RIGHT)", ["-- Select --"] + all_songs, key="sb")

        data_a = get_base64(song_a) if song_a != "-- Select --" else ""
        data_b = get_base64(song_b) if song_b != "-- Select --" else ""

        mixer_html = f"""
        <div style="background: #000; border: 2px solid {primary_neon}; border-radius: 20px; padding: 15px; font-family: monospace; color: white;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div style="border: 1px solid {primary_neon}; padding: 10px; border-radius: 15px; text-align: center;">
                    <div style="display: flex; justify-content: space-between; font-size: 10px; color: {primary_neon};">
                        <span id="curA">00:00</span><span id="remA">-00:00</span>
                    </div>
                    <canvas id="canvasA" style="width: 100%; height: 60px; background: #111; margin: 5px 0; border-radius:5px;"></canvas>
                    <input type="range" id="volA" min="0" max="1" step="0.01" value="0.7" style="width: 100%;">
                    <div style="margin-top: 10px;">
                        <button onclick="control('A', 'play')" style="background:{primary_neon}; border:none; padding:5px 10px; border-radius:5px; cursor:pointer;">PLAY</button>
                        <button onclick="control('A', 'pause')" style="background:none; border:1px solid {primary_neon}; color:{primary_neon}; padding:5px 10px; border-radius:5px; cursor:pointer;">PAUSE</button>
                    </div>
                </div>

                <div style="border: 1px solid #FF44CC; padding: 10px; border-radius: 15px; text-align: center;">
                    <div style="display: flex; justify-content: space-between; font-size: 10px; color: #FF44CC;">
                        <span id="curB">00:00</span><span id="remB">-00:00</span>
                    </div>
                    <canvas id="canvasB" style="width: 100%; height: 60px; background: #111; margin: 5px 0; border-radius:5px;"></canvas>
                    <input type="range" id="volB" min="0" max="1" step="0.01" value="0.7" style="width: 100%;">
                    <div style="margin-top: 10px;">
                        <button onclick="control('B', 'play')" style="background:#FF44CC; border:none; padding:5px 10px; border-radius:5px; color:white; cursor:pointer;">PLAY</button>
                        <button onclick="control('B', 'pause')" style="background:none; border:1px solid #FF44CC; color:#FF44CC; padding:5px 10px; border-radius:5px; cursor:pointer;">PAUSE</button>
                    </div>
                </div>
            </div>

            <div style="margin-top:20px; text-align:center;">
                <small>CROSSFADER (A <-> B)</small><br>
                <input type="range" id="fader" min="0" max="1" step="0.01" value="0.5" style="width: 80%;">
            </div>

            <audio id="audioA" src="data:audio/mp3;base64,{data_a}"></audio>
            <audio id="audioB" src="data:audio/mp3;base64,{data_b}"></audio>

            <script>
                const audA = document.getElementById('audioA');
                const audB = document.getElementById('audioB');
                const fader = document.getElementById('fader');
                let audioCtx;
                let analyserA, analyserB;
                let sourceA, sourceB;

                function initAudio() {{
                    if (!audioCtx) {{
                        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                        
                        // Setup Deck A
                        analyserA = audioCtx.createAnalyser();
                        sourceA = audioCtx.createMediaElementSource(audA);
                        sourceA.connect(analyserA);
                        analyserA.connect(audioCtx.destination);
                        
                        // Setup Deck B
                        analyserB = audioCtx.createAnalyser();
                        sourceB = audioCtx.createMediaElementSource(audB);
                        sourceB.connect(analyserB);
                        analyserB.connect(audioCtx.destination);

                        startVisualizer('canvasA', analyserA, '{primary_neon}');
                        startVisualizer('canvasB', analyserB, '#FF44CC');
                    }}
                }}

                function startVisualizer(canvasID, analyser, color) {{
                    const canvas = document.getElementById(canvasID);
                    const ctx = canvas.getContext('2d');
                    analyser.fftSize = 64;
                    const bufferLength = analyser.frequencyBinCount;
                    const dataArray = new Uint8Array(bufferLength);

                    function draw() {{
                        requestAnimationFrame(draw);
                        analyser.getByteFrequencyData(dataArray);
                        ctx.clearRect(0, 0, canvas.width, canvas.height);
                        let barWidth = (canvas.width / bufferLength) * 2.5;
                        let x = 0;
                        for(let i = 0; i < bufferLength; i++) {{
                            let barHeight = dataArray[i] / 5;
                            ctx.fillStyle = color;
                            ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
                            x += barWidth + 1;
                        }}
                    }}
                    draw();
                }}

                function control(deck, action) {{
                    initAudio();
                    if (audioCtx.state === 'suspended') audioCtx.resume();
                    const target = (deck === 'A') ? audA : audB;
                    if (action === 'play') target.play();
                    else target.pause();
                }}

                // Volume & Fader Logic
                function updateVolumes() {{
                    const volA = document.getElementById('volA').value;
                    const volB = document.getElementById('volB').value;
                    const f = parseFloat(fader.value);
                    audA.volume = volA * (1 - f);
                    audB.volume = volB * f;
                }}

                fader.oninput = updateVolumes;
                document.getElementById('volA').oninput = updateVolumes;
                document.getElementById('volB').oninput = updateVolumes;

                // Time Update
                const updateUI = (aud, cur, rem) => {{
                    aud.ontimeupdate = () => {{
                        const fmt = s => new Date(s * 1000).toISOString().substr(14, 5);
                        document.getElementById(cur).innerText = fmt(aud.currentTime);
                        if(aud.duration) document.getElementById(rem).innerText = "-" + fmt(aud.duration - aud.currentTime);
                    }};
                }}
                updateUI(audA, 'curA', 'remA');
                updateUI(audB, 'curB', 'remB');
            </script>
        </div>
        """
        components.html(mixer_html, height=450)
        st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | Tactical Sound Module v4.2")
