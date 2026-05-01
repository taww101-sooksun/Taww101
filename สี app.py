import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import os

# ==========================================
# 0. INITIALIZATION (เชื่อมต่อระบบ)
# ==========================================
def init_chat_system():
    # ตรวจสอบการเชื่อมต่อ Firebase
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            if "private_key" in fb_creds:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ เชื่อมต่อฐานข้อมูลไม่ได้: {e}")

    # ตั้งค่าตัวแปรเบื้องต้น
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'user' not in st.session_state: st.session_state.user = "AGENT-X"

# ==========================================
# 1. THE CHAT ENGINE (JavaScript + UI)
# ==========================================
def room_chat_full_system():
    st.markdown(f"""
        <h2 style='color:{st.session_state.theme_color}; text-shadow: 0 0 15px {st.session_state.theme_color}; text-align:center;'>
            📡 SYNAPSE COMMUNICATOR
        </h2>
    """, unsafe_allow_html=True)

    db_url = st.secrets["firebase_db_url"]
    current_user = st.session_state.user
    theme_color = st.session_state.theme_color

    # ส่วนของระบบ Real-time (ดักฟัง Firebase ตรงๆ)
    chat_js_html = f"""
    <div id="chat-container" style="background:#000; border:2px solid {theme_color}; border-radius:15px; padding:15px; font-family:monospace;">
        <div style="display:flex; justify-content:space-between; margin-bottom:10px; border-bottom:1px solid #333; padding-bottom:5px;">
            <span style="color:{theme_color}; font-size:12px; font-weight:bold;">● LIVE_LINK</span>
            <span id="notif-badge" style="color:#fff; background:#444; padding:2px 10px; border-radius:10px; font-size:12px; transition: 0.3s;">0 NEW MESSAGES</span>
        </div>
        <div id="message-box" style="height:350px; overflow-y:auto; display:flex; flex-direction:column; gap:12px; padding-right:5px;"></div>
    </div>

    <audio id="notif-sound" src="https://www.soundjay.com/buttons/sounds/button-3.mp3" preload="auto"></audio>

    <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>

    <script>
        const config = {{ databaseURL: "{db_url}" }};
        if (!firebase.apps.length) {{ firebase.initializeApp(config); }}
        const db = firebase.database();
        
        const msgBox = document.getElementById('message-box');
        const notifBadge = document.getElementById('notif-badge');
        const sound = document.getElementById('notif-sound');
        const currentUser = "{current_user}";
        let lastCount = -1;

        // ดักฟังข้อความล่าสุด 50 ข้อความ
        db.ref('chat_messages').limitToLast(50).on('child_added', (snap) => {{
            const data = snap.val();
            const isMe = data.user === currentUser;
            const div = document.createElement('div');
            div.style.alignSelf = isMe ? 'flex-end' : 'flex-start';
            div.style.maxWidth = '85%';
            
            div.innerHTML = `
                <div style="font-size:10px; color:#888; margin-bottom:2px; text-align:${{isMe ? 'right' : 'left'}};">${{data.user}}</div>
                <div style="background:${{isMe ? '{theme_color}22' : '#222'}}; 
                            color:${{isMe ? '{theme_color}' : '#fff'}}; 
                            padding:10px 14px; border-radius:15px; 
                            border:1px solid ${{isMe ? '{theme_color}' : '#444'}};
                            box-shadow: ${{isMe ? '0 0 10px '+ '{theme_color}' +'33' : 'none'}};">
                    ${{data.text}}
                </div>
            `;
            msgBox.appendChild(div);
            msgBox.scrollTop = msgBox.scrollHeight;
        }});

        // ระบบแจ้งเตือนเสียงและสีแดง
        db.ref('chat_notifications/unread_count').on('value', (snap) => {{
            const count = snap.val() || 0;
            notifBadge.innerText = count + " NEW MESSAGES";
            
            if (count > 0) {{
                notifBadge.style.background = "#FF0000";
                notifBadge.style.boxShadow = "0 0 15px #FF0000";
                if (lastCount !== -1 && count > lastCount) {{
                    sound.play();
                }}
            }} else {{
                notifBadge.style.background = "#444";
                notifBadge.style.boxShadow = "none";
            }}
            lastCount = count;
        }});
    </script>
    """
    
    components.html(chat_js_html, height=450)

    # ส่วนส่งข้อความ (Python)
    with st.container():
        col_msg, col_send = st.columns([4, 1])
        with col_msg:
            user_msg = st.text_input("ENTER SIGNAL...", key="msg_input", label_visibility="collapsed")
        with col_send:
            if st.button("SEND ⚡", use_container_width=True) and user_msg:
                # ส่งข้อความ
                db.reference('chat_messages').push({
                    'user': current_user,
                    'text': user_msg,
                    'timestamp': datetime.now().isoformat()
                })
                # เพิ่มจำนวนแจ้งเตือนให้คนอื่น
                notif_ref = db.reference('chat_notifications/unread_count')
                notif_ref.set((notif_ref.get() or 0) + 1)
                st.rerun()

    if st.button("CLEAR ALL NOTIFICATIONS", use_container_width=True):
        db.reference('chat_notifications').update({'unread_count': 0})
        st.rerun()

# ==========================================
# 2. RUN APP
# ==========================================
st.set_page_config(page_title="SYNAPSE CHAT", layout="wide")
init_chat_system()
room_chat_full_system()
