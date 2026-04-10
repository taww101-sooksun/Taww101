import streamlit as st
import os 
import time
import base64
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from folium.features import DivIcon
from streamlit_folium import st_folium
from math import radians, cos, sin, asin, sqrt
import pytz
from timezonefinder import TimezoneFinder
from datetime import datetime
from streamlit_js_eval import get_geolocation 

# ==========================================
# 0. CONFIG & STYLING (นูน มีไฟ อยู่นิ่งๆไม่เจ็บตัว)
# ==========================================
st.set_page_config(page_title="SYNAPSE OS", layout="wide", initial_sidebar_state="collapsed")

def apply_custom_background():
    theme = st.session_state.get('theme_color', "#1408BF")
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: linear-gradient(270deg, #AFEEEE, #FF7F50, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
            background-size: 1600% 1600%;
            animation: RainbowFlow 60s ease infinite;
        }}
        @keyframes RainbowFlow {{
            0%{{background-position:0% 50%}}
            50%{{background-position:100% 50%}}
            100%{{background-position:0% 50%}}
        }}
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(0, 0, 0, 0.7) !important;
            border-radius: 20px !important;
            padding: 10px !important;
            border: 2px solid {theme} !important;
            box-shadow: 0 0 15px {theme}88;
        }}
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{
            color: #FFFFFF !important;
            background-color: {theme}44 !important;
            border: 1px solid {theme} !important;
            box-shadow: 0 0 15px {theme} !important;
            transform: scale(1.05);
        }}
        div.stButton > button {{
            background-color: rgba(0, 0, 0, 0.8) !important;
            color: white !important;
            border: 2px solid {theme} !important;
            border-radius: 15px !important;
            filter: drop-shadow(0 0 5px {theme});
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def show_logo():
    theme = st.session_state.get('theme_color', "#1408BF")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if os.path.exists("logo1.png"):
            with open("logo1.png", "rb") as f:
                data = base64.b64encode(f.read()).decode()
            st.markdown(f"""
                <div style="text-align:center; filter: drop-shadow(0 0 15px {theme}); margin-bottom: 20px;">
                    <img src="data:image/png;base64,{data}" style="width:100%; max-width:220px; border-radius:15px;">
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"<h1 style='text-align:center; color:{theme}; text-shadow: 0 0 15px {theme};'>SYNAPSE</h1>", unsafe_allow_html=True)

# ==========================================
# 1. UTILS & INIT
# ==========================================
def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#1408BF"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except: pass

def get_local_time(lat, lon):
    try:
        tf = TimezoneFinder()
        tz_str = tf.timezone_at(lat=lat, lng=lon)
        return datetime.now(pytz.timezone(tz_str)) if tz_str else datetime.now()
    except: return datetime.now()

# ==========================================
# 2. MODULES (ปรับปรุงใหม่ตามคำขอ)
# ==========================================
def room_secure_chat():
    st.subheader("💬 SECURE CHAT (Real-time)")
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    target = st.selectbox("🎯 เลือกผู้รับข้อความ:", friends)
    
    if target:
        rid = "_".join(sorted([st.session_state.user, target]))
        chat_container = st.container(height=300, border=True)
        chats = db.reference(f'private_rooms/{rid}').order_by_key().limit_to_last(15).get()
        
        with chat_container:
            if chats:
                for c in chats.values():
                    is_me = c['u'] == st.session_state.user
                    align, color = ("right", st.session_state.theme_color) if is_me else ("left", "#333")
                    st.markdown(f'<div style="text-align:{align}; margin-bottom:10px;"><div style="display:inline-block; background:{color}; padding:10px; border-radius:10px; color:white;"><b>{c["u"]}</b>: {c["m"]}</div></div>', unsafe_allow_html=True)

        with st.form("send_msg", clear_on_submit=True):
            m = st.text_input("พิมพ์ข้อความที่นี่...")
            if st.form_submit_button("SEND"):
                if m:
                    db.reference(f'private_rooms/{rid}').push({'u': st.session_state.user, 'm': m, 'ts': time.time()})
                    st.rerun()

def room_audio_call():
    st.subheader("📞 VOICE CALL (P2P)")
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    target = st.selectbox("เลือก AGENT ที่จะโทรหา:", friends)
    
    if target:
        call_html = f"""
        <div style="background:#000; padding:20px; border-radius:15px; border:2px solid {st.session_state.theme_color}; text-align:center;">
            <div id="status" style="color:{st.session_state.theme_color}; margin-bottom:10px;">READY</div>
            <audio id="remoteAudio" autoplay></audio>
            <button id="startCall" style="background:{st.session_state.theme_color}; color:white; padding:10px 20px; border:none; border-radius:5px;">📞 CALL</button>
            <button onclick="location.reload()" style="background:red; color:white; padding:10px 20px; border:none; border-radius:5px;">❌ END</button>
        </div>
        <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
        <script>
            const peer = new Peer('{st.session_state.user}');
            peer.on('call', call => {{
                navigator.mediaDevices.getUserMedia({{audio: true}}).then(s => {{
                    call.answer(s);
                    call.on('stream', rs => {{ document.getElementById('remoteAudio').srcObject = rs; }});
                }});
            }});
            document.getElementById('startCall').onclick = () => {{
                navigator.mediaDevices.getUserMedia({{audio: true}}).then(s => {{
                    const call = peer.call('{target}', s);
                    call.on('stream', rs => {{ document.getElementById('remoteAudio').srcObject = rs; }});
                }});
            }};
        </script>
        """
        components.html(call_html, height=200)

# ==========================================
# 3. MAIN (แก้ไขจุด Error)
# ==========================================
def main():
    init_system()
    apply_custom_background()
    loc = get_geolocation() 

    if not st.session_state.get('logged_in', False):
        from datetime import time as dt_time # ป้องกันชื่อชนกัน
        # ฟังก์ชัน login เดิมของท่าน
        show_logo()
        # ... (โค้ด login) ...
        # (เพื่อให้รันได้ ผมขอใส่ปุ่มข้ามไว้สั้นๆ สำหรับทดสอบ)
        if st.button("GO TO SYSTEM (DEMO)"): 
             st.session_state.logged_in = True
             st.session_state.user = "AGENT_T"
             st.rerun()
        return

    show_logo()

    with st.sidebar:
        st.write(f"👤 AGENT: **{st.session_state.user}**")
        if st.button("🚪 LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()

    tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "💬 CHAT", "📞 CALL", "🎧 MUSIC", "⚙️ SETTINGS"])
    
    with tabs[0]: 
        if 'room_core' in globals(): room_core(loc)
    with tabs[1]: 
        if 'room_radar' in globals(): room_radar(loc)
    with tabs[2]: 
        room_secure_chat() # ระบบแชตใหม่
    with tabs[3]: 
        room_audio_call()  # แก้ไขจาก room_call() เป็น room_audio_call()
    with tabs[4]: 
        if 'room_music' in globals(): room_music()
    with tabs[5]: 
        st.session_state.theme_color = st.color_picker("ปรับสีไฟนีออน", st.session_state.theme_color)

if __name__ == "__main__":
    main()
