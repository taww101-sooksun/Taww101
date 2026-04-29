import streamlit as st
import os 
import base64
import time
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# ==========================================
# 1. INITIAL SETUP (ต้องอยู่บนสุดและรันก่อนเสมอ)
# ==========================================
def init_system():
    # จองค่าใน Session State
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'user' not in st.session_state: st.session_state.user = "Ta101"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0

    # เชื่อมต่อ Firebase
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            if "private_key" in fb_creds:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n").strip().strip('"')
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception:
            pass

# เรียกใช้งานทันที
init_system()

# ==========================================
# 2. UI STYLING (เรียกใช้ bg_color หลังจากรัน init แล้ว)
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
# 3. MODULES
# ==========================================

def room_core():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-align:center;'>🚀 CORE COMMAND</h2>", unsafe_allow_html=True)
    now = datetime.utcnow() + timedelta(hours=7)
    st.markdown(f"""<div class="neon-box">
        <h1 style="margin:0; color:{st.session_state.theme_color};">{now.strftime('%H:%M:%S')}</h1>
        <p style="margin:0;">AGENT: {st.session_state.user} | 'อยู่นิ่งๆ ไม่เจ็บตัว'</p>
    </div>""", unsafe_allow_html=True)
    st.progress(min(((now.hour * 3600) + (now.minute * 60) + now.second) / 86400, 1.0))

def room_radar():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color};'>🛰️ RADAR</h2>", unsafe_allow_html=True)
    loc = get_geolocation()
    all_users = db.reference('users').get()
    lat, lon = (loc['coords']['latitude'], loc['coords']['longitude']) if loc else (13.7367, 100.5231)
    m = folium.Map(location=[lat, lon], zoom_start=16, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google")
    folium.Marker([lat, lon], tooltip="YOU", icon=folium.Icon(color='red')).add_to(m)
    st_folium(m, width="100%", height=400, key="radar")
    if st.button("📡 BROADCAST", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': lat, 'lon': lon, 'ts': time.time()})

def room_comms():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color};'>💬 COMM</h2>", unsafe_allow_html=True)
    with st.form("chat", clear_on_submit=True):
        m = st.text_input("Signal...")
        if st.form_submit_button("SEND") and m:
            db.reference('public_chat').push({'u': st.session_state.user, 'm': m, 'ts': time.time()})
            st.rerun()
    msgs = db.reference('public_chat').order_by_key().limit_to_last(10).get()
    if msgs:
        for v in reversed(list(msgs.values())):
            st.markdown(f"🟢 **{v.get('u')}**: {v.get('m','')}")

def room_music():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-align:center;'>🎧 RAINBOW STATION</h2>", unsafe_allow_html=True)
    songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if not songs: return st.warning("No Music Found")
    
    s_a = st.selectbox("SELECT SOURCE", ["-- STANDBY --"] + songs, index=st.session_state.song_index + 1)
    song_b64, name = "", "WAITING..."
    if s_a != "-- STANDBY --":
        with open(s_a, "rb") as f: song_b64 = base64.b64encode(f.read()).decode()
        st.session_state.song_index = songs.index(s_a)
        name = s_a

    # JavaScript Visualizer 7 สี + ตัวหนังสือวิ่งรุ้ง
    v_html = f"""
    <div style="background:#000; border:2px solid {st.session_state.theme_color}; border-radius:15px; padding:15px;">
        <div style="overflow:hidden; background:#050505; border-radius:5px; margin-bottom:10px; padding:5px;">
            <p id="mText" style="display:inline-block; padding-left:100%; color:white; font-family:Orbitron; animation: marquee 10s linear infinite;">
                <span id="rainbow">>>> {name} <<< ANALYZING FREQUENCY...</span>
            </p>
        </div>
        <canvas id="canvas" style="width:100%; height:200px;"></canvas>
        <button id="pBtn" style="width:100%; margin-top:10px; padding:12px; background:transparent; border:1px solid {st.session_state.theme_color}; color:{st.session_state.theme_color}; font-family:Orbitron; cursor:pointer;">[ SYNC SIGNAL ]</button>
        <audio id="audio" src="data:audio/mp3;base64,{song_b64}"></audio>
    </div>
    <style>
        @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
        #rainbow {{ animation: rb 4s linear infinite; }}
        @keyframes rb {{ 0%{{color:#f00}} 20%{{color:#ff0}} 40%{{color:#0f0}} 60%{{color:#0ff}} 80%{{color:#00f}} 100%{{color:#f0f}} }}
    </style>
    <script>
    const canvas=document.getElementById('canvas'), ctx=canvas.getContext('2d'), audio=document.getElementById('audio'), btn=document.getElementById('pBtn'), mText=document.getElementById('mText');
    let aCtx, ans, src, data; mText.style.animationPlayState='paused';
    btn.onclick=()=>{{
        if(!aCtx){{
            aCtx=new(window.AudioContext||window.webkitAudioContext)(); ans=aCtx.createAnalyser();
            src=aCtx.createMediaElementSource(audio); src.connect(ans); ans.connect(aCtx.destination);
            ans.fftSize=128; data=new Uint8Array(ans.frequencyBinCount); draw();
        }}
        if(audio.paused){{ audio.play(); btn.innerText="[ ACTIVE ]"; mText.style.animationPlayState='running'; }}
        else {{ audio.pause(); btn.innerText="[ PAUSED ]"; mText.style.animationPlayState='paused'; }}
    }};
    function draw(){{
        requestAnimationFrame(draw); ans.getByteFrequencyData(data);
        ctx.fillStyle='rgba(0,0,0,0.2)'; ctx.fillRect(0,0,canvas.width,canvas.height);
        let x=0; const bW=(canvas.width/data.length)*2;
        for(let i=0; i<data.length; i++){{
            let bH=data[i]*0.8, h=(i/data.length)*360;
            ctx.fillStyle=`hsl(${{h}}, 100%, 50%)`; ctx.fillRect(x, canvas.height-bH, bW-1, bH); x+=bW;
        }}
    }}
    </script>
    """
    components.html(v_html, height=400)

# ==========================================
# 4. MAIN LAYOUT
# ==========================================
def main():
    with st.sidebar:
        st.title("⚙️ SYSTEM")
        st.session_state.user = st.text_input("ID", st.session_state.user)
        st.session_state.theme_color = st.color_picker("THEME", st.session_state.theme_color)
        st.session_state.bg_color = st.color_picker("BG", st.session_state.bg_color)
    
    t1, t2, t3, t4 = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMM", "🎧 MUSIC"])
    with t1: room_core()
    with t2: room_radar()
    with t3: room_comms()
    with t4: room_music()

if __name__ == "__main__":
    main()
