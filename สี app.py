import streamlit as st
import os 
import base64
import random
import time
import math
from datetime import datetime, timedelta, date
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# ==========================================
# 1. CRITICAL INITIALIZATION (ต้องรันก่อนอันดับแรก)
# ==========================================
st.set_page_config(page_title="SYNAPSE X", layout="wide")

# จัดการ Session State ให้เรียบร้อยตั้งแต่ต้นน้ำ
if 'theme_color' not in st.session_state: st.session_state['theme_color'] = "#39FF14"
if 'bg_color' not in st.session_state: st.session_state['bg_color'] = "#000000"
if 'user' not in st.session_state: st.session_state['user'] = "Ta101"
if 'song_index' not in st.session_state: st.session_state['song_index'] = 0

@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            if "private_key" in fb_creds:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n").strip().strip('"')
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_db_url"]
            })
            return True
        except Exception as e:
            st.error(f"🛰️ Firebase Connection Error: {e}")
    return False

init_firebase()

# ==========================================
# 2. UI STYLING
# ==========================================
theme_clr = st.session_state['theme_color']
bg_clr = st.session_state['bg_color']

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp {{ 
        background-color: {bg_clr} !important; 
        color: #FFFFFF !important; 
        font-family: 'Orbitron', sans-serif; 
    }}
    /* บังคับสีตัวอักษรทุกจุดให้เห็นชัดบนพื้นหลังดำ */
    h1, h2, h3, p, span, div, label {{ color: #FFFFFF !important; }}
    .stButton>button {{ 
        border: 2px solid {theme_clr} !important; 
        color: {theme_clr} !important; 
        background: transparent !important; 
        border-radius: 10px; 
    }}
    .stButton>button:hover {{ background: {theme_clr} !important; color: black !important; }}
    .neon-box {{ 
        border: 1px solid {theme_clr}; 
        padding: 15px; border-radius: 10px; 
        text-align: center; box-shadow: 0 0 10px {theme_clr}; 
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. CORE MODULES
# ==========================================

def room_core():
    st.markdown(f"<h2 style='text-align:center;'>🚀 CORE COMMAND</h2>", unsafe_allow_html=True)
    now = datetime.utcnow() + timedelta(hours=7)
    st.markdown(f"""
        <div class="neon-box">
            <h1 style="margin:0; color:{st.session_state.theme_color};">{now.strftime('%H:%M:%S')}</h1>
            <p style="margin:0;">AGENT: {st.session_state.user} | 'อยู่นิ่งๆ ไม่เจ็บตัว'</p>
        </div>
    """, unsafe_allow_html=True)
    seconds = (now.hour * 3600) + (now.minute * 60) + now.second
    progress = seconds / 86400
    st.progress(min(progress, 1.0))

def room_radar():
    st.markdown(f"<h2>🛰️ SATELLITE RADAR</h2>", unsafe_allow_html=True)
    loc = get_geolocation()
    all_users = db.reference('users').get()
    lat, lon = (loc['coords']['latitude'], loc['coords']['longitude']) if loc else (13.7367, 100.5231)
    m = folium.Map(location=[lat, lon], zoom_start=16, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
    folium.Marker([lat, lon], tooltip="YOU", icon=folium.Icon(color='red', icon='user', prefix='fa')).add_to(m)
    if all_users:
        for uid, data in all_users.items():
            if uid != st.session_state.user and data.get('lat'):
                folium.Marker([data['lat'], data['lon']], tooltip=uid, icon=folium.Icon(color='green')).add_to(m)
    st_folium(m, width="100%", height=450, key="radar_map")
    if st.button("📡 BROADCAST POSITION", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': lat, 'lon': lon, 'ts': time.time()})
        st.toast("Intelligence Data Transmitted!")

def room_comms():
    st.markdown(f"<h2>💬 COMM CENTER</h2>", unsafe_allow_html=True)
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
                    db.reference('public_chat').push({'u': st.session_state.user, 'm': msg, 'f': f_b64, 'ft': f_type, 'ts': time.time()})
                    st.rerun()
        msgs = db.reference('public_chat').order_by_key().limit_to_last(15).get()
        if msgs:
            for v in reversed(list(msgs.values())):
                st.markdown(f"🟢 **{v.get('u')}**: {v.get('m','')}")
                if v.get('f'):
                    raw = base64.b64decode(v['f'])
                    if "image" in v['ft']: st.image(raw, width=300)
                    elif "video" in v['ft']: st.video(raw)
    with t2:
        all_u = db.reference('users').get()
        friends = [uid for uid in all_u.keys() if uid != st.session_state.user] if all_u else []
        target = st.selectbox("🎯 Target Agent:", [""] + friends)
        if target:
            call_js = f"""
            <div style="background:#111; padding:15px; border:1px solid {st.session_state.theme_color}; border-radius:10px; text-align:center;">
                <button id="cBtn" style="width:100%; padding:10px; background:#28a745; color:white; border:none; border-radius:5px;">📞 CALL {target}</button>
                <audio id="rAudio" autoplay></audio>
            </div>
            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <script>
                const peer = new Peer('{st.session_state.user}');
                peer.on('call', c => {{ navigator.mediaDevices.getUserMedia({{audio:true}}).then(s=>{{ c.answer(s); c.on('stream',rs=>{{document.getElementById('rAudio').srcObject=rs;}}); }}) }});
                document.getElementById('cBtn').onclick = () => {{
                    navigator.mediaDevices.getUserMedia({{audio:true}}).then(s=>{{ const c=peer.call('{target}',s); c.on('stream',rs=>{{document.getElementById('rAudio').srcObject=rs;}}); }});
                }};
            </script>
            """
            components.html(call_js, height=200)

def room_music():
    st.markdown(f"<h2 style='text-align:center;'>🎧 HOLOGRAPHIC STATION</h2>", unsafe_allow_html=True)
    songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if not songs:
        st.warning("⚠️ ไม่พบไฟล์เพลงในระบบ")
        return
    s_a = st.selectbox("🎯 SELECT SOURCE", ["-- STANDBY --"] + songs, index=st.session_state.song_index + 1)
    if s_a != "-- STANDBY --":
        st.session_state.song_index = songs.index(s_a)
        with open(s_a, "rb") as f:
            song_b64 = base64.b64encode(f.read()).decode()
        
        visualizer_html = f"""
        <div style="background: #000; border: 3px solid {st.session_state.theme_color}; border-radius: 20px; padding: 15px;">
            <canvas id="canvas" style="width: 100%; height: 220px;"></canvas>
            <button id="pBtn" style="width: 100%; margin-top:10px; padding: 15px; background: transparent; border: 2px solid {st.session_state.theme_color}; color: {st.session_state.theme_color}; font-family: Orbitron; cursor: pointer;">[ PLAY / PAUSE ]</button>
            <audio id="audio" src="data:audio/mp3;base64,{song_b64}"></audio>
        </div>
        <script>
            const canvas = document.getElementById('canvas'); const ctx = canvas.getContext('2d');
            const audio = document.getElementById('audio'); const btn = document.getElementById('pBtn');
            let aCtx, ans, src, data;
            btn.onclick = () => {{
                if (!aCtx) {{
                    aCtx = new AudioContext(); ans = aCtx.createAnalyser();
                    src = aCtx.createMediaElementSource(audio);
                    src.connect(ans); ans.connect(aCtx.destination);
                    ans.fftSize = 128; data = new Uint8Array(ans.frequencyBinCount);
                    draw();
                }}
                audio.paused ? audio.play() : audio.pause();
            }};
            function draw() {{
                requestAnimationFrame(draw); ans.getByteFrequencyData(data);
                ctx.fillStyle = 'black'; ctx.fillRect(0,0,canvas.width,canvas.height);
                data.forEach((v, i) => {{
                    ctx.fillStyle = `hsl(${{(i/data.length)*360}}, 100%, 50%)`;
                    ctx.fillRect(i*(canvas.width/data.length)*2, canvas.height-v*0.8, (canvas.width/data.length)*2-2, v*0.8);
                }});
            }}
        </script>
        """
        components.html(visualizer_html, height=400)

def room_sensor():
    st.markdown(f"<h2 style='text-align:center;'>📟 SENSOR HUB</h2>", unsafe_allow_html=True)
    sensor_js = f"""
    <div style="background: #000; border: 2px solid {st.session_state.theme_color}; border-radius: 20px; padding: 20px; font-family: 'Orbitron'; color: white; text-align:center;">
        <small>📳 MOTION DETECTOR</small>
        <h1 id="mag_val" style="font-size: 50px; color: #f0f;">1.000</h1>
        <button id="sBtn" style="width: 100%; padding: 15px; background: transparent; border: 2px solid {st.session_state.theme_color}; color: {st.session_state.theme_color}; cursor: pointer;">[ START SENSORS ]</button>
    </div>
    <script>
        document.getElementById('sBtn').onclick = () => {{
            window.addEventListener('devicemotion', (e) => {{
                const acc = e.accelerationIncludingGravity;
                let mag = Math.sqrt(acc.x**2 + acc.y**2 + acc.z**2) / 9.806;
                document.getElementById('mag_val').innerText = mag.toFixed(3);
            }});
            document.getElementById('sBtn').style.display = 'none';
        }};
    </script>
    """
    components.html(sensor_js, height=250)

def room_logic():
    st.markdown(f"<h2 style='text-align:center;'>🧬 THE TRUTH DECODER</h2>", unsafe_allow_html=True)
    
    def decode_truth(dt):
        day_val = dt.isoweekday() # 1=Mon, 7=Sun
        # ธาตุตามตำราไทย (รูปที่ 2)
        elements = {1:"ไฟ (อาทิตย์)", 2:"ดิน (จันทร์)", 3:"ลม (อังคาร)", 4:"น้ำ (พุธ)", 5:"ดิน (พฤหัส)", 6:"น้ำ (ศุกร์)", 7:"ไฟ (เสาร์)"}
        # ปีนักษัตร (พ.ศ. 2527 = ชวด)
        zodiacs = ["มะเมีย", "มะแม", "วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง"]
        zodiac = zodiacs[(dt.year + 543) % 12]
        
        # คำนวณจันทรคติแบบง่าย
        ref = date(1900, 1, 1)
        pos = ((dt - ref).days - 0.5) % 29.53
        phase = f"ขึ้น {int(pos)+1} ค่ำ" if pos <= 14.76 else f"แรม {int(pos-14.76)+1} ค่ำ"
        
        res = math.sqrt(day_val**2 + (int(pos)%15)**2)
        return {"res": round(res, 4), "phase": phase, "zodiac": zodiac, "element": elements.get(day_val, "ไม่ระบุ")}

    target_date = st.date_input("เลือกวันที่ตรวจสอบ", value=date.today())
    if target_date:
        d = decode_truth(target_date)
        st.markdown(f"""
            <div class="neon-box">
                <small>รหัสพิกัดความจริง</small>
                <h1 style="color:{st.session_state.theme_color}; font-size:60px;">{d['res']}</h1>
                <p>ปี{d['zodiac']} | ธาตุ{d['element']} | {d['phase']}</p>
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# 4. MAIN PROGRAM
# ==========================================
def main():
    with st.sidebar:
        st.title("⚙️ SYSTEM")
        # ใช้ก้ามปู ['user'] ปลอดภัยกว่า
        new_user = st.text_input("AGENT ID", value=st.session_state['user'])
        if new_user != st.session_state['user']:
            st.session_state['user'] = new_user
            st.rerun()

        st.session_state['theme_color'] = st.color_picker("THEME", st.session_state['theme_color'])
        st.session_state['bg_color'] = st.color_picker("BACKGROUND", st.session_state['bg_color'])
        st.caption(f"STATUS: ONLINE | AGENT: {st.session_state['user']}")

    tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "🎧 MUSIC", "📟 SENSOR", "🧬 LOGIC"])
    rooms = [room_core, room_radar, room_comms, room_music, room_sensor, room_logic]
    
    for i, tab in enumerate(tabs):
        with tab:
            rooms[i]()

if __name__ == "__main__":
    main()
