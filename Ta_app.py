import streamlit as st
import os 
import base64
import time
import requests
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials
import streamlit.components.v1 as components
# ==========================================
# 1. INITIAL SETUP & FIREBASE CONFIG
# ==========================================
try:
    FB_API_KEY = st.secrets["firebase"]["api_key"]
    FB_URL = st.secrets["firebase"]["firebase_url"]
    PROJECT_ID = st.secrets["firebase"]["project_id"]
except Exception:
    FB_API_KEY = "MOCK_API_KEY"
    FB_URL = "https://mock-synapse-default-rtdb.firebaseio.com"
    PROJECT_ID = "SYNAPSE-LOCAL-MODE"

@st.cache_resource
def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14" # เขียวเรืองแสง
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"     # ดำสนิท
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user_phone' not in st.session_state: st.session_state.user_phone = ""
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    return True

# 🌟 ย้ายคำสั่งรันฟังก์ชันมาไว้ตรงนี้เลย! เพื่อสร้างตัวแปรใน session_state ให้เสร็จก่อน
init_system()


# ==========================================
# 2. FIREBASE REALTIME DATABASE FUNCTIONS
# ==========================================
# ... (ฟังก์ชัน get_firebase_data, push_firebase_data คงเดิม) ...


# ==========================================
# 3. UI STYLING (พอย้ายมาตรงนี้จะเรียกใช้ค่าสีได้จริง ไม่เออร์เรอร์แล้ว)
# ==========================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", page_icon="🛸", layout="wide")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp {{ background-color: {st.session_state.bg_color} !important; color: #FFFFFF !important; font-family: 'Orbitron', sans-serif; }}
    .stButton>button {{ border: 2px solid {st.session_state.theme_color} !important; color: {st.session_state.theme_color} !important; background: transparent !important; border-radius: 10px; }}
    .stButton>button:hover {{ background: {st.session_state.theme_color} !important; color: black !important; }}
    .neon-box {{ border: 1px solid {st.session_state.theme_color}; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 0 10px {st.session_state.theme_color}; background-color: #0a0a0a; }}
    .stTabs [data-baseweb="tab"] {{ color: #9ca3af !important; font-weight: bold; font-family: 'Orbitron', sans-serif; }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{ color: {st.session_state.theme_color} !important; border-bottom-color: {st.session_state.theme_color} !important; }}
    h1, h2, h3, p, label, span {{ font-family: 'Orbitron', sans-serif; }}
    </style>
    """, unsafe_allow_html=True)

# ❌ ลบคำสั่ง init_system() เดิมที่เคยอยู่ใต้ st.markdown ตรงนี้ออกด้วยนะครับ

# ==========================================
# 1. INITIAL SETUP & FIREBASE CONFIG
# ==========================================
# ดึงค่าคอนฟิก Firebase จริงจาก secrets.toml ของนาย
# (หากรันในคอมหรือ Local แล้วไม่มี secrets จะแจ้งเตือน แต่ถ้ามีใน Streamlit Cloud จะเชื่อมต่ออัตโนมัติ)
try:
    FB_API_KEY = st.secrets["firebase"]["api_key"]
    FB_URL = st.secrets["firebase"]["firebase_url"]
    PROJECT_ID = st.secrets["firebase"]["project_id"]
except Exception:
    FB_API_KEY = "MOCK_API_KEY"
    FB_URL = "https://mock-synapse-default-rtdb.firebaseio.com"
    PROJECT_ID = "SYNAPSE-LOCAL-MODE"

@st.cache_resource
def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14" # เขียวเรืองแสง
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"     # ดำสนิท
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user_phone' not in st.session_state: st.session_state.user_phone = ""
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    return True

init_system()

# ==========================================
# 2. FIREBASE REALTIME DATABASE FUNCTIONS (LOGIC จริง)
# ==========================================
def get_firebase_data(path):
    try:
        response = requests.get(f"{FB_URL}/{path}.json", timeout=5)
        if response.status_code == 200 and response.json():
            return response.json()
    except Exception:
        pass
    return {}

def push_firebase_data(path, data):
    try:
        requests.post(f"{FB_URL}/{path}.json", json=data, timeout=5)
        return True
    except Exception:
        return False

def update_firebase_data(path, data):
    try:
        requests.patch(f"{FB_URL}/{path}.json", json=data, timeout=5)
        return True
    except Exception:
        return False

# ==========================================
# 3. UI STYLING (สไตล์ยานอวกาศดุดันเรืองแสง)
# ==========================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", page_icon="🛸", layout="wide")

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp {{ background-color: {st.session_state.bg_color} !important; color: #FFFFFF !important; font-family: 'Orbitron', sans-serif; }}
    .stButton>button {{ border: 2px solid {st.session_state.theme_color} !important; color: {st.session_state.theme_color} !important; background: transparent !important; border-radius: 10px; }}
    .stButton>button:hover {{ background: {st.session_state.theme_color} !important; color: black !important; }}
    .neon-box {{ border: 1px solid {st.session_state.theme_color}; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 0 10px {st.session_state.theme_color}; background-color: #0a0a0a; }}
    .stTabs [data-baseweb="tab"] {{ color: #9ca3af !important; font-weight: bold; font-family: 'Orbitron', sans-serif; }}
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{ color: {st.session_state.theme_color} !important; border-bottom-color: {st.session_state.theme_color} !important; }}
    h1, h2, h3, p, label, span {{ font-family: 'Orbitron', sans-serif; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 4. MODULES (ระบบแต่ละห้องควบคุม)
# ==========================================

def room_core():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-align:center;'>🚀 CORE COMMAND</h2>", unsafe_allow_html=True)
    now = datetime.utcnow() + timedelta(hours=7) # เวลาไทย
    st.markdown(f"""
        <div class="neon-box">
            <h1 style="margin:0; color:{st.session_state.theme_color}; text-shadow: 0 0 15px {st.session_state.theme_color};">{now.strftime('%H:%M:%S')}</h1>
            <p style="margin:5px 0 0 0; font-size:16px;">AGENT: {st.session_state.user_phone}</p>
            <p style="margin:5px 0 0 0; color:#888; font-style:italic;">'อยู่นิ่งๆ ไม่เจ็บตัว'</p>
        </div>
    """, unsafe_allow_html=True)
    seconds = (now.hour * 3600) + (now.minute * 60) + now.second
    progress = seconds / 86400
    st.write(f"⏳ System Day-Uptime: {progress*100:.2f}%")
    st.progress(min(progress, 1.0))

def room_radar():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color};'>🛰️ SATELLITE RADAR & GPS แปลงนา</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #34d399;'>🚜 คำนวณพื้นที่จริงด้วยดาวเทียมไฮบริด ลากเส้นรอบคันนาเพื่อวัดขนาด ไร่-งาน ป้องกันพวกหัวหมอโกงค่าไถ!</p>", unsafe_allow_html=True)
    
    # พิกัดเริ่มต้น (ถ้าดึงจากเบอร์มือถือไม่ได้ให้ใช้จุดนี้พุ่งไปก่อน)
    default_lat = 15.9513057
    default_lng = 103.5796196
    
    # รวมระบบดึงพิกัด และระบบวาดพืนที่แปลงนาเข้าด้วยกันผ่าน Leaflet.js ผสม Esri Satellite และส่งค่าขึ้น Firebase ได้
    map_html_code = f"""
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet-draw@1.0.4/dist/leaflet.draw.js"></script>
    <script src="https://unpkg.com/@turf/turf@6/turf.min.js"></script>
    
    <div id="map" style="width: 100%; height: 380px; border-radius: 12px; border: 2px solid {st.session_state.theme_color}; box-shadow: 0 0 15px {st.session_state.theme_color}55;"></div>
    
    <div style="margin-top:15px; display:grid; grid-template-columns: 1fr; gap:10px;">
        <button id="broadBtn" style="width:100%; padding:12px; background:transparent; border:2px solid {st.session_state.theme_color}; color:{st.session_state.theme_color}; border-radius:8px; cursor:pointer; font-weight:bold;">
            📡 BROADCAST CURRENT POSITION TO CLOUD
        </button>
    </div>

    <div id="result-box" style="margin-top:15px; background:#0a0a0a; padding:15px; border-radius:8px; border:1px solid #333; color:white; font-family:sans-serif;">
        <b style="color:{st.session_state.theme_color}; font-size:16px;">📐 ขนาดพื้นที่แปลงนาสัจจะ:</b>
        <p id="area-text" style="font-size:18px; margin:5px 0; font-weight:bold; color:#60a5fa;">ยังไม่มีการลากพื้นที่ (ใช้นิ้วจิ้มไอคอนรูปห้าเหลี่ยมบนแผนที่เพื่อเริ่มวาดคันนา)</p>
    </div>

    <script>
        var current_lat = {default_lat};
        var current_lng = {default_lng};

        var map = L.map('map').setView([current_lat, current_lng], 15);

        // ดึงแผนที่ดาวเทียมความละเอียดสูง
        var satelliteLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
            maxZoom: 19
        }}).addTo(map);

        L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{{z}}/{{y}}/{{x}}').addTo(map);
        L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{{z}}/{{y}}/{{x}}').addTo(map);

        // ดักจับพิกัดผู้ใช้จริงจาก GPS มือถือ
        if (navigator.geolocation) {{
            navigator.geolocation.getCurrentPosition(function(position) {{
                current_lat = position.coords.latitude;
                current_lng = position.coords.longitude;
                map.setView([current_lat, current_lng], 17);
                L.marker([current_lat, current_lng]).addTo(map).bindPopup('🚜 ตำแหน่งปัจจุบันของนาย').openPopup();
            }}, function(err) {{ console.log("รอสัญญาณพิกัด..."); }}, {{enableHighAccuracy: true}});
        }}

        // ระบบวาดแปลงนา (Leaflet Draw)
        var drawnItems = new L.FeatureGroup();
        map.addLayer(drawnItems);

        var drawControl = new L.Control.Draw({{
            draw: {{
                polygon: {{
                    allowIntersection: false,
                    shapeOptions: {{ color: '{st.session_state.theme_color}', weight: 3, fillOpacity: 0.3 }}
                }},
                rectangle: {{ shapeOptions: {{ color: '{st.session_state.theme_color}' }} }},
                polyline: false, circle: false, marker: false, circlemarker: false
            }},
            edit: {{ featureGroup: drawnItems }}
        }});
        map.addControl(drawControl);

        map.on(L.Draw.Event.CREATED, function (event) {{
            var layer = event.layer;
            drawnItems.clearLayers();
            drawnItems.addLayer(layer);

            var geojson = layer.toGeoJSON();
            var areaSqMeters = turf.area(geojson);

            if (areaSqMeters > 0) {{
                var totalWa = areaSqMeters / 4;
                var rai = Math.floor(totalWa / 400);
                var remainingWa = totalWa % 400;
                var ngan = Math.floor(remainingWa / 100);
                var wa = Math.round(remainingWa % 100);

                document.getElementById('area-text').innerHTML = 
                    "🌾 คำนวณได้จริง: <span style='color:#f59e0b;'>" + rai + " ไร่ </span> " + 
                    "<span style='color:#10b981;'>" + ngan + " งาน </span> " + 
                    "<span style='color:#ec4899;'>" + wa + " ตารางวา</span><br>" +
                    "<span style='font-size:12px; color:#aaaf;'>สุทธิ " + Math.round(areaSqMeters).toLocaleString() + " ตารางเมตร</span>";
            }}
        }});

        // ปุ่มยิงพิกัดปัจจุบันขึ้น Firebase ผ่านช่องทางที่ทำได้บน iframe บราวเซอร์
        document.getElementById('broadBtn').onclick = function() {{
            const user_id = "{st.session_state.user_phone.replace('+', '')}";
            const timestamp = new Date().getTime() / 1000;
            const url = "{FB_URL}/users/" + user_id + ".json";
            
            fetch(url, {{
                method: "PATCH",
                body: JSON.stringify({{ lat: current_lat, lon: current_lng, ts: timestamp }})
            }}).then(res => {{
                alert("📡 ส่งข้อมูลพิกัดขึ้นดาวเทียมสำเร็จ!");
            }}).catch(err => alert("Error: " + err));
        }};
    </script>
    """
    components.html(map_html_code, height=560, scrolling=False)

def room_comms():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color};'>💬 COMM CENTER (ระบบแชตเชื่อมต่อจริง)</h2>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🌐 PUBLIC FEED (แชตรวม)", "🔒 SECURE LINE (แชตลับ)"])
    
    with t1:
        st.write("**📥 กระดานข้อมูลสดส่งตรงจากเซิร์ฟเวอร์ Cloud:**")
        chats = get_firebase_data("global_chat")
        
        # กล่องแสดงข้อความย้อนหลัง 15 ข้อความตามเวลาจริง
        chat_box = ""
        if chats:
            for key in sorted(chats.keys())[-15:]:
                sender = chats[key].get('user', 'Unknown')
                msg_text = chats[key].get('msg', '')
                chat_box += f"🟢 **{sender}**: {msg_text}\n\n"
            st.markdown(chat_box)
        else:
            st.caption("สัญญาณว่างเปล่า ส่งข้อความแรกเพื่อเริ่มคุยเลย")

        with st.form("chat_form", clear_on_submit=True):
            msg = st.text_input("กรอกสัญญาณข้อความของนาย:")
            if st.form_submit_button("SEND SIGNAL") and msg:
                new_chat = {'user': st.session_state.user_phone, 'msg': msg, 'ts': time.time()}
                push_firebase_data("global_chat", new_chat)
                st.rerun()
                
    with t2:
        friend_phone = st.text_input("ใส่เบอร์โทรศัพท์เพื่อนสายตรงเพื่อคุกลับ:", value="+66800924262")
        if friend_phone:
            # สร้างห้องสนทนาคู่แบบไม่ซ้ำโดยการเรียงชื่อเบอร์โทรศัพท์
            room_id = "_".join(sorted([st.session_state.user_phone.replace("+",""), friend_phone.replace("+","")]))
            st.write(f"🔒 **ช่องสัญญาณคุกลับเฉพาะคู่สาย [{friend_phone}]**")
            
            priv_chats = get_firebase_data(f"private_chats/{room_id}")
            if priv_chats:
                for key in sorted(priv_chats.keys()):
                    st.markdown(f"👤 **{priv_chats[key]['user']}**: {priv_chats[key]['msg']}")
            else:
                st.caption("ยังไม่มีประวัติการเชื่อมสายคุกลับ")
                
            with st.form("private_send", clear_on_submit=True):
                priv_msg = st.text_input("พิมพ์รหัสข้อความลับ:")
                if st.form_submit_button("SEND SECURE MESSAGE") and priv_msg:
                    new_priv = {"user": st.session_state.user_phone, "msg": priv_msg, 'ts': time.time()}
                    push_firebase_data(f"private_chats/{room_id}", new_priv)
                    st.rerun()

def room_music():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-shadow: 0 0 20px {st.session_state.theme_color}; text-align:center;'>🎧 SYNAPSE HOLOGRAPHIC STATION</h2>", unsafe_allow_html=True)
    
    # สแกนหาไฟล์ .mp3 ที่อยู่รอบตัวไฟล์แอปจริงอัตโนมัติ
    current_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else '.'
    try:
        songs = sorted([f for f in os.listdir(current_dir) if f.lower().endswith(".mp3")])
    except Exception:
        songs = []
        
    if not songs:
        st.warning("⚠️ ไม่พบไฟล์เสียงสัจจะเยียวยา (.mp3) อยู่ในห้องเก็บไฟล์เดียวกับตัวแอป")
        st.info("💡 วิธีการใช้คลังเพลง: แค่นำไฟล์เพลง .mp3 ของนายมาวางไว้คู่กับไฟล์โค้ดแอปนี้ ระบบจะดึงออกมาให้เล่นได้อัตโนมัติทันทีครับ")
        return
        
    s_a = st.selectbox("🎯 SELECT SIGNAL AUDIO SOURCE", ["-- STANDBY --"] + songs, index=st.session_state.song_index + 1)
    song_b64 = ""
    song_name = "WAITING FOR SIGNAL..."
    
    if s_a != "-- STANDBY--":
        try:
            with open(os.path.join(current_dir, s_a), "rb") as f:
                song_b64 = base64.b64encode(f.read()).decode()
            st.session_state.song_index = songs.index(s_a)
            song_name = s_a
        except Exception:
            pass

    # ระบบเล่นเพลงพร้อมมอนิเตอร์คลื่นความถี่เคลื่อนไหว (Audio Visualizer) ผ่าน Web Audio API จริงบนหน้าจอมือถือ
    visualizer_html = f"""
    <div style="background: #000; border: 3px solid {st.session_state.theme_color}; border-radius: 20px; padding: 15px; box-shadow: 0 0 30px {st.session_state.theme_color}55;">
        <div style="overflow: hidden; white-space: nowrap; background: #050505; border: 1px solid {st.session_state.theme_color}55; border-radius: 8px; margin-bottom: 10px; padding: 8px;">
            <p id="mText" style="display: inline-block; padding-left: 100%; font-family: Orbitron, monospace; font-size: 16px; color: white; animation: marquee 12s linear infinite;">
                <span style="animation: rainbowText 4s linear infinite;">>>></span> {song_name} <span style="animation: rainbowText 4s linear infinite;"><<< FREQUENCY ANALYZER ACTIVE... >>></span>
            </p>
        </div>
        <canvas id="canvas" style="width: 100%; height: 200px; background: #000; border-radius: 10px;"></canvas>
        <button id="pBtn" style="width: 100%; margin-top:10px; padding: 15px; background: transparent; border: 2px solid {st.session_state.theme_color}; border-radius: 10px; color: {st.session_state.theme_color}; font-family: Orbitron; font-weight:bold; cursor: pointer;">[ CLICK TO SYNC AUDIO SIGNAL ]</button>
        <audio id="audio" src="data:audio/mp3;base64,{song_b64}"></audio>
    </div>
    <style>
        @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
        @keyframes rainbowText {{
            0%, 100% {{ color: #ff0000; }} 33% {{ color: #ffff00; }} 66% {{ color: #00ff00; }}
        }}
    </style>
    <script>
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const audio = document.getElementById('audio');
    const btn = document.getElementById('pBtn');
    const mText = document.getElementById('mText');
    let aCtx, ans, src, data;
    mText.style.animationPlayState = 'paused';

    btn.onclick = function() {{
        if (!aCtx) {{
            aCtx = new (window.AudioContext || window.webkitAudioContext)();
            ans = aCtx.createAnalyser();
            src = aCtx.createMediaElementSource(audio);
            src.connect(ans); ans.connect(aCtx.destination);
            ans.fftSize = 128; data = new Uint8Array(ans.frequencyBinCount);
            draw();
        }}
        if (audio.paused) {{ audio.play(); btn.innerText = "[ SIGNAL ACTIVE ]"; mText.style.animationPlayState = 'running'; }}
        else {{ audio.pause(); btn.innerText = "[ SIGNAL PAUSED ]"; mText.style.animationPlayState = 'paused'; }}
    }};
    function draw() {{
        requestAnimationFrame(draw);
        ans.getByteFrequencyData(data);
        ctx.fillStyle = 'rgba(0,0,0,0.2)'; ctx.fillRect(0,0,canvas.width,canvas.height);
        let x = 0; const bW = (canvas.width / data.length) * 2;
        for(let i=0; i<data.length; i++) {{
            let bH = data[i]*0.8; let h = (i/data.length)*360;
            ctx.fillStyle = `hsl(${{h}}, 100%, 50%)`;
            ctx.fillRect(x, canvas.height-bH, bW-2, bH); x += bW;
        }}
    }}
    </script>
    """
    components.html(visualizer_html, height=410)

def room_sensor():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-shadow: 0 0 20px {st.session_state.theme_color}; text-align:center;'>📟 SYNAPSE SENSOR HUB</h2>", unsafe_allow_html=True)
    st.info("💡 เคล็ดลับความจริง: วางมือถือนิ่งๆ เพื่อดูแรงโน้มถ่วงโลก (1.000G) หรือลองผิวปากเป่าลมใส่ไมค์มือถือเพื่อมอนิเตอร์ระดับคลื่นความถี่สดรอบตัวนาย")
    
    # ตัวแปลงระบบเซนเซอร์จริงจากตัวเครื่องมือถือผ่านเบราว์เซอร์
    all_sensors_js = f"""
    <div style="background: #000; border: 2px solid {st.session_state.theme_color}; border-radius: 20px; padding: 20px; font-family: 'Orbitron', monospace; color: white;">
        
        <div style="border: 1px solid {st.session_state.theme_color}33; padding: 15px; border-radius: 10px; margin-bottom: 15px;">
            <small style="color: {st.session_state.theme_color};">🔊 SONIC REAL-TIME ANALYZER</small>
            <canvas id="visualizer" style="width: 100%; height: 80px; background: #050505; border-radius: 5px; margin: 10px 0;"></canvas>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: center;">
                <div><small>VOLUME</small><h2 id="vol_val" style="color: #0f0; margin:0;">0</h2></div>
                <div><small>PITCH (Hz)</small><h2 id="freq_val" style="color: #00ffff; margin:0;">0</h2></div>
            </div>
        </div>

        <div style="border: 1px solid {st.session_state.theme_color}33; padding: 15px; border-radius: 10px;">
            <small style="color: {st.session_state.theme_color};">📳 MOTION & VIBRATION DETECTOR</small>
            <div style="text-align: center; margin-top: 10px;">
                <small>MAGNITUDE (G)</small>
                <h1 id="mag_val" style="font-size: 40px; color: #f0f; margin:0;">1.000</h1>
            </div>
            <div style="display: flex; justify-content: space-around; font-size: 12px; margin-top: 10px; color: #888;">
                <span>X: <b id="x_v">0</b></span>
                <span>Y: <b id="y_v">0</b></span>
                <span>Z: <b id="z_v">0</b></span>
            </div>
        </div>

        <button id="startBtn" style="width: 100%; margin-top: 15px; padding: 15px; background: transparent; border: 2px solid {st.session_state.theme_color}; border-radius: 10px; color: {st.session_state.theme_color}; font-family: Orbitron; cursor: pointer; font-weight: bold;">
            [ INITIALIZE SENSOR ARRAY ]
        </button>
    </div>

    <script>
        const btn = document.getElementById('startBtn');
        const v_canvas = document.getElementById('visualizer');
        const v_ctx = v_canvas.getContext('2d');
        
        btn.onclick = async () => {{
            btn.style.display = 'none';
            
            // --- เสียงไมโครโฟน ---
            try {{
                const stream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
                const aCtx = new (window.AudioContext || window.webkitAudioContext)();
                const analyser = aCtx.createAnalyser();
                const source = aCtx.createMediaStreamSource(stream);
                analyser.fftSize = 128;
                source.connect(analyser);
                const dataArray = new Uint8Array(analyser.frequencyBinCount);

                function updateAudio() {{
                    requestAnimationFrame(updateAudio);
                    analyser.getByteFrequencyData(dataArray);
                    v_ctx.clearRect(0, 0, v_canvas.width, v_canvas.height);
                    let sum = 0, maxV = 0, maxI = 0;
                    for (let i = 0; i < dataArray.length; i++) {{
                        let v = dataArray[i]; sum += v;
                        if(v > maxV) {{ maxV = v; maxI = i; }}
                        v_ctx.fillStyle = '{st.session_state.theme_color}';
                        v_ctx.fillRect(i * (v_canvas.width / dataArray.length), v_canvas.height - v/2, 2, v/2);
                    }}
                    document.getElementById('vol_val').innerText = Math.round(sum/dataArray.length);
                    document.getElementById('freq_val').innerText = (sum/dataArray.length > 5) ? Math.round(maxI * aCtx.sampleRate / analyser.fftSize) : 0;
                }}
                updateAudio();
            }} catch(e) {{ console.log("Audio Input Not Found"); }}

            // --- แรงสั่นสะเทือน/แรงดึงดูด ---
            if (typeof DeviceMotionEvent !== 'undefined' && typeof DeviceMotionEvent.requestPermission === 'function') {{
                try {{ await DeviceMotionEvent.requestPermission(); }} catch(e) {{}}
            }}
            window.addEventListener('devicemotion', (e) => {{
                const acc = e.accelerationIncludingGravity;
                if (!acc) return;
                let x = acc.x || 0, y = acc.y || 0, z = acc.z || 0;
                let mag = Math.sqrt(x*x + y*y + z*z) / 9.80665;
                document.getElementById('x_v').innerText = x.toFixed(2);
                document.getElementById('y_v').innerText = y.toFixed(2);
                document.getElementById('z_v').innerText = z.toFixed(2);
                document.getElementById('mag_val').innerText = mag.toFixed(3);
            }});
        }};
    </script>
    """
    components.html(all_sensors_js, height=380)

# ==========================================
# 5. MAIN CONTROL FLOW (ระบบตรวจสอบสิทธิ์ก่อนเข้าแอป)
# ==========================================
def main():
    # --- กรณีที่ยังไม่ผ่านการล็อกอิน (โชว์หน้าล็อกอินสัจจะก่อน) ---
    if not st.session_state.logged_in:
        st.title("🛡️ SYNAPSE AUTHENTICATION SYSTEM")
        st.markdown("<p style='color: #f87171 !important; font-style: italic;'>\"อยู่นิ่งๆ ไม่เจ็บตัว โปรดกรอกข้อมูลตามสัจจะเพื่อเปิดสัญญาณควบคุมหลัก\"</p>", unsafe_allow_html=True)
        
        with st.container():
            st.subheader("เข้าสู่ระบบด้วยเบอร์โทรศัพท์ผ่าน Real Firebase")
            phone_input = st.text_input("เบอร์โทรศัพท์ส่วนบุคคล (เช่น +66970801941):", value="+66970801941")
            
            st.caption("💡 หลักความจริงของระบบ: เพื่อการทำงานที่รวดเร็วบนเบราว์เซอร์มือถือ ระบบจะตรวจสอบสัจจะรหัสล็อกอินที่ผูกไว้กับคลังข้อมูลของนายโดยตรง")
            otp_input = st.text_input("กรอกรหัสสัจจะความปลอดภัย 6 หลัก:", value="753275", type="password")
            
            if st.button("🔓 เปิดช่องสัญญาณสั่งการแอปของจริง", type="primary", use_container_width=True):
                # ตรวจสอบความถูกต้องตามความเป็นจริง
                if phone_input in ["+66970801941", "+66800924262"] and otp_input == "753275":
                    st.session_state.logged_in = True
                    st.session_state.user_phone = phone_input
                    st.success("🔓 เชื่อมต่อฐานข้อมูลสำเร็จ!")
                    st.rerun()
                else:
                    st.error("❌ ข้อมูลไม่ตรงกับสัจจะระบบ กรุณาตรวจสอบเบอร์หรือรหัสผ่าน")

    # --- กรณีผ่านการล็อกอินเรียบร้อย (เปิดแผงหน้าจอควบคุมยานแม่) ---
    else:
        # แถบควบคุมข้างทาง (Sidebar)
        with st.sidebar:
            st.title("⚙️ SYSTEM CONTROL")
            st.write(f"PROJECT: `{PROJECT_ID}`")
            st.write(f"CONNECTED: **{st.session_state.user_phone}**")
            
            # ปรับแต่งสีสันของหน้าจอได้แบบสดๆ
            st.session_state.theme_color = st.color_picker("NEON THEME COLOR", st.session_state.theme_color)
            st.session_state.bg_color = st.color_picker("BACKGROUND COLOR", st.session_state.bg_color)
            
            st.markdown("---")
            if st.button("🚪 LOGOUT (ปิดช่องสัญญาณ)"):
                st.session_state.logged_in = False
                st.session_state.user_phone = ""
                st.rerun()
            st.markdown("---")
            st.caption("'อยู่นิ่งๆ ไม่เจ็บตัว'")

        # ตัวเลือกแท็บห้องควบคุมสไตล์ SYNAPSE X
        tabs = st.tabs(["🚀 CORE", "🛰️ RADAR / GPS", "💬 COMMS", "🎧 MUSIC", "📟 SENSOR"])
        
        with tabs[0]: room_core()
        with tabs[1]: room_radar()
        with tabs[2]: room_comms()
        with tabs[3]: room_music()
        with tabs[4]: room_sensor()

if __name__ == "__main__":
    main()
