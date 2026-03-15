import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time

# --- 1. INITIALIZE FIREBASE (เชื่อมต่อฐานข้อมูล) ---
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        fb_config = {
            "type": "service_account",
            "project_id": "notty-101",
            "private_key_id": "e280e1fe09351106936545fc0d0175dfb45716b2",
            "private_key": st.secrets.get("private_key") if "private_key" in st.secrets else "-----BEGIN PRIVATE KEY-----\n...", # แนะนำให้ใช้ st.secrets เพื่อความปลอดภัย
            "client_email": "firebase-adminsdk-fbsvc@notty-101.iam.gserviceaccount.com",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
        # หมายเหตุ: เพื่อความจริงใจ แนะนำให้คุณเปลี่ยนไปใช้ st.secrets ในอนาคตแทนการวาง Private Key ในโค้ดโดยตรง
        cred = credentials.Certificate(fb_config)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://notty-101-default-rtdb.firebaseio.com/'
        })
    return True

init_firebase()

# --- 2. CONFIGURATION ---
st.set_page_config(page_title="SYNAPSE IDENTITY", layout="wide")

# Initialize Session States
for key, val in {
    'user_name': 'AGENT_X',
    'theme_color': '#00f2fe',
    'lang': 'TH'
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- 3. LANGUAGE MATRIX ---
TAB_LABELS = {
    "TH": ["🚀 แกนหลัก", "🛰️ เรดาร์", "💬 สื่อสาร", "📊 ล็อก", "🔐 ปลอดภัย", "📺 มีเดีย", "🧹 ระบบ"],
    "EN": ["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "📊 LOG", "🔐 SEC", "📺 MEDIA", "🧹 SYS"],
    "JP": ["🚀 コア", "🛰️ レーダー", "💬 通信", "📊 ログ", "🔐 セキュリティ", "📺 メディア", "🧹 システム"],
    "CN": ["🚀 核心", "🛰️ 雷达", "💬 通讯", "📊 日志", "🔐 安全", "📺 媒体", "🧹 系统"],
    "MM": ["🚀 အဓိက", "🛰️ ရေဒါ", "💬 ဆက်သွယ်ရေး", "📊 မှတ်တမ်း", "🔐 လုံခြုံရေး", "📺 မီဒီယာ", "စနစ်"],
    "LA": ["🚀 ແກນຫຼັກ", "🛰️ ເຣດາ", "💬 ສື່ສານ", "📊 ບັນທຶກ", "🔐 ປອດໄພ", "📺 ມີເດຍ", "🧹 ລະບົບ"]
}

# --- 4. ADVANCED CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; }}
    .stTextInput>div>div>input {{ background-color: #111; color: {st.session_state.theme_color}; border: 1px solid {st.session_state.theme_color}55; }}
    .chat-bubble {{
        border-left: 4px solid {st.session_state.theme_color};
        background: rgba(255, 255, 255, 0.03);
        padding: 12px;
        border-radius: 0px 10px 10px 0px;
        margin-bottom: 10px;
        font-family: 'Courier New', Courier, monospace;
    }}
    .stButton>button {{ width: 100%; }}
    </style>
    """, unsafe_allow_html=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("🌐 SYNAPSE IDENTITY")
    st.session_state.user_name = st.text_input("YOUR ID", st.session_state.user_name)
    st.session_state.theme_color = st.color_picker("THEME COLOR", st.session_state.theme_color)
    st.session_state.lang = st.selectbox("LANGUAGE", list(TAB_LABELS.keys()), index=list(TAB_LABELS.keys()).index(st.session_state.lang))
    st.markdown("---")
    st.caption(f'Slogan: "อยู่นิ่งๆ ไม่เจ็บตัว"')

# --- 6. MAIN CONTENT ---
tabs = st.tabs(TAB_LABELS[st.session_state.lang])

# --- TAB 1: RADAR ---
with tabs[1]:
    st.subheader("🛰️ GPS TARGET LOCK")
    c1, c2 = st.columns(2)
    with c1: lat = st.number_input("LATITUDE", value=13.7500, format="%.4f")
    with c2: lon = st.number_input("LONGITUDE", value=100.5100, format="%.4f")
    
    if st.button("SET TARGET"):
        db.reference('radar/target').set({
            'lat': lat, 'lon': lon, 
            'by': st.session_state.user_name, 
            'ts': time.time()
        })
        st.toast("Coordinate Locked!")

# --- TAB 2: COMMS (PRIVATE CHAT) ---
with tabs[2]:
    st.subheader("💬 NEURAL PRIVATE LINK")
    target_id = st.text_input("ENTER RECIPIENT ID", placeholder="Who are you talking to?")
    
    if target_id:
        # ป้องกันการสลับห้องแชท (A คุยกับ B หรือ B คุยกับ A จะเป็นห้องเดียวกัน)
        room_id = f"priv_{'_'.join(sorted([st.session_state.user_name, target_id]))}"
        chat_ref = db.reference(f'private_rooms/{room_id}')
        
        # ช่องส่งข้อความ
        chat_msg = st.chat_input("Transmit data...")
        if chat_msg:
            chat_ref.push({
                'name': st.session_state.user_name,
                'msg': chat_msg,
                'ts': time.time()
            })
            st.rerun()

        # แสดงผลข้อความ
        st.write(f"--- Channel: {room_id} ---")
        raw_data = chat_ref.order_by_child('ts').limit_to_last(10).get()
        
        if raw_data:
            # เรียงลำดับตามเวลาจริง (Timestamp)
            sorted_msgs = sorted(raw_data.values(), key=lambda x: x['ts'])
            for m in sorted_msgs:
                st.markdown(f"""
                    <div class="chat-bubble">
                        <b style="color:{st.session_state.theme_color}">{m['name']}</b><br>
                        {m['msg']}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No logs in this neural link.")

# --- TAB 6: SYSTEM ---
with tabs[6]:
    st.subheader("🧹 SYSTEM DIAGNOSTICS")
    is_connected = db.reference('.info/connected').get()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("DB STATUS", "ONLINE" if is_connected else "OFFLINE")
    col2.metric("USER ID", st.session_state.user_name)
    col3.metric("LOCALE", st.session_state.lang)
    
    if st.button("CLEAR LOCAL CACHE"):
        st.cache_resource.clear()
        st.success("System Rebooted")
