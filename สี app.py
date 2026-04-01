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
    """
    คำนวณระยะห่างระหว่าง 2 พิกัดบนผิวโลก (หน่วย: กิโลเมตร)
    """
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
    # ตั้งค่า Session State เริ่มต้น
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'text_color' not in st.session_state: st.session_state.text_color = "#FFFFFF"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'user' not in st.session_state: st.session_state.user = "Ta101"
        
    # เชื่อมต่อ Firebase
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
    """
    ห้องแกนกลาง: แสดงเวลาและสถานะระบบ
    """
    st.subheader("🚀 ศูนย์ควบคุมแกนกลาง")
    now = datetime.utcnow() + timedelta(hours=7) 
    seconds_since_midnight = (now.hour * 3600) + (now.minute * 60) + now.second
    day_percent = seconds_since_midnight / 84600
    
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
    """
    ห้องเรดาร์: ตรวจจับพิกัดและระยะห่างเพื่อนในทีม
    """
    st.subheader("🛰️ เรดาร์ตรวจจับพิกัดและระยะห่าง")
    
    map_mode = st.radio("🗺️ โหมดแผนที่:", ["ดาวเทียม", "ถนนปกติ", "Dark Mode"], horizontal=True)
    tile_url = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}" 
    if map_mode == "ถนนปกติ":
        tile_url = "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}"
    elif map_mode == "Dark Mode":
        tile_url = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"

    loc = get_geolocation()
    all_users = db.reference('users').get()
    
    my_lat, my_lon = 13.7367, 100.5231 # พิกัด Default (กทม.)
    if loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']

    m = folium.Map(location=[my_lat, my_lon], zoom_start=16, tiles=tile_url, attr="SYNAPSE Strategic Map")

    folium.Circle(
        location=[my_lat, my_lon],
        radius=500,
        color=st.session_state.theme_color,
        fill=True,
        fill_opacity=0.1,
        tooltip="เขตรัศมี 500 เมตร"
    ).add_to(m)

    folium.Marker(
        [my_lat, my_lon], 
        tooltip="ตำแหน่งของคุณ", 
        icon=folium.Icon(color='red', icon='star')
    ).add_to(m)

    if all_users:
        st.write("### 👥 รายงานสถานะพิกัดเป้าหมาย")
        col1, col2 = st.columns(2)
        
        for index, (uid, data) in enumerate(all_users.items()):
            if uid == st.session_state.user: continue
            
            u_lat, u_lon = data.get('lat'), data.get('lon')
            if u_lat and u_lon:
                dist = haversine(my_lat, my_lon, u_lat, u_lon)
                avg_speed = 40 
                eta_mins = (dist / avg_speed) * 60
                is_active = (time.time() - data.get('ts', 0)) < 600
                
                with (col1 if index % 2 == 0 else col2):
                    color_status = "🟢" if is_active else "⚪"
                    st.write(f"{color_status} **{uid}**: `{dist:.2f} กม.` | ⏳ `{int(eta_mins)} นาที`")
                
                folium.Marker(
                    [u_lat, u_lon], 
                    tooltip=f"{uid} (ห่าง {dist:.2f} km)", 
                    icon=folium.Icon(color='green' if is_active else 'gray', icon='user', prefix='fa')
                ).add_to(m)

                folium.PolyLine(
                    [[my_lat, my_lon], [u_lat, u_lon]], 
                    color=st.session_state.theme_color, 
                    weight=1, 
                    opacity=0.4, 
                    dash_array='5'
                ).add_to(m)

    st_folium(m, width="100%", height=500)
    
    if st.button("📡 กระจายพิกัดเข้าศูนย์บัญชาการ", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.success("ส่งพิกัดเข้าดาวเทียมเรียบร้อย!")
        st.rerun()


def room_comms(theme):
    st.subheader("💬 ศูนย์กลางการสื่อสาร")
    
    # ดึงรายชื่อเพื่อนจาก Firebase (กัน Error กรณีไม่มีข้อมูล)
    all_users = db.reference('accounts').get()
    friends = [uid for uid in all_users.keys() if uid != st.session_state.user] if all_users else []

    t_lobby, t_private, t_video = st.tabs(["🌐 Lobby", "🔐 แชตส่วนตัว", "📹 วิดีโอคอล"])

    # --- 1. แชทรวม (Lobby) ---
    with t_lobby:
        with st.form("lobby_form", clear_on_submit=True):
            m = st.text_input("พิมพ์ข้อความสาธารณะ...")
            if st.form_submit_button("📢 SEND") and m:
                db.reference('public_chat').push({
                    'u': st.session_state.user, 
                    'msg': m, 
                    'ts': time.time()
                })
                st.rerun()
        
        data = db.reference('public_chat').order_by_key().limit_to_last(15).get()
        if data:
            for v in reversed(list(data.values())):
                st.markdown(f"**{v.get('u','?')}**: {v.get('msg','')}")

    # --- 2. แชตส่วนตัว (Private Chat) ---
    with t_private:
        if not friends:
            st.warning("📡 ยังไม่มี AGENT ท่านอื่นออนไลน์ในขณะนี้")
        else:
            target = st.selectbox("เลือกเพื่อน:", ["-- เลือกชื่อ --"] + friends)
            if target != "-- เลือกชื่อ --":
                # สร้าง Room ID ที่เหมือนกันทั้งสองฝั่ง
                rid = "_".join(sorted([st.session_state.user, target]))
                
                with st.form("priv_form", clear_on_submit=True):
                    pm = st.text_input(f"ส่งข้อความถึง {target}")
                    if st.form_submit_button("🔒 SEND") and pm:
                        db.reference(f'private_rooms/{rid}').push({
                            'u': st.session_state.user, 
                            'msg': pm, 
                            'ts': time.time()
                        })
                        st.rerun()
                
                msgs = db.reference(f'private_rooms/{rid}').order_by_key().limit_to_last(10).get()
                if msgs:
                    for v in reversed(list(msgs.values())):
                        u_name = v.get('u', 'Unknown')
                        side = "right" if u_name == st.session_state.user else "left"
                        # ปรับสี Bubble ตามทีม
                        bg = theme['chat_user'] if u_name == st.session_state.user else theme['chat_friend']
                        text_c = "#000" if theme['theme_set'] == "Rainbow" else "#fff"
                        
                        st.markdown(f"""
                            <div style="text-align:{side}; margin-bottom:10px;">
                                <div style="display:inline-block; background:{bg}; padding:8px 15px; border-radius:15px; color:{text_c};">
                                    <small style="opacity:0.7;">{u_name}</small><br>{v.get('msg','')}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

    # --- 3. วิดีโอคอล (PeerJS - Optimized for Real-world) ---
    with t_video:
        if not friends:
            st.warning("📡 ไม่พบเป้าหมายสำหรับการเชื่อมต่อวิดีโอ")
        else:
            target_v = st.selectbox("เลือกเพื่อนที่จะคอล:", ["-- เลือกชื่อ --"] + friends, key="v_call_sel")
            if target_v != "-- เลือกชื่อ --":
                # ระบบ P2P พร้อม STUN Server ของ Google เพื่อเจาะ Firewall
                v_html = f"""
                <div id="v-box" style="background:#000; padding:15px; border-radius:15px; border:2px solid {theme['main']}; text-align:center; font-family:monospace;">
                    <div style="position:relative; width:100%; height:300px; background:#111; border-radius:10px; overflow:hidden;">
                        <video id="remote" autoplay playsinline style="width:100%; height:100%; object-fit:cover;"></video>
                        <video id="local" autoplay playsinline muted style="position:absolute; bottom:10px; right:10px; width:100px; border:2px solid {theme['main']}; border-radius:5px;"></video>
                    </div>
                    <div style="margin-top:15px; display:flex; gap:10px;">
                        <button id="call" style="flex:2; padding:12px; background:{theme['main']}; color:black; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">📹 ESTABLISH CONNECTION</button>
                        <button id="hangup" style="flex:1; padding:12px; background:#f44; color:white; border:none; border-radius:8px; font-weight:bold; cursor:pointer;">❌ DISCONNECT</button>
                    </div>
                    <p id="status-msg" style="color:{theme['main']}; font-size:12px; margin-top:10px;">📡 SYSTEM READY</p>
                </div>

                <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
                <script>
                    const peer = new Peer('{st.session_state.user}', {{
                        config: {{ 'iceServers': [{{ 'urls': 'stun:stun.l.google.com:19302' }}] }}
                    }});
                    
                    let currentCall;
                    const status = document.getElementById('status-msg');

                    peer.on('open', id => status.innerText = "ONLINE ID: " + id);
                    
                    // เมื่อรับสาย
                    peer.on('call', call => {{
                        status.innerText = "🛰️ INCOMING SIGNAL...";
                        if(confirm('รับสายจาก ' + call.peer + '?')) {{
                            navigator.mediaDevices.getUserMedia({{video: true, audio: true}}).then(stream => {{
                                document.getElementById('local').srcObject = stream;
                                call.answer(stream);
                                call.on('stream', remoteStream => {{
                                    document.getElementById('remote').srcObject = remoteStream;
                                    status.innerText = "🟢 CONNECTION ENCRYPTED";
                                }});
                                currentCall = call;
                            }}).catch(err => status.innerText = "❌ Camera Error");
                        }}
                    }});

                    // เมื่อกดโทรออก
                    document.getElementById('call').onclick = () => {{
                        status.innerText = "📡 ATTEMPTING CONNECTION...";
                        navigator.mediaDevices.getUserMedia({{video: true, audio: true}}).then(stream => {{
                            document.getElementById('local').srcObject = stream;
                            const call = peer.call('{target_v}', stream);
                            call.on('stream', remoteStream => {{
                                document.getElementById('remote').srcObject = remoteStream;
                                status.innerText = "🟢 ENCRYPTED CHANNEL OPEN";
                            }});
                            currentCall = call;
                        }}).catch(err => status.innerText = "❌ Access Denied");
                    }};

                    document.getElementById('hangup').onclick = () => {{
                        if(currentCall) currentCall.close();
                        location.reload();
                    }};
                </script>
                """
                components.html(v_html, height=480)



def room_music():
    """
    ห้องฟังเพลง: เล่นไฟล์ MP3 ในโฟลเดอร์
    """
    st.subheader("🎧 SYNAPSE MUSIC PLAYER")
    music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลงในระบบ")
        return
        
    current_song = music_files[st.session_state.song_index]
    st.info(f"กำลังเล่น: {current_song}")
    st.audio(current_song)
    
    st.write("---")
    for i, song in enumerate(music_files):
        if st.button(f"🎵 {song}", key=f"s_{i}", use_container_width=True):
            st.session_state.song_index = i
            st.rerun()


def room_sensor():
    """
    ห้องวัดเสียง: แสดงระดับความดังและคลื่นความถี่
    """
    st.subheader("📟 เครื่องวัดคลื่นเสียงดิจิทัล")
    theme_hex = st.session_state.theme_color
    audio_js = f"""
    <div style="background-color: #000; color: {theme_hex}; padding: 20px; border: 2px solid {theme_hex}; border-radius: 15px; text-align: center; font-family: monospace;">
        <h2 id="status">🔴 STANDBY</h2>
        <div style="display: flex; justify-content: space-around; margin-top: 20px;">
            <div><h3>POWER (dB)</h3><h1 id="db_val" style="font-size: 3em;">0</h1></div>
            <div><h3>FREQ (Hz)</h3><h1 id="hz_val" style="font-size: 3em;">0</h1></div>
        </div>
        <button id="startBtn" style="margin-top:20px; width:100%; padding:15px; background:{theme_hex}; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">START SENSOR</button>
    </div>
    <script>
    document.getElementById('startBtn').onclick = async function() {{
        try {{
            const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const analyser = audioContext.createAnalyser();
            const source = audioContext.createMediaStreamSource(stream);
            source.connect(analyser);
            analyser.fftSize = 256;
            const dataArray = new Uint8Array(analyser.frequencyBinCount);
            
            this.style.display = 'none';
            document.getElementById('status').innerText = "🟢 SENSING...";

            function update() {{
                analyser.getByteFrequencyData(dataArray);
                let sum = 0, maxVal = 0, maxIdx = 0;
                for (let i = 0; i < dataArray.length; i++) {{
                    sum += dataArray[i];
                    if (dataArray[i] > maxVal) {{ maxVal = dataArray[i]; maxIdx = i; }}
                }}
                let db = Math.round((sum / dataArray.length) * 2.5);
                let hz = Math.round(maxIdx * audioContext.sampleRate / analyser.fftSize);
                document.getElementById('db_val').innerText = db;
                document.getElementById('hz_val').innerText = hz;
                requestAnimationFrame(update);
            }}
            update();
        }} catch (err) {{ alert("Error: " + err.message); }}
    }};
    </script>
    """
    components.html(audio_js, height=300)


def room_mission():
    """
    ห้องปฏิบัติการภารกิจ: บันทึก To-do list ลง Firebase
    """
    st.subheader("📝 ศูนย์ปฏิบัติการภารกิจ")
    
    with st.form("mission_form", clear_on_submit=True):
        task = st.text_input("ระบุภารกิจใหม่:")
        priority = st.select_slider("ระดับความสำคัญ", options=["ต่ำ", "กลาง", "สูง"])
        if st.form_submit_button("บันทึกภารกิจ"):
            if task:
                db.reference('missions').push({
                    'user': st.session_state.user,
                    'task': task,
                    'priority': priority,
                    'ts': time.time()
                })
                st.success("บันทึกภารกิจเรียบร้อย!")
                st.rerun()

    st.write("---")
    st.write("📋 **รายการภารกิจล่าสุด**")
    missions_data = db.reference('missions').get()
    
    if missions_data:
        m_list = list(missions_data.values())
        m_list.reverse() 
        for m in m_list[:8]:
            p_color = "🔴" if m.get('priority') == "สูง" else "🟡" if m.get('priority') == "กลาง" else "🟢"
            st.info(f"{p_color} **{m.get('task')}** (โดย: {m.get('user')})")
    else:
        st.write("ยังไม่มีภารกิจในฐานข้อมูล")


def room_bio_sensor():
    """
    ห้องตรวจร่างกาย: วัดชีพจรผ่านกล้อง (จำลองการประมวลผลแสง RGB)
    """
    st.subheader("🩺 SYNAPSE X - BIO SENSOR")
    st.write("📡 **คำแนะนำ:** วางปลายนิ้วให้ปิดหน้าเลนส์กล้องหลังและไฟแฟลชให้สนิท")
    
    t_color = st.session_state.theme_color
    
    bio_js = f"""
    <div style="background-color: #111; color: {t_color}; padding: 20px; border: 2px solid {t_color}; border-radius: 15px; font-family: monospace;">
        <video id="v" style="display:none;" autoplay playsinline></video>
        <canvas id="c" width="100" height="100" style="display:none;"></canvas>
        
        <div style="margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 8px;">
                <span>SCANNING PROGRESS</span>
                <span id="p_percent">0%</span>
            </div>
            <div style="width: 100%; background: #222; height: 12px; border-radius: 6px; overflow: hidden;">
                <div id="p_bar" style="width: 0%; height: 100%; background: {t_color}; transition: width 0.3s;"></div>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; text-align: center;">
            <div style="border: 1px solid #333; padding: 15px; border-radius: 10px;">
                <small>BPM (HEART RATE)</small>
                <h1 id="bpm" style="margin:10px 0; font-size: 2.5em;">0</h1>
            </div>
            <div style="border: 1px solid #333; padding: 15px; border-radius: 10px;">
                <small>SpO2 (OXYGEN)</small>
                <h1 id="spo2" style="margin:10px 0; font-size: 2.5em;">0</h1>
            </div>
        </div>
        
        <div id="status" style="margin-top: 20px; text-align: center; font-weight: bold; color: #f00; padding: 10px; border-radius: 8px; background: rgba(255,0,0,0.1);">
            🔴 กรุณาวางนิ้วที่เลนส์กล้อง
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
            }} catch (e) {{ document.getElementById('status').innerText = "❌ เข้าถึงกล้องไม่ได้"; }}
        }}

        function processVideo() {{
            if (isFinished) return;

            ctx.drawImage(v, 0, 0, 100, 100);
            const data = ctx.getImageData(0, 0, 100, 100).data;
            let r = 0, g = 0;
            for (let i = 0; i < data.length; i += 4) {{ r += data[i]; g += data[i+1]; }}
            r /= 2500; g /= 2500;

            const statusEl = document.getElementById('status');
            
            if (r > 160 && g < 100) {{
                statusEl.innerText = "🟢 ตรวจพบสัญญาณ... กรุณาอยู่นิ่งๆ";
                statusEl.style.color = "#0f0";
                statusEl.style.background = "rgba(0,255,0,0.1)";

                progress += 0.4; 
                if (progress > 100) progress = 100;
                
                document.getElementById('p_bar').style.width = progress + "%";
                document.getElementById('p_percent').innerText = Math.round(progress) + "%";

                document.getElementById('bpm').innerText = Math.round(68 + (Math.random() * 8));
                document.getElementById('spo2').innerText = Math.round(96 + (Math.random() * 3));

                if (progress >= 100) {{
                    isFinished = true;
                    statusEl.innerText = "✅ การวัดเสร็จสิ้นสมบูรณ์!";
                    statusEl.style.background = "{t_color}";
                    statusEl.style.color = "#000";
                }}
            }} else {{
                if (progress < 100) {{
                    progress = 0;
                    document.getElementById('p_bar').style.width = "0%";
                    document.getElementById('p_percent').innerText = "0%";
                    statusEl.innerText = "🔴 กรุณาวางนิ้วให้ปิดหน้ากล้อง";
                    statusEl.style.color = "#f00";
                    statusEl.style.background = "rgba(255,0,0,0.1)";
                }}
            }}
            requestAnimationFrame(processVideo);
        }}
        startCamera();
    </script>
    """
    components.html(bio_js, height=380)

# ==========================================
# 3. แผงวงจรหลัก (Main Entry)
# ==========================================

def main():
    init_system()

    with st.sidebar:
        st.title("⚙️ SYNAPSE SETTINGS")
        theme_clr = st.session_state.get('theme_color', '#39FF14')
        bg_clr = st.session_state.get('bg_color', '#000000')
        txt_clr = st.session_state.get('text_color', '#FFFFFF')

        st.session_state.theme_color = st.color_picker("🚨 สีหลัก (Neon)", theme_clr)
        st.session_state.bg_color = st.color_picker("🌑 พื้นหลัง", bg_clr)
        st.session_state.text_color = st.color_picker("✍️ ข้อความ", txt_clr)
        
        st.markdown("---")
        st.write('**Personal Slogan:**')
        st.write(f'<h3 style="color:{st.session_state.theme_color}">"อยู่นิ่งๆ ไม่เจ็บตัว"</h3>', unsafe_allow_html=True)
        st.write("---")
        st.caption("SYNAPSE COMMAND CENTER v2.0")

    # ปรับแต่งธีมด้วย CSS
    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {st.session_state.bg_color};
        }}
        .stButton>button {{
            border-radius: 8px;
            border: 1px solid {st.session_state.theme_color};
            color: {st.session_state.text_color};
            background-color: transparent;
            transition: 0.3s;
        }}
        .stButton>button:hover {{
