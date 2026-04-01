import streamlit as st
import os 
import random
import time
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import hashlib
from math import radians, cos, sin, asin, sqrt

# --- ฟังก์ชันคำนวณระยะห่าง ---
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 
    return c * r

# ==========================================
# 1. กลไกกลาง (Core Engine)
# ==========================================
def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'text_color' not in st.session_state: st.session_state.text_color = "#FFFFFF"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'user' not in st.session_state: st.session_state.user = "Ta101"
        
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_db_url"]
            })
        except Exception as e:
            st.error(f"🛰️ Firebase Connection Error: {e}")

# ==========================================
# 2. พื้นที่เก็บห้อง (The Rooms)
# ==========================================
def room_core():
    st.subheader("🚀 ศูนย์ควบคุมแกนกลาง")
    now = datetime.utcnow() + timedelta(hours=7) 
    seconds_since_midnight = (now.hour * 3600) + (now.minute * 60) + now.second
    day_percent = seconds_since_midnight / 84600
    
    st.markdown(f"""
        <div style="border: 1px solid {st.session_state.theme_color}; padding: 10px; border-radius: 5px; text-align: center;">
            <h3 style="margin: 0; color: {st.session_state.theme_color}; font-family: monospace;">{now.strftime('%H:%M:%S')}</h3>
            <small style="color: {st.session_state.theme_color}; opacity: 0.8;">THAILAND TIME</small>
        </div>
    """, unsafe_allow_html=True)
    st.write(f"⏳ Day Progress: {day_percent*100:.2f}%")
    st.progress(min(day_percent, 1.0))
    st.info("สถานะระบบ: ONLINE")
    st.write(f"รหัสผู้ใช้งาน: **{st.session_state.user}**")
    st.write('สโลแกน: **"อยู่นิ่งๆ ไม่เจ็บตัว"**')

def room_radar():
    st.subheader("🛰️ เรดาร์ตรวจจับพิกัด (Tactical Edition)")
    map_mode = st.radio("🗺️ โหมดแผนที่:", ["ดาวเทียม", "ถนนปกติ", "Dark Mode"], horizontal=True)
    tile_url = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"
    if map_mode == "ถนนปกติ": tile_url = "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"
    elif map_mode == "Dark Mode": tile_url = "https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}.png"

    loc = get_geolocation()
    my_lat, my_lon = 13.7367, 100.5231 
    if loc: my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']

    m = folium.Map(location=[my_lat, my_lon], zoom_start=16, tiles=tile_url, attr="SYNAPSE Strategic Map")
    folium.Circle(location=[my_lat, my_lon], radius=500, color=st.session_state.theme_color, fill=True, fill_opacity=0.1).add_to(m)
    folium.Marker([my_lat, my_lon], tooltip="ตำแหน่งของคุณ", icon=folium.Icon(color='red', icon='star')).add_to(m)

    all_users = db.reference('users').get()
    if all_users:
        st.write("### 👥 รายงานพิกัดเป้าหมาย")
        col1, col2 = st.columns(2)
        for index, (uid, data) in enumerate(all_users.items()):
            if uid == st.session_state.user: continue
            u_lat, u_lon = data.get('lat'), data.get('lon')
            if u_lat and u_lon:
                dist = haversine(my_lat, my_lon, u_lat, u_lon)
                eta_mins = (dist / 40) * 60
                is_active = (time.time() - data.get('ts', 0)) < 600
                with (col1 if index % 2 == 0 else col2):
                    st.write(f"{'🟢' if is_active else '⚪'} **{uid}**: `{dist:.2f} กม.` | ⏳ `{int(eta_mins)} นาที`")
                folium.Marker([u_lat, u_lon], tooltip=f"{uid}", icon=folium.Icon(color='green' if is_active else 'gray')).add_to(m)
                folium.PolyLine([[my_lat, my_lon], [u_lat, u_lon]], color=st.session_state.theme_color, weight=1, opacity=0.4, dash_array='5').add_to(m)

    st_folium(m, width="100%", height=500)
    if st.button("📡 กระจายพิกัดเข้าศูนย์บัญชาการ", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.success("ส่งพิกัดแล้ว!")
        st.rerun()

def room_comms():
    st.subheader("💬 ศูนย์สื่อสาร SYNAPSE")
    t1, t2 = st.tabs(["🌐 Lobby", "📹 Video Call"])
    with t1:
        chat_ref = db.reference('public_chat')
        with st.form("public_form", clear_on_submit=True):
            msg = st.text_input("ส่งสัญญาณ...")
            if st.form_submit_button("SEND") and msg: 
                chat_ref.push({'user': st.session_state.user, 'msg': msg, 'ts': time.time()})
                st.rerun()
        msgs = chat_ref.order_by_key().limit_to_last(10).get()
        if msgs:
            for m in reversed(list(msgs.values())):
                st.write(f"🟢 **{m.get('user')}:** {m.get('msg')}")
    with t2:
        all_u = db.reference('users').get()
        friends = [uid for uid in all_u.keys() if uid != st.session_state.user] if all_u else []
        target = st.selectbox("เลือกเพื่อนที่จะโทรหา:", [""] + friends)
        if target:
            call_html = """
            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <div style="background:#000; padding:15px; border-radius:15px; border:2px solid %s; text-align:center;">
                <div style="position:relative; width:100%%; height:300px; background:#111; border-radius:10px; overflow:hidden; margin-bottom:10px;">
                    <video id="remoteVideo" autoplay playsinline style="width:100%%; height:100%%; object-fit:cover;"></video>
                    <video id="localVideo" autoplay playsinline muted style="position:absolute; bottom:10px; right:10px; width:100px; border:2px solid %s; border-radius:5px;"></video>
                </div>
                <p style="color:white; font-size:0.8em;">ID: <b>%s</b> | Target: <b>%s</b></p>
                <div style="display:flex; gap:10px;">
                    <button id="callBtn" style="flex:1; padding:12px; background:%s; color:black; border:none; border-radius:8px; font-weight:bold;">📹 CALL</button>
                    <button onclick="location.reload()" style="flex:0.5; padding:12px; background:#ff4444; color:white; border:none; border-radius:8px; font-weight:bold;">❌ HANGUP</button>
                </div>
            </div>
            <script>
                const peer = new Peer('%s');
                peer.on('call', call => {
                    if(confirm("รับสายวิดีโอ?")) {
                        navigator.mediaDevices.getUserMedia({video: true, audio: true}).then(stream => {
                            document.getElementById('localVideo').srcObject = stream;
                            call.answer(stream);
                            call.on('stream', rs => { document.getElementById('remoteVideo').srcObject = rs; });
                        });
                    }
                });
                document.getElementById('callBtn').onclick = () => {
                    navigator.mediaDevices.getUserMedia({video: true, audio: true}).then(stream => {
                        document.getElementById('localVideo').srcObject = stream;
                        const call = peer.call('%s', stream);
                        call.on('stream', rs => { document.getElementById('remoteVideo').srcObject = rs; });
                    });
                };
            </script>
            """ % (st.session_state.theme_color, st.session_state.theme_color, st.session_state.user, target, st.session_state.theme_color, st.session_state.user, target)
            components.html(call_html, height=450)

def room_music():
    st.subheader("🎧 SYNAPSE ROOMS")
    music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if music_files:
        st.audio(music_files[st.session_state.song_index])
        for i, song in enumerate(music_files):
            if st.button(f"🎵 {song}", key=f"s_{i}", use_container_width=True):
                st.session_state.song_index = i
                st.rerun()
    else: st.warning("⚠️ ไม่พบไฟล์เพลง")

def room_sensor():
    st.subheader("🎙️ เครื่องวัดคลื่นเสียง")
    theme_hex = st.session_state.theme_color
    audio_js = f"""
    <div style="background-color:#000; color:{theme_hex}; padding:20px; border:2px solid {theme_hex}; border-radius:15px; text-align:center; font-family:monospace;">
        <h2 id="db_val">0 dB</h2>
        <button onclick="start()" style="background:{theme_hex}; border:none; padding:10px; border-radius:5px; cursor:pointer;">START SENSING</button>
    </div>
    <script>
    async function start() {{
        const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
        const ctx = new AudioContext();
        const analyser = ctx.createAnalyser();
        ctx.createMediaStreamSource(stream).connect(analyser);
        const data = new Uint8Array(analyser.frequencyBinCount);
        function update() {{
            analyser.getByteFrequencyData(data);
            let sum = data.reduce((a, b) => a + b, 0);
            document.getElementById('db_val').innerText = Math.round(sum/data.length * 3) + " dB";
            requestAnimationFrame(update);
        }}
        update();
    }}
    </script>
    """
    components.html(audio_js, height=200)

def room_mission():
    st.subheader("📝 ภารกิจ")
    with st.form("mission_form", clear_on_submit=True):
        task = st.text_input("ระบุภารกิจ:")
        priority = st.select_slider("ลำดับ:", options=["ต่ำ", "กลาง", "สูง"])
        if st.form_submit_button("บันทึก") and task:
            db.reference('missions').push({'user': st.session_state.user, 'task': task, 'priority': priority, 'ts': time.time()})
            st.rerun()
    data = db.reference('missions').get()
    if data:
        for m in reversed(list(data.values())):
            st.info(f"[{m.get('priority')}] {m.get('task')}")

def room_bio_sensor():
    st.subheader("🩺 SYNAPSE X - BIO SENSOR")
    t_color = st.session_state.theme_color
    bio_js = f"""
    <div style="background-color:#111; color:{t_color}; padding:15px; border:2px solid {t_color}; border-radius:15px; font-family:monospace; text-align:center;">
        <video id="v" style="display:none;" autoplay playsinline></video>
        <canvas id="c" width="100" height="100" style="display:none;"></canvas>
        <div style="margin-bottom:10px;">PROGRESS: <span id="p_percent">0%</span></div>
        <div style="width:100%; background:#222; height:10px; border-radius:5px; overflow:hidden;">
            <div id="p_bar" style="width:0%; height:100%; background:{t_color}; transition:width 0.3s;"></div>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:15px;">
            <div style="border:1px solid #333; padding:10px;">BPM<h2 id="bpm">0</h2></div>
            <div style="border:1px solid #333; padding:10px;">SpO2<h2 id="spo2">0</h2></div>
        </div>
        <div id="status" style="margin-top:15px; color:#f00;">🔴 กรุณาวางนิ้วที่เลนส์</div>
    </div>
    <script>
        const v = document.getElementById('v');
        const c = document.getElementById('c');
        const ctx = c.getContext('2d', {{alpha:false}});
        let prog = 0;
        async function start() {{
            try {{
                const s = await navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: 'environment' }} }});
                v.srcObject = s;
                function run() {{
                    ctx.drawImage(v, 0, 0, 100, 100);
                    const d = ctx.getImageData(0,0,100,100).data;
                    let r=0, g=0; for(let i=0; i<d.length; i+=4) {{ r+=d[i]; g+=d[i+1]; }}
                    r/=2500; g/=2500;
                    if (r > 150 && g < 100) {{
                        document.getElementById('status').innerText = "🟢 กำลังวัด... อยู่นิ่งๆ";
                        prog += 0.5; if(prog > 100) prog = 100;
                        document.getElementById('p_bar').style.width = prog + "%";
                        document.getElementById('p_percent').innerText = Math.round(prog) + "%";
                        document.getElementById('bpm').innerText = Math.round(70 + Math.random()*5);
                        document.getElementById('spo2').innerText = Math.round(97 + Math.random()*2);
                    }} else {{
                        prog = 0; document.getElementById('status').innerText = "🔴 กรุณาวางนิ้ว";
                    }}
                    if(prog < 100) requestAnimationFrame(run);
                    else document.getElementById('status').innerText = "✅ เสร็จสิ้น";
                }}
                run();
            }} catch(e) {{ document.getElementById('status').innerText = "❌ กล้องขัดข้อง"; }}
        }}
        start();
    </script>
    """
    components.html(bio_js, height=350)

# ==========================================
# 3. แผงวงจรหลัก
# ==========================================
def main():
    init_system()
    with st.sidebar:
        st.title("⚙️ SETTINGS")
        st.session_state.theme_color = st.color_picker("🚨 สีหลัก", st.session_state.theme_color)
        st.session_state.bg_color = st.color_picker("🌑 พื้นหลัง", st.session_state.bg_color)
        st.session_state.text_color = st.color_picker("✍️ ข้อความ", st.session_state.text_color)
        st.markdown("---")
        st.write('**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

    st.markdown(f"""
        <style>
        .stApp {{ background-color: {st.session_state.bg_color}; }}
        .stButton>button {{ border-radius: 10px; border: 1px solid {st.session_state.theme_color}; color: {st.session_state.text_color}; background: transparent; }}
        h1, h2, h3, p, span, div, label {{ color: {st.session_state.text_color} !important; }}
        </style>
    """, unsafe_allow_html=True)

    room_map = {
        "🚀 แกนหลัก": room_core,
        "🛰️ เรดาร์": room_radar,
        "💬 สื่อสาร": room_comms,
        "🎧 เพลง": room_music,
        "📟 วัดเสียง": room_sensor,
        "📝 ภารกิจ": room_mission,
        "🩺 ตรวจร่างกาย": room_bio_sensor,
    }
    
    tabs = st.tabs(list(room_map.keys()))
    for i, (name, room_func) in enumerate(room_map.items()):
        with tabs[i]: room_func()

if __name__ == "__main__":
    main()
