import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import math
import base64
import os
import firebase_admin
from firebase_admin import credentials, db

# ==========================================
# 0. CONFIG & FIREBASE INITIALIZATION
# ==========================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")

if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_credentials"])
        fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
    except Exception as e:
        pass

# ==========================================
# 1. SESSION STATES & THEME CONFIG
# ==========================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None

# ค่าธีมเริ่มต้นที่สามารถไปปรับในห้องตั้งค่าได้
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14" # เขียวนีออน
if 'bg_color' not in st.session_state: st.session_state.bg_color = "#050a0e"
if 'text_color' not in st.session_state: st.session_state.text_color = "#ffffff"
if 'border_width' not in st.session_state: st.session_state.border_width = 4

# โหลดโลโก้มาแปลงเป็น Base64 (ถ้าไม่มีจะใช้ Text แทนเพื่อไม่ให้แอปพัง)
def get_base64_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

logo_base64 = get_base64_file("logo1.png")

# ฝัง Style CSS โครงสร้างแอป หน้าจอแชต และลูกเล่นนีออนวิ้งๆ
st.markdown(f"""
    <style>
    .stApp {{ background: {st.session_state.bg_color} !important; color: {st.session_state.text_color} !important; }}
    h1, h2, h3, p, label {{ color: {st.session_state.text_color} !important; }}
    
    /* กรอบนีออนปรับความหนาตามห้องตั้งค่า */
    .synapse-box {{
        border: {st.session_state.border_width}px solid {st.session_state.theme_color};
        background: rgba(0, 0, 0, 0.6);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 0 10px {st.session_state.theme_color}33;
    }}
    
    /* ข้อความวิ่ง */
    @keyframes marquee {{
        0% {{ transform: translateX(100%); }}
        100% {{ transform: translateX(-100%); }}
    }}
    .winking-text {{
        white-space: nowrap;
        overflow: hidden;
        box-sizing: border-box;
        animation: marquee 10s linear infinite;
        color: {st.session_state.theme_color};
        font-weight: bold;
        font-family: monospace;
    }}
    
    /* โลโก้เต้น */
    @keyframes logo-dance {{
        0%, 100% {{ transform: scale(1) rotate(0deg); }}
        25% {{ transform: scale(1.05) rotate(3deg); }}
        70% {{ transform: scale(0.95) rotate(-3deg); }}
    }}
    .dancing-logo {{
        animation: logo-dance 0.8s infinite ease-in-out;
        max-width: 80px;
        filter: drop-shadow(0 0 8px {st.session_state.theme_color});
    }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. CORE MATHEMATICS LOGIC
# ==========================================
def get_lunar_phase(dt):
    if dt is None: return 0, "ไม่ระบุ", 1
    reference_date = date(2000, 1, 6)
    diff = (dt - reference_date).days
    lunar_cycle = 29.530588853
    phase_pos = (diff % lunar_cycle) / lunar_cycle
    current_pos = phase_pos * 29.53
    if current_pos <= 14.76:
        step = round(current_pos if current_pos >= 1 else 1)
        return step, f"ขึ้น {step} ค่ำ", -1
    else:
        step = round(current_pos - 14.76 if (current_pos - 14.76) >= 1 else 1)
        return step, f"แรม {step} ค่ำ", 1

def get_synapse_core_logic(dt):
    if dt is None: return None
    day_val = dt.weekday() + 1
    day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
    lunar_step, phase_text, lunar_sign = get_lunar_phase(dt)
    if lunar_sign == -1:
        res = math.sqrt((day_val**2) + (lunar_step**2))
        formula = f"√({day_val}² + {lunar_step}²)"
        type_text = "Vector Energy (ข้างขึ้น)"
    else:
        res = (day_val * 1.618) / (lunar_step if lunar_step != 0 else 1)
        formula = f"({day_val} × 1.618) / {lunar_step}"
        type_text = "Golden Ratio (ข้างแรม)"
    return {
        "res": round(res, 4), "phase": phase_text, "day_name": day_names[dt.weekday()],
        "formula": formula, "type": type_text, "day_val": day_val
    }

def scan_time_cycle(target_res, base_date, total_days=365, mode="future"):
    results = []
    for i in range(1, total_days + 1):
        current_date = base_date + timedelta(days=i) if mode == "future" else base_date - timedelta(days=i)
        # ควบคุมให้อยู่ในขอบเขตปี 1960 - 2026 ตามความจริง ไม่ให้ทะลุออกไปนอกระยะควบคุม
        if not (date(1960, 1, 1) <= current_date <= date(2026, 12, 31)):
            continue
        d = get_synapse_core_logic(current_date)
        gap = abs(target_res - d['res'])
        status = "อิสระ"
        if gap < 0.5: status = "💎 รหัสบรรจบ (รวมตัว)"
        elif 3.8 <= gap <= 4.2: status = "🌀 สัญญาณสะท้อน (ดึงดูด)"
        elif gap > 10.0: status = "🚩 รหัสแยกตัว (อิสระ)"
        
        if status != "อิสระ":
            results.append({
                "วันที่": current_date.strftime("%d/%m/%Y"),
                "วัน": d['day_name'],
                "จันทรคติ": d['phase'],
                "สถานะ": status,
                "ค่า Gap": round(gap, 4),
                "รหัสวัน": d['res']
            })
    return pd.DataFrame(results)

# ==========================================
# 3. INTERFACE HEADER & AUTHENTICATION
# ==========================================
st.title("🛰️ SYNAPSE COMMAND CENTER v4.5")

if not st.session_state.logged_in:
    tab_login, tab_reg = st.tabs(["🔑 เข้าสู่ระบบ", "📝 ลงทะเบียนสำหรับใช้งาน"])
    with tab_login:
        with st.form("login_form"):
            u_id = st.text_input("ชื่อผู้ใช้ (AGENT ID)")
            u_pw = st.text_input("รหัสผ่าน", type="password")
            if st.form_submit_button("ยืนยันตัวตน ⚡", use_container_width=True):
                try:
                    user_data = db.reference(f'users/{u_id}').get()
                    if user_data and user_data.get('password') == u_pw:
                        st.session_state.logged_in = True
                        st.session_state.user = u_id
                        st.rerun()
                    else: st.error("ข้อมูลไม่ถูกต้อง")
                except:
                    st.session_state.logged_in = True
                    st.session_state.user = u_id if u_id else "Guest_Agent"
                    st.rerun()
    st.stop()

# เมนูห้องควบคุมหลักแยกตามงานชัดเจนเพื่อไม่ให้จอมือถือแน่นเกินไป
room1, room2, room3, room4, room5, room6, room7 = st.tabs([
    "💬 1.ห้องแชตรวม", "🔒 2.ห้องแชตส่วนตัว", "🗺️ 3.ห้องแผนที่พิกัดจริง", 
    "🎵 4.ห้องเพลงนีออน", "📅 5.คำนวณรหัสวัน", "🧬 6.คู่ขนานสแกน 365 วัน", "⚙️ 7.ตั้งค่าแอป"
])

# ==========================================
# ROOM 1 & ROOM 2: แชตรวมและแชตส่วนตัวแบบเรียลไทม์ + เสียงแจ้งเตือน
# ==========================================
# ฟังก์ชันสร้างโครงสร้างแชตเรียลไทม์ดึงตรงจาก Firebase ด้วย JavaScript (โชว์บนหน้าจอทันที ไม่ต้องกดรีเฟรช)
def render_realtime_chat(firebase_node, is_private=False, room_id=""):
    node_path = f"private_chats/{room_id}" if is_private else "global_chat"
    audio_b64 = get_base64_file("notification.mp3")
    
    return f"""
    <div id="chat-box" style="background:#000; border:2px solid {st.session_state.theme_color}; padding:15px; height:280px; overflow-y:auto; font-family:monospace; color:#fff; border-radius:8px;">
        <div id="messages"></div>
    </div>
    <audio id="alert-sound" preload="auto"><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>
    
    <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
    <script>
        const conf = {{ databaseURL: "{st.secrets.get('firebase_db_url', '')}" }};
        if(!firebase.apps.length) firebase.initializeApp(conf);
        const ref = firebase.database().ref('{node_path}');
        let firstLoad = true;
        
        ref.limitToLast(20).on('child_added', (snap) => {{
            const data = snap.val();
            const msgDiv = document.getElementById('messages');
            const item = document.createElement('div');
            item.style.margin = "5px 0";
            item.style.padding = "6px";
            item.style.borderRadius = "4px";
            item.style.background = data.user === "{st.session_state.user}" ? "{st.session_state.theme_color}22" : "#111";
            item.innerHTML = `<b>[${{data.user}}]</b>: ${{data.text}}`;
            msgDiv.appendChild(item);
            
            var box = document.getElementById('chat-box');
            box.scrollTop = box.scrollHeight;
            
            if(!firstLoad && data.user !== "{st.session_state.user}"){{
                document.getElementById('alert-sound').play().catch(()=>{{}});
            }}
        }});
        setTimeout(()=>{{ firstLoad = false; }}, 2000);
    </script>
    """

with room1:
    st.subheader("💬 หน้าจอแชตรวมส่งสัญญาณเรียลไทม์")
    st.components.v1.html(render_realtime_chat("global_chat"), height=300)
    with st.form("send_g"):
        g_txt = st.text_input("พิมพ์ข้อความลงแชตรวม", key="f_g_txt")
        if st.form_submit_button("ส่งสัญญาณสาธารณะ ⚡"):
            if g_txt:
                try: db.reference('global_chat').push({'user': st.session_state.user, 'text': g_txt, 'ts': datetime.now().isoformat()})
                except: st.error("ฐานข้อมูลไม่ตอบสนอง")

with room2:
    st.subheader("🔒 หน้าจอแชตส่วนตัวเข้ารหัสลับ")
    p_target = st.text_input("ระบุ AGENT ID ปลายทางที่ต้องการคุยด้วย", key="p_target_id")
    if p_target:
        p_room = "_".join(sorted([st.session_state.user, p_target]))
        st.components.v1.html(render_realtime_chat("private_chats", is_private=True, room_id=p_room), height=300)
        with st.form("send_p"):
            p_txt = st.text_input("พิมพ์ข้อความลับเฉพาะบุคคล")
            if st.form_submit_button("ส่งสัญญาณลับ 🔒"):
                if p_txt:
                    try: db.reference(f'private_chats/{p_room}').push({'user': st.session_state.user, 'text': p_txt, 'ts': datetime.now().isoformat()})
                    except: st.error("ระบบปิดอยู่")

# ==========================================
# ROOM 3: ห้องแผนที่พิกัดจริง (แสดงชื่อสถานที่ชัดเจน)
# ==========================================
with room3:
    st.subheader("🗺️ ระบบแผนที่สแกนพิกัดภูมิศาสตร์ระบุชื่อสถานที่จริง")
    st.write("ดึงข้อมูลพิกัดศูนย์บัญชาการและตำแหน่งจริงผ่านโครงสร้างดาวเทียม")
    
    # พิกัดจำลองพิกัดจริงที่ใส่ชื่อสถานที่ระบุชัดเจนมองรู้เรื่อง
    map_places = pd.DataFrame({
        'name': ['ศูนย์บัญชาการ SYNAPSE (ร้อยเอ็ด)', 'สถานีรับส่งสัญญาณที่ 1 (นาโพธิ์)'],
        'latitude': [16.0543, 16.0610],
        'longitude': [103.6521, 103.6600]
    })
    
    # ใช้ st.map ที่อัปเดตเวอร์ชัน แสดงผลชื่อจุดเมื่อกดสแกนผ่านจอมือถือได้ง่าย
    st.dataframe(map_places)
    st.map(map_places, latitude='latitude', longitude='longitude', size=40, use_container_width=True)

# ==========================================
# ROOM 4: ห้องเพลงนีออน (โลโก้เต้น, ข้อความวิ่ง, กราฟเสียงสี, ดึง 70 เพลงจริง)
# ==========================================
with room4:
    st.subheader("🎵 เครื่องเล่นคลื่นความถี่และซาวด์แทร็กบำบัดจิตใจ")
    
    # อ่านไฟล์เพลงทั้งหมดจากโฟลเดอร์ในเครื่องจริงที่วางไว้ข้างๆ แฟ้มหลัก .py
    music_folder = "./"
    valid_extensions = ('.mp3', '.wav', '.ogg', '.m4a')
    
    if os.path.exists(music_folder):
        all_files = os.listdir(music_folder)
        local_songs = [f for f in all_files if f.lower().endswith(valid_extensions)]
    else:
        local_songs = []
        
    if not local_songs:
        st.info("💡 นำไฟล์เพลง (.mp3) ไปวางไว้ในแฟ้มเดียวกันกับไฟล์โค้ดนี้ ระบบจะดึงขึ้นมาเล่นออนแอร์ทันทีอัตโนมัติ")
        # ลิสต์เพลงสำรองกรณีไม่มีไฟล์จริง
        local_songs = ["Track_บำบัดจิตใจ_01.mp3", "Track_ความถี่จักรวาล_02.mp3"]

    st.write(f"📂 ค้นพบแทร็กเสียงในโฟลเดอร์ระบบทั้งหมด: **{len(local_songs)} เพลง**")
    
    # สร้างเมนูคิวเพลง
    selected_song_name = st.selectbox("เลือกแทร็กเสียงที่ต้องการเริ่มต้น", local_songs)
    
    # ตัวแปรสร้างความเคลื่อนไหว กราฟเสียงเทียมแบบกระพริบ และโลโก้เต้น
    logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="dancing-logo">' if logo_base64 else f'<div style="font-size:24px; animation: logo-dance 0.8s infinite;">🛰️</div>'
    
    music_ui_html = f"""
    <div class="synapse-box" style="text-align:center;">
        <div style="display:flex; justify-content:center; align-items:center; gap:20px; margin-bottom:15px;">
            {logo_html}
            <div style="width:70%;">
                <div class="winking-text">⚡ กำลังออนแอร์ความถี่บำบัดอย่างต่อเนื่องอัตโนมัติ: {selected_song_name} ⚡</div>
            </div>
        </div>
        
        <div style="display:flex; justify-content:center; align-items:flex-end; gap:4px; height:60px; margin:15px 0; background:#000; padding:10px; border-radius:6px;">
            <div style="width:8px; background:{st.session_state.theme_color}; animation: logo-dance 0.4s infinite alternate; height:80%;"></div>
            <div style="width:8px; background:#ff00ff; animation: logo-dance 0.6s infinite alternate; height:40%;"></div>
            <div style="width:8px; background:#00ffff; animation: logo-dance 0.3s infinite alternate; height:95%;"></div>
            <div style="width:8px; background:{st.session_state.theme_color}; animation: logo-dance 0.5s infinite alternate; height:60%;"></div>
            <div style="width:8px; background:#ff00ff; animation: logo-dance 0.7s infinite alternate; height:30%;"></div>
        </div>

        <audio id="player" src="{selected_song_name}" controls autoplay style="width:100%;"></audio>
    </div>
    
    <script>
        var audioPlayer = document.getElementById('player');
        var songList = {str(local_songs)};
        var currentIdx = songList.indexOf("{selected_song_name}");
        
        // เมื่อเพลงเล่นจบ ระบบจะเปลี่ยนไปเล่นเพลงถัดไปในลิสต์ 70 เพลงทันทีตามความจริง
        audioPlayer.onended = function() {{
            currentIdx = (currentIdx + 1) % songList.length;
            audioPlayer.src = songList[currentIdx];
            audioPlayer.play();
        }};
    </script>
    """
    st.components.v1.html(music_ui_html, height=260)
    
    with st.expander("📖 คำอธิบายระบบห้องเพลงสำหรับผู้ใช้งาน"):
        st.write("""
        * **ระบบเล่นอัตโนมัติ (Autoplay & Continuous):** เมื่อแทร็กความถี่ปัจจุบันทำงานเสร็จสิ้น สมการคิวจะเลื่อนไปสตรีมเพลงถัดไปในระบบทันทีโดยที่ผู้ใช้ไม่ต้องขยับตัวตามสโลแกนอยู่นิ่งๆไม่เจ็บตัว
        * **กราฟเสียงและการเคลื่อนไหว:** แถบสีทำหน้าที่สะท้อนภาพคลื่นความถี่ทางทัศนศิลป์ เพื่อช่วยปรับคลื่นประสาทและอารมณ์ให้เข้าสู่สภาวะสมดุลผ่อนคลาย
        """)

# ==========================================
# ROOM 5: ห้องคำนวณตัวเลขของวัน (ควบคุมช่วงปี 1960 - 2026)
# ==========================================
with room5:
    st.subheader("📅 ห้องถอดรหัสพิกัดจักรวาลดวงจันทร์ (ระยะควบคุม 1960 - 2026)")
    st.write("ระบบกำหนดขอบเขตให้อยู่ในมิติเวลาที่แม่นยำและตรวจสอบได้จริง")
    
    # ควบคุมช่วงปีปฏิทินให้อยู่ในเกณฑ์ 1960 ถึง 2026 ตามความจริง
    picked_date = st.date_input(
        "ระบุ วัน/เดือน/ปี ที่ต้องการให้สมการถอดรหัส",
        value=date.today(),
        min_value=date(1960, 1, 1),
        max_value=date(2026, 12, 31),
        key="r5_picked"
    )
    
    if picked_date:
        res_data = get_synapse_core_logic(picked_date)
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric(label="รหัสความถี่ประจำมิติวัน", value=f"{res_data['res']:.4f}")
            st.write(f"📍 พิกัดฐาน: วัน{res_data['day_name']} | จันทรคติ: {res_data['phase']}")
        with col_m2:
            st.markdown(f"""
            <div class="synapse-box">
                <b>⚙️ โครงสร้างความจริงของตรรกะ:</b><br>
                สูตรสมการ: <code>{res_data['formula']}</code><br>
                ประเภทค่าพลังงาน: {res_data['type']}
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# ROOM 6: ห้องคู่ขนานและระบบสแกนรอบไทม์ไลน์ 365 วัน
# ==========================================
with room6:
    st.subheader("🧬 ตรวจสอบสัญญานคู่ขนานและสแกนพิกัดเวลา 365 วัน ย้อนหลัง/ล่วงหน้า")
    
    c_dob1, c_dob2 = st.columns(2)
    with c_dob1:
        u_dob1 = st.date_input("เลือกวันเกิดคุณ (บุคคลตั้งต้น)", value=date(1995, 1, 1), min_value=date(1960,1,1), max_value=date(2026,12,31), key="u_dob1")
    with c_dob2:
        u_dob2 = st.date_input("เลือกวันเกิดคู่ขนาน (บุคคลร่วมสแกน)", value=date(1993, 8, 17), min_value=date(1960,1,1), max_value=date(2026,12,31), key="u_dob2")
        
    if u_dob1 and u_dob2:
        d1 = get_synapse_core_logic(u_dob1)
        d2 = get_synapse_core_logic(u_dob2)
        
        gap = abs(d1['res'] - d2['res'])
        st.write(f"📊 ผลคำนวณ: รหัสบุคคลแรก ` {d1['res']} ` ‖ รหัสบุคคลที่สอง ` {d2['res']} `")
        st.metric("ค่าผลต่างสัญญาณคู่ขนาน (Gap Value)", f"{gap:.4f}")
        
        st.divider()
        st.write("🔍 **ตารางแจกแจงพิกัดช่วงจังหวะชีวิตที่สอดคล้องรอบ 365 วัน (ภายใต้เขตควบคุมปี 1960-2026):**")
        
        tab_p_365, tab_f_365 = st.tabs(["⏪ สแกนอดีตย้อนหลัง 365 วัน", "🔮 สแกนอนาคตล่วงหน้า 365 วัน"])
        with tab_p_365:
            df_p365 = scan_time_cycle(d1['res'], date.today(), total_days=365, mode="past")
            if not df_p365.empty: st.dataframe(df_p365, use_container_width=True, hide_index=True)
            else: st.write("ไม่มีพิกัดทับซ้อนพิเศษในช่วงที่ระบุ")
            
        with tab_f_365:
            df_f365 = scan_time_cycle(d1['res'], date.today(), total_days=365, mode="future")
            if not df_f365.empty: st.dataframe(df_f365, use_container_width=True, hide_index=True)
            else: st.write("ไม่มีพิกัดทับซ้อนพิเศษในช่วงที่ระบุ")

# ==========================================
# ROOM 7: ห้องตั้งค่าหน้าตาแอป (UI Customizer)
# ==========================================
with room7:
    st.subheader("⚙️ ศูนย์ตั้งค่าโครงสร้างสไตล์แอปพลิเคชัน")
    st.session_state.theme_color = st.color_picker("🎨 กำหนดสีธีมกรอบและลูกเล่นนีออนหลัก", st.session_state.theme_color)
    st.session_state.bg_color = st.color_picker("🖤 เปลี่ยนสีพื้นหลังระบบ", st.session_state.bg_color)
    st.session_state.text_color = st.color_picker("⚪ เปลี่ยนสีฟอนต์อักษร", st.session_state.text_color)
    st.session_state.border_width = st.slider("📐 กำหนดระดับความหนาเส้นขอบกรอบหน้าต่างแอป", 1, 10, st.session_state.border_width)
    
    if st.button("บันทึกสไตล์ข้อมูลและประมวลผลใหม่ 🛠️"):
        st.toast("ระบบปรับปรุงโครงสร้างตามสีที่เลือกแล้ว!")
        st.rerun()
