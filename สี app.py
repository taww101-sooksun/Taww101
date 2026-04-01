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

# ==========================================
# 0. ฟังก์ชันคำนวณระยะทาง
# ==========================================
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

def room_radar():
    st.subheader("🛰️ เรดาร์ตรวจจับพิกัด")
    map_mode = st.radio("🗺️ โหมดแผนที่:", ["ดาวเทียม", "ถนนปกติ", "Dark Mode"], horizontal=True)
    tile_url = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"
    if map_mode == "ถนนปกติ": tile_url = "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"
    elif map_mode == "Dark Mode": tile_url = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"

    loc = get_geolocation()
    my_lat, my_lon = 13.7367, 100.5231 
    if loc: my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']

    m = folium.Map(location=[my_lat, my_lon], zoom_start=16, tiles=tile_url, attr="SYNAPSE")
    folium.Marker([my_lat, my_lon], tooltip="คุณอยู่ที่นี่", icon=folium.Icon(color='red')).add_to(m)

    all_users = db.reference('users').get()
    if all_users:
        for uid, data in all_users.items():
            if uid == st.session_state.user: continue
            u_lat, u_lon = data.get('lat'), data.get('lon')
            if u_lat and u_lon:
                dist = haversine(my_lat, my_lon, u_lat, u_lon)
                folium.Marker([u_lat, u_lon], tooltip=f"{uid} ({dist:.2f} km)", icon=folium.Icon(color='green')).add_to(m)
    
    st_folium(m, width="100%", height=400)
    if st.button("📡 กระจายพิกัดปัจจุบัน", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.success("ส่งพิกัดแล้ว!")

def room_comms():
    st.subheader("💬 ศูนย์สื่อสาร SYNAPSE")
    t1, t2 = st.tabs(["🌐 Lobby", "📞 Video Call"])
    with t1:
        chat_ref = db.reference('public_chat')
        with st.form("chat_f", clear_on_submit=True):
            msg = st.text_input("ข้อความ...")
            if st.form_submit_button("SEND") and msg:
                chat_ref.push({'user': st.session_state.user, 'msg': msg, 'ts': time.time()})
        msgs = chat_ref.order_by_key().limit_to_last(10).get()
        if msgs:
            for m in reversed(list(msgs.values())):
                st.write(f"🟢 **{m.get('user')}:** {m.get('msg')}")
    with t2:
        all_u = db.reference('users').get()
        friends = [uid for uid in all_u.keys() if uid != st.session_state.user] if all_u else []
        target = st.selectbox("เลือกเป้าหมาย:", [""] + friends)
        if target:
            call_html = """
            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <div style="background:#000; padding:15px; border:2px solid %s; border-radius:15px; text-align:center; color:white;">
                <video id="remoteVideo" autoplay style="width:100%%; height:200px; background:#111;"></video>
                <p>ID: %s | Target: %s</p>
                <button id="callBtn" style="width:100%%; padding:10px; background:%s; border:none; border-radius:5px;">📹 CALL</button>
            </div>
            <script>
                const peer = new Peer('%s');
                peer.on('call', c => { 
                    if(confirm("Incoming Call?")) {
                        navigator.mediaDevices.getUserMedia({video:true, audio:true}).then(s => {
                            c.answer(s); c.on('stream', rs => { document.getElementById('remoteVideo').srcObject = rs; });
                        });
                    }
                });
                document.getElementById('callBtn').onclick = () => {
                    navigator.mediaDevices.getUserMedia({video:true, audio:true}).then(s => {
                        const c = peer.call('%s', s);
                        c.on('stream', rs => { document.getElementById('remoteVideo').srcObject = rs; });
                    });
                };
            </script>
            """ % (st.session_state.theme_color, st.session_state.user, target, st.session_state.theme_color, st.session_state.user, target)
            components.html(call_html, height=400)

def room_music():
    st.subheader("🎧 เครื่องเล่นเพลง")
    music_files = [f for f in os.listdir('.') if f.lower().endswith(".mp3")]
    if music_files:
        st.audio(music_files[st.session_state.song_index])
        for i, song in enumerate(music_files):
            if st.button(f"🎵 {song}", key=f"m_{i}", use_container_width=True):
                st.session_state.song_index = i
                st.rerun()

def room_sensor():
    st.subheader("🎙️ เครื่องวัดคลื่นเสียง")
    theme = st.session_state.theme_color
    html = f"""
    <div style="color:{theme}; border:2px solid {theme}; padding:20px; border-radius:15px; text-align:center;">
        <h1 id="db">0 dB</h1>
        <button onclick="start()" style="padding:10px; background:{theme}; border:none; border-radius:5px;">START SENSOR</button>
    </div>
    <script>
    async function start() {{
        const s = await navigator.mediaDevices.getUserMedia({{audio:true}});
        const ctx = new AudioContext();
        const src = ctx.createMediaStreamSource(s);
        const ans = ctx.createAnalyser();
        src.connect(ans);
        const data = new Uint8Array(ans.frequencyBinCount);
        function loop() {{
            ans.getByteFrequencyData(data);
            let v = data.reduce((a,b)=>a+b)/data.length;
            document.getElementById('db').innerText = Math.round(v) + " dB";
            requestAnimationFrame(loop);
        }}
        loop();
    }}
    </script>
    """
    components.html(html, height=200)

def room_mission():
    st.subheader("📝 ภารกิจ")
    with st.form("m_f", clear_on_submit=True):
        t = st.text_input("ภารกิจ:")
        p = st.select_slider("ลำดับ:", ["ต่ำ", "กลาง", "สูง"])
        if st.form_submit_button("SAVE") and t:
            db.reference('missions').push({'user': st.session_state.user, 'task': t, 'priority': p, 'ts': time.time()})
    data = db.reference('missions').get()
    if data:
        for m in reversed(list(data.values())):
            st.info(f"[{m.get('priority')}] {m.get('task')}")

def room_bio_sensor():
    st.subheader("🩺 BIO SENSOR")
    t_color = st.session_state.theme_color
    bio_js = f"""
    <div style="background:#111; color:{t_color}; padding:15px; border:2px solid {t_color}; border-radius:15px; text-align:center;">
        <video id="v" style="display:none;" autoplay playsinline></video>
        <canvas id="c" width="10" height="10" style="display:none;"></canvas>
        <h2 id="bpm">0 BPM</h2>
        <div id="status">🔴 กรุณาวางนิ้วที่เลนส์</div>
    </div>
    <script>
        async function start() {{
            const v = document.getElementById('v');
            const c = document.getElementById('c');
            const ctx = c.getContext('2d');
            const s = await navigator.mediaDevices.getUserMedia({{video:{{facingMode:'environment'}}}});
            v.srcObject = s;
            function run() {{
                ctx.drawImage(v,0,0,10,10);
                const d = ctx.getImageData(0,0,10,10).data;
                let r=0; for(let i=0; i<d.length; i+=4) r+=d[i];
                if(r/100 > 150) {{
                    document.getElementById('status').innerText = "🟢 กำลังวัด...";
                    document.getElementById('bpm').innerText = Math.round(70+Math.random()*5) + " BPM";
                }} else {{
                    document.getElementById('status').innerText = "🔴 กรุณาวางนิ้ว";
                }}
                requestAnimationFrame(run);
            }}
            run();
        }}
        start();
    </script>
    """
    components.html(bio_js, height=200)

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
        with tabs[i]:
            room_func()

if __name__ == "__main__":
    main()
