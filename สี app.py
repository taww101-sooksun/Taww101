import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import base64
import os

# --- 1. แปลงไฟล์เสียงในเครื่องเป็น Base64 (เพื่อให้เสียงดังชัวร์) ---
def get_audio_base64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except: return ""

# --- 2. ฟังก์ชันจัดการรูปภาพ (แปลงรูปส่งเข้า Firebase) ---
def image_to_base64(image_file):
    return base64.b64encode(image_file.read()).decode()

# --- 3. ตั้งค่าระบบ ---
st.set_page_config(page_title="SYNAPSE OS", layout="wide")

if not firebase_admin._apps:
    fb_creds = dict(st.secrets["firebase_credentials"])
    fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate(fb_creds)
    firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None
theme = "#39FF14" # สีเขียวนีออนหลักของคุณ

# --- 4. UI หน้า LOGIN / REGISTER ---
if not st.session_state.logged_in:
    st.markdown(f"<h1 style='text-align:center; color:{theme}; text-shadow: 0 0 20px {theme};'>SYNAPSE CONNECT</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 LOGIN", "📝 REGISTER"])
    with tab1:
        with st.form("l_form"):
            u = st.text_input("AGENT ID")
            p = st.text_input("PASSWORD", type="password")
            if st.form_submit_button("CONNECT ⚡", use_container_width=True):
                data = db.reference(f'users/{u}').get()
                if data and data.get('password') == p:
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.rerun()
    with tab2:
        with st.form("r_form"):
            nu = st.text_input("NEW ID")
            np = st.text_input("NEW PASS", type="password")
            if st.form_submit_button("CREATE"):
                db.reference(f'users/{nu}').set({'password': np, 'friends': []})
                st.success("สร้างสำเร็จ")
    st.stop()

# --- 5. ระบบแชต & แจ้งเตือน (ชุดรวม) ---
audio_data = get_audio_base64("notification.mp3")

col1, col2 = st.columns([1, 3])

with col1:
    st.markdown(f"<h4 style='color:{theme}'>👤 {st.session_state.user}</h4>", unsafe_allow_html=True)
    f_id = st.text_input("ADD FRIEND ID")
    if st.button("➕ ADD"):
        my_ref = db.reference(f'users/{st.session_state.user}/friends')
        fs = my_ref.get() or []
        if f_id not in fs:
            fs.append(f_id); my_ref.set(fs); st.rerun()

with col2:
    # JavaScript จัดการ Real-time Chat, เสียง และ รูปภาพ
    chat_html = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
        .chat-font {{ font-family: 'Orbitron', sans-serif; letter-spacing: 1px; }}
    </style>
    <div id="chat-box" style="background:#050505; border:1px solid {theme}66; border-radius:10px; padding:15px; height:450px; overflow-y:auto; display:flex; flex-direction:column; gap:15px;">
        <div style="display:flex; justify-content:space-between; border-bottom:1px solid #222; padding-bottom:5px;">
            <span style="color:{theme}; font-size:10px;">SYSTEM_ONLINE</span>
            <span id="notif" style="color:#fff; background:#444; padding:2px 8px; border-radius:5px; font-size:10px;">0 NEW</span>
        </div>
        <div id="msgs" class="chat-font" style="display:flex; flex-direction:column; gap:10px;"></div>
    </div>
    <audio id="beep" src="data:audio/mp3;base64,{audio_data}" preload="auto"></audio>
    
    <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
    <script>
        const conf = {{ databaseURL: "{st.secrets['firebase_db_url']}" }};
        if(!firebase.apps.length) firebase.initializeApp(conf);
        const db = firebase.database();
        let lastC = -1;

        // โหลดข้อความและรูปภาพ
        db.ref('global_chat').limitToLast(20).on('child_added', (s) => {{
            const d = s.val();
            const isMe = d.user === "{st.session_state.user}";
            const div = document.createElement('div');
            div.style.alignSelf = isMe ? 'flex-end' : 'flex-start';
            
            let content = d.text ? `<div style="background:${{isMe ? '{theme}11':'#111'}}; border:1px solid ${{isMe ? '{theme}':'#333'}}; padding:8px 12px; border-radius:8px; color:#fff; font-size:13px;">${{d.text}}</div>` : "";
            if(d.img) content += `<img src="data:image/png;base64,${{d.img}}" style="max-width:200px; border-radius:8px; margin-top:5px; border:1px solid {theme}44;">`;
            
            div.innerHTML = `<div style="font-size:9px; color:#666; margin-bottom:2px; text-align:${{isMe?'right':'left'}};">${{d.user}}</div>` + content;
            document.getElementById('msgs').appendChild(div);
            document.getElementById('chat-box').scrollTop = 99999;
        }});

        // เสียงและไฟแดง
        db.ref('chat_notifications/unread_count').on('value', (s) => {{
            const c = s.val() || 0;
            const n = document.getElementById('notif');
            n.innerText = c + " NEW SIGNAL";
            if(c > 0) {{
                n.style.background = "#FF0000"; n.style.boxShadow = "0 0 10px #FF0000";
                if(lastC !== -1 && c > lastC) document.getElementById('beep').play().catch(()=>{{}});
            }} else {{ n.style.background = "#444"; n.style.boxShadow="none"; }}
            lastC = c;
        }});
        
        // ปลดล็อคเสียงเมื่อคลิก
        document.addEventListener('click', () => document.getElementById('beep').load());
    </script>
    """
    components.html(chat_html, height=480)

    # --- ส่วนส่งข้อความ & รูปภาพ (Python) ---
    with st.container():
        c_text, c_img, c_btn = st.columns([3, 1, 1])
        with c_text:
            msg = st.text_input("MESSAGE", label_visibility="collapsed", placeholder="พิมพ์ข้อความที่นี่...")
        with c_img:
            img_file = st.file_uploader("IMG", type=['png','jpg','jpeg'], label_visibility="collapsed")
        with c_btn:
            if st.button("SEND ⚡", use_container_width=True):
                payload = {'user': st.session_state.user, 'ts': datetime.now().isoformat()}
                if msg: payload['text'] = msg
                if img_file: payload['img'] = image_to_base64(img_file)
                
                if msg or img_file:
                    db.reference('global_chat').push(payload)
                    cnt = db.reference('chat_notifications/unread_count').get() or 0
                    db.reference('chat_notifications').set(cnt + 1)
                    st.rerun()

if st.button("CLEAR NOTIF"):
    db.reference('chat_notifications').set(0)
    st.rerun()
