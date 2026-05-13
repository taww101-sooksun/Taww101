import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import base64
import os
import time
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# --- 1. INITIAL CONFIG ---
st.set_page_config(page_title="SYNAPSE OMNI", layout="wide", initial_sidebar_state="collapsed")

def apply_synapse_theme():
    st.markdown("""
        <style>
            #MainMenu, footer, header {visibility: hidden;}
            .stApp { top: -60px; background-color: #000; }
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
            * { font-family: 'Orbitron', sans-serif !important; }
            .stTabs [data-baseweb="tab-list"] { gap: 10px; }
            .stTabs [aria-selected="true"] {
                border: 4px solid #39FF14 !important;
                box-shadow: 0 0 25px #39FF14;
                color: #39FF14 !important;
                background-color: #111 !important;
            }
            .chat-box { border: 3px solid #39FF14; border-radius: 15px; padding: 10px; background: rgba(0,0,0,0.8); margin-bottom: 10px; }
            .private-box { border: 3px solid #ff00de; border-radius: 15px; padding: 10px; background: rgba(0,0,0,0.8); }
        </style>
    """, unsafe_allow_html=True)

apply_synapse_theme()

# --- 2. CORE UTILITIES ---
def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

all_songs = sorted([f for f in os.listdir('.') if f.endswith('.mp3')])

if not firebase_admin._apps:
    fb_creds = dict(st.secrets["firebase_credentials"])
    fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate(fb_creds)
    firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})

# --- 3. STICKY LOGO ---
logo_b64 = get_base64("logo1.png")
st.markdown(f"""
    <div style="text-align:center; padding:10px;">
        <img src="data:image/png;base64,{logo_b64}" style="width:110px; filter: drop-shadow(0 0 15px #39FF14);">
        <h2 style="color:#39FF14; text-shadow: 0 0 10px #39FF14; margin:0;">SYNAPSE COMMAND</h2>
        <p style="color:#39FF14; font-size:10px; letter-spacing:2px;">อยู่นิ่งๆ ไม่เจ็บตัว</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. AUTH SYSTEM ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        auth_tab1, auth_tab2 = st.tabs(["🔐 LOGIN", "📝 REGISTER"])
        with auth_tab1:
            with st.form("l_form"):
                u = st.text_input("AGENT ID")
                p = st.text_input("PASSWORD", type="password")
                if st.form_submit_button("CONNECT", use_container_width=True):
                    res = db.reference(f'users/{u}').get()
                    if res and res.get('password') == p:
                        st.session_state.logged_in, st.session_state.user = True, u
                        st.rerun()
                    else: st.error("ID หรือรหัสผ่านไม่ถูกต้อง")
        with auth_tab2:
            with st.form("r_form"):
                new_u = st.text_input("NEW AGENT ID")
                new_p = st.text_input("NEW PASSWORD", type="password")
                confirm_p = st.text_input("CONFIRM PASSWORD", type="password")
                if st.form_submit_button("REGISTER", use_container_width=True):
                    if new_p != confirm_p: st.error("รหัสผ่านไม่ตรงกัน")
                    elif not new_u: st.warning("กรุณาใส่ ID")
                    else:
                        if db.reference(f'users/{new_u}').get(): st.error("ID นี้ถูกใช้ไปแล้ว")
                        else:
                            db.reference(f'users/{new_u}').set({'password': new_p})
                            st.success("ลงทะเบียนสำเร็จ! กรุณาไปที่หน้า LOGIN")
    st.stop()

# --- 5. GPS & DATA ---
loc = get_geolocation()
my_lat, my_lon = 13.756, 100.501
if loc:
    my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']
    db.reference(f'active_locations/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})

tab_r, tab_p, tab_m, tab_s = st.tabs(["🛰️ RADAR", "🔒 PRIVATE", "🎧 MIXER", "⚙️ SYSTEM"])

# --- RADAR & GLOBAL CHAT ---
with tab_r:
    m = folium.Map(location=[my_lat, my_lon], zoom_start=17, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')
    agents = db.reference('active_locations').get()
    if agents:
        for uid, d in agents.items():
            folium.Marker([d['lat'], d['lon']], popup=uid, icon=folium.Icon(color='red' if uid == st.session_state.user else 'lime')).add_to(m)
    st_folium(m, width="100%", height=300)

    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    st.caption("GLOBAL CHAT")
    components.html(f"""
        <div id="g" style="color:#39FF14; height:150px; overflow-y:auto; font-size:12px; font-family:monospace;"></div>
        <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
        <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
        <script>
            if(!firebase.apps.length) firebase.initializeApp({{databaseURL: "{st.secrets['firebase_db_url']}"}});
            firebase.database().ref('global_chat').limitToLast(10).on('child_added', (s)=>{{
                document.getElementById('g').innerHTML += `<div><b>${{s.val().user}}:</b> ${{s.val().text}}</div>`;
                document.getElementById('g').scrollTop = 9999;
            }});
        </script>
    """, height=160)
    g_msg = st.text_input("MESSAGE", key="gk")
    if st.button("SEND ⚡"):
        if g_msg: db.reference('global_chat').push({'user': st.session_state.user, 'text': g_msg})
    st.markdown('</div>', unsafe_allow_html=True)

# --- PRIVATE CHAT (FIXED) ---
with tab_p:
    st.markdown('<div class="private-box">', unsafe_allow_html=True)
    all_users = db.reference('active_locations').get()
    
    # ดึงรายชื่อเพื่อนที่ออนไลน์ (ที่ไม่ใช่ตัวเอง)
    friend_list = [k for k in all_users.keys() if k != st.session_state.user] if all_users else []
    
    if not friend_list:
        st.warning("ยังไม่มี Agent คนอื่นออนไลน์ในขณะนี้")
    else:
        target = st.selectbox("TALK TO:", friend_list)
        if target:
            path = f"private/{'_'.join(sorted([st.session_state.user, target]))}"
            components.html(f"""
                <div id="p" style="color:#ff00de; height:200px; overflow-y:auto; font-size:12px; font-family:monospace;"></div>
                <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
                <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
                <script>
                    if(!firebase.apps.length) firebase.initializeApp({{databaseURL: "{st.secrets['firebase_db_url']}"}});
                    firebase.database().ref('{path}').limitToLast(15).on('child_added', (s)=>{{
                        document.getElementById('p').innerHTML += `<div><b>${{s.val().user}}:</b> ${{s.val().text}}</div>`;
                        document.getElementById('p').scrollTop = 9999;
                    }});
                </script>
            """, height=210)
            p_msg = st.text_input("PRIVATE MSG", key="pk")
            if st.button("WHISPER 🔒"):
                if p_msg: db.reference(path).push({'user': st.session_state.user, 'text': p_msg})
    st.markdown('</div>', unsafe_allow_html=True)

# --- NEON MIXER ---
with tab_m:
    if len(all_songs) >= 2:
        sA = st.selectbox("DECK A", all_songs, index=0)
        sB = st.selectbox("DECK B", all_songs, index=1)
        # ส่วนผสมเพลงใช้ JS เดียวกับเวอร์ชันก่อนหน้าได้เลยครับ
    else:
        st.warning("ต้องการไฟล์ .mp3 อย่างน้อย 2 ไฟล์ในโฟลเดอร์")

# --- SYSTEM ---
with tab_sys:
    if st.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()
