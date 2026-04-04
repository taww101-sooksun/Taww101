import streamlit as st
import os 
import time
import base64
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from folium.features import DivIcon
from streamlit_folium import st_folium
from math import radians, cos, sin, asin, sqrt
import pytz
from timezonefinder import TimezoneFinder
from datetime import datetime
from streamlit_js_eval import get_geolocation 

# ==========================================
# 0. CONFIG & STYLE SYSTEM
# ==========================================
st.set_page_config(page_title="SYNAPSE OS อยู่นิ่งๆไม่เจ็บตัว", layout="wide", initial_sidebar_state="collapsed")

def apply_custom_background():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#1408BF"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {st.session_state.bg_color}44 !important;
            color: white !important;
        }}
        section[data-testid="stSidebar"] {{
            background-color: rgba(0,0,0,0.5);
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: rgba(255, 255, 255, 0.05) !important;
            border-radius: 12px !important;
            padding: 8px 16px !important;
            color: #BBBBBB !important;
            font-weight: bold !important;
            border: 4px solid transparent !important;
        }}
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            color: #FFFFFF !important;
            background-color: {st.session_state.theme_color}44 !important;
            border: 4px solid {st.session_state.theme_color} !important;
            box-shadow: 0 0 15px {st.session_state.theme_color} !important;
        }}
        div.stButton > button {{
            background-color: rgba(0, 0, 0, 0.8) !important;
            color: white !important;
            border: 4px solid {st.session_state.theme_color} !important;
            border-radius: 15px !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# 1. HELPER FUNCTIONS
# ==========================================
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon, dlat = lon2 - lon1, lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * 6371

def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#1408BF"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ ระบบเชื่อมต่อฐานข้อมูลขัดข้อง: {e}")

def get_local_time(lat, lon):
    try:
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=lat, lng=lon)
        if timezone_str:
            local_tz = pytz.timezone(timezone_str)
            return datetime.now(local_tz)
    except: pass
    return datetime.now(pytz.timezone('Asia/Bangkok'))

# ==========================================
# 2. ROOM MODULES
# ==========================================
def room_login():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color};'>SYNAPSE LOGIN</h1>", unsafe_allow_html=True)
        tab_l, tab_r = st.tabs(["🔑 UNLOCK SYSTEM", "📝 REGISTER AGENT"])
        with tab_l:
            with st.form("login"):
                uid = st.text_input("AGENT ID")
                pw = st.text_input("PASSWORD", type="password")
                if st.form_submit_button("ACCESS GRANTED", use_container_width=True):
                    user_data = db.reference(f'users/{uid}').get()
                    if user_data and user_data.get('pw') == pw:
                        st.session_state.user = uid
                        st.session_state.logged_in = True
                        st.rerun()
                    else: st.error("รหัสผ่านไม่ถูกต้อง")
        with tab_r:
            with st.form("reg"):
                new_id = st.text_input("NEW AGENT ID")
                new_pw = st.text_input("SET PASSWORD", type="password")
                if st.form_submit_button("CREATE ACCOUNT", use_container_width=True):
                    db.reference(f'users/{new_id}').set({'pw': new_pw, 'ts': time.time()})
                    st.success("ลงทะเบียนสำเร็จ!")

def room_core(loc):
    st.subheader("🏠 CORE CONTROL")
    lat, lon = 13.7367, 100.5231
    if loc and 'coords' in loc:
        lat = loc['coords'].get('latitude', lat)
        lon = loc['coords'].get('longitude', lon)
    
    current_time = get_local_time(lat, lon)
    st.markdown(f"""
        <div style="text-align:center; padding:30px; border:4px solid {st.session_state.theme_color}; border-radius:15px; background:rgba(0,0,0,0.3);">
            <h1 style="font-size:5em; color:{st.session_state.theme_color};">{current_time.strftime('%H:%M:%S')}</h1>
            <p>📍 LAT: {lat:.4f} | LON: {lon:.4f}</p>
        </div>
    """, unsafe_allow_html=True)

def room_radar(loc):
    st.subheader("🛰️ STRATEGIC GPS")
    my_lat, my_lon = 13.7367, 100.5231 
    if loc and 'coords' in loc:
        my_lat = loc['coords'].get('latitude', my_lat)
        my_lon = loc['coords'].get('longitude', my_lon)
    
    m = folium.Map(location=[my_lat, my_lon], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr='Google')
    folium.Marker([my_lat, my_lon], icon=folium.Icon(color='red', icon='star')).add_to(m)
    
    try:
        users_ref = db.reference('users').get()
        if users_ref:
            for uid, data in users_ref.items():
                if uid != st.session_state.user and 'lat' in data:
                    folium.Marker([data['lat'], data['lon']], tooltip=uid).add_to(m)
    except: pass
    
    st_folium(m, width="100%", height=400)
    if st.button("📡 BROADCAST LOCATION", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})

def room_music():
    st.subheader("🎧 SYNAPSE PRO AUDIO ENGINE - อยู่นิ่งๆไม่เจ็บตัว")
    
    # ส่วนแสดงไฟล์ในเครื่อง (แสดงชื่อเฉยๆ)
    music_files = sorted([f for f in os.listdir('.') if f.endswith((".mp3", ".wav"))])
    if music_files:
        with st.expander("📂 รายชื่อเพลงใน Server (Local Files)"):
            for f in music_files:
                st.write(f"🎵 {f}")
    
    player_html = """
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { background-color: transparent; color: white; font-family: sans-serif; }
            .player-card { background: rgba(13, 17, 23, 0.95); border: 2px solid #00ffc8; box-shadow: 0 0 25px #00ffc833; }
            #visualizer-canvas { background: #000; border-radius: 8px; height: 100px; width: 100%; border: 1px solid #333; }
            input[type="range"] { accent-color: #00ffc8; cursor: pointer; }
            label { font-size: 10px; color: #00ffc8; text-transform: uppercase; letter-spacing: 1px; }
        </style>
    </head>
    <body>
        <div class="player-card p-5 rounded-2xl w-full">
            <h2 class="text-center text-[#00ffc8] font-bold mb-4 tracking-widest">FX MASTER ENGINE</h2>
            
            <input type="file" id="file-input" multiple accept="audio/*" class="block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-[#00ffc8] file:text-black hover:file:bg-cyan-400 mb-6">

            <canvas id="visualizer-canvas" class="mb-4"></canvas>

            <div class="text-center mb-6">
                <p id="song-title" class="text-sm font-semibold truncate text-gray-300">WAITING FOR TRACK...</p>
                <div class="flex justify-center gap-4 mt-3">
                    <button id="play-pause-btn" class="bg-[#00ffc8] text-black px-8 py-2 rounded-full font-black hover:scale-105 transition-transform">PLAY / PAUSE</button>
                </div>
            </div>

            <div class="grid grid-cols-3 gap-4 mb-6 border-b border-gray-700 pb-4">
                <div><label>Bass</label><input type="range" id="low-gain" min="-15" max="15" value="0" class="w-full"></div>
                <div><label>Mid</label><input type="range" id="mid-gain" min="-15" max="15" value="0" class="w-full"></div>
                <div><label>High</label><input type="range" id="high-gain" min="-15" max="15" value="0" class="w-full"></div>
            </div>

            <div class="grid grid-cols-3 gap-4">
                <div><label>Distortion</label><input type="range" id="dist-gain" min="0" max="100" value="0" class="w-full"></div>
                <div><label>Echo/Delay</label><input type="range" id="echo-gain" min="0" max="0.8" step="0.1" value="0" class="w-full"></div>
                <div><label>Pan L/R</label><input type="range" id="pan-val" min="-1" max="1" step="0.1" value="0" class="w-full"></div>
            </div>

            <audio id="audio-element" class="hidden"></audio>
        </div>

        <script>
            const audio = document.getElementById('audio-element');
            const fileInput = document.getElementById('file-input');
            const playPauseBtn = document.getElementById('play-pause-btn');
            const canvas = document.getElementById('visualizer-canvas');
            const ctx = canvas.getContext('2d');
            
            let audioCtx, source, analyzer;
            let lowFilter, midFilter, highFilter;
            let distortNode, delayNode, feedbackGain, panNode;

            fileInput.onchange = (e) => {
                const file = e.target.files[0];
                if(file) {
                    audio.src = URL.createObjectURL(file);
                    document.getElementById('song-title').innerText = file.name;
                    setupAudio();
                }
            };

            function makeDistortionCurve(amount) {
                let k = typeof amount === 'number' ? amount : 50,
                    n_samples = 44100,
                    curve = new Float32Array(n_samples),
                    deg = Math.PI / 180, i = 0, x;
                for ( ; i < n_samples; ++i ) {
                    x = i * 2 / n_samples - 1;
                    curve[i] = ( 3 + k ) * x * 20 * deg / ( Math.PI + k * Math.abs(x) );
                }
                return curve;
            }

            function setupAudio() {
                if(!audioCtx) {
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    source = audioCtx.createMediaElementSource(audio);
                    analyzer = audioCtx.createAnalyser();
                    
                    // EQ Nodes
                    lowFilter = audioCtx.createBiquadFilter(); lowFilter.type = 'lowshelf'; lowFilter.frequency.value = 320;
                    midFilter = audioCtx.createBiquadFilter(); midFilter.type = 'peaking'; midFilter.frequency.value = 1000;
                    highFilter = audioCtx.createBiquadFilter(); highFilter.type = 'highshelf'; highFilter.frequency.value = 3200;

                    // FX Nodes
                    distortNode = audioCtx.createWaveShaper();
                    distortNode.oversample = '4x';
                    
                    delayNode = audioCtx.createDelay();
                    delayNode.delayTime.value = 0.3; 
                    feedbackGain = audioCtx.createGain();
                    feedbackGain.gain.value = 0; // Echo intensity

                    panNode = audioCtx.createStereoPanner();

                    // Routing: Source -> EQ -> Distortion -> Pan -> Analyzer -> Destination
                    // Echo Loop: Distortion -> Delay -> FeedbackGain -> Delay (Loop)
                    source.connect(lowFilter);
                    lowFilter.connect(midFilter);
                    midFilter.connect(highFilter);
                    highFilter.connect(distortNode);
                    
                    // Echo Path
                    distortNode.connect(delayNode);
                    delayNode.connect(feedbackGain);
                    feedbackGain.connect(delayNode);
                    feedbackGain.connect(panNode); // Echo output
                    
                    distortNode.connect(panNode); // Direct sound output
                    panNode.connect(analyzer);
                    analyzer.connect(audioCtx.destination);
                    
                    visualize();
                }
            }

            playPauseBtn.onclick = () => {
                if(audioCtx?.state === 'suspended') audioCtx.resume();
                audio.paused ? audio.play() : audio.pause();
            };

            function visualize() {
                analyzer.fftSize = 128;
                const bufferLength = analyzer.frequencyBinCount;
                const dataArray = new Uint8Array(bufferLength);

                function draw() {
                    requestAnimationFrame(draw);
                    analyzer.getByteFrequencyData(dataArray);
                    ctx.fillStyle = 'black';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    let barWidth = (canvas.width / bufferLength) * 2;
                    let x = 0;
                    for(let i = 0; i < bufferLength; i++) {
                        let barHeight = dataArray[i] / 2;
                        ctx.fillStyle = `rgb(0, ${dataArray[i]+100}, 200)`;
                        ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
                        x += barWidth + 1;
                    }
                }
                draw();
            }

            // Listeners
            document.getElementById('low-gain').oninput = (e) => lowFilter.gain.value = e.target.value;
            document.getElementById('mid-gain').oninput = (e) => midFilter.gain.value = e.target.value;
            document.getElementById('high-gain').oninput = (e) => highFilter.gain.value = e.target.value;
            
            document.getElementById('dist-gain').oninput = (e) => {
                distortNode.curve = e.target.value > 0 ? makeDistortionCurve(parseInt(e.target.value)) : null;
            };
            document.getElementById('echo-gain').oninput = (e) => feedbackGain.gain.value = e.target.value;
            document.getElementById('pan-val').oninput = (e) => panNode.pan.value = e.target.value;

        </script>
    </body>
    </html>
    """
    
    components.html(player_html, height=550, scrolling=False)


def room_camera(loc):
    st.subheader("📷 AGENT SCANNER")
    img = st.camera_input("SNAPSHOT")
    if img:
        st.image(img)
        if st.button("📤 UPLOAD TO CLOUD"):
            st.success("บันทึกสำเร็จ!")

def room_secure_chat():
    st.subheader("💬 SECURE CHAT")
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    target = st.selectbox("🎯 เลือกผู้รับ:", friends)
    if target:
        rid = "_".join(sorted([st.session_state.user, target]))
        msg = st.text_input("พิมพ์ข้อความ...")
        if st.button("SEND"):
            db.reference(f'private_rooms/{rid}').push({'u': st.session_state.user, 'm': msg, 'ts': time.time()})
            st.rerun()

def room_call():
    st.subheader("📞 P2P CALL")
    st.info("ระบบกำลังพัฒนาช่องทางการสื่อสาร")

# ==========================================
# 2.5 DJ CROSSFADE MODULE
# ==========================================
def room_dj_crossfade():
    st.subheader("🎚️ SYNAPSE CROSSFADE ENGINE - อยู่นิ่งๆไม่เจ็บตัว")
    
    dj_html = """
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { font-family: 'Inter', sans-serif; background-color: transparent; color: #AFEEEE; }
            .player-container {
                background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
                background-size: 1200% 1200%;
                animation: RainbowFlow 15s ease infinite;
                padding: 20px; border-radius: 20px; border: 4px solid #AFEEEE;
                box-shadow: 0 0 25px rgba(175, 238, 238, 0.4);
            }
            @keyframes RainbowFlow {
                0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%}
            }
            .btn-coral {
                background-color: #FF7F50 !important; color: white !important; font-weight: bold;
                border: 2px solid #AFEEEE !important; transition: 0.3s; width: 100%;
                padding: 10px; border-radius: 10px; cursor: pointer;
            }
            .progress-bg { background: rgba(0,0,0,0.5); height: 8px; border-radius: 4px; overflow: hidden; margin-top: 5px; }
            .progress-fill { background: #AFEEEE; height: 100%; width: 0%; transition: width 0.1s linear; }
            .track-box { background: rgba(0,0,0,0.3); padding: 10px; border-radius: 12px; margin-bottom: 10px; border: 1px solid rgba(175,238,238,0.2); }
        </style>
    </head>
    <body>
        <div class="player-container">
            <h2 class="text-xl font-bold mb-4 text-white text-center">DJ MONITOR SYSTEM</h2>
            
            <div class="track-box">
                <div class="flex justify-between text-xs mb-1">
                    <span>TRACK A: <span id="nameA">No File</span></span>
                    <span id="timeA">0:00 / 0:00</span>
                </div>
                <input type="file" id="fileA" accept="audio/*" class="text-[10px] mb-2" onchange="loadAudio(this.files[0], 'A')">
                <div class="progress-bg"><div id="fillA" class="progress-fill"></div></div>
            </div>

            <div class="track-box">
                <div class="flex justify-between text-xs mb-1">
                    <span>TRACK B: <span id="nameB">No File</span></span>
                    <span id="timeB">0:00 / 0:00</span>
                </div>
                <input type="file" id="fileB" accept="audio/*" class="text-[10px] mb-2" onchange="loadAudio(this.files[0], 'B')">
                <div class="progress-bg"><div id="fillB" class="progress-fill"></div></div>
            </div>

            <div class="grid grid-cols-2 gap-2 mt-4">
                <button id="start-btn" class="btn-coral" onclick="startPlayingA()" disabled>START PLAY</button>
                <button id="crossfade-btn" class="btn-coral" onclick="startCrossfade()" disabled>CROSSFADE</button>
            </div>
            
            <div class="mt-4 text-center text-xs bg-black/50 p-2 rounded-lg">
                STATUS: <span id="current-status">WAITING FILES</span> | 
                ACTIVE: <span id="current-song" class="text-[#FF7F50]">-</span>
            </div>
        </div>

        <script>
            let audioContext, songABuffer, songBBuffer, songASource, songBSource, songAGain, songBGain;
            let startTimeA, startTimeB, isPlaying = false, currentPlaying = 'None';

            function formatTime(seconds) {
                const min = Math.floor(seconds / 60);
                const sec = Math.floor(seconds % 60);
                return min + ":" + (sec < 10 ? '0' : '') + sec;
            }

            function updateUI() {
                if (!isPlaying || !audioContext) return;
                
                const now = audioContext.currentTime;
                
                if (songABuffer && songASource) {
                    const elapsedA = (now - startTimeA) % songABuffer.duration;
                    document.getElementById('fillA').style.width = (elapsedA / songABuffer.duration * 100) + "%";
                    document.getElementById('timeA').textContent = formatTime(elapsedA) + " / " + formatTime(songABuffer.duration);
                }
                
                if (songBBuffer && songBSource) {
                    const elapsedB = (now - startTimeB) % songBBuffer.duration;
                    document.getElementById('fillB').style.width = (elapsedB / songBBuffer.duration * 100) + "%";
                    document.getElementById('timeB').textContent = formatTime(elapsedB) + " / " + formatTime(songBBuffer.duration);
                }
                requestAnimationFrame(updateUI);
            }

            async function loadAudio(file, key) {
                if (!audioContext) audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const buffer = await audioContext.decodeAudioData(await file.arrayBuffer());
                if (key === 'A') { songABuffer = buffer; document.getElementById('nameA').textContent = file.name; }
                else { songBBuffer = buffer; document.getElementById('nameB').textContent = file.name; }
                if (songABuffer && songBBuffer) document.getElementById('start-btn').disabled = false;
            }

            function playTrack(buffer, gainVal) {
                const source = audioContext.createBufferSource();
                source.buffer = buffer; source.loop = true;
                const gain = audioContext.createGain();
                gain.gain.setValueAtTime(gainVal, audioContext.currentTime);
                source.connect(gain); gain.connect(audioContext.destination);
                source.start(0);
                return { source, gain };
            }

            function startPlayingA() {
                const now = audioContext.currentTime;
                const trackA = playTrack(songABuffer, 1.0);
                songASource = trackA.source; songAGain = trackA.gain; startTimeA = now;
                const trackB = playTrack(songBBuffer, 0.0);
                songBSource = trackB.source; songBGain = trackB.gain; startTimeB = now;
                isPlaying = true; currentPlaying = 'A';
                document.getElementById('current-song').textContent = 'A';
                document.getElementById('crossfade-btn').disabled = false;
                updateUI();
            }

            function startCrossfade() {
                const duration = 5; const now = audioContext.currentTime;
                if (currentPlaying === 'A') {
                    songAGain.gain.linearRampToValueAtTime(1, now);
                    songAGain.gain.linearRampToValueAtTime(0, now + duration);
                    songBGain.gain.linearRampToValueAtTime(0, now);
                    songBGain.gain.linearRampToValueAtTime(1, now + duration);
                    currentPlaying = 'B';
                } else {
                    songBGain.gain.linearRampToValueAtTime(1, now);
                    songBGain.gain.linearRampToValueAtTime(0, now + duration);
                    songAGain.gain.linearRampToValueAtTime(0, now);
                    songAGain.gain.linearRampToValueAtTime(1, now + duration);
                    currentPlaying = 'A';
                }
                document.getElementById('current-song').textContent = currentPlaying;
            }
        </script>
    </body>
    </html>
    """
               
    
    components.html(dj_html, height=650)

# ==========================================
# 3. MAIN SYSTEM
# ==========================================
def main():
    init_system()
    apply_custom_background()
    loc = get_geolocation()

    if not st.session_state.logged_in:
        room_login()
    else:
        tabs = st.tabs([
            "🏠 CORE", "🛰️ RADAR", "💬 CHAT", "📞 CALL", 
            "🎧 MUSIC", "⚙️ SETTINGS", "🎚️ DJ TOOLS", "📷 SCANNER"
        ])

        with tabs[0]: room_core(loc)
        with tabs[1]: room_radar(loc)
        with tabs[2]: room_secure_chat()
        with tabs[3]: room_call()
        with tabs[4]: room_music()
        with tabs[5]: st.subheader("🎨 SETTINGS")
        with tabs[6]: room_dj_crossfade()
        with tabs[7]: room_camera(loc)

if __name__ == "__main__":
    main()

                        
