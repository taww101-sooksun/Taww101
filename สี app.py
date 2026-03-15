import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time

# --- 1. INITIALIZE FIREBASE (ยึดตามความเป็นจริง ไม่หลอกกัน) ---
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
            # ใช้ URL ที่ตรงกับ Region ของเพื่อน (Singapore)
            target_url = "https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/"
            firebase_admin.initialize_app(cred, {'databaseURL': target_url})
            return True
        except Exception as e:
            st.error(f"📡 Connection Error: {e}")
            return False
    return True

init_firebase()

# --- 2. MULTI-LANGUAGE DICTIONARY (6 ภาษา) ---
LANG_DATA = {
    "TH": {"welcome": "ยินดีต้อนรับ", "core": "🚀 แกนหลัก", "radar": "🛰️ เรดาร์", "comms": "💬 สื่อสาร", "login": "เข้าสู่ระบบ", "pass": "รหัสผ่าน", "lat": "ละติจูด", "lon": "ลองติจูด", "time": "เวลาของระบบ"},
    "EN": {"welcome": "Welcome", "core": "🚀 CORE", "radar": "🛰️ RADAR", "comms": "💬 COMMS", "login": "LOGIN", "pass": "PASSWORD", "lat": "LATITUDE", "lon": "LONGITUDE", "time": "SYS TIME"},
    "JP": {"welcome": "ようこそ", "core": "🚀 コア", "radar": "🛰️ レーダー", "comms": "💬 通信", "login": "ログイン", "pass": "パスワード", "lat": "緯度", "lon": "経度", "time": "システム時間"},
    "CN": {"welcome": "欢迎", "core": "🚀 核心", "radar": "🛰️ 雷达", "comms": "💬 通讯", "login": "登录", "pass": "密码", "lat": "纬度", "lon": "经度", "time": "系统时间"},
    "MM": {"welcome": "ကြိုဆိုပါတယ်", "core": "🚀 အဓိက", "radar": "🛰️ ရေဒါ", "comms": "💬 ဆက်သွယ်ရေး", "login": "လော့ဂ်အင်", "pass": "စကားဝှက်", "lat": "လတ္တီတွဒ်", "lon": "လောင်ဂျီတွဒ်", "time": "စနစ်အချိန်"},
    "LA": {"welcome": "ຍິນດີຕ້ອນຮັບ", "core": "🚀 ແກນຫຼັກ", "radar": "🛰️ ເຣດາ", "comms": "💬 ສື່ສານ", "login": "ເຂົ້າສູ່ລະບົບ", "pass": "ລະຫັດຜ່ານ", "lat": "ລະຕິຈູດ", "lon": "ລອງຕິຈູດ", "time": "ເວລາລະບົບ"}
}

# --- 3. LOGIN & SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user_name' not in st.session_state: st.session_state.user_name = "AGENT_X"
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#00f2fe"
if 'lang' not in st.session_state: st.session_state.lang = "TH"

def login_screen():
    st.markdown("<h1 style='text-align: center; color:#00f2fe;'>SYNAPSE IDENTITY</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pw = st.text_input("PASSWORD", type="password")
        if st.button("ENTER"):
            if pw == "notty101": 
                st.session_state.logged_in = True
                st.rerun()
            else: st.error("Access Denied")
    st.stop()

if not st.session_state.logged_in: login_screen()

# --- 4. UI SETUP ---
st.set_page_config(page_title="SYNAPSE v3", layout="wide")
L = LANG_DATA[st.session_state.lang]

st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; }}
    .stButton>button {{ border: 1px solid {st.session_state.theme_color}; background: transparent; color: {st.session_state.theme_color}; border-radius: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("🌐 CONTROL")
    st.session_state.user_name = st.text_input("NAME", st.session_state.user_name)
    st.session_state.lang = st.selectbox("LANG", list(LANG_DATA.keys()))
    st.session_state.theme_color = st.color_picker("THEME", st.session_state.theme_color)
    st.write('**Slogan:** "อยู่นิ่งๆ ไม่เจ็บตัว"')
    if st.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

# --- 6. MAIN CONTENT ---
tabs = st.tabs([L["core"], L["radar"], L["comms"], "🛠️ ระบบ"])

# TAB 0: แกนหลัก (Dashboard + นาฬิกา)
with tabs[0]:
    c1, c2 = st.columns([2,1])
    with c1:
        st.header(f"{L['welcome']}, {st.session_state.user_name}")
    with c2:
        st.metric(L["time"], time.strftime("%H:%M:%S"))
    
    st.markdown("---")
    if st.button("📢 BROADCAST SIGNAL"):
        db.reference('logs/activity').push({'user': st.session_state.user_name, 'ts': time.time()})
        st.toast("Signal Sent!")

# TAB 1: เรดาร์ (พิกัด + สีหมุดแผ่นที่)
with tabs[1]:
    st.subheader(L["radar"])
    col_a, col_b = st.columns(2)
    lat_val = col_a.number_input(L["lat"], value=13.7500, format="%.4f")
    lon_val = col_b.number_input(L["lon"], value=100.5100, format="%.4f")
    
    # แสดงแผนที่ (หมุดสีจะเปลี่ยนตาม Theme ที่เลือก)
    import pandas as pd
    map_data = pd.DataFrame({'lat': [lat_val], 'lon': [lon_val]})
    st.map(map_data, color=st.session_state.theme_color)
    
    if st.button("📍 LOCK LOCATION"):
        db.reference('radar/target').set({'lat': lat_val, 'lon': lon_val, 'user': st.session_state.user_name})
        st.success("Target Locked!")

# TAB 2: สื่อสาร (Chat + Call Link)
with tabs[2]:
    st.subheader(L["comms"])
    target = st.text_input("TARGET ID")
    if target:
        msg = st.chat_input("Message...")
        if msg:
            db.reference(f'chats/{st.session_state.user_name}_{target}').push({'msg': msg, 'ts': time.time()})
    
    st.markdown("---")
    st.write("📞 **Quick Call**")
    st.markdown(f'<a href="tel:0812345678"><button style="width:100%;">Call Operator</button></a>', unsafe_allow_html=True)

# TAB 3: ระบบ (Check Path)
with tabs[3]:
    st.write("Database Path:", "Asia-Southeast1 (Singapore)")
    if st.button("REBOOT"):
        st.cache_resource.clear()
        st.rerun()
