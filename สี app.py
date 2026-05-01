import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import base64
import os

# --- 0. ฟังก์ชันพิเศษ: ซ่อนความเป็น Streamlit และจัดการไฟล์ ---
def hide_streamlit_branding():
    st.markdown("""
        <style>
            /* ซ่อนเมนูขวาบน, Footer และ Header ของ Streamlit */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp { top: -60px; } /* ขยับแอปขึ้นไปแทนที่ช่องว่าง Header */
        </style>
    """, unsafe_allow_html=True)

def get_base64_bin(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

# --- 1. ตั้งค่าระบบเริ่มต้น ---
st.set_page_config(page_title="SYNAPSE PRO", layout="wide")
hide_streamlit_branding()

# แสดง Logo (logo1.png) ไว้บนสุด
if os.path.exists("logo1.png"):
    # แสดงรูปภาพ logo1.png ขนาดกว้าง 200px (ปรับได้ตามชอบ)
    col_logo, _ = st.columns([1, 4])
    with col_logo:
        st.image("logo1.png", width=200)
else:
    st.caption("⚠️ ไม่พบไฟล์ logo1.png ในระบบ")

# --- 2. การเชื่อมต่อ Firebase (เหมือนเดิม) ---
if not firebase_admin._apps:
    fb_creds = dict(st.secrets["firebase_credentials"])
    fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate(fb_creds)
    firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})

if 'user' not in st.session_state: st.session_state.user = "Agent_Ta101"
theme = "#39FF14"

# เตรียมไฟล์เสียง
audio_data = get_base64_bin("notification.mp3")

# --- 3. โครงสร้างหน้าจอแชต ---
# (ส่วน CSS และ HTML เดิมที่ปรับแต่งตัวหนังสือใหม่และระบบแจ้งเตือน)
chat_html = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    body {{ background: transparent; color: #fff; font-family: 'Orbitron', sans-serif; }}
    #chat-box {{
        background: rgba(0,0,0,0.95);
        border: 2px solid {theme};
        border-radius: 15px;
        height: 480px;
        overflow-y: auto;
        padding: 20px;
        box-shadow: 0 0 30px {theme}22;
    }}
    .msg-bubble {{
        padding: 12px 18px; border-radius: 10px; max-width: 85%; font-size: 14px; margin-bottom: 10px;
    }}
    .me {{ background: {theme}22; border-right: 4px solid {theme}; align-self: flex-end; }}
    .others {{ background: #222; border-left: 4px solid #888; align-self: flex-start; }}
    .notif-btn {{
        background: #333; color: #fff; padding: 5px 15px; border-radius: 20px; font-size: 12px;
    }}
    .active-red {{
        background: #FF0000 !important; box-shadow: 0 0 15px #FF0000; font-weight: bold;
    }}
</style>

<div id="chat-box">
    <div style="display:flex; justify-content:space-between; margin-bottom:15px; border-bottom: 1px solid #333; padding-bottom: 5px;">
        <span style="color:{theme}; font-size:12px;">🛰️ SYNAPSE_LINK_LIVE</span>
        <span id="notif" class="notif-btn">0 NEW SIGNAL</span>
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
    let lastCnt = -1;
    const sound = document.getElementById('beep');

    // คลิกเพื่อปลดล็อกเสียง
    document.addEventListener('click', () => {{
        sound.play().then(() => {{ sound.pause(); sound.currentTime = 0; }});
    }}, {{once: true}});

    // แสดงข้อความ
    db.ref('global_chat').limitToLast(20).on('child_added', (s) => {{
        const d = s.val();
        const isMe = d.user === "{st.session_state.user}";
        const box = document.getElementById('msgs');
        const div = document.createElement('div');
        div.className = "msg-bubble " + (isMe ? "me" : "others");
        div.style.alignSelf = isMe ? 'flex-end' : 'flex-start';
        
        let txt = d.text ? `<div>${{d.text}}</div>` : "";
        let img = d.img ? `<img src="data:image/png;base64,${{d.img}}" style="max-width:100%; border-radius:8px; margin-top:8px;">` : "";
        
        div.innerHTML = `<div style="font-size:9px; color:#777; margin-bottom:4px;">${{d.user}}</div>` + txt + img;
        box.appendChild(div);
        document.getElementById('chat-box').scrollTop = 999999;
    }});

    // แจ้งเตือนสีแดง + เสียง
    db.ref('chat_notifications/unread_count').on('value', (s) => {{
        const c = s.val() || 0;
        const n = document.getElementById('notif');
        n.innerText = c + " NEW SIGNAL";
        if(c > 0) {{
            n.classList.add('active-red');
            if(lastCnt !== -1 && c > lastCnt) sound.play();
        }} else {{
            n.classList.remove('active-red');
        }}
        lastCnt = c;
    }});
</script>
"""

components.html(chat_html, height=520)

# --- 4. ส่วนควบคุมการส่ง (Python) ---
with st.container():
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        msg_in = st.text_input("MSG", placeholder="ระบุสัญญาณ...", label_visibility="collapsed")
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
                cur = db.reference('chat_notifications/unread_count').get() or 0
                db.reference('chat_notifications').set(cur + 1)
                st.rerun()

if st.button("CLEAR NOTIFICATION"):
    db.reference('chat_notifications').set(0)
    st.rerun()
