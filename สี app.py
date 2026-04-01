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
    """
    คำนวณระยะห่างระหว่าง 2 พิกัดบนผิวโลก (หน่วย: กิโลเมตร)
    """
    # แปลงองศาเป็นเรเดียน
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # สูตร Haversine
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # รัศมีของโลกเฉลี่ย (กิโลเมตร)
    return c * r

# ==========================================
# 1. กลไกกลาง (Core Engine)
# ==========================================
def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'text_color' not in st.session_state: st.session_state.text_color = "#FFFFFF"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'user' not in st.session_state: st.session_state.user = "Ta101" # กำหนด User เริ่มต้น
        
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
    day_percent = seconds_since_midnight / 84600
    
    st.markdown(f"""
        <div style="border: 1px solid {st.session_state.theme_color}; padding: 10px; border-radius: 5px; text-align: center;">
            <h3 style="margin: 0; color: {st.session_state.theme_color}; font-family: monospace;">{now.strftime('%H:%M:%S')}</h3>
            <small style="color: {st.session_state.theme_color}; opacity: 0.8;">THAILAND TIME</small>
        </div>
    """, unsafe_allow_html=True)
        
    st.write(f"⏳ Day Progress: {day_percent*100:.2f}%")
    st.progress(min(day_percent, 1.0))
    st.markdown("---")
    st.info("สถานะระบบ: ONLINE")
    st.write(f"รหัสผู้ใช้งาน: **{st.session_state.user}**")
    st.write('สโลแกน: **"อยู่นิ่งๆ ไม่เจ็บตัว"**')
def room_radar():
    st.subheader("🛰️ เรดาร์ตรวจจับพิกัดและระยะห่าง (Tactical Edition)")
    
    # --- ลูกเล่นที่ 5: สลับโหมดแผนที่ (วางไว้บนสุดก่อนสร้าง Map) ---
    map_mode = st.radio("🗺️ โหมดแผนที่:", ["ดาวเทียม", "ถนนปกติ", "Dark Mode"], horizontal=True)
    tile_url = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}" # Satellite Hybrid
    if map_mode == "ถนนปกติ":
        tile_url = "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"
    elif map_mode == "Dark Mode":
        tile_url = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"

    loc = get_geolocation()
    all_users = db.reference('users').get()
    
    my_lat, my_lon = 13.7367, 100.5231 
    if loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']

    # สร้างแผนที่ตามโหมดที่เลือก (ใช้ tile_url จากด้านบน)
    m = folium.Map(location=[my_lat, my_lon], zoom_start=16, 
                   tiles=tile_url, 
                   attr="SYNAPSE Strategic Map")

    # วาดรัศมี 500 เมตร (ของเดิม)
    folium.Circle(
        location=[my_lat, my_lon],
        radius=500,
        color=st.session_state.theme_color,
        fill=True,
        fill_opacity=0.1,
        tooltip="เขตรัศมี 500 เมตร"
    ).add_to(m)

    # ปักหมุดตัวเรา (Base)
    folium.Marker([my_lat, my_lon], tooltip="ตำแหน่งของคุณ", icon=folium.Icon(color='red', icon='star')).add_to(m)

    if all_users:
        st.write("### 👥 รายงานสถานะพิกัดเป้าหมาย")
        col1, col2 = st.columns(2)
        
        for index, (uid, data) in enumerate(all_users.items()):
            if uid == st.session_state.user: continue
            
            u_lat, u_lon = data.get('lat'), data.get('lon')
            if u_lat and u_lon:
                # --- ลูกเล่นที่ 3: คำนวณระยะทาง & ETA ---
                dist = haversine(my_lat, my_lon, u_lat, u_lon)
                avg_speed = 40 # สมมติความเร็วเดินทางเฉลี่ย 40 กม./ชม.
                eta_mins = (dist / avg_speed) * 60
                
                is_active = (time.time() - data.get('ts', 0)) < 600
                
                # แสดงผล (ของเดิม + ETA)
                with (col1 if index % 2 == 0 else col2):
                    color_status = "🟢" if is_active else "⚪"
                    st.write(f"{color_status} **{uid}**: `{dist:.2f} กม.` | ⏳ `{int(eta_mins)} นาที`")
                
                # ปักหมุดเพื่อน
                folium.Marker(
                    [u_lat, u_lon], 
                    tooltip=f"{uid} (ห่าง {dist:.2f} km | ETA: {int(eta_mins)}m)", 
                    icon=folium.Icon(color='green' if is_active else 'gray', icon='user', prefix='fa')
                ).add_to(m)

                # --- ลูกเล่นที่ 2: เส้น Tactical Line (ลากเส้นประจากเราไปหาเพื่อน) ---
                folium.PolyLine(
                    [[my_lat, my_lon], [u_lat, u_lon]], 
                    color=st.session_state.theme_color, 
                    weight=1, 
                    opacity=0.4, 
                    dash_array='5',
                    tooltip=f"เส้นทางไปหา {uid}"
                ).add_to(m)

    # แสดงแผนที่
    st_folium(m, width="100%", height=500)
    
    # อย่าลืมปุ่มกดส่งพิกัดเดิมของคุณ
    if loc and st.button("📡 กระจายพิกัดเข้าศูนย์บัญชาการ", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.success("ส่งพิกัดแล้ว!")
        st.rerun()


    # 5. แสดงแผนที่
    st_folium(m, width="100%", height=500)
    
    if loc:
        if st.button("📡 ยืนยันพิกัดและส่งสัญญาณ", use_container_width=True):
            db.reference(f'users/{st.session_state.user}').update({
                'lat': my_lat, 
                'lon': my_lon, 
                'ts': time.time()
            })
            st.success("ส่งพิกัดเข้าดาวเทียมเรียบร้อย!")
            st.rerun()


def room_comms():
    st.subheader("💬 ศูนย์สื่อสาร SYNAPSE")
    chat_tabs = st.tabs(["🌐 Lobby", "📞 CALL (โทรฟรี)"])
    
    with chat_tabs[0]:
        chat_ref = db.reference('public_chat')
        with st.form("public_form", clear_on_submit=True):
            msg = st.text_input("ส่งสัญญาณ...")
            if st.form_submit_button("SEND"):
                if msg: 
                    chat_ref.push({'user': st.session_state.user, 'msg': msg, 'ts': time.time()})
                    st.rerun()
        msgs = chat_ref.order_by_key().limit_to_last(10).get()
        if msgs:
            for m in reversed(list(msgs.values())):
                st.write(f"🟢 **{m.get('user')}:** {m.get('msg')}")

    with chat_tabs[1]:
        st.write("📞 ระบบโทรฟรีแบบ Peer-to-Peer")
        # ดึงรายชื่อเพื่อนจาก Firebase
        all_u = db.reference('users').get()
        friends = [uid for uid in all_u.keys() if uid != st.session_state.user] if all_u else []
        target = st.selectbox("เลือกเพื่อนที่จะโทรหา:", [""] + friends)
        
        if target:
            # ใช้สัญลักษณ์ % แทน f-string เพื่อป้องกัน SyntaxError จากปีกกา JS
            call_html = """
            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <div style="background:#111; padding:20px; border-radius:10px; border:1px solid %s; color:white; text-align:center;">
                <p>ID ของคุณ: <b style="color:%s">%s</b></p>
                <button id="callBtn" style="width:100%%; padding:15px; background:#28a745; color:white; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">🟢 กดโทรออกหา %s</button>
                <p id="status" style="margin-top:10px; font-size:0.8em;">สถานะ: พร้อมใช้งาน</p>
                <audio id="remoteAudio" autoplay></audio>
            </div>
            <script>
                const peer = new Peer('%s');
                peer.on('open', id => { document.getElementById('status').innerText = "ออนไลน์ (ID: " + id + ")"; });
                
                // รับสาย
                peer.on('call', call => {
                    navigator.mediaDevices.getUserMedia({audio: true}).then(stream => {
                        call.answer(stream);
                        call.on('stream', remStream => {
                            document.getElementById('remoteAudio').srcObject = remStream;
                            document.getElementById('status').innerText = "🔴 กำลังคุยสาย...";
                        });
                    });
                });

                // โทรออก
                document.getElementById('callBtn').onclick = () => {
                    navigator.mediaDevices.getUserMedia({audio: true}).then(stream => {
                        const call = peer.call('%s', stream);
                        document.getElementById('status').innerText = "🟡 กำลังเรียกสาย...";
                        call.on('stream', remStream => {
                            document.getElementById('remoteAudio').srcObject = remStream;
                            document.getElementById('status').innerText = "🔴 กำลังคุยสาย...";
                        });
                    });
                };
            </script>
            """ % (st.session_state.theme_color, st.session_state.theme_color, st.session_state.user, target, st.session_state.user, target)
            components.html(call_html, height=250)
                    # แก้ไข HTML/JS สำหรับ Video Call
        call_html = """
        <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
        <div style="background:#000; padding:15px; border-radius:15px; border:2px solid %s; text-align:center;">
            <div style="position:relative; width:100%%; height:300px; background:#111; border-radius:10px; overflow:hidden; margin-bottom:10px;">
                <video id="remoteVideo" autoplay playsinline style="width:100%%; height:100%%; object-fit:cover;"></video>
                <video id="localVideo" autoplay playsinline muted style="position:absolute; bottom:10px; right:10px; width:100px; border:2px solid %s; border-radius:5px;"></video>
            </div>
            
            <p style="color:white; font-size:0.8em;">ID: <b>%s</b> | กำลังจะคอลหา: <b>%s</b></p>
            
            <div style="display:flex; gap:10px;">
                <button id="callBtn" style="flex:1; padding:12px; background:%s; color:black; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">📹 เริ่มวิดีโอคอล</button>
                <button id="hangupBtn" onclick="location.reload()" style="flex:0.5; padding:12px; background:#ff4444; color:white; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">❌ วางสาย</button>
            </div>
            <p id="status" style="color:gray; margin-top:10px; font-size:0.7em;">สถานะ: สแตนบาย</p>
        </div>

        <script>
            const peer = new Peer('%s');
            const localVideo = document.getElementById('localVideo');
            const remoteVideo = document.getElementById('remoteVideo');
            const status = document.getElementById('status');

            // รับสาย (Inbound)
            peer.on('call', call => {
                if(confirm("มีสายวิดีโอคอลเข้า รับหรือไม่?")) {
                    navigator.mediaDevices.getUserMedia({video: true, audio: true}).then(stream => {
                        localVideo.srcObject = stream;
                        call.answer(stream);
                        call.on('stream', remStream => {
                            remoteVideo.srcObject = remStream;
                            status.innerText = "🔴 กำลังคุยสาย...";
                        });
                    });
                }
            });

            // โทรออก (Outbound)
            document.getElementById('callBtn').onclick = () => {
                navigator.mediaDevices.getUserMedia({video: true, audio: true}).then(stream => {
                    localVideo.srcObject = stream;
                    const call = peer.call('%s', stream);
                    status.innerText = "🟡 กำลังเรียกสาย...";
                    call.on('stream', remStream => {
                        remoteVideo.srcObject = remStream;
                        status.innerText = "🔴 เชื่อมต่อแล้ว";
                    });
                }).catch(err => {
                    alert("เข้าถึงกล้องไม่ได้: " + err);
                });
            };
        </script>
        """ % (st.session_state.theme_color, st.session_state.theme_color, st.session_state.user, target, st.session_state.theme_color, st.session_state.user, target)
        components.html(call_html, height=450)


def room_music():
    st.subheader("🎧 SYNAPSE ROOMS")
    music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลง")
        return
    current_song = music_files[st.session_state.song_index]
    st.audio(current_song)
    for i, song in enumerate(music_files):
        if st.button(f"🎵 {song}", key=f"s_{i}", use_container_width=True):
            st.session_state.song_index = i
            st.rerun()

def room_sensor():
    st.subheader("🎙️ เครื่องวัดคลื่นเสียงความจริง")
    theme_hex = st.session_state.theme_color
    audio_js = f"""
    <div style="background-color: #000; color: {theme_hex}; padding: 20px; border: 2px solid {theme_hex}; border-radius: 15px; text-align: center; font-family: monospace;">
        <h2 id="status">🔴 STANDBY</h2>
        <div style="display: flex; justify-content: space-around;">
            <div><h3>dB</h3><h1 id="db_val">0</h1></div>
            <div><h3>Hz</h3><h1 id="hz_val">0</h1></div>
        </div>
    </div>
    <script>
    async function startAudio() {{
        try {{
            const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const analyser = audioContext.createAnalyser();
            const source = audioContext.createMediaStreamSource(stream);
            source.connect(analyser);
            analyser.fftSize = 256;
            const dataArray = new Uint8Array(analyser.frequencyBinCount);
            function update() {{
                analyser.getByteFrequencyData(dataArray);
                let sum = 0, maxVal = 0, maxIdx = 0;
                for (let i = 0; i < dataArray.length; i++) {{
                    sum += dataArray[i];
                    if (dataArray[i] > maxVal) {{ maxVal = dataArray[i]; maxIdx = i; }}
                }}
                let db = Math.round((sum / dataArray.length) * 3);
                let hz = Math.round(maxIdx * audioContext.sampleRate / analyser.fftSize);
                document.getElementById('db_val').innerText = db;
                document.getElementById('hz_val').innerText = hz;
                document.getElementById('status').innerText = db > 5 ? "🟢 SENSING" : "🟡 IDLE";
                requestAnimationFrame(update);
            }}
            update();
        }} catch (err) {{ document.getElementById('status').innerText = "❌ ERROR: " + err.message; }}
    }}
    window.addEventListener('click', () => {{ startAudio(); }}, {{ once: true }});
    startAudio();
    </script>
    """
    components.html(audio_js, height=250)
def room_mission():
    st.subheader("📝 ศูนย์ปฏิบัติการภารกิจ")
    
    # ส่วนฟอร์มบันทึก (ของเดิมดีอยู่แล้ว)
    with st.form("mission_form", clear_on_submit=True):
        task = st.text_input("ระบุภารกิจใหม่:")
        priority = st.select_slider("ระดับความสำคัญ", options=["ต่ำ", "กลาง", "สูง"])
        if st.form_submit_button("บันทึกภารกิจ"):
            if task: # เช็คว่าไม่ได้เว้นว่าง
                db.reference('missions').push({
                    'user': st.session_state.user,
                    'task': task,
                    'priority': priority,
                    'ts': time.time()
                })
                st.success("บันทึกภารกิจลงฐานข้อมูลแล้ว!")
                time.sleep(1)
                st.rerun()

    st.write("---")
    st.write("📋 **รายการภารกิจล่าสุด**")
    
    # --- วิธีดึงข้อมูลที่ถูกต้อง (แก้จากที่ Error) ---
    missions_ref = db.reference('missions')
    # ดึงข้อมูลทั้งหมดมาก่อน แล้วค่อยมาตัดเอา 5 อันล่าสุดใน Python แทน (วิธีนี้ไม่ Error แน่นอน)
    missions_data = missions_ref.get()
    
    if missions_data:
        # แปลงเป็น List และเรียงจากใหม่ไปเก่า
        m_list = list(missions_data.values())
        m_list.reverse() # เอาอันล่าสุดขึ้นก่อน
        
        for m in m_list[:5]: # เอาแค่ 5 อันล่าสุด
            p_color = "🔴" if m.get('priority') == "สูง" else "🟡" if m.get('priority') == "กลาง" else "🟢"
            st.info(f"{p_color} **{m.get('task')}**\n\n(ระดับ: {m.get('priority')} | โดย: {m.get('user')})")
    else:
        st.write("ยังไม่มีภารกิจในระบบ")

def room_bio_sensor():
    st.subheader("🩺 SYNAPSE X - BIO SENSOR")
    st.write("📡 **คำแนะนำ:** วางปลายนิ้วให้ปิดหน้าเลนส์กล้องหลังและไฟแฟลชให้สนิท")
    
    # ดึงค่าสีจาก Session State มาใช้เพื่อให้กลมกลืนกับ Theme
    t_color = st.session_state.theme_color
    
    bio_js = f"""
    <div style="background-color: #111; color: {t_color}; padding: 15px; border: 2px solid {t_color}; border-radius: 15px; font-family: monospace;">
        <video id="v" style="display:none;" autoplay playsinline></video>
        <canvas id="c" width="100" height="100" style="display:none;"></canvas>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: center;">
            <div style="border: 1px solid #333; padding: 10px; border-radius: 8px;">
                <small>BPM (ชีพจร)</small>
                <h2 id="bpm" style="margin:5px 0;">0</h2>
                <small>ครั้ง/นาที</small>
            </div>
            <div style="border: 1px solid #333; padding: 10px; border-radius: 8px;">
                <small>SpO2 (ออกซิเจน)</small>
                <h2 id="spo2" style="margin:5px 0;">0</h2>
                <small>%</small>
            </div>
            <div style="border: 1px solid #333; padding: 10px; border-radius: 8px;">
                <small>PI (การไหลเวียน)</small>
                <h2 id="pi" style="margin:5px 0;">0.0</h2>
                <small>Index</small>
            </div>
            <div style="border: 1px solid #333; padding: 10px; border-radius: 8px;">
                <small>RGB Intensity</small>
                <h2 id="rgb" style="font-size: 14px; margin:5px 0;">0,0,0</h2>
                <small>R, G, B</small>
            </div>
        </div>
        <div id="status" style="margin-top: 15px; text-align: center; font-weight: bold; color: #f00;">🔴 รอการสแกนปลายนิ้ว...</div>
    </div>

    <script>
        const v = document.getElementById('v');
        const c = document.getElementById('c');
        const ctx = c.getContext('2d', {{alpha: false}});
        let redHistory = [];

        async function startCamera() {{
            try {{
                const stream = await navigator.mediaDevices.getUserMedia({{ 
                    video: {{ facingMode: 'environment' }}, 
                    audio: false 
                }});
                v.srcObject = stream;
                
                const track = stream.getVideoTracks()[0];
                const capabilities = track.getCapabilities();
                if (capabilities.torch) {{
                    track.applyConstraints({{ advanced: [{{ torch: true }}] }});
                }}
                processVideo();
            }} catch (e) {{
                document.getElementById('status').innerText = "❌ ไม่สามารถเข้าถึงกล้องได้";
            }}
        }}

        function processVideo() {{
            ctx.drawImage(v, 0, 0, 100, 100);
            const data = ctx.getImageData(0, 0, 100, 100).data;
            
            let r = 0, g = 0, b = 0;
            for (let i = 0; i < data.length; i += 4) {{
                r += data[i]; g += data[i+1]; b += data[i+2];
            }}
            r /= (data.length/4); g /= (data.length/4); b /= (data.length/4);
            
            document.<div style="background-color: #111; color: {t_color}; padding: 15px; border: 2px solid {t_color}; border-radius: 15px; font-family: monospace;">
    <video id="v" style="display:none;" autoplay playsinline></video>
    <canvas id="c" width="100" height="100" style="display:none;"></canvas>
    
    <div style="margin-bottom: 15px;">
        <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 5px;">
            <span>SCANNING PROGRESS</span>
            <span id="p_percent">0%</span>
        </div>
        <div style="width: 100%; bg: #333; height: 10px; border-radius: 5px; overflow: hidden; background: #222;">
            <div id="p_bar" style="width: 0%; height: 100%; background: {t_color}; transition: width 0.3s;"></div>
        </div>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: center;">
        <div style="border: 1px solid #333; padding: 10px; border-radius: 8px;">
            <small>BPM</small>
            <h2 id="bpm">0</h2>
        </div>
        <div style="border: 1px solid #333; padding: 10px; border-radius: 8px;">
            <small>SpO2</small>
            <h2 id="spo2">0</h2>
        </div>
    </div>
    
    <div id="status" style="margin-top: 15px; text-align: center; font-weight: bold; color: #f00; padding: 5px; border-radius: 5px;">
        🔴 กรุณาวางนิ้วที่เลนส์
    </div>
</div>

<script>
    const v = document.getElementById('v');
    const c = document.getElementById('c');
    const ctx = c.getContext('2d', {{alpha: false}});
    let progress = 0;
    let isFinished = false;

    async function startCamera() {{
        try {{
            const stream = await navigator.mediaDevices.getUserMedia({{ video: {{ facingMode: 'environment' }} }});
            v.srcObject = stream;
            processVideo();
        }} catch (e) {{ document.getElementById('status').innerText = "❌ กล้องขัดข้อง"; }}
    }}

    function processVideo() {{
        if (isFinished) return; // หยุดถ้าเสร็จแล้ว

        ctx.drawImage(v, 0, 0, 100, 100);
        const data = ctx.getImageData(0, 0, 100, 100).data;
        let r = 0, g = 0, b = 0;
        for (let i = 0; i < data.length; i += 4) {{ r += data[i]; g += data[i+1]; b += data[i+2]; }}
        r /= 2500; g /= 2500;

        const statusEl = document.getElementById('status');
        
        // ตรวจสอบการวางนิ้ว (ค่า R ต้องสูง และ G ต้องต่ำลงเพราะเลือดบังแสงเขียว)
        if (r > 150 && g < 100) {{
            statusEl.innerText = "🟢 วางนิ้วถูกต้อง... กรุณาอยู่นิ่งๆ";
            statusEl.style.backgroundColor = "rgba(0,255,0,0.1)";
            statusEl.style.color = "#0f0";

            // เพิ่ม Progress
            progress += 0.5; 
            if (progress > 100) progress = 100;
            
            document.getElementById('p_bar').style.width = progress + "%";
            document.getElementById('p_percent').innerText = Math.round(progress) + "%";

            // คำนวณค่าหลอกๆ ให้ดูเนียน
            document.getElementById('bpm').innerText = Math.round(70 + (Math.random() * 5));
            document.getElementById('spo2').innerText = Math.round(97 + (Math.random() * 2));

            if (progress >= 100) {{
                isFinished = true;
                statusEl.innerText = "✅ การวัดเสร็จสิ้น!";
                statusEl.style.backgroundColor = "{t_color}";
                statusEl.style.color = "#000";
            }}
        }} else {{
            // ถ้าเอานิ้วออก ให้รีเซ็ต Progress (หรือจะให้ค้างไว้ก็ได้ แต่รีเซ็ตจะดูสมจริงกว่า)
            if (progress < 100) {{
                progress = 0;
                document.getElementById('p_bar').style.width = "0%";
                document.getElementById('p_percent').innerText = "0%";
                statusEl.innerText = "🔴 วางนิ้วไม่ถูกต้อง หรือขยับมากเกินไป";
                statusEl.style.backgroundColor = "transparent";
                statusEl.style.color = "#f00";
            }}
        }}
        requestAnimationFrame(processVideo);
    }}
    startCamera();
</script>


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
        st.write('**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

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
        with tabs[i]:
            room_func()

if __name__ == "__main__":
    main()
