import streamlit as st
import os 
import time
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import hashlib

# ==========================================
# 1. กลไกกลาง (Core Engine)
# ==========================================
def init_system():
    # ตั้งค่า Default Theme
    if 'theme_set' not in st.session_state: st.session_state.theme_set = "Matrix"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'auth_status' not in st.session_state: st.session_state.auth_status = False
    if 'user' not in st.session_state: st.session_state.user = None
        
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ Firebase Error: {e}")

def hash_pw(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# ==========================================
# 2. ระบบจัดการสี (Theme Manager)
# ==========================================
def apply_theme():
    themes = {
        "Matrix": {"bg": "#000000", "main": "#39FF14", "text": "#FFFFFF"},
        "Ocean":  {"bg": "#001219", "main": "#00A8E8", "text": "#E0FBFC"},
        "Ember":  {"bg": "#1a0000", "main": "#FF4D4D", "text": "#FFFFFF"}
    }
    t = themes[st.session_state.theme_set]
    
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {t['bg']} !important; color: {t['text']} !important; }}
        .stButton>button {{ 
            border: 2px solid {t['main']} !important; 
            color: {t['main']} !important; 
            background: transparent !important; 
            border-radius: 10px;
        }}
        .stButton>button:hover {{ background: {t['main']} !important; color: {t['bg']} !important; }}
        h1, h2, h3, p, span, label, .stMarkdown {{ color: {t['text']} !important; }}
        .stTabs [data-baseweb="tab-list"] {{ background-color: transparent; }}
        .stTabs [data-baseweb="tab"] {{ color: {t['text']}; }}
        .stTabs [aria-selected="true"] {{ color: {t['main']} !important; border-bottom-color: {t['main']} !important; }}
        </style>
    """, unsafe_allow_html=True)
    return t

# ==========================================
# 3. หน้าจอหลักและห้องต่างๆ
# ==========================================
def login_page():
    st.title("🛡️ SYNAPSE AUTH")
    t1, t2 = st.tabs(["🔐 Login", "📝 Register"])
    with t1:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("ENTER SYSTEM", use_container_width=True):
            data = db.reference(f'accounts/{u}').get()
            if data and data.get('pw') == hash_pw(p):
                st.session_state.auth_status, st.session_state.user = True, u
                st.rerun()
            else: st.error("❌ ข้อมูลไม่ถูกต้อง")
    with t2:
        ru = st.text_input("New Username", key="r_u")
        rp = st.text_input("New Password", type="password", key="r_p")
        if st.button("CREATE ACCOUNT", use_container_width=True):
            if ru and rp:
                db.reference(f'accounts/{ru}').set({'pw': hash_pw(rp)})
                st.success("✅ ลงทะเบียนสำเร็จ!")

def room_comms(theme):
    st.subheader("💬 ศูนย์สื่อสารแยกโซน")
    tab_pub, tab_priv = st.tabs(["🌐 Lobby (สาธารณะ)", "🔐 Private (ส่วนตัว)"])
    
    with tab_pub:
        with st.form("pub_chat", clear_on_submit=True):
            m = st.text_input("ส่งข้อความถึงทุกคน...")
            if st.form_submit_button("SEND"):
                db.reference('public_chat').push({'u': st.session_state.user, 'msg': m, 'ts': time.time()})
        msgs = db.reference('public_chat').order_by_key().limit_to_last(15).get()
        if msgs:
            for i in reversed(list(msgs.values())):
                st.markdown(f"**{i.get('u')}**: {i.get('msg')}")

    with tab_priv:
        all_u = db.reference('accounts').get()
        friends = [uid for uid in all_u.keys() if uid != st.session_state.user] if all_u else []
        target = st.selectbox("เลือกคนที่ต้องการคุยลับด้วย:", ["-- เลือกชื่อเพื่อน --"] + friends)
        
        if target != "-- เลือกชื่อเพื่อน --":
            st.caption(f"🔒 ห้องลับระหว่างคุณ กับ {target}")
            room_id = "_".join(sorted([st.session_state.user, target]))
            with st.form("priv_chat", clear_on_submit=True):
                pm = st.text_input(f"กระซิบถึง {target}...")
                if st.form_submit_button("SEND PRIVATE"):
                    db.reference(f'private_rooms/{room_id}').push({'u': st.session_state.user, 'msg': pm, 'ts': time.time()})
            
            p_msgs = db.reference(f'private_rooms/{room_id}').order_by_key().limit_to_last(20).get()
            if p_msgs:
                for pi in reversed(list(p_msgs.values())):
                    c = theme['main'] if pi.get('u') == st.session_state.user else "#888888"
                    st.markdown(f"<span style='color:{c}'><b>{pi.get('u')}</b></span>: {pi.get('msg')}", unsafe_allow_html=True)

def room_music():
    st.subheader("🎧 SYNAPSE MUSIC")
    files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if not files:
        st.warning("⚠️ ไม่พบไฟล์เพลงใน GitHub")
        return
    
    curr = files[st.session_state.song_index]
    st.info(f"💿 Playing: {curr}")
    st.audio(curr, autoplay=True)
    
    st.write("---")
    cols = st.columns(2)
    for idx, f in enumerate(files):
        with cols[idx % 2]:
            if st.button(f"🎵 {f}", key=f"m_{idx}", use_container_width=True):
                st.session_state.song_index = idx
                st.rerun()

# ==========================================
# 4. Main Application
# ==========================================
def main():
    init_system()
    if not st.session_state.auth_status:
        # ใช้สีเริ่มต้นสำหรับหน้า Login
        st.markdown("<style>.stApp { background-color: #000; color: #fff; }</style>", unsafe_allow_html=True)
        login_page()
        return

    # เลือกชุดสีที่ Sidebar
    with st.sidebar:
        st.title("⚙️ CONTROL")
        st.write(f"👤 User: **{st.session_state.user}**")
        st.session_state.theme_set = st.radio("🎨 เลือกชุดสีแอป:", ["Matrix", "Ocean", "Ember"])
        st.markdown("---")
        if st.button("🚪 LOGOUT", use_container_width=True):
            st.session_state.auth_status = False
            st.rerun()

    current_theme = apply_theme()

    menu = {"💬 สื่อสาร": lambda: room_comms(current_theme), "🎧 เพลง": room_music}
    tabs = st.tabs(list(menu.keys()))
    for i, (name, func) in enumerate(menu.items()):
        with tabs[i]: func()

if __name__ == "__main__":
    main()
