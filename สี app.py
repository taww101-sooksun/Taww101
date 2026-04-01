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

# --- ต้องมีฟังก์ชันนี้ก่อน ระบบถึงจะวัดระยะห่างได้ ---
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
    day_percent = seconds_since_midnight / 86400 # แก้ไขจาก 84600 เป็น 86400
    
    st.markdown(f"""
        <div style="border: 1px solid {st.session_state.theme_color}; padding: 10px; border-radius: 5px; text-align: center;">
            <h3 style="margin: 0; color: {st.session_state.theme_color}; font-family: monospace;">{now.strftime('%H:%M:%S')}</h3>
            <small style="color: {st.session_state.theme_color}; opacity: 0.8;">THAILAND TIME</small>
        </div>
    """, unsafe_allow_html=True)
    st.write(f"⏳ Day Progress: {day_percent*100:.2f}%")
    st.progress(min(day_percent, 1.0))
    st.info("สถานะระบบ: ONLINE")
    st.write('สโลแกน: **"อยู่นิ่งๆ ไม่เจ็บตัว"**')

def room_radar():
    st.subheader("🛰️ เรดาร์ (Tactical Edition)")
    map_mode = st.radio("🗺️ โหมดแผนที่:", ["ดาวเทียม", "ถนนปกติ", "Dark Mode"], horizontal=True)
    tile_url = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"
    if map_mode == "ถนนปกติ": tile_url = "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"
    elif map_mode == "Dark Mode": tile_url = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"

    loc = get_geolocation()
    all_users = db.reference('users').get()
    my_lat, my_lon = 13.7367, 100.5231 
    if loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']

    m = folium.Map(location=[my_lat, my_lon], zoom_start=16, tiles=tile_url, attr="SYNAPSE")
    folium.Circle([my_lat, my_lon], radius=500, color=st.session_state.theme_color, fill=True, fill_opacity=0.1).add_to(m)
    folium.Marker([my_lat, my_lon], tooltip="Base", icon=folium.Icon(color='red', icon='star')).add_to(m)

    if all_users:
        col1, col2 = st.columns(2)
        for index, (uid, data) in enumerate(all_users.items()):
            if uid == st.session_state.user: continue
            u_lat, u_lon = data.get('lat'), data.get('lon')
            if u_lat and u_lon:
                dist = haversine(my_lat, my_lon, u_lat, u_lon)
                eta = int((dist / 40) * 60)
                is_active = (time.time() - data.get('ts', 0)) < 600
                with (col1 if index % 2 == 0 else col2):
                    st.write(f"{'🟢' if is_active else '⚪'} **{uid}**: `{dist:.2f} กม.` | ⏳ `{eta} นาที`")
                folium.Marker([u_lat, u_lon], tooltip=f"{uid} ({dist:.2f}km)", icon=folium.Icon(color='green' if is_active else 'gray')).add_to(m)
                folium.PolyLine([[my_lat, my_lon], [u_lat, u_lon]], color=st.session_state.theme_color, weight=1, opacity=0.4, dash_array='5').add_to(m)

    st_folium(m, width="100%", height=500, key="radar_map")
    if loc and st.button("📡 กระจายพิกัดจริง", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.rerun()

def room_comms():
    st.subheader("💬 ศูนย์สื่อสาร")
    chat_tabs = st.tabs(["🌐 Lobby", "📞 CALL (Video)"])
    with chat_tabs[0]:
        chat_ref = db.reference('public_chat')
        with st.form("chat_form", clear_on_submit=True):
            msg = st.text_input("ส่งสัญญาณ...")
            if st.form_submit_button("SEND") and msg:
                chat_ref.push({'user': st.session_state.user, 'msg': msg, 'ts': time.time()})
                st.rerun()
        msgs = chat_ref.limit_to_last(10).get()
        if msgs:
            for m in reversed(list(msgs.values())): st.write(f"🟢 **{m.get('user')}:** {m.get('msg')}")

    with chat_tabs[1]:
        all_u = db.reference('users').get()
        friends = [uid for uid in all_u.keys() if uid != st.session_state.user] if all_u else []
        target = st.selectbox("เลือกเป้าหมาย:", [""] + friends)
        if target:
            call_html = f"""
            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <div style="background:#000; padding:15px; border-radius:15px; border:2px solid {st.session_state.theme_color}; text-align:center; color:white;">
                <video id="remoteVideo" autoplay playsinline style="width:100%; height:250px; background:#111; border-radius:10px;"></video>
                <video id="localVideo" autoplay playsinline muted style="width:80px; border:1px solid {st.session_state.theme_color}; position:absolute; bottom:80px; right:30px;"></video>
                <p>ID: {st.session_state.user} -> {target}</p>
                <button id="callBtn" style="width:100%; padding:10px; background:{st.session_state.theme_color}; color:black; border:none; border-radius:5px; font-weight:bold;">📹 START CALL</button>
            </div>
            <script>
                const peer = new Peer('{st.session_state.user}');
                peer.on('call', call => {{
                    navigator.mediaDevices.getUserMedia({{video:true, audio:true}}).then(s => {{
                        document.getElementById('localVideo').srcObject = s;
                        call.answer(s);
                        call.on('stream', rs => {{ document.getElementById('remoteVideo').srcObject = rs; }});
                    }});
                }});
                document.getElementById('callBtn').onclick = () => {{
                    navigator.mediaDevices.getUserMedia({{video:true, audio:true}}).then(s => {{
                        document.getElementById('localVideo').srcObject = s;
                        const call = peer.call('{target}', s);
                        call.on('stream', rs => {{ document.getElementById('remoteVideo').srcObject = rs; }});
                    }});
                }};
            </script>
            """
            components.html(call_html, height=400)

def room_music():
    st.subheader("🎧 SYNAPSE PLAYER")
    music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if music_files:
        st.audio(music_files[st.session_state.song_index])
        for i, song in enumerate(music_files):
            if st.button(f"🎵 {song}", key=f"ms_{i}", use_container_width=True):
                st.session_state.song_index = i
                st.rerun()

def room_sensor():
    st.subheader("🎙️ เครื่องวัดคลื่นเสียง")
    audio_js = f"""
    <div style="background:#000; color:{st.session_state.theme_color}; padding:20px; border:2px solid {st.session_state.theme_color}; border-radius:15px; text-align:center; font-family:monospace;">
        <h2 id="st">🟡 STANDBY</h2>
        <div style="display:flex; justify-content:space-around;">
            <div><h3>dB</h3><h1 id="db">0</h1></div>
            <div><h3>Hz</h3><h1 id="hz">0</h1></div>
        </div>
    </div>
    <script>
    async function startAudio() {{
        try {{
            const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
            const ctx = new AudioContext();
            const analyser = ctx.createAnalyser();
            const source = ctx.createMediaStreamSource(stream);
            source.connect(analyser);
            const data = new Uint8Array(analyser.frequencyBinCount);
            function update() {{
                analyser.getByteFrequencyData(data);
                let sum = data.reduce((a,b) => a+b, 0);
                let db = Math.round(sum/data.length * 3);
                document.getElementById('db').innerText = db;
                document.getElementById('st').innerText = db > 5 ? "🟢 SENSING" : "🟡 IDLE";
                requestAnimationFrame(update);
            }}
            update();
        }} catch(e) {{ document.getElementById('st').innerText = "❌ ERROR"; }}
    }}
    startAudio();
    </script>
    """
    components.html(audio_js, height=250)

def room_mission():
    st.subheader("📝 ศูนย์ภารกิจ")
    with st.form("m_form", clear_on_submit=True):
        task = st.text_input("ภารกิจ:")
        pri = st.select_slider("ระดับ:", options=["ต่ำ", "กลาง", "สูง"])
        if st.form_submit_button("บันทึก") and task:
            db.reference('missions').push({'user':st.session_state.user, 'task':task, 'priority':pri, 'ts':time.time()})
            st.rerun()
    m_data = db.reference('missions').get()
    if m_data:
        for m in reversed(list(m_data.values())[-5:]):
            st.info(f"📌 {m['task']} ({m['priority']})")

def room_bio_sensor():
    st.subheader("🩺 BIO SENSOR (PPG Tech)")
    t_color = st.session_state.theme_color
    bio_js = f"""
    <div style="background:#111; color:{t_color}; padding:15px; border:2px solid {t_color}; border-radius:15px; font-family:monospace;">
        <video id="v" style="display:none;" autoplay playsinline></video>
        <canvas id="c" width="100" height="100" style="display:none;"></canvas>
        <div style="margin-bottom:15px;">
            <div style="display:flex; justify-content:space-between; font-size:12px;"><span>PROGRESS</span><span id="p_p">0%</span></div>
            <div style="width:100%; height:10px; background:#222; border-radius:5px; overflow:hidden;">
                <div id="p_b" style="width:0%; height:100%; background:{t_color}; transition:width 0.3s;"></div>
            </div>
        </div>
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; text-align:center;">
            <div style="border:1px solid #333; padding:10px;">BPM<h2 id="bpm">0</h2></div>
            <div style="border:1px solid #333; padding:10px;">SpO2<h2 id="spo2">0</h2></div>
        </div>
        <div id="stat" style="margin-top:15px; text-align:center; color:#f00; font-weight:bold;">🔴 กรุณาวางนิ้วที่เลนส์</div>
    </div>
    <script>
    const v = document.getElementById('v'), c = document.getElementById('c'), ctx = c.getContext('2d');
    let progress = 0, isDone = false;
    async function init() {{
        try {{
            const s = await navigator.mediaDevices.getUserMedia({{video:{{facingMode:'environment'}}}});
            v.srcObject = s;
            const t = s.getVideoTracks()[0];
            if (t.getCapabilities().torch) t.applyConstraints({{advanced:[{{torch:true}}]}});
            loop();
        }} catch(e) {{ document.getElementById('stat').innerText = "❌ No Camera"; }}
    }}
    function loop() {{
        if (isDone) return;
        ctx.drawImage(v, 0, 0, 100, 100);
        const d = ctx.getImageData(0,0,100,100).data;
        let r=0, g=0;
        for(let i=0; i<d.length; i+=4) {{ r+=d[i]; g+=d[i+1]; }}
        r/=2500; g/=2500;
        const sEl = document.getElementById('stat');
        if (r > 150 && g < 100) {{
            sEl.innerText = "🟢 วางนิ้วถูกต้อง..."; sEl.style.color = "#0f0";
            progress += 0.5;
            if (progress >= 100) {{ progress = 100; isDone = true; sEl.innerText = "✅ วัดผลเสร็จสิ้น!"; }}
            document.getElementById('p_b').style.width = progress+"%";
            document.getElementById('p_p').innerText = Math.round(progress)+"%";
            document.getElementById('bpm').innerText = Math.round(72+(Math.random()*4));
            document.getElementById('spo2').innerText = Math.round(98+(Math.random()*2));
        }} else {{
            progress = 0; document.getElementById('p_b').style.width = "0%";
            sEl.innerText = "🔴 กรุณาวางนิ้วที่เลนส์"; sEl.style.color = "#f00";
        }}
        requestAnimationFrame(loop);
    }}
    init();
    </script>
    """
    components.html(bio_js, height=350)
    st.info("⚠️ ข้อมูลเพื่อความบันเทิงและการทดสอบเท่านั้น")

# ==========================================
# 3. แผงวงจรหลัก
# ==========================================
def main():
    init_system()
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {st.session_state.bg_color} !important; color: {st.session_state.text_color} !important; }}
        .stButton>button {{ border: 2px solid {st.session_state.theme_color} !important; color: {st.session_state.theme_color} !important; background: transparent !important; }}
        h1, h2, h3, p, span, div, label {{ color: {st.session_state.text_color} !important; }}
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.title("⚙️ SETTINGS")
        st.session_state.theme_color = st.color_picker("🚨 สีหลัก", st.session_state.theme_color)
        st.session_state.bg_color = st.color_picker("🌑 พื้นหลัง", st.session_state.bg_color)
        st.session_state.text_color = st.color_picker("✍️ ข้อความ", st.session_state.text_color)
        st.markdown("---")
        st.write('**"อยู่นิ่งๆ ไม่เจ็บตัว"**')

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
    for i, room_func in enumerate(room_map.values()):
        with tabs[i]: room_func()

if __name__ == "__main__":
    main()
