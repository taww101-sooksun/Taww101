import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time
import pandas as pd
import os

# --- 1. CONFIG & LOGO (ห้ามเอาออก) ---
logo_path = "logo3.jpg"
logo_exists = os.path.exists(logo_path)
st.set_page_config(
    page_title="SYNAPSE IDENTITY", 
    page_icon=logo_path if logo_exists else "🌐", 
    layout="wide"
)

# --- 2. INITIALIZE FIREBASE (แก้ Region ตามรูปที่ส่งมา) ---
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
        # ใช้ URL ตรงตามที่ Error แจ้งมาเป๊ะๆ
        target_url = "https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/"
        firebase_admin.initialize_app(cred, {'databaseURL': target_url})
        st.toast("✅ SYNAPSE CORE CONNECTED")
    except Exception as e:
        st.error(f"🚨 Connection Error: {e}")

# --- 3. เพลง AUTO-PLAY (ห้ามเอาออก) ---
def play_audio():
    link = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
    st.components.v1.html(f"""
        <audio id="synapse-audio" loop autoplay style="display:none;"><source src="{link}" type="audio/mpeg"></audio>
        <script>
            var audio = document.getElementById("synapse-audio");
            window.parent.document.addEventListener('click', function() {{ audio.play(); }}, {{ once: true }});
        </script>
    """, height=0)

# --- 4. LOGIC แชทส่วนตัว (ห้ามเอาออก) ---
def private_chat_logic(my_name, target_name, p_msg=None):
    try:
        pair = sorted([my_name, target_name])
        room_id = f"priv_{pair[0]}_{pair[1]}"
        ref = db.reference(f'private_rooms/{room_id}')
        
        if p_msg:
            ref.push({'name': my_name, 'msg': p_msg, 'ts': time.time()})
        
        raw_p_msgs = ref.get()
        if raw_p_msgs:
            msgs = list(raw_p_msgs.values()) if isinstance(raw_p_msgs, dict) else [m for m in raw_p_msgs if m]
            return sorted(msgs, key=lambda x: x.get('ts', 0))[-15:]
    except Exception as e:
        st.error(f"Chat Logic Error: {e}")
    return []

# --- 5. MULTI-LANGUAGE DATA (ห้ามเอาออก - 6 ภาษา) ---
LANG_DATA = {
    "TH": {"welcome": "ยินดีต้อนรับ", "core": "🚀 แกนหลัก", "radar": "🛰️ เรดาร์", "comms": "💬 สื่อสาร", "sys": "🧹 ระบบ", "lat": "ละติจูด", "lon": "ลองติจูด", "time": "เวลาของระบบ", "manual": "คู่มือ"},
    "EN": {"welcome": "Welcome", "core": "🚀 CORE", "radar": "🛰️ RADAR", "comms": "💬 COMMS", "sys": "🧹 SYSTEM", "lat": "LATITUDE", "lon": "LONGITUDE", "time": "SYS TIME", "manual": "MANUAL"},
    "JP": {"welcome": "ようこそ", "core": "🚀 コア", "radar": "🛰️ レーダー", "comms": "💬 通信", "sys": "🧹 システム", "lat": "緯度", "lon": "経度", "time": "システム時間", "manual": "マニュアル"},
    "CN": {"welcome": "欢迎", "core": "🚀 核心", "radar": "🛰️ 雷达", "comms": "💬 通讯", "sys": "🧹 系统", "lat": "纬度", "lon": "经度", "time": "系统时间", "manual": "手册"},
    "MM": {"welcome": "ကြိုဆိုပါတယ်", "core": "🚀 အဓိက", "radar": "🛰️ ရေဒါ", "comms": "💬 ဆက်သွယ်ရေး", "sys": "🧹 စနစ်", "lat": "လတ္တီတွဒ်", "lon": "လောင်ဂျီတွဒ်", "time": "စနစ်အချိန်", "manual": "လမ်းညွှန်"},
    "LA": {"welcome": "ຍິນດີຕ້ອນຮັບ", "core": "🚀 ແກນຫຼັກ", "radar": "🛰️ ເຣດາ", "comms": "💬 ສື່ສານ", "sys": "🧹 ລະບົບ", "lat": "ລະຕິຈູด", "lon": "ລောင်ຕິຈູດ", "time": "ເວລາລະບົບ", "manual": "ຄູ່ມື"}
}

# --- 6. SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = "AGENT_X"
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#00f2fe"
if 'lang' not in st.session_state: st.session_state.lang = "TH"

# --- 7. LOGIN UI (ห้ามเอาออก) ---
if not st.session_state.logged_in:
    if logo_exists: st.image(logo_path, width=400)
    st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color};'>🌐 SYNAPSE IDENTITY</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pw = st.text_input("SECURITY KEY", type="password")
        if st.button("🚀 ENTER SYSTEM"):
            if pw == "notty101":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("❌ Access Denied")
    st.markdown("<p style='text-align:center; color:#444; margin-top:50px;'><i>อยู่นิ่งๆ ไม่เจ็บตัว</i></p>", unsafe_allow_html=True)
    st.stop()

# --- 8. MAIN APP START ---
L = LANG_DATA[st.session_state.lang]
play_audio() # รันเพลง

st.markdown(f"<style>.stApp {{ background: #000; color: {st.session_state.theme_color}; }}</style>", unsafe_allow_html=True)

with st.sidebar:
    if logo_exists: st.image(logo_path, use_column_width=True)
    st.title("🌐 CONTROL")
    st.session_state.user_name = st.text_input("ID", st.session_state.user_name)
    st.session_state.lang = st.selectbox("LANGUAGE", list(LANG_DATA.keys()))
    st.session_state.theme_color = st.color_picker("THEME COLOR", st.session_state.theme_color)
    if st.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

# --- 9. TABS INTEGRATION ---
tabs = st.tabs([L["core"], L["radar"], L["comms"], L["sys"]])

with tabs[0]: # แกนหลัก
    st.header(f"{L['welcome']}, {st.session_state.user_name}")
    st.components.v1.html(f"""
        <div style="background:rgba(0,0,0,0.8); color:{st.session_state.theme_color}; padding:15px; border-radius:10px; border:1px solid {st.session_state.theme_color}; font-family:monospace;">
            <div style="display:flex; justify-content:space-between;">
                <div>📍 LAT/LON: <span id="g">...</span></div>
                <div>⏰ LOCAL: <span id="t">00:00:00</span></div>
            </div>
        </div>
        <script>
            setInterval(() => {{
                navigator.geolocation.getCurrentPosition(p => {{
                    document.getElementById('g').innerText = p.coords.latitude.toFixed(6) + ", " + p.coords.longitude.toFixed(6);
                }});
                document.getElementById('t').innerText = new Date().toLocaleTimeString('th-TH');
            }}, 1000);
        </script>
    """, height=100)
    if st.button("📢 BROADCAST SIGNAL"):
        db.reference('logs/activity').push({'user': st.session_state.user_name, 'ts': time.time()})
        st.toast("Signal Broadcasted!")

with tabs[1]: # เรดาร์
    st.subheader(L["radar"])
    col_a, col_b = st.columns(2)
    lat_v = col_a.number_input(L["lat"], value=13.7500)
    lon_v = col_b.number_input(L["lon"], value=100.5100)
    st.map(pd.DataFrame({'lat': [lat_v], 'lon': [lon_v]}), color=st.session_state.theme_color)

with tabs[2]: # สื่อสาร (แชท & วิดีโอ)
    st.subheader(L["comms"])
    target = st.text_input("แชทกับใคร:", value="User2")
    if st.button("📹 VIDEO CALL START"):
        st.components.v1.html("<video id='v' autoplay playsinline style='width:100%; border:2px solid #00f2fe; border-radius:10px; background:#000;'></video><script>navigator.mediaDevices.getUserMedia({video:true,audio:true}).then(s=>document.getElementById('v').srcObject=s)</script>", height=300)
    
    st.markdown("---")
    msgs = private_chat_logic(st.session_state.user_name, target)
    for m in msgs:
        st.write(f"**{m['name']}**: {m['msg']}")
    
    with st.form("chat_f", clear_on_submit=True):
        txt = st.text_input("พิมพ์ข้อความ...")
        if st.form_submit_button("ส่ง"):
            private_chat_logic(st.session_state.user_name, target, txt)
            st.rerun()

with tabs[3]: # ระบบ
    st.subheader(f"📖 {L['manual']}")
    st.write(f'Slogan: "อยู่นิ่งๆ ไม่เจ็บตัว"')
    if st.button("REBOOT CORE"):
        st.cache_resource.clear()
        st.rerun()
