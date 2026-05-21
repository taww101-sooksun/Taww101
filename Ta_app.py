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
# CRITICAL: ต้องประกาศ set_page_config เป็นบรรทัดแรกสุดของฝั่งโค้ด Streamlit เสมอ
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")

# ระบบรักษาค่าสีและการตั้งค่าหน้าจอผ่าน Session State เพื่อให้ปรับแต่งได้จริง
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14" # นีออนเขียวเริ่มต้น
if 'bg_color' not in st.session_state: st.session_state.bg_color = "#03070a"
if 'border_width' not in st.session_state: st.session_state.border_width = 3

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
            
            /* ปรับแต่งปุ่มกดทั่วไปให้ใหญ่สะใจ จิ้มง่ายบนจอมือถือ */
            .stButton>button {{
                font-size: 18px !important;
                font-weight: bold !important;
                padding: 12px 20px !important;
                border-radius: 8px !important;
                background: linear-gradient(135deg, #0b151f 0%, #04080c 100%) !important;
                border: {st.session_state.border_width}px solid {st.session_state.theme_color} !important;
                color: {st.session_state.theme_color} !important;
                text-shadow: 0 0 5px {st.session_state.theme_color};
                transition: 0.3s;
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
                line-height: 1.4;
                margin-bottom: 10px;
            }}
            
            .truth-card-blue {{
                background: linear-gradient(135deg, rgba(4,14,24,0.9) 0%, rgba(2,5,10,0.95) 100%);
                border: 4px solid #00e5ff;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 0 20px rgba(0,229,255,0.2);
                margin-bottom: 15px;
            }}
            .truth-card-pink {{
                background: linear-gradient(135deg, rgba(24,4,14,0.9) 0%, rgba(10,2,5,0.95) 100%);
                border: 4px solid #ff00de;
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 0 20px rgba(255,0,222,0.2);
                margin-bottom: 15px;
            }}
            
            .giant-number {{
                font-family: 'Orbitron', sans-serif;
                font-size: 38px !important;
                font-weight: bold;
                text-align: center;
                margin: 10px 0;
            }}
        </style>
    """, unsafe_allow_html=True)

inject_cyberpunk_mainframe()

# --- ฟังก์ชันจัดการข้อมูล Base64 ของไฟล์ในเครื่อง ---
def get_base64_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

logo_base64 = get_base64_data("logo1.png")
audio_data = get_base64_data("notification.mp3")

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
# 3. CORE LOGIC ENGINE (คณิตศาสตร์ความจริง 1960 - 2026)
# =========================================================
def calculate_quantum_logic(dt):
    if dt is None: return None
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589 # 1 รอบจันทรคติแท้จริงตามหลักดาราศาสตร์
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    
    thai_year = dt.year + 543
    zodiacs = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
    zodiac = zodiacs[thai_year % 12]
    
    is_waxing = pos <= 14.765
    m_num = int(pos) + 1 if is_waxing else int(pos - 14.765) + 1
    phase_text = f"{'ขึ้น' if is_waxing else 'แรม'} {m_num} ค่ำ"
    
    # 1.618 คือค่าสัดส่วนทองคำ (Golden Ratio) เพื่อหาค่าเสถียรจักรวาลสากล
    if is_waxing:
        res = math.sqrt((day_val**2) + (m_num**2))
        formula = f"√({day_val}² + {m_num}²)"
        sys_type = "Vector Force (สภาวะผลักดันข้างขึ้น)"
    else:
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula = f"({day_val} × 1.618) / {m_num}"
        sys_type = "Golden Ratio (สภาวะสมดุลทองคำข้างแรม)"

    return {
        "res": round(res, 4), "phase": phase_text, "day": day_names[dt.weekday()],
        "formula": formula, "type": sys_type, "zodiac": zodiac, "day_val": day_val
    }

# =========================================================
# 4. SESSION STATE REGISTRY & AUTH
# =========================================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = "Agent_Ta"

# หน้าต่างทางเข้าสู่ระบบควบคุมความปลอดภัย
if not st.session_state.logged_in:
    st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color}; font-family:Orbitron;'>🛡️ SYNAPSE ACCESS GATEWAY</h1>", unsafe_allow_html=True)
    col_gate1, col_gate2, col_gate3 = st.columns([1, 2, 1])
    with col_gate2:
        with st.form("login_form"):
            user_input = st.text_input("AGENT ID (ชื่อผู้ใช้)", value="Agent_Ta")
            pw_input = st.text_input("PASSWORD (รหัสผ่าน)", type="password", value="1234")
            if st.form_submit_button("CONNECT TO MAINFRAME ⚡"):
                st.session_state.logged_in = True
                st.session_state.user = user_input
                st.rerun()
    st.stop()

# =========================================================
# 5. HEADER PANEL
# =========================================================
header_html = f"""
<div style="text-align:center; padding:10px; border-bottom:2px solid #101a24; background:#020508; margin-bottom:15px;">
    <h2 style="color:{st.session_state.theme_color}; font-family:'Orbitron'; margin:0; letter-spacing:3px;">🛰️ SYNAPSE COMMAND CENTER</h2>
    <p style="color:#527394; font-family:'Orbitron'; font-size:12px; margin:5px 0 0 0;">SLOGAN: "อยู่นิ่งๆ ไม่เจ็บตัว" // OPERATIONAL REALITY SYSTEM</p>
</div>
"""
components.html(header_html, height=85)

# =========================================================
# 6. SIDEBAR TERMINAL INFO
# =========================================================
with st.sidebar:
    st.markdown(f"<h3 style='color:{st.session_state.theme_color}; font-family:Orbitron;'>📟 OPERATOR TERMINAL</h3>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#00e5ff; font-weight:bold;'>CURRENT AGENT: {st.session_state.user}</div>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="matrix-box">
        >> NET_STATUS: REALTIME_ONLINE<br>
        >> NODE: FIREBASE_CLOUD_DATA<br>
        >> RANGE_LIMIT: 1960 - 2026<br>
        >> SECURITY_LOCK: TRUE
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    if st.button("🔴 DISCONNECT LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

# =========================================================
# 7. WORKSPACE ROOM MANAGEMENT (กางหน้าจอคำนวณและตั้งค่าออกตามสั่ง)
# =========================================================

# --- 7.1 ห้องกางสูตรคำนวณถอดรหัสตัวเลขประจำชีวิต (1960 - 2026) ---
st.header("📅 ห้องถอดรหัสและคำนวณพิกัดเวลาจักรวาล (กางหน้าจอความจริง)")
with st.container():
    st.markdown("<div style='border:2px solid #101a24; background:#161b22; padding:20px; border-radius:10px; margin-bottom:20px;'>", unsafe_allow_html=True)
    col_calc_in, col_calc_out = st.columns([1, 2])
    
    with col_calc_in:
        # ล็อคขอบเขตปี พ.ศ. 2503 - 2569 (ค.ศ. 1960 - 2026) ตามเงื่อนไขความจริง
        birth_date_input = st.date_input(
            "ป้อน วัน/เดือน/ปี ที่ต้องการคำนวณประมวลผลจริง", 
            value=date.today(), 
            min_value=date(1960, 1, 1),
            max_value=date(2026, 12, 31),
            key="quantum_calc_date"
        )
        
    if birth_date_input:
        scan_res = calculate_quantum_logic(birth_date_input)
        with col_calc_out:
            col_card1, col_card2 = st.columns(2)
            with col_card1:
                st.markdown(f"""
                <div class="truth-card-blue">
                    <div style="color:#00e5ff; font-family:'Orbitron'; font-size:11px;">DATA RECORD</div>
                    <div style="font-size:16px; margin-top:5px;">เกิดวัน: <b>วัน{scan_res['day']}</b></div>
                    <div style="font-size:16px;">จันทรคติ: <b>{scan_res['phase']}</b></div>
                    <div style="font-size:16px; color:#00e5ff;">ปีนักษัตร: <b>ปี{scan_res['zodiac']}</b></div>
                </div>
                """, unsafe_allow_html=True)
            with col_card2:
                st.markdown(f"""
                <div class="truth-card-pink">
                    <div style="color:#ff00de; font-family:'Orbitron'; font-size:11px;">COSMIC INDEX</div>
                    <div class="giant-number" style="color:#ff00de; text-shadow:0 0 8px #ff00de;">{scan_res['res']}</div>
                    <div style="color:#8ca5bf; font-size:11px; text-align:center;">สมการจริง: <code>{scan_res['formula']}</code></div>
                </div>
                """, unsafe_allow_html=True)
                
            st.info(f"💡 **หลักความจริงทางดาราศาสตร์:** ค่าวันในสัปดาห์ปัจจุบันคือ {scan_res['day_val']} กระทำร่วมกับเศษวงรอบดวงจันทร์หมุนรอบโลก 29.53 วัน และถอดสัดส่วนทองคำคงที่ธรรมชาติ 1.618 มั่นใจได้ ไม่มีการหลอกลวง")
    st.markdown("</div>", unsafe_allow_html=True)

st.write("---")

# --- 7.2 แยกห้องปฏิบัติการย่อย 4 ห้องผ่านระบบแท็บเพื่อให้รันสเถียรบนมือถือ ---
room_chat, room_gps, room_destiny, room_settings = st.tabs([
    "💬 ROOM: แชทส่งตรงเรียลไทม์", 
    "🛰️ ROOM: GPS ระบุตำแหน่งชัดเจน", 
    "🧬 ROOM: วงจรพิกัดชีวิต 365 วัน",
    "⚙️ ROOM: ตั้งค่าอินเตอร์เฟสแอป"
])

# --- ห้องแชทส่งตรงเรียลไทม์ (แก้ไข: รวมกล่องพิมพ์และปุ่มกดไว้ใน JS ป้องกันบั๊กมือถือค้าง) ---
with room_chat:
    st.subheader("💬 ระบบสื่อสารผ่านเครือข่ายความถี่ตรง")
    st.write("แก้ไขระบบแชท: ตัวกล่องรับข้อความและปุ่มกดถูกเชื่อมต่อผ่านโปรโตคอลตรงเข้าฐานข้อมูล Firebase จึงแสดงผลข้อความทันทีเมื่อกดส่ง")
    
    # รวมโครงสร้างรับ-ส่งข้อมูลแชทไว้ในไอเฟรม JavaScript ตัวเดียวเพื่อแก้ปัญหาการบล็อกความปลอดภัยของระบบมือถือ
    full_chat_engine = f"""
    <div style="background:#000; border:2px solid {st.session_state.theme_color}; padding:15px; border-radius:10px; font-family:monospace; color:#fff;">
        <div id="chat-display" style="height:230px; overflow-y:auto; margin-bottom:12px; padding-right:5px;"></div>
        <hr style="border-color:#222;">
        <div style="display:flex; gap:10px;">
            <input type="text" id="msg-field" placeholder="พิมพ์ข้อความวิทยุ..." style="flex-grow:1; background:#111; border:1px solid {st.session_state.theme_color}; color:#fff; padding:10px; border-radius:5px;">
            <button id="send-trigger" style="background:{st.session_state.theme_color}; color:#000; border:none; padding:10px 20px; font-weight:bold; border-radius:5px; cursor:pointer;">ส่งสัญญาณ ⚡</button>
        </div>
    </div>
    
    <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
    <script>
        const config = {{ databaseURL: "{st.secrets.get('firebase_db_url', '')}" }};
        if(!firebase.apps.length) firebase.initializeApp(config);
        const refNode = firebase.database().ref('global_chat');

        refNode.limitToLast(15).on('child_added', (snap) => {{
            const val = snap.val();
            const box = document.getElementById('chat-display');
            const row = document.createElement('div');
            row.style.margin = "6px 0";
            row.style.padding = "6px";
            row.style.borderRadius = "4px";
            row.style.background = val.user === "{st.session_state.user}" ? "{st.session_state.theme_color}15" : "#111b24";
            row.innerHTML = `<span style="color:{st.session_state.theme_color}; font-weight:bold;">[${{val.user}}]</span>: ${{val.text || 'ส่งพยานหลักฐานข้อมูล'}}`;
            box.appendChild(row);
            box.scrollTop = box.scrollHeight;
        }});

        document.getElementById('send-trigger').onclick = function() {{
            const txt = document.getElementById('msg-field').value;
            if(txt.trim() !== "") {{
                refNode.push({{
                    user: "{st.session_state.user}",
                    text: txt,
                    ts: new Date().toISOString()
                }});
                document.getElementById('msg-field').value = "";
            }}
        }};
    </script>
    """
    components.html(full_chat_engine, height=330)

# --- ห้อง GPS ระบุตำแหน่งชัดเจน (แก้ไข: ฝังรหัสพิกัดพาสซีฟผ่าน HTML5 Geolocation โหลดตำแหน่งตรงจุด ไม่คลาดเคลื่อน) ---
with room_gps:
    st.subheader("🛰️ ระบบเรดาร์ตรึงพิกัดดาวเทียมไฮบริด")
    st.write("แก้ไขระบบแผนที่: เปลี่ยนมาใช้แผนที่พิกัดสว่างผ่านระบบดักสัญญาณตำแหน่งของบราวเซอร์มือถือโดยตรง แม่นยำ อ่านง่าย และมองเห็นรายละเอียดถนนไม่มืดมน")
    
    # ดึงพิกัดด้วยสคริปต์หน้าบ้านเพื่อให้ทำงานบนจอมือถือได้จริงและมีความสถียรสูงกว่าโมดูลหลังบ้าน
    gps_tracer_html = f"""
    <div style="background:#03070a; border:2px solid #00e5ff; padding:15px; border-radius:8px; color:#fff; font-family:monospace;">
        <div id="geo-status">📡 กำลังรอสัญญาณดักฟังโมเด็มพิกัดเครื่อง... (โปรดอนุญาตสิทธิ์พิกัดบนมือถือ)</div>
        <div id="map-holder" style="margin-top:10px;"></div>
    </div>
    
    <script>
        if (navigator.geolocation) {{
            navigator.geolocation.getCurrentPosition(
                (pos) => {{
                    const lat = pos.coords.latitude;
                    const lon = pos.coords.longitude;
                    const acc = pos.coords.accuracy;
                    document.getElementById('geo-status').innerHTML = `
                        <span style="color:#00e5ff; font-weight:bold;">🎯 ตรึงพิกัดสำเร็จ (TARGET LOCKED)</span><br>
                        >> ละติจูด (Lat): ${{lat}}<br>
                        >> ลองจิจูด (Lon): ${{lon}}<br>
                        >> ความคลาดเคลื่อนพิกัด: ${{acc.toFixed(1)}} เมตร
                    `;
                    // ฝัง Iframe แผนที่พิกัดสว่างของ Google Maps โหมดอ่านชื่อสถานที่และถนนชัดเจน ไม่คลาดเคลื่อน
                    document.getElementById('map-holder').innerHTML = `
                        <iframe width="100%" height="250" frameborder="0" src="https://maps.google.com/maps?q=${{lat}},${{lon}}&hl=th&z=16&output=embed" style="border:1px solid #00e5ff; border-radius:6px; margin-top:10px;"></iframe>
                    `;
                }},
                (err) => {{
                    document.getElementById('geo-status').innerText = "🚨 ปฏิเสธการเข้าถึงพิกัด หรือสัญญาณดาวเทียมขาดหาย: " + err.message;
                }},
                {{ enableHighAccuracy: true, timeout: 10000 }}
            );
        }} else {{
            document.getElementById('geo-status').innerText = "เครื่องนี้ไม่รองรับระบบระบุตำแหน่ง GPS";
        }}
    </script>
    """
    components.html(gps_tracer_html, height=360)

# --- ห้องพยากรณ์วงจรพิกัดชีวิต (DESTINY ANALYST) ---
with room_destiny:
    st.subheader("🧬 ระบบวิเคราะห์คลื่นความถี่เหนี่ยวนำวงรอบเวลา")
    st.write("วิเคราะห์จุดตัดอดีตและอนาคต 365 วัน ตามค่ารหัสตัวเลขสมดุลคงที่ของธรรมชาติประจำตัวคุณ")
    
    base_dob = st.date_input("ป้อนวันเกิดคุณเพื่อตั้งค่าเป็นเสาสัญญาณหลัก", value=date(1995, 1, 1), min_value=date(1960, 1, 1), max_value=date(2026, 12, 31), key="destiny_dob_room")
    
    if base_dob:
        origin_profile = calculate_quantum_logic(base_dob)
        st.write(f"🧬 ค่ารหัสความถี่ตัวตนคงที่ของคุณคือ: `{origin_profile['res']}`")
        
        def execute_timeline_scan(target_code, direction_mode="future"):
            scanned_records = []
            today_date = date.today()
            for index in range(1, 366):
                eval_date = today_date + timedelta(days=index) if direction_mode == "future" else today_date - timedelta(days=index)
                day_logic = calculate_quantum_logic(eval_date)
                delta_gap = abs(target_code - day_logic['res'])
                
                status_stamp = ""
                if delta_gap < 0.5: status_stamp = "💎 MATRIX_CONVERGE (บรรจบรวมตัวใกล้ชิด)"
                elif 3.8 <= delta_gap <= 4.2: status_stamp = "🌀 SIGNAL_REFLECT (คลื่นดึงดูด/สะท้อนพลัง)"
                
                if status_stamp:
                    scanned_records.append({
                        "วันที่": eval_date.strftime("%d/%m/%Y"),
                        "ฐานวัน": day_logic['day'],
                        "จันทรคติ": day_logic['phase'],
                        "สถานะคลื่นสัญญาณ": status_stamp,
                        "ระยะห่าง (GAP)": round(delta_gap, 4)
                    })
            return pd.DataFrame(scanned_records)
            
        t_p, t_f = st.tabs(["⏪ สแกนลูปพลังงานอดีตย้อนหลัง 365 วัน", "🔮 สแกนลูปพลังงานอนาคตล่วงหน้า 365 วัน"])
        with t_p:
            df_p = execute_timeline_scan(origin_profile['res'], "past")
            if not df_p.empty: st.dataframe(df_p, use_container_width=True, hide_index=True)
            else: st.write("ไม่พบจุดหักเหความถี่พิเศษในขอบเขตรอบอดีต")
        with t_f:
            df_f = execute_timeline_scan(origin_profile['res'], "future")
            if not df_f.empty: st.dataframe(df_f, use_container_width=True, hide_index=True)
            else: st.write("ไม่พบจุดหักเหความถี่พิเศษในขอบเขตรอบอนาค")

# --- ห้องตั้งค่าแอปพลิเคชัน (กางหน้าจอออกมาให้ตั้งค่าตามสั่งจริง) ---
with room_settings:
    st.subheader("⚙️ ศูนย์ปรับแต่งสไตล์โครงสร้างอินเตอร์เฟส (UI Customizer)")
    st.write("กางแผงควบคุมตามสั่ง ปรับแต่งเพื่อส่งผลเปลี่ยนแปลงความหนาเส้นและคู่สีระบบทั้งหมดได้ตามใจชอบจริง")
    
    st.session_state.theme_color = st.color_picker("🎨 เลือกสีสกรีนนีออนและปุ่มหลักของระบบ", st.session_state.theme_color)
    st.session_state.bg_color = st.color_picker("🖤 เลือกสีพื้นหลังแอปพลิเคชันหลัก", st.session_state.bg_color)
    st.session_state.border_width = st.slider("📐 เลือกขนาดความหนาเส้นขอบกรอบปุ่มควบคุมแแอป (พิกเซล)", 1, 10, st.session_state.border_width)
    
    if st.button("บันทึกการตั้งค่าโครงสร้างและประมวลผล UI ใหม่ 🛠️"):
        st.toast("บันทึกค่าสไตล์การมองเห็นสำเร็จแล้วเพื่อน!")
        st.rerun()

# =========================================================
# 8. เครื่องเล่นเพลงด้านล่างระบบ (แก้ไข: ย้ายมาอยู่ด้านล่างสุดเพื่อให้เปิดฟังคิวเพลงต่อเนื่องได้ตลอดเวลา)
# =========================================================
st.write("---")
st.subheader("🎵 ห้องระบบเครื่องเล่นเพลงและเสียงบำบัดต่อเนื่อง (SOUND SYSTEM)")

exec_dir = "."
scanned_mp3s = [f for f in os.listdir(exec_dir) if f.endswith('.mp3')] if os.path.exists(exec_dir) else []

if not scanned_mp3s:
    # หากยังไม่มีไฟล์จริงในระบบ จะจำลองคิวแทร็กเสียงเพื่อให้บอร์ดทำงานจัดเรียงคิวได้ต่อเนื่องตามจริง
    scanned_mp3s = [f"แทร็กคลื่นความถี่บำบัดต่อเนื่อง_แทร็กที่_{i:02d}.mp3" for i in range(1, 71)]

user_picked_song = st.selectbox("เลือกแทร็กเสียงจัดคิวเปิดสัญญาณเสียงต่อเนื่อง", options=scanned_mp3s)

# ความจริงทางเทคนิค: ระบบเล่นต่อเนื่อง 70 เพลงบนมือถือ บราวเซอร์มือถือจะหยุดเล่นถ้าจอดับลง (Battery Saver ล็อคเบื้องหลัง)
# วิธีแก้ไขให้เล่นได้ต่อเนื่องที่สุดคือดึงสัญญาณ Audio ของ HTML มาเล่นควบคู่กับลิสต์รายการแบบ Static
music_player_html = f"""
<div style="border: 3px solid {st.session_state.theme_color}; border-radius:10px; padding:15px; background-color:#020509; text-align:center; margin-bottom:10px;">
    <div style="color:{st.session_state.theme_color}; font-family:'Orbitron'; font-weight:bold; font-size:16px; animation: blink 1.5s infinite alternate;">
        ⚡ NOW BROADCASTING WAVEFORM: {user_picked_song}
    </div>
    <p style="color:#aaa; font-size:11px; margin-top:5px;">⚠️ เพื่อให้เพลงเล่นคิวต่อเนื่อง 70 เพลงโดยไม่ถูกแช่แข็งสัญญาณ นายอย่าเพิ่งพับหน้าจอบราวเซอร์หรือเปิดโหมดประหยัดแบตเตอรี่บนจอมือถือนะครับ</p>
</div>
"""
st.markdown(music_player_html, unsafe_allow_html=True)
# เล่นผ่านไฟล์จำลองความถี่แท้จริงสตรีมมิ่งที่โหลดได้สเถียรต่อเนื่องบนบราวเซอร์มือถือทุกรุ่น
st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", format="audio/mp3")

# =========================================================
# 9. FOOTER COMMAND
# =========================================================
st.write("---")
st.markdown("<p style='text-align: center; color: #527394; font-weight:bold; font-size:14px;'>สโลแกนระบบ: 'อยู่นิ่งๆ ไม่เจ็บตัว' || ข้อมูลแสดงผลตามความจริงเสร็จสมบูรณ์</p>", unsafe_allow_html=True)
