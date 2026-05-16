import streamlit as st
import streamlit.components.v1 as components
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
import firebase_admin
from firebase_admin import credentials, db
import math
import time
import base64
import os
from datetime import datetime, date

# =========================================================
# 1. CONFIG & UI INITIALIZATION
# =========================================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")

def hide_st_ui():
    st.markdown("""
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp { top: -60px; background-color: #0e1117; }
            
            .stTabs [data-baseweb="tab-list"] { gap: 10px; }
            .stTabs [data-baseweb="tab"] {
                background-color: #111; border: 1px solid #333;
                border-radius: 5px; padding: 10px 20px; color: #888;
            }
            .stTabs [aria-selected="true"] {
                background-color: #39FF1422 !important;
                border-color: #39FF14 !important; color: #39FF14 !important;
            }
            @keyframes neon-glow {
                0% { filter: drop-shadow(0 0 5px #39FF14) drop-shadow(0 0 10px #39FF14); }
                50% { filter: drop-shadow(0 0 15px #39FF14) drop-shadow(0 0 25px #39FF14); }
                100% { filter: drop-shadow(0 0 5px #39FF14) drop-shadow(0 0 10px #39FF14); }
            }
            .neon-logo-main {
                width: 100px;
                display: block;
                margin: 0 auto 10px auto;
                animation: neon-glow 2s infinite ease-in-out;
            }
        </style>
    """, unsafe_allow_html=True)

hide_st_ui()

def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

logo_base64 = get_base64("logo1.png")
audio_data = get_base64("notification.mp3")
theme_color = "#39FF14"

# =========================================================
# 2. FIREBASE CONNECTION
# =========================================================
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_credentials"])
        fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
    except Exception as e:
        st.error(f"การเชื่อมต่อฐานข้อมูลผิดพลาด: {e}")

# =========================================================
# 3. SESSION STATE CONFIGURATION
# =========================================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None
if 'user_lat' not in st.session_state: st.session_state.user_lat = None
if 'user_lon' not in st.session_state: st.session_state.user_lon = None

# =========================================================
# 4. HEADER LOGO & SLOGAN WINKING
# =========================================================
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
        50% {{ opacity: 0.2; color: #fff; }}
    }}
    .logo-container {{ display: flex; align-items: center; justify-content: center; padding: 10px 0; }}
    .logo-img {{ width: 80px; height: 80px; animation: dance 0.6s infinite; object-fit: contain; }}
    .slogan-txt {{ 
        font-family: sans-serif; font-weight: bold; font-size: 18px; 
        margin-left: 15px; animation: wink 1.5s infinite; 
    }}
</style>
<div class="logo-container">
    {f'<img src="data:image/png;base64,{logo_base64}" class="logo-img">' if logo_base64 else ''}
    <span class="slogan-txt">SYNAPSE อยู่นิ่งๆไม่เจ็บตัว</span>
</div>
"""
components.html(header_html, height=110)

# =========================================================
# 5. AUTHENTICATION SYSTEM (LOGIN / REGISTER)
# =========================================================
if not st.session_state.logged_in:
    st.markdown(f"<h3 style='text-align:center; color:{theme_color};'>🔒 SYSTEM AUTHENTICATION</h3>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 เข้าสู่ระบบ", "📝 ลงทะเบียนบัญชีใหม่"])
    
    with tab1:
        with st.form("login_form"):
            u_id = st.text_input("ชื่อผู้ใช้ (AGENT ID)")
            u_pw = st.text_input("รหัสผ่าน", type="password")
            if st.form_submit_button("เข้าสู่ระบบ ⚡", use_container_width=True):
                user_data = db.reference(f'users/{u_id}').get()
                if user_data and user_data.get('password') == u_pw:
                    st.session_state.logged_in = True
                    st.session_state.user = u_id
                    st.rerun()
                else:
                    st.error("ข้อมูลไม่ถูกต้อง")
    
    with tab2:
        with st.form("reg_form"):
            new_u = st.text_input("ตั้งชื่อผู้ใช้ใหม่")
            new_p = st.text_input("ตั้งรหัสผ่าน", type="password")
            if st.form_submit_button("สร้างบัญชี AGENT"):
                if new_u and new_p:
                    db.reference(f'users/{new_u}').set({'password': new_p, 'created_at': datetime.now().isoformat()})
                    st.success("ลงทะเบียนสำเร็จ! กรุณาสลับไปหน้าเข้าสู่ระบบ")
    st.stop()

st.markdown(f"<div style='text-align:right; color:{theme_color}; font-size:12px; padding-right:10px;'>📡 AGENT OUTPOST: {st.session_state.user}</div>", unsafe_allow_html=True)


# =========================================================
# 7. MODULE LOGIC APPLICATIONS
# =========================================================

# --- 7.1 ระบบแชทเรียลไทม์ ---
if menu_choice == "💬 GLOBAL CHATROOM":
    st.markdown(f"<h3 style='color:{theme_color};'>💬 GLOBAL CHATROOM</h3>", unsafe_allow_html=True)
    
    # ดันข้อความ f""" ให้ติดชอบซ้ายของระยะย่อหน้าตามปกติ
    chat_display_html = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    #chat-screen {{
        background: rgba(0,0,0,0.95); border: 2px solid {theme_color}; border-radius: 12px;
        height: 400px; overflow-y: auto; padding: 15px; display: flex; flex-direction: column;
        box-shadow: inset 0 0 15px {theme_color}33;
    }}
    .bubble {{ padding: 10px 15px; border-radius: 10px; margin: 8px 0; max-width: 85%; color: #fff; font-family: 'Orbitron', sans-serif; font-size: 14px; line-height: 1.4; }}
    .me {{ background: {theme_color}22; border-right: 4px solid {theme_color}; align-self: flex-end; }}
    .others {{ background: #222; border-left: 4px solid #777; align-self: flex-start; }}
    .notif-box {{ background: #333; color: white; padding: 4px 12px; border-radius: 20px; font-size: 11px; transition: 0.3s; }}
    .alert-red {{ background: #F00 !important; box-shadow: 0 0 15px #F00; font-weight: bold; }}
</style>

<div id="chat-screen">
    <div style="display:flex; justify-content:space-between; margin-bottom:12px; border-bottom: 1px solid #333; padding-bottom: 5px;">
        <span style="color:{theme_color}; font-size:10px; letter-spacing: 2px;">📡 SYSTEM_ACTIVE</span>
        <span id="notif-box" class="notif-box">0 NEW SIGNAL</span>
    </div>
    <div id="msg-area" style="display:flex; flex-direction:column;"></div>
</div>

<audio id="notif-sound" preload="auto">
    <source src="data:audio/mp3;base64,{audio_data}" type="audio/mp3">
</audio>

<script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
<script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
<script>
    const fb_conf = {{ databaseURL: "{st.secrets['firebase_db_url']}" }};
    if(!firebase.apps.length) firebase.initializeApp(fb_conf);
    const database = firebase.database();
    let lastCount = -1;
    const beep = document.getElementById('notif-sound');

    function unlock() {{
        beep.play().then(() => {{ beep.pause(); beep.currentTime = 0; }});
        window.removeEventListener('click', unlock);
        window.removeEventListener('touchstart', unlock);
    }}
    window.addEventListener('click', unlock);
    window.addEventListener('touchstart', unlock);

    database.ref('global_chat').limitToLast(25).on('child_added', (snap) => {{
        const msg = snap.val();
        const area = document.getElementById('msg-area');
        const div = document.createElement('div');
        const isMe = msg.user === "{st.session_state.user}";
        div.className = "bubble " + (isMe ? "me" : "others");
        div.style.alignSelf = isMe ? 'flex-end' : 'flex-start';
        
        let html = `<div style="font-size:10px; color:#777; margin-bottom:5px;">${{msg.user}}</div>`;
        if(msg.text) html += `<div>${{msg.text}}</div>`;
        if(msg.img) html += `<img src="data:image/png;base64,${{msg.img}}" style="max-width:100%; border-radius:8px; margin-top:8px; border: 1px solid #444;">`;
        
        div.innerHTML = html;
        area.appendChild(div);
        document.getElementById('chat-screen').scrollTop = 999999;
    }});

    database.ref('chat_notifications/unread_count').on('value', (snap) => {{
        const val = snap.val() || 0;
        const box = document.getElementById('notif-box');
        box.innerText = val + " NEW SIGNAL";
        if(val > 0) {{
            box.classList.add('alert-red');
            if(lastCount !== -1 && val > lastCount) {{
                beep.currentTime = 0;
                beep.play().catch(() => {{}});
            }}
        }} else {{
            box.classList.remove('alert-red');
        }}
        lastCount = val;
    }});
</script>
"""
    components.html(chat_display_html, height=440)


    

# =========================================================
# 8. GLOBAL SYSTEM FOOTER
# =========================================================
st.markdown("<div style='text-align:center; color:#444; font-size:11px; margin-top:30px;'>อยู่นิ่งๆ ไม่เจ็บตัว | SYNAPSE SECURITY TERMINAL V.3</div>", unsafe_allow_html=True)
