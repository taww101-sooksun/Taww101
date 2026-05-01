import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import os

# ==========================================
# 0. CONFIG & INITIALIZATION
# ==========================================
def init_all_systems():
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            if "private_key" in fb_creds:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ ระบบเชื่อมต่อขัดข้อง: {e}")

    # Session States
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user' not in st.session_state: st.session_state.user = None
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"

# ==========================================
# 1. LOGIN & REGISTER SYSTEM
# ==========================================
def auth_gate():
    st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color}; text-shadow: 0 0 15px {st.session_state.theme_color};'>SYNAPSE OS</h1>", unsafe_allow_html=True)
    
    auth_tab, reg_tab = st.tabs(["🔑 LOGIN", "📝 REGISTER"])
    
    with auth_tab:
        with st.form("login_form"):
            u = st.text_input("AGENT ID")
            p = st.text_input("PASSWORD", type="password")
            if st.form_submit_button("CONNECT ⚡", use_container_width=True):
                user_data = db.reference(f'users/{u}').get()
                if user_data and user_data.get('password') == p:
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("❌ ข้อมูลไม่ถูกต้อง")

    with reg_tab:
        with st.form("reg_form"):
            new_u = st.text_input("NEW AGENT ID")
            new_p = st.text_input("NEW PASSWORD", type="password")
            confirm = st.text_input("CONFIRM PASSWORD", type="password")
            if st.form_submit_button("CREATE AGENT", use_container_width=True):
                if new_u and new_p == confirm:
                    db.reference(f'users/{new_u}').set({
                        'password': new_p,
                        'created_at': datetime.now().isoformat(),
                        'friends': []
                    })
                    st.success("✅ ลงทะเบียนสำเร็จ! กรุณาไปหน้า Login")
                else:
                    st.error("❌ ตรวจสอบข้อมูลอีกครั้ง")

# ==========================================
# 2. FRIEND & CHAT ENGINE (JavaScript)
# ==========================================
def room_communicator():
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("👥 FRIENDS")
        # ส่วนเพิ่มเพื่อน
        friend_id = st.text_input("ADD ID", placeholder="Agent Name...", label_visibility="collapsed")
        if st.button("➕ ADD FRIEND", use_container_width=True):
            if db.reference(f'users/{friend_id}').get():
                my_ref = db.reference(f'users/{st.session_state.user}/friends')
                friends = my_ref.get() or []
                if friend_id not in friends:
                    friends.append(friend_id)
                    my_ref.set(friends)
                    st.success("เพิ่มแล้ว")
                else: st.warning("มีรายชื่ออยู่แล้ว")
            else: st.error("ไม่พบ Agent นี้")
        
        st.write("---")
        # แสดงรายการเพื่อน
        my_friends = db.reference(f'users/{st.session_state.user}/friends').get() or []
        for f in my_friends:
            st.button(f"👤 {f}", use_container_width=True)

    with col2:
        # ระบบแชต Real-time (JS)
        db_url = st.secrets["firebase_db_url"]
        theme = st.session_state.theme_color
        current_u = st.session_state.user

        chat_html = f"""
        <div id="chat-ui" style="background:#000; border:2px solid {theme}; border-radius:15px; padding:15px; font-family:monospace;">
            <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                <span style="color:{theme}; font-size:12px;">● SIGNAL_STABLE</span>
                <span id="notif" style="color:#fff; background:#444; padding:2px 10px; border-radius:10px; font-size:12px;">0 NEW</span>
            </div>
            <div id="msg-box" style="height:300px; overflow-y:auto; display:flex; flex-direction:column; gap:10px;"></div>
        </div>
        <audio id="beep" src="https://www.soundjay.com/buttons/sounds/button-3.mp3" preload="auto"></audio>
        
        <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
        <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
        <script>
            const cfg = {{ databaseURL: "{db_url}" }};
            if (!firebase.apps.length) firebase.initializeApp(cfg);
            const db = firebase.database();
            let lastCnt = -1;

            // ดักข้อความ
            db.ref('chat_messages').limitToLast(30).on('child_added', (s) => {{
                const d = s.val();
                const isMe = d.user === "{current_u}";
                const div = document.createElement('div');
                div.style.alignSelf = isMe ? 'flex-end' : 'flex-start';
                div.innerHTML = `<div style="font-size:9px; color:#888;">${{d.user}}</div>
                                 <div style="background:${{isMe ? '{theme}22':'#222'}}; color:${{isMe ? '{theme}':'#fff'}}; 
                                 padding:8px 12px; border-radius:10px; border:1px solid ${{isMe ? '{theme}':'#444'}};">${{d.text}}</div>`;
                document.getElementById('msg-box').appendChild(div);
                document.getElementById('msg-box').scrollTop = 99999;
            }});

            // แจ้งเตือนสีแดง + เสียง
            db.ref('chat_notifications/unread_count').on('value', (s) => {{
                const c = s.val() || 0;
                const n = document.getElementById('notif');
                n.innerText = c + " NEW";
                if(c > 0) {{ 
                    n.style.background = "#F00"; n.style.boxShadow = "0 0 10px #F00";
                    if(lastCnt !== -1 && c > lastCnt) document.getElementById('beep').play();
                }} else {{ n.style.background = "#444"; n.style.boxShadow = "none"; }}
                lastCnt = c;
            }});
        </script>
        """
        components.html(chat_html, height=400)

        # ช่องส่งข้อความ (Python)
        with st.form("send_msg", clear_on_submit=True):
            m = st.text_input("MESSAGE", label_visibility="collapsed")
            if st.form_submit_button("SEND ⚡", use_container_width=True) and m:
                db.reference('chat_messages').push({'user': current_u, 'text': m, 'time': datetime.now().isoformat()})
                # อัปเดตแจ้งเตือน
                cnt = db.reference('chat_notifications/unread_count').get() or 0
                db.reference('chat_notifications').update({'unread_count': cnt + 1})

    if st.button("CLEAR ALL NOTIFICATIONS"):
        db.reference('chat_notifications').update({'unread_count': 0})
        st.rerun()

# ==========================================
# MAIN EXECUTION
# ==========================================
st.set_page_config(page_title="SYNAPSE OS", layout="wide")
init_all_systems()

if not st.session_state.logged_in:
    auth_gate()
else:
    st.sidebar.write(f"👤 AGENT: {st.session_state.user}")
    if st.sidebar.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()
    room_communicator()
