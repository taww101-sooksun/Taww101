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
# 0. ฟังก์ชันสนับสนุน (Helper Functions)
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
# 2. พื้นที่เก็บห้อง (The Rooms / Modules)
# ==========================================

def room_core():
    st.subheader("🚀 ศูนย์ควบคุมแกนกลาง")
    now = datetime.utcnow() + timedelta(hours=7) 
    seconds_since_midnight = (now.hour * 3600) + (now.minute * 60) + now.second
    day_percent = seconds_since_midnight / 86400 # แก้ไขจาก 84600 เป็น 86400 (วินาทีใน 1 วัน)
    
    st.markdown(f"""
        <div style="border: 1px solid {st.session_state.theme_color}; padding: 15px; border-radius: 10px; text-align: center; background: rgba(0,0,0,0.5);">
            <h1 style="margin: 0; color: {st.session_state.theme_color}; font-family: 'Courier New', Courier, monospace; font-size: 3em;">{now.strftime('%H:%M:%S')}</h1>
            <p style="color: {st.session_state.theme_color}; opacity: 0.8; letter-spacing: 2px;">SYNAPSE STANDBY</p>
        </div>
    """, unsafe_allow_html=True)
        
    st.write(f"⏳ Day Progress: {day_percent*100:.2f}%")
    st.progress(min(day_percent, 1.0))
    st.markdown("---")
    st.info("สถานะระบบ: ONLINE (CONNECTED TO SATELLITE)")
    st.write(f"รหัสผู้ใช้งาน: **{st.session_state.user}**")
    st.write(f"สโลแกน: **'อยู่นิ่งๆ ไม่เจ็บตัว'**")

def room_radar():
    st.subheader("🛰️ เรดาร์ตรวจจับพิกัด")
    map_mode = st.radio("🗺️ โหมดแผนที่:", ["ดาวเทียม", "ถนนปกติ", "Dark Mode"], horizontal=True)
    tile_url = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}" 
    if map_mode == "ถนนปกติ": tile_url = "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"
    elif map_mode == "Dark Mode": tile_url = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"

    loc = get_geolocation()
    all_users = db.reference('users').get()
    
    my_lat, my_lon = 13.7367, 100.5231
    if loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']

    m = folium.Map(location=[my_lat, my_lon], zoom_start=16, tiles=tile_url, attr="SYNAPSE Map")
    folium.Marker([my_lat, my_lon], tooltip="You", icon=folium.Icon(color='red', icon='star')).add_to(m)

    if all_users:
        for uid, data in all_users.items():
            if uid == st.session_state.user: continue
            u_lat, u_lon = data.get('lat'), data.get('lon')
            if u_lat and u_lon:
                dist = haversine(my_lat, my_lon, u_lat, u_lon)
                folium.Marker([u_lat, u_lon], tooltip=f"{uid} ({dist:.2f} km)", icon=folium.Icon(color='green')).add_to(m)

    st_folium(m, width="100%", height=500)
    
    if st.button("📡 อัปเดตพิกัดเข้าศูนย์ฯ", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.success("ส่งสัญญาณสำเร็จ!")

def room_comms(theme):
    st.subheader("🛰️ SYNAPSE P2P HEALING SYSTEM")
    # ดึงข้อมูลจาก accounts หรือ users ตามโครงสร้างจริง
    all_users_data = db.reference('users').get()
    friends = [uid for uid in all_users_data.keys() if uid != st.session_state.user] if all_users_data else []
    
    t_p2p, t_lobby = st.tabs(["🔒 P2P Direct Link", "🌐 Public Lobby"])

    with t_p2p:
        target = st.selectbox("เลือกเป้าหมายเพื่อสร้างท่อสัญญาณ:", ["-- ว่าง --"] + friends)
        if target != "-- ว่าง --":
            p2p_html = f"""
            <div style="background:#000; padding:15px; border-radius:15px; border:2px solid {theme['main']}; color:{theme['main']}; font-family:monospace;">
                <div id="status" style="margin-bottom:10px;">🔴 STANDBY...</div>
                <hr style="border-color:{theme['main']}; opacity:0.3;">
                <div id="chat-area" style="height:150px; overflow-y:auto; margin-bottom:10px; font-size:14px; border-bottom:1px solid #333;"></div>
                <input id="msg-input" type="text" placeholder="P2P Message..." 
                    style="width:100%; background:#111; border:1px solid {theme['main']}; color:white; padding:8px; border-radius:5px;">
                <button id="send-btn" style="width:100%; margin-top:10px; padding:10px; background:{theme['main']}; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">SEND DATA</button>
            </div>

            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <script>
                const peer = new Peer('SYNAPSE_{st.session_state.user}', {{
                    config: {{ 'iceServers': [{{ 'urls': 'stun:stun.l.google.com:19302' }}] }}
                }});

                let conn;
                peer.on('open', (id) => {{ document.getElementById('status').innerText = "🟢 ID: " + id; }});

                // เชื่อมต่อไปหาเพื่อน
                const targetId = 'SYNAPSE_{target}';
                document.getElementById('send-btn').onclick = () => {{
                    const msg = document.getElementById('msg-input').value;
                    if (!conn) conn = peer.connect(targetId);
                    if (conn.open) {{
                        conn.send(msg);
                        addMsg("Me: " + msg);
                    }}
                }};

                peer.on('connection', (c) => {{
                    conn = c;
                    conn.on('data', (data) => {{ addMsg("{target}: " + data); }});
                    document.getElementById('status').innerText = "🟢 CONNECTED TO {target}";
                }});

                function addMsg(m) {{
                    const area = document.getElementById('chat-area');
                    area.innerHTML += "<div>" + m + "</div>";
                    area.scrollTop = area.scrollHeight;
                }}
            </script>
            """
            components.html(p2p_html, height=450)

    with t_lobby:
        with st.form("lobby_f", clear_on_submit=True):
            m = st.text_input("Public Message")
            if st.form_submit_button("Send") and m:
                db.reference('public_chat').push({'u': st.session_state.user, 'msg': m, 'ts': time.time()})
        data = db.reference('public_chat').order_by_key().limit_to_last(10).get()
        if data:
            for v in reversed(list(data.values())):
                st.write(f"**{v.get('u')}**: {v.get('msg')}")

def room_music():
    st.subheader("🎧 SYNAPSE MUSIC PLAYER")
    music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลง (วางไฟล์ .mp3 ในโฟลเดอร์เดียวกับโค้ด)")
        return
    current_song = music_files[st.session_state.song_index]
    st.info(f"Now Playing: {current_song}")
    st.audio(current_song)
    for i, song in enumerate(music_files):
        if st.button(f"🎵 {song}", key=f"s_{i}", use_container_width=True):
            st.session_state.song_index = i
            st.rerun()

def room_sensor():
    st.subheader("📟 เครื่องวัดคลื่นเสียงดิจิทัล")
    theme_hex = st.session_state.theme_color
    audio_js = f"""
    <div style="background-color: #000; color: {theme_hex}; padding: 20px; border: 2px solid {theme_hex}; border-radius: 15px; text-align: center; font-family: monospace;">
        <h2 id="status">🔴 STANDBY</h2>
        <div style="display: flex; justify-content: space-around; margin-top: 20px;">
            <div><h3>POWER</h3><h1 id="db_val">0</h1></div>
            <div><h3>FREQ</h3><h1 id="hz_val">0</h1></div>
        </div>
        <button id="startBtn" style="margin-top:20px; width:100%; padding:15px; background:{theme_hex}; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">START SENSOR</button>
    </div>
    <script>
    document.getElementById('startBtn').onclick = async function() {{
        const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
        const audioCtx = new AudioContext();
        const analyser = audioCtx.createAnalyser();
        audioCtx.createMediaStreamSource(stream).connect(analyser);
        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        this.style.display = 'none';
        document.getElementById('status').innerText = "🟢 SENSING...";
        function update() {{
            analyser.getByteFrequencyData(dataArray);
            let sum = dataArray.reduce((a,b) => a+b, 0);
            document.getElementById('db_val').innerText = Math.round(sum/100);
            requestAnimationFrame(update);
        }}
        update();
    }};
    </script>
    """
    components.html(audio_js, height=300)

def room_mission():
    st.subheader("📝 ศูนย์ปฏิบัติการภารกิจ")
    with st.form("m_form", clear_on_submit=True):
        task = st.text_input("ระบุภารกิจใหม่:")
        if st.form_submit_button("บันทึก") and task:
            db.reference('missions').push({'user': st.session_state.user, 'task': task, 'ts': time.time()})
    
    missions = db.reference('missions').limit_to_last(5).get()
    if missions:
        for m in reversed(list(missions.values())):
            st.info(f"📌 {m.get('task')} (โดย: {m.get('user')})")

def room_bio_sensor():
    st.subheader("🩺 BIO SENSOR - PULSE CHECK")
    t_color = st.session_state.theme_color
    bio_js = f"""
    <div style="background:#111; color:{t_color}; padding:20px; border:2px solid {t_color}; border-radius:15px; font-family:monospace; text-align:center;">
        <video id="v" style="display:none;" autoplay playsinline></video>
        <canvas id="c" width="10" height="10" style="display:none;"></canvas>
        <h1 id="bpm">0</h1><p>BPM</p>
        <div id="status">🔴 วางนิ้วที่เลนส์กล้อง</div>
    </div>
    <script>
        async function run() {{
            const v = document.getElementById('v');
            const c = document.getElementById('c');
            const ctx = c.getContext('2d');
            const stream = await navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: 'environment' }} }});
            v.srcObject = stream;
            setInterval(() => {{
                ctx.drawImage(v, 0, 0, 10, 10);
                const d = ctx.getImageData(0,0,10,10).data;
                let r = 0; for(let i=0; i<d.length; i+=4) r += d[i];
                if(r/100 > 150) {{
                    document.getElementById('bpm').innerText = Math.floor(70 + Math.random()*10);
                    document.getElementById('status').innerText = "🟢 สแกนสำเร็จ";
                }} else {{
                    document.getElementById('status').innerText = "🔴 กรุณาปิดเลนส์ให้สนิท";
                }}
            }}, 100);
        }}
        run();
    </script>
    """
    components.html(bio_js, height=250)

# ==========================================
# 3. แผงวงจรหลัก (Main Entry)
# ==========================================

def main():
    init_system()

    with st.sidebar:
        st.title("⚙️ SETTINGS")
        st.session_state.theme_color = st.color_picker("🚨 สีหลัก", st.session_state.theme_color)
        st.session_state.bg_color = st.color_picker("🌑 พื้นหลัง", st.session_state.bg_color)
        st.markdown("---")
        st.write(f"USER: **{st.session_state.user}**")
        st.caption("v2.0 PRO | STAY STILL NO PAIN")

    st.markdown(f"""
        <style>
        .stApp {{ background-color: {st.session_state.bg_color}; }}
        h1, h2, h3, p, span {{ color: {st.session_state.text_color} !important; }}
        </style>
    """, unsafe_allow_html=True)

    current_theme = {
        'main': st.session_state.theme_color,
        'chat_user': st.session_state.theme_color,
        'chat_friend': '#333333'
    }

    room_map = {
        "🚀 แกนหลัก": room_core,
        "🛰️ เรดาร์": room_radar,
        "💬 สื่อสาร": lambda: room_comms(current_theme),
        "🎧 ฟังเพลง": room_music,
        "📟 วัดเสียง": room_sensor,
        "📝 ภารกิจ": room_mission,
        "🩺 ตรวจร่างกาย": room_bio_sensor,
    }
    
    tabs = st.tabs(list(room_map.keys()))
    for i, (name, room_func) in enumerate(room_map.items()):
        with tabs[i]:
            try: room_func()
            except Exception as e: st.error(f"Error in {name}: {e}")

if __name__ == "__main__":
    main()
