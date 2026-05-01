import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import base64
import os

# --- 0. CONFIG & CSS HIDE STREAMLIT ---
st.set_page_config(page_title="SYNAPSE PRO", layout="wide")

def hide_st_ui():
    st.markdown("""
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp { top: -60px; }
            body { background-color: #000; color: #fff; }
        </style>
    """, unsafe_allow_html=True)

hide_st_ui()

def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

# --- 1. FIREBASE CONNECTION ---
if not firebase_admin._apps:
    fb_creds = dict(st.secrets["firebase_credentials"])
    fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate(fb_creds)
    firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})

# --- 2. SESSION STATE & LOGO/SOUND DATA ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None

logo_base64 = get_base64("logo1.png")
audio_data = get_base64("notification.mp3")
theme_color = "#39FF14"

# --- 3. HEADER: LOGO DANCING & SLOGAN WINKING ---
header_html = f"""
<style>
    @keyframes dance {{
        0% {{ transform: translate(0, 0) rotate(0deg); }}
        25% {{ transform: translate(2px, -2px) rotate(2deg); }}
        50% {{ transform: translate(-2px, 2px) rotate(-2deg); }}
        75% {{ transform: translate(1px, -1px) rotate(1deg); }}
        100% {{ transform: translate(0, 0) rotate(0deg); }}
    }}
    @keyframes wink {{
        0%, 100% {{ opacity: 1; color: {theme_color}; text-shadow: 0 0 10px {theme_color}; }}
        50% {{ opacity: 0.3; color: #fff; }}
    }}
    .logo-img {{ width: 100px; animation: dance 0.6s infinite; }}
    .slogan-txt {{ 
        font-family: sans-serif; font-weight: bold; font-size: 18px; 
        margin-left: 15px; animation: wink 1.2s infinite; 
    }}
</style>
<div style="display: flex; align-items: center; justify-content: center; padding: 20px 0;">
    <img src="data:image/png;base64,{logo_base64}" class="logo-img">
    <span class="slogan-txt">SYNAPSE อยู่นิ้งๆไม่เจ็บตัว</span>
</div>
"""
components.html(header_html, height=140)

# --- 4. LOGIN / REGISTER PAGE ---
if not st.session_state.logged_in:
    st.markdown(f"<h3 style='text-align:center; color:{theme_color};'>IDENTITY VERIFICATION</h3>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 LOGIN", "📝 REGISTER"])
    
    with tab1:
        with st.form("login_form"):
            u_id = st.text_input("AGENT ID")
            u_pw = st.text_input("PASSWORD", type="password")
            if st.form_submit_button("ACCESS ⚡", use_container_width=True):
                user_data = db.reference(f'users/{u_id}').get()
                if user_data and user_data.get('password') == u_pw:
                    st.session_state.logged_in = True
                    st.session_state.user = u_id
                    st.rerun()
                else:
                    st.error("รหัสไม่ถูกต้อง หรือไม่มี Agent ID นี้")
    
    with tab2:
        with st.form("reg_form"):
            new_u = st.text_input("NEW AGENT ID")
            new_p = st.text_input("NEW PASSWORD", type="password")
            if st.form_submit_button("CREATE IDENTITY"):
                if new_u and new_p:
                    db.reference(f'users/{new_u}').set({'password': new_p, 'created_at': datetime.now().isoformat()})
                    st.success("ลงทะเบียนสำเร็จ! กรุณาไปที่หน้า Login")
    st.stop()

# --- 5. CHAT MAIN INTERFACE ---
st.markdown(f"<div style='text-align:right; color:{theme_color}; font-size:12px;'>AGENT: {st.session_state.user}</div>", unsafe_allow_html=True)

chat_display_html = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    #chat-screen {{
        background: rgba(0,0,0,0.9); border: 2px solid {theme_color}; border-radius: 10px;
        height: 450px; overflow-y: auto; padding: 15px; display: flex; flex-direction: column;
    }}
    .bubble {{ padding: 10px; border-radius: 8px; margin: 5px 0; max-width: 80%; color: #fff; font-family: 'Orbitron', sans-serif; font-size: 13px; }}
    .me {{ background: {theme_color}22; border-right: 3px solid {theme_color}; align-self: flex-end; }}
    .others {{ background: #222; border-left: 3px solid #777; align-self: flex-start; }}
    .notif-btn {{ background: #444; color: white; padding: 3px 10px; border-radius: 5px; font-size: 11px; }}
    .alert-red {{ background: #F00 !important; box-shadow: 0 0 15px #F00; }}
</style>

<div id="chat-screen">
    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
        <span style="color:{theme_color}; font-size:10px;">SYSTEM_ACTIVE</span>
        <span id="notif-box" class="notif-btn">0 NEW</span>
    </div>
    <div id="msg-area" style="display:flex; flex-direction:column;"></div>
</div>

<audio id="notif-sound" src="data:audio/mp3;base64,{audio_data}" preload="auto"></audio>

<script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
<script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
<script>
    const fb_conf = {{ databaseURL: "{st.secrets['firebase_db_url']}" }};
    if(!firebase.apps.length) firebase.initializeApp(fb_conf);
    const database = firebase.database();
    let lastUnreadCount = -1;
    const beepSound = document.getElementById('notif-sound');

    // ปลดล็อกเสียงเมื่อคลิก
    document.addEventListener('click', () => {{
        beepSound.play().then(() => {{ beepSound.pause(); beepSound.currentTime = 0; }});
    }}, {{once: true}});

    // แสดงข้อความแชท
    database.ref('global_chat').limitToLast(20).on('child_added', (snap) => {{
        const msg = snap.val();
        const isMe = msg.user === "{st.session_state.user}";
        const area = document.getElementById('msg-area');
        const div = document.createElement('div');
        div.className = "bubble " + (isMe ? "me" : "others");
        
        let content = `<div style="font-size:9px; color:#999;">${{msg.user}}</div>`;
        if(msg.text) content += `<div>${{msg.text}}</div>`;
        if(msg.img) content += `<img src="data:image/png;base64,${{msg.img}}" style="max-width:100%; border-radius:5px; margin-top:5px;">`;
        
        div.innerHTML = content;
        area.appendChild(div);
        document.getElementById('chat-screen').scrollTop = 999999;
    }});

    // แจ้งเตือนไฟแดงและเสียง
    database.ref('chat_notifications/unread_count').on('value', (snap) => {{
        const val = snap.val() || 0;
        const box = document.getElementById('notif-box');
        box.innerText = val + " NEW SIGNAL";
        if(val > 0) {{
            box.classList.add('alert-red');
            if(lastUnreadCount !== -1 && val > lastUnreadCount) beepSound.play();
        }} else {{
            box.classList.remove('alert-red');
        }}
        lastUnreadCount = val;
    }});
</script>
"""
components.html(chat_display_html, height=500)

# --- 6. MESSAGE CONTROLS ---
with st.container():
    c1, c2, c3 = st.columns([3, 1, 1])
    with c1:
        m_txt = st.text_input("MESSAGE", placeholder="ส่งข้อความ...", label_visibility="collapsed")
    with c2:
        m_img = st.file_uploader("IMG", type=['png','jpg','jpeg'], label_visibility="collapsed")
    with c3:
        if st.button("SEND ⚡", use_container_width=True):
            if m_txt or m_img:
                payload = {'user': st.session_state.user, 'ts': datetime.now().isoformat()}
                if m_txt: payload['text'] = m_txt
                if m_img: payload['img'] = base64.b64encode(m_img.read()).decode()
                
                db.reference('global_chat').push(payload)
                
                # อัปเดตตัวเลขแจ้งเตือน (ไฟแดงจะขึ้นที่เครื่องคนอื่น)
                cur_unread = db.reference('chat_notifications/unread_count').get() or 0
                db.reference('chat_notifications').set(cur_unread + 1)
                st.rerun()

if st.button("ล้างการแจ้งเตือน"):
    db.reference('chat_notifications').set(0)
    st.rerun()

if st.button("LOGOUT"):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()
