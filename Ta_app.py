import streamlit as st
import os 
import base64
import random
import time
import json
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# ==========================================
# 1. INITIAL SETUP (ฝังคีย์ตรงเสถียรที่สุด)
# ==========================================
@st.cache_resource
def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'user' not in st.session_state: st.session_state.user = "Ta101"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0

    if not firebase_admin._apps:
        try:
            if "firebase_db_url" not in st.secrets:
                st.error("🚨 ระบบขัดข้อง: ไม่พบข้อมูล firebase_db_url ในช่อง Secrets ครับ")
                st.stop()
                
            pk = (
                "-----BEGIN PRIVATE KEY-----\n"
                "MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDV5dVoW3hzqShK\n"
                "dV9ff8WXAYjYAyvCd+CL1M+2G0X59waOZ8Q+v1uBssg4KjM9ErWiNT4sayy2DDYF\n"
                "kDHFOxMyyjXHxKGe3Mh0Bum9Qt05zJW2kC7QUDe+2sm58f+hTbyXPydnwxlNoxSE\n"
                "VCjkybEeVUGYMwCJ3feF5Cwa7YRl9Ysf8php2rLIInyXVR6W/eSpRG5wTcyvujm6\n"
                "VYOURHqEJnh0G/BQBGpC0fhCj5eyVwS101EvGkBt4GQRGno/lDVnGc56qgI+aH8D\n"
                "piOyXaHESSSOR6EqrhJxBZQNDR0XHQ6+LikQ4b0MTeQlA7EFfq987z1X7WayRGVp\n"
                "TczT9qIvAgMBAAECgf9DyxeosC0AMYXcGcNKTnpQIt25W4WdSfuVzmm89jgmmlFr\n"
                "xM4QKsSQjPMEUmgTHPIU7fx4CCyv9W+Y2GydrxPdZk85ZektMXZ13a62C1rU5fHa\n"
                "q9UIo1Sxa0oxN6WqVs924sl6HkGz7CjjNAcVTir1WxZhRzsURee6F3DscWex66DQ\n"
                "4DjCfCfEngKfcv4cMiDYWgGelOgsFy+/BMkTmTbpAE3EQUc76pMiamqDZJO2ELQM\n"
                "rnydZTqqFwmIIIZuqrOlhTnpm0UTOlKN7RG+20jzrkOYP1v23jRNeJL/P3UmUtD4\n"
                "sw1ZQ1UAwkXiKo10/mA6lMDhAILy/ualdboTsKUCgYEA7ccOvKsVcDaw99ol0fPA\n"
                "pjhPn3yNIMQsWLq/3Vm9a9tzgTPjH+kkKrMfpDfdoSjobHomwuMIB82NcQUyCoqx\n"
                "bw9GCAIYnbBpaqpKGJC6VEGYHOD7d6ROEYX/HznEpwMsZwGqzFHjdFOORiKu4Dr7\n"
                "7DBPNAlhXdWI25KX+eHBP20CgYEA5kpHu79ak+925Mg91hPKgkx4U+F07Erv8Un5\n"
                "qEjwibftWCgqCZH/DZW7nX+ZceJtpeD5/PzctzYnTR1oayD6pG9XOiqspKRf5i9U\n"
                "wPVbtCRulfwU3X7Q07H8B7uv3fyurTEgSEa2pe1bZiffAWHd20l0KwSL8XKw35EI\n"
                "sZtEuosCgYBD2KSv2PFJD5H3ZtubyL2TsEWn8FYkn1U4DDFq64xNFlUi7LdGB7Q2\n"
                "Kt5AcWBf99g5+7DLsxQ7hb9yHFVnBKQUWHtXFaIIfKnXsbdqwwEnwX+x3dBjFxLf\n"
                "lShytH0UWqd0zNj7a/JG4wCZqpPTj4EKp84xvut1ZtSiMnYC6xPFEQKBgQDMB+Om\n"
                "I9NMXk0oRYEDumUhLD8vkgDVmU8cqD3ZK0ZxvdM619rmv8MJdi/TSsnYbJRY8wqJ\n"
                "aj7i08feOr/Yqk9mgH73ufdbp4aPmj+s9bVZ1S1lFQIine8PoyzhQYalfNBBOwceo\n"
                "QX5xY+omiAy8XMkDEAEsW8rhEIxEh2r8cGRkIQKBgQCLt/F2c4y9YNEv6NOrzWmL\n"
                "+esSDjRo1jBDE4OkaDpTq8mSs+IjrhOYvGQ2qFnTVrrLKAHUkMurPl9ajmTkWsMs\n"
                "ndrc4eogY6fFCBD1uxPfjsJdTHlLKVsSnQSLBck0/lAq8QwcFlpI5F9/PW/S8HueT\n"
                "p9ZxD44K3CFPeUPenGQPEw==\n"
                "-----END PRIVATE KEY-----\n"
            )

            fb_creds = {
                "type": "service_account",
                "project_id": "sooksun-101",
                "private_key_id": "bc48e69bc03ee880b2a94e17e09b88d13e66267d",
                "private_key": pk,
                "client_email": "firebase-adminsdk-fbsvc@sooksun-101.iam.gserviceaccount.com",
                "client_id": "110249511757111431543",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40sooksun-101.iam.gserviceaccount.com",
                "universe_domain": "googleapis.com"
            }
            
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_db_url"]
            })
        except Exception as e:
            st.error(f"🛰️ Firebase Connection Error: {e}")
            st.stop()
    return True

init_system()

# ==========================================
# 2. UI STYLING & NEON THEME
# ==========================================
st.set_page_config(page_title="SYNAPSE X", layout="wide")
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp {{ background-color: {st.session_state.bg_color} !important; color: #FFFFFF !important; font-family: 'Orbitron', sans-serif; }}
    .stButton>button {{ border: 2px solid {st.session_state.theme_color} !important; color: {st.session_state.theme_color} !important; background: transparent !important; border-radius: 10px; font-weight: bold; }}
    .stButton>button:hover {{ background: {st.session_state.theme_color} !important; color: black !important; }}
    .neon-box {{ border: 1px solid {st.session_state.theme_color}; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 0 10px {st.session_state.theme_color}; }}
    #MainMenu {{visibility: hidden;}} footer {{visibility: hidden;}} header {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. MODULES (ระบบแยกห้องทำงาน)
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
    seconds = (now.hour * 3600) + (now.minute * 60) + now.second
    progress = seconds / 86400
    st.write(f"⏳ System Uptime: {progress*100:.2f}%")
    st.progress(min(progress, 1.0))

def room_radar():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color};'>🛰️ SATELLITE RADAR</h2>", unsafe_allow_html=True)
    loc = get_geolocation()
    lat, lon = 13.7367, 100.5231
    if loc and 'coords' in loc:
        try:
            lat = loc['coords']['latitude']
            lon = loc['coords']['longitude']
        except Exception: pass
            
    all_users = db.reference('users').get()
    m = folium.Map(location=[lat, lon], zoom_start=16, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
    folium.Marker([lat, lon], tooltip="YOU", icon=folium.Icon(color='red', icon='user', prefix='fa')).add_to(m)
    
    if all_users and isinstance(all_users, dict):
        for uid, data in all_users.items():
            if uid != st.session_state.user and isinstance(data, dict) and data.get('lat'):
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
                    db.reference('public_chat').push({'u': st.session_state.user, 'm': msg, 'f': f_b64, 'ft': f_type, 'ts': time.time()})
                    st.rerun()
                    
        try: msgs = db.reference('public_chat').order_by_key().limit_to_last(15).get()
        except Exception: msgs = None
        if msgs and isinstance(msgs, dict):
            for v in reversed(list(msgs.values())):
                if isinstance(v, dict):
                    st.markdown(f"🟢 **{v.get('u')}**: {v.get('m','')}")
                    if v.get('f'):
                        raw = base64.b64decode(v['f'])
                        if "image" in v.get('ft', ''): st.image(raw, width=300)
                        elif "video" in v.get('ft', ''): st.video(raw)
                        
    with t2:
        all_u = db.reference('users').get()
        friends = [uid for uid in all_u.keys() if uid != st.session_state.user] if all_u and isinstance(all_u, dict) else []
        target = st.selectbox("🎯 Target Agent:", [""] + friends)
        if target:
            call_js = """
            <div style="background:#111; padding:15px; border:1px solid %s; border-radius:10px; text-align:center;">
                <button id="cBtn" style="width:100%%; padding:10px; background:#28a745; color:white; border:none; border-radius:5px; font-family:monospace; font-weight:bold; cursor:pointer;">📞 CALL %s</button>
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
            """ % (st.session_state.theme_color, target, st.session_state.user, target)
            components.html(call_js, height=200)

def room_music():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-shadow: 0 0 20px {st.session_state.theme_color}; text-align:center;'>🎧 SYNAPSE HOLOGRAPHIC STATION</h2>", unsafe_allow_html=True)
    songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if not songs:
        st.warning("⚠️ ไม่พบสัญญาณเสียงในหน่วยความจำ")
        return
        
    s_a = st.selectbox("🎯 SELECT SIGNAL SOURCE", ["-- STANDBY --"] + songs, index=min(st.session_state.song_index + 1, len(songs)))
    song_b64, song_name = "", "WAITING FOR SIGNAL..."
    if s_a != "-- STANDBY --":
        with open(s_a, "rb") as f: song_b64 = base64.b64encode(f.read()).decode()
        st.session_state.song_index = songs.index(s_a)
        song_name = s_a

    visualizer_html = f"""
    <div style="background: #000; border: 3px solid {st.session_state.theme_color}; border-radius: 20px; padding: 15px; box-shadow: 0 0 30px {st.session_state.theme_color}55;">
        <div style="overflow: hidden; white-space: nowrap; background: #050505; border: 1px solid {st.session_state.theme_color}55; border-radius: 8px; margin-bottom: 10px; padding: 8px;">
            <p id="mText" style="display: inline-block; padding-left: 100%; font-family: Orbitron, monospace; font-size: 16px; color: white; animation: marquee 12s linear infinite;">
                <span style="animation: rainbowText 4s linear infinite;">>>></span> {song_name} <span style="animation: rainbowText 4s linear infinite;"><<< ANALYZING... SECURE LINE... >>></span>
            </p>
        </div>
        <canvas id="canvas" style="width: 100%; height: 220px; background: #000; border-radius: 10px;"></canvas>
        <button id="pBtn" style="width: 100%; margin-top:10px; padding: 15px; background: transparent; border: 2px solid {st.session_state.theme_color}; border-radius: 10px; color: {st.session_state.theme_color}; font-family: Orbitron; font-weight:bold; cursor: pointer;">[ CLICK TO SYNC ]</button>
        <audio id="audio" src="data:audio/mp3;base64,{song_b64}"></audio>
    </div>
    <style>
        @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
        @keyframes rainbowText {{ 0%, 100% {{ color: #ff0000; }} 50% {{ color: #00ff00; }} }}
    </style>
    <script>
    const canvas = document.getElementById('canvas'); const ctx = canvas.getContext('2d');
    const audio = document.getElementById('audio'); const btn = document.getElementById('pBtn'); const mText = document.getElementById('mText');
    let aCtx, ans, src, data; mText.style.animationPlayState = 'paused';
    btn.onclick = function() {{
        if (!aCtx) {{
            aCtx = new (window.AudioContext || window.webkitAudioContext)(); ans = aCtx.createAnalyser();
            src = aCtx.createMediaElementSource(audio); src.connect(ans); ans.connect(aCtx.destination);
            ans.fftSize = 128; data = new Uint8Array(ans.frequencyBinCount); draw();
        }}
        if (audio.paused) {{ audio.play(); btn.innerText = "[ SIGNAL ACTIVE ]"; mText.style.animationPlayState = 'running'; }}
        else {{ audio.pause(); btn.innerText = "[ SIGNAL PAUSED ]"; mText.style.animationPlayState = 'paused'; }}
    }};
    function draw() {{
        requestAnimationFrame(draw); ans.getByteFrequencyData(data);
        ctx.fillStyle = 'rgba(0,0,0,0.2)'; ctx.fillRect(0,0,canvas.width,canvas.height);
        let x = 0; const bW = (canvas.width / data.length) * 2;
        for(let i=0; i<data.length; i++) {{
            let bH = data[i]*0.9; let h = (i/data.length)*360;
            ctx.fillStyle = `hsl(${{h}}, 100%, 50%)`; ctx.shadowBlur = 10; ctx.shadowColor = ctx.fillStyle;
            ctx.fillRect(x, canvas.height-bH, bW-2, bH); x += bW;
        }}
    }}
    </script>
    """
    components.html(visualizer_html, height=420)

def room_sensor():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-shadow: 0 0 20px {st.session_state.theme_color}; text-align:center;'>📟 SYNAPSE SENSOR HUB</h2>", unsafe_allow_html=True)
    all_sensors_js = f"""
    <div style="background: #000; border: 2px solid {st.session_state.theme_color}; border-radius: 20px; padding: 20px; font-family: 'Orbitron', monospace; color: white;">
        <div style="overflow: hidden; white-space: nowrap; background: #0a0a0a; border: 1px solid {st.session_state.theme_color}55; border-radius: 5px; margin-bottom: 15px; padding: 5px;">
            <p style="display: inline-block; padding-left: 100%; font-size: 14px; color: {st.session_state.theme_color}; animation: marquee 15s linear infinite;">SYSTEM ONLINE >>> MONITORING REAL-TIME DATA...</p>
        </div>
        <div style="border: 1px solid {st.session_state.theme_color}33; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
            <small style="color: {st.session_state.theme_color};">🔊 SONIC ANALYZER</small>
            <canvas id="visualizer" style="width: 100%; height: 80px; background: #050505; border-radius: 5px; margin: 10px 0;"></canvas>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: center;">
                <div><small>VOLUME</small><h2 id="vol_val" style="color: #0f0; margin:0;">0</h2></div>
                <div><small>PITCH (Hz)</small><h2 id="freq_val" style="color: #00ffff; margin:0;">0</h2></div>
            </div>
        </div>
        <div style="border: 1px solid {st.session_state.theme_color}33; padding: 15px; border-radius: 10px;">
            <small style="color: {st.session_state.theme_color};">📳 MOTION DETECTOR</small>
            <div style="text-align: center; margin-top: 10px;">
                <small>MAGNITUDE (G)</small><h1 id="mag_val" style="font-size: 45px; color: #f0f; margin:0;">1.000</h1>
            </div>
        </div>
        <button id="startBtn" style="width: 100%; margin-top: 15px; padding: 15px; background: transparent; border: 2px solid {st.session_state.theme_color}; border-radius: 10px; color: {st.session_state.theme_color}; font-family: Orbitron; cursor: pointer; font-weight: bold;">[ INITIALIZE SENSOR ARRAY ]</button>
    </div>
    <script>
        const btn = document.getElementById('startBtn'); const v_canvas = document.getElementById('visualizer'); const v_ctx = v_canvas.getContext('2d');
        btn.onclick = async () => {{
            btn.style.display = 'none';
            try {{
                const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
                const aCtx = new (window.AudioContext || window.webkitAudioContext)(); const analyser = aCtx.createAnalyser();
                const source = aCtx.createMediaStreamSource(stream); analyser.fftSize = 128; source.connect(analyser);
                const dataArray = new Uint8Array(analyser.frequencyBinCount);
                function updateAudio() {{
                    requestAnimationFrame(updateAudio); analyser.getByteFrequencyData(dataArray);
                    v_ctx.clearRect(0, 0, v_canvas.width, v_canvas.height); let sum = 0, maxV = 0, maxI = 0;
                    for (let i = 0; i < dataArray.length; i++) {{
                        let v = dataArray[i]; sum += v; if(v > maxV) {{ maxV = v; maxI = i; }}
                        v_ctx.fillStyle = '{st.session_state.theme_color}'; v_ctx.fillRect(i * (v_canvas.width / dataArray.length), v_canvas.height - v/2, 2, v/2);
                    }}
                    document.getElementById('vol_val').innerText = Math.round(sum/dataArray.length);
                    document.getElementById('freq_val').innerText = (sum/dataArray.length > 5) ? Math.round(maxI * aCtx.sampleRate / analyser.fftSize) : 0;
                }} updateAudio();
            }} catch(e) {{ alert("Audio Fault: " + e); }}
            try {{
                if (typeof DeviceMotionEvent.requestPermission === 'function') {{ await DeviceMotionEvent.requestPermission(); }}
                window.addEventListener('devicemotion', (e) => {{
                    const acc = e.accelerationIncludingGravity; if (!acc) return;
                    let x = acc.x||0, y = acc.y||0, z = acc.z||0;
                    document.getElementById('mag_val').innerText = (Math.sqrt(x*x + y*y + z*z) / 9.80665).toFixed(3);
                }});
            }} catch(err) {{}}
        }};
    </script>
    """
    components.html(all_sensors_js, height=550)

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
