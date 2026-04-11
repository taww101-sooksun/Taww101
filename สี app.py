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
# 0. CONFIG & NEON CSS (ขอบหนา ไฟฟุ้ง ตามสั่ง)
# ==========================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide", initial_sidebar_state="collapsed")

def apply_custom_background():
    theme = st.session_state.get('theme_color', "#1408BF")
    st.markdown(f"""
        <style>
        .stApp {{ background-color: #000000; color: white; }}
        
        /* Tabs - ขอบหนา ไฟฟุ้ง */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(0, 0, 0, 0.9) !important;
            border-radius: 25px !important;
            padding: 12px !important;
            border: 6px solid {theme} !important;
            box-shadow: 0 0 40px {theme};
            margin: 15px 0px !important;
        }}
        .stTabs [data-baseweb="tab"] {{ color: white !important; font-weight: bold; }}
        .stTabs [aria-selected="true"] {{ background-color: {theme}44 !important; }}

        /* ปุ่ม - ขอบหนา ไฟนูน */
        div.stButton > button {{
            background: linear-gradient(145deg, #000, #222) !important;
            color: white !important;
            border: 5px solid {theme} !important;
            border-radius: 20px !important;
            filter: drop-shadow(0 0 15px {theme});
            transition: all 0.3s ease;
            width: 100%; height: 50px; font-weight: bold;
        }}
        div.stButton > button:hover {{ transform: scale(1.02); filter: drop-shadow(0 0 25px {theme}); }}

        /* Logic Box - ขอบเขียวหนา Matrix */
        .logic-box {{
            background: rgba(0, 10, 0, 0.95);
            border: 5px solid #00ff41;
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 0 30px rgba(0, 255, 65, 0.6);
            margin-bottom: 20px;
        }}
        header, footer {{visibility: hidden !important;}}
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 1. UTILS (คำนวณรหัสคู่ขนาน)
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
# 2. MODULES (แก้ไข Duplicate ID ด้วย Unique Key)
# ==========================================

def room_reality_scanner(suffix="main"):
    """ใส่ suffix เพื่อป้องกัน Duplicate ID"""
    st.subheader("🧬 Reality Extractor & Code Scanner")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="logic-box">', unsafe_allow_html=True)
        st.write("### 🔍 สแกนส่วนบุคคล")
        # ใส่ key เฉพาะตัวเพื่อแก้ Error
        dob = st.date_input("เลือกวันเกิด", value=date(1970, 1, 1), min_value=date(1900,1,1), key=f"dob_{suffix}")
        res = get_reality_logic(dob)
        st.metric("REALITY CODE", res['res'])
        st.info(f"สภาวะ: {res['phase']}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="logic-box" style="border-color:#1408BF;">', unsafe_allow_html=True)
        st.write("### 🛰️ ตรวจสอบรหัสคู่ขนาน")
        u1 = st.date_input("AGENT 1", value=date(1996, 8, 17), key=f"ag1_{suffix}")
        u2 = st.date_input("AGENT 2", value=date.today(), key=f"ag2_{suffix}")
        if st.button("COMPUTE GAP", key=f"btn_{suffix}"):
            r1, r2 = get_reality_logic(u1)['res'], get_reality_logic(u2)['res']
            gap = abs(r1-r2)
            st.write(f"CODE 1: `{r1}` | CODE 2: `{r2}`")
            st.subheader(f"GAP: {gap:.4f}")
            if gap <= 1.5: st.success("MATCH: OPTIMAL")
            else: st.warning("MATCH: STABLE")
        st.markdown('</div>', unsafe_allow_html=True)

def room_audio_call():
    theme = st.session_state.theme_color
    st.markdown(f'<div class="logic-box" style="border-color:{theme}; text-align:center;"><h2>📞 SYNAPSE VOICE</h2></div>', unsafe_allow_html=True)
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    target = st.selectbox("🎯 TARGET ID:", friends, key="call_target")

    call_html = f"""
    <div style="background:#000; padding:20px; border:3px solid {theme}; border-radius:15px; text-align:center;">
        <h4 id="status" style="color:#00ff41;">📡 พร้อมเชื่อมต่อ...</h4>
        <audio id="remoteAudio" autoplay></audio>
        <div style="margin:20px 0;">
            <button id="callBtn" style="padding:15px; background:{theme}; color:white; border:none; border-radius:10px; cursor:pointer; width:45%;">📞 CALL</button>
            <button id="hangBtn" style="padding:15px; background:#f44; color:white; border:none; border-radius:10px; cursor:pointer; width:45%;">❌ END</button>
        </div>
    </div>
    <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
    <script>
        const peer = new Peer('{st.session_state.user}');
        let currentCall = null;
        peer.on('call', (call) => {{
            if(confirm("🚨 Incoming Call! Accept?")) {{
                navigator.mediaDevices.getUserMedia({{audio:true}}).then(stream => {{
                    call.answer(stream);
                    call.on('stream', rem => {{ document.getElementById('remoteAudio').srcObject = rem; }});
                    currentCall = call;
                    document.getElementById('status').innerText = "🎙️ ON CALL";
                }});
            }}
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
        document.getElementById('btn-hangup').onclick = () => {{ location.reload(); }};
    </script>
    """
    components.html(call_html, height=280)

# ==========================================
# 3. MAIN
# ==========================================
def main():
    init_system()
    apply_custom_background()
    loc = get_geolocation()

    if not st.session_state.logged_in:
        # ส่วน Login (ข้ามไปก่อน)
        st.session_state.logged_in = True # Test
        st.session_state.user = "Ta103"
        st.rerun()

    with st.sidebar:
        st.write(f"### 👤 {st.session_state.user}")
        st.session_state.theme_color = st.color_picker("THEME", st.session_state.theme_color)
        if st.button("LOGOUT"): st.session_state.logged_in = False; st.rerun()

    tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "🧬 SCANNER", "💬 CHAT", "📞 VOICE", "🎧 MUSIC"])
    
    with tabs[0]: 
        st.subheader("🏠 DASHBOARD")
        # ใช้ suffix="dash" เพื่อไม่ให้ซ้ำกับหน้า Scanner
        room_reality_scanner(suffix="dash") 
        
    with tabs[2]: 
        # ใช้ suffix="scanner" ป้องกัน Duplicate ID
        room_reality_scanner(suffix="scanner") 

if __name__ == "__main__":
    main()
