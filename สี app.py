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
# 2. CORE MODULES (เพิ่มห้อง DJ CROSSFADE)
# ==========================================

def room_dj_crossfade():
    st.subheader("🎚️ SYNAPSE CROSSFADE ENGINE - อยู่นิ่งๆไม่เจ็บตัว")
    
    # โค้ด HTML ที่รวมชุดสีรุ้งวิ่งและ UI ที่คุณต้องการ
    dj_html = """
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body { font-family: 'Inter', sans-serif; background-color: transparent; color: #AFEEEE; }
            
            /* ตัวเครื่องเล่นแบบ Rainbow Flow */
            .player-container {
                background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
                background-size: 1200% 1200%;
                animation: RainbowFlow 15s ease infinite;
                padding: 24px;
                border-radius: 20px;
                border: 4px solid #AFEEEE;
                box-shadow: 0 0 25px rgba(175, 238, 238, 0.4);
            }

            @keyframes RainbowFlow {
                0%{background-position:0% 50%}
                50%{background-position:100% 50%}
                100%{background-position:0% 50%}
            }

            /* ปุ่มสี Coral */
            .btn-coral {
                background-color: #FF7F50 !important;
                color: white !important;
                font-weight: bold;
                border: 2px solid #AFEEEE !important;
                transition: 0.3s;
                width: 100%;
                padding: 12px;
                border-radius: 10px;
                margin-bottom: 10px;
            }
            .btn-coral:hover { filter: brightness(1.2); box-shadow: 0 0 15px #FF7F50; }
            .btn-coral:disabled { background-color: #555 !important; border-color: #333 !important; }

            #lyrics-container { background: rgba(0, 0, 0, 0.7); border-radius: 15px; padding: 15px; margin-top: 20px; border: 1px solid #AFEEEE; }
        </style>
    </head>
    <body>
        <div class="player-container">
            <h2 class="text-2xl font-bold mb-4 text-white text-center">CROSSFADE SYSTEM</h2>
            
            <div class="space-y-4 mb-6">
                <input type="file" id="fileA" accept="audio/*" class="text-xs text-white mb-2" onchange="loadAudio(this.files[0], 'A')">
                <input type="file" id="fileB" accept="audio/*" class="text-xs text-white" onchange="loadAudio(this.files[0], 'B')">
            </div>

            <button id="start-btn" class="btn-coral" onclick="startPlayingA()" disabled>START TRACK A</button>
            <button id="crossfade-btn" class="btn-coral" onclick="startCrossfade()" disabled>CROSSFADE TO B</button>
            <button id="vocal-btn" class="btn-coral" onclick="toggleVocalRemoval()" disabled>VOCAL REMOVER</button>

            <div id="lyrics-container">
                <p class="text-sm">STATUS: <span id="current-status" class="text-white">WAITING...</span></p>
                <p class="text-sm">PLAYING: <span id="current-song" class="text-white">-</span></p>
            </div>
        </div>

        <script>
            // (ใส่ JavaScript ของคุณที่นี่ - เหมือนในไฟล์ HTML เดิมเป๊ะๆ)
            // ... (โค้ด AudioContext, loadAudio, startCrossfade ที่คุณส่งมา<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>เครื่องมือผสมเพลงแบบไร้รอยต่อ</title>
    <!-- Load Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Custom styles for aesthetic */
        body {
            font-family: 'Inter', sans-serif;
            background-color: #0d1117;
            color: #c9d1d9;
        }
        .lyrics-block pre {
             /* Preserve formatting while allowing wrapping */
            white-space: pre-wrap;
            word-wrap: break-word;
        }
    </style>
</head>
<body class="p-4 md:p-8">

    <div class="max-w-xl mx-auto bg-[#161b22] p-6 rounded-xl shadow-2xl border border-[#30363d]">
        <h1 class="text-3xl font-bold mb-4 text-[#58a6ff]">เครื่องมือผสมเพลง Crossfade</h1>
        <p class="mb-6 text-sm text-[#8b949e]">โหลดเพลง A และเพลง B เพื่อทดลองการเปลี่ยนผ่านเสียงแบบเนียน (Crossfade) โดยใช้ Web Audio API</p>

        <!-- Status Display -->
        <div id="status-box" class="mb-4 p-3 bg-[#21262d] rounded-lg border border-[#30363d]">
            <p class="text-sm font-medium">สถานะ: <span id="current-status" class="text-yellow-400">รอการโหลดไฟล์</span></p>
            <p class="text-sm font-medium">เพลงปัจจุบัน: <span id="current-song" class="text-blue-400">-</span></p>
        </div>

        <!-- File Inputs -->
        <div class="space-y-4 mb-6">
            <div>
                <label for="fileA" class="block text-sm font-medium mb-1">เลือกเพลง A (ไฟล์ .mp3/.wav)</label>
                <input type="file" id="fileA" accept="audio/*" class="w-full text-sm text-gray-400
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-full file:border-0
                    file:text-sm file:font-semibold
                    file:bg-purple-600 file:text-white
                    hover:file:bg-purple-700
                    cursor-pointer" onchange="loadAudio(this.files[0], 'A')">
            </div>
            <div>
                <label for="fileB" class="block text-sm font-medium mb-1">เลือกเพลง B (ไฟล์ .mp3/.wav)</label>
                <input type="file" id="fileB" accept="audio/*" class="w-full text-sm text-gray-400
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-full file:border-0
                    file:text-sm file:font-semibold
                    file:bg-purple-600 file:text-white
                    hover:file:bg-purple-700
                    cursor-pointer" onchange="loadAudio(this.files[0], 'B')">
            </div>
        </div>

        <!-- Controls -->
        <div class="flex flex-col space-y-3">
            <button id="start-btn" onclick="startPlayingA()" disabled
                class="w-full py-3 px-4 bg-green-600 text-white font-bold rounded-lg shadow-md hover:bg-green-700 transition duration-150 disabled:bg-gray-500">
                เริ่มเล่นเพลง A
            </button>
            
            <label for="fade-duration-input" class="block text-sm font-medium pt-2">ระยะเวลา Crossfade (วินาที): <span id="fade-duration-value">10</span></label>
            <input type="range" id="fade-duration-input" min="1" max="10" value="10" step="0.5" 
                   oninput="document.getElementById('fade-duration-value').textContent = this.value"
                   class="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer range-lg">

            <button id="crossfade-btn" onclick="startCrossfade()" disabled
                class="w-full py-3 px-4 bg-orange-600 text-white font-bold rounded-lg shadow-md hover:bg-orange-700 transition duration-150 disabled:bg-gray-500">
                เริ่ม Crossfade ไปยังเพลง B
            </button>

            <!-- Vocal Removal Button -->
            <button id="vocal-btn" onclick="toggleVocalRemoval()" disabled
                class="w-full py-3 px-4 bg-blue-600 text-white font-bold rounded-lg shadow-md hover:bg-blue-700 transition duration-150 disabled:bg-gray-500">
                เปิด เอฟเฟกต์แยกเสียงร้อง (คาราโอเกะ)
            </button>

        </div>

        <!-- Lyrics Display Area -->
        <div id="lyrics-container" class="mt-8 p-4 bg-[#21262d] rounded-xl border border-[#30363d] h-[300px] overflow-y-auto hidden">
            <h2 class="text-xl font-bold mb-3 text-white">เนื้อเพลง</h2>
            
            <div id="lyrics-A" class="lyrics-block hidden">
                <p class="font-semibold text-purple-400 mb-2">เพลง A: ไม่มีเนื้อเพลงที่ระบุ (Placeholder)</p>
                <pre class="text-sm leading-relaxed text-gray-300">
ไม่มีเนื้อเพลงสำหรับเพลง A (Placeholder)

คุณสามารถเพิ่มเนื้อเพลงที่ถูกต้องสำหรับไฟล์ที่คุณโหลดได้ที่นี่!
</pre>
            </div>

            <div id="lyrics-B" class="lyrics-block hidden">
                <p class="font-semibold text-purple-400 mb-2">เพลง B: เพลงตัวอย่าง (Placeholder Lyrics)</p>
                <pre class="text-sm leading-relaxed text-gray-300">
เนื้อเพลงสำหรับเพลง B ยังไม่มีข้อมูล
คุณสามารถเพิ่มเนื้อเพลงที่ถูกต้องสำหรับไฟล์ที่คุณโหลดได้ที่นี่!

***
เมื่อเพลง B ถูกเปิด เนื้อเพลงนี้จะปรากฏขึ้น
เพื่อให้คุณสามารถร้องตามได้อย่างสนุกสนาน
</pre>
            </div>
        </div>
    </div>

    <script>
        // Global variables for Web Audio API
        let audioContext;
        let songABuffer = null;
        let songBBuffer = null;
        let songASource = null;
        let songBSource = null;
        let songAGain = null;
        let songBGain = null;
        let isPlaying = false;
        let currentPlaying = 'None';

        // Variables for Vocal Removal Effect
        let isVocalEffectActive = false;
        let vocalEffectChainA = null;
        let vocalEffectChainB = null;

        // --- Utility Functions ---

        /**
         * Initializes the AudioContext if it hasn't been created yet.
         * (เริ่มต้น AudioContext หากยังไม่ได้สร้าง)
         */
        function initAudioContext() {
            if (!audioContext) {
                const AudioContextClass = window.AudioContext || window.webkitAudioContext;
                if (!AudioContextClass) {
                    updateStatus('Error', 'เบราว์เซอร์ไม่รองรับ Web Audio API', 'text-red-500');
                    return;
                }
                audioContext = new AudioContextClass();
                console.log("AudioContext initialized.");
            }
        }
        
        /**
         * Updates the lyrics display based on the currently playing song key.
         * (อัปเดตการแสดงเนื้อเพลงตามเพลงที่กำลังเล่น)
         */
        function updateLyricsDisplay(songKey) {
            const container = document.getElementById('lyrics-container');
            const lyricsA = document.getElementById('lyrics-A');
            const lyricsB = document.getElementById('lyrics-B');
            
            // Hide all blocks first
            lyricsA.classList.add('hidden');
            lyricsB.classList.add('hidden');

            if (songKey === 'A') {
                container.classList.remove('hidden');
                lyricsA.classList.remove('hidden');
                container.scrollTop = 0; // Scroll to top when new song starts
            } else if (songKey === 'B') {
                container.classList.remove('hidden');
                lyricsB.classList.remove('hidden');
                container.scrollTop = 0; // Scroll to top when new song starts
            } else {
                 container.classList.add('hidden');
            }
        }


        /**
         * Updates the status display on the UI.
         * (อัปเดตสถานะบนหน้าจอ)
         */
        function updateStatus(status, song, colorClass = 'text-yellow-400') {
            document.getElementById('current-status').textContent = status;
            document.getElementById('current-status').className = colorClass;
            document.getElementById('current-song').textContent = song;
            currentPlaying = song;

            // Enable/Disable controls based on state (เปิด/ปิดปุ่มควบคุมตามสถานะ)
            const startBtn = document.getElementById('start-btn');
            const crossfadeBtn = document.getElementById('crossfade-btn');
            const vocalBtn = document.getElementById('vocal-btn');

            // Logic to disable buttons when files are not ready
            if (songABuffer && songBBuffer) {
                startBtn.disabled = isPlaying;
                
                // Disable crossfade if not playing or if effect is active
                crossfadeBtn.disabled = !isPlaying || isVocalEffectActive;

                // Disable vocal button if no song is playing
                vocalBtn.disabled = !isPlaying;
            } else {
                startBtn.disabled = true;
                crossfadeBtn.disabled = true;
                vocalBtn.disabled = true;
            }

            // Update vocal button text
            if (isVocalEffectActive) {
                vocalBtn.textContent = 'ปิด เอฟเฟกต์แยกเสียงร้อง (คาราโอเกะ)';
            } else {
                vocalBtn.textContent = 'เปิด เอฟเฟกต์แยกเสียงร้อง (คาราโอเกะ)';
            }
            
            // NEW: Update Lyrics Display
            if (isPlaying) {
                updateLyricsDisplay(song); 
            } else {
                updateLyricsDisplay('None');
            }
        }

        /**
         * Converts file to ArrayBuffer and decodes it using AudioContext.
         * (โหลดและถอดรหัสไฟล์เสียง)
         */
        function loadAudio(file, songKey) {
            if (!file) {
                updateStatus('ไฟล์ไม่ถูกต้อง', currentPlaying, 'text-red-500');
                return;
            }
            initAudioContext();
            updateStatus(`กำลังโหลด ${songKey}...`, currentPlaying, 'text-yellow-400');

            const reader = new FileReader();
            reader.onload = async (e) => {
                try {
                    const arrayBuffer = e.target.result;
                    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

                    if (songKey === 'A') {
                        songABuffer = audioBuffer;
                    } else {
                        songBBuffer = audioBuffer;
                    }

                    const fileName = file.name;
                    updateStatus(`โหลด ${songKey} (${fileName}) สำเร็จ`, currentPlaying, 'text-green-400');

                    if (songABuffer && songBBuffer) {
                        updateStatus('พร้อมเล่น', currentPlaying, 'text-lime-400');
                        document.getElementById('start-btn').disabled = false;
                    }

                } catch (error) {
                    console.error("Error decoding audio data:", error);
                    updateStatus(`ไม่สามารถถอดรหัสไฟล์ ${songKey} ได้`, currentPlaying, 'text-red-500');
                }
            };
            reader.onerror = (e) => {
                console.error("File reading error:", e);
                updateStatus(`ข้อผิดพลาดในการอ่านไฟล์ ${songKey}`, currentPlaying, 'text-red-500');
            };

            reader.readAsArrayBuffer(file);
        }

        /**
         * Creates a new source and gain structure for a song.
         * @param {AudioBuffer} buffer The audio buffer to play.
         * @param {number} startGain Initial gain (0.0 to 1.0).
         * @returns {object} {source: AudioBufferSourceNode, gain: GainNode}
         * (สร้าง Source และ Gain Node สำหรับเล่นเพลง)
         */
        function playSong(buffer, startGain) {
            if (!buffer || !audioContext) return null;

            // 1. Create Source Node
            const source = audioContext.createBufferSource();
            source.buffer = buffer;
            source.loop = true; 

            // 2. Create Gain Node
            const gainNode = audioContext.createGain();
            gainNode.gain.setValueAtTime(startGain, audioContext.currentTime);

            // 3. Connect: Source -> Gain -> Destination (speakers)
            // Initially connect directly to destination. This connection will be modified by the effect.
            source.connect(gainNode);
            gainNode.connect(audioContext.destination);

            // 4. Start playback
            source.start();

            return { source, gain: gainNode };
        }

        /**
         * Starts playing Song A for the first time, initializing A full volume and B muted.
         * (เริ่มเล่นเพลง A เป็นครั้งแรก)
         */
        function startPlayingA() {
            initAudioContext();
            if (!songABuffer || !songBBuffer) {
                updateStatus('กรุณาโหลดทั้งเพลง A และ B ก่อน', currentPlaying, 'text-red-500');
                return;
            }

            // Stop any existing playback and reset effect state
            if (songASource) songASource.stop();
            if (songBSource) songBSource.stop();
            isVocalEffectActive = false; // Reset effect state

            // Play Song A at full volume (1.0)
            const songA = playSong(songABuffer, 1.0);
            songASource = songA.source;
            songAGain = songA.gain;

            // Initialize Song B components (started but muted)
            const songB = playSong(songBBuffer, 0.0);
            songBSource = songB.source;
            songBGain = songB.gain;

            isPlaying = true;
            updateStatus('กำลังเล่น', 'A', 'text-green-500'); // This updates currentPlaying and calls updateLyricsDisplay
        }

        /**
         * Triggers the smooth crossfade from the current song to the other song.
         * (เริ่ม Crossfade อย่างราบรื่นไปยังเพลงถัดไป)
         */
        function startCrossfade() {
            if (!isPlaying || !audioContext) return;
            
            // SECURITY CHECK: Must disable effect before crossfade
            if (isVocalEffectActive) {
                updateStatus('กรุณาปิดเอฟเฟกต์แยกเสียงร้องก่อนเริ่ม Crossfade', currentPlaying, 'text-red-500');
                return;
            }

            const fadeDuration = parseFloat(document.getElementById('fade-duration-input').value);
            const startTime = audioContext.currentTime;
            
            if (!songAGain || !songBGain) return;

            updateStatus(`กำลัง Crossfade (${fadeDuration} วิ...)`, currentPlaying, 'text-orange-400');
            document.getElementById('crossfade-btn').disabled = true;
            document.getElementById('crossfade-btn').textContent = 'กำลัง Crossfade...';

            if (currentPlaying === 'A') {
                // Crossfade from A to B
                // 1. Fade A out smoothly (ramp gain from 1.0 to 0.0)
                songAGain.gain.linearRampToValueAtTime(1.0, startTime);
                songAGain.gain.linearRampToValueAtTime(0.0, startTime + fadeDuration);

                // 2. Fade B in smoothly (ramp gain from 0.0 to 1.0)
                songBGain.gain.linearRampToValueAtTime(0.0, startTime);
                songBGain.gain.linearRampToValueAtTime(1.0, startTime + fadeDuration);

                setTimeout(() => {
                    // Stop Song A completely and reset source/gain
                    songASource.stop();
                    const newSongA = playSong(songABuffer, 0.0);
                    songASource = newSongA.source;
                    songAGain = newSongA.gain;
                    
                    updateStatus('กำลังเล่น', 'B', 'text-green-500'); // This updates currentPlaying and calls updateLyricsDisplay
                    document.getElementById('crossfade-btn').disabled = false;
                    document.getElementById('crossfade-btn').textContent = 'เริ่ม Crossfade ไปยังเพลง A'; 
                }, fadeDuration * 1000);

            } else if (currentPlaying === 'B') {
                // Crossfade from B to A
                // 1. Fade B out smoothly
                songBGain.gain.linearRampToValueAtTime(1.0, startTime);
                songBGain.gain.linearRampToValueAtTime(0.0, startTime + fadeDuration);

                // 2. Fade A in smoothly
                songAGain.gain.linearRampToValueAtTime(0.0, startTime);
                songAGain.gain.linearRampToValueAtTime(1.0, startTime + fadeDuration);

                setTimeout(() => {
                    // Stop Song B completely and reset source/gain
                    songBSource.stop();
                    const newSongB = playSong(songBBuffer, 0.0);
                    songBSource = newSongB.source;
                    songBGain = newSongB.gain;

                    updateStatus('กำลังเล่น', 'A', 'text-green-500'); // This updates currentPlaying and calls updateLyricsDisplay
                    document.getElementById('crossfade-btn').disabled = false;
                    document.getElementById('crossfade-btn').textContent = 'เริ่ม Crossfade ไปยังเพลง B'; 
                }, fadeDuration * 1000);
            }
        }

        /**
         * Toggles the Stereo Phase Cancellation effect (Karaoke/Vocal Removal).
         * (เปิด/ปิด เอฟเฟกต์แยกเสียงร้อง)
         */
        function toggleVocalRemoval() {
            initAudioContext();
            if (!songAGain || !songBGain || !isPlaying) return;

            const activeGain = (currentPlaying === 'A') ? songAGain : songBGain;
            const inactiveGain = (currentPlaying === 'A') ? songBGain : songAGain;
            
            // Check if the current song is playing at full volume (prevent running during crossfade)
            if (Math.abs(activeGain.gain.value - 1.0) > 0.1 || inactiveGain.gain.value > 0.1) {
                updateStatus('กรุณาเล่นเพลงเต็มเสียง (1.0) ก่อนใช้อีเฟกต์', currentPlaying, 'text-red-500');
                return;
            }

            const activeEffectChain = (currentPlaying === 'A') ? vocalEffectChainA : vocalEffectChainB;
            
            isVocalEffectActive = !isVocalEffectActive;

            if (isVocalEffectActive) {
                // --- ACTIVATE VOCAL REMOVAL ---
                
                // 1. Disconnect the currently active gain from the final destination
                activeGain.disconnect(audioContext.destination);

                // 2. Create the nodes for phase inversion (Vocal Removal)
                const splitter = audioContext.createChannelSplitter(2);
                const merger = audioContext.createChannelMerger(2);
                const inverter = audioContext.createGain();
                inverter.gain.setValueAtTime(-1, audioContext.currentTime); // Invert phase

                // Store nodes
                if (currentPlaying === 'A') {
                    vocalEffectChainA = { splitter, merger, inverter };
                } else {
                    vocalEffectChainB = { splitter, merger, inverter };
                }
                
                // 3. Connect: Gain -> Splitter
                activeGain.connect(splitter);
                
                // 4. Connect Splitter Channel 0 (Left) to Merger Channel 0 (Left) (straight)
                splitter.connect(merger, 0, 0);

                // 5. Connect Splitter Channel 1 (Right) -> Inverter -> Merger Channel 0 (Left)
                // This mixes the inverted Right channel into the Left channel, cancelling centered sounds.
                // Output is now mono.
                splitter.connect(inverter, 1, 0);
                inverter.connect(merger, 0, 0);

                // 6. Connect the output of the Merger to both channels of the destination
                merger.connect(audioContext.destination);

                updateStatus('เอฟเฟกต์แยกเสียงร้อง: เปิด', currentPlaying, 'text-purple-400');

            } else {
                // --- DEACTIVATE VOCAL REMOVAL ---
                
                // 1. Disconnect active gain from the splitter, and merger from destination
                if (activeEffectChain) {
                    activeGain.disconnect(); // Disconnect everything from the gain
                    activeEffectChain.merger.disconnect(audioContext.destination);
                }

                // 2. Restore direct connection
                activeGain.connect(audioContext.destination);
                
                // 3. Clear the effect chain for the current song
                if (currentPlaying === 'A') {
                    vocalEffectChainA = null;
                } else {
                    vocalEffectChainB = null;
                }

                updateStatus('กำลังเล่น', currentPlaying, 'text-green-500');
            }
        }
    </script>
</body>
</html>


) ...
        </script>
    </body>
    </html>
    """
    components.html(dj_html, height=700)

# ==========================================
# 3. MAIN SYSTEM (ปรับการแสดงผล Tab)
# ==========================================
def main():
    # ... (โค้ด init_system, apply_custom_background เดิม) ...
    
    tabs = st.tabs([
        "🏠 CORE", "🛰️ RADAR", "💬 CHAT", "📞 CALL", 
        "🎧 MUSIC", "⚙️ SETTINGS", "🎚️ DJ TOOLS", "📷 SCANNER"
    ])

    with tabs[0]: room_core(loc)
    with tabs[1]: room_radar(loc)
    with tabs[2]: room_secure_chat()
    with tabs[3]: room_call()
    with tabs[4]: 
    with tabs[5]: room_music()
    with tabs[6]: room_dj_crossfade() 
    with tabs[7]: room_dj_crossfade()    
    w
    room_dj_crossfade() # <-- ใส่ต่อท้ายตรงนี้ (ห้ามเยื้องออกจากแนว with เดิม)
    with tabs[7]:
        room_camera(loc)
