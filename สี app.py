import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
import base64
import os
import time
from datetime import datetime
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# --- 1. INITIAL CONFIG ---
st.set_page_config(page_title="SYNAPSE OMNI", layout="wide", initial_sidebar_state="collapsed")

def apply_global_style():
    st.markdown("""
        <style>
            #MainMenu, footer, header {visibility: hidden;}
            .stApp { top: -60px; background-color: #000; color: #fff; }
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
            * { font-family: 'Orbitron', sans-serif !important; }
            
            /* Neon Text Animation */
            .neon-title {
                text-align: center; font-size: 2rem; color: #fff;
                text-shadow: 0 0 10px #39FF14, 0 0 20px #39FF14;
                animation: wink 2s infinite; margin-bottom: 20px;
            }
            @keyframes wink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
            
            .stTabs [aria-selected="true"] { border-bottom: 4px solid #39FF14 !important; box-shadow: 0 5px 15px #39FF1444; }
        </style>
    """, unsafe_allow_html=True)

apply_global_style()

# --- 2. FIREBASE & UTILS ---
if not firebase_admin._apps:
    fb_creds = dict(st.secrets["firebase_credentials"])
    fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate(fb_creds)
    firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})

def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

all_songs = sorted([f for f in os.listdir('.') if f.endswith('.mp3')])
logo_b64 = get_base64("logo1.png")
notif_sound = get_base64("notification.mp3")

# --- 3. AUTHENTICATION SYSTEM (Login / Register) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown('<div class="neon-title">SYNAPSE AUTH</div>', unsafe_allow_html=True)
    auth_tab1, auth_tab2 = st.tabs(["🔑 LOGIN", "📝 REGISTER"])
    
    with auth_tab1:
        with st.form("login"):
            u = st.text_input("AGENT ID")
            p = st.text_input("PASSWORD", type="password")
            if st.form_submit_button("CONNECT ⚡", use_container_width=True):
                res = db.reference(f'users/{u}').get()
                if res and res.get('password') == p:
                    st.session_state.logged_in, st.session_state.user = True, u
                    st.rerun()
                else: st.error("Access Denied")
                
    with auth_tab2:
        with st.form("register"):
            nu = st.text_input("NEW AGENT ID")
            np = st.text_input("NEW PASSWORD", type="password")
            cp = st.text_input("CONFIRM PASSWORD", type="password")
            if st.form_submit_button("CREATE ACCOUNT"):
                if nu and np == cp:
                    db.reference(f'users/{nu}').set({'password': np, 'created_at': datetime.now().isoformat()})
                    st.success("Registration Complete! Please Login.")
                else: st.error("Data Mismatch")
    st.stop()

# --- 4. MAIN INTERFACE ---
st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo_b64}" width="80" style="filter:drop-shadow(0 0 10px #39FF14);"></div>', unsafe_allow_html=True)
st.markdown(f'<div style="text-align:right; font-size:10px; color:#39FF14;">ID: {st.session_state.user}</div>', unsafe_allow_html=True)

tab_map, tab_chat, tab_music = st.tabs(["🛰️ RADAR", "💬 COMMS", "🎧 MIXER"])

# --- GPS RADAR ---
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return None

# --- 2. แสดงโลโก้ที่ "หน้าหลัก" (เพื่อให้เห็นทันที) ---
logo_data = get_base64_image("logo1.png")
if logo_data:
    st.markdown(f'<img src="data:image/png;base64,{logo_data}" class="neon-logo-main">', unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align: center; color: #00FF00;'>SYNAPSE</h1>", unsafe_allow_html=True)
# --- 3. ระบบดึงพิกัดจริง (No Default) ---

# ใช้ Session State เก็บค่า เพื่อไม่ให้แผนที่รีเฟรชหายไปมาระหว่างรอ
if 'user_lat' not in st.session_state:
    st.session_state.user_lat = None
    st.session_state.user_lon = None

# ดึงพิกัดจากเครื่อง
loc = get_geolocation() 

if loc and 'coords' in loc:
    # อัปเดตพิกัดจริงเข้าตัวแปรล็อก
    st.session_state.user_lat = loc['coords']['latitude']
    st.session_state.user_lon = loc['coords']['longitude']
    accuracy = loc['coords'].get('accuracy', 0)
    
    st.success(f"🎯 ล็อกเป้าหมายสำเร็จ! (แม่นยำในระยะ {accuracy:.0f} เมตร)")
else:
    st.info("🛰️ กำลังค้นหาสัญญาณดาวเทียมจากมือถือคุณ... กรุณาเปิด GPS และรอสักครู่")
    # หยุดการทำงานไว้ตรงนี้จนกว่าพิกัดจะมา (ป้องกันแผนที่ดีดไปที่อื่น)
    st.stop() 

my_lat = st.session_state.user_lat
my_lon = st.session_state.user_lon


# --- 4. แผนที่ Google Hybrid ---
# ตอนนี้ my_lat จะมีค่าแน่นอน ไม่ Error แล้วครับ
m = folium.Map(
    location=[my_lat, my_lon], 
    zoom_start=18, 
    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
    attr='Google Maps'
)


folium.Marker(
    [my_lat, my_lon], 
    icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
).add_to(m)

st_folium(m, width="100%", height=500)

if st.button("🛰️ บันทึกและส่งพิกัดปัจจุบัน", use_container_width=True):
    try:
        db.reference(f'users/Bas_Admin').update({
            'lat': my_lat, 'lon': my_lon, 'ts': time.time()
        })
        st.toast("ส่งพิกัดเข้าดาวเทียมแล้ว!")
    except: st.error("Firebase Connection Error")
with tab_map:
    loc = get_geolocation()
    if loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        st.write(f"📍 LAT: `{lat}` | LON: `{lon}`")
        db.reference(f'active_locations/{st.session_state.user}').update({'lat': lat, 'lon': lon, 'ts': time.time()})
        
        m = folium.Map(location=[lat, lon], zoom_start=17, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google')
        folium.Marker([lat, lon], icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')).add_to(m)
        st_folium(m, width="100%", height=400)
    else:
        st.warning("WAITING FOR SATELLITE SIGNAL...")

# --- CHAT (LEFT-RIGHT + SOUND) ---
with tab_chat:
    components.html(f"""
        <div id="chat-box" style="height:350px; overflow-y:auto; display:flex; flex-direction:column; gap:10px; padding:10px; background:#050505; border:1px solid #222; border-radius:10px;"></div>
        <audio id="beep"><source src="data:audio/mp3;base64,{notif_sound}" type="audio/mp3"></audio>
        <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
        <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
        <script>
            const fb = firebase.initializeApp({{databaseURL: "{st.secrets['firebase_db_url']}"}}).database();
            fb.ref('global_chat').limitToLast(20).on('child_added', (s) => {{
                const d = s.val();
                const isMe = d.user === "{st.session_state.user}";
                const bubble = `
                    <div style="align-self:${{isMe?'flex-end':'flex-start'}}; 
                                background:${{isMe?'#39FF1422':'#333'}}; 
                                border:1px solid ${{isMe?'#39FF14':'#555'}}; 
                                color:${{isMe?'#39FF14':'#fff'}}; 
                                padding:8px 12px; border-radius:15px; font-size:13px; max-width:80%;">
                        <div style="font-size:9px; opacity:0.6; margin-bottom:3px;">${{d.user}}</div>
                        ${{d.text}}
                    </div>`;
                const box = document.getElementById('chat-box');
                box.innerHTML += bubble; box.scrollTop = box.scrollHeight;
                if(!isMe) document.getElementById('beep').play();
            }});
        </script>
    """, height=370)
    msg = st.text_input("ENTER SIGNAL")
    if st.button("SEND ⚡"):
        if msg: db.reference('global_chat').push({'user': st.session_state.user, 'text': msg, 'ts': time.time()})

# --- MUSIC MIXER (CROSSFADE + VISUALIZER) ---
with tab_music:
    if len(all_songs) >= 2:
        c1, c2 = st.columns(2)
        s1 = c1.selectbox("DECK A", all_songs, index=0)
        s2 = c2.selectbox("DECK B", all_songs, index=1)
        
        html_mixer = f"""
        <canvas id="scope" style="width:100%; height:100px; background:#000; border-radius:10px; border:1px solid #333;"></canvas>
        <div id="status" style="text-align:center; color:#39FF14; font-size:12px; margin:10px 0;">SYSTEM READY</div>
        <button id="playBtn" style="width:100%; padding:15px; background:linear-gradient(90deg, #39FF14, #00f3ff); border:none; border-radius:10px; font-weight:bold; cursor:pointer;">START MIXING FLOW</button>
        
        <script>
            let ctx, analyser, data, active='A';
            async function play() {{
                ctx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = ctx.createAnalyser();
                data = new Uint8Array(analyser.frequencyBinCount);
                
                const load = async (b64) => ctx.decodeAudioData(await (await fetch('data:audio/mp3;base64,' + b64)).arrayBuffer());
                let bA = await load('{get_base64(s1)}');
                let bB = await load('{get_base64(s2)}');

                const run = (buf, isA) => {{
                    active = isA ? 'A' : 'B';
                    let src = ctx.createBufferSource(); src.buffer = buf;
                    let gain = ctx.createGain();
                    src.connect(gain).connect(analyser).connect(ctx.destination);
                    
                    // Crossfade logic
                    gain.gain.setValueAtTime(0, ctx.currentTime);
                    gain.gain.linearRampToValueAtTime(1, ctx.currentTime + 3);
                    
                    src.onended = () => run(isA ? bB : bA, !isA);
                    src.start(0);
                    document.getElementById('status').innerText = "PLAYING DECK " + active;
                }};
                run(bA, true);
                render();
            }}

            function render() {{
                requestAnimationFrame(render);
                analyser.getByteFrequencyData(data);
                const can = document.getElementById('scope');
                const c = can.getContext('2d');
                c.clearRect(0,0,can.width,can.height);
                for(let i=0; i<data.length; i++) {{
                    c.fillStyle = `hsl(${{i + (active=='A'?120:200)}}, 100%, 50%)`;
                    c.fillRect(i*2, can.height - data[i]/2, 1, data[i]/2);
                }}
            }}
            document.getElementById('playBtn').onclick = play;
        </script>
        """
        components.html(html_mixer, height=300)
    else: st.error("Need 2 MP3 files")

st.markdown("<div style='text-align:center; color:#333; font-size:10px;'>อยู่นิ่งๆ ไม่เจ็บตัว | OMNI COMMAND V.3</div>", unsafe_allow_html=True)
