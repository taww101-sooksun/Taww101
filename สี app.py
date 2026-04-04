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

# --- จุดสำคัญ: ต้อง Import แบบนี้เท่านั้น ---
from streamlit_js_eval import get_geolocation 
def apply_custom_background():
    # 1. เช็กก่อนว่ามีตัวแปรสีในระบบหรือยัง ถ้าไม่มีให้ตั้งค่าเริ่มต้นไว้ (กันเจ็บตัว!)
    if 'bg_color' not in st.session_state:
        st.session_state.bg_color = "#0e1117"  # ใส่สีพื้นฐานที่คุณชอบไว้ตรงนี้

    # 2. แก้ไข f-string ให้ถูกต้อง (ใส่ชื่อตัวแปร และใช้ปีกกา 2 ชั้นสำหรับ CSS)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {st.session_state.bg_color}44 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
        }}

        /* ตัวอักษรในเมนู */
        .stTabs [data-baseweb="tab"] {{
            background-color: rgba(255, 255, 255, 0.05) !important;
            border-radius: 12px !important;
            padding: 8px 16px !important;
            height: 50px !important;
            color: #BBBBBB !important; /* สีเทาอ่อนตอนยังไม่เลือก */
            font-weight: bold !important;
            transition: all 0.3s ease !important;
            border: 4px solid transparent !important;
        }}

        /* เมนูห้องตอนที่ถูกเลือก (Selected Tab) */
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            color: #FFFFFF !important; /* ตัวหนังสือขาวชัดเจน */
            background-color: {st.session_state.}44 !important;
            border: 4px solid {st.session_state.theme_color} !important;
            box-shadow: 0 0 15px {st.session_state.theme_color} !important; /* ไฟนีออนรอบเมนูที่เลือก */
            transform: scale(1.05); /* นูนออกมานิดนึง */
        }}

        /* เส้นใต้เมนูที่เลือก (ไฟวิ่งด้านล่าง) */
        .stTabs [data-baseweb="tab-highlight"] {{
            background-color: #FFFFFF !important;
            height: 10px !important;
            box-shadow: 0 0 10px #FFFFFF !important;
        }}

        /* 3. ปรับแต่งปุ่มทั่วไป (นูนมีไฟเหมือนเดิม) */
        div.stButton > button {{
            background-color: rgba(0, 0, 0, 0.8) !important;
            color: white !important;
            border: 4px solid {st.session_state.theme_color} !important;
            border-radius: 15px !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5) !important;
            filter: drop-shadow(0 0 5px {st.session_state.theme_color});
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# ==========================================
# 0. CONFIG & INITIALIZATION
# ==========================================
st.set_page_config(page_title="SYNAPSE OS อยู่นิ้งๆไม่้จ็บตัว", layout="wide", initial_sidebar_state="collapsed")

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon, dlat = lon2 - lon1, lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * 6371

def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#1408BF"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    
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
# 1. AUTHENTICATION
# ==========================================
def room_login():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color}; letter-spacing: 5px;'>SYNAPSE LOGIN</h1>", unsafe_allow_html=True)
        tab_l, tab_r = st.tabs(["🔑 UNLOCK SYSTEM", "📝 REGISTER AGENT"])
        with tab_l:
            with st.form("login"):
                uid = st.text_input("AGENT ID ใสชื่อผู้ใช่")
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

# ==========================================
# 2. CORE MODULES
# ==========================================
def room_core(loc):
    st.subheader("🏠 CORE CONTROL อยู่นิ้งๆไม่เจ็บตัว 🇹🇭")
    lat, lon = 13.7367, 100.5231
    if loc and 'coords' in loc:
        lat = loc['coords'].get('latitude', lat)
        lon = loc['coords'].get('longitude', lon)
    
    current_time = get_local_time(lat, lon)
    st.markdown(f"""
        <div style="text-align:center; padding:30px; border:4px solid {st.session_state.theme_color}; border-radius:15px; background:rgba(0,0,0,0.3); box-shadow: 0 0 20px {st.session_state.theme_color}44;">
            <h1 style="font-size:5em; color:{st.session_state.theme_color}; margin:0; font-family: monospace;">{current_time.strftime('%H:%M:%S')}</h1>
            <p style="color:#888; letter-spacing: 2px;">📍 LAT: {lat:.4f} | LON: {lon:.4f}</p>
            <p style="color:{st.session_state.theme_color}; font-weight:bold;">AGENT {st.session_state.user} ONLINE</p>
        </div>
    """, unsafe_allow_html=True)
def room_radar(loc):
    st.subheader("🛰️ STRATEGIC GPS - ระบบติดตามพิกัดเครือข่าย AGENT อยู่นิ้งๆไม่เจ็บตัว📡")
    
    # 1. พิกัดตัวเรา
    my_lat, my_lon = 13.7367, 100.5231 
    if loc and 'coords' in loc:
        my_lat = loc['coords'].get('latitude', my_lat)
        my_lon = loc['coords'].get('longitude', my_lon)
    
    # สร้าง Container แผนที่ให้นูนมีไฟ (เปิด div)
    st.markdown(f'<div style="border: 2px solid {st.session_state.theme_color}; border-radius: 15px; overflow: hidden; box-shadow: 0 0 20px {st.session_state.theme_color}88;">', unsafe_allow_html=True)
    
    # 2. สร้างแผนที่ดาวเทียม
    m = folium.Map(
        location=[my_lat, my_lon], 
        zoom_start=15, 
        tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
        attr='Google Satellite'
    )
    
    # Marker ของตัวเรา (สีแดง)
    folium.Marker(
        [my_lat, my_lon], 
        icon=folium.Icon(color='red', icon='star'), 
        tooltip="YOU (ฉันเอง)"
    ).add_to(m)

    # ลูกเล่น: วงรัศมีเรดาร์รอบตัวเรา
    folium.Circle(
        location=[my_lat, my_lon],
        radius=1000,
        color=st.session_state.theme_color,
        fill=True,
        fill_color=st.session_state.theme_color,
        fill_opacity=0.1,
        weight=2
    ).add_to(m)
    
    # 3. ดึงข้อมูล AGENT คนอื่นๆ และลากเส้น
    try:
        users_ref = db.reference('users').get()
        if users_ref:
            for uid, data in users_ref.items():
                if uid != st.session_state.user and 'lat' in data and 'lon' in data:
                    u_lat, u_lon = data['lat'], data['lon']
                    dist = haversine(my_lat, my_lon, u_lat, u_lon)
                    
                    # วาง Marker เพื่อน
                    folium.Marker(
                        [u_lat, u_lon], 
                        icon=folium.Icon(color='green', icon='info-sign'), 
                        tooltip=f"AGENT: {uid} | ห่าง: {dist:.2f} กม."
                    ).add_to(m)
                    
                    # ลากเส้นเชื่อมโยง
                    folium.PolyLine(
                        [[my_lat, my_lon], [u_lat, u_lon]], 
                        color=st.session_state.theme_color, 
                        weight=2, 
                        dash_array='10', 
                        opacity=0.6
                    ).add_to(m)
    except: pass
    
    # แสดงแผนที่
    st_folium(m, width="100%", height=250, returned_objects=[])
    
    # ปิด Container (สำคัญมาก!)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 4. ปุ่มส่งพิกัด (เพื่อให้เพื่อนเห็นเรา)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📡 BROADCAST MY LOCATION", key="btn_broadcast", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({
            'lat': my_lat, 
            'lon': my_lon, 
            'ts': time.time()
        })
        st.toast("ส่งพิกัดสำเร็จ! เพื่อนๆ จะเห็นคุณบนเรดาร์")
# --- แก้บรรทัดนี้ ---
def room_camera(loc): 
    st.subheader("📷 AGENT SCANNER - อยู่นื้งๆไม่เจ็บตัว🎬")
    
    # ดึงค่าพิกัดมาเตรียมไว้ (กันเหนียวถ้า loc เป็น None)
    lat = loc['coords'].get('latitude', 0) if loc else 0
    lon = loc['coords'].get('longitude', 0) if loc else 0

    img_file = st.camera_input("TAKE A SNAPSHOT")

    if img_file:
        # --- ลูกเล่น HUD แบบที่ 2 (แสดงผลบนหน้าจอ) ---
        st.markdown(f"""
            <div style="position: relative; text-align: center; color: {st.session_state.theme_color};">
                <div style="position: absolute; top: 10px; left: 20px; text-shadow: 2px 2px #000; font-family: monospace; text-align: left; font-size: 12px;">
                    🔴 RECORDING...<br>
                    AGENT: {st.session_state.user}<br>
                    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </div>
                <div style="position: absolute; bottom: 10px; right: 20px; text-shadow: 2px 2px #000; font-family: monospace; text-align: right; font-size: 12px;">
                    LOC: {lat:.4f}, {lon:.4f}<br>
                    STATUS: SYNAPSE_OS_ONLINE
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.image(img_file, use_container_width=True)
        # --- จบลูกเล่น HUD ---

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 UPLOAD TO CLOUD", use_container_width=True):
                # โค้ดส่วนอัปโหลด (เหมือนเดิมที่คุณมี)
                bytes_data = img_file.getvalue()
                base64_image = base64.b64encode(bytes_data).decode()
                db.reference(f'gallery/{st.session_state.user}').push({
                    'u': st.session_state.user,
                    'img': base64_image,
                    'ts': time.time(),
                    'lat': lat,
                    'lon': lon
                })
                st.success("บันทึกภาพสำเร็จ!")
        # ... (ส่วนที่เหลือของฟังก์ชันเดิม) ...

        
        with col2:
            st.download_button("💾 SAVE TO DEVICE", data=img_file, file_name=f"SYNAPSE_{int(time.time())}.jpg", mime="image/jpeg", use_container_width=True)

    # แสดงคลังภาพล่าสุดจาก AGENT คนอื่นๆ
    st.write("---")
    st.caption("🖼️ RECENT FIELD PHOTOS (GALLERY)")
    gallery = db.reference('gallery').get()
    if gallery:
        # รวมภาพจากทุก Agent มาแสดง
        for agent_id, photos in gallery.items():
            for p_id, p_data in list(photos.items())[-1:]: # ดึงรูปปัจจุบันรูปเดียวของแต่ละคนมาโชว์
                st.write(f"👤 จาก AGENT: {agent_id}")
                st.image(base64.b64decode(p_data['img']), width=500)


def room_call():
    st.subheader("📞 SYNAPSE P2P CALL อยู่นิ้งๆไม่เจ็บตัว")
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    target = st.selectbox("เลือก AGENT ที่จะโทรหา:", friends)
    if target:
        st.info(f"พร้อมเชื่อมต่อกับ {target} ผ่านเครือข่าย P2P")
        call_html = f"""
        <div style="background:#111; padding:20px; border-radius:15px; border:4px solid {st.session_state.theme_color}; text-align:center;">
            <video id="remoteVideo" autoplay playsinline style="width:100%; height:300px; background:#000; border-radius:10px;"></video>
            <video id="localVideo" autoplay playsinline muted style="width:100px; position:absolute; bottom:30px; right:30px; border:2px solid {st.session_state.theme_color};"></video>
            <div style="margin-top:10px;">
                <button id="startCall" style="background:{st.session_state.theme_color}; color:black; padding:10px 20px; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">📞 START CALL</button>
                <button onclick="location.reload()" style="background:#ff4444; color:white; padding:10px 20px; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">❌ DISCONNECT</button>
            </div>
        </div>
        <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
        <script>
            const peer = new Peer('{st.session_state.user}');
            const localVideo = document.getElementById('localVideo');
            const remoteVideo = document.getElementById('remoteVideo');
            peer.on('call', call => {{
                navigator.mediaDevices.getUserMedia({{video: true, audio: true}}).then(stream => {{
                    localVideo.srcObject = stream;
                    call.answer(stream);
                    call.on('stream', remoteStream => {{ remoteVideo.srcObject = remoteStream; }});
                }});
            }});
            document.getElementById('startCall').onclick = () => {{
                navigator.mediaDevices.getUserMedia({{video: true, audio: true}}).then(stream => {{
                    localVideo.srcObject = stream;
                    const call = peer.call('{target}', stream);
                    call.on('stream', remoteStream => {{ remoteVideo.srcObject = remoteStream; }});
                }});
            }};
        </script>
        """
        components.html(call_html, height=450)


# ==========================================
# 2. CORE MODULES (ปรับปรุงส่วน Music)
# ==========================================

                <div><label>MID</label><input type="range" id="mid-gain" min="-15" max="15" value="0" class="w-full"></div>
                <div><label>TREBLE</label><input type="range" id="high-gain" min="-15" max="15" value="0" class="w-full"></div>
            </div>
            <audio id="audio-element" class="hidden"></audio>
        </div>

        <script>
            const audio = document.getElementById('audio-element');
            const fileInput = document.getElementById('file-input');
            const playPauseBtn = document.getElementById('play-pause-btn');
            const canvas = document.getElementById('visualizer-canvas');
            const ctx = canvas.getContext('2d');
            let audioCtx, source, analyzer, lowFilter, midFilter, highFilter;

            fileInput.onchange = (e) => {
                const file = e.target.files[0];
                if(file) {
                    audio.src = URL.createObjectURL(file);
                    document.getElementById('song-title').innerText = file.name;
                    setupAudio();
                }
            };

            function setupAudio() {
                if(!audioCtx) {
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    source = audioCtx.createMediaElementSource(audio);
                    analyzer = audioCtx.createAnalyser();
                    
                    lowFilter = audioCtx.createBiquadFilter(); lowFilter.type = 'lowshelf'; lowFilter.frequency.value = 320;
                    midFilter = audioCtx.createBiquadFilter(); midFilter.type = 'peaking'; midFilter.frequency.value = 1000;
                    highFilter = audioCtx.createBiquadFilter(); highFilter.type = 'highshelf'; highFilter.frequency.value = 3200;

                    source.connect(lowFilter); lowFilter.connect(midFilter); midFilter.connect(highFilter);
                    highFilter.connect(analyzer); analyzer.connect(audioCtx.destination);
                    
                    visualize();
                }
            }

            playPauseBtn.onclick = () => {
                if(audioCtx?.state === 'suspended') audioCtx.resume();
                audio.paused ? audio.play() : audio.pause();
            };

            // ระบบ Visualizer
            function visualize() {
                analyzer.fftSize = 64;
                const bufferLength = analyzer.frequencyBinCount;
                const dataArray = new Uint8Array(bufferLength);

                function draw() {
                    requestAnimationFrame(draw);
                    analyzer.getByteFrequencyData(dataArray);
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    let barWidth = (canvas.width / bufferLength) * 2.5;
                    let x = 0;
                    for(let i = 0; i < bufferLength; i++) {
                        let barHeight = dataArray[i] / 2;
                        ctx.fillStyle = `rgb(0, 255, 200)`;
                        ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
                        x += barWidth + 1;
                    }
                }
                draw();
            }
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

            
def room_secure_chat():
    st.subheader("💬 SECURE CHAT📝อยู่นิ่งๆไม่เจ็บตัว")
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    
    target = st.selectbox("🎯 เลือกผู้รับข้อความ:", friends)
    if target:
        rid = "_".join(sorted([st.session_state.user, target]))
        with st.form("chat_form", clear_on_submit=True):
            msg = st.text_input("พิมพ์ข้อความที่นี่...")
            up = st.file_uploader("ส่งรูปภาพ/วิดีโอ", type=['jpg', 'png', 'mp4'])
            if st.form_submit_button("SEND MESSAGE"):
                f_data, f_type = (base64.b64encode(up.read()).decode(), up.type) if up else (None, None)
                db.reference(f'private_rooms/{rid}').push({
                    'u': st.session_state.user, 
                    'm': msg, 
                    'f': f_data, 
                    'ft': f_type, 
                    'ts': time.time()
                })
                st.rerun()
        
        chats = db.reference(f'private_rooms/{rid}').order_by_key().limit_to_last(15).get()
        if chats:
            for c in reversed(list(chats.values())):
                align = "right" if c['u'] == st.session_state.user else "left"
                color = st.session_state.theme_color if c['u'] == st.session_state.user else "#333"
                st.markdown(f'<div style="text-align:{align}; margin-bottom:10px;"><div style="display:inline-block; background:{color}; padding:10px; border-radius:10px; color:white;"><b>{c["u"]}</b>: {c["m"]}</div></div>', unsafe_allow_html=True)
                if c.get('f'):
                    try:
                        dec = base64.b64decode(c['f'])
                        if "image" in c['ft']: st.image(dec, width=250)
                        elif "video" in c['ft']: st.video(dec)
                    except: pass
    
    # ลบส่วน with tabs[5] และ room_music() ออกจากตรงนี้ 
    # เพราะเราไปเรียกใช้ใน main() แยก Tab กันชัดเจนอยู่แล้วครับ

# ==========================================
# 3. MAIN SYSTEM
# ==========================================
def main():
    init_system()
    apply_custom_background()
    
    loc = get_geolocation() 

    if not st.session_state.get('logged_in', False):
        room_login()
        return

    with st.sidebar:
        st.write(f"👤 AGENT: **{st.session_state.user}**")
        st.caption("'อยู่นิ่งๆ ไม่เจ็บตัว'")
        st.write("---")
        if st.button("🚪 LOGOUT", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    # --- ส่วนแสดงโลโก้ (ใช้ชื่อไฟล์ตัวพิมพ์เล็กทั้งหมดตามที่แจ้ง) ---
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1]) 
    with c2:
        # แก้เป็น logo1.png (ตัวเล็กทั้งหมด)
        if os.path.exists("logo1.png"):
            st.image("logo1.png", use_container_width=True)
        else:
            # ถ้ายังไม่ขึ้น ให้ลองเรียกตรงๆ หรือโชว์ชื่อระบบสำรองไว้
            try:
                st.image("logo1.png", use_container_width=True)
            except:
                st.markdown(f"""
                    <h1 style='text-align:center; color:{st.session_state.theme_color}; 
                    text-shadow: 0 0 15px {st.session_state.theme_color}; font-family: monospace;'>
                    SYNAPSE OS</h1>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        # เช็คไฟล์โลโก้
        st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color};'>SYNAPSE OS</h1>", unsafe_allow_html=True)

    # ประกาศ Tabs ครั้งเดียวที่นี่
    tabs = st.tabs([
        "🏠 CORE", 
        "🛰️ RADAR", 
        "💬 CHAT", 
        "📞 CALL", 
        "🎧 MUSIC", 
        "⚙️ SETTINGS", 
        "📷 SCANNER"
    ])

    with tabs[0]:
        room_core(loc)
    with tabs[1]:
        room_radar(loc)
    with tabs[2]:
        room_secure_chat() # ฟังก์ชันนี้จะทำงานแค่ใน Tab ตัวเอง
    with tabs[3]:
        room_call()
    with tabs[4]:
        room_music()
    with tabs[5]: 
        st.subheader("🎨 SYSTEM THEME CUSTOMIZATION")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            if st.button("🔴 STEALTH RED", key="red_theme", use_container_width=True):
                st.session_state.theme_color = "#FF0000"
                st.rerun()
        with col_p2:
            if st.button("🟢 CYBER NEON", key="green_theme", use_container_width=True):
                st.session_state.theme_color = "#00FF41"
                st.rerun()
        
        st.write("---")
        new_color = st.color_picker("🎯 ปรับแต่งสีอิสระ", st.session_state.theme_color)
        if new_color != st.session_state.theme_color:
            st.session_state.theme_color = new_color
            st.rerun()

    with tabs[6]:
        room_camera(loc)

if __name__ == "__main__":
    main()

