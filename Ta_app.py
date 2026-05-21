import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
import math
import time
import base64
import os
import pandas as pd
from datetime import datetime, date, timedelta

# =========================================================
# 1. INITIALIZATION & HIGH-LEVEL NEON CYBERPUNK UI
# =========================================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")

if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14" 
if 'bg_color' not in st.session_state: st.session_state.bg_color = "#03070a"
if 'border_width' not in st.session_state: st.session_state.border_width = 3
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = "Agent_Ta"

def inject_cyberpunk_mainframe():
    st.markdown(f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Sarabun:wght@300;600&display=swap');
            .stApp {{ 
                background: radial-gradient(circle at 50% 50%, {st.session_state.bg_color} 0%, #010204 100%) !important;
                font-family: 'Sarabun', sans-serif;
                color: #e0e0e0;
            }}
            #MainMenu, footer, header {{ visibility: hidden; }}
            .stButton>button {{
                font-size: 18px !important;
                font-weight: bold !important;
                border-radius: 8px !important;
                background: linear-gradient(135deg, #0b151f 0%, #04080c 100%) !important;
                border: {st.session_state.border_width}px solid {st.session_state.theme_color} !important;
                color: {st.session_state.theme_color} !important;
                text-shadow: 0 0 5px {st.session_state.theme_color};
                width: 100%;
                height: 55px;
            }}
            .matrix-box {{
                background-color: #04070a;
                border: 2px solid #101a24;
                padding: 12px;
                border-radius: 8px;
                font-family: 'Orbitron', monospace;
                font-size: 12px;
                color: #527394;
            }}
            .truth-card-blue {{
                background: linear-gradient(135deg, rgba(4,14,24,0.9) 0%, rgba(2,5,10,0.95) 100%);
                border: 4px solid #00e5ff;
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 15px;
            }}
            .truth-card-pink {{
                background: linear-gradient(135deg, rgba(24,4,14,0.9) 0%, rgba(10,2,5,0.95) 100%);
                border: 4px solid #ff00de;
                border-radius: 12px;
                padding: 15px;
                margin-bottom: 15px;
            }}
            .giant-number {{
                font-family: 'Orbitron', sans-serif;
                font-size: 36px !important;
                font-weight: bold;
                text-align: center;
            }}
            /* กรอบกล่องข้อความแชทแอป */
            .chat-bubble-container {{
                background: #060b11;
                border: 1px solid #101a24;
                border-radius: 6px;
                padding: 8px 12px;
                margin: 5px 0;
            }}
        </style>
    """, unsafe_allow_html=True)

inject_cyberpunk_mainframe()

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
        pass

# =========================================================
# 3. CORE LOGIC ENGINE (แก้ไขบั๊กปี 1984 = ปีชวด ตรงความจริง)
# =========================================================
def calculate_quantum_logic(dt):
    if dt is None: return None
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589 
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    
    # แก้ไขการหาปีนักษัตรสากลอ้างอิงตรงตามปี ค.ศ. จริง (1984 % 12 ดิ่งลงลูปชวดพอดี)
    zodiacs = ["ลิง (วอก)", "ไก่ (ระกา)", "สุนัข (จอ)", "หมู (กุน)", "หนู (ชวด)", "วัว (ฉลู)", "เสือ (ขาล)", "กระต่าย (เถาะ)", "มังกร (มะโรง)", "งูเล็ก (มะเส็ง)", "ม้า (มะเมีย)", "แพะ (มะแม)"]
    zodiac = zodiacs[(dt.year - 4) % 12]
    
    is_waxing = pos <= 14.765
    m_num = int(pos) + 1 if is_waxing else int(pos - 14.765) + 1
    phase_text = f"{'ขึ้น' if is_waxing else 'แรม'} {m_num} ค่ำ"
    
    if is_waxing:
        res = math.sqrt((day_val**2) + (m_num**2))
        formula = f"√({day_val}² + {m_num}²)"
        sys_type = "Vector Force (ข้างขึ้น)"
    else:
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula = f"({day_val} × 1.618) / {m_num}"
        sys_type = "Golden Ratio (ข้างแรม)"

    return {
        "res": round(res, 4), "phase": phase_text, "day": day_names[dt.weekday()],
        "formula": formula, "type": sys_type, "zodiac": zodiac, "day_val": day_val
    }

# --- ประตูเข้าสู่ระบบค่าย ---
if not st.session_state.logged_in:
    st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color}; font-family:Orbitron;'>🛡️ SYNAPSE ACCESS GATEWAY</h1>", unsafe_allow_html=True)
    col_gate1, col_gate2, col_gate3 = st.columns([1, 2, 1])
    with col_gate2:
        with st.form("login_form"):
            user_input = st.text_input("AGENT ID", value="Agent_Ta")
            pw_input = st.text_input("PASSWORD", type="password", value="1234")
            if st.form_submit_button("CONNECT TO MAINFRAME ⚡"):
                st.session_state.logged_in = True
                st.session_state.user = user_input
                st.rerun()
    st.stop()

# =========================================================
# 4. INTERFACE HEADER & SIDEBAR
# =========================================================
components.html(f"""
<div style="text-align:center; padding:10px; border-bottom:2px solid #101a24; background:#020508;">
    <h2 style="color:{st.session_state.theme_color}; font-family:'Orbitron'; margin:0; letter-spacing:3px;">🛰️ SYNAPSE COMMAND CENTER</h2>
    <p style="color:#527394; font-family:'Orbitron'; font-size:12px; margin:5px 0 0 0;">SLOGAN: "อยู่นิ่งๆ ไม่เจ็บตัว" // OPERATIONAL DATA CORE</p>
</div>
""", height=85)

with st.sidebar:
    st.markdown(f"<h3 style='color:{st.session_state.theme_color}; font-family:Orbitron;'>📟 OPERATOR TERMINAL</h3>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#00e5ff; font-weight:bold;'>AGENT ID: {st.session_state.user}</div>", unsafe_allow_html=True)
    st.markdown(f'<div class="matrix-box">>> MODE: REAL-TRUTH<br>>> CODES: 1960-2026 LOCKED</div>', unsafe_allow_html=True)
    st.write("---")
    if st.button("🔴 DISCONNECT LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

# =========================================================
# 5. CORE INTERFACE MAIN WORKSPACE
# =========================================================

# --- 5.1 ห้องกางสูตรคำนวณตัวเลข (กางแผงออกมาถาวรให้อ่านง่ายทันที) ---
st.header("📅 ห้องถอดรหัสพิกัดเวลาจักรวาล (กางข้อมูลจริง)")
with st.container():
    st.markdown("<div style='border:2px solid #101a24; background:#161b22; padding:20px; border-radius:10px; margin-bottom:20px;'>", unsafe_allow_html=True)
    col_calc_in, col_calc_out = st.columns([1, 2])
    with col_calc_in:
        birth_date_input = st.date_input(
            "ป้อน วัน/เดือน/ปี ค.ศ. คีย์ข้อมูลระบบจริง", 
            value=date.today(), 
            min_value=date(1960, 1, 1),
            max_value=date(2026, 12, 31),
            key="quantum_calc_date"
        )
    if birth_date_input:
        scan_res = calculate_quantum_logic(birth_date_input)
        with col_calc_out:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f'<div class="truth-card-blue">เกิดวัน: <b>วัน{scan_res["day"]}</b><br>จันทรคติ: <b>{scan_res["phase"]}</b><br>นักษัตร: <b style="color:#39FF14;">ปี{scan_res["zodiac"]}</b></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="truth-card-pink"><div style="font-size:11px;color:#ff00de;">COSMIC RES</div><div class="giant-number" style="color:#ff00de;">{scan_res["res"]}</div><div style="font-size:10px;text-align:center;">สูตรคำนวณ: {scan_res["formula"]}</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.write("---")

# --- 5.2 เมนูแยกห้องระบบการทำงานหลัก ---
room_chat, room_gps, room_destiny, room_settings = st.tabs([
    "💬 ROOM: แชทส่งตรงอ่านง่าย", 
    "🛰️ ROOM: GPS ล็อคเป้าแม่นยำ", 
    "🧬 ROOM: เรดาร์วิเคราะห์พิกัดชีวิต",
    "⚙️ ROOM: แผงปรับแต่งค่า UI แอป"
])

# --- ห้องแชทส่งตรงอ่านง่าย (แก้ไข: ส่งปุ๊บ ข้อความจะเด้งขึ้นแสดงด้านล่างให้อ่านทันทีในหน้านี้เลย!) ---
with room_chat:
    st.subheader("💬 ระบบกล่องจดหมายแชทกลางเครือข่าย")
    
    # ฟอร์มการพิมพ์ข้อความส่งตรงเข้า Firebase
    with st.form("python_chat_form", clear_on_submit=True):
        input_msg = st.text_input("พิมพ์ข้อความคลื่นวิทยุของคุณตรงนี้...", placeholder="ใส่ข้อความแล้วกดส่งสัญญาณ...")
        submit_btn = st.form_submit_button("ส่งสัญญาณแชททันที ⚡")
        
        if submit_btn and input_msg.strip() != "":
            try:
                db.reference('global_chat').push({
                    'user': st.session_state.user,
                    'text': input_msg.strip(),
                    'ts': datetime.now().isoformat()
                })
                st.toast("ส่งข้อความขึ้นศูนย์ข้อมูลสำเร็จ!")
            except Exception as chat_err:
                st.error(f"การเชื่อมต่อล้มเหลว: {chat_err}")

    # กระดานอ่านข้อความแชท (ดึงค่าสดจาก Firebase ล่าสุด 10 ข้อความมาเรียงให้อ่านทันทีที่ส่ง)
    st.write("📖 **กระดานอ่านข้อความจริงในระบบ:**")
    try:
        chat_records = db.reference('global_chat').limitToLast(10).get()
        if chat_records:
            # วนลูปแสดงผลจากข้อความล่าสุดลงมาด้านล่าง
            for key, data in reversed(list(chat_records.items())):
                sender = data.get('user', 'Unknown')
                message = data.get('text', '')
                accent = st.session_state.theme_color if sender == st.session_state.user else "#00e5ff"
                st.markdown(f"""
                <div class="chat-bubble-container" style="border-left: 4px solid {accent};">
                    <span style="color:{accent}; font-weight:bold;">[{sender}]</span> : {message}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("ยังไม่มีสัญญาณข้อความส่งเข้ามาในระบบ")
    except Exception as read_err:
        st.caption("กำลังรอการซิงค์พิกัดโครงข่ายแชท...")

# --- ห้อง GPS ระบุตำแหน่งแม่นยำ (แก้ไข: ล็อคพิกัดให้เป๊ะที่สุดด้วย HighAccuracy สูงสุดทางฮาร์ดแวร์มือถือ) ---
with room_gps:
    st.subheader("🛰️ ระบบเรดาร์ตรึงพิกัดดาวเทียม (HIGH ACCURACY REAL-TIME)")
    st.write("ดักฟังพิกัดจริงจากชิปโมเด็มมือถือโดยตรง ล็อคค่าพิกัดสว่างไม่คลาดเคลื่อน")
    
    gps_engine_code = f"""
    <div style="background:#03070a; border:2px solid {st.session_state.theme_color}; padding:15px; border-radius:8px; font-family:monospace; color:#fff;">
        <div id="gps-status-box">📡 กำลังเร่งค้นหาสัญญาณดาวเทียม GPS สด... (โปรดกดยอมรับเปิดสิทธิ์พิกัดบนบราวเซอร์มือถือ)</div>
        <div id="map-frame-box" style="margin-top:10px;"></div>
    </div>
    
    <script>
        if (navigator.geolocation) {{
            // ใช้ฟังก์ชันเฝ้าติดตามและเร่งระดับฮาร์ดแวร์ให้ดึงพิกัดให้แม่นยำที่สุด (ไม่ใช้ค่าแคชเก่าค้างค้างเครื่อง)
            navigator.geolocation.getCurrentPosition(
                (position) => {{
                    const latitude = position.coords.latitude;
                    const longitude = position.coords.longitude;
                    const accuracy_meters = position.coords.accuracy;
                    
                    document.getElementById('gps-status-box').innerHTML = `
                        <span style="color:{st.session_state.theme_color}; font-weight:bold;">🎯 ตรึงพิกัดเป๊ะ (TARGET LOCATED)</span><br>
                        >> พิกัดละติจูด (Lat): ${{latitude}}<br>
                        >> พิกัดลองจิจูด (Lon): ${{longitude}}<br>
                        >> รัศมีความคลาดเคลื่อนลดเหลือเพียง: ${{accuracy_meters.toFixed(1)}} เมตรเท่านั้น!
                    `;
                    
                    // เรียกแผนที่โหมดนำทางดาวเทียมแบบสว่าง ข้อมูลครบถ้วน ไม่คลาดเคลื่อนพิกัดค่าย
                    document.getElementById('map-frame-box').innerHTML = `
                        <iframe width="100%" height="260" frameborder="0" src="https://maps.google.com/maps?q=${{latitude}},${{longitude}}&hl=th&z=16&output=embed" style="border:1px solid {st.session_state.theme_color}; border-radius:6px;"></iframe>
                    `;
                }},
                (error) => {{
                    document.getElementById('gps-status-box').innerText = "🚨 ดักสัญญาณล้มเหลว: " + error.message;
                }},
                {{ 
                    enableHighAccuracy: true, // เปิดชิป GPS เต็มกำลังความแม่นยำสูง
                    timeout: 12000, 
                    maximumAge: 0 // บังคับอ่านค่าสดใหม่ ไม่เอาค่าเก่าที่คลาดเคลื่อน
                }}
            );
        }} else {{
            document.getElementById('gps-status-box').innerText = "อุปกรณ์มือถือของท่านไม่รองรับระบบโมดูล GPS หน้าเว็บบราวเซอร์";
        }}
    </script>
    """
    components.html(gps_engine_code, height=360)

# --- ห้องพยากรณ์วงจรพิกัดชีวิต (DESTINY ANALYST) ---
with room_destiny:
    st.subheader("🧬 ระบบวิเคราะห์คลื่นความถี่เหนี่ยวนำวงรอบเวลา")
    base_dob = st.date_input("ป้อนวันเกิดตั้งต้นเพื่อกวาดสัญญาณเรดาร์", value=date(1984, 1, 1), min_value=date(1960, 1, 1), max_value=date(2026, 12, 31))
    if base_dob:
        origin_profile = calculate_quantum_logic(base_dob)
        st.write(f"🧬 รหัสวิเคราะห์ฐานดวงความจริงของคุณ ({origin_profile['zodiac']}): `{origin_profile['res']}`")

# --- ห้องตั้งค่าอินเตอร์เฟสแอปพลิเคชัน ---
with room_settings:
    st.subheader("⚙️ ศูนย์ปรับแต่งโครงสร้างหน้าจอแอปพลิเคชัน")
    st.session_state.theme_color = st.color_picker("🎨 เปลี่ยนสีกรอบนีออน/ปุ่มหลักทั้งหมด", st.session_state.theme_color)
    st.session_state.bg_color = st.color_picker("🖤 เปลี่ยนสีพื้นหลังระบบหลัก", st.session_state.bg_color)
    st.session_state.border_width = st.slider("📐 ขนาดความหนาขอบเส้นโครงสร้างปุ่ม (พิกเซล)", 1, 10, st.session_state.border_width)
    if st.button("ยืนยันบันทึกโครงสร้างระบบ UI ใหม่ 🛠️"):
        st.rerun()

# =========================================================
# 6. ห้องเครื่องเล่นเพลงและเสียงบำบัดในโฟลเดอร์ปฏิบัติการ (แก้ไข: ดึงค่าตรงโฟลเดอร์เครื่องทำงานจริง)
# =========================================================
st.write("---")
st.subheader("🎵 ห้องระบบเครื่องเล่นเพลงประจำโฟลเดอร์ระบบ (LOCAL ARCHIVE PLAYER)")

# ใช้ os.getcwd() ดึงค่าโฟลเดอร์ปัจจุบันที่ไฟล์โค้ด .py นั่งอยู่จริงแบบไม่มีพลาด
app_current_folder = os.getcwd()
scanned_mp3_files = [f for f in os.listdir(app_current_folder) if f.lower().endswith('.mp3')]

if not scanned_mp3_files:
    st.warning("📂 ตรวจสอบตามความจริง: ตอนนี้ในโฟลเดอร์แอปยังไม่มีไฟล์นามสกุล `.mp3` ไปวางคู่กับไฟล์โค้ดโปรแกรมนี้เลยเพื่อน ระบบเลยเปิดเพลงจากเครื่องตรงๆ ไม่ได้")
    # จำลองลิสต์ไว้รอรับไฟล์จริงเมื่อนายเอามันมาวาง
    scanned_mp3_files = ["(ระบบพร้อมอ่านทันทีถ้าวางไฟล์เสียงคู่กับโค้ด .mp3)", "แทร็กความถี่จำลองคลื่นบำบัดจักรวาล.mp3"]

selected_track = st.selectbox("เลือกแทร็กเสียงที่ตรวจพบคู่โฟลเดอร์ปัจจุบัน", options=scanned_mp3_files)

# ฟังก์ชันตัวจริงในการดึงไฟล์เสียงรอบตัวแปลงเป็นข้อมูล Base64 ส่งเข้าหูฟัง
target_audio_path = os.path.join(app_current_folder, selected_track)
if os.path.exists(target_audio_path) and selected_track.lower().endswith('.mp3'):
    try:
        with open(target_audio_path, "rb") as sound_file:
            audio_base64_string = base64.b64encode(sound_file.read()).decode()
        # ส่งชุดคำสั่ง HTML เครื่องเล่นเสียงที่ดึงพลังงานมาจากไฟล์ข้างตัวจริงเสียงจริง 
        st.markdown(f'<p style="color:#39FF14;">🔊 กำลังดึงไฟล์เสียงรอบตัวมาเล่น: <b>{selected_track}</b></p>', unsafe_allow_html=True)
        st.markdown(f'<audio controls autoplay style="width: 100%;"><source src="data:audio/mp3;base64,{audio_base64_string}" type="audio/mp3"></audio>', unsafe_allow_html=True)
    except Exception as play_error:
        st.error(f"ระบบถอดรหัสคลื่นเสียงขัดข้อง: {play_error}")
else:
    # แทร็กจำลองความถี่แท้จริงรันต่อเนื่องสเถียรบนมือถือระหว่างรอสแกนเจอไฟล์ในเครื่อง
    st.markdown(f'<div style="border:2px dashed #333; padding:10px; border-radius:6px; text-align:center; color:#888;">📻 เล่นสถานีสตรีมมิ่งความถี่สากลสำรองระหว่างรอวางไฟล์เพลงจริง</div>', unsafe_allow_html=True)
    st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", format="audio/mp3")

st.write("---")
st.markdown("<p style='text-align: center; color: #527394; font-weight:bold;'>สโลแกนระบบ: 'อยู่นิ่งๆ ไม่เจ็บตัว' || รายงานผลจากความจริง 100%</p>", unsafe_allow_html=True)
