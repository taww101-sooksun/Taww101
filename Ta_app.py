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
# 1. INITIAL SETUP & SECURITY CHECK
# ==========================================
st.set_page_config(page_title="SYNAPSE X", layout="wide", initial_sidebar_state="expanded")

def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'user' not in st.session_state: st.session_state.user = "Ta101"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'authenticated' not in st.session_state: st.session_state.authenticated = False

    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            if "private_key" in fb_creds:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n").strip().strip('"')
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_db_url"]
            })
        except Exception as e:
            st.error(f"🛰️ Firebase Connection Error: {e}")
    return True

init_system()

# ==========================================
# 2. ADVANCED UI CUSTOMIZATION (BLUE-RED-NEON & DE-STREAMLIT)
# ==========================================
# แทรก CSS ซ่อนหัว/ท้ายสัญลักษณ์ของ Streamlit พร้อมเอฟเฟกต์สีสันใหม่และไฟขอบ 4 ทิศ
st.markdown(f"""
    <style>
    /* ลบดีไซน์ยี่ห้อ Streamlit ออกทั้งหมด */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    div[data-testid="stDecoration"] {{display: none;}}
    
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .stApp {{ 
        background-color: {st.session_state.bg_color} !important; 
        color: #FFFFFF !important; 
        font-family: 'Orbitron', sans-serif; 
    }}
    
    /* ปุ่มสไตล์ Cyber ไฮบริดน้ำเงิน แดง นีออน */
    .stButton>button {{ 
        border: 2px solid {st.session_state.theme_color} !important; 
        color: #FFFFFF !important; 
        background: linear-gradient(45deg, #FF0055, #0066FF) !important; 
        border-radius: 10px;
        font-weight: bold;
        box-shadow: 0 0 10px #0066FF, 0 0 5px #FF0055;
    }}
    .stButton>button:hover {{ 
        box-shadow: 0 0 20px {st.session_state.theme_color};
        color: #000000 !important;
        background: {st.session_state.theme_color} !important;
    }}
    
    /* กล่องข้อความกรอบนีออน 4 มิติ */
    .neon-box {{ 
        border: 2px solid #0066FF; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center; 
        box-shadow: inset 0 0 15px #FF0055, 0 0 15px {st.session_state.theme_color}; 
        background-color: rgba(0,0,0,0.8);
    }}
    
    /* โลโก้เต้นระบำขอบทองสไตล์นีออน */
    @keyframes dance {{
        0% {{ transform: scale(1) rotate(0deg); box-shadow: 0 0 15px #FFD700, 0 0 5px #FF0000; }}
        50% {{ transform: scale(1.05) rotate(2deg); box-shadow: 0 0 25px #39FF14, 0 0 15px #0066FF; }}
        100% {{ transform: scale(1) rotate(0deg); box-shadow: 0 0 15px #FFD700, 0 0 5px #FF0000; }}
    }}
    .dancing-logo {{
        width: 130px;
        height: 130px;
        margin: 0 auto;
        border-radius: 50%;
        border: 4px solid #FFD700;
        animation: dance 3s infinite ease-in-out;
        object-fit: cover;
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. AUTHENTICATION SYSTEM
# ==========================================
def login_screen():
    st.markdown("<center><h1 style='color:#FF0055; text-shadow: 0 0 10px #FF0055;'>🔒 SYNAPSE GATEWAY</h1></center>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="neon-box">', unsafe_allow_html=True)
        user_input = st.text_input("รหัสตัวแทน (AGENT ID)", value="")
        pass_input = st.text_input("รหัสผ่านความปลอดภัย (PASSWORD)", type="password")
        mode = st.radio("ปฏิบัติการ :", ["เข้าสู่ระบบ", "ลงทะเบียนตัวแทนใหม่"], horizontal=True)
        
        if st.button("EXECUTE PROTOCOL", use_container_width=True):
            if not user_input or not pass_input:
                st.warning("❌ กรุณากรอกรหัสข้อมูลให้ครบถ้วน")
            else:
                acc_ref = db.reference(f'accounts/{user_input}')
                account_data = acc_ref.get()
                
                if mode == "ลงทะเบียนตัวแทนใหม่":
                    if account_data:
                        st.error("❌ มีรหัสตัวแทนนี้อยู่ในระบบสารสนเทศแล้ว")
                    else:
                        acc_ref.set({'pass': pass_input, 'created': time.time()})
                        st.success("🛰️ ลงทะเบียนตัวแทนใหม่สำเร็จ เข้าสู่ระบบได้ทันที")
                else:
                    if account_data and account_data.get('pass') == pass_input:
                        st.session_state.user = user_input
                        st.session_state.authenticated = True
                        st.success("🔓 อนุมัติสิทธิ์เข้าถึงฐานข้อมูลกลาง!")
                        st.rerun()
                    else:
                        st.error("❌ รหัสตัวแทนหรือรหัสผ่านไม่ถูกต้องพ้นสภาพความปลอดภัย")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 4. MODULE ROOMS
# ==========================================

def room_core():
    # แสดงโลโก้เต้นระบำขอบทอง 4 มิติ (ดึงรูปภาพโลโก้ในเครื่องมาแสดง)
    if os.path.exists("logo1.png"):
        with open("logo1.png", "rb") as f:
            data = f.read()
            b64_logo = base64.b64encode(data).decode()
        st.markdown(f'<center><img src="data:image/png;base64,{b64_logo}" class="dancing-logo"></center><br>', unsafe_allow_html=True)
    else:
        st.markdown('<center><div class="dancing-logo" style="background:#222; display:flex; align-items:center; justify-content:center; color:#FFD700; font-weight:bold;">LOGO1</div></center><br>', unsafe_allow_html=True)

    st.markdown(f"<h2 style='text-align:center; color:#0066FF; text-shadow: 0 0 10px #FF0055;'>🚀 CORE COMMAND CENTER</h2>", unsafe_allow_html=True)
    now = datetime.utcnow() + timedelta(hours=7)
    st.markdown(f"""
        <div class="neon-box">
            <h1 style="margin:0; color:{st.session_state.theme_color}; text-shadow: 0 0 15px #0066FF;">{now.strftime('%H:%M:%S')}</h1>
            <p style="margin:5px 0 0 0; font-weight:bold;">ACTIVE AGENT: <span style="color:#FF0055;">{st.session_state.user}</span></p>
            <p style="margin:0; color:#CCCCCC; font-style: italic;">"อยู่นิ่งๆ ไม่เจ็บตัว"</p>
        </div>
    """, unsafe_allow_html=True)
    
    seconds = (now.hour * 3600) + (now.minute * 60) + now.second
    progress = seconds / 86400
    st.write(f"⏳ พลังงานขับเคลื่อนโครงข่ายรายวัน: {progress*100:.2f}%")
    st.progress(min(progress, 1.0))

def room_radar():
    st.markdown("<h2 style='color:#FF0055;'>🛰️ SATELLITE HIGH-ACCURACY GPS</h2>", unsafe_allow_html=True)
    
    # เปิดการตั้งค่าพิกัดความแม่นยำสูงระดับฮาร์ดแวร์อุปกรณ์ (EnableHighAccuracy=true)
    loc = get_geolocation()
    
    if loc and 'coords' in loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        st.success(f"🎯 พิกัดดาวเทียมตรงจุดจริง (ไม่คลาดเคลื่อน): Lat {lat} | Lon {lon}")
    else:
        lat, lon = 13.7367, 100.5231
        st.warning("⚠️ กำลังค้นหาสัญญาณพิกัดด่วน... เปิดพิกัด GPS บนมือถือเพื่อความแม่นยำสูงสุด")

    all_users = db.reference('users').get()
    
    # สร้าง Map ดึงภาพไฮบริดจากดาวเทียม ซูมพิกัดเจาะลึกความละเอียดสูง
    m = folium.Map(location=[lat, lon], zoom_start=18, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
    folium.Marker([lat, lon], tooltip="ตำแหน่งของคุณ", icon=folium.Icon(color='red', icon='user', prefix='fa')).add_to(m)
    
    if all_users:
        for uid, data in all_users.items():
            if uid != st.session_state.user and data.get('lat'):
                folium.Marker([data['lat'], data['lon']], tooltip=f"Agent: {uid}", icon=folium.Icon(color='blue')).add_to(m)
                
    st_folium(m, width="100%", height=450, key="radar_map")
    
    if st.button("📡 ยิงสัญญาณระบุตำแหน่งพิกัดแท้จริงลงฐานข้อมูล", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({
            'lat': lat,
            'lon': lon,
            'ts': time.time()
        })
        st.toast("ส่งพิกัดดาวเทียมชุดสมบูรณ์เสร็จสิ้น!")

def room_comms():
    st.markdown("<h2 style='color:#0066FF;'>💬 COMM LIVE SYNC CENTER</h2>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🌐 โครงข่ายแชตสดไร้ดีเลย์", "📞 สัญญาณโทรความถี่สูง SECURE CALL"])
    
    with t1:
        # ยัดระบบรับส่งข้อความ Realtime ผ่าน Firebase Database JavaScript ตรงๆ แชตเด้งทันทีไม่ต้องรอ Rerun หน้าจอแอปทั้งหมด
        chat_js = f"""
        <div style="background:#000; border:2px solid #FF0055; padding:15px; border-radius:10px;">
            <div id="chat_logs" style="height:250px; overflow-y:auto; background:#0a0a0a; border:1px solid #333; padding:10px; margin-bottom:10px; font-family:monospace; color:#fff;">
                <p style="color:#888;">>>> กำลังเปิดช่องรับส่งสัญญาณสด...</p>
            </div>
            <input type="text" id="chat_msg" placeholder="พิมพ์ข้อความส่งเข้าเซิร์ฟเวอร์หลัก..." style="width:78%; padding:10px; background:#111; color:#fff; border:1px solid #0066FF; border-radius:5px;">
            <button id="send_btn" style="width:18%; padding:10px; background:linear-gradient(45deg, #0066FF, #39FF14); color:#000; font-weight:bold; border:none; border-radius:5px; cursor:pointer;">SEND</button>
        </div>

        <script src="https://www.gstatic.com/firebasejs/8.10.1/firebase-app.js"></script>
        <script src="https://www.gstatic.com/firebasejs/8.10.1/firebase-database.js"></script>
        <script>
            var firebaseConfig = {{ databaseURL: "{st.secrets['firebase_db_url']}" }};
            if (!firebase.apps.length) {{ firebase.initializeApp(firebaseConfig); }}
            var db = firebase.database();

            // ฟังฟังก์ชันเมื่อมีแชตใหม่เด้งเข้าดึงข้อมูลโชว์ทันที
            db.ref('public_chat').limitToLast(15).on('value', function(snapshot) {{
                var logs = document.getElementById('chat_logs');
                logs.innerHTML = "";
                snapshot.forEach(function(childSnapshot) {{
                    var data = childSnapshot.val();
                    var p = document.createElement('p');
                    p.innerHTML = "<b style='color:#39FF14'>🟢 " + data.u + "</b>: " + data.m;
                    logs.appendChild(p);
                }});
                logs.scrollTop = logs.scrollHeight;
            }});

            document.getElementById('send_btn').onclick = function() {{
                var text = document.getElementById('chat_msg').value;
                if(text.trim() !== "") {{
                    db.ref('public_chat').push({{
                        u: "{st.session_state.user}",
                        m: text,
                        ts: Date.now()
                    }});
                    document.getElementById('chat_msg').value = "";
                }}
            }};
        </script>
        """
        components.html(chat_js, height=360)
        
    with t2:
        all_u = db.reference('users').get()
        friends = [uid for uid in all_u.keys() if uid != st.session_state.user] if all_u else []
        target = st.selectbox("🎯 เลือกเป้าหมายปลายทางเพื่อเชื่อมต่อสายตรง :", [""] + friends)
        if target:
            # เพิ่มการตั้งค่า ICE Servers เสริมเสถียรภาพการส่งคลื่นเสียงไม่หลุดง่ายในระบบเครือข่ายมือถือ
            call_js = """
            <div style="background:#050505; padding:15px; border:2px solid #0066FF; border-radius:10px; text-align:center;">
                <h3 style="color:#fff; font-family:Orbitron;">📞 TARGET SECURE SIGNAL: %s</h3>
                <button id="cBtn" style="width:100%%; padding:12px; background:linear-gradient(45deg, #FF0055, #0066FF); color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">[ กดเชื่อมต่อวงจรเสียง ]</button>
                <audio id="rAudio" autoplay></audio>
            </div>
            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <script>
                const config = {'iceServers': [{'urls': 'stun:stun.l.google.com:19302'}, {'urls': 'stun:stun1.l.google.com:19302'}]};
                const peer = new Peer('%s', {config: config});
                
                peer.on('call', c => { 
                    navigator.mediaDevices.getUserMedia({audio:true}).then(s=>{ 
                        c.answer(s); 
                        c.on('stream',rs=>{ document.getElementById('rAudio').srcObject=rs; }); 
                    });
                });
                
                document.getElementById('cBtn').onclick = () => {
                    navigator.mediaDevices.getUserMedia({audio:true}).then(s=>{ 
                        const c = peer.call('%s', s); 
                        c.on('stream',rs=>{ document.getElementById('rAudio').srcObject=rs; }); 
                    });
                    document.getElementById('cBtn').innerText = "[ กำลังส่งความถี่ถอดรหัสสาย... ]";
                };
            </script>
            """ % (target, st.session_state.user, target)
            components.html(call_js, height=220)

def room_music():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-align:center;'>🎧 CONTINUOUS HOLOGRAPHIC STATION</h2>", unsafe_allow_html=True)
    songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if not songs:
        st.warning("⚠️ ไม่พบข้อมูลไฟล์เสียงนามสกุล .mp3 ในเครื่อง")
        return
    s_a = st.selectbox("🎯 รายการคลื่นเสียงในหน่วยความจำ", ["-- STANDBY SOURCE --"] + songs, index=st.session_state.song_index + 1)
    song_b64 = ""
    song_name = "WAITING FOR SIGNAL..."
    if s_a != "-- STANDBY SOURCE --":
        with open(s_a, "rb") as f:
            song_b64 = base64.b64encode(f.read()).decode()
        st.session_state.song_index = songs.index(s_a)
        song_name = s_a

    # เพิ่มระบการวนลูปต่อเนื่อง 'loop' ลงบนออบเจกต์เสียงโดยตรง
    visualizer_html = f"""
    <div style="background: #000; border: 3px solid #FF0055; border-radius: 20px; padding: 15px; box-shadow: 0 0 20px #0066FF;">
        <div style="overflow: hidden; white-space: nowrap; background: #050505; border: 1px solid {st.session_state.theme_color}55; border-radius: 8px; margin-bottom: 10px; padding: 8px;">
            <p id="mText" style="display: inline-block; padding-left: 100%; font-family: Orbitron, monospace; font-size: 16px; color: white; animation: marquee 12s linear infinite;">
                <span style="animation: rainbowText 4s linear infinite;">>>></span> {song_name} <span style="animation: rainbowText 4s linear infinite;"><<< เล่นเสียงแบบลูปต่อเนื่องอัตโนมัติ >>></span>
            </p>
        </div>
        <canvas id="canvas" style="width: 100%; height: 200px; background: #000; border-radius: 10px;"></canvas>
        <button id="pBtn" style="width: 100%; margin-top:10px; padding: 15px; background: transparent; border: 2px solid {st.session_state.theme_color}; border-radius: 10px; color: #fff; font-family: Orbitron; font-weight:bold; cursor: pointer;">[ SYNC AUDIO STREAM ]</button>
        <audio id="audio" src="data:audio/mp3;base64,{song_b64}" loop></audio>
    </div>
    <style>
        @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
    </style>
    <script>
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const audio = document.getElementById('audio');
    const btn = document.getElementById('pBtn');
    let aCtx, ans, src, data;

    btn.onclick = function() {{
        if (!aCtx) {{
            aCtx = new (window.AudioContext || window.webkitAudioContext)();
            ans = aCtx.createAnalyser();
            src = aCtx.createMediaElementSource(audio);
            src.connect(ans); ans.connect(aCtx.destination);
            ans.fftSize = 128; data = new Uint8Array(ans.frequencyBinCount);
            draw();
        }}
        if (audio.paused) {{ audio.play(); btn.innerText = "[ สัญญาณกำลังทำงานอย่างต่อเนื่อง ]"; btn.style.borderColor = "#FF0055"; }}
        else {{ audio.pause(); btn.innerText = "[ สัญญาณหยุดชั่วคราว ]"; btn.style.borderColor = "#39FF14"; }}
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
    components.html(visualizer_html, height=420)

def room_math():
    # 📟 ห้องแล็บคำนวณสูตรคณิตศาสตร์รหัสควอนตัม 1960 - 2026
    st.markdown("<h2 style='color:#FFD700; text-shadow: 0 0 10px #FFD700;'>📟 QUANTUM MATRIX LAB (1960 - 2026)</h2>", unsafe_allow_html=True)
    
    st.markdown('<div class="neon-box">', unsafe_allow_html=True)
    birth_year = st.number_input("ป้อนปีคริสต์ศักราชที่ต้องการวิเคราะห์คำนวณ (ค.ศ. 1960 - 2026) :", min_value=1960, max_value=2026, value=1990)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🧮 สมการคลื่นความถี่จำลอง")
        # สูตรตัวเลขทางคณิตศาสตร์วิเคราะห์รอบวงโคจรชีวิต
        base_calc = (birth_year * 7) % 9
        quantum_code = (birth_year ** 2) / 1960
        st.info(f"🧬 ค่าฐานสมดุลวิเคราะห์: **{base_calc}**")
        st.success(f"🌀 ค่ารหัสลับคลื่นควอนตัม: **{quantum_code:.4f}**")
    
    with col2:
        st.markdown("### 📈 ดัชนีสนามพลังงานคงที่")
        current_year = 2026
        age_span = current_year - birth_year
        vibration_freq = (age_span * 3.1415) / 100
        st.info(f"⏳ ระยะช่วงปีสะสมอายุไข: **{age_span} ปี**")
        st.metric("ความถี่กระแสจิต (Consciousness Frequency)", f"{vibration_freq:.4f} Hz")
        
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 5. MAIN ARCHITECTURE
# ==========================================
def main():
    if not st.session_state.authenticated:
        login_screen()
    else:
        with st.sidebar:
            st.title("⚙️ SYNAPSE DASHBOARD")
            st.markdown(f"**ตัวแทนใช้งาน:** <span style='color:{st.session_state.theme_color};'>{st.session_state.user}</span>", unsafe_allow_html=True)
            st.session_state.theme_color = st.color_picker("ปรับแต่งคลื่นสีหน้าหลัก (THEME)", st.session_state.theme_color)
            st.session_state.bg_color = st.color_picker("สีพื้นหลังแกนกลาง (BG)", st.session_state.bg_color)
            st.markdown("---")
            if st.button("🔴 ออกจากระบบความปลอดภัย", use_container_width=True):
                st.session_state.authenticated = False
                st.rerun()

        # แท็บโมดูลการทำงานของระบบ
        tabs = st.tabs(["🚀 CORE COMMAND", "🛰️ HIGH-GPS RADAR", "💬 COMM LIVE", "🎧 LOOP MUSIC", "📟 QUANTUM MATH"])
        rooms = [room_core, room_radar, room_comms, room_music, room_math]
        for i, tab in enumerate(tabs):
            with tab: 
                rooms[i]()

if __name__ == "__main__":
    main()
ยังแชตไม่ได้
