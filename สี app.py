import streamlit as st
import os 
import time
from datetime import datetime, timedelta
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
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
    if 'active_target' not in st.session_state: st.session_state.active_target = None # สำหรับแชตส่วนตัว

    # เชื่อมต่อ Firebase
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
# 2. ระบบจัดการธีมสี (4 ชุดสี รวมสายรุ้ง)
# ==========================================
def apply_theme():
    # เพิ่มธีม "Rainbow" (สายรุ้ง) เข้าไปตามคำขอ
    themes = {
        "Matrix":  {"bg": "#000000", "main": "#39FF14", "text": "#FFFFFF", "chat_user": "#39FF14", "chat_friend": "#333"},
        "Ocean":   {"bg": "#001219", "main": "#00A8E8", "text": "#E0FBFC", "chat_user": "#00A8E8", "chat_friend": "#005F73"},
        "Ember":   {"bg": "#1a0000", "main": "#FF4D4D", "text": "#FFFFFF", "chat_user": "#FF4D4D", "chat_friend": "#990000"},
        "Rainbow": {"bg": "#FFFFFF", "main": "#FF69B4", "text": "#000000", "chat_user": "#FFB6C1", "chat_friend": "#E0FFFF"}
    }
    t = themes[st.session_state.theme_set]
    
    # ถ้าเป็นธีมสายรุ้ง จะเพิ่ม Gradient Background ให้
    bg_style = f"background-color: {t['bg']} !important;"
    if st.session_state.theme_set == "Rainbow":
        bg_style = "background: linear-gradient(135deg, #FF99CC, #99CCFF, #99FFCC) !important;"

    st.markdown(f"""
        <style>
        .stApp {{ {bg_style} color: {t['text']} !important; }}
        .stButton>button {{ 
            border: 2px solid {t['main']} !important; 
            color: {t['text']} !important; 
            background: {t['main']} !important; 
            border-radius: 12px;
            font-weight: bold;
        }}
        .stButton>button:hover {{ background: {t['text']} !important; color: {t['main']} !important; }}
        h1, h2, h3, h4, h5, h6, p, span, label, .stMarkdown, .stCaption {{ color: {t['text']} !important; }}
        
        .stTabs [data-baseweb="tab-list"] {{ background-color: transparent; gap: 5px; }}
        .stTabs [data-baseweb="tab"] {{ 
            color: {t['text']}; 
            border-radius: 10px 10px 0 0;
            padding: 8px 15px;
        }}
        .stTabs [aria-selected="true"] {{ 
            color: {t['main']} !important; 
            border-bottom: 3px solid {t['main']} !important; 
            font-weight: bold;
        }}
        
        /* สไตล์ช่อง Input */
        div[data-baseweb="input"] > div {{
            background-color: #f0f0f0 !important;
            color: #000 !important;
            border: 1px solid #ccc !important;
        }}
        </style>
    """, unsafe_allow_html=True)
    return t

# ==========================================
# 3. หน้าเข้าสู่ระบบ (Authentication)
# ==========================================
def login_page():
    st.title("🛡️ SYNAPSE SECURITY GATE")
    t1, t2 = st.tabs(["🔐 ลงชื่อเข้าใช้", "📝 ลงทะเบียน"])
    
    with t1:
        u_login = st.text_input("ชื่อผู้ใช้", key="u_log")
        p_login = st.text_input("รหัสผ่าน", type="password", key="p_log")
        if st.button("เข้าสู่ระบบ", use_container_width=True):
            user_data = db.reference(f'accounts/{u_login}').get()
            if user_data and user_data.get('pw') == hash_pw(p_login):
                st.session_state.auth_status = True
                st.session_state.user = u_login
                db.reference(f'users/{u_login}').update({'status': 'online', 'ts': time.time()})
                st.rerun()
            else:
                st.error("❌ ข้อมูลไม่ถูกต้อง")

    with t2:
        u_reg = st.text_input("ตั้งชื่อผู้ใช้", key="u_reg")
        p_reg = st.text_input("ตั้งรหัสผ่าน", type="password", key="p_reg")
        if st.button("สร้างบัญชี", use_container_width=True):
            if u_reg and p_reg:
                existing = db.reference(f'accounts/{u_reg}').get()
                if existing:
                    st.warning("⚠️ ชื่อนี้มีคนใช้แล้ว")
                else:
                    db.reference(f'accounts/{u_reg}').set({'pw': hash_pw(p_reg)})
                    st.success("✅ สำเร็จ! กรุณาไปหน้า Login")

# ==========================================
# 4. ห้องสื่อสาร (Comms Room)
# ==========================================
def room_comms(theme):
    st.subheader("💬 ระบบสื่อสาร SYNAPSE")
    tab_pub, tab_priv, tab_call = st.tabs(["🌐 Lobby", "🔐 แชตส่วนตัว", "📞 สายตรง (Call)"])
    
    all_users = db.reference('accounts').get()
    friends = [uid for uid in all_users.keys() if uid != st.session_state.user] if all_users else []

    # --- แชตสาธารณะ ---
    with tab_pub:
        with st.form("pub_chat", clear_on_submit=True):
            msg = st.text_input("ส่งข้อความถึงทุกคน...")
            if st.form_submit_button("SEND") and msg:
                db.reference('public_chat').push({'u': st.session_state.user, 'msg': msg, 'ts': time.time()})
        msgs = db.reference('public_chat').order_by_key().limit_to_last(15).get()
        if msgs:
            for m in reversed(list(msgs.values())):
                st.write(f"🟢 **{m.get('u')}**: {m.get('msg')}")

    # --- แชตส่วนตัว (ระบบศูนย์ควบคุมข้อความ) ---
    with tab_priv:
        st.caption("📩 ข้อความของคุณ (คลิกเพื่อเปิด)")
        all_rooms = db.reference('private_rooms').get()
        rooms_with_me = []
        if all_rooms:
            for rid in all_rooms.keys():
                if st.session_state.user in rid:
                    rooms_with_me.append(rid)
        
        # แสดงรายการห้องที่มีความเคลื่อนไหว
        if rooms_with_me:
            for rid in rooms_with_me:
                # แยกชื่อเพื่อนออกมา
                f_name = rid.replace(st.session_state.user, "").replace("_", "")
                last_msg = list(all_rooms[rid].values())[-1] # ข้อความล่าสุด
                status_color = theme['main'] if pi.get('u') == st.session_state.user else "#888"
                if st.button(f"💬 คุยกับ {f_name} (ล่าสุด: {last_msg['msg'][:20]}...)", key=f"btn_{rid}"):
                    st.session_state.active_target = f_name
        
        st.divider()
        
        # ส่วนเลือกเพื่อน หรือแสดงห้องที่เลือก
        target_p = st.selectbox("เลือกคนที่ต้องการคุยด้วย (ส่วนตัว):", ["-- เลือกชื่อเพื่อน --"] + friends, 
                                index=friends.index(st.session_state.active_target) + 1 if st.session_state.active_target in friends else 0)
        
        if target_p != "-- เลือกชื่อเพื่อน --":
            st.session_state.active_target = target_p
            room_id = "_".join(sorted([st.session_state.user, target_p]))
            
            with st.form("priv_chat", clear_on_submit=True):
                pm = st.text_input(f"ส่งข้อความถึง {target_p}...")
                if st.form_submit_button("🔒 SEND PRIVATE"):
                    db.reference(f'private_rooms/{room_id}').push({'u': st.session_state.user, 'msg': pm, 'ts': time.time()})
            
            p_msgs = db.reference(f'private_rooms/{room_id}').order_by_key().limit_to_last(20).get()
            if p_msgs:
                for pi in reversed(list(p_msgs.values())):
                    # จัดรูปแบบแชตแยกฝั่งซ้าย-ขวา
                    align = "right" if pi.get('u') == st.session_state.user else "left"
                    bg = theme['chat_user'] if pi.get('u') == st.session_state.user else theme['chat_friend']
                    txt_c = "#000" if pi.get('u') == st.session_state.user else "#fff"
                    st.markdown(f"""
                        <div style="text-align: {align}; margin-bottom: 5px;">
                            <div style="display: inline-block; background: {bg}; color: {txt_c}; padding: 8px 15px; border-radius: 15px;">
                                <b>{pi.get('u')}</b>: {pi.get('msg')}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

    # --- ระบบโทร (CALL - พร้อมปุ่มวางสาย) ---
    with tab_call:
        target_c = st.selectbox("โทรหาใครดีครับ:", ["-- เลือกชื่อ --"] + friends, key="c_sel")
        if target_c != "-- เลือกชื่อ --":
            # ระบบ PeerJS ตัวเต็ม พร้อมปุ่มวางสาย
            call_html = """
            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <div style="background:#111; padding:20px; border-radius:15px; border:2px solid %s; text-align:center;">
                <p style="color:white;">สายของคุณ: <b>%s</b> -> <b>%s</b></p>
                <div style="display: flex; gap: 10px; justify-content: center;">
                    <button id="callBtn" style="flex: 1; padding:15px; background:%s; color:black; border:none; border-radius:10px; font-weight:bold; cursor:pointer;">🟢 CALL</button>
                    <button id="hangupBtn" style="flex: 1; padding:15px; background:#FF4D4D; color:white; border:none; border-radius:10px; font-weight:bold; cursor:pointer; display:none;">🔴 วางสาย</button>
                </div>
                <audio id="remoteAudio" autoplay></audio>
                <p id="status" style="color:#888; font-size:12px; margin-top:10px;">สถานะ: พร้อมใช้งาน</p>
            </div>
            <script>
                const peer = new Peer('%s', {
                    config: {'iceServers': [{ 'urls': 'stun:stun.l.google.com:19302' }, { 'urls': 'stun:stun1.l.google.com:19302' }]}
                });
                let currentCall = null;

                peer.on('call', c => {
                    navigator.mediaDevices.getUserMedia({audio:true}).then(s => {
                        c.answer(s);
                        handleCall(c);
                    });
                });

                function handleCall(c) {
                    currentCall = c;
                    document.getElementById('callBtn').style.display = 'none';
                    document.getElementById('hangupBtn').style.display = 'block';
                    document.getElementById('status').innerText = 'สถานะ: กำลังคุยสาย...';
                    
                    c.on('stream', rs => { document.getElementById('remoteAudio').srcObject = rs; });
                    c.on('close', () => { endCall(); });
                }

                function endCall() {
                    if(currentCall) currentCall.close();
                    document.getElementById('callBtn').style.display = 'block';
                    document.getElementById('hangupBtn').style.display = 'none';
                    document.getElementById('status').innerText = 'สถานะ: วางสายแล้ว';
                    document.getElementById('remoteAudio').srcObject = null;
                }

                document.getElementById('callBtn').onclick = () => {
                    navigator.mediaDevices.getUserMedia({audio:true}).then(s => {
                        const c = peer.call('%s', s);
                        handleCall(c);
                    });
                };
                document.getElementById('hangupBtn').onclick = () => { endCall(); };
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
        # หน้า Login ใช้ธีมมืดพื้นฐาน
        st.markdown("<style>.stApp { background-color: #000; color: #fff; }</style>", unsafe_allow_html=True)
        login_page()
        return

    # แสดงเมนูที่ Sidebar
    with st.sidebar:
        st.title("⚙️ CONTROL")
        st.write(f"👤 User: **{st.session_state.user}**")
        st.write('สโลแกน: **"อยู่นิ่งๆ ไม่เจ็บตัว"**')
        st.markdown("---")
        # เพิ่มตัวเลือก "Rainbow" เข้าไป
        st.session_state.theme_set = st.radio("🎨 เลือกชุดสีแอป:", ["Matrix", "Ocean", "Ember", "Rainbow"])
        if st.button("🚪 LOGOUT", use_container_width=True):
            st.session_state.auth_status = False
            st.session_state.user = None
            st.rerun()

    # ใช้ธีมที่เลือก
    current_theme = apply_theme()

    # แท็บเมนูหลัก
    menu = {"💬 สื่อสาร": lambda: room_comms(current_theme), "🎧 เพลง": room_music}
    tabs = st.tabs(list(menu.keys()))
    for i, func in enumerate(menu.values()):
        with tabs[i]: func()

if __name__ == "__main__":
    main()
