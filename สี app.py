import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time

# --- 1. INITIALIZE FIREBASE (ป้องกัน Error ซ้ำซ้อน) ---
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        # ดึงข้อมูลจาก st.secrets เพื่อความปลอดภัยขั้นสูงสุด
        # ถ้าคุณยังไม่ได้ตั้ง Secrets ให้ใส่ Dict ปกติแทนที่นี่ชั่วคราวได้
        try:
            fb_config = {
                "type": "service_account",
                "project_id": st.secrets["project_id"],
                "private_key": st.secrets["private_key"].replace('\\n', '\n'),
                "client_email": st.secrets["client_email"],
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            cred = credentials.Certificate(fb_config)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["database_url"]
            })
        except:
            # กรณีรัน Local แล้วยังไม่มี Secrets ให้ใช้แบบเดิมไปก่อน (แต่ต้องระวัง!)
            st.error("กรุณาตั้งค่า Secrets ใน Streamlit Cloud หรือเช็ค Private Key ของคุณ")
            st.stop()
    return True

# เรียกใช้งานฟังก์ชันเชื่อมต่อ
init_firebase()

# --- 2. CONFIGURATION & UI ---
st.set_page_config(page_title="SYNAPSE IDENTITY", layout="wide")

# จัดการ Session State
if 'user_name' not in st.session_state: st.session_state.user_name = "AGENT_X"
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#00f2fe"
if 'lang' not in st.session_state: st.session_state.lang = "TH"

# --- 3. CSS (Cyberpunk Style) ---
st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; }}
    .stTextInput>div>div>input {{ background-color: #111; color: {st.session_state.theme_color}; }}
    .chat-bubble {{
        border: 1px solid {st.session_state.theme_color}33;
        background: rgba(255, 255, 255, 0.05);
        padding: 10px; border-radius: 10px; margin-bottom: 8px;
        border-left: 4px solid {st.session_state.theme_color};
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🌐 SYNAPSE IDENTITY")
    st.session_state.user_name = st.text_input("YOUR ID", st.session_state.user_name)
    st.session_state.theme_color = st.color_picker("THEME COLOR", st.session_state.theme_color)
    st.session_state.lang = st.selectbox("LANGUAGE", ["TH", "EN", "JP", "CN", "MM", "LA"])
    st.markdown("---")
    st.write('**Slogan:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

# --- 5. TABS ---
TAB_LABELS = {
    "TH": ["🚀 แกนหลัก", "🛰️ เรดาร์", "💬 สื่อสาร", "📊 ล็อก", "🔐 ปลอดภัย", "📺 มีเดีย", "🧹 ระบบ"],
    "EN": ["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "📊 LOG", "🔐 SEC", "📺 MEDIA", "🧹 SYS"]
}
selected_tabs = TAB_LABELS.get(st.session_state.lang, TAB_LABELS["EN"])
tabs = st.tabs(selected_tabs)

# --- TAB 0: แกนหลัก (Dashboard) ---
with tabs[0]:
    st.subheader("🖥️ SYSTEM DASHBOARD")
    col1, col2 = st.columns(2)
    col1.metric("CURRENT OPERATOR", st.session_state.user_name)
    col2.metric("SYSTEM STATUS", "ACTIVE")
    st.info("Neural Link connection established. All data encrypted.")

# --- TAB 1: เรดาร์ (GPS) ---
with tabs[1]:
    st.subheader("🛰️ GPS TARGET LOCK")
    lat = st.number_input("LATITUDE", value=13.75)
    lon = st.number_input("LONGITUDE", value=100.50)
    if st.button("LOCK TARGET"):
        db.reference('radar/target').set({'lat': lat, 'lon': lon, 'by': st.session_state.user_name, 'ts': time.time()})
        st.success("Target Coordinate Locked!")

# --- TAB 2: สื่อสาร (Private Chat) ---
with tabs[2]:
    st.subheader("💬 NEURAL PRIVATE LINK")
    target_id = st.text_input("TARGET ID")
    if target_id:
        room_id = f"priv_{'_'.join(sorted([st.session_state.user_name, target_id]))}"
        chat_ref = db.reference(f'private_rooms/{room_id}')
        
        msg = st.chat_input("Enter message...")
        if msg:
            chat_ref.push({'name': st.session_state.user_name, 'msg': msg, 'ts': time.time()})
            st.rerun()

        # แสดงผล
        raw = chat_ref.order_by_child('ts').limit_to_last(10).get()
        if raw:
            for m in sorted(raw.values(), key=lambda x: x['ts']):
                st.markdown(f'<div class="chat-bubble"><b>{m["name"]}</b>: {m["msg"]}</div>', unsafe_allow_html=True)

# --- TAB 4: ปลอดภัย (Access Key) ---
with tabs[4]:
    st.subheader("🔐 SECURITY LAYER")
    access_code = st.text_input("ENCRYPTION KEY", type="password")
    if access_code == "notty101": # ตัวอย่างรหัส
        st.success("Access Granted. Master Key: `X-777-ALPHA`")
    elif access_code:
        st.error("Invalid Encryption Key.")

# --- TAB 5: มีเดีย ---
with tabs[5]:
    st.subheader("📺 MEDIA STREAM")
    img_url = st.text_input("IMAGE URL", "https://via.placeholder.com/600x300.png?text=Synapse+Identity")
    if img_url:
        st.image(img_url, caption="Remote Feed")

# --- TAB 6: ระบบ (แก้บั๊ก .info) ---
with tabs[6]:
    st.subheader("🧹 SYSTEM DIAGNOSTICS")
    try:
        # ใช้การดึงข้อมูลจาก Path ปกติเพื่อเช็ค Connection
        db.reference('status').get(timeout=5)
        st.success("CORE ONLINE")
    except:
        st.error("CORE OFFLINE - Check Credentials")
    
    if st.button("REBOOT SYSTEM"):
        st.cache_resource.clear()
        st.rerun()
