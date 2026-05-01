import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import base64
import os

# ==========================================
# 0. CONFIG & LOGO FUNCTION
# ==========================================
def get_base64_bin(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

# ==========================================
# 1. INITIALIZATION & HIDE STREAMLIT UI
# ==========================================
st.set_page_config(page_title="SYNAPSE PRO", layout="wide")

st.markdown("""
    <style>
        /* ซ่อน Streamlit UI ทั้งหมด */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp { top: -60px; } /* ขยับแอปขึ้นไป */
        
        /* สไตล์หลักสำหรับทั้งหน้า */
        body {
            background-color: #000;
            color: #fff;
            font-family: monospace;
        }
    </style>
""", unsafe_allow_html=True)

# ดึงไฟล์โลโก้และเสียงเตรียมไว้
logo_base64 = get_base64_bin("logo1.png")
audio_data = get_base64_bin("notification.mp3")

if not firebase_admin._apps:
    fb_creds = dict(st.secrets["firebase_credentials"])
    fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate(fb_creds)
    firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})

if 'user' not in st.session_state: st.session_state.user = "Agent_Ta101"
theme = "#39FF14"

# ==========================================
# 2. LOGO (100) DANCING + SLOGAN WINKING
# ==========================================
logo_and_slogan_html = f"""
<style>
    /* แอนิเมชันสำหรับโลโก้เต้น */
    @keyframes dance {{
        0% {{ transform: translate(0, 0) rotate(0deg); }}
        25% {{ transform: translate(2px, -3px) rotate(3deg); }}
        50% {{ transform: translate(-2px, 3px) rotate(-3deg); }}
        75% {{ transform: translate(1px, -1px) rotate(1deg); }}
        100% {{ transform: translate(0, 0) rotate(0deg); }}
    }}

    /* แอนิเมชันสำหรับตัวหนังสือวิ้งๆ */
    @keyframes wink {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0; }}
    }}

    .dancing-logo {{
        width: 100px;
        height: auto;
        animation: dance 0.5s infinite; /* ปรับเวลาให้เร็วขึ้นสำหรับ 'เต้น' */
    }}

    .winking-slogan {{
        font-family: sans-serif;
        font-size: 16px;
        color: #fff;
        margin-left: 15px;
        animation: wink 1s infinite step-end; /* เวิ้งๆ แบบกะพริบ */
        vertical-align: middle;
    }}
</style>

<div style="display: flex; align-items: center; justify-content: center; width: 100%; padding: 10px 0;">
    <img src="data:image/png;base64,{logo_base64}" class="dancing-logo">
    <span class="winking-slogan">SYNAPSE อยู่นิ้งๆไม่เจ็บตัว</span>
</div>
"""
components.html(logo_and_slogan_html, height=130)

# ==========================================
# 3. CHAT ROOM (Real-time, เสียง, รูปภาพ)
# ==========================================
st.markdown(f"<h3 style='color:{theme}; text-shadow: 0 0 10px {theme}; text-align:center;'>📡 ศูนย์สื่อสาร SYNAPSE</h3>", unsafe_allow_html=True)

chat_html = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    body {{ background: transparent; color: #fff; font-family: 'Orbitron', sans-serif; }}
    #chat-box {{
        background: rgba(0,0,0,0.9);
        border: 2px solid {theme};
        border-radius: 15px;
        height: 400px;
        overflow-y: auto;
        padding: 20px;
        box-shadow: inset 0 0 20px {theme}22, 0 0 10px {theme}44;
    }}
    .msg-bubble {{
        padding: 10px 15px; border-radius: 10px; max-width: 80%; font-size: 14px; margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.1);
    }}
    .me {{ background: {theme}22; border-right: 4px solid {theme}; align-self: flex-end; }}
    .others {{ background: #222; border-left: 4px solid #888; align-self: flex-start; }}
    .notif-active {{
        background: #FF0000 !important;
        box-shadow: 0 0 15px #FF0000 !important;
        color: white !important;
    }}
</style>

<div id="chat-box">
    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
        <span style="color:{theme}; font-size:12px;">● SIGNAL_STABLE</span>
        <span id="notif-btn" style="background:#444; padding:2px 10px; border-radius:10px; font-size:11px; transition: 0.3s;">0 NEW SIGNAL</span>
    </div>
    <div id="msgs" style="display:flex; flex-direction:column; gap:10px;"></div>
</div>

<audio id="beep" src="data:audio/mp3;base64,{audio_data}" preload="auto"></audio>

<script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
<script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>

<script>
    const conf = {{ databaseURL: "{st.secrets['firebase_db_url']}" }};
    if(!firebase.apps.length) firebase.initializeApp(conf);
    const db = firebase.database();
    let lastUnread = -1;
    const sound = document.getElementById('beep');

    // คลิกปลดล็อกเสียง
    document.addEventListener('click', () => {{
        sound.play().then(() => {{ sound.pause(); sound.currentTime = 0; }});
    }}, {{once: true}});

    // แสดงแชต
    db.ref('global_chat').limitToLast(20).on('child_added', (snap) => {{
        const d = snap.val();
        if(!d) return;
        const isMe = d.user === "{st.session_state.user}";
        const box = document.getElementById('msgs');
        const div = document.createElement('div');
        div.className = "msg-bubble " + (isMe ? "me" : "others");
        div.style.alignSelf = isMe ? 'flex-end' : 'flex-start';
        
        let txt = d.text ? `<div>${{d.text}}</div>` : "";
        let img = d.img ? `<img src="data:image/png;base64,${{d.img}}" style="max-width:100%; border-radius:8px; margin-top:8px;">` : "";
        
        div.innerHTML = `<div style="font-size:9px; color:#666; margin-bottom:4px;">[ ${{d.user}} ]</div>` + txt + img;
        box.appendChild(div);
        document.getElementById('chat-box').scrollTop = 999999;
    }});

    // แจ้งเตือนไฟแดงและเสียง
    db.ref('chat_notifications/unread_count').on('value', (snap) => {{
        const c = snap.val() || 0;
        const btn = document.getElementById('notif-btn');
        btn.innerText = c + " NEW SIGNAL";
        
        if(c > 0) {{
            btn.classList.add('notif-active');
            if(lastUnread !== -1 && c > lastUnread) sound.play().catch(() => {{}});
        }} else {{
            btn.classList.remove('notif-active');
        }}
        lastUnread = c;
    }});
</script>
"""
components.html(chat_html, height=450)

# ==========================================
# 4. SEND (Python)
# ==========================================
with st.container():
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        msg_in = st.text_input("MSG", placeholder="ส่งข้อความ...", label_visibility="collapsed")
    with c2:
        up_img = st.file_uploader("IMG", type=['png','jpg','jpeg'], label_visibility="collapsed")
    with c3:
        if st.button("SEND ⚡", use_container_width=True):
            if msg_in or up_img:
                p_load = {'user': st.session_state.user, 'ts': datetime.now().isoformat()}
                if msg_in: p_load['text'] = msg_in
                if up_img: 
                    with up_img:
                        p_load['img'] = base64.b64encode(up_img.read()).decode()
                
                db.reference('global_chat').push(p_load)
                
                # เพิ่มเลขแจ้งเตือน
                current = db.reference('chat_notifications/unread_count').get() or 0
                db.reference('chat_notifications').set(current + 1)
                st.rerun()

if st.button("ล้างแจ้งเตือน"):
    db.reference('chat_notifications').set(0)
    st.rerun()
