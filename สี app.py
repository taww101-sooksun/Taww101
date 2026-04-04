import streamlit as st
import os 
import time
import json
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
    st_folium(m, width="100%", height=400)

def room_music():
    st.subheader("🎧 SYNAPSE HYBRID AUDIO - อยู่นิ่งๆไม่เจ็บตัว")
    music_dir = "music"
    if not os.path.exists(music_dir):
        os.makedirs(music_dir)
    
    local_files = [f for f in os.listdir(music_dir) if f.endswith((".mp3", ".wav"))]
    local_files_json = json.dumps(local_files)

    hybrid_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background: transparent; color: white; }}
            .main-card {{
                background: linear-gradient(270deg, #ff0000, #00ff00, #0000ff, #ff00ff);
                background-size: 800% 800%;
                animation: RainbowFlow 12s ease infinite;
                padding: 20px; border-radius: 24px; border: 4px solid #00ffc8;
            }}
            @keyframes RainbowFlow {{ 0%{{background-position:0% 50%}} 50%{{background-position:100% 50%}} 100%{{background-position:0% 50%}} }}
            .btn-action {{ background: #FF7F50; color: white; font-weight: bold; border-radius: 12px; cursor: pointer; padding: 10px; }}
            #visualizer-canvas {{ background: rgba(0,0,0,0.8); border-radius: 12px; height: 80px; width: 100%; }}
            .playlist-box {{ background: rgba(0,0,0,0.6); height: 150px; overflow-y: auto; border-radius: 12px; padding: 10px; }}
            .track-item {{ padding: 8px; border-bottom: 1px solid #333; cursor: pointer; }}
            .track-item.active {{ border-left: 4px solid #00ffc8; background: rgba(0, 255, 200, 0.1); }}
        </style>
    </head>
    <body>
        <div class="main-card">
            <canvas id="visualizer-canvas" class="mb-4"></canvas>
            <div class="text-center mb-4">
                <p id="song-title" class="text-sm font-bold">READY TO PLAY</p>
            </div>
            <div class="grid grid-cols-3 gap-2 mb-4">
                <button onclick="prevTrack()" class="btn-action">PREV</button>
                <button id="play-btn" onclick="togglePlay()" class="btn-action bg-white !text-black">PLAY</button>
                <button onclick="nextTrack()" class="btn-action">NEXT</button>
            </div>
            <div class="mb-2 flex gap-2">
                <label class="btn-action flex-1 text-center text-xs bg-cyan-600 cursor-pointer">
                    UPLOAD <input type="file" id="file-input" multiple accept="audio/*" class="hidden" onchange="handleUpload(this.files)">
                </label>
                <button onclick="loadLocalLibrary()" class="btn-action flex-1 text-xs bg-purple-600">SYNC SERVER</button>
            </div>
            <div id="playlist" class="playlist-box"></div>
        </div>
        <audio id="main-audio" class="hidden"></audio>
        <script>
            const audio = document.getElementById('main-audio');
            const localTracks = {local_files_json};
            let tracks = []; let currentIndex = 0;
            let audioCtx, analyzer;

            function initAudio() {{
                if (audioCtx) return;
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                const source = audioCtx.createMediaElementSource(audio);
                analyzer = audioCtx.createAnalyser();
                source.connect(analyzer); analyzer.connect(audioCtx.destination);
                const canvas = document.getElementById('visualizer-canvas');
                const ctx = canvas.getContext('2d');
                function draw() {{
                    requestAnimationFrame(draw);
                    const data = new Uint8Array(analyzer.frequencyBinCount);
                    analyzer.getByteFrequencyData(data);
                    ctx.clearRect(0,0,canvas.width, canvas.height);
                    ctx.fillStyle = '#00ffc8';
                    for(let i=0; i<64; i++) {{ ctx.fillRect(i*5, canvas.height - data[i]/2, 4, data[i]/2); }}
                }}
                draw();
            }}
            function handleUpload(files) {{ Array.from(files).forEach(f => addTrack(f.name, URL.createObjectURL(f))); }}
            async function loadLocalLibrary() {{ 
                for(const n of localTracks) {{ addTrack(n, 'music/'+n); }} 
            }}
            function addTrack(name, url) {{
                tracks.push({{ name, url }}); renderPlaylist();
                if(tracks.length===1) loadTrack(0);
            }}
            function renderPlaylist() {{
                const container = document.getElementById('playlist');
                container.innerHTML = '';
                tracks.forEach((t, i) => {{
                    const d = document.createElement('div');
                    d.className = `track-item ${{i===currentIndex?'active':''}}`;
                    d.innerText = t.name; d.onclick = () => loadTrack(i);
                    container.appendChild(d);
                }});
            }}
            function loadTrack(i) {{
                initAudio(); currentIndex = i; audio.src = tracks[i].url;
                document.getElementById('song-title').innerText = tracks[i].name;
                audio.play(); renderPlaylist();
            }}
            function togglePlay() {{
                initAudio();
                if(audio.paused) {{ audio.play(); }} else {{ audio.pause(); }}
            }}
            function nextTrack() {{ if(currentIndex < tracks.length-1) loadTrack(currentIndex+1); }}
            function prevTrack() {{ if(currentIndex > 0) loadTrack(currentIndex - 1); }}
        </script>
    </body>
    </html>
    """
    components.html(hybrid_html, height=600)

def room_dj_crossfade():
    st.subheader("🎚️ DJ CROSSFADE SYSTEM")
    st.info("โมดูลดีเจกำลังทำงาน...")

def main():
    init_system()
    apply_custom_background()
    loc = get_geolocation()

    if not st.session_state.get('logged_in'):
        room_login()
    else:
        tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "🎧 MUSIC", "🎚️ DJ TOOLS", "⚙️ SETTINGS"])
        with tabs[0]: room_core(loc)
        with tabs[1]: room_radar(loc)
        with tabs[2]: room_music()
        with tabs[3]: room_dj_crossfade()
        with tabs[4]: st.write("ตั้งค่าระบบ")

if __name__ == "__main__":
    main()

