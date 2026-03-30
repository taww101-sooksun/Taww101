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
    if 'active_target' not in st.session_state: st.session_state.active_target = None 

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
# 2. ระบบจัดการธีมสี (4 ชุดสี รวมสายรุ้ง)
# ==========================================
def apply_theme():
    themes = {
        "Matrix":  {"bg": "#000000", "main": "#39FF14", "text": "#FFFFFF", "chat_user": "#39FF14", "chat_friend": "#333"},
        "Ocean":   {"bg": "#001219", "main": "#00A8E8", "text": "#E0FBFC", "chat_user": "#00A8E8", "chat_friend": "#005F73"},
        "Ember":   {"bg": "#1a0000", "main": "#FF4D4D", "text": "#FFFFFF", "chat_user": "#FF4D4D", "chat_friend": "#990000"},
        "Rainbow": {"bg": "#FFFFFF", "main": "#FF69B4", "text": "#000000", "chat_user": "#FFB6C1", "chat_friend": "#E0FFFF"}
    }
    t = themes[st.session_state.theme_set]
    bg_style = f"background-color: {t['bg']} !important;"
    if st.session_state.theme_set == "Rainbow":
        bg_style = "background: linear-gradient(135deg, #FF99CC, #99CCFF, #99FFCC) !important;"

    st.markdown(f"""
        <style>
        .stApp {{ {bg_style} color: {t['text']} !important; }}
        .stButton>button {{ border: 2px solid {t['main']} !important; color: {t['text']} !important; background: {t['main']} !important; border-radius: 12px; font-weight: bold; }}
        h1, h2, h3, p, span, label, .stMarkdown {{ color: {t['text']} !important; }}
        .stTabs [aria-selected="true"] {{ color: {t['main']} !important; border-bottom: 3px solid {t['main']} !important; }}
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
        u = st.text_input("ชื่อผู้ใช้", key="l_u")
        p = st.text_input("รหัสผ่าน", type="password", key="l_p")
        if st.button("เข้าสู่ระบบ", use_container_width=True):
            data = db.reference(f'accounts/{u}').get()
            if data and data.get('pw') == hash_pw(p):
                st.session_state.auth_status, st.session_state.user = True, u
                st.rerun()
            else: st.error("❌ ข้อมูลไม่ถูกต้อง")
    with t2:
        ru = st.text_input("New User", key="r_u")
        rp = st.text_input("New PW", type="password", key="r_p")
        if st.button("สร้างบัญชี", use_container_width=True):
            if ru and rp:
                db.reference(f'accounts/{ru}').set({'pw': hash_pw(rp)})
                st.success("✅ สำเร็จ!")

# ==========================================
# 4. ห้องสื่อสาร (Comms Room - FIXED)
# ==========================================
def room_comms(theme):
    st.subheader("💬 ระบบสื่อสาร SYNAPSE")
    tab_pub, tab_priv, tab_call = st.tabs(["🌐 Lobby", "🔐 แชตส่วนตัว", "📞 สายตรง (Call)"])
    
    all_users = db.reference('accounts').get()
    friends = [uid for uid in all_users.keys() if uid != st.session_state.user] if all_users else []

    with tab_pub:
        with st.form("pub_chat", clear_on_submit=True):
            msg = st.text_input("ส่งข้อความถึงทุกคน...")
            if st.form_submit_button("SEND") and msg:
                db.reference('public_chat').push({'u': st.session_state.user, 'msg': msg, 'ts': time.time()})
        msgs = db.reference('public_chat').order_by_key().limit_to_last(15).get()
        if msgs:
            for m in reversed(list(msgs.values())):
                st.write(f"🟢 **{m.get('u')}**: {m.get('msg')}")

    with tab_priv:
        st.caption("📩 ข้อความที่ทักมา")
        all_rooms = db.reference('private_rooms').get()
        if all_rooms:
            for rid in all_rooms.keys():
                if st.session_state.user in rid:
                    f_name = rid.replace(st.session_state.user, "").replace("_", "")
                    last_m = list(all_rooms[rid].values())[-1]
                    # แก้จุด Error: เปลี่ยนจาก pi เป็น last_m
                    if st.button(f"💬 {f_name}: {last_m['msg'][:15]}...", key=f"btn_{rid}"):
                        st.session_state.active_target = f_name
        
        st.divider()
        target_p = st.selectbox("เลือกเพื่อน:", ["-- เลือกชื่อ --"] + friends, 
                                index=friends.index(st.session_state.active_target) + 1 if st.session_state.active_target in friends else 0)
        
        if target_p != "-- เลือกชื่อ --":
            st.session_state.active_target = target_p
            room_id = "_".join(sorted([st.session_state.user, target_p]))
            with st.form("priv_chat", clear_on_submit=True):
                pm = st.text_input(f"กระซิบถึง {target_p}...")
                if st.form_submit_button("SEND"):
                    db.reference(f'private_rooms/{room_id}').push({'u': st.session_state.user, 'msg': pm, 'ts': time.time()})
            
            p_msgs = db.reference(f'private_rooms/{room_id}').order_by_key().limit_to_last(15).get()
            if p_msgs:
                for pi in reversed(list(p_msgs.values())):
                    align = "right" if pi.get('u') == st.session_state.user else "left"
                    bg = theme['chat_user'] if pi.get('u') == st.session_state.user else theme['chat_friend']
                    st.markdown(f'<div style="text-align:{align};"><div style="display:inline-block; background:{bg}; padding:8px 12px; border-radius:10px; margin:2px; color:#000;"><b>{pi.get('u')}</b>: {pi.get('msg')}</div></div>', unsafe_allow_html=True)

    with tab_call:
        target_c = st.selectbox("โทรหาใคร:", ["-- เลือกชื่อ --"] + friends, key="c_sel")
        if target_c != "-- เลือกชื่อ --":
            call_html = """
            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <div style="background:#111; padding:20px; border-radius:15px; border:2px solid %s; text-align:center;">
                <p style="color:white;">ID: %s -> %s</p>
                <button id="callBtn" style="padding:15px; background:%s; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">🟢 โทรออก</button>
                <button id="hangupBtn" style="padding:15px; background:#FF4D4D; color:white; border:none; border-radius:10px; font-weight:bold; cursor:pointer; display:none;">🔴 วางสาย</button>
                <audio id="remoteAudio" autoplay></audio>
            </div>
            <script>
                const peer = new Peer('%s', {config: {'iceServers': [{ 'urls': 'stun:stun.l.google.com:19302' }]}});
                let currCall = null;
                peer.on('call', c => { navigator.mediaDevices.getUserMedia({audio:true}).then(s => { c.answer(s); handle(c); }); });
                function handle(c) { 
                    currCall = c; 
                    document.getElementById('callBtn').style.display='none'; 
                    document.getElementById('hangupBtn').style.display='inline';
                    c.on('stream', rs => { document.getElementById('remoteAudio').srcObject = rs; });
                }
                document.getElementById('callBtn').onclick = () => { navigator.mediaDevices.getUserMedia({audio:true}).then(s => { const c = peer.call('%s', s); handle(c); }); };
                document.getElementById('hangupBtn').onclick = () => { if(currCall) currCall.close(); location.reload(); };
            </script>
            """ % (theme['main'], st.session_state.user, target_c, theme['main'], st.session_state.user, target_c)
            components.html(call_html, height=250)

# ==========================================
# 5. ห้องเพลง & Main
# ==========================================
def room_music():
    st.subheader("🎧 SYNAPSE MUSIC")
    files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if files:
        st.audio(files[st.session_state.song_index], autoplay=True)
        for idx, f in enumerate(files):
            if st.button(f"🎵 {f}", key=f"m_{idx}"):
                st.session_state.song_index = idx
                st.rerun()

def main():
    init_system()
    if not st.session_state.auth_status:
        login_page()
        return
    with st.sidebar:
        st.title("⚙️ CONTROL")
        st.write(f"👤 User: **{st.session_state.user}**")
        st.session_state.theme_set = st.radio("🎨 เลือกธีม:", ["Matrix", "Ocean", "Ember", "Rainbow"])
        if st.button("🚪 LOGOUT"): st.session_state.auth_status = False; st.rerun()
    
    t = apply_theme()
    menu = {"💬 สื่อสาร": lambda: room_comms(t), "🎧 เพลง": room_music}
    tabs = st.tabs(list(menu.keys()))
    for i, func in enumerate(menu.values()):
        with tabs[i]: func()

if __name__ == "__main__":
    main()
