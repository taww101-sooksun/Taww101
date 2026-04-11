# ==============================================================================
# 📂 SYSTEM: SYNAPSE COMMAND CENTER (MASTER NEON EDITION)
# 📂 AGENT: TAWW101 | "อยู่นิ่งๆ ไม่เจ็บตัว"
# 📂 FEATURES: FULL NEON UI, REAL-TIME CHAT, P2P VOICE (PEERJS)
# ==============================================================================

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
from datetime import datetime, date
import math
import random
from streamlit_js_eval import get_geolocation 

# ==========================================
# 0. CONFIG & CSS STYLING (ตามแบบที่คุณชอบ)
# ==========================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide", initial_sidebar_state="collapsed")

def apply_custom_background():
    theme = st.session_state.get('theme_color', "#1408BF")
    st.markdown(f"""
        <style>
        /* พื้นหลังแอป */
        .stApp {{ background-color: #000000; color: white; }}
        
        /* ส่วนของ Tabs - ขอบหนา ไฟฟุ้ง */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(0, 0, 0, 0.9) !important;
            border-radius: 25px !important;
            padding: 12px !important;
            border: 6px solid {theme} !important;
            box-shadow: 0 0 40px {theme};
            margin: 15px 0px !important;
        }}
        
        /* ปรับสีตัวหนังสือใน Tab */
        .stTabs [data-baseweb="tab"] {{ color: white !important; font-weight: bold; }}
        .stTabs [aria-selected="true"] {{ background-color: {theme}44 !important; }}

        /* ส่วนของปุ่ม - ขอบหนา ไฟนูน */
        div.stButton > button {{
            background: linear-gradient(145deg, #000, #222) !important;
            color: white !important;
            border: 5px solid {theme} !important;
            border-radius: 20px !important;
            filter: drop-shadow(0 0 15px {theme});
            transition: all 0.3s ease;
            width: 100%;
            height: 50px;
            font-weight: bold;
        }}
        div.stButton > button:hover {{ transform: scale(1.02); filter: drop-shadow(0 0 25px {theme}); }}

        /* กล่อง Logic - ขอบเขียวหนาแบบในรูป */
        .logic-box {{
            background: rgba(0, 10, 0, 0.95);
            border: 5px solid #00ff41;
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 0 30px rgba(0, 255, 65, 0.6);
            margin-bottom: 20px;
        }}
        
        /* ซ่อน Header/Footer ของ Streamlit */
        header, footer {{visibility: hidden !important;}}
        </style>
    """, unsafe_allow_html=True)

def show_logo():
    theme = st.session_state.get('theme_color', "#1408BF")
    if os.path.exists("logo1.png"):
        with open("logo1.png", "rb") as f:
            data = base64.b64encode(f.read()).decode()
        st.markdown(f'<div style="text-align:center; filter: drop-shadow(0 0 15px {theme}); margin-bottom: 25px;"><img src="data:image/png;base64,{data}" style="width:100%; max-width:240px; border-radius:20px;"></div>', unsafe_allow_html=True)
    else:
        st.markdown(f"<h1 style='text-align:center; color:{theme}; text-shadow: 0 0 15px {theme};'>SYNAPSE OS</h1>", unsafe_allow_html=True)

# ==========================================
# 1. UTILS & LOGIC (Reality & Time)
# ==========================================
def get_reality_logic(dt):
    ref_date = date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    if pos <= 14.765:
        m_num = int(pos) + 1
        res = math.sqrt((day_val**2) + (m_num**2))
        phase = f"ขึ้น {m_num} ค่ำ"
    else:
        m_num = int(pos - 14.765) + 1
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        phase = f"แรม {m_num} ค่ำ"
    return {"res": round(res, 4), "phase": phase}

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

# ==========================================
# 2. CORE MODULES (แชต และ โทร)
# ==========================================

def room_secure_chat():
    st.subheader("💬 SECURE MESSENGER")
    users_data = db.reference('users').get()
    friends = [u for u in users_data.keys() if u != st.session_state.user] if users_data else []
    target = st.selectbox("🎯 SELECT TARGET AGENT:", friends)
    
    if target:
        rid = "_".join(sorted([st.session_state.user, target]))
        # กล่องแชทแบบ Scroll
        st.markdown('<div class="logic-box" style="height:350px; overflow-y:auto; border-color:#555;">', unsafe_allow_html=True)
        chats = db.reference(f'private_rooms/{rid}').order_by_key().limit_to_last(20).get()
        if chats:
            for c in chats.values():
                is_me = c['u'] == st.session_state.user
                color = st.session_state.theme_color if is_me else "#333"
                align = "right" if is_me else "left"
                st.markdown(f'<div style="text-align:{align}; margin-bottom:10px;"><div style="display:inline-block; background:{color}; padding:8px 15px; border-radius:15px;"><b>{c["u"]}:</b> {c["m"]}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        with st.form("send_msg", clear_on_submit=True):
            m_input = st.text_input("Message...")
            if st.form_submit_button("SEND DATA"):
                if m_input:
                    db.reference(f'private_rooms/{rid}').push({'u': st.session_state.user, 'm': m_input, 'ts': time.time()})
                    st.rerun()

def room_audio_call():
    theme = st.session_state.theme_color
    st.markdown(f'<div class="logic-box" style="border-color:{theme}; text-align:center;"><h2>📞 ENCRYPTED VOICE</h2></div>', unsafe_allow_html=True)
    
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    target = st.selectbox("🎯 TARGET ID:", friends, key="call_target")

    # PeerJS Bridge
    call_html = f"""
    <div style="background:#000; padding:20px; border:3px solid {theme}; border-radius:15px; text-align:center;">
        <h4 id="status" style="color:#00ff41;">📡 SYSTEM READY</h4>
        <audio id="remoteAudio" autoplay></audio>
        <audio id="ringtone" loop src="https://www.soundjay.com/phone/phone-calling-1.mp3"></audio>
        <div style="margin:20px 0;">
            <button id="callBtn" style="padding:15px; background:{theme}; color:white; border:none; border-radius:10px; cursor:pointer; width:45%;">📞 CALL</button>
            <button id="hangBtn" style="padding:15px; background:#f44; color:white; border:none; border-radius:10px; cursor:pointer; width:45%;">❌ END</button>
        </div>
    </div>
    <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
    <script>
        const peer = new Peer('{st.session_state.user}');
        let currentCall = null;
        const ring = document.getElementById('ringtone');

        peer.on('call', (call) => {{
            ring.play();
            if(confirm("🚨 Incoming Call from Agent! Accept?")) {{
                ring.pause();
                navigator.mediaDevices.getUserMedia({{audio:true}}).then(stream => {{
                    call.answer(stream);
                    call.on('stream', rem => {{ document.getElementById('remoteAudio').srcObject = rem; }});
                    currentCall = call;
                    document.getElementById('status').innerText = "🎙️ IN CONVERSATION";
                }});
            }} else {{ ring.pause(); call.close(); }}
        }});

        document.getElementById('callBtn').onclick = () => {{
            const tid = "{target}";
            navigator.mediaDevices.getUserMedia({{audio:true}}).then(stream => {{
                const call = peer.call(tid, stream);
                document.getElementById('status').innerText = "🛰️ CALLING...";
                call.on('stream', rem => {{ document.getElementById('remoteAudio').srcObject = rem; }});
                currentCall = call;
            }});
        }};

        document.getElementById('hangBtn').onclick = () => {{ location.reload(); }};
    </script>
    """
    components.html(call_html, height=300)

def room_reality_scanner():
    st.subheader("🧬 Reality Extractor")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="logic-box">', unsafe_allow_html=True)
        st.write("### 🔍 สแกนส่วนบุคคล")
        dob = st.date_input("เลือกวันเกิด", value=date(1970, 1, 1), min_value=date(1900,1,1))
        res = get_reality_logic(dob)
        st.metric("REALITY CODE", res['res'])
        st.info(f"สภาวะ: {res['phase']}")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="logic-box" style="border-color:#1408BF;">', unsafe_allow_html=True)
        st.write("### 🛰️ ตรวจสอบรหัสคู่ขนาน")
        u1 = st.date_input("AGENT 1", value=date(1996, 8, 17))
        u2 = st.date_input("AGENT 2", value=date.today())
        if st.button("COMPUTE GAP"):
            r1, r2 = get_reality_logic(u1)['res'], get_reality_logic(u2)['res']
            gap = abs(r1-r2)
            st.subheader(f"GAP: {gap:.4f}")
            if gap <= 1.5: st.success("MATCH: OPTIMAL")
            else: st.warning("MATCH: STABLE")
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 3. MAIN CONTROLLER
# ==========================================
def main():
    init_system()
    apply_custom_background()
    loc = get_geolocation()

    if not st.session_state.logged_in:
        show_logo()
        c1, c2, c3 = st.columns([1, 1.5, 1])
        with c2:
            st.markdown('<div class="logic-box" style="border-color:#1408BF;">', unsafe_allow_html=True)
            uid = st.text_input("AGENT ID")
            upw = st.text_input("PASSWORD", type="password")
            if st.button("ACCESS SYSTEM"):
                user = db.reference(f'users/{uid}').get()
                if user and user['pw'] == upw:
                    st.session_state.user = uid
                    st.session_state.logged_in = True
                    st.rerun()
                else: st.error("DENIED")
            st.markdown('</div>', unsafe_allow_html=True)
        return

    show_logo()
    with st.sidebar:
        st.write(f"### 👤 {st.session_state.user}")
        st.session_state.theme_color = st.color_picker("THEME", st.session_state.theme_color)
        if st.button("LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()

    tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "🧬 SCANNER", "💬 CHAT", "📞 VOICE", "🎧 MUSIC"])
    with tabs[0]: 
        st.subheader("🏠 DASHBOARD")
        room_reality_scanner() # หรือใส่ Dashborad ตามใจชอบ
    with tabs[2]: room_reality_scanner()
    with tabs[3]: room_secure_chat()
    with tabs[4]: room_audio_call()
    with tabs[5]:
        files = [f for f in os.listdir('.') if f.endswith(".mp3")]
        if files:
            st.audio(files[st.session_state.song_index])

if __name__ == "__main__":
    main()
