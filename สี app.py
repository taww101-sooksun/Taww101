import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import base64
import os
def room_login():
    # แสดงโลโก้ logo1.jpg ที่กลางหน้าจอ
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("logo1.jpg", use_container_width=True)
        except:
            st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color};'>SYNAPSE</h1>", unsafe_allow_html=True)
# --- 1. เตรียมไฟล์เสียงแจ้งเตือน ---
def get_audio_base64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

# --- 2. ฟังก์ชันแปลงรูปภาพเป็นรหัส ---
def image_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode()

# --- 3. ตั้งค่าระบบเริ่มต้น ---
st.set_page_config(page_title="SYNAPSE PRO", layout="wide")

if not firebase_admin._apps:
    fb_creds = dict(st.secrets["firebase_credentials"])
    fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate(fb_creds)
    firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})

if 'user' not in st.session_state: st.session_state.user = "Agent_Ta101" # ดึงชื่อจากระบบของคุณ
theme = "#39FF14"

# --- 4. ดึงไฟล์เสียงเตรียมไว้ ---
audio_data = get_audio_base64("notification.mp3")

# --- 5. โครงสร้างหน้าจอแชต ---
st.markdown(f"<h2 style='color:{theme}; text-shadow: 0 0 10px {theme}; text-align:center;'>📡 SYNAPSE COMMUNICATOR</h2>", unsafe_allow_html=True)

chat_html = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    body {{ background: transparent; color: #fff; font-family: 'Orbitron', sans-serif; }}
    #chat-box {{
        background: rgba(0,0,0,0.9);
        border: 2px solid {theme};
        border-radius: 15px;
        height: 500px;
        overflow-y: auto;
        padding: 20px;
        display: flex;
        flex-direction: column;
        gap: 15px;
        box-shadow: inset 0 0 20px {theme}33;
    }}
    .msg-bubble {{
        padding: 12px 18px;
        border-radius: 10px;
        max-width: 85%;
        font-size: 14px;
        line-height: 1.5;
        border: 1px solid rgba(255,255,255,0.1);
    }}
    .me {{ background: {theme}22; border-right: 4px solid {theme}; align-self: flex-end; }}
    .others {{ background: #222; border-left: 4px solid #888; align-self: flex-start; }}
    .notif-active {{
        background: #FF0000 !important;
        box-shadow: 0 0 20px #FF0000 !important;
        color: white !important;
    }}
</style>

<div id="chat-box">
    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
        <span style="color:{theme}; font-size:12px;">● LIVE_SIGNAL</span>
        <span id="notif-btn" style="background:#444; padding:3px 12px; border-radius:20px; font-size:11px; transition:0.3s;">0 NEW</span>
    </div>
    <div id="message-container" style="display:flex; flex-direction:column; gap:12px;"></div>
</div>

<audio id="notif-sound" src="data:audio/mp3;base64,{audio_data}" preload="auto"></audio>

<script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
<script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>

<script>
    const config = {{ databaseURL: "{st.secrets['firebase_db_url']}" }};
    if (!firebase.apps.length) firebase.initializeApp(config);
    const db = firebase.database();
    let lastUnread = -1;

    // --- ฟังก์ชันปลดล็อกเสียง ---
    const sound = document.getElementById('notif-sound');
    function unlock() {{
        sound.play().then(() => {{ sound.pause(); sound.currentTime = 0; }});
        document.removeEventListener('click', unlock);
    }}
    document.addEventListener('click', unlock);

    // --- รับข้อความและรูปภาพ ---
    db.ref('global_chat').limitToLast(25).on('child_added', (snap) => {{
        const d = snap.val();
        if(!d) return;
        const isMe = d.user === "{st.session_state.user}";
        const box = document.getElementById('message-container');
        
        const div = document.createElement('div');
        div.className = "msg-bubble " + (isMe ? "me" : "others");
        
        let html = `<div style="font-size:10px; color:#999; margin-bottom:5px;">${{d.user}}</div>`;
        if(d.text) html += `<div>${{d.text}}</div>`;
        if(d.img) html += `<img src="data:image/png;base64,${{d.img}}" style="max-width:100%; border-radius:8px; margin-top:8px; border:1px solid #444;">`;
        
        div.innerHTML = html;
        box.appendChild(div);
        document.getElementById('chat-box').scrollTop = 999999;
    }});

    // --- ระบบไฟแดงและเสียงแจ้งเตือน ---
    db.ref('chat_notifications/unread_count').on('value', (snap) => {{
        const count = snap.val() || 0;
        const btn = document.getElementById('notif-btn');
        btn.innerText = count + " NEW SIGNAL";
        
        if(count > 0) {{
            btn.classList.add('notif-active');
            if(lastUnread !== -1 && count > lastUnread) {{
                sound.currentTime = 0;
                sound.play().catch(e => console.log("คลิกหน้าจอก่อนนะเพื่อน!"));
            }}
        }} else {{
            btn.classList.remove('notif-active');
        }}
        lastUnread = count;
    }});
</script>
"""

components.html(chat_html, height=550)

# --- 6. ส่วนควบคุมการส่งข้อความและรูปภาพ (Python) ---
with st.container():
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        msg_input = st.text_input("MESSAGE", placeholder="ส่งข้อความ...", label_visibility="collapsed")
    with c2:
        img_upload = st.file_uploader("IMG", type=['jpg','png','jpeg'], label_visibility="collapsed")
    with c3:
        if st.button("SEND ⚡", use_container_width=True):
            if msg_input or img_upload:
                data = {'user': st.session_state.user, 'ts': datetime.now().isoformat()}
                if msg_input: data['text'] = msg_input
                if img_upload: data['img'] = image_to_base64(img_upload)
                
                db.reference('global_chat').push(data)
                
                # อัปเดตตัวเลขแจ้งเตือนให้เพื่อนเห็นไฟแดง
                current_unread = db.reference('chat_notifications/unread_count').get() or 0
                db.reference('chat_notifications').set({'unread_count': current_unread + 1})
                st.rerun()

if st.button("ล้างการแจ้งเตือน"):
    db.reference('chat_notifications').set({'unread_count': 0})
    st.rerun()
