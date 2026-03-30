import streamlit as st
import os 
import time
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import hashlib

# ==========================================
# 1. การตั้งค่าระบบพื้นฐาน (Core Settings)
# ==========================================
def init_system():
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
            st.error(f"🛰️ Firebase Connection Error: {e}")

def hash_pw(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# ==========================================
# 2. ระบบจัดการธีมสี (3 ชุดสี)
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
        .stButton>button {{ border: 2px solid {t['main']} !important; color: {t['main']} !important; background: transparent !important; border-radius: 12px; }}
        .stButton>button:hover {{ background: {t['main']} !important; color: {t['bg']} !important; }}
        h1, h2, h3, p, span, label, .stMarkdown {{ color: {t['text']} !important; }}
        .stTabs [data-baseweb="tab-list"] {{ background-color: transparent; }}
        .stTabs [aria-selected="true"] {{ color: {t['main']} !important; border-bottom-color: {t['main']} !important; }}
        </style>
    """, unsafe_allow_html=True)
    return t

# ==========================================
# 3. หน้าเข้าสู่ระบบ (Authentication)
# ==========================================
def login_page():
    st.title("🛡️ SYNAPSE SECURITY GATE")
    t1, t2 = st.tabs(["🔐 Login", "📝 Register"])
    with t1:
        u = st.text_input("Username", key="l_u")
        p = st.text_input("Password", type="password", key="l_p")
        if st.button("ENTER", use_container_width=True):
            data = db.reference(f'accounts/{u}').get()
            if data and data.get('pw') == hash_pw(p):
                st.session_state.auth_status, st.session_state.user = True, u
                st.rerun()
            else: st.error("❌ ข้อมูลไม่ถูกต้อง")
    with t2:
        ru = st.text_input("New User", key="r_u")
        rp = st.text_input("New PW", type="password", key="r_p")
        if st.button("REGISTER", use_container_width=True):
            if ru and rp:
                db.reference(f'accounts/{ru}').set({'pw': hash_pw(rp)})
                st.success("✅ สำเร็จ!")

# ==========================================
# 4. ห้องสื่อสาร (Lobby & Private Chat & CALL)
# ==========================================
def room_comms(theme):
    st.subheader("💬 ระบบสื่อสาร SYNAPSE")
    tab_pub, tab_priv, tab_call = st.tabs(["🌐 Lobby", "🔐 Private Chat", "📞 CALL (โทร)"])
    
    all_users = db.reference('accounts').get()
    friends = [uid for uid in all_users.keys() if uid != st.session_state.user] if all_users else []

    with tab_pub:
        with st.form("pub_chat", clear_on_submit=True):
            msg = st.text_input("ส่งข้อความสาธารณะ...")
            if st.form_submit_button("SEND"):
                db.reference('public_chat').push({'u': st.session_state.user, 'msg': msg, 'ts': time.time()})
        msgs = db.reference('public_chat').order_by_key().limit_to_last(10).get()
        if msgs:
            for m in reversed(list(msgs.values())):
                st.write(f"🟢 **{m.get('u')}**: {m.get('msg')}")

    with tab_priv:
        target_p = st.selectbox("คุยส่วนตัวกับ:", ["-- เลือกเพื่อน --"] + friends, key="p_sel")
        if target_p != "-- เลือกเพื่อน --":
            room_id = "_".join(sorted([st.session_state.user, target_p]))
            with st.form("priv_chat", clear_on_submit=True):
                pm = st.text_input(f"กระซิบถึง {target_p}...")
                if st.form_submit_button("SEND PRIVATE"):
                    db.reference(f'private_rooms/{room_id}').push({'u': st.session_state.user, 'msg': pm, 'ts': time.time()})
            p_msgs = db.reference(f'private_rooms/{room_id}').order_by_key().limit_to_last(15).get()
            if p_msgs:
                for pi in reversed(list(p_msgs.values())):
                    c = theme['main'] if pi.get('u') == st.session_state.user else "#888"
                    st.markdown(f"<span style='color:{c}'><b>{pi.get('u')}</b></span>: {pi.get('msg')}", unsafe_allow_html=True)

    with tab_call:
        target_c = st.selectbox("โทรหาใครดีครับ:", ["-- เลือกเพื่อน --"] + friends, key="c_sel")
        if target_c != "-- เลือกเพื่อน --":
            # ระบบ PeerJS พร้อม STUN Server ทะลุ 4G
            call_html = """
            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <div style="background:#111; padding:20px; border-radius:15px; border:2px solid %s; text-align:center;">
                <p style="color:white;">ID ของคุณ: <b>%s</b></p>
                <p style="color:white;">กำลังต่อสายไปที่: <b>%s</b></p>
                <button id="callBtn" style="width:100%%; padding:15px; background:%s; color:black; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">🟢 กดโทรออก (CALL)</button>
                <audio id="remoteAudio" autoplay></audio>
            </div>
            <script>
                const peer = new Peer('%s', {
                    config: {'iceServers': [{ 'urls': 'stun:stun.l.google.com:19302' }, { 'urls': 'stun:stun1.l.google.com:19302' }]}
                });
                peer.on('call', c => {
                    navigator.mediaDevices.getUserMedia({audio:true}).then(s => {
                        c.answer(s);
                        c.on('stream', rs => { document.getElementById('remoteAudio').srcObject = rs; });
                    });
                });
                document.getElementById('callBtn').onclick = () => {
                    navigator.mediaDevices.getUserMedia({audio:true}).then(s => {
                        const c = peer.call('%s', s);
                        c.on('stream', rs => { document.getElementById('remoteAudio').srcObject = rs; });
                    });
                };
            </script>
            """ % (theme['main'], st.session_state.user, target_c, theme['main'], st.session_state.user, target_c)
            components.html(call_html, height=300)

# ==========================================
# 5. ห้องฟังเพลง (Music Station)
# ==========================================
def room_music():
    st.subheader("🎧 SYNAPSE MUSIC")
    files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if not files:
        st.warning("⚠️ อัปโหลดเพลง .mp3 ลง GitHub ด้วยครับ")
        return
    curr = files[st.session_state.song_index]
    st.audio(curr, autoplay=True)
    st.write(f"💿 กำลังเล่น: {curr}")
    for idx, f in enumerate(files):
        if st.button(f"🎵 {f}", key=f"m_{idx}", use_container_width=True):
            st.session_state.song_index = idx
            st.rerun()

# ==========================================
# 6. Main Application
# ==========================================
def main():
    init_system()
    if not st.session_state.auth_status:
        login_page()
        return

    with st.sidebar:
        st.title("⚙️ SETTINGS")
        st.write(f"👤 User: **{st.session_state.user}**")
        st.session_state.theme_set = st.radio("🎨 ชุดสี:", ["Matrix", "Ocean", "Ember"])
        if st.button("🚪 LOGOUT", use_container_width=True):
            st.session_state.auth_status = False
            st.rerun()

    current_theme = apply_theme()
    menu = {"💬 สื่อสาร": lambda: room_comms(current_theme), "🎧 เพลง": room_music}
    tabs = st.tabs(list(menu.keys()))
    for i, func in enumerate(menu.values()):
        with tabs[i]: func()

if __name__ == "__main__":
    main()
