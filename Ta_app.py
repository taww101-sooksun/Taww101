import streamlit as st
import os 
import base64
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
# 1. INITIAL SETUP & SECURITY CHECK
# ==========================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide", initial_sidebar_state="expanded")

def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    if 'user' not in st.session_state: st.session_state.user = None
    if 'authenticated' not in st.session_state: st.session_state.authenticated = False
    if 'song_index' not in st.session_state: st.session_state.song_index = 0

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
# 2. ADVANCED UI CUSTOMIZATION
# ==========================================
st.markdown(f"""
    <style>
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
    
    .neon-box {{ 
        border: 2px solid #0066FF; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center; 
        box-shadow: inset 0 0 15px #FF0055, 0 0 15px {st.session_state.theme_color}; 
        background-color: rgba(0,0,0,0.8);
    }}
    
    @keyframes dance-neon {{
        0% {{ transform: scale(1) rotate(0deg); border-color: #FF0055; box-shadow: 0 0 20px #FF0055, inset 0 0 10px #FF0055; }}
        33% {{ transform: scale(1.03) rotate(1deg); border-color: #0066FF; box-shadow: 0 0 25px #0066FF, inset 0 0 15px #0066FF; }}
        66% {{ transform: scale(0.98) rotate(-1deg); border-color: #39FF14; box-shadow: 0 0 20px #39FF14, inset 0 0 10px #39FF14; }}
        100% {{ transform: scale(1) rotate(0deg); border-color: #FFD700; box-shadow: 0 0 20px #FFD700, inset 0 0 10px #FFD700; }}
    }}
    .dancing-logo {{
        width: 120px;
        height: 120px;
        margin: 0 auto;
        border-radius: 25px; 
        border: 4px solid #FFD700;
        animation: dance-neon 4s infinite ease-in-out;
        object-fit: cover;
        background: #000000;
        padding: 5px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- ฟังก์ชันดึงไฟล์ Base64 ---
def get_base64_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

logo_base64 = get_base64_file("logo1.png")
audio_base64 = get_base64_file("notification.mp3")

# ==========================================
# 3. AUTHENTICATION SYSTEM (GATEWAY)
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
                acc_ref = db.reference(f'users/{user_input}')
                account_data = acc_ref.get()
                
                if mode == "ลงทะเบียนตัวแทนใหม่":
                    if account_data:
                        st.error("❌ มีรหัสตัวแทนนี้อยู่ในระบบสารสนเทศแล้ว")
                    else:
                        acc_ref.set({
                            'password': pass_input, 
                            'created_at': datetime.now().isoformat()
                        })
                        st.success("🛰️ ลงทะเบียนตัวแทนใหม่สำเร็จ เข้าสู่ระบบได้ทันที")
                else:
                    if account_data and account_data.get('password') == pass_input:
                        st.session_state.user = user_input
                        st.session_state.authenticated = True
                        st.success("🔓 อนุมัติสิทธิ์เข้าถึงฐานข้อมูลกลาง!")
                        st.rerun()
                    else:
                        st.error("❌ รหัสตัวแทนหรือรหัสผ่านไม่ถูกต้อง พ้นสภาพความปลอดภัย")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 4. MODULE ROOMS
# ==========================================

def room_core():
    if logo_base64:
        st.markdown(f'<center><img src="data:image/png;base64,{logo_base64}" class="dancing-logo"></center><br>', unsafe_allow_html=True)
    else:
        st.markdown('<center><div class="dancing-logo" style="display:flex; align-items:center; justify-content:center; color:#FFD700; font-weight:bold; font-size:20px;">[ NO LOGO ]</div></center><br>', unsafe_allow_html=True)

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
    loc = get_geolocation()
    
    # ดึงค่าพิกัดปัจจุบันจากเบราว์เซอร์มือถือ
    if loc and 'coords' in loc:
        lat = loc['coords']['latitude']
        lon = loc['coords']['longitude']
        st.success(f"🎯 พิกัดดาวเทียมตรงจุดจริง (อัปเดตสด): Lat {lat} | Lon {lon}")
    else:
        lat, lon = 13.7367, 100.5231
        st.warning("⚠️ กำลังค้นหาสัญญาณพิกัดด่วน... โปรดเปิดพิกัดตำแหน่งบนมือถือ")

    # ดึงพิกัดของ Agents ทั้งหมดมาพล็อตลงแผนที่ดาวเทียม
    all_users = db.reference('users').get()
    m = folium.Map(location=[lat, lon], zoom_start=16, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
    folium.Marker([lat, lon], tooltip="ตำแหน่งของคุณ", icon=folium.Icon(color='red', icon='user', prefix='fa')).add_to(m)
    
    if all_users:
        for uid, data in all_users.items():
            if uid != st.session_state.user and isinstance(data, dict) and data.get('lat'):
                folium.Marker([data['lat'], data['lon']], tooltip=f"Agent: {uid}", icon=folium.Icon(color='blue')).add_to(m)
                
    st_folium(m, width="100%", height=450, key="radar_map")
    
    if st.button("📡 ยิงสัญญาณระบุตำแหน่งพิกัดแท้จริงลงฐานข้อมูล", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({
            'lat': lat,
            'lon': lon,
            'gps_ts': time.time()
        })
        st.toast("ส่งพิกัดดาวเทียมชุดสมบูรณ์เข้าเซิร์ฟเวอร์กลางแล้ว!")


def room_comms():
    st.markdown("<h2 style='color:#0066FF;'>💬 COMM LIVE SYNC CENTER</h2>", unsafe_allow_html=True)
    
    # ดึงตัวแปรที่จำเป็นส่งให้ JavaScript ทำงานร่วมกับ Firebase
    db_url = st.secrets['firebase_db_url']
    current_agent = st.session_state.user
    
    chat_js = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
        #chat-screen {{
            background: rgba(0,0,0,0.95); border: 2px solid {st.session_state.theme_color}; border-radius: 12px;
            height: 350px; overflow-y: auto; padding: 15px; display: flex; flex-direction: column;
            box-shadow: inset 0 0 15px {st.session_state.theme_color}33;
        }}
        .bubble {{ padding: 10px 15px; border-radius: 10px; margin: 8px 0; max-width: 85%; color: #fff; font-family: 'Orbitron', sans-serif; font-size: 14px; line-height: 1.4; }}
        .me {{ background: {st.session_state.theme_color}22; border-right: 4px solid {st.session_state.theme_color}; align-self: flex-end; }}
        .others {{ background: #222; border-left: 4px solid #777; align-self: flex-start; }}
        .notif-box {{ background: #333; color: white; padding: 4px 12px; border-radius: 20px; font-size: 11px; }}
        .alert-red {{ background: #F00 !important; box-shadow: 0 0 15px #F00; font-weight: bold; }}
    </style>

    <div id="chat-screen">
        <div style="display:flex; justify-content:space-between; margin-bottom:12px; border-bottom: 1px solid #333; padding-bottom: 5px;">
            <span style="color:{st.session_state.theme_color}; font-size:10px; letter-spacing: 2px;">📡 LIVE STREAM SIGNAL</span>
            <span id="notif-box" class="notif-box">0 NEW SIGNAL</span>
        </div>
        <div id="msg-area" style="display:flex; flex-direction:column;"></div>
    </div>

    <div style="margin-top: 10px; display: flex; gap: 10px;">
        <input type="text" id="chat_msg" placeholder="พิมพ์ข้อความส่งสัญญาณ..." style="flex-grow:1; padding:12px; background:#111; color:#fff; border:1px solid #0066FF; border-radius:8px;">
        <button id="send_btn" style="width:100px; padding:12px; background:linear-gradient(45deg, #0066FF, #39FF14); color:#000; font-weight:bold; border:none; border-radius:8px; cursor:pointer;">SEND</button>
    </div>

    <audio id="notif-sound" preload="auto">
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
    </audio>

    <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
    <script>
        const fb_conf = {{ databaseURL: "{db_url}" }};
        if(!firebase.apps.length) firebase.initializeApp(fb_conf);
        const database = firebase.database();
        let lastCount = -1;
        const beep = document.getElementById('notif-sound');

        function unlock() {{
            beep.play().then(() => {{ beep.pause(); beep.currentTime = 0; }}).catch(()=>{{\}});
            window.removeEventListener('click', unlock);
            window.removeEventListener('touchstart', unlock);
        }}
        window.addEventListener('click', unlock);
        window.addEventListener('touchstart', unlock);

        // โหลดข้อมูลและดักจับข้อความใหม่ในฐานข้อมูล global_chat หลัก
        database.ref('global_chat').limitToLast(25).on('child_added', (snap) => {{
            const msg = snap.val();
            const area = document.getElementById('msg-area');
            const div = document.createElement('div');
            const isMe = msg.user === "{current_agent}";
            
            div.className = "bubble " + (isMe ? "me" : "others");
            div.style.alignSelf = isMe ? 'flex-end' : 'flex-start';
            
            let html = `<div style="font-size:10px; color:#777; margin-bottom:5px;">${{msg.user}}</div>`;
            if(msg.text) html += `<div>${{msg.text}}</div>`;
            if(msg.img) html += `<img src="data:image/png;base64,${{msg.img}}" style="max-width:100%; border-radius:8px; margin-top:8px; border: 1px solid #444;">`;
            
            div.innerHTML = html;
            area.appendChild(div);
            document.getElementById('chat-screen').scrollTop = 999999;
        }});

        // ปุ่มกดส่งข้อความทาง JS
        document.getElementById('send_btn').onclick = function() {{
            const txt = document.getElementById('chat_msg').value;
            if(txt.trim() !== "") {{
                database.ref('global_chat').push({{
                    user: "{current_agent}",
                    text: txt,
                    ts: new Date().toISOString()
                }});
                document.getElementById('chat_msg').value = "";
                
                // กระตุ้นระบบสั่น/แจ้งเตือนเพื่อน
                database.ref('chat_notifications/unread_count').transaction((cur) => {{
                    return (cur || 0) + 1;
                }});
            }}
        }};

        document.getElementById('chat_msg').addEventListener("keypress", function(e) {{
            if (e.key === "Enter") {{ e.preventDefault(); document.getElementById('send_btn').click(); }}
        }});

        // รับค่าชุดนับแจ้งเตือนส่งสัญญาณเสียงบี๊ป
        database.ref('chat_notifications/unread_count').on('value', (snap) => {{
            const val = snap.val() || 0;
            const box = document.getElementById('notif-box');
            box.innerText = val + " NEW SIGNAL";
            if(val > 0) {{
                box.classList.add('alert-red');
                if(lastCount !== -1 && val > lastCount) {{
                    beep.currentTime = 0;
                    beep.play().catch(() => {{}});
                }}
            }} else {{
                box.classList.remove('alert-red');
            }}
            lastCount = val;
        }});
    </script>
    """
    components.html(chat_js, height=450)
    
    if st.button("🔔 ล้างสถานะการแจ้งเตือนแชต (RESET NOTIFICATION)", use_container_width=True):
        db.reference('chat_notifications').set({'unread_count': 0})
        st.rerun()


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
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-shadow: 0 0 20px {st.session_state.theme_color}; text-align:center;'>🧬 THE TRUTH DECODER</h2>", unsafe_allow_html=True)
    
    def decode_truth(dt):
        ref_date = date(1900, 1, 1)
        diff = (dt - ref_date).days
        lunar_cycle = 29.530589
        pos = (diff - 0.5) % lunar_cycle
        day_val = dt.weekday() + 1
        
        thai_year = dt.year + 543
        zodiacs = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
        zodiac = zodiacs[thai_year % 12]
        
        elements = {1: "ดิน", 2: "น้ำ", 3: "ไฟ", 4: "ลม", 5: "ทอง", 6: "น้ำ", 7: "ดิน"}
        element = elements.get(day_val, "ดิน")

        if pos <= 14.765:
            m_num = int(pos) + 1
            phase = f"ขึ้น {m_num} ค่ำ"
            res = math.sqrt((day_val**2) + (m_num**2))
            formula = f"√({day_val}² + {m_num}²)"
            p_type = "แรงผลักดันวงเวียนเวกเตอร์ (Vector)"
        else:
            m_num = int(pos - 14.765) + 1
            phase = f"แรม {m_num} ค่ำ"
            res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
            formula = f"({day_val} × 1.618) / {m_num}"
            p_type = "สมดุลสัดส่วนทองคำศักดิ์สิทธิ์ (Phi)"
            
        return {"res": round(res, 4), "phase": phase, "zodiac": zodiac, "element": element, "formula": formula, "type": p_type, "day_num": day_val, "lunar_num": m_num, "diff": diff, "day_name": ["จันทร์","อังคาร","พุธ","พฤหัสบดี","ศุกร์","เสาร์","อาทิตย์"][dt.weekday()]}

    # ฟังก์ชันสแกนหาไทม์ไลน์
    def run_scanner(base_res, start_dt, days_range, direction="future"):
        data_list = []
        for i in range(1, days_range + 1):
            target_step = start_dt + timedelta(days=i) if direction == "future" else start_dt - timedelta(days=i)
            inf = decode_truth(target_step)
            gap = abs(base_res - inf['res'])
            
            # บันทึกเฉพาะพิกัดสำคัญตามเกณฑ์ ธร-เพชร-กงจักร
            status = ""
            if gap <= 1.0: status = "💎 เพชร (บรรจบสูงสุด)"
            elif 3.8 <= gap <= 4.2: status = "🌀 ธร (สะท้อนคู่ขนาน)"
            elif gap >= 10.0: status = "⚙️ กงจักร (แยกตัวอิสระ)"
            
            if status:
                data_list.append({
                    "วันที่สแกนพบ": target_step.strftime('%Y-%m-%d'),
                    "รหัสวัน": inf['res'],
                    "ค่า GAP": round(gap, 4),
                    "ระดับสัญญาณ": status,
                    "รายละเอียด": f"วัน{inf['day_name']} {inf['phase']} ปี{inf['zodiac']}"
                })
        return data_list

    st.subheader("1️⃣ ตรวจสอบพิกัดความจริงรายวัน (1960 - 2026)")
    target_date = st.date_input("เลือกวันที่ตรวจสอบพิกัดสารสนเทศ", value=date.today(), min_value=date(1960,1,1), max_value=date(2026,12,31))
    
    if target_date:
        d = decode_truth(target_date)
        st.markdown(f"""
            <div style="text-align:center; padding:20px; border:2px solid {st.session_state.theme_color}; border-radius:20px; background:rgba(0,0,0,0.3);">
                <small>รหัสพิกัดคลื่นความถี่จักรวาล</small>
                <h1 style="color:{st.session_state.theme_color}; font-size:60px; margin:0;">{d['res']}</h1>
                <p style="color:#888;">{d['type']}</p>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📅 **ฐานวัน ({d['day_num']}):** วัน{d['day_name']} (แรงดึงดูดโลก)")
            st.info(f"🌙 **จันทรคติ ({d['phase']}):** พิกัด {d['lunar_num']} (แรงดึงดูดดวงจันทร์)")
        with col2:
            st.success(f"🐎 **ปีนักษัตรประจำวัน:** ปี{d['zodiac']}")
            st.success(f"💎 **ธาตุสนามพลังงาน:** ธาตุ{d['element']}")

        st.markdown(f"""
            <div style="background:#111; padding:15px; border-left:5px solid {st.session_state.theme_color}; border-radius:10px; margin-top:10px;">
                <p style="font-size:14px; color:#aaa; margin:0;">
                    <b>สูตรการคำนวณถอดรหัสความจริง:</b> {d['formula']}<br>
                    วิเคราะห์ผลรวมความต่อเนื่องนับจากปีหลัก 1900 รวมทั้งสิ้น {d['diff']:,} วัน
                </p>
            </div>
        """, unsafe_allow_html=True)

        # ---------------------------------------------------------
        # 2. วิเคราะห์รหัสคู่ขนาน & หาค่า GAP (ธร-เพชร-กงจักร)
        # ---------------------------------------------------------
        st.divider()
        st.subheader("2️⃣ วิเคราะห์รหัสคู่ขนาน & สัญญาณ GAP")
        c1, c2 = st.columns(2)
        with c1:
            dob1 = st.date_input("👤 AGENT 1 (ตัวตั้งต้นความจริง)", value=date.today(), min_value=date(1960,1,1), key="u1_main")
        with c2:
            dob2 = st.date_input("👤 AGENT 2 (เป้าหมายร่วมสแกน)", value=None, min_value=date(1960,1,1), key="u2_main")

        if dob1 and dob2:
            dat1 = decode_truth(dob1)
            dat2 = decode_truth(dob2)
            g_val = abs(dat1['res'] - dat2['res'])

            st.markdown("#### 🛠️ กระบวนการถอดรหัสและเปรียบเทียบสัญญาณสด")
            col_ex1, col_ex2 = st.columns(2)
            with col_ex1:
                st.markdown(f"**AGENT 1:** {dob1}")
                st.write(f"- วัน{dat1['day_name']} = `{dat1['day_num']}` | {dat1['phase']} = `{dat1['lunar_num']}`")
                st.code(f"สูตร: {dat1['formula']} = {dat1['res']}")
            with col_ex2:
                st.markdown(f"**AGENT 2:** {dob2}")
                st.write(f"- วัน{dat2['day_name']} = `{dat2['day_num']}` | {dat2['phase']} = `{dat2['lunar_num']}`")
                st.code(f"สูตร: {dat2['formula']} = {dat2['res']}")

            st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color}; text-shadow: 0 0 15px {st.session_state.theme_color};'>GAPผลลัพธ์ห่าง: {g_val:.4f}</h1>", unsafe_allow_html=True)
            
            if g_val <= 1.0:
                st.error("💎 **ระดับความเสถียร: เพชร (Diamond)** - รหัสคลื่นบรรจบขั้นสูงสุด")
            elif 3.8 <= g_val <= 4.2:
                st.warning("🌀 **ระดับความเสถียร: ธร (Tor)** - สัญญาณสะท้อนคู่ขนานเหนี่ยวนำสำคัญ")
            elif g_val >= 10.0:
                st.success("⚙️ **ระดับความเสถียร: กงจักร (Chakra)** - รหัสตัดขาดหรือแยกตัวเป็นอิสระต่อกัน")

            # ---------------------------------------------------------
            # 3. แผนที่พิกัดเวลา (Past & Future Timeline)
            # ---------------------------------------------------------
            st.divider()
            st.subheader("3️⃣ ตารางแผนที่พิกัดกาลเวลาจุดเปลี่ยน (วิเคราะห์ล่วงหน้า-ย้อนหลัง 365 วัน)")
            st.write(f"คำนวณฐานรอบวันของรหัสตัวตั้งต้น: **{dat1['res']}**")
            t_back, t_next = st.tabs(["⏪ ตรวจสอบจุดพลังงานในอดีต", "🔮 พยากรณ์คลื่นความถี่ในอนาคต"])
            with t_back:
                past_data = run_scanner(dat1['res'], date.today(), 365, "past")
                if past_data: st.dataframe(past_data, use_container_width=True)
                else: st.info("--- ไม่พบสัญญาณแทรกแซงพิเศษในรอบ 365 วันที่ผ่านมา ---")
            with t_next:
                future_data = run_scanner(dat1['res'], date.today(), 365, "future")
                if future_data: st.dataframe(future_data, use_container_width=True)
                else: st.info("--- ไม่พบวันบรรจบพลังงานระดับวิกฤตล่วงหน้าใน 365 วันนี้ ---")

# ==========================================
# 5. MAIN ARCHITECTURE
# ==========================================
def main():
    if not st.session_state.authenticated:
        login_screen()
    else:
        with st.sidebar:
            st.title("⚙️ SYNAPSE DASHBOARD")
            st.markdown(f"**ตัวแทนล็อกอิน:** <span style='color:{st.session_state.theme_color};'>{st.session_state.user}</span>", unsafe_allow_html=True)
            st.session_state.theme_color = st.color_picker("ปรับแต่งหน้าสีธีม (THEME)", st.session_state.theme_color)
            st.session_state.bg_color = st.color_picker("สีพื้นหลังแกนกลาง (BG)", st.session_state.bg_color)
            st.markdown("---")
            if st.button("🔴 ออกจากระบบความปลอดภัย", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.rerun()

        tabs = st.tabs(["🚀 CORE COMMAND", "🛰️ HIGH-GPS RADAR", "💬 COMM LIVEแชตสด", "🎧 LOOP MUSIC", "📟 QUANTUM MATRIX"])
        rooms = [room_core, room_radar, room_comms, room_music, room_math]
        for i, tab in enumerate(tabs):
            with tab: 
                rooms[i]()

if __name__ == "__main__":
    main()
