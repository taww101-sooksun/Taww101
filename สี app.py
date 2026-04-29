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
# --- [ 1. IMPORT ทั้งหมด ] ---
import streamlit as st
import os 
import base64
# ... (import อื่นๆ ของคุณ)

# --- [ 2. INITIAL SETUP ฟังก์ชันตั้งค่า ] ---
def init_system():
    # จองค่าไว้ในกระเป๋าก่อน
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'user' not in st.session_state: st.session_state.user = "Ta101"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    
    # ส่วน Firebase
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            if "private_key" in fb_creds:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n").strip().strip('"')
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_db_url"]
            })
        except Exception as e:
            pass # หรือ st.error(e)

# --- [ 3. รันฟังก์ชันทันที ] ---
# ต้องรันตรงนี้เพื่อให้ session_state มีค่า bg_color เตรียมพร้อมไว้
init_system()

# --- [ 4. UI STYLING (วางไว้หลังรัน init_system) ] ---
st.set_page_config(page_title="SYNAPSE X", layout="wide")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp {{ 
        background-color: {st.session_state.bg_color} !important; 
        color: #FFFFFF !important; 
        font-family: 'Orbitron', sans-serif; 
    }}
    /* ... CSS อื่นๆ ของคุณ ... */
    </style>
    """, unsafe_allow_html=True)

# --- [ 5. ส่วนอื่นๆ ของแอป ] ---
# def main()...

# ==========================================
# 1. CORE ENGINE & FIREBASE (เสถียรที่สุด)
# ==========================================
# --- [ 1. INITIAL SETUP & FIREBASE ] ---
@st.cache_resource
def init_system():
    # ต้องจองค่าพวกนี้ก่อนที่ CSS ด้านล่างจะเรียกใช้
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'user' not in st.session_state: st.session_state.user = "Ta101"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0

    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            if "private_key" in fb_creds:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n").strip().strip('"')
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_db_url"]
            })
        except Exception as e:
            st.error(f"🛰️ Firebase Connection Error: {e}")
    return True

# --- สำคัญมาก: ต้องเรียกใช้งานก่อนทำอย่างอื่น ---
init_system()

# --- [ 2. UI STYLING ] ---
# ย้ายมาไว้ตรงนี้เพื่อให้แน่ใจว่า st.session_state.bg_color มีค่าแล้ว
st.set_page_config(page_title="SYNAPSE X", layout="wide")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp {{ 
        background-color: {st.session_state.bg_color} !important; 
        color: #FFFFFF !important; 
        font-family: 'Orbitron', sans-serif; 
    }}
    .stButton>button {{ 
        border: 2px solid {st.session_state.theme_color} !important; 
        color: {st.session_state.theme_color} !important; 
        background: transparent !important; 
        border-radius: 10px; 
    }}
    .stButton>button:hover {{ 
        background: {st.session_state.theme_color} !important; 
        color: black !important; 
    }}
    </style>
    """, unsafe_allow_html=True)


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
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-shadow: 0 0 20px {st.session_state.theme_color}; text-align:center;'>🎧 SYNAPSE AUDIO TERMINAL</h2>", unsafe_allow_html=True)
    
    songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    
    if not songs:
        st.warning("⚠️ ไม่พบสัญญาณเสียงในหน่วยความจำ")
        return

    # 1. เลือกเพลงจาก Dropdown (อันเดียวจบ)
    s_a = st.selectbox("🎯 SELECT SIGNAL SOURCE", ["-- STANDBY --"] + songs, index=st.session_state.song_index + 1)
    
    song_b64 = ""
    song_name = "WAITING FOR SIGNAL..."
    if s_a != "-- STANDBY --":
        with open(s_a, "rb") as f:
            song_b64 = base64.b64encode(f.read()).decode()
        st.session_state.song_index = songs.index(s_a)
        song_name = f"PLAYING: {s_a}"

    # 2. ตัวเครื่องเล่นใหม่: มีข้อความวิ่ง (Marquee) แทนปุ่มสีรุ้ง
    visualizer_html = f"""
    <div style="background: #000; border: 2px solid {st.session_state.theme_color}; border-radius: 15px; padding: 20px; box-shadow: 0 0 25px {st.session_state.theme_color}33;">
        
        <div style="overflow: hidden; white-space: nowrap; background: #0a0a0a; border: 1px solid {st.session_state.theme_color}55; border-radius: 5px; margin-bottom: 15px; padding: 5px;">
            <p style="display: inline-block; padding-left: 100%; font-family: 'Orbitron', sans-serif; font-size: 14px; color: {st.session_state.theme_color}; text-shadow: 0 0 10px {st.session_state.theme_color}; animation: marquee 15s linear infinite;">
                {song_name} >>> ANALYZING FREQUENCY... >>> SECURE LINE ACTIVE... >>> {song_name}
            </p>
        </div>

        <canvas id="canvas" style="width: 100%; height: 180px; background: #000; border-radius: 5px; cursor: pointer;"></canvas>
        
        <div style="margin-top: 15px; text-align: center;">
            <button id="pBtn" style="width: 100%; padding: 12px; background: transparent; border: 1px solid {st.session_state.theme_color}; border-radius: 8px; color: {st.session_state.theme_color}; font-family: 'Orbitron', sans-serif; cursor: pointer; transition: 0.3s; box-shadow: inset 0 0 10px {st.session_state.theme_color}44;">
                [ CLICK TO SYNC AUDIO ]
            </button>
        </div>

        <audio id="audio" src="data:audio/mp3;base64,{song_b64}"></audio>
    </div>

    <style>
        @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
        #pBtn:hover {{ background: {st.session_state.theme_color}22; box-shadow: 0 0 15px {st.session_state.theme_color}; }}
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
            source = audioCtx.createMediaElementSource(audio);
            source.connect(analyser);
            analyser.connect(audioCtx.destination);
            analyser.fftSize = 64; // ปรับให้ Bar ดูใหญ่และแข็งแรงขึ้น
            dataArray = new Uint8Array(analyser.frequencyBinCount);
            draw();
        }}
        if (audio.paused) {{ audio.play(); btn.innerText = "[ SIGNAL ACTIVE ]"; btn.style.borderColor = "#ff0000"; btn.style.color = "#ff0000"; }}
        else {{ audio.pause(); btn.innerText = "[ SIGNAL PAUSED ]"; btn.style.borderColor = "{st.session_state.theme_color}"; btn.style.color = "{st.session_state.theme_color}"; }}
    }};

    function draw() {{
        requestAnimationFrame(draw);
        analyser.getByteFrequencyData(dataArray);
        ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const barWidth = (canvas.width / dataArray.length);
        for (let i = 0; i < dataArray.length; i++) {{
            const barHeight = dataArray[i] * 0.8;
            // ใช้สีตาม Theme แต่ไล่ความสว่างแบบ Neon
            ctx.fillStyle = '{st.session_state.theme_color}';
            ctx.shadowBlur = 15;
            ctx.shadowColor = '{st.session_state.theme_color}';
            ctx.fillRect(i * barWidth, canvas.height - barHeight, barWidth - 4, barHeight);
        }}
    }}
    </script>
    """
    components.html(visualizer_html, height=360)

    st.markdown("---")
    st.caption("ระบบตัดเสียงก้องอัตโนมัติ: เชื่อมต่อผ่านช่องทางเดียวเท่านั้น")

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
