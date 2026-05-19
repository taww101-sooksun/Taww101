import streamlit as st
import streamlit.components.v1 as components
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
import firebase_admin
from firebase_admin import credentials, db
import math
import time
import base64
import os
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit as st

# 1. ตั้งค่าสีและขนาดฟอนต์ตามที่ชอบ (เน้นปุ่มใหญ่ กดง่าย ชัดเจน)
st.markdown("""
    <style>
    /* ปรับหัวข้อและปุ่มให้ใหญ่ขึ้น เหมาะกับจิ้มบนมือถือ */
    .stButton>button {
        width: 100%;
        height: 55px;
        font-size: 18px !important;
        font-weight: bold;
    }
    h1, h2, h3 {
        color: #FF4B4B; /* สีแดง/น้ำเงินตามคอนเซปต์แอป */
    }
    </style>
""", unsafe_allow_html=True)

# 2. จัดการระบบห้องด้วย Session State
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login' # เริ่มต้นที่หน้าล็อกอิน

# ฟังก์ชันสำหรับเปลี่ยนห้องอย่างปลอดภัย
def change_room(room_name):
    st.session_state.current_page = room_name
    st.invalidate() # ช่วยเคลียร์สถานะเก่า
    st.rerun() # บังคับให้โหลดหน้าจอใหม่ทันที เพื่อป้องกันข้อผิดพลาด removeChild

# --- การควบคุมการแสดงผลแต่ละห้อง ---
placeholder = st.empty() # ใช้ Container เปล่าควบคุมเพื่อความเสถียร

with placeholder.container():
    if st.session_state.current_page == 'login':
        st.title("ลงชื่อเข้าใช้งาน")
        # โค้ดหน้าล็อกอิน...
        if st.button("เข้าสู่ระบบ (ไปยังห้องหลัก)"):
            change_room('main_room')

    elif st.session_state.current_page == 'main_room':
        st.title("ห้องหลัก (COMMAND CENTER)")
        
        # ปรับขนาดปุ่มเมนูให้ใหญ่ จิ้มง่าย ไม่หลุดไปโดนส่วนอื่น
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎵 ห้องเครื่องเล่นเพลง"):
                change_room('music_room')
        with col2:
            if st.button("💬 ห้องแชท"):
                change_room('chat_room')

    elif st.session_state.current_page == 'music_room':
        st.title("🎵 ห้องเครื่องเล่นเพลง")
        
        # ตัวอย่างการดึงเพลงจากโฟลเดอร์เดียวกัน
        st.write("รายชื่อเพลงในระบบ...")
        
        if st.button("⬅️ กลับหน้าหลัก"):
            change_room('main_room')

    elif st.session_state.current_page == 'chat_room':
        st.title("💬 ห้องแชท")
        # โค้ดห้องแชท...
        if st.button("⬅️ กลับหน้าหลัก"):
            change_room('main_room')

# =========================================================
# 1. INITIALIZATION & HIGH-LEVEL NEON CYBERPUNK UI
# =========================================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")

def inject_cyberpunk_mainframe():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Sarabun:wght@300;600&display=swap');
            
            /* พื้นหลังและฟอนต์ภาพรวม */
            .stApp { 
                background: radial-gradient(circle at 50% 50%, #03070a 0%, #010204 100%) !important;
                font-family: 'Sarabun', sans-serif;
                color: #e0e0e0;
            }
            
            /* ซ่อนเมนู Streamlit เดิม */
            #MainMenu, footer, header { visibility: hidden; }
            .stApp { top: -60px; }
            
            /* ปรับแต่งเมนูด้านซ้าย (Sidebar) ให้ดูล้ำขึ้น */
            [data-testid="stSidebar"] {
                background-color: #03060a !important;
                border-right: 3px solid #39FF14 !important;
                box-shadow: 5px 0 15px rgba(57, 255, 20, 0.1);
            }
            
            /* ปรับขนาดตัวเลือก Radio Menu ให้ใหญ่ จิ้มง่ายบนมือถือ */
            .stRadio>div {
                gap: 15px !important;
            }
            .stRadio label {
                font-size: 18px !important;
                font-weight: bold !important;
                color: #00e5ff !important;
                padding: 10px 15px !important;
                border: 2px solid #101a24 !important;
                border-radius: 8px !important;
                background: #060b10 !important;
                display: block !important;
                width: 100% !important;
                cursor: pointer;
            }
            .stRadio [data-checked="true"] label {
                border-color: #39FF14 !important;
                color: #39FF14 !important;
                box-shadow: 0 0 10px rgba(57, 255, 20, 0.3) !important;
                background: rgba(57, 255, 20, 0.05) !important;
            }
            
            /* ตกแต่งปุ่มกดทั่วไป */
            .stButton>button {
                font-size: 18px !important;
                font-weight: bold !important;
                padding: 12px 20px !important;
                border-radius: 8px !important;
                background: linear-gradient(135deg, #0b151f 0%, #04080c 100%) !important;
                border: 2px solid #ff00de !important;
                color: #ff00de !important;
                text-shadow: 0 0 5px #ff00de;
                transition: 0.3s;
                width: 100%;
            }
            .stButton>button:hover {
                border-color: #39FF14 !important;
                color: #39FF14 !important;
                text-shadow: 0 0 5px #39FF14;
                box-shadow: 0 0 15px rgba(57, 255, 20, 0.4);
            }
            
            /* กล่องแสดงสถานะสไตล์รกรุงรัง (Matrix Terminals) */
            .matrix-box {
                background-color: #04070a;
                border: 2px solid #101a24;
                padding: 12px;
                border-radius: 8px;
                font-family: 'Orbitron', monospace;
                font-size: 11px;
                color: #527394;
                line-height: 1.4;
                margin-bottom: 10px;
                overflow: hidden;
            }
            
            /* การ์ดแกนกลางความจริง */
            .truth-card-blue {
                background: linear-gradient(135deg, rgba(4,14,24,0.9) 0%, rgba(2,5,10,0.95) 100%);
                border: 4px solid #00e5ff;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 0 20px rgba(0,229,255,0.2);
                margin-bottom: 15px;
            }
            .truth-card-pink {
                background: linear-gradient(135deg, rgba(24,4,14,0.9) 0%, rgba(10,2,5,0.95) 100%);
                border: 4px solid #ff00de;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 0 20px rgba(255,0,222,0.2);
                margin-bottom: 15px;
            }
            
            /* ตัวเลขพิกัดใหญ่ๆ ชัดๆ */
            .giant-number {
                font-family: 'Orbitron', sans-serif;
                font-size: 38px !important;
                font-weight: bold;
                text-align: center;
                margin: 10px 0;
            }
            
            /* ตารางข้อมูลคอมพิวเตอร์ */
            .stDataFrame {
                border: 2px solid #101a24 !important;
                border-radius: 8px !important;
                background-color: #020406 !important;
            }
        </style>
    """, unsafe_allow_html=True)

inject_cyberpunk_mainframe()

# --- ฟังก์ชันตัวช่วยแปลงไฟล์เข้ารหัส Base64 ---
def get_base64_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

logo_base64 = get_base64_data("logo1.png")
audio_data = get_base64_data("notification.mp3")
theme_green = "#39FF14"

# =========================================================
# 2. FIREBASE DATALINK CONNECTION
# =========================================================
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_credentials"])
        fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
    except Exception as e:
        st.error(f"📡 MAIN CONNECTOR FAILURE: {e}")

# =========================================================
# 3. CORE LOGIC ENGINE (คณิตศาสตร์ความจริงเดี่ยว)
# =========================================================
def calculate_quantum_logic(dt):
    if dt is None: return None
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    
    thai_year = dt.year + 543
    zodiacs = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
    zodiac = zodiacs[thai_year % 12]
    
    is_waxing = pos <= 14.765
    m_num = int(pos) + 1 if is_waxing else int(pos - 14.765) + 1
    phase_text = f"{'ขึ้น' if is_waxing else 'แรม'} {m_num} ค่ำ"
    
    if is_waxing:
        res = math.sqrt((day_val**2) + (m_num**2))
        formula = f"√({day_val}² + {m_num}²)"
        sys_type = "Vector Force (สภาวะผลักดัน)"
    else:
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula = f"({day_val} × 1.618) / {m_num}"
        sys_type = "Golden Ratio (สภาวะสมดุลทองคำ)"

    return {
        "res": round(res, 4), "phase": phase_text, "day": day_names[dt.weekday()],
        "formula": formula, "type": sys_type, "zodiac": zodiac
    }

# =========================================================
# 4. SESSION STATE REGISTRY
# =========================================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None
if 'user_lat' not in st.session_state: st.session_state.user_lat = None
if 'user_lon' not in st.session_state: st.session_state.user_lon = None

# =========================================================
# 5. MAIN GATEWAY: AUTHENTICATION (LOGIN / REGISTER)
# =========================================================
if not st.session_state.logged_in:
    header_gate = f"""
    <div style="text-align:center; padding:20px 0;">
        <h1 style="color:#ff00de; font-family:'Orbitron'; letter-spacing:5px; text-shadow: 0 0 15px #ff00de;">🛡️ SYNAPSE ACCESS GATEWAY</h1>
        <p style="color:#527394; font-family:'Orbitron'; font-size:11px;">SYSTEM HARDWARE DEPLOYMENT // CORE V.3.5 // SECURITY MANIFEST</p>
    </div>
    """
    components.html(header_gate, height=120)
    
    col_gate1, col_gate2, col_gate3 = st.columns([1, 2, 1])
    with col_gate2:
        choice = st.radio("GATE_CONTROL_SELECTION", ["🔑 ENTRY MODULE (เข้าสู่ระบบ)", "📝 REGISTER AGENT (ลงทะเบียน)"], label_visibility="collapsed")
        
        st.write("")
        if choice == "🔑 ENTRY MODULE (เข้าสู่ระบบ)":
            with st.form("login_form"):
                user_input = st.text_input("AGENT ID", placeholder="กรอกรหัสตัวแทน...")
                pw_input = st.text_input("PASSWORD", type="password", placeholder="กรอกรหัสผ่าน...")
                if st.form_submit_button("CONNECT TO MAINFRAME ⚡"):
                    user_data = db.reference(f'users/{user_input}').get()
                    if user_data and user_data.get('password') == pw_input:
                        st.session_state.logged_in = True
                        st.session_state.user = user_input
                        st.rerun()
                    else:
                        st.error("🚨 ACCESS DENIED: ข้อมูลตรวจสอบไม่ผ่านรหัสความปลอดภัย")
                        
        else:
            with st.form("reg_form"):
                new_user = st.text_input("NEW AGENT ID", placeholder="ตั้งชื่อผู้ใช้ใหม่...")
                new_pw = st.text_input("NEW PASSWORD", type="password", placeholder="ตั้งรหัสผ่าน...")
                if st.form_submit_button("GENERATE SECURITY PROFILE"):
                    if new_user and new_pw:
                        db.reference(f'users/{new_user}').set({
                            'password': new_pw, 
                            'created_at': datetime.now().isoformat()
                        })
                        st.success("📝 PROFILE RECORDED: ลงทะเบียนสำเร็จ! โปรดสลับไปที่เมนูเข้าสู่ระบบ")
    st.stop()

# =========================================================
# 6. HEADER COMMAND CENTER (DYNAMIC TEXT / LOGO / SLOGAN)
# =========================================================
header_mainframe = f"""
<style>
    @keyframes logo_pulse {{
        0% {{ transform: scale(1) rotate(0deg); filter: drop-shadow(0 0 5px {theme_green}); }}
        50% {{ transform: scale(1.03) rotate(1deg); filter: drop-shadow(0 0 20px {theme_green}); }}
        100% {{ transform: scale(1) rotate(0deg); filter: drop-shadow(0 0 5px {theme_green}); }}
    }}
    @keyframes text_wink {{
        0%, 100% {{ opacity: 1; color: {theme_green}; text-shadow: 0 0 12px {theme_green}; }}
        50% {{ opacity: 0.3; color: #fff; text-shadow: none; }}
    }}
    .panel-container {{ display: flex; align-items: center; justify-content: center; padding: 10px 0; border-bottom: 2px solid #101a24; background: #020508; margin-bottom: 15px; }}
    .panel-logo {{ width: 65px; height: 65px; animation: logo_pulse 2s infinite ease-in-out; object-fit: contain; }}
    .panel-title {{ font-family: 'Orbitron', sans-serif; font-weight: bold; font-size: 22px; letter-spacing: 3px; margin-left: 20px; animation: text_wink 2s infinite; }}
</style>
<div class="panel-container">
    {f'<img src="data:image/png;base64,{logo_base64}" class="panel-logo">' if logo_base64 else ''}
    <span class="panel-title">SYNAPSE COMMAND CENTER</span>
</div>
"""
components.html(header_mainframe, height=95)

# =========================================================
# 7. SIDEBAR MATRIX TERMINAL OPERATOR
# =========================================================
with st.sidebar:
    st.markdown(f"<h3 style='color:#39FF14; font-family:Orbitron; font-size:18px; text-shadow:0 0 5px #39FF14;'>📟 OPERATOR TERMINAL</h3>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#00e5ff; font-size:14px; font-weight:bold; margin-bottom:10px;'>CURRENT AGENT: {st.session_state.user}</div>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="matrix-box">
        >> NET_STATUS: LINK_ESTABLISHED<br>
        >> NODE: CLOUD_FIREBASE_SYS<br>
        >> BUFFER: ACTIVE_ST_RECOMP<br>
        >> MATRIX_LAT: {st.session_state.user_lat if st.session_state.user_lat else 'NULL'}<br>
        >> MATRIX_LON: {st.session_state.user_lon if st.session_state.user_lon else 'NULL'}<br>
        >> SLOGAN_HASH: "อยู่นิ่งๆ ไม่เจ็บตัว"
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    
    menu_selection = st.radio(
        "NAVIGATION_SYSTEM",
        ["💬 ROOM_01: GLOBAL COMMS", "🛰️ ROOM_02: GPS TARGET", "🔮 ROOM_03: TRUTH SCAN", "🧬 ROOM_04: DESTINY ANALYST", "🎵 ROOM_05: SOUND SYSTEM"],
        label_visibility="collapsed"
    )
    
    st.write("---")
    if st.button("🔴 DISCONNECT (LOGOUT)"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

# =========================================================
# 8. HARDWARE WORKSPACE CAPABILITIES (ห้องย่อยทั้ง 5 ห้อง)
# =========================================================

# --- 8.1 ห้องแชทวิทยุกลาง (GLOBAL COMMS) ---
if menu_selection == "💬 ROOM_01: GLOBAL COMMS":
    st.markdown("<h2 style='color:#39FF14; font-family:Orbitron; font-size:22px;'>💬 ROOM_01 // GLOBAL CHATROOM TELEMETRY</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#527394; font-size:13px;'>**คำอธิบายห้อง:** ห้องสื่อสารเครือข่ายย่อยแบบเรียลไทม์ ใช้รับส่งข้อความคลื่นวิทยุและพยานหลักฐานรูปภาพร่วมกับหน่วยข้อมูลอื่น ข้อมูลจะอัปเดตทันทีผ่านระบบ Realtime Datalink</p>", unsafe_allow_html=True)
    
    chat_mainframe_html = f"""
    <style>
        #screen-frame {{
            background: rgba(2,5,10,0.98); border: 2px solid {theme_green}; border-radius: 10px;
            height: 380px; overflow-y: auto; padding: 12px; display: flex; flex-direction: column;
            box-shadow: inset 0 0 15px rgba(57, 255, 20, 0.1);
        }}
        .bubble {{ padding: 10px 14px; border-radius: 8px; margin: 6px 0; max-width: 85%; color: #fff; font-size: 14px; }}
        .me {{ background: {theme_green}12; border-right: 4px solid {theme_green}; align-self: flex-end; }}
        .others {{ background: #101620; border-left: 4px solid #ff00de; align-self: flex-start; }}
        .notif-capsule {{ background: #0c141c; color: #527394; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-family: 'Orbitron'; }}
        .signal-alert {{ background: #ff0055 !important; color: white !important; box-shadow: 0 0 10px #ff0055; font-weight: bold; }}
    </style>

    <div id="screen-frame">
        <div style="display:flex; justify-content:space-between; margin-bottom:10px; border-bottom: 1px solid #101a24; padding-bottom: 5px;">
            <span style="color:{theme_green}; font-family:'Orbitron'; font-size:10px; letter-spacing: 1px;">📡 DATA_STREAM_OPEN</span>
            <span id="notif-box" class="notif-capsule">0 SIGNAL</span>
        </div>
        <div id="msg-terminal-area" style="display:flex; flex-direction:column;"></div>
    </div>

    <audio id="beep-emitter" preload="auto">
        <source src="data:audio/mp3;base64,{audio_data}" type="audio/mp3">
    </audio>

    <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
    <script>
        const conf = {{ databaseURL: "{st.secrets['firebase_db_url']}" }};
        if(!firebase.apps.length) firebase.initializeApp(conf);
        const d_base = firebase.database();
        let last_count_val = -1;
        const sound_node = document.getElementById('beep-emitter');

        function force_unlock() {{
            sound_node.play().then(() => {{ sound_node.pause(); sound_node.currentTime = 0; }});
            window.removeEventListener('click', force_unlock);
            window.removeEventListener('touchstart', force_unlock);
        }}
        window.addEventListener('click', force_unlock);
        window.addEventListener('touchstart', force_unlock);

        d_base.ref('global_chat').limitToLast(20).on('child_added', (snap) => {{
            const data = snap.val();
            const area = document.getElementById('msg-terminal-area');
            const element = document.createElement('div');
            const checkMe = data.user === "{st.session_state.user}";
            element.className = "bubble " + (checkMe ? "me" : "others");
            element.style.alignSelf = checkMe ? 'flex-end' : 'flex-start';
            
            let block = `<div style="font-size:10px; color:#527394; font-family:'Orbitron'; margin-bottom:4px;">${{data.user}}</div>`;
            if(data.text) block += `<div>${{data.text}}</div>`;
            if(data.img) block += `<img src="data:image/png;base64,${{data.img}}" style="max-width:100%; border-radius:6px; margin-top:6px; border: 1px solid #101a24;">`;
            
            element.innerHTML = block;
            area.appendChild(element);
            document.getElementById('screen-frame').scrollTop = 999999;
        }});

        d_base.ref('chat_notifications/unread_count').on('value', (snap) => {{
            const current_num = snap.val() || 0;
            const target_box = document.getElementById('notif-box');
            target_box.innerText = current_num + " NEW SIGNAL";
            if(current_num > 0) {{
                target_box.classList.add('signal-alert');
                if(last_count_val !== -1 && current_num > last_count_val) {{
                    sound_node.currentTime = 0;
                    sound_node.play().catch(() => {{}});
                }}
            }} else {{
                target_box.classList.remove('signal-alert');
            }}
            last_count_val = current_num;
        }});
    </script>
    """
    components.html(chat_mainframe_html, height=400)

    with st.container():
        ctrl1, ctrl2, ctrl3 = st.columns([3, 1, 1])
        with ctrl1:
            in_msg = st.text_input("INPUT TRANSMISSION", placeholder="พิมพ์ข้อความคลื่นเสียง...", label_visibility="collapsed", key="chat_tx")
        with ctrl2:
            in_file = st.file_uploader("UPLOAD DATA", type=['png','jpg','jpeg'], label_visibility="collapsed", key="chat_img")
        with ctrl3:
            if st.button("SEND SIGNAL ⚡", use_container_width=True):
                if in_msg or in_file:
                    payload = {'user': st.session_state.user, 'ts': datetime.now().isoformat()}
                    if in_msg: payload['text'] = in_msg
                    if in_file: payload['img'] = base64.b64encode(in_file.read()).decode()
                    db.reference('global_chat').push(payload)
                    
                    notify_count = db.reference('chat_notifications/unread_count').get() or 0
                    db.reference('chat_notifications').set({'unread_count': notify_count + 1})
                    st.rerun()

    st.write("---")
    if st.button("🧼 RESET OVERLOAD SIGNAL COUNT", use_container_width=True):
        db.reference('chat_notifications').set({'unread_count': 0})
        st.rerun()

# --- 8.2 ห้องเรดาร์ระบุพิกัดดาวเทียม (GPS TARGET) ---
elif menu_selection == "🛰️ ROOM_02: GPS TARGET":
    st.markdown("<h2 style='color:#00e5ff; font-family:Orbitron; font-size:22px;'>🛰️ ROOM_02 // GPS TARGET LOCKING TRACER</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#527394; font-size:13px;'>**คำอธิบายห้อง:** ห้องเชื่อมโยงระบบพิกัดระบุตำแหน่งผ่านดาวเทียม จะอ่านค่าฮาร์ดแวร์ GPS บนโทรศัพท์มือถือของคุณแบบเรียลไทม์ และรายงานตำแหน่งที่ตั้งปัจจุบันลงแผนที่ภาพถ่ายดาวเทียมเพื่อบันทึกพิกัดค่าย</p>", unsafe_allow_html=True)
    
    satellite_location = get_geolocation()

    if satellite_location and 'coords' in satellite_location:
        st.session_state.user_lat = satellite_location['coords']['latitude']
        st.session_state.user_lon = satellite_location['coords']['longitude']
        offset_range = satellite_location['coords'].get('accuracy', 0)
        
        st.success(f"🎯 TARGET LOCKED: ตรึงพิกัดดาวเทียมเรียบร้อย! (ระดับความคลาดเคลื่อนทางเวกเตอร์: {offset_range:.1f} เมตร)")
        
        c_lat = st.session_state.user_lat
        c_lon = st.session_state.user_lon

        folium_map = folium.Map(
            location=[c_lat, c_lon], 
            zoom_start=18, 
            tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
            attr='Google Satellite Hybrid'
        )

        folium.Marker(
            [c_lat, c_lon], 
            icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
        ).add_to(folium_map)

        st_folium(folium_map, width="100%", height=420)

        if st.button("🛰️ SYNC POSITION TO CLOUD STORAGE", use_container_width=True):
            try:
                db.reference(f'users/{st.session_state.user}').update({
                    'lat': c_lat, 'lon': c_lon, 'ts': time.time()
                })
                st.toast("อัปเดตพิกัดส่งเข้าศูนย์กลางย่อยแล้ว")
            except Exception as e: 
                st.error(f"Datalink Error: {e}")
    else:
        st.warning("🛰️ WAITING FOR SIGNAL: กำลังประมวลผลดักฟังพิกัดจากโมเด็มเครื่อง... โปรดกดยอมรับสิทธิ์การเข้าถึงพิกัดบนบราวเซอร์มือถือด้วยครับ")

# --- 8.3 ห้องถอดรหัสความจริงควอนตัม (TRUTH SCAN) ---
elif menu_selection == "🔮 ROOM_03: TRUTH SCAN":
    st.markdown("<h2 style='color:#ff00de; font-family:Orbitron; font-size:22px;'>🔮 ROOM_03 // THE QUANTUM TRUTH SCANNER TERMINAL</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#527394; font-size:13px;'>**คำอธิบายห้อง:** ห้องประมวลผลค่าความถี่อ้างอิงจากหลักดาราศาสตร์และจันทรคติไทย ป้อนวันเดือนปีเกิดเพื่อวิเคราะห์ระดับคลื่นสมดุลของโครงสร้างชีวิต โดยคำนวณตามจริงไม่มีการโกหกหลอกลวง</p>", unsafe_allow_html=True)
    
    st.write("---")
    # ขยายขอบเขตอายุตั้งแต่ปี 1960 - 2026 เพื่อให้รองรับคนใช้งานได้ทุกช่วงวัยตามต้องการ
    birth_date_input = st.date_input(
        "📅 ENTER CHRONO DATE (ป้อนวัน/เดือน/ปีเกิดที่ต้องการสแกน)", 
        value=None, 
        min_value=date(1960, 1, 1),
        max_value=date(2026, 12, 31)
    )
    
    if birth_date_input:
        scan_res = calculate_quantum_logic(birth_date_input)
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown(f"""
            <div class="truth-card-blue">
                <div style="color:#00e5ff; font-family:'Orbitron'; font-size:12px;">QUANTUM REGISTRY DATA</div>
                <div style="color:#fff; font-size:18px; margin-top:10px;">พิกัดวันเกิด: <b>วัน{scan_res['day']}</b></div>
                <div style="color:#fff; font-size:18px;">จันทรคติ: <b>{scan_res['phase']}</b></div>
                <div style="color:#00e5ff; font-size:18px;">ปีนักษัตร: <b>ปี{scan_res['zodiac']}</b></div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_t2:
            st.markdown(f"""
            <div class="truth-card-pink">
                <div style="color:#ff00de; font-family:'Orbitron'; font-size:12px;">COSMIC INDEX COMPLETED</div>
                <div class="giant-number" style="color:#ff00de; text-shadow:0 0 10px #ff00de;">{scan_res['res']}</div>
                <div style="color:#8ca5bf; font-size:12px; text-align:center;">สมการคณิตศาสตร์: <code>{scan_res['formula']}</code></div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown(f"""
        <div class="matrix-box" style="font-size:14px; color:#fff; border-left:4px solid #39FF14;">
            <b>📡 การวิเคราะห์สภาวะระบบ:</b> {scan_res['type']}<br>
            ความถี่ตัวเลขระดับย่อยถูกถอดรหัสออกมาตามความเป็นจริงของสมดุลรอบวงโคจรดวงจันทร์ ค่านิ่ง เสถียร ไม่มีการแปรผันหลอกลวง
        </div>
        """, unsafe_allow_html=True)
        
        extracted_digits = str(scan_res['res']).replace('.', '')
        st.success(f"🧬 EXTRAPOLATED CORE MATRIX CODE: {extracted_digits[1:3]} || {extracted_digits[2:4]}")
    else:
        st.info("💡 PANEL STANDBY: โปรดป้อนข้อมูลลงในระบบตารางเวลาด้านบนเพื่อทำการสแกนประมวลผล")

# --- 8.4 ห้องพยากรณ์วงจรพิกัดชีวิต (DESTINY ANALYST) ---
elif menu_selection == "🧬 ROOM_04: DESTINY ANALYST":
    st.markdown("<h2 style='color:#39FF14; font-family:Orbitron; font-size:22px;'>🧬 ROOM_04 // FULL-CYCLE DESTINY RADAR SCANNERS</h2>", unsafe_allow_html=True)
    # แก้ไข Syntax บั๊กเครื่องหมายคำพูดซ้อนกันตรงบรรทัดนี้แล้ว
    st.markdown("<p style='color:#527394; font-size:13px;'>**คำอธิบายห้อง:** ห้องจำลองคลื่นความถี่ล่วงหน้าและย้อนหลัง 365 วัน ระบบจะทำการเทียบค่าน้ำหนักดวงดาวเพื่อตรวจหาจุด \"บรรจบ\", \"สะท้อน (Gap 4)\", หรือ \"แยกตัว\" จากค่ารหัสหลักของผู้ใช้อย่างละเอียด</p>", unsafe_allow_html=True)
    
    st.write("---")
    # ขยายขอบเขตอายุตั้งแต่ปี 1960 - 2026 เพื่อให้ผู้ใช้ทุกช่วงอายุเข้ามาคีย์ข้อมูลระบบได้
    base_dob = st.date_input(
        "👤 SELECT CHRONO PROFILE ORIGIN (ป้อนวันเกิดของคุณเพื่อเป็นจุดศูนย์กลาง)", 
        value=None, 
        min_value=date(1960, 1, 1),
        max_value=date(2026, 12, 31),
        key="destiny_dob"
    )
    
    if base_dob:
        origin_profile = calculate_quantum_logic(base_dob)
        
        st.markdown(f"""
        <div class="matrix-box" style="font-size:13px;">
            >> CORE_TARGET_INDEX: {origin_profile['res']} || SYSTEM: {origin_profile['type']}<br>
            >> INITIATING RADAR SWEEP ACROSS 365-DAY TIMELINE WINDOW...
        </div>
        """, unsafe_allow_html=True)
        
        sc_col1, sc_col2 = st.columns(2)
        with sc_col1:
            past_slider = st.slider("⏪ TIME RANGE BACKWARD (สแกนย้อนหลัง/อดีต - วัน)", 0, 365, 180)
        with sc_col2:
            future_slider = st.slider("🔮 TIME RANGE FORWARD (สแกนล่วงหน้า/อนาคต - วัน)", 0, 365, 180)
            
        def execute_timeline_scan(target_code, days_range, direction_mode="future"):
            scanned_records = []
            today_date = date.today()
            
            for index in range(days_range + 1):
                eval_date = today_date + timedelta(days=index) if direction_mode == "future" else today_date - timedelta(days=index)
                day_logic = calculate_quantum_logic(eval_date)
                delta_gap = abs(target_code - day_logic['res'])
                
                status_stamp = "อิสระ"
                if delta_gap < 0.5: status_stamp = "💎 MATRIX_CONVERGE (บรรจบใกล้ชิด)"
                elif 3.8 <= delta_gap <= 4.2: status_stamp = "🌀 SIGNAL_REFLECT (สะท้อน/ดึงดูดสูง)"
                elif delta_gap > 10.0: status_stamp = "🚩 VECTOR_DIVERGE (แยกตัว/อิสระหลุดพ้น)"
                
                if status_stamp != "อิสระ":
                    scanned_records.append({
                        "พิกัดวันที่": eval_date.strftime("%d/%m/%Y"),
                        "ฐานวัน": day_logic['day'],
                        "สถานะคลื่นสัญญาณ": status_stamp,
                        "ระยะห่าง (GAP)": round(delta_gap, 4),
                        "รหัสความถี่วัน": day_logic['res']
                    })
            return pd.DataFrame(scanned_records)
            
        tab_p, tab_f = st.tabs([f"⏩ HISTORICAL SCANNER (อดีต {past_slider} วัน)", f"🔮 PROPHETIC SCANNER (อนาคต {future_slider} วัน)"])
        
        with tab_p:
            past_df = execute_timeline_scan(origin_profile['res'], past_slider, "past")
            if not past_df.empty:
                st.write(f"📊 ตรวจพบพิกัดจุดหักเหความถี่ในอดีตจำนวน {len(past_df)} จุดเชื่อมโยง:")
                st.dataframe(past_df, use_container_width=True, hide_index=True)
            else:
                st.info(">> NO DATA: ไม่พบคลื่นแทรกแซงพิเศษตามขอบเขตในอดีตที่ระบุ")
                
        with tab_f:
            future_df = execute_timeline_scan(origin_profile['res'], future_slider, "future")
            if not future_df.empty:
                st.write(f"📊 ตรวจพบพิกัดจุดบรรจบเหนี่ยวนำในอนาคตจำนวน {len(future_df)} จุดสำคัญ:")
                st.dataframe(future_df, use_container_width=True, hide_index=True)
            else:
                st.info(">> NO DATA: ไม่พบคลื่นแทรกแซงพิเศษตามขอบเขตในอนาคตที่ระบุ")
    else:
        st.info("💡 RADAR OFFLINE: โปรดใส่พิกัดวันเกิดเพื่อเปิดระบบกวาดสัญญาณเรดาร์วงจรรหัสชีวิต")

# --- 8.5 ห้องเครื่องเล่นเพลงและคลื่นเสียง (SOUND SYSTEM) ---
elif menu_selection == "🎵 ROOM_05: SOUND SYSTEM":
    st.markdown("<h2 style='color:#00e5ff; font-family:Orbitron; font-size:22px;'>🎵 ROOM_05 // LOCAL ARCHIVE MP3 AUDIO PLAYER</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#527394; font-size:13px;'>**คำอธิบายห้อง:** ระบบเครื่องเล่นเพลงที่คัดกรองไฟล์นามสกุล `.mp3` ทั้งหมดในโฟลเดอร์ปฏิบัติการของแอปพลิเคชัน เพื่อส่งคลื่นสัญญาณเสียงปรับสภาพแวดล้อมทางสมอง</p>", unsafe_allow_html=True)
    
    execution_directory = os.path.dirname(__file__) if __file__ else "."
    scanned_mp3_files = [file for file in os.listdir(execution_directory) if file.endswith('.mp3')]
    
    if not scanned_mp3_files:
        st.error("⚠️ FILE NOT FOUND: ไม่พบไฟล์เสียงเพลงนามสกุล .mp3 บรรจุอยู่ในโฟลเดอร์เดียวกันกับตัวโปรแกรมนี้เลยเพื่อน! กรุณานำไฟล์เพลงมาวางคู่กับไฟล์โค้ดนี้")
    else:
        st.markdown("<p style='color:#fff; font-size:16px;'>🎚️ SELECT AUDIO WAVEFORM (คลิกเลือกไฟล์เพลงเพื่อส่งสัญญาณ):</p>", unsafe_allow_html=True)
        
        user_picked_song = st.selectbox("AUDIO_FILE_SELECT", options=scanned_mp3_files, label_visibility="collapsed")
        
        if user_picked_song:
            target_audio_fullpath = os.path.join(execution_directory, user_picked_song)
            
            st.markdown(f"""
            <div style="border: 4px solid #00e5ff; border-radius:10px; padding:20px; background-color:#020509; text-align:center; box-shadow:0 0 15px rgba(0,229,255,0.3); margin:15px 0;">
                <div style="color:#ff00de; font-family:'Orbitron'; font-size:20px; font-weight:bold;">NOW BROADCASTING // {user_picked_song}</div>
            </div>
            """, unsafe_allow_html=True)
            
            try:
                with open(target_audio_fullpath, "rb") as audio_file:
                    encoded_audio_bytes = base64.b64encode(audio_file.read()).decode()
                audio_component_markup = f'<audio controls autoplay style="width: 100%; margin-top:10px;"><source src="data:audio/mp3;base64,{encoded_audio_bytes}" type="audio/mp3"></audio>'
                st.markdown(audio_component_markup, unsafe_allow_html=True)
            except Exception as player_error:
                st.error(f"เกิดข้อผิดพลาดทางระบบควบคุมเสียง: {player_error}")

# =========================================================
# 9. FOOTER COMMAND CORE MANIFEST
# =========================================================
st.write("---")
st.markdown("<p style='text-align: center; color: #527394; font-family:sans-serif; font-weight:bold; font-size:14px; letter-spacing:1px;'>สโลแกนระบบ: 'อยู่นิ่งๆ ไม่เจ็บตัว' || BASE SYSTEM OPERATIONAL SUCCESS</p>", unsafe_allow_html=True)
