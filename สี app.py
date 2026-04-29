import streamlit as st
import os 
import base64
import random
import time
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# ==========================================
# 1. CORE ENGINE & FIREBASE (เสถียรที่สุด)
# ==========================================
@st.cache_resource
def init_system():
    # Session State Setup
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'user' not in st.session_state: st.session_state.user = "Ta101"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0

    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            # ล้างค่าขยะใน Private Key เพื่อกัน Error InvalidByte
            if "private_key" in fb_creds:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n").strip().strip('"')
            
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_db_url"]
            })
        except Exception as e:
            st.error(f"🛰️ Firebase Connection Error: {e}")
    return True

init_system()

# ==========================================
# 2. UI STYLING (Dark Neon Style)
# ==========================================
st.set_page_config(page_title="SYNAPSE X", layout="wide")
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp {{ background-color: {st.session_state.bg_color} !important; color: #FFFFFF !important; font-family: 'Orbitron', sans-serif; }}
    .stButton>button {{ border: 2px solid {st.session_state.theme_color} !important; color: {st.session_state.theme_color} !important; background: transparent !important; border-radius: 10px; }}
    .stButton>button:hover {{ background: {st.session_state.theme_color} !important; color: black !important; }}
    .neon-box {{ border: 1px solid {st.session_state.theme_color}; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 0 10px {st.session_state.theme_color}; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. MODULES (The Rooms)
# ==========================================

def room_core():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-align:center;'>🚀 CORE COMMAND</h2>", unsafe_allow_html=True)
    now = datetime.utcnow() + timedelta(hours=7)
    
    st.markdown(f"""
        <div class="neon-box">
            <h1 style="margin:0; color:{st.session_state.theme_color};">{now.strftime('%H:%M:%S')}</h1>
            <p style="margin:0;">AGENT: {st.session_state.user} | 'อยู่นิ่งๆ ไม่เจ็บตัว'</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Day Progress
    seconds = (now.hour * 3600) + (now.minute * 60) + now.second
    progress = seconds / 86400
    st.write(f"⏳ System Uptime: {progress*100:.2f}%")
    st.progress(min(progress, 1.0))

def room_radar():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color};'>🛰️ SATELLITE RADAR</h2>", unsafe_allow_html=True)
    loc = get_geolocation()
    all_users = db.reference('users').get()
    
    lat, lon = (loc['coords']['latitude'], loc['coords']['longitude']) if loc else (13.7367, 100.5231)
    
    m = folium.Map(location=[lat, lon], zoom_start=16, 
                  tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
    
    folium.Marker([lat, lon], tooltip="YOU", icon=folium.Icon(color='red', icon='user', prefix='fa')).add_to(m)
    
    if all_users:
        for uid, data in all_users.items():
            if uid != st.session_state.user and data.get('lat'):
                folium.Marker([data['lat'], data['lon']], tooltip=uid, icon=folium.Icon(color='green')).add_to(m)

    st_folium(m, width="100%", height=450, key="radar")
    if st.button("📡 BROADCAST POSITION", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': lat, 'lon': lon, 'ts': time.time()})
        st.toast("Intelligence Data Transmitted!")

def room_comms():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color};'>💬 COMM CENTER</h2>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🌐 PUBLIC FEED", "📞 SECURE CALL"])
    
    with t1:
        with st.form("chat_form", clear_on_submit=True):
            col1, col2 = st.columns([4, 1])
            msg = col1.text_input("Enter Signal...")
            up_file = col2.file_uploader("📁", type=['jpg', 'png', 'mp4'], label_visibility="collapsed")
            if st.form_submit_button("SEND"):
                f_b64, f_type = None, None
                if up_file:
                    f_b64 = base64.b64encode(up_file.getvalue()).decode()
                    f_type = up_file.type
                if msg or f_b64:
                    db.reference('public_chat').push({
                        'u': st.session_state.user, 'm': msg, 'f': f_b64, 'ft': f_type, 'ts': time.time()
                    })
                    st.rerun()

        st.write("---")
        msgs = db.reference('public_chat').order_by_key().limit_to_last(15).get()
        if msgs:
            for v in reversed(list(msgs.values())):
                st.markdown(f"🟢 **{v.get('u')}**: {v.get('m','')}")
                if v.get('f'):
                    raw = base64.b64decode(v['f'])
                    if "image" in v['ft']: st.image(raw, width=300)
                    elif "video" in v['ft']: st.video(raw)

    with t2:
        st.info("P2P Voice Communication Active")
        all_u = db.reference('users').get()
        friends = [uid for uid in all_u.keys() if uid != st.session_state.user] if all_u else []
        target = st.selectbox("🎯 Target Agent:", [""] + friends)
        if target:
            call_js = """
            <div style="background:#111; padding:15px; border:1px solid %s; border-radius:10px; text-align:center;">
                <p>AGENT ID: <b>%s</b></p>
                <button id="cBtn" style="width:100%%; padding:10px; background:#28a745; color:white; border:none; border-radius:5px;">📞 CALL %s</button>
                <audio id="rAudio" autoplay></audio>
            </div>
            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <script>
                const peer = new Peer('%s');
                peer.on('call', c => { navigator.mediaDevices.getUserMedia({audio:true}).then(s=>{ c.answer(s); c.on('stream',rs=>{document.getElementById('rAudio').srcObject=rs;}); })});
                document.getElementById('cBtn').onclick = () => {
                    navigator.mediaDevices.getUserMedia({audio:true}).then(s=>{ const c=peer.call('%s',s); c.on('stream',rs=>{document.getElementById('rAudio').srcObject=rs;}); });
                };
            </script>
            """ % (st.session_state.theme_color, st.session_state.user, target, st.session_state.user, target)
            components.html(call_js, height=200)

def room_music():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color};'>🎧 DJ STATION</h2>", unsafe_allow_html=True)
    songs = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if songs:
        s_a = st.selectbox("DECK A", ["-- Select --"] + songs, index=st.session_state.song_index + 1)
        if s_a != "-- Select --":
            st.audio(s_a)
            st.session_state.song_index = songs.index(s_a)
        
        st.write("Playlist:")
        for i, s in enumerate(songs):
            if st.button(f"🎵 {s}", key=f"play_{i}", use_container_width=True):
                st.session_state.song_index = i
                st.rerun()
def room_music():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-shadow: 0 0 20px {st.session_state.theme_color}; text-align:center;'>🎧 RAINBOW DJ STATION</h2>", unsafe_allow_html=True)
    
    songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    
    if not songs:
        st.warning("⚠️ ไม่พบไฟล์เพลงในระบบ")
        return

    # --- ส่วนของ Visualizer สีสันสดใส ---
    s_a = st.selectbox("เลือกเพลงที่จะเล่น", ["-- Select --"] + songs, index=st.session_state.song_index + 1)
    
    # แปลงไฟล์เป็น Base64 เพื่อให้ JavaScript เล่นได้เสถียร
    song_b64 = ""
    if s_a != "-- Select --":
        with open(s_a, "rb") as f:
            song_b64 = base64.b64encode(f.read()).decode()
        st.session_state.song_index = songs.index(s_a)

    visualizer_html = f"""
    <div style="background: #000; border: 3px solid {st.session_state.theme_color}; border-radius: 20px; padding: 20px; box-shadow: 0 0 30px {st.session_state.theme_color}55;">
        <canvas id="canvas" style="width: 100%; height: 200px; background: #050505; border-radius: 10px;"></canvas>
        <div style="margin-top: 15px; text-align: center;">
            <button id="pBtn" style="width: 100%; padding: 15px; background: linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #8b00ff); 
            background-size: 400% 400%; animation: rainbow 5s ease infinite; border: none; border-radius: 10px; color: white; font-weight: bold; font-size: 1.2em; cursor: pointer; text-shadow: 1px 1px 5px #000;">
                ▶ START VISUALIZER
            </button>
        </div>
        <audio id="audio" src="data:audio/mp3;base64,{song_b64}"></audio>
    </div>

    <style>
        @keyframes rainbow {{ 
            0%{{background-position:0% 50%}} 50%{{background-position:100% 50%}} 100%{{background-position:0% 50%}} 
        }}
    </style>

    <script>
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const audio = document.getElementById('audio');
    const btn = document.getElementById('pBtn');
    
    let audioCtx, analyser, source, dataArray;

    btn.onclick = function() {{
        if (!audioCtx) {{
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            analyser = audioCtx.createAnalyser();
            source = audioCtx.createMediaStreamSource(audio.captureStream ? audio.captureStream() : audio.mozCaptureStream ? audio.mozCaptureStream() : null) || audioCtx.createMediaElementSource(audio);
            source.connect(analyser);
            analyser.connect(audioCtx.destination);
            analyser.fftSize = 128;
            dataArray = new Uint8Array(analyser.frequencyBinCount);
            draw();
        }}
        if (audio.paused) {{ audio.play(); btn.innerText = "⏸ PAUSE"; }}
        else {{ audio.pause(); btn.innerText = "▶ RESUME"; }}
    }};

    function draw() {{
        requestAnimationFrame(draw);
        analyser.getByteFrequencyData(dataArray);
        ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const barWidth = (canvas.width / dataArray.length) * 2.5;
        let x = 0;

        for (let i = 0; i < dataArray.length; i++) {{
            const barHeight = dataArray[i] / 1.5;
            // สร้างสีแบบ Rainbow ตามตำแหน่ง Bar
            const hue = (i / dataArray.length) * 360;
            ctx.fillStyle = `hsl(${{hue}}, 100%, 50%)`;
            ctx.shadowBlur = 15;
            ctx.shadowColor = `hsl(${{hue}}, 100%, 50%)`;
            
            ctx.fillRect(x, canvas.height - barHeight, barWidth - 2, barHeight);
            x += barWidth;
        }}
    }}
    </script>
    """
    components.html(visualizer_html, height=350)

    # --- ส่วนแสดงรายชื่อเพลงด้านล่าง ---
    st.write("---")
    cols = st.columns(3)
    for i, song in enumerate(songs):
        with cols[i % 3]:
            if st.button(f"🎵 {song[:15]}...", key=f"btn_{i}", use_container_width=True):
                st.session_state.song_index = i
                st.rerun()

def room_sensor():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color};'>🎙️ SENSOR LAB</h2>", unsafe_allow_html=True)
    audio_js = f"""
    <div style="background:#000; color:{st.session_state.theme_color}; padding:20px; border:2px solid {st.session_state.theme_color}; border-radius:15px; text-align:center;">
        <div style="display:flex; justify-content:space-around;">
            <div><p>DECIBEL</p><h1 id="db">0</h1></div>
            <div><p>FREQUENCY</p><h1 id="hz">0</h1></div>
        </div>
        <canvas id="osc" style="width:100%; height:60px;"></canvas>
    </div>
    <script>
    async function start() {{
        const s = await navigator.mediaDevices.getUserMedia({{audio:true}});
        const ctx = new AudioContext();
        const ans = ctx.createAnalyser();
        ctx.createMediaStreamSource(s).connect(ans);
        const data = new Uint8Array(ans.frequencyBinCount);
        function loop() {{
            ans.getByteFrequencyData(data);
            let sum=0; for(let v of data) sum+=v;
            document.getElementById('db').innerText = Math.round(sum/data.length);
            requestAnimationFrame(loop);
        }}
        loop();
    }}
    start();
    </script>
    """
    components.html(audio_js, height=250)

# ==========================================
# 4. MAIN LAYOUT
# ==========================================
def main():
    with st.sidebar:
        st.title("⚙️ SYSTEM")
        st.session_state.user = st.text_input("AGENT ID", st.session_state.user)
        st.session_state.theme_color = st.color_picker("THEME", st.session_state.theme_color)
        st.session_state.bg_color = st.color_picker("BACKGROUND", st.session_state.bg_color)
        st.markdown("---")
        st.caption("'อยู่นิ่งๆ ไม่เจ็บตัว'")

    tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "🎧 MUSIC", "📟 SENSOR"])
    rooms = [room_core, room_radar, room_comms, room_music, room_sensor]
    
    for i, tab in enumerate(tabs):
        with tab: rooms[i]()

if __name__ == "__main__":
    main()
