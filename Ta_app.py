import streamlit as st
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
import firebase_admin
from firebase_admin import credentials, db
import math
import time
import base64

# --- 1. ตั้งค่าพื้นฐาน ---
st.set_page_config(page_title="SYNAPSE COMMAND", layout="wide")

st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background-color: #0e1117; }
    
    @keyframes neon-import streamlit as st
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

# =========================================================
# 1. CONFIG & HIGH-LEVEL NEON UI INITIALIZATION
# =========================================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")

def inject_cyberpunk_ui():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Sarabun:wght@300;500&display=swap');
            
            .stApp { 
                background: radial-gradient(circle at 50% 50%, #080f14 0%, #030508 100%) !important;
                font-family: 'Sarabun', sans-serif;
                color: #e0e0e0;
            }
            
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp { top: -60px; }
            
            .stTabs [data-baseweb="tab-list"] { gap: 12px; }
            .stTabs [data-baseweb="tab"] {
                background-color: #0b1116; border: 1px solid #1a2936;
                border-radius: 8px; padding: 12px 24px; color: #666;
                font-family: 'Orbitron', sans-serif; transition: 0.3s;
            }
            .stTabs [aria-selected="true"] {
                background-color: rgba(57, 255, 20, 0.1) !important;
                border-color: #39FF14 !important; color: #39FF14 !important;
                box-shadow: 0 0 15px rgba(57, 255, 20, 0.3);
            }
            
            .stTextInput>div>div>input, .stForm {
                background-color: #090e12 !important;
                border: 1px solid #1a2936 !important;
                color: #fff !important;
                border-radius: 8px !important;
            }
            .stTextInput>div>div>input:focus {
                border-color: #39FF14 !important;
                box-shadow: 0 0 10px rgba(57, 255, 20, 0.5) !important;
            }
            
            .truth-card {
                background: linear-gradient(135deg, rgba(11,20,28,0.9) 0%, rgba(4,8,12,0.95) 100%);
                border: 2px solid #39FF14;
                border-radius: 16px;
                padding: 25px;
                text-align: center;
                box-shadow: 0 0 25px rgba(57, 255, 20, 0.15), inset 0 0 15px rgba(57, 255, 20, 0.1);
                margin: 15px 0;
            }
            
            .logic-stream-box {
                background-color: #060a0d;
                border-left: 4px solid #ff00de;
                padding: 15px;
                border-radius: 0 8px 8px 0;
                color: #a3b8cc;
                font-size: 13px;
                margin-bottom: 15px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            }
            
            .stDataFrame {
                border: 1px solid #1a2936 !important;
                border-radius: 10px !important;
                background-color: #05080b !important;
            }
        </style>
    """, unsafe_allow_html=True)

inject_cyberpunk_ui()

def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

logo_base64 = get_base64("logo1.png")
audio_data = get_base64("notification.mp3")
theme_color = "#39FF14"

# =========================================================
# 2. FIREBASE CONNECTION
# =========================================================
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_credentials"])
        fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
    except Exception as e:
        st.error(f"การเชื่อมต่อฐานข้อมูลผิดพลาด: {e}")

# =========================================================
# 3. SESSION STATE CONFIGURATION
# =========================================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None
if 'user_lat' not in st.session_state: st.session_state.user_lat = None
if 'user_lon' not in st.session_state: st.session_state.user_lon = None

# =========================================================
# 4. HEADER LOGO & SLOGAN WINKING
# =========================================================
header_html = f"""
<style>
    @keyframes dance {{
        0% {{ transform: translate(0, 0) rotate(0deg); }}
        25% {{ transform: translate(1px, -1px) rotate(1deg); }}
        50% {{ transform: translate(-1px, 1px) rotate(-1deg); }}
        100% {{ transform: translate(0, 0) rotate(0deg); }}
    }}
    @keyframes wink {{
        0%, 100% {{ opacity: 1; color: {theme_color}; text-shadow: 0 0 12px {theme_color}; }}
        50% {{ opacity: 0.3; color: #fff; text-shadow: none; }}
    }}
    .logo-container {{ display: flex; align-items: center; justify-content: center; padding: 15px 0; border-bottom: 1px solid #121e29; margin-bottom: 15px; }}
    .logo-img {{ width: 70px; height: 70px; animation: dance 1s infinite ease-in-out; object-fit: contain; }}
    .slogan-txt {{ 
        font-family: 'Orbitron', sans-serif; font-weight: bold; font-size: 20px; letter-spacing: 2px;
        margin-left: 15px; animation: wink 2s infinite; 
    }}
</style>
<div class="logo-container">
    {f'<img src="data:image/png;base64,{logo_base64}" class="logo-img">' if logo_base64 else ''}
    <span class="slogan-txt">SYNAPSE COMMAND CENTER</span>
</div>
"""
components.html(header_html, height=110)

# =========================================================
# 5. AUTHENTICATION SYSTEM (LOGIN / REGISTER)
# =========================================================
if not st.session_state.logged_in:
    st.markdown(f"<h3 style='text-align:center; color:{theme_color}; font-family:Orbitron;'>🔒 SYSTEM AUTHENTICATION</h3>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 เข้าสู่ระบบ SYSTEMS", "📝 ลงทะเบียน AGENT ใหม่"])
    
    with tab1:
        with st.form("login_form"):
            u_id = st.text_input("ชื่อผู้ใช้ (AGENT ID)")
            u_pw = st.text_input("รหัสผ่าน", type="password")
            if st.form_submit_button("เข้าสู่ระบบ ⚡", use_container_width=True):
                user_data = db.reference(f'users/{u_id}').get()
                if user_data and user_data.get('password') == u_pw:
                    st.session_state.logged_in = True
                    st.session_state.user = u_id
                    st.rerun()
                else:
                    st.error("ข้อมูลตรวจสอบความปลอดภัยไม่ถูกต้อง")
    
    with tab2:
        with st.form("reg_form"):
            new_u = st.text_input("ตั้งชื่อผู้ใช้ใหม่")
            new_p = st.text_input("ตั้งรหัสผ่าน", type="password")
            if st.form_submit_button("สร้างบัญชี AGENT"):
                if new_u and new_p:
                    db.reference(f'users/{new_u}').set({'password': new_p, 'created_at': datetime.now().isoformat()})
                    st.success("ลงทะเบียนสำเร็จ! กรุณาสลับไปหน้าเข้าสู่ระบบเพื่อใช้งาน")
    st.stop()

st.markdown(f"<div style='text-align:right; color:{theme_color}; font-family:Orbitron; font-size:12px; padding-right:10px;'>📡 AGENT OUTPOST: {st.session_state.user}</div>", unsafe_allow_html=True)

# =========================================================
# 6. NAVIGATION CONTROLLER
# =========================================================
st.markdown("<h5 style='color:#6886a3; font-family:Orbitron; margin-bottom:5px;'>🎛️ NAVIGATION CONTROLLER</h5>", unsafe_allow_html=True)
menu_choice = st.radio(
    "เลือกฟังก์ชันระบบ:", 
    ["💬 GLOBAL CHATROOM", "🛰️ GPS TRACER", "🔮 THE TRUTH SCANNER", "🎵 NEON MIXER"],
    horizontal=True,
    key="main_menu_navigator",
    label_visibility="collapsed"
)

st.divider()

if st.sidebar.button("🔴 ออกจากระบบ (LOGOUT)", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# =========================================================
# 7. MODULE LOGIC APPLICATIONS
# =========================================================

# --- 7.1 ระบบแชทเรียลไทม์ ---
if menu_choice == "💬 GLOBAL CHATROOM":
    st.markdown(f"<h3 style='color:{theme_color}; font-family:Orbitron;'>💬 GLOBAL CHATROOM</h3>", unsafe_allow_html=True)
    
    chat_display_html = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    #chat-screen {{
        background: rgba(4,8,12,0.95); border: 2px solid {theme_color}; border-radius: 12px;
        height: 380px; overflow-y: auto; padding: 15px; display: flex; flex-direction: column;
        box-shadow: inset 0 0 15px {theme_color}22;
    }}
    .bubble {{ padding: 10px 15px; border-radius: 10px; margin: 6px 0; max-width: 85%; color: #fff; font-family: sans-serif; font-size: 14px; line-height: 1.4; }}
    .me {{ background: {theme_color}15; border-right: 4px solid {theme_color}; align-self: flex-end; }}
    .others {{ background: #111b24; border-left: 4px solid #ff00de; align-self: flex-start; }}
    .notif-box {{ background: #162533; color: #888; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-family: 'Orbitron'; }}
    .alert-red {{ background: #ff0055 !important; color: white; box-shadow: 0 0 10px #ff0055; font-weight: bold; }}
</style>

<div id="chat-screen">
    <div style="display:flex; justify-content:space-between; margin-bottom:12px; border-bottom: 1px solid #1a2936; padding-bottom: 5px;">
        <span style="color:{theme_color}; font-family:'Orbitron'; font-size:10px; letter-spacing: 2px;">📡 LINK_ESTABLISHED</span>
        <span id="notif-box" class="notif-box">0 SIGNAL</span>
    </div>
    <div id="msg-area" style="display:flex; flex-direction:column;"></div>
</div>

<audio id="notif-sound" preload="auto">
    <source src="data:audio/mp3;base64,{audio_data}" type="audio/mp3">
</audio>

<script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
<script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
<script>
    const fb_conf = {{ databaseURL: "{st.secrets['firebase_db_url']}" }};
    if(!firebase.apps.length) firebase.initializeApp(fb_conf);
    const database = firebase.database();
    let lastCount = -1;
    const beep = document.getElementById('notif-sound');

    function unlock() {{
        beep.play().then(() => {{ beep.pause(); beep.currentTime = 0; }});
        window.removeEventListener('click', unlock);
        window.removeEventListener('touchstart', unlock);
    }}
    window.addEventListener('click', unlock);
    window.addEventListener('touchstart', unlock);

    database.ref('global_chat').limitToLast(25).on('child_added', (snap) => {{
        const msg = snap.val();
        const area = document.getElementById('msg-area');
        const div = document.createElement('div');
        const isMe = msg.user === "{st.session_state.user}";
        div.className = "bubble " + (isMe ? "me" : "others");
        div.style.alignSelf = isMe ? 'flex-end' : 'flex-start';
        
        let html = `<div style="font-size:10px; color:#527394; font-family:'Orbitron'; margin-bottom:4px;">${{msg.user}}</div>`;
        if(msg.text) html += `<div>${{msg.text}}</div>`;
        if(msg.img) html += `<img src="data:image/png;base64,${{msg.img}}" style="max-width:100%; border-radius:6px; margin-top:6px; border: 1px solid #1a2936;">`;
        
        div.innerHTML = html;
        area.appendChild(div);
        document.getElementById('chat-screen').scrollTop = 999999;
    }});

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
    components.html(chat_display_html, height=410)

    with st.container():
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            m_txt = st.text_input("MESSAGE", placeholder="ส่งข้อความคลื่นวิทยุ...", label_visibility="collapsed", key="msg_input")
        with c2:
            m_img = st.file_uploader("IMAGE", type=['png','jpg','jpeg'], label_visibility="collapsed", key="img_upload")
        with c3:
            if st.button("ส่งสัญญาณ ⚡", use_container_width=True):
                if m_txt or m_img:
                    p_load = {'user': st.session_state.user, 'ts': datetime.now().isoformat()}
                    if m_txt: p_load['text'] = m_txt
                    if m_img: p_load['img'] = base64.b64encode(m_img.read()).decode()
                    db.reference('global_chat').push(p_load)
                    
                    cur = db.reference('chat_notifications/unread_count').get() or 0
                    db.reference('chat_notifications').set({'unread_count': cur + 1})
                    st.rerun()

    st.divider()
    if st.button("🧼 RESET NOTIFICATION COUNT", use_container_width=True):
        db.reference('chat_notifications').set({'unread_count': 0})
        st.rerun()

# --- 7.2 ระบบแผนที่ดาวเทียม GPS ---
elif menu_choice == "🛰️ GPS TRACER":
    st.markdown(f"<h3 style='color:#00FF00; font-family:Orbitron;'>🛰️ GLOBAL GPS TARGET TRACER</h3>", unsafe_allow_html=True)
    
    loc = get_geolocation() 

    if loc and 'coords' in loc:
        st.session_state.user_lat = loc['coords']['latitude']
        st.session_state.user_lon = loc['coords']['longitude']
        accuracy = loc['coords'].get('accuracy', 0)
        st.success(f"🎯 ดาวเทียมล็อกเป้าพิกัดสำเร็จ! (ขอบเขตคลาดเคลื่อนต่ำสุด: {accuracy:.0f} เมตร)")
        
        my_lat = st.session_state.user_lat
        my_lon = st.session_state.user_lon

        m = folium.Map(
            location=[my_lat, my_lon], 
            zoom_start=18, 
            tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
            attr='Google Maps'
        )

        folium.Marker(
            [my_lat, my_lon], 
            icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
        ).add_to(m)

        st_folium(m, width="100%", height=450)

        if st.button("🛰️ ทำการซิงค์ข้อมูลส่งขึ้นระบบคลาวด์ Firebase", use_container_width=True):
            try:
                db.reference(f'users/{st.session_state.user}').update({
                    'lat': my_lat, 'lon': my_lon, 'ts': time.time()
                })
                st.toast("อัปเดตข้อมูลตำแหน่งเข้าเซิร์ฟเวอร์กลางแล้ว")
            except: 
                st.error("ไม่สามารถเชื่อมต่อฐานข้อมูลปลายทางได้")
    else:
        st.info("🛰️ กำลังตรวจสอบสัญญาณจีพีเอสจากเครื่องโทรศัพท์... โปรดกดยอมรับสิทธิ์การเข้าถึงตำแหน่งอุปกรณ์ด้วยครับ")

# --- 7.3 ระบบคำนวณถอดรหัสความจริง ---
elif menu_choice == "🔮 THE TRUTH SCANNER":
    st.markdown(f"<h2 style='color:#39FF14; text-shadow: 0 0 15px rgba(57,255,20,0.4); text-align:center; font-family:Orbitron;'>🧬 THE QUANTUM TRUTH SCANNERS</h2>", unsafe_allow_html=True)
    
    def decode_truth(dt):
        if dt is None: return None
        ref_date = date(1900, 1, 1)
        diff = (dt - ref_date).days
        lunar_cycle = 29.530589
        pos = (diff - 0.5) % lunar_cycle
        day_val = dt.weekday() + 1
        
        thai_year = dt.year + 543
        zodiacs = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
        zodiac = zodiacs[thai_year % 12]
        
        elements = {1: "ดิน", 2: "น้ำ", 3: "ไฟ", 4: "ลม", 5: "ทอง", 6: "น้ำ", 7: "ดิน"}
        element = elements.get(day_val)

        is_waxing = pos <= 14.765
        m_num = int(pos) + 1 if is_waxing else int(pos - 14.765) + 1
        phase = f"{'ขึ้น' if is_waxing else 'แรม'} {m_num} ค่ำ"

        if is_waxing:
            res = math.sqrt((day_val**2) + (m_num**2))
            formula = f"√({day_val}² + {m_num}²)"
            p_type = "แรงผลักดันเวกเตอร์ (Vector)"
        else:
            res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
            formula = f"({day_val} × 1.618) / {m_num}"
            p_type = "สมดุลสัดส่วนทองคำ (Golden Ratio)"
            
        if res < 2.5: freq_level = "🟢 ALPHA CONSTANT (สงบนิ่งเสถียร)"
        elif 2.5 <= res < 5.0: freq_level = "🔵 BETA WAVE (พลังงานปฏิสัมพันธ์สูง)"
        elif 5.0 <= res < 9.0: freq_level = "🟡 GAMMA RADIATION (แรงผลักดันเฉียบพลัน) {
        0% { filter: drop-shadow(0 0 5px #00FF00) drop-shadow(0 0 10px #00FF00); }
        50% { filter: drop-shadow(0 0 15px #00FF00) drop-shadow(0 0 25px #00FF00); }
        100% { filter: drop-shadow(0 0 5px #00FF00) drop-shadow(0 0 10px #00FF00); }
    }
    .neon-logo-main {
        width: 150px;
        display: block;
        margin: 0 auto 20px auto;
        animation: neon-glow 2s infinite ease-in-out;
    }
    </style>
    """, unsafe_allow_html=True)

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return None

# --- 2. แสดงโลโก้ที่ "หน้าหลัก" (เพื่อให้เห็นทันที) ---
logo_data = get_base64_image("logo1.png")
if logo_data:
    st.markdown(f'<img src="data:image/png;base64,{logo_data}" class="neon-logo-main">', unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align: center; color: #00FF00;'>SYNAPSE</h1>", unsafe_allow_html=True)
# --- 3. ระบบดึงพิกัดจริง (No Default) ---

# ใช้ Session State เก็บค่า เพื่อไม่ให้แผนที่รีเฟรชหายไปมาระหว่างรอ
if 'user_lat' not in st.session_state:
    st.session_state.user_lat = None
    st.session_state.user_lon = None

# ดึงพิกัดจากเครื่อง
loc = get_geolocation() 

if loc and 'coords' in loc:
    # อัปเดตพิกัดจริงเข้าตัวแปรล็อก
    st.session_state.user_lat = loc['coords']['latitude']
    st.session_state.user_lon = loc['coords']['longitude']
    accuracy = loc['coords'].get('accuracy', 0)
    
    st.success(f"🎯 ล็อกเป้าหมายสำเร็จ! (แม่นยำในระยะ {accuracy:.0f} เมตร)")
else:
    st.info("🛰️ กำลังค้นหาสัญญาณดาวเทียมจากมือถือคุณ... กรุณาเปิด GPS และรอสักครู่")
    # หยุดการทำงานไว้ตรงนี้จนกว่าพิกัดจะมา (ป้องกันแผนที่ดีดไปที่อื่น)
    st.stop() 

my_lat = st.session_state.user_lat
my_lon = st.session_state.user_lon


# --- 4. แผนที่ Google Hybrid ---
# ตอนนี้ my_lat จะมีค่าแน่นอน ไม่ Error แล้วครับ
m = folium.Map(
    location=[my_lat, my_lon], 
    zoom_start=18, 
    tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', 
    attr='Google Maps'
)


folium.Marker(
    [my_lat, my_lon], 
    icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
).add_to(m)

st_folium(m, width="100%", height=500)

if st.button("🛰️ บันทึกและส่งพิกัดปัจจุบัน", use_container_width=True):
    try:
        db.reference(f'users/Bas_Admin').update({
            'lat': my_lat, 'lon': my_lon, 'ts': time.time()
        })
        st.toast("ส่งพิกัดเข้าดาวเทียมแล้ว!")
    except: st.error("Firebase Connection Error")
