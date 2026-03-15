import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time
import pandas as pd
import os

# --- 1. CONFIGURATION & LOGO SETUP (ตำแหน่ง B: Favicon) ---
logo_path = "logo3.jpg"
logo_exists = os.path.exists(logo_path)

st.set_page_config(
    page_title="SYNAPSE IDENTITY",
    page_icon=logo_path if logo_exists else "🌐",
    layout="wide"
)

# --- 2. INITIALIZE FIREBASE (ยึดตามรูป Admin SDK และ Region Singapore) ---
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        try:
            fb_config = {
                "type": "service_account",
                "project_id": st.secrets["project_id"],
                "private_key": st.secrets["private_key"].replace('\\n', '\n'),
                "client_email": st.secrets["client_email"],
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            cred = credentials.Certificate(fb_config)
            # URL ตัวนี้ต้องตรงกับหน้า Console ของคุณ (Region Singapore)
            target_url = "https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/"
            firebase_admin.initialize_app(cred, {'databaseURL': target_url})
            return True
        except Exception as e:
            st.error(f"🚨 เชื่อมต่อ Firebase ไม่ได้: {e}")
            return False
    return True

init_firebase()

# --- 3. ฟังก์ชันเล่นเสียง (Auto-play ตามที่คุณส่งมา) ---
def play_audio():
    link = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
    st.components.v1.html(f"""
        <audio id="synapse-audio" loop autoplay style="display:none;"><source src="{link}" type="audio/mpeg"></audio>
        <script>
            var audio = document.getElementById("synapse-audio");
            window.parent.document.addEventListener('click', function() {{ audio.play(); }}, {{ once: true }});
        </script>
    """, height=0)
    return link

# --- 4. LOGIC แชทส่วนตัว (จากโค้ดเดิมของคุณ) ---
def private_chat_logic(my_name, target_name, p_msg=None):
    pair = sorted([my_name, target_name])
    room_id = f"priv_{pair[0]}_{pair[1]}"
    
    try:
        ref = db.reference(f'private_rooms/{room_id}')
        if p_msg:
            ref.push({
                'name': my_name, 'msg': p_msg, 'ts': time.time()
            })
        
        raw_p_msgs = ref.get()
        if raw_p_msgs:
            if isinstance(raw_p_msgs, dict):
                msgs_list = list(raw_p_msgs.values())
            else:
                msgs_list = [m for m in raw_p_msgs if m is not None]
            return sorted(msgs_list, key=lambda x: x.get('ts', 0))[-10:]
    except Exception as e:
        st.error(f"Chat Logic Error: {e}")
    return []

# --- 5. MULTI-LANGUAGE DATA (6 ภาษา) ---
LANG_DATA = {
    "TH": {"welcome": "ยินดีต้อนรับ", "core": "🚀 แกนหลัก", "radar": "🛰️ เรดาร์", "comms": "💬 สื่อสาร", "sys": "🧹 ระบบ", "lat": "ละติจูด", "lon": "ลองติจูด", "time": "เวลาของระบบ", "manual": "คู่มือ"},
    "EN": {"welcome": "Welcome", "core": "🚀 CORE", "radar": "🛰️ RADAR", "comms": "💬 COMMS", "sys": "🧹 SYSTEM", "lat": "LATITUDE", "lon": "LONGITUDE", "time": "SYS TIME", "manual": "MANUAL"},
    "JP": {"welcome": "ようこそ", "core": "🚀 コア", "radar": "🛰️ レーダー", "comms": "💬 通信", "sys": "🧹 システム", "lat": "緯度", "lon": "経度", "time": "システム時間", "manual": "マニュアル"},
    "CN": {"welcome": "欢迎", "core": "🚀 核心", "radar": "🛰️ 雷达", "comms": "💬 通讯", "sys": "🧹 系统", "lat": "纬度", "lon": "经度", "time": "系统时间", "manual": "手册"},
    "MM": {"welcome": "ကြိုဆိုပါတယ်", "core": "🚀 အဓိက", "radar": "🛰️ ရေဒါ", "comms": "💬 ဆက်သွယ်ရေး", "sys": "🧹 စနစ်", "lat": "လတ္တီတွဒ်", "lon": "လောင်ဂျီတွဒ်", "time": "စနစ်အချိန်", "manual": "လမ်းညွှန်"},
    "LA": {"welcome": "ຍິນດີຕ້ອນຮັບ", "core": "🚀 ແກນຫຼັກ", "radar": "🛰️ ເຣດາ", "comms": "💬 ສື່ສານ", "login": "ເຂົ້າສູ່ລະບົບ", "sys": "🧹 ລະບົບ", "lat": "ລະຕິຈູด", "lon": "ລောင်ຕິຈູດ", "time": "ເວລາລະບົບ", "manual": "ຄູ່ມື"}
}

# --- 6. SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = "AGENT_X"
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#00f2fe"
if 'lang' not in st.session_state: st.session_state.lang = "TH"

# --- 7. LOGIN UI ---
def login_ui():
    if logo_exists:
        st.image(logo_path, width=400) 
    
    st.markdown(f"""
        <div style="text-align: center; padding: 20px; border: 1px solid {st.session_state.theme_color}; border-radius: 15px; background: rgba(0,0,0,0.5);">
            <h1 style="color:{st.session_state.theme_color}; margin-bottom:0;">🌐 SYNAPSE IDENTITY</h1>
            <p style="color:#888;">NEURAL NETWORK INTERFACE SYSTEM</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        password = st.text_input("SECURITY KEY REQUIRED", type="password", placeholder="กรุณาใส่รหัสผ่าน...")
        if st.button("🚀 ENTER SYSTEM"):
            if password == "notty101": 
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ Access Denied")
    
    st.markdown(f"<p style='text-align:center; color:#444; margin-top:50px;'><i>อยู่นิ่งๆ ไม่เจ็บตัว</i></p>", unsafe_allow_html=True)
    st.stop()

if not st.session_state.logged_in:
    login_ui()

# --- 8. MAIN UI SETUP ---
L = LANG_DATA[st.session_state.lang]
play_audio() # รันเพลงวนลูป

st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; }}
    .stButton>button {{ border: 1px solid {st.session_state.theme_color}; color: {st.session_state.theme_color}; background: transparent; width: 100%; border-radius: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 9. SIDEBAR ---
with st.sidebar:
    if logo_exists: st.image(logo_path, use_column_width=True)
    st.title("🌐 CONTROL")
    st.session_state.user_name = st.text_input("ID", st.session_state.user_name)
    st.session_state.lang = st.selectbox("LANGUAGE", list(LANG_DATA.keys()))
    st.session_state.theme_color = st.color_picker("THEME COLOR", st.session_state.theme_color)
    st.markdown("---")
    st.write('**Slogan:** "อยู่นิ่งๆ ไม่เจ็บตัว"')
    if st.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

# --- 10. MAIN TABS (GPS, Radar, Comms, Sys) ---
tabs = st.tabs([L["core"], L["radar"], L["comms"], L["sys"]])

# TAB 0: แกนหลัก (เพิ่ม GPS & เวลาเรียลไทม์)
with tabs[0]:
    st.header(f"{L['welcome']}, {st.session_state.user_name}")
    st.components.v1.html(f"""
        <div style="background: rgba(0,0,0,0.8); color: {st.session_state.theme_color}; padding: 15px; border-radius: 10px; border: 1px solid {st.session_state.theme_color}; font-family: monospace;">
            <div style="display: flex; justify-content: space-between;">
                <div>🛰️ LAT/LON: <span id="gps-raw">SEARCHING...</span></div>
                <div>⏰ LOCAL: <span id="time-raw">--:--:--</span></div>
            </div>
        </div>
        <script>
            function update() {{
                navigator.geolocation.getCurrentPosition(p => {{
                    document.getElementById('gps-raw').innerText = p.coords.latitude.toFixed(6) + ", " + p.coords.longitude.toFixed(6);
                }});
                document.getElementById('time-raw').innerText = new Date().toLocaleTimeString('th-TH');
            }}
            setInterval(update, 1000);
        </script>
    """, height=100)
    
    if st.button("📢 BROADCAST SIGNAL"):
        db.reference('logs/activity').push({'user': st.session_state.user_name, 'ts': time.time()})
        st.toast("Signal Broadcasted!")

# TAB 1: เรดาร์
with tabs[1]:
    st.subheader(L["radar"])
    col_a, col_b = st.columns(2)
    lat_val = col_a.number_input(L["lat"], value=13.7500, format="%.4f")
    lon_val = col_b.number_input(L["lon"], value=100.5100, format="%.4f")
    st.map(pd.DataFrame({'lat': [lat_val], 'lon': [lon_val]}), color=st.session_state.theme_color)

# TAB 2: สื่อสาร (แชทส่วนตัว + วิดีโอคอล)
with tabs[2]:
    st.subheader(L["comms"])
    target_name = st.text_input("แชทกับใคร:", value="User2")
    
    if st.button("📹 VIDEO CALL START"):
        st.components.v1.html("""
            <video id="v" autoplay playsinline style="width:100%; border:2px solid #00f2fe; border-radius:10px; background:#000;"></video>
            <script>
                navigator.mediaDevices.getUserMedia({video:true, audio:true}).then(s => {document.getElementById('v').srcObject = s;});
            </script>
        """, height=300)

    st.markdown("---")
    msgs = private_chat_logic(st.session_state.user_name, target_name)
    for m in msgs:
        align = "right" if m['name'] == st.session_state.user_name else "left"
        st.markdown(f"<div style='text-align:{align}; color:#fff;'><b>{m['name']}</b>: {m['msg']}</div>", unsafe_allow_html=True)
    
    with st.form("chat_p", clear_on_submit=True):
        p_msg = st.text_input("พิมพ์ข้อความ...")
        if st.form_submit_button("ส่ง"):
            private_chat_logic(st.session_state.user_name, target_name, p_msg)
            st.rerun()

# TAB 3: ระบบ & คู่มือ
with tabs[3]:
    st.subheader(f"📖 {L['manual']}")
    with st.expander("เปิดอ่านคู่มือการใช้งาน"):
        st.write(f"1. ใส่รหัส 'notty101' เพื่อเข้าเครื่อง")
        st.write(f"2. หน้า {L['core']} ใช้ส่งสัญญาณยืนยันตัวตน")
        st.write(f"3. หน้า {L['radar']} ใช้ปักหมุดตำแหน่ง")
        st.write(f"4. หน้า {L['comms']} ใช้สำหรับติดต่อสื่อสารส่วนตัวและวิดีโอ")
    
    if st.button("REBOOT CORE"):
        st.cache_resource.clear()
        st.rerun()
