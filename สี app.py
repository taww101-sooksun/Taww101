import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time

# --- 1. INITIALIZE FIREBASE (เชื่อมต่อระบบ) ---
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        try:
            # ดึงค่าจาก Secrets (อยู่นิ่งๆ ไม่เจ็บตัว เพราะเราซ่อนกุญแจไว้หลังบ้าน)
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
            return True
        except Exception as e:
            st.error("🚨 ตรวจพบความผิดพลาด: กรุณาตั้งค่า Secrets ให้ครบถ้วน")
            st.stop()
    return True

init_firebase()

# --- 2. CONFIGURATION & UI ---
st.set_page_config(page_title="SYNAPSE IDENTITY", layout="wide")

if 'user_name' not in st.session_state: st.session_state.user_name = "AGENT_X"
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#00f2fe"
if 'lang' not in st.session_state: st.session_state.lang = "TH"

# --- 3. CUSTOM CSS (Cyberpunk Theme) ---
st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; }}
    .stTextInput>div>div>input {{ background-color: #111 !important; color: {st.session_state.theme_color} !important; border: 1px solid {st.session_state.theme_color}55 !important; }}
    .stButton>button {{ border: 1px solid {st.session_state.theme_color} !important; color: {st.session_state.theme_color} !important; background: transparent !important; width: 100%; border-radius: 10px; }}
    .chat-bubble {{ border-left: 4px solid {st.session_state.theme_color}; background: rgba(255,255,255,0.05); padding: 12px; margin-bottom: 10px; border-radius: 0 10px 10px 0; font-family: 'Courier New', monospace; }}
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🌐 SYNAPSE IDENTITY")
    st.session_state.user_name = st.text_input("YOUR ID", st.session_state.user_name)
    st.session_state.theme_color = st.color_picker("THEME COLOR", st.session_state.theme_color)
    st.session_state.lang = st.selectbox("LANGUAGE", ["TH", "EN", "JP", "CN", "MM", "LA"])
    st.markdown("---")
    st.write(f'**Slogan:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

# --- 5. MAIN CONTENT (TABS) ---
TAB_LABELS = {
    "TH": ["🚀 แกนหลัก", "🛰️ เรดาร์", "💬 สื่อสาร", "🔐 ปลอดภัย", "🧹 ระบบ"],
    "EN": ["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "🔐 SEC", "🧹 SYS"]
}
selected_tabs = TAB_LABELS.get(st.session_state.lang, TAB_LABELS["EN"])
tabs = st.tabs(selected_tabs)

# --- [TAB 0: แกนหลัก] ---
with tabs[0]:
    st.markdown(f"""
        <div style="text-align: center; border: 1px solid {st.session_state.theme_color}; padding: 20px; border-radius: 15px; background: rgba(0,0,0,0.5);">
            <h1 style="color:{st.session_state.theme_color}; margin-bottom: 0;">SYNAPSE CORE</h1>
            <p style="letter-spacing: 2px;">NEURAL INTERFACE v3.13</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("OPERATOR", st.session_state.user_name)
    
    try:
        db.reference('status').get(timeout=3)
        c2.metric("CORE STATUS", "ONLINE")
    except:
        c2.metric("CORE STATUS", "OFFLINE")
        
    c3.metric("SYS TIME", time.strftime("%H:%M", time.localtime()))
    
    if st.button("📢 BROADCAST SIGNAL"):
        db.reference('logs/activity').push({
            'event': 'SIGNAL_SENT', 'user': st.session_state.user_name, 'ts': time.time()
        })
        st.toast("Signal Broadcasted!")

# --- [TAB 1: เรดาร์] ---
with tabs[1]:
    st.subheader("🛰️ GPS TARGET LOCK")
    lat = st.number_input("LATITUDE", value=13.7500, format="%.4f")
    lon = st.number_input("LONGITUDE", value=100.5100, format="%.4f")
    if st.button("LOCK COORDINATES"):
        db.reference('radar/target').set({
            'lat': lat, 'lon': lon, 'user': st.session_state.user_name, 'ts': time.time()
        })
        st.success("Target Locked in Database!")

# --- [TAB 2: สื่อสาร] ---
with tabs[2]:
    st.subheader("💬 NEURAL PRIVATE LINK")
    target = st.text_input("TARGET ID", placeholder="ต้องการส่งข้อมูลให้ใคร?")
    if target:
        room_id = f"priv_{'_'.join(sorted([st.session_state.user_name, target]))}"
        chat_ref = db.reference(f'private_rooms/{room_id}')
        
        msg = st.chat_input("Enter message...")
        if msg:
            chat_ref.push({'name': st.session_state.user_name, 'msg': msg, 'ts': time.time()})
            st.rerun()
            
        msgs = chat_ref.order_by_child('ts').limit_to_last(15).get()
        if msgs:
            for m in sorted(msgs.values(), key=lambda x: x['ts']):
                st.markdown(f'<div class="chat-bubble"><b style="color:{st.session_state.theme_color}">{m["name"]}</b><br>{m["msg"]}</div>', unsafe_allow_html=True)
        else:
            st.caption("ไม่มีประวัติการสื่อสาร")

# --- [TAB 3: ปลอดภัย] ---
with tabs[3]:
    st.subheader("🔐 SECURITY LAYER")
    pw = st.text_input("ENCRYPTION KEY", type="password")
    if pw == "notty101":
        st.success("ACCESS GRANTED: ข้อมูลลับคือ 'อยู่นิ่งๆ ไม่เจ็บตัว'")
    elif pw:
        st.error("ACCESS DENIED")

# --- [TAB 4: ระบบ] ---
with tabs[4]:
    st.subheader("🧹 DIAGNOSTICS")
    if st.button("REBOOT SYSTEM"):
        st.cache_resource.clear()
        st.rerun()
    st.write("Database Path: `Active`")
