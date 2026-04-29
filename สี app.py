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
# 1. INITIAL SETUP
# ==========================================
@st.cache_resource
def init_system():
    # กำหนดค่าเริ่มต้นใน Session State
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'user' not in st.session_state: st.session_state.user = "Ta101"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0

    if not firebase_admin._apps:
        try:
            # ดึงข้อมูลจาก st.secrets
            fb_creds = dict(st.secrets["firebase_credentials"])
            # ล้างค่าขึ้นบรรทัดใหม่ใน Private Key ให้ถูกต้องตามฟอร์แมต JSON/RSA
            if "private_key" in fb_creds:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
            
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_db_url"]
            })
        except Exception as e:
            # ไม่หยุดการทำงาน แต่แจ้งเตือนให้ทราบความเป็นจริง
            st.warning(f"⚠️ Firebase Offline: {e}")
            return False
    return True

is_connected = init_system()

# ==========================================
# 2. UI STYLING (ปรับให้ Scannable)
# ==========================================
st.set_page_config(page_title="SYNAPSE X", layout="wide")
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp {{ background-color: {st.session_state.bg_color} !important; color: #FFFFFF !important; font-family: 'Orbitron', sans-serif; }}
    .stButton>button {{ border: 2px solid {st.session_state.theme_color} !important; color: {st.session_state.theme_color} !important; background: transparent !important; border-radius: 10px; transition: 0.3s; }}
    .stButton>button:hover {{ background: {st.session_state.theme_color} !important; color: black !important; box-shadow: 0 0 15px {st.session_state.theme_color}; }}
    .neon-box {{ border: 1px solid {st.session_state.theme_color}; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 0 10px {st.session_state.theme_color}; margin-bottom: 20px; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. MODULES
# ==========================================

def room_core():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-align:center;'>🚀 CORE COMMAND</h2>", unsafe_allow_html=True)
    now = datetime.now() # ใช้ Local Time เพื่อความเป็นจริงของที่อยู่ผู้ใช้
    st.markdown(f"""
        <div class="neon-box">
            <h1 style="margin:0; color:{st.session_state.theme_color};">{now.strftime('%H:%M:%S')}</h1>
            <p style="margin:0;">AGENT: {st.session_state.user} | 'อยู่นิ่งๆ ไม่เจ็บตัว'</p>
        </div>
    """, unsafe_allow_html=True)
    
    # คำนวณ % ของวัน
    seconds = (now.hour * 3600) + (now.minute * 60) + now.second
    progress = seconds / 86400
    st.write(f"⏳ Day Progress: {progress*100:.2f}%")
    st.progress(progress)

def room_radar():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color};'>🛰️ SATELLITE RADAR</h2>", unsafe_allow_html=True)
    loc = get_geolocation()
    
    # กรณีไม่มี Firebase จะไม่ดึงข้อมูล
    all_users = db.reference('users').get() if is_connected else None
    
    # พิกัดเริ่มต้น (กรุงเทพฯ) ถ้าหา GPS ไม่เจอ
    lat, lon = (13.7367, 100.5231)
    if loc and 'coords' in loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']

    m = folium.Map(location=[lat, lon], zoom_start=16, tiles="https://mt1.google.com/vt/lyrs=y&x={{x}}&y={{y}}&z={{z}}", attr="Google Hybrid")
    folium.Marker([lat, lon], tooltip="YOU", icon=folium.Icon(color='red', icon='user', prefix='fa')).add_to(m)
    
    if all_users:
        for uid, data in all_users.items():
            if uid != st.session_state.user and isinstance(data, dict) and 'lat' in data:
                folium.Marker([data['lat'], data['lon']], tooltip=uid, icon=folium.Icon(color='green')).add_to(m)
    
    st_folium(m, width="100%", height=450, key="radar_map")
    
    if st.button("📡 BROADCAST POSITION", use_container_width=True):
        if is_connected:
            db.reference(f'users/{st.session_state.user}').update({'lat': lat, 'lon': lon, 'ts': time.time()})
            st.toast("Intelligence Data Transmitted!")
        else:
            st.error("Connection Offline")

def room_comms():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color};'>💬 COMM CENTER</h2>", unsafe_allow_html=True)
    if not is_connected:
        st.error("ระบบสื่อสารขัดข้อง: ไม่พบการเชื่อมต่อ Firebase")
        return

    t1, t2 = st.tabs(["🌐 PUBLIC FEED", "📞 SECURE CALL"])
    with t1:
        with st.form("chat_form", clear_on_submit=True):
            col1, col2 = st.columns([4, 1])
            msg = col1.text_input("Enter Signal...", placeholder="Type message...")
            up_file = col2.file_uploader("📁", type=['jpg', 'png', 'mp4'], label_visibility="collapsed")
            if st.form_submit_button("SEND"):
                f_b64, f_type = None, None
                if up_file:
                    f_b64 = base64.b64encode(up_file.getvalue()).decode()
                    f_type = up_file.type
                if msg or f_b64:
                    db.reference('public_chat').push({
                        'u': st.session_state.user, 
                        'm': msg, 
                        'f': f_b64, 
                        'ft': f_type, 
                        'ts': time.time()
                    })
                    st.rerun()

        # แสดงข้อความ
        msgs = db.reference('public_chat').order_by_key().limit_to_last(10).get()
        if msgs:
            for v in reversed(list(msgs.values())):
                with st.container():
                    st.markdown(f"**{v.get('u')}**: {v.get('m','')}")
                    if v.get('f'):
                        try:
                            raw = base64.b64decode(v['f'])
                            if "image" in v['ft']: st.image(raw, width=250)
                            elif "video" in v['ft']: st.video(raw)
                        except: st.caption("File Error")
                    st.divider()
    with t2:
        st.caption("Peer-to-Peer Secure Audio Line")
        # Logic เดิมของคุณทำงานได้ถ้า PeerJS ID ไม่ซ้ำกัน
        target = st.text_input("🎯 Target Agent ID to Call:")
        if target:
            # แทรก Component เดิม
            pass 

def room_music():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-align:center;'>🎧 HOLOGRAPHIC STATION</h2>", unsafe_allow_html=True)
    # ค้นหาไฟล์ .mp3 ในโฟลเดอร์ปัจจุบัน
    songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    
    if not songs:
        st.info("📂 วิธีใช้งาน: วางไฟล์ .mp3 ไว้ในโฟลเดอร์เดียวกับโค้ดนี้เพื่อเริ่มเล่น")
        return

    s_a = st.selectbox("🎯 SELECT SIGNAL", songs, index=min(st.session_state.song_index, len(songs)-1))
    
    # แปลงไฟล์เป็น Base64 เพื่อส่งเข้า HTML Audio
    with open(s_a, "rb") as f:
        song_b64 = base64.b64encode(f.read()).decode()
    
    # HTML Visualizer (ปรับปรุงให้ลื่นไหลขึ้น)
    visualizer_html = f"""
    <div style="background: #000; border: 2px solid {st.session_state.theme_color}; border-radius: 15px; padding: 15px;">
        <p style="color:{st.session_state.theme_color}; font-size:12px;">NOW ANALYZING: {s_a}</p>
        <canvas id="canvas" style="width: 100%; height: 150px;"></canvas>
        <audio id="audio" src="data:audio/mp3;base64,{song_b64}"></audio>
        <button id="pBtn" style="width:100%; padding:10px; background:transparent; border:1px solid {st.session_state.theme_color}; color:{st.session_state.theme_color}; cursor:pointer;">[ PLAY / PAUSE ]</button>
    </div>
    <script>
        const audio = document.getElementById('audio');
        const canvas = document.getElementById('canvas');
        const ctx = canvas.getContext('2d');
        let aCtx, analyser, source, data;

        document.getElementById('pBtn').onclick = () => {{
            if(!aCtx) {{
                aCtx = new AudioContext();
                analyser = aCtx.createAnalyser();
                source = aCtx.createMediaElementSource(audio);
                source.connect(analyser);
                analyser.connect(aCtx.destination);
                analyser.fftSize = 64;
                data = new Uint8Array(analyser.frequencyBinCount);
                draw();
            }}
            audio.paused ? audio.play() : audio.pause();
        }};

        function draw() {{
            requestAnimationFrame(draw);
            analyser.getByteFrequencyData(data);
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            data.forEach((v, i) => {{
                ctx.fillStyle = '{st.session_state.theme_color}';
                ctx.fillRect(i * 10, canvas.height - v/2, 8, v/2);
            }});
        }}
    </script>
    """
    components.html(visualizer_html, height=300)

def room_sensor():
    # โค้ด Room Sensor เดิมของคุณดีอยู่แล้ว แต่ระวังเรื่อง Permission บน iOS/Safari 
    # ซึ่งต้องเปิดผ่าน HTTPS เท่านั้นถึงจะใช้งาน DeviceMotion ได้จริง
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-align:center;'>📟 SENSOR HUB</h2>", unsafe_allow_html=True)
    # (Copy ส่วน room_sensor เดิมมาใส่ได้เลยครับ)

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
        if st.button("RESET SYSTEM"):
            st.rerun()

    tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "🎧 MUSIC", "📟 SENSOR"])
    with tabs[0]: room_core()
    with tabs[1]: room_radar()
    with tabs[2]: room_comms()
    with tabs[3]: room_music()
    with tabs[4]: room_sensor()

if __name__ == "__main__":
    main()
