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
    # ตั้งค่าสถานะเริ่มต้น
    if 'theme_set' not in st.session_state: st.session_state.theme_set = "Matrix"
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'auth_status' not in st.session_state: st.session_state.auth_status = False
    if 'user' not in st.session_state: st.session_state.user = None
    
    # เชื่อมต่อ Firebase (ใช้ Secrets ที่คุณท่านใส่ไว้)
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': st.secrets["firebase_db_url"]
            })
        except Exception as e:
            st.error(f"🛰️ Firebase Connection Error: {e}")

def hash_pw(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# ==========================================
# 2. ระบบจัดการธีมสี (3 ชุดสี)
# ==========================================
def apply_theme():
    themes = {
        "Matrix": {"bg": "#000000", "main": "#39FF14", "text": "#FFFFFF", "sub": "#1DB954"},
        "Ocean":  {"bg": "#001219", "main": "#00A8E8", "text": "#E0FBFC", "sub": "#005F73"},
        "Ember":  {"bg": "#1a0000", "main": "#FF4D4D", "text": "#FFFFFF", "sub": "#990000"}
    }
    t = themes[st.session_state.theme_set]
    
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {t['bg']} !important; color: {t['text']} !important; }}
        .stButton>button {{ 
            border: 2px solid {t['main']} !important; 
            color: {t['main']} !important; 
            background: transparent !important; 
            border-radius: 12px;
            font-weight: bold;
        }}
        .stButton>button:hover {{ background: {t['main']} !important; color: {t['bg']} !important; }}
        h1, h2, h3, p, span, label, .stMarkdown {{ color: {t['text']} !important; }}
        .stTabs [data-baseweb="tab-list"] {{ background-color: transparent; gap: 10px; }}
        .stTabs [data-baseweb="tab"] {{ 
            color: {t['text']}; 
            border-radius: 10px 10px 0 0;
            padding: 10px 20px;
        }}
        .stTabs [aria-selected="true"] {{ 
            color: {t['main']} !important; 
            border-bottom: 3px solid {t['main']} !important; 
        }}
        input {{ background-color: #222 !important; color: white !important; border: 1px solid {t['main']} !important; }}
        </style>
    """, unsafe_allow_html=True)
    return t

# ==========================================
# 3. หน้าเข้าสู่ระบบ (Authentication)
# ==========================================
def login_page():
    st.title("🛡️ SYNAPSE SECURITY GATE")
    tab1, tab2 = st.tabs(["🔐 ลงชื่อเข้าใช้", "📝 ลงทะเบียนใหม่"])
    
    with tab1:
        u_login = st.text_input("ชื่อผู้ใช้ (Username)", key="u_log")
        p_login = st.text_input("รหัสผ่าน (Password)", type="password", key="p_log")
        if st.button("เข้าสู่ระบบ SYNAPSE", use_container_width=True):
            user_data = db.reference(f'accounts/{u_login}').get()
            if user_data and user_data.get('pw') == hash_pw(p_login):
                st.session_state.auth_status = True
                st.session_state.user = u_login
                # อัปเดตสถานะออนไลน์
                db.reference(f'users/{u_login}').update({'status': 'online', 'last_seen': time.time()})
                st.rerun()
            else:
                st.error("❌ ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

    with tab2:
        u_reg = st.text_input("ตั้งชื่อผู้ใช้", key="u_reg")
        p_reg = st.text_input("ตั้งรหัสผ่าน", type="password", key="p_reg")
        p_conf = st.text_input("ยืนยันรหัสผ่านอีกครั้ง", type="password", key="p_conf")
        if st.button("สร้างบัญชีผู้ใช้", use_container_width=True):
            if u_reg and p_reg == p_conf:
                existing = db.reference(f'accounts/{u_reg}').get()
                if existing:
                    st.warning("⚠️ ชื่อนี้มีคนใช้แล้วครับ")
                else:
                    db.reference(f'accounts/{u_reg}').set({'pw': hash_pw(p_reg)})
                    st.success("✅ ลงทะเบียนสำเร็จ! กรุณาไปหน้าเข้าสู่ระบบ")
            else:
                st.error("❌ ข้อมูลไม่ครบหรือรหัสผ่านไม่ตรงกัน")

# ==========================================
# 4. ห้องสื่อสาร (Lobby & Private Chat & Call)
# ==========================================
def room_comms(theme):
    st.subheader("💬 ระบบสื่อสารไร้พรมแดน")
    tab_pub, tab_priv, tab_call = st.tabs(["🌐 Lobby", "🔐 แชตส่วนตัว", "📞 สายตรง (Call)"])
    
    # --- แชตสาธารณะ ---
    with tab_pub:
        with st.form("pub_chat", clear_on_submit=True):
            msg = st.text_input("ตะโกนบอกทุกคน...")
            if st.form_submit_button("SEND") and msg:
                db.reference('public_chat').push({'u': st.session_state.user, 'msg': msg, 'ts': time.time()})
        
        msgs = db.reference('public_chat').order_by_key().limit_to_last(15).get()
        if msgs:
            for m in reversed(list(msgs.values())):
                st.write(f"🟢 **{m.get('u')}**: {m.get('msg')}")

    # --- แชตส่วนตัว (ไม่ต้องเพิ่มเพื่อน) ---
    with tab_priv:
        all_users = db.reference('accounts').get()
        friends = [uid for uid in all_users.keys() if uid != st.session_state.user] if all_users else []
        target = st.selectbox("เลือกคนที่คุณต้องการคุยลับด้วย:", ["-- เลือกชื่อ --"] + friends)
        
        if target != "-- เลือกชื่อ --":
            room_id = "_".join(sorted([st.session_state.user, target]))
            with st.form("priv_chat", clear_on_submit=True):
                pm = st.text_input(f"กระซิบหา {target}...")
                if st.form_submit_button("🔒 ส่งข้อความส่วนตัว"):
                    db.reference(f'private_rooms/{room_id}').push({'u': st.session_state.user, 'msg': pm, 'ts': time.time()})
            
            p_msgs = db.reference(f'private_rooms/{room_id}').order_by_key().limit_to_last(20).get()
            if p_msgs:
                for pi in reversed(list(p_msgs.values())):
                    color = theme['main'] if pi.get('u') == st.session_state.user else "#888"
                    st.markdown(f"<span style='color:{color}'><b>{pi.get('u')}</b></span>: {pi.get('msg')}", unsafe_allow_html=True)

    # --- ระบบโทร (Call) ---
    with tab_call:
        target_c = st.selectbox("เลือกคนที่ต้องการโทรหา:", ["-- เลือกชื่อ --"] + friends, key="call_sel")
        if target_c != "-- เลือกชื่อ --":
            call_js = """
            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <div style="background:#111; padding:20px; border:2px solid %s; border-radius:15px; text-align:center;">
                <h3 style="color:white;">ID: %s <br>📞 กำลังติดต่อ -> %s</h3>
                <button id="callBtn" style="width:100%%; padding:15px; background:%s; color:black; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">🟢 กดเพื่อโทรออก (CALL)</button>
                <audio id="remoteAudio" autoplay style="display:none;"></audio>
            </div>
            <script>
                // ใส่ STUN Server เพื่อให้โทรผ่าน 4G ได้
                const peer = new Peer('%s', {
                    config: {'iceServers': [
                        { 'urls': 'stun:stun.l.google.com:19302' },
                        { 'urls': 'stun:stun1.l.google.com:19302' }
                    ]}
                });
                
                peer.on('call', call => {
                    navigator.mediaDevices.getUserMedia({audio:true}).then(stream => {
                        call.answer(stream);
                        call.on('stream', remoteStream => {
                            document.getElementById('remoteAudio').srcObject = remoteStream;
                        });
                    });
                });

                document.getElementById('callBtn').onclick = () => {
                    navigator.mediaDevices.getUserMedia({audio:true}).then(stream => {
                        const call = peer.call('%s', stream);
                        call.on('stream', remoteStream => {
                            document.getElementById('remoteAudio').srcObject = remoteStream;
                        });
                    });
                };
            </script>
            """ % (theme['main'], st.session_state.user, target_c, theme['main'], st.session_state.user, target_c)
            components.html(call_js, height=300)

# ==========================================
# 5. ห้องฟังเพลง (Music Room)
# ==========================================
def room_music():
    st.subheader("🎧 SYNAPSE MUSIC STATION")
    music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลง .mp3 ใน GitHub ของคุณท่าน")
        return

    curr = music_files[st.session_state.song_index]
    st.markdown(f"💿 กำลังเล่น: **{curr}**")
    st.audio(curr, format="audio/mp3", autoplay=True)

    st.write("---")
    cols = st.columns(2)
    for idx, f in enumerate(music_files):
        with cols[idx % 2]:
            if st.button(f"🎵 {f}", key=f"m_{idx}", use_container_width=True):
                st.session_state.song_index = idx
                st.rerun()

# ==========================================
# 6. แผงวงจรหลัก (Main Entry)
# ==========================================
def main():
    init_system()
    
    if not st.session_state.auth_status:
        # หน้า Login ใช้ธีมมืดพื้นฐาน
        st.markdown("<style>.stApp { background-color: #000; }</style>", unsafe_allow_html=True)
        login_page()
        return

    # แสดงเมนูที่ Sidebar
    with st.sidebar:
        st.title("⚙️ CONTROL PANEL")
        st.write(f"👤 ยินดีต้อนรับ: **{st.session_state.user}**")
        st.write('สโลแกน: **"อยู่นิ่งๆ ไม่เจ็บตัว"**')
        st.markdown("---")
        st.session_state.theme_set = st.radio("🎨 เปลี่ยนชุดสีแอป:", ["Matrix", "Ocean", "Ember"])
        if st.button("🚪 ออกจากระบบ", use_container_width=True):
            st.session_state.auth_status = False
            st.session_state.user = None
            st.rerun()

    # ใช้ธีมที่เลือก
    current_theme = apply_theme()

    # เมนูแท็บหลัก
    menu = {
        "🚀 หน้าหลัก": lambda: st.write(f"ระบบ SYNAPSE พร้อมใช้งานแล้วคุณ {st.session_state.user}"),
        "💬 สื่อสาร": lambda: room_comms(current_theme),
        "🎧 เพลง": room_music
    }
    
    tabs = st.tabs(list(menu.keys()))
    for i, (name, func) in enumerate(menu.items()):
        with tabs[i]:
            func()

if __name__ == "__main__":
    main()
