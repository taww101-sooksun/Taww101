import streamlit as st

# =========================================================
# 1. INITIALIZATION & HIGH-LEVEL NEON CYBERPUNK UI
# =========================================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")

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

def inject_cyberpunk_mainframe():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Sarabun:wght@300;600&display=swap');
            
            .stApp { 
                background: radial-gradient(circle at 50% 50%, #03070a 0%, #010204 100%) !important;
                font-family: 'Sarabun', sans-serif;
                color: #e0e0e0;
            }
            
            #MainMenu, footer, header { visibility: hidden; }
            .stApp { top: -60px; }
            
            [data-testid="stSidebar"] {
                background-color: #03060a !important;
                border-right: 3px solid #39FF14 !important;
                box-shadow: 5px 0 15px rgba(57, 255, 20, 0.1);
            }
            
            .stRadio>div { gap: 15px !important; }
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
                height: 55px;
            }
            .stButton>button:hover {
                border-color: #39FF14 !important;
                color: #39FF14 !important;
                text-shadow: 0 0 5px #39FF14;
                box-shadow: 0 0 15px rgba(57, 255, 20, 0.4);
            }
            
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
            
            .giant-number {
                font-family: 'Orbitron', sans-serif;
                font-size: 38px !important;
                font-weight: bold;
                text-align: center;
                margin: 10px 0;
            }
        </style>
    """, unsafe_allow_html=True)

inject_cyberpunk_mainframe()

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
# 3. CORE LOGIC ENGINE
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
# 5. MAIN GATEWAY: AUTHENTICATION
# =========================================================
if not st.session_state.logged_in:
    header_gate = """
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
# 6. HEADER COMMAND CENTER
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
        >> MATRIX_LAT: {st.session_state.user_lat if st.session_state.user_lat else 'NULL'}<br>
        >> MATRIX_LON: {st.session_state.user_lon if st.session_state.user_lon else 'NULL'}<br>
        >> SLOGAN_HASH: "อยู่นิ่งๆ ไม่เจ็บตัว"
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    menu_selection = st.radio(
        "NAVIGATION_SYSTEM",
        ["💬 ROOM_01: GLOBAL COMMS", "🛰️ ROOM_02: GPS TARGET", "🔮 ROOM_03: TRUTH SCAN", "🧬 ROOM_04: DESTINY ANALYST", "🎵 ROOM_05: SOUND SYSTEM"],
        key="main_navigation"
    )
    
    st.write("---")
    if st.button("🔴 DISCONNECT (LOGOUT)"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

# =========================================================
# 8. HARDWARE WORKSPACE CAPABILITIES
# =========================================================
main_content_area = st.empty()

with main_content_area.container():
    # --- 8.1 ห้องแชทวิทยุกลาง (GLOBAL COMMS) ---
    if menu_selection == "💬 ROOM_01: GLOBAL COMMS":
        st.markdown("<h2 style='color:#39FF14; font-family:Orbitron; font-size:22px;'>💬 ROOM_01 // GLOBAL CHATROOM TELEMETRY</h2>", unsafe_allow_html=True)
        st.markdown("<p style='color:#527394; font-size:13px;'>**คำอธิบายห้อง:** ห้องสื่อสารเครือข่ายย่อยแบบเรียลไทม์ ใช้รับส่งข้อความคลื่นวิทยุและพยานหลักฐานรูปภาพร่วมกับหน่วยข้อมูลอื่น ข้อมูลจะอัปเดตทันทีผ่านระบบ Realtime Datalink</p>", unsafe_allow_html=True)
        
        chat_mainframe_html = f"""
        <style>
            #screen-frame {{
                background: rgba(2,5,10,0.98); border: 2px solid {theme_green}; border-radius: 10px;
                height: 380px; overflow-y: auto; padding: 12px; display: flex; flex-direction: column;
            }}
            .bubble {{ padding: 10px 14px; border-radius: 8px; margin: 6px 0; max-width: 85%; color: #fff; font-size: 14px; }}
            .me {{ background: {theme_green}12; border-right: 4px solid {theme_green}; align-self: flex-end; }}
            .others {{ background: #101620; border-left: 4px solid #ff00de; align-self: flex-start; }}
            .notif-capsule {{ background: #0c141c; color: #527394; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-family: 'Orbitron'; }}
            .signal-alert {{ background: #ff0055 !important; color: white !important; font-weight: bold; }}
        </style>

        <div id="screen-frame">
            <div style="display:flex; justify-content:space-between; margin-bottom:10px; border-bottom: 1px solid #101a24; padding-bottom: 5px;">
                <span style="color:{theme_green}; font-family:'Orbitron'; font-size:10px;">📡 DATA_STREAM_OPEN</span>
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
                
                let block = `<div style="font-size:10px; color:#527394; font-family:'Orbitron';">${{data.user}}</div>`;
                if(data.text) block += `<div>${{data.text}}</div>`;
                if(data.img) block += `<img src="data:image/png;base64,${{data.img}}" style="max-width:100%; border-radius:6px; margin-top:6px;">`;
                
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
        
        satellite_location = get_geolocation()
        if satellite_location and 'coords' in satellite_location:
            st.session_state.user_lat = satellite_location['coords']['latitude']
            st.session_state.user_lon = satellite_location['coords']['longitude']
            offset_range = satellite_location['coords'].get('accuracy', 0)
            st.success(f"🎯 TARGET LOCKED: ตรึงพิกัดดาวเทียมเรียบร้อย! (ความคลาดเคลื่อน: {offset_range:.1f} เมตร)")
            
            folium_map = folium.Map(location=[st.session_state.user_lat, st.session_state.user_lon], zoom_start=18)
            folium.Marker([st.session_state.user_lat, st.session_state.user_lon], icon=folium.Icon(color='red')).add_to(folium_map)
            st_folium(folium_map, width="100%", height=420)
        else:
            st.warning("🛰️ WAITING FOR SIGNAL: โปรดกดเปิดสิทธิ์ยอมรับ GPS บนหน้าจอบราวเซอร์มือถือด้วยครับ")

    # --- 8.3 ห้องถอดรหัสความจริงควอนตัม (TRUTH SCAN) ---
    elif menu_selection == "🔮 ROOM_03: TRUTH SCAN":
        st.markdown("<h2 style='color:#ff00de; font-family:Orbitron; font-size:22px;'>🔮 ROOM_03 // THE QUANTUM TRUTH SCANNER TERMINAL</h2>", unsafe_allow_html=True)
        
        birth_date_input = st.date_input("📅 ENTER CHRONO DATE (ป้อนวัน/เดือน/ปีเกิด)", value=None, min_value=date(1960, 1, 1), max_value=date(2026, 12, 31))
        if birth_date_input:
            scan_res = calculate_quantum_logic(birth_date_input)
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.markdown(f'<div class="truth-card-blue">วันเกิด: <b>วัน{scan_res["day"]}</b><br>จันทรคติ: <b>{scan_res["phase"]}</b></div>', unsafe_allow_html=True)
            with col_t2:
                st.markdown(f'<div class="truth-card-pink"><div class="giant-number">{scan_res["res"]}</div></div>', unsafe_allow_html=True)

    # --- 8.4 ห้องพยากรณ์วงจรพิกัดชีวิต (DESTINY ANALYST) ---
    elif menu_selection == "🧬 ROOM_04: DESTINY ANALYST":
        st.markdown("<h2 style='color:#39FF14; font-family:Orbitron; font-size:22px;'>🧬 ROOM_04 // FULL-CYCLE DESTINY RADAR SCANNERS</h2>", unsafe_allow_html=True)
        base_dob = st.date_input("👤 SELECT CHRONO PROFILE ORIGIN", value=None, min_value=date(1960, 1, 1), max_value=date(2026, 12, 31), key="destiny_dob")
        if base_dob:
            st.info("กำลังเปิดระบบเรดาร์กวาดข้อมูล...")

    # --- 8.5 ห้องเครื่องเล่นเพลงและคลื่นเสียง (SOUND SYSTEM) ---
    elif menu_selection == "🎵 ROOM_05: SOUND SYSTEM":
        st.markdown("<h2 style='color:#00e5ff; font-family:Orbitron; font-size:22px;'>🎵 ROOM_05 // LOCAL ARCHIVE MP3 AUDIO PLAYER</h2>", unsafe_allow_html=True)
        execution_directory = os.path.dirname(__file__) if __file__ else "."
        scanned_mp3_files = [file for file in os.listdir(execution_directory) if file.endswith('.mp3')]
        
        if not scanned_mp3_files:
            st.error("⚠️ ไม่พบไฟล์เสียงเพลงนามสกุล .mp3 ในเครื่องเลยเพื่อน")
        else:
            user_picked_song = st.selectbox("เลือกเพลง:", options=scanned_mp3_files)
            if user_picked_song:
                st.success(f"กำลังเล่นเพลง: {user_picked_song}")

# =========================================================
# 9. FOOTER
# =========================================================
st.write("---")
st.markdown("<p style='text-align: center; color: #527394;'>สโลแกนระบบ: 'อยู่นิ่งๆ ไม่เจ็บตัว'</p>", unsafe_allow_html=True)
