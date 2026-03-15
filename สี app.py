import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time
import pandas as pd
import os

# --- 1. CONFIGURATION & LOGO SETUP (คงไว้ตามเดิม) ---
logo_path = "logo3.jpg"
logo_exists = os.path.exists(logo_path)

st.set_page_config(
    page_title="SYNAPSE IDENTITY",
    page_icon=logo_path if logo_exists else "🌐",
    layout="wide"
)

# --- 2. INITIALIZE FIREBASE (ปรับปรุงให้ใช้ Service Account และ URL ที่ถูกต้อง) ---
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
        # ใช้ URL ตามที่คุณระบุ (Singapore Region)
        target_url = "https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/"
        firebase_admin.initialize_app(cred, {'databaseURL': target_url})
    except Exception as e:
        st.error(f"🚨 เชื่อมต่อ Firebase ไม่ได้: {e}")

# --- 3. ฟังก์ชันเล่นเสียง (Auto-play ที่คุณต้องการ) ---
def play_audio():
    link = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
    st.components.v1.html(f"""
        <audio id="synapse-audio" loop autoplay style="display:none;"><source src="{link}" type="audio/mpeg"></audio>
        <script>
            var audio = document.getElementById("synapse-audio");
            window.parent.document.addEventListener('click', function() {{ audio.play(); }}, {{ once: true }});
        </script>
    """, height=0)

# --- 4. LOGIC แชทส่วนตัว (Logic เดิมของคุณเป๊ะๆ) ---
def private_chat_logic(my_name, target_name, p_msg=None):
    pair = sorted([my_name, target_name])
    room_id = f"priv_{pair[0]}_{pair[1]}"
    if p_msg:
        db.reference(f'private_rooms/{room_id}').push({
            'name': my_name, 'msg': p_msg, 'ts': time.time()
        })
    raw_p_msgs = db.reference(f'private_rooms/{room_id}').get()
    if raw_p_msgs:
        if isinstance(raw_p_msgs, dict):
            msgs_list = list(raw_p_msgs.values())
        else:
            msgs_list = [m for m in raw_p_msgs if m is not None]
        return sorted(msgs_list, key=lambda x: x.get('ts', 0))[-15:]
    return []

# --- 5. MULTI-LANGUAGE DATA (คงเดิม) ---
LANG_DATA = {
    "TH": {"welcome": "ยินดีต้อนรับ", "core": "🚀 แกนหลัก", "radar": "🛰️ เรดาร์", "comms": "💬 สื่อสาร", "sys": "🧹 ระบบ", "lat": "ละติจูด", "lon": "ลองติจูด", "time": "เวลาของระบบ", "manual": "คู่มือ"},
    "EN": {"welcome": "Welcome", "core": "🚀 CORE", "radar": "🛰️ RADAR", "comms": "💬 COMMS", "sys": "🧹 SYSTEM", "lat": "LATITUDE", "lon": "LONGITUDE", "time": "SYS TIME", "manual": "MANUAL"},
    "LA": {"welcome": "ຍິນດີຕ້ອນຮັບ", "core": "🚀 ແກນຫຼັກ", "radar": "🛰️ ເຣດາ", "comms": "💬 ສື່ສານ", "sys": "🧹 ລະບົບ", "lat": "ລະຕິຈູด", "lon": "ລອງຕິຈູດ", "time": "ເວລາລະບົບ", "manual": "ຄູ່ມື"}
}

# --- 6. SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = "AGENT_X"
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#00f2fe"
if 'lang' not in st.session_state: st.session_state.lang = "TH"

# --- 7. LOGIN UI (คงเดิม) ---
def login_ui():
    if logo_exists: st.image(logo_path, width=400)
    st.markdown(f"<h1 style='color:{st.session_state.theme_color}; text-align:center;'>🌐 SYNAPSE IDENTITY</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        password = st.text_input("SECURITY KEY REQUIRED", type="password")
        if st.button("🚀 ENTER SYSTEM"):
            if password == "notty101":
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("❌ Access Denied")
    st.stop()

if not st.session_state.logged_in: login_ui()

# --- 8. MAIN APP START ---
L = LANG_DATA[st.session_state.lang]
play_audio() # เล่นเสียงเพลงวนลูป

# CSS ปรับแต่งตาม Theme
st.markdown(f"<style>.stApp {{ background: #000; color: {st.session_state.theme_color}; }}</style>", unsafe_allow_html=True)

with st.sidebar:
    if logo_exists: st.image(logo_path, use_column_width=True)
    st.title("🌐 CONTROL")
    st.session_state.lang = st.selectbox("LANGUAGE", list(LANG_DATA.keys()))
    st.session_state.theme_color = st.color_picker("THEME COLOR", st.session_state.theme_color)
    if st.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

# --- 9. TABS INTEGRATION ---
tabs = st.tabs([L["core"], L["radar"], L["comms"], L["sys"]])

# TAB 0: แกนหลัก (เพิ่ม GPS & เวลาเรียลไทม์ที่คุณต้องการ)
with tabs[0]:
    st.header(f"{L['welcome']}, {st.session_state.user_name}")
    st.markdown("### 🛰️ แผนที่เรียวทาม GPS & นาฬิกาบอกตำแหน่ง")
    st.components.v1.html(f"""
        <div style="background: rgba(0,0,0,0.8); color: {st.session_state.theme_color}; padding: 15px; border-radius: 10px; border: 1px solid {st.session_state.theme_color}; font-family: monospace;">
            <div style="display: flex; justify-content: space-between;">
                <div>📍 LAT/LON: <span id="gps-raw">SEARCHING...</span></div>
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

# TAB 1: เรดาร์ (ปักหมุด)
with tabs[1]:
    st.subheader(L["radar"])
    col_a, col_b = st.columns(2)
    lat_v = col_a.number_input(L["lat"], value=13.75)
    lon_v = col_b.number_input(L["lon"], value=100.51)
    st.map(pd.DataFrame({'lat': [lat_v], 'lon': [lon_v]}), color=st.session_state.theme_color)

# TAB 2: สื่อสาร (แชทส่วนตัว + วิดีโอคอล)
with tabs[2]:
    st.subheader(L["comms"])
    target_user = st.text_input("TARGET ID (คุยกับใคร)", "AGENT_Y")
    
    # วิดีโอคอล
    if st.button("📹 VIDEO CALL START"):
        st.components.v1.html("""
            <video id="v" autoplay playsinline style="width:100%; border:2px solid #00f2fe; border-radius:10px; background:#000;"></video>
            <script>
                navigator.mediaDevices.getUserMedia({video:true, audio:true}).then(s => {document.getElementById('v').srcObject = s;});
            </script>
        """, height=300)

    st.markdown("---")
    # แชทส่วนตัว
    msgs = private_chat_logic(st.session_state.user_name, target_user)
    for m in msgs:
        align = "right" if m['name'] == st.session_state.user_name else "left"
        st.markdown(f"<div style='text-align:{align}; color:#fff;'><b>{m['name']}</b>: {m['msg']}</div>", unsafe_allow_html=True)
    
    with st.form("chat_p", clear_on_submit=True):
        p_msg = st.text_input("ENTER MESSAGE...")
        if st.form_submit_button("SEND"):
            private_chat_logic(st.session_state.user_name, target_user, p_msg)
            st.rerun()

# TAB 3: ระบบ (คู่มือ & รีบูต)
with tabs[3]:
    st.subheader(L["sys"])
    st.write(f'Slogan: "อยู่นิ่งๆ ไม่เจ็บตัว"')
    if st.button("REBOOT CORE"):
        st.cache_resource.clear()
        st.rerun()
