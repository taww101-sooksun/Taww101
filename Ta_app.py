import streamlit as st
import base64
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
            
            /* สไตล์สำหรับกล่องวิทยุแอนิเมชัน */
            .matrix-box {
                background-color: #04070a;
                border: 2px solid #101a24;
                padding: 12px;
                border-radius: 8px;
                font-family: 'Orbitron', monospace;
                font-size: 11px;
                color: #527394;
                line-height: 1.4;
                margin-bottom: 15px;
                overflow: hidden;
            }
            
            /* สไตล์สำหรับปุ่มแท็บเลือกห้องด้านบนให้เหมาะกับมือถือ */
            .stTabs [data-baseweb="tab-list"] {
                gap: 8px !important;
                background-color: #020508 !important;
                padding: 5px !important;
                border-radius: 10px !important;
                border: 1px solid #101a24 !important;
                overflow-x: auto !important; /* เลื่อนซ้ายขวาได้ถ้าจอแคบ */
            }
            .stTabs [data-baseweb="tab"] {
                height: 45px !important;
                white-space: nowrap !important;
                background-color: #060b10 !important;
                border: 2px solid #101a24 !important;
                border-radius: 8px !important;
                color: #00e5ff !important;
                font-weight: bold !important;
                font-size: 14px !important;
                padding: 0px 15px !important;
            }
            .stTabs [aria-selected="true"] {
                background-color: rgba(57, 255, 20, 0.05) !important;
                border-color: #39FF14 !important;
                color: #39FF14 !important;
                box-shadow: 0 0 10px rgba(57, 255, 20, 0.2) !important;
            }
            
            /* ปุ่มกดส่งสัญญาณ */
            .stButton>button {
                font-size: 16px !important;
                font-weight: bold !important;
                padding: 10px !important;
                border-radius: 8px !important;
                background: linear-gradient(135deg, #0b151f 0%, #04080c 100%) !important;
                border: 2px solid #39FF14 !important;
                color: #39FF14 !important;
                text-shadow: 0 0 5px #39FF14;
                transition: 0.3s;
                width: 100%;
                height: 50px;
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
    .panel-title {{ font-family: 'Orbitron', sans-serif; font-weight: bold; font-size: 20px; letter-spacing: 2px; margin-left: 15px; animation: text_wink 2s infinite; }}
</style>
<div class="panel-container">
    {f'<img src="data:image/png;base64,{logo_base64}" class="panel-logo">' if logo_base64 else ''}
    <span class="panel-title">SYNAPSE SYSTEM</span>
</div>
"""
components.html(header_mainframe, height=95)

# แสดงสถานะ Operator และสโลแกนไว้ด้านบนสุดของจอหลักเลย เพื่อความสะดวกบนมือถือ
st.markdown(f"""
<div class="matrix-box">
    AGENT: <b>{st.session_state.user}</b> | STATUS: <b>ONLINE</b> | สโลแกน: <b>"อยู่นิ่งๆ ไม่เจ็บตัว"</b>
</div>
""", unsafe_allow_html=True)

# =========================================================
# 7. MAIN NAVIGATION TABS (แก้ปัญหาจอมือถือ ไม่มีปุ่มกด)
# =========================================================
# สร้างแท็บกดเลือกห้องอันใหญ่ๆ ไว้ตรงกลางหน้าจอหลักเลย จิ้มเปลี่ยนหน้าได้ทันที!
room_tabs = st.tabs(["💬 ROOM 01", "🛰️ ROOM 02", "🔮 ROOM 03", "🧬 ROOM 04", "🎵 ROOM 05"])

# --- แท็บที่ 1: ROOM_01 (GLOBAL COMMS) ---
with room_tabs[0]:
    st.markdown("<h3 style='color:#39FF14; font-family:Orbitron;'>💬 ROOM_01 // GLOBAL CHATROOM TELEMETRY</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#527394; font-size:12px;'>ห้องสื่อสารเครือข่ายย่อยแบบเรียลไทม์ ข้อมูลจะอัปเดตทันทีผ่าน Realtime Datalink</p>", unsafe_allow_html=True)
    
    chat_mainframe_html = f"""
    <style>
        #screen-frame {{
            background: rgba(2,5,10,0.98); border: 2px solid {theme_green}; border-radius: 10px;
            height: 350px; overflow-y: auto; padding: 12px; display: flex; flex-direction: column;
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
    components.html(chat_mainframe_html, height=370)

    in_msg = st.text_input("INPUT TRANSMISSION", placeholder="พิมพ์ข้อความคลื่นเสียง...", label_visibility="collapsed", key="chat_tx")
    in_file = st.file_uploader("UPLOAD DATA", type=['png','jpg','jpeg'], label_visibility="collapsed", key="chat_img")
    
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

# --- แท็บที่ 2: ROOM_02 (GPS TARGET) ---
with room_tabs[1]:
    st.markdown("<h3 style='color:#00e5ff; font-family:Orbitron;'>🛰️ ROOM_02 // GPS TARGET LOCKING TRACER</h3>", unsafe_allow_html=True)
    satellite_location = get_geolocation()
    if satellite_location and 'coords' in satellite_location:
        st.session_state.user_lat = satellite_location['coords']['latitude']
        st.session_state.user_lon = satellite_location['coords']['longitude']
        st.success(f"🎯 TARGET LOCKED: พิกัด [{st.session_state.user_lat}, {st.session_state.user_lon}]")
        
        folium_map = folium.Map(location=[st.session_state.user_lat, st.session_state.user_lon], zoom_start=18)
        folium.Marker([st.session_state.user_lat, st.session_state.user_lon], icon=folium.Icon(color='red')).add_to(folium_map)
        st_folium(folium_map, width="100%", height=350)
    else:
        st.warning("🛰️ WAITING FOR SIGNAL: โปรดกดอนุญาตให้ระบบเข้าถึง GPS บนบราวเซอร์มือถือด้วยครับ")

# --- แท็บที่ 3: ROOM_03 (TRUTH SCAN) ---
with room_tabs[2]:
    st.markdown("<h3 style='color:#ff00de; font-family:Orbitron;'>🔮 ROOM_03 // THE QUANTUM TRUTH SCANNER</h3>", unsafe_allow_html=True)
    birth_date_input = st.date_input("📅 ENTER CHRONO DATE (ป้อนวันเกิด)", value=None, min_value=date(1960, 1, 1), max_value=date(2026, 12, 31))
    if birth_date_input:
        scan_res = calculate_quantum_logic(birth_date_input)
        st.markdown(f'<div class="truth-card-blue">วันเกิด: <b>วัน{scan_res["day"]} ({scan_res["zodiac"]})</b><br>จันทรคติ: <b>{scan_res["phase"]}</b></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="truth-card-pink"><div class="giant-number">{scan_res["res"]}</div><div style="text-align:center;font-size:12px;color:#527394;">{scan_res["type"]}</div></div>', unsafe_allow_html=True)

# --- แท็บที่ 4: ROOM_04 (DESTINY ANALYST) ---
with room_tabs[3]:
    st.markdown("<h3 style='color:#39FF14; font-family:Orbitron;'>🧬 ROOM_04 // DESTINY RADAR SCANNERS</h3>", unsafe_allow_html=True)
    base_dob = st.date_input("👤 SELECT CHRONO PROFILE ORIGIN", value=None, min_value=date(1960, 1, 1), max_value=date(2026, 12, 31), key="destiny_dob")
    if base_dob:
        st.info("ระบบเรดาร์กำลังประมวลผลฐานข้อมูล...")

# --- แท็บที่ 5: ROOM_05 (SOUND SYSTEM) ---
with room_tabs[4]:
    st.markdown("<h3 style='color:#00e5ff; font-family:Orbitron;'>🎵 ROOM_05 // LOCAL ARCHIVE MP3 PLAYER</h3>", unsafe_allow_html=True)
    execution_directory = "."
    scanned_mp3_files = [file for file in os.listdir(execution_directory) if file.endswith('.mp3')]
    
    if not scanned_mp3_files:
        st.error("⚠️ ไม่พบไฟล์เพลง .mp3 ใน Directory ของระบบ")
    else:
        user_picked_song = st.selectbox("เลือกไฟล์เสียงเพื่อถอดรหัสสัญญาณ:", options=scanned_mp3_files)
        if user_picked_song:
            st.success(f"🔊 LOADING: {user_picked_song}")

# =========================================================
# 8. SYSTEM DISCONNECT (ปุ่มล็อกเอาต์ด้านล่างสุดหน้าหลัก)
# =========================================================
st.write("---")
if st.button("🔴 DISCONNECT SYSTEM (ออกจากระบบ)", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# ==========================================
# ส่วนที่ 1: การตั้งค่าหน้าจอและ CSS (กู้คืนสีสัน Neon ขั้นสุด)
# ==========================================

st.set_page_config(page_title="Synapse", layout="centered")

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_base64 = get_base64_image("logo1.png")
logo_html_link = f"data:image/png;base64,{logo_base64}" if logo_base64 else ""

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    .stApp {{ background-color: #000; }}

    /* Logo ตรงกลางพร้อมแสง Neon หมุนสลับสี */
    .block-container::before {{
        content: "";
        position: absolute;
        top: 10px; left: 50%;
        transform: translateX(-50%);
        width: 100px; height: 100px;
        background-image: url("{logo_html_link}");
        background-size: contain;
        background-repeat: no-repeat;
        z-index: 999;
        filter: drop-shadow(0 0 10px #ff00de);
        animation: logo-glow 4s infinite alternate;
    }}

    @keyframes logo-glow {{
        0% {{ filter: drop-shadow(0 0 10px #ff00de); transform: translateX(-50%) scale(1); }}
        50% {{ filter: drop-shadow(0 0 25px #00f3ff); transform: translateX(-50%) scale(1.1); }}
        100% {{ filter: drop-shadow(0 0 10px #ff8c00); transform: translateX(-50%) scale(1); }}
    }}

    .neon-title {{
        font-family: 'Orbitron', sans-serif;
        color: #fff;
        text-align: center;
        text-shadow: 0 0 10px #ff00de, 0 0 20px #00f3ff;
        font-size: 1.6rem;
        margin-top: 110px;
        letter-spacing: 3px;
        animation: text-flicker 2s infinite;
    }}
    @keyframes text-flicker {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.8; }}
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="neon-title">SYNAPSE</h1>', unsafe_allow_html=True)

# ==========================================
# ส่วนที่ 2: HTML/JS - ระบบเล่นต่อเนื่อง + สีสันสะบัด
# ==========================================

html_code = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: transparent; color: white; overflow: hidden; font-family: 'Inter', sans-serif; }
        .neon-card { border: 2px solid #333; background: rgba(0,0,0,0.9); box-shadow: 0 0 30px rgba(255,0,222,0.2); }
        
        /* กราฟเสียงสีรุ้งสะบัด */
        .visualizer-box { height: 150px; background: #050505; border-radius: 15px; border: 1px solid #222; }
        
        .deck { padding: 15px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px; transition: 0.5s; }
        .deck-active { border: 1px solid #00f3ff; box-shadow: 0 0 15px #00f3ff; background: rgba(0,243,255,0.05); }
        
        /* ปุ่มสไตล์ Cyberpunk */
        .btn-mix { 
            background: linear-gradient(45deg, #ff00de, #00f3ff);
            color: white; font-weight: bold; padding: 12px; border-radius: 10px;
            text-transform: uppercase; letter-spacing: 2px; transition: 0.3s;
            box-shadow: 0 0 15px rgba(255,0,222,0.4);
        }
        .btn-mix:hover { transform: scale(1.05); box-shadow: 0 0 25px rgba(0,243,255,0.6); }
        
        .progress-bar { height: 6px; background: #222; border-radius: 10px; overflow: hidden; }
        .progress-inner { height: 100%; width: 0%; background: linear-gradient(90deg, #ff00de, #ff8c00); }
    </style>
</head>
<body>
    <div class="max-w-md mx-auto p-4 neon-card rounded-3xl">
        <canvas id="scope" class="visualizer-box w-full mb-4"></canvas>

        <div id="cardA" class="deck">
            <div class="flex justify-between text-[10px] mb-2">
                <span id="labelA" class="text-pink-500 font-bold">DECK A</span>
                <span id="timeA" class="font-mono">00:00</span>
            </div>
            <input type="file" id="inA" class="hidden" onchange="handleFile(this.files[0], 'A')">
            <button onclick="document.getElementById('inA').click()" class="text-[10px] border border-gray-600 px-3 py-1 rounded">LOAD A</button>
            <div id="nameA" class="text-[11px] mt-1 truncate text-gray-400">No Song</div>
            <div class="progress-bar mt-2"><div id="barA" class="progress-inner"></div></div>
        </div>

        <div id="cardB" class="deck">
            <div class="flex justify-between text-[10px] mb-2">
                <span id="labelB" class="text-cyan-400 font-bold">DECK B</span>
                <span id="timeB" class="font-mono">00:00</span>
            </div>
            <input type="file" id="inB" class="hidden" onchange="handleFile(this.files[0], 'B')">
            <button onclick="document.getElementById('inB').click()" class="text-[10px] border border-gray-600 px-3 py-1 rounded">LOAD B</button>
            <div id="nameB" class="text-[11px] mt-1 truncate text-gray-400">No Song</div>
            <div class="progress-bar mt-2"><div id="barB" class="progress-inner" style="background: #00f3ff;"></div></div>
        </div>

        <button onclick="startMix()" class="btn-mix w-full mt-2">🔥 START AUTO-MIX</button>
        <div id="status" class="text-[10px] text-center mt-3 text-gray-500 uppercase tracking-widest">System Ready</div>
    </div>

    <script>
        let ctx, analyser, songA, songB, gainA, gainB, sourceA, sourceB;
        let active = 'A', isPlaying = false, data;

        function init() {
            if (!ctx) {
                ctx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = ctx.createAnalyser();
                analyser.fftSize = 256;
                data = new Uint8Array(analyser.frequencyBinCount);
                render();
            }
        }

        async function handleFile(file, side) {
            init();
            document.getElementById('name'+side).innerText = "Loading...";
            const buffer = await ctx.decodeAudioData(await file.arrayBuffer());
            if(side === 'A') songA = buffer; else songB = buffer;
            document.getElementById('name'+side).innerText = file.name;
        }

        function render() {
            requestAnimationFrame(render);
            if(!analyser) return;
            analyser.getByteFrequencyData(data);
            const can = document.getElementById('scope');
            const c = can.getContext('2d');
            c.clearRect(0,0,can.width,can.height);
            
            let bw = (can.width / data.length) * 2.5;
            let x = 0;
            for(let i=0; i<data.length; i++) {
                let h = (data[i]/255) * can.height;
                let hue = (i * 3) + (Date.now() / 50) % 360;
                c.fillStyle = `hsl(${hue}, 100%, 50%)`;
                c.fillRect(x, can.height - h, bw - 1, h);
                x += bw;
            }
            updateEngine();
        }

        function startMix() {
            if(!songA || !songB) return alert("อาจารย์ครับ โหลดเพลงให้ครบ A/B ก่อน!");
            if(isPlaying) return;
            
            sourceA = ctx.createBufferSource(); sourceA.buffer = songA;
            gainA = ctx.createGain(); 
            sourceA.connect(gainA).connect(analyser).connect(ctx.destination);
            
            sourceB = ctx.createBufferSource(); sourceB.buffer = songB;
            gainB = ctx.createGain(); gainB.gain.value = 0;
            sourceB.connect(gainB).connect(analyser).connect(ctx.destination);
            
            sourceA.loop = true; sourceB.loop = true;
            sourceA.start(0); sourceB.start(0);
            isPlaying = true;
            document.getElementById('status').innerText = "Playing: Deck A";
            document.getElementById('cardA').classList.add('deck-active');
        }

        function updateEngine() {
            if(!isPlaying) return;
            let now = ctx.currentTime;
            
            // ระบบเช็กเวลาและ Auto-Crossfade เมื่อเพลงใกล้จบ (สมมติเล่น Loop)
            // ในที่นี้ใช้การอัปเดต Progress Bar และ UI
            updateUI('A', songA, gainA);
            updateUI('B', songB, gainB);
        }

        function updateUI(s, buffer, gain) {
            let bar = document.getElementById('bar'+s);
            let time = document.getElementById('time'+s);
            // จำลองการเดินของเวลาใน Loop
            let p = (ctx.currentTime % buffer.duration) / buffer.duration;
            bar.style.width = (p * 100) + "%";
            
            let rem = buffer.duration - (ctx.currentTime % buffer.duration);
            let m = Math.floor(rem/60), sec = Math.floor(rem%60);
            time.innerText = (m<10?'0':'')+m+":"+(sec<10?'0':'')+sec;

            // AUTO CROSSFADE LOGIC: เมื่อเหลือ 5 วินาทีสุดท้าย
            if(active === s && rem < 5) {
                crossfade();
            }
        }

        function crossfade() {
            let next = (active === 'A' ? 'B' : 'A');
            let now = ctx.currentTime;
            let dur = 4; // วินาทีในการ Fade
            
            if(active === 'A') {
                gainA.gain.linearRampToValueAtTime(0, now + dur);
                gainB.gain.linearRampToValueAtTime(1, now + dur);
                document.getElementById('cardA').classList.remove('deck-active');
                document.getElementById('cardB').classList.add('deck-active');
            } else {
                gainB.gain.linearRampToValueAtTime(0, now + dur);
                gainA.gain.linearRampToValueAtTime(1, now + dur);
                document.getElementById('cardB').classList.remove('deck-active');
                document.getElementById('cardA').classList.add('deck-active');
            }
            active = next;
            document.getElementById('status').innerText = "Auto-Mixing to: Deck " + active;
        }
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=650)

st.markdown("""
<div style='text-align: center; color: #555; font-size: 12px; font-family: "Orbitron"; letter-spacing: 2px;'>
    อยู่นิ่งๆ ไม่เจ็บตัว | AUTO-MIX ENGINE v5.0 | © 2026
</div>
""", unsafe_allow_html=True)
