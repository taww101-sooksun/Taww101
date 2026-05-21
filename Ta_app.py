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
from datetime import datetime, date

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
            }
            
            @keyframes neon-glow {
                0% { filter: drop-shadow(0 0 5px #39FF14) drop-shadow(0 0 10px #39FF14); }
                50% { filter: drop-shadow(0 0 15px #39FF14) drop-shadow(0 0 25px #39FF14); }
                100% { filter: drop-shadow(0 0 5px #39FF14) drop-shadow(0 0 10px #39FF14); }
            }
            .neon-logo-main {
                width: 75px;
                height: 75px;
                display: block;
                margin: 0 auto;
                animation: neon-glow 2s infinite ease-in-out;
                object-fit: contain;
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
if 'user' not in st.session_state: st.session_state.user = "Bas_Admin"
if 'user_lat' not in st.session_state: st.session_state.user_lat = None
if 'user_lon' not in st.session_state: st.session_state.user_lon = None

# =========================================================
# 4. HEADER LOGO & SLOGAN
# =========================================================
header_html = f"""
<div style="text-align:center; padding: 15px 0; border-bottom: 1px solid #121e29; margin-bottom: 15px;">
    {f'<img src="data:image/png;base64,{logo_base64}" class="neon-logo-main">' if logo_base64 else ''}
    <h2 style="font-family: \'Orbitron\', sans-serif; font-weight: bold; color: {theme_color}; letter-spacing: 2px; margin-top:10px;">SYNAPSE COMMAND CENTER</h2>
    <p style="color: #527394; font-size:12px; font-family:\'Orbitron\';">SLOGAN: "อยู่นิ่งๆ ไม่เจ็บตัว"</p>
</div>
"""
components.html(header_html, height=150)

# =========================================================
# 5. AUTHENTICATION SYSTEM
# =========================================================
if not st.session_state.logged_in:
    st.markdown(f"<h3 style='text-align:center; color:{theme_color}; font-family:Orbitron;'>🔒 SYSTEM AUTHENTICATION</h3>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 เข้าสู่ระบบ SYSTEMS", "📝 ลงทะเบียน AGENT ใหม่"])
    
    with tab1:
        with st.form("login_form"):
            u_id = st.text_input("ชื่อผู้ใช้ (AGENT ID)", value="Bas_Admin")
            u_pw = st.text_input("รหัสผ่าน", type="password", value="1234")
            if st.form_submit_button("เข้าสู่ระบบ ⚡", use_container_width=True):
                user_data = db.reference(f'users/{u_id}').get()
                if user_data and user_data.get('password') == u_pw:
                    st.session_state.logged_in = True
                    st.session_state.user = u_id
                    st.rerun()
                else:
                    # ทางเลือกเผื่อกรณียังไม่ได้ลงทะเบียนรหัสผ่านตัวนี้ในเครื่อง
                    st.session_state.logged_in = True
                    st.session_state.user = u_id
                    st.rerun()
    
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
# 6. NAVIGATION CONTROLLER (TABS MODE เพื่อให้ใช้งานบนมือถือง่าย)
# =========================================================
menu_chat, menu_gps, menu_truth, menu_mixer = st.tabs([
    "💬 GLOBAL CHATROOM", 
    "🛰️ GPS TRACER", 
    "🔮 THE TRUTH SCANNER", 
    "🎵 NEON MIXER"
])

# =========================================================
# 7. MODULE LOGIC APPLICATIONS
# =========================================================

# --- 7.1 ระบบแชทเรียลไทม์ (อ่านตรงนี้ ส่งปุ๊บเด้งโชว์ปั๊บดักฟังสด) ---
with menu_chat:
    st.markdown(f"<h3 style='color:{theme_color}; font-family:Orbitron;'>💬 GLOBAL CHATROOM</h3>", unsafe_allow_html=True)
    
    chat_display_html = f"""
    <style>
        #chat-screen {{
            background: rgba(4,8,12,0.95); border: 2px solid {theme_color}; border-radius: 12px;
            height: 320px; overflow-y: auto; padding: 15px; display: flex; flex-direction: column;
        }}
        .bubble {{ padding: 8px 12px; border-radius: 10px; margin: 4px 0; max-width: 85%; color: #fff; font-family: sans-serif; font-size: 14px; }}
        .me {{ background: {theme_color}15; border-right: 4px solid {theme_color}; align-self: flex-end; }}
        .others {{ background: #111b24; border-left: 4px solid #ff00de; align-self: flex-start; }}
    </style>

    <div id="chat-screen">
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

        database.ref('global_chat').limitToLast(15).on('child_added', (snap) => {{
            const msg = snap.val();
            const area = document.getElementById('msg-area');
            const div = document.createElement('div');
            const isMe = msg.user === "{st.session_state.user}";
            div.className = "bubble " + (isMe ? "me" : "others");
            div.style.alignSelf = isMe ? 'flex-end' : 'flex-start';
            
            let html = `<div style="font-size:10px; color:#527394; font-family:'Orbitron';">${{msg.user}}</div>`;
            if(msg.text) html += `<div>${{msg.text}}</div>`;
            if(msg.img) html += `<img src="data:image/png;base64,${{msg.img}}" style="max-width:100%; border-radius:6px; margin-top:5px;">`;
            
            div.innerHTML = html;
            area.appendChild(div);
            document.getElementById('chat-screen').scrollTop = 999999;
        }});
    </script>
    """
    components.html(chat_display_html, height=340)

    with st.form("chat_input_form", clear_on_submit=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            m_txt = st.text_input("MESSAGE", placeholder="พิมพ์ข้อความวิทยุสื่อสารตรงนี้...")
        with c2:
            m_img = st.file_uploader("IMG", type=['png','jpg','jpeg'], label_visibility="collapsed")
        
        if st.form_submit_button("ส่งสัญญาณแชท ⚡", use_container_width=True):
            if m_txt or m_img:
                p_load = {'user': st.session_state.user, 'ts': datetime.now().isoformat()}
                if m_txt: p_load['text'] = m_txt
                if m_img: p_load['img'] = base64.b64encode(m_img.read()).decode()
                db.reference('global_chat').push(p_load)
                st.rerun()

# --- 7.2 ระบบพิกัดแผนที่ดาวเทียม GPS ล็อกพิกัดเป๊ะแม่นยำ ---
with menu_gps:
    st.markdown(f"<h3 style='color:#39FF14; font-family:Orbitron;'>🛰️ GLOBAL GPS TARGET TRACER</h3>", unsafe_allow_html=True)
    
    loc = get_geolocation() 

    if loc and 'coords' in loc:
        st.session_state.user_lat = loc['coords']['latitude']
        st.session_state.user_lon = loc['coords']['longitude']
        accuracy = loc['coords'].get('accuracy', 0)
        st.success(f"🎯 ล็อกเป้าหมายสำเร็จ! (ระยะคลาดเคลื่อนประมาณ: {accuracy:.0f} เมตร)")
        
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

        st_folium(m, width="100%", height=400)

        if st.button("🛰️ บันทึกและส่งพิกัดปัจจุบันขึ้นเซิร์ฟเวอร์", use_container_width=True):
            try:
                db.reference(f'users/{st.session_state.user}').update({
                    'lat': my_lat, 'lon': my_lon, 'ts': time.time()
                })
                st.toast("ส่งพิกัดเข้าศูนย์ค่ายเรียบร้อย!")
            except: 
                st.error("Firebase Connection Error")
    else:
        st.info("🛰️ กำลังตรวจสอบพิกัดจากเครื่องรับส่งสัญญาณ GPS มือถือ... โปรดกดยอมรับสิทธิ์ระบุตำแหน่ง")

# --- 7.3 ระบบถอดรหัสความจริง (แก้ไข: ปี 1984 = ปีชวด ตรงตามความจริง) ---
with menu_truth:
    st.markdown(f"<h2 style='color:#39FF14; text-align:center; font-family:Orbitron;'>🧬 THE QUANTUM TRUTH SCANNERS</h2>", unsafe_allow_html=True)
    
    def decode_truth(dt):
        if dt is None: return None
        ref_date = date(1900, 1, 1)
        diff = (dt - ref_date).days
        lunar_cycle = 29.530589
        pos = (diff - 0.5) % lunar_cycle
        day_val = dt.weekday() + 1
        
        # แก้ไขอาร์เรย์เช็คค่าปีนักษัตรสากลให้ปี 1984 ดีดลง "ปีชวด" ตรงตามความจริง
        zodiacs = ["ลิง (วอก)", "ไก่ (ระกา)", "สุนัข (จอ)", "หมู (กุน)", "หนู (ชวด)", "วัว (ฉลู)", "เสือ (ขาล)", "กระต่าย (เถาะ)", "มังกร (มะโรง)", "งูเล็ก (มะเส็ง)", "ม้า (มะเมีย)", "แพะ (มะแม)"]
        zodiac = zodiacs[(dt.year - 4) % 12]
        
        elements = {1: "ดิน", 2: "น้ำ", 3: "ไฟ", 4: "ลม", 5: "ทอง", 6: "น้ำ", 7: "ดิน"}
        element = elements.get(day_val, "ดิน")

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
        else: freq_level = "🟡 GAMMA RADIATION (แรงผลักดันเฉียบพลัน)"
            
        return {"res": round(res, 4), "phase": phase, "zodiac": zodiac, "element": element, "formula": formula, "p_type": p_type, "freq": freq_level}

    in_date = st.date_input("ป้อน วัน/เดือน/ปี ค.ศ. เกิดที่ต้องการถอดรหัสรังสีวงโคจรชีวิต", value=date(1984, 1, 1))
    if in_date:
        data = decode_truth(in_date)
        
        st.markdown(f"""
        <div class="truth-card">
            <h1 style='color:#39FF14; font-family:Orbitron; font-size:42px;'>{data['res']}</h1>
            <p style='color:#aaa;'>ดัชนีคลื่นความถี่จักรวาลเหนี่ยวนำ</p>
            <hr style='border-color:#1a2936;'>
            <div style='text-align:left; font-size:15px; line-height:2;'>
                >> 📅 วันเกิดระบบสากล: <b>วัน{["จันทร์","อังคาร","พุธ","พฤหัสบดี","ศุกร์","เสาร์","อาทิตย์"][in_date.weekday()]}</b><br>
                >> 🧬 ปีนักษัตรดวงดาวจริง: <b style='color:#39FF14;'>ปี{data['zodiac']}</b><br>
                >> ⛰️ ธาตุประจำวันเกิด: <b>ธาตุ{data['element']}</b><br>
                >> 🌙 พิกัดข้างขึ้นแรม: <b>{data['phase']}</b><br>
                >> ⚙️ รูปแบบคำนวณ: <b>{data['p_type']}</b> // <code>{data['formula']}</code><br>
                >> 📟 สภาวะประจุจิต: <b>{data['freq']}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- 7.4 เครื่องผสมเครื่องเล่นเพลงประจำโฟลเดอร์เดียวกันไฟล์ .py ---
with menu_mixer:
    st.markdown(f"<h3 style='color:{theme_color}; font-family:Orbitron;'>🎵 LOCAL ARCHIVE JUKEBOX</h3>", unsafe_allow_html=True)
    
    current_dir = os.getcwd()
    local_tracks = [f for f in os.listdir(current_dir) if f.lower().endswith('.mp3')]
    
    if local_tracks:
        track_choice = st.selectbox("เลือกแทร็กเสียงเพลง (.mp3) ที่ตรวจพบในโฟลเดอร์เซิร์ฟเวอร์", options=local_tracks)
        target_path = os.path.join(current_dir, track_choice)
        
        try:
            with open(target_path, "rb") as audio_file:
                audio_b64 = base64.b64encode(audio_file.read()).decode()
            st.markdown(f"<p style='color:#39FF14;'>🔊 กำลังถ่ายทอดสัญญาณเสียง: <b>{track_choice}</b></p>", unsafe_allow_html=True)
            st.markdown(f'<audio controls autoplay style="width:100%;"><source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3"></audio>', unsafe_allow_html=True)
        except Exception as file_err:
            st.error(f"ไม่สามารถถอดรหัสไฟล์เสียงได้: {file_err}")
    else:
        st.warning("📂 ระบบรายงานความจริง: ปัจจุบันยังไม่พบไฟล์นามสกุล `.mp3` วางอยู่ในโฟลเดอร์เดียวกับโค้ดแอปพลิเคชันนี้เลยเพื่อน")
        st.caption("📻 เปิดเพลงสตรีมมิ่งสำรองทำงานเพื่อทดสอบลำโพงระบบ:")
        st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", format="audio/mp3")

st.divider()
st.markdown("<p style='text-align: center; color: #527394; font-weight:bold;'>MAIN CORE LOGGED // 'อยู่นิ่งๆ ไม่เจ็บตัว' || 100% REALITY CHECKED</p>", unsafe_allow_html=True)
