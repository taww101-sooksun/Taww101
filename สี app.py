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

# --- 1. CONFIG & NEON SYSTEM STYLE ---
st.set_page_config(page_title="SYNAPSE OMNI", layout="wide", initial_sidebar_state="collapsed")

def apply_synapse_theme():
    st.markdown("""
        <style>
            #MainMenu, footer, header {visibility: hidden;}
            .stApp { top: -60px; background-color: #000; }
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
            * { font-family: 'Orbitron', sans-serif !important; }
            
            /* Neon Borders & UI */
            .stTabs [data-baseweb="tab-list"] { gap: 10px; }
            .stTabs [aria-selected="true"] {
                border: 4px solid #39FF14 !important;
                box-shadow: 0 0 25px #39FF14;
                color: #39FF14 !important;
                background-color: #111 !important;
            }
            .chat-container {
                border: 3px solid #39FF14; border-radius: 15px;
                padding: 10px; background: rgba(0,0,0,0.8);
                box-shadow: inset 0 0 15px #39FF1444; margin-bottom: 10px;
            }
            .private-container {
                border: 3px solid #ff00de; border-radius: 15px;
                padding: 10px; box-shadow: inset 0 0 15px #ff00de44;
            }
            .auth-box {
                border: 2px solid #39FF14; border-radius: 20px;
                padding: 25px; background: rgba(10,10,10,0.9);
                box-shadow: 0 0 20px #39FF1433;
            }
        </style>
    """, unsafe_allow_html=True)

apply_synapse_theme()

# --- 2. DATA UTILITIES & FIREBASE ---
def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

if not firebase_admin._apps:
    fb_creds = dict(st.secrets["firebase_credentials"])
    fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate(fb_creds)
    firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})

# --- 3. PERSISTENT LOGO (Visible on all pages) ---
logo_b64 = get_base64("logo1.png")
st.markdown(f"""
    <div style="text-align:center; padding:10px;">
        <img src="data:image/png;base64,{logo_b64}" style="width:120px; filter: drop-shadow(0 0 15px #39FF14); animation: pulse 2s infinite;">
        <h2 style="color:#39FF14; text-shadow: 0 0 10px #39FF14; margin-top:5px;">SYNAPSE COMMAND</h2>
        <p style="color:#39FF14; font-size:12px; letter-spacing:3px;">อยู่นิ่งๆ ไม่เจ็บตัว</p>
    </div>
    <style>@keyframes pulse {{ 0% {{transform:scale(1);}} 50% {{transform:scale(1.05);}} 100% {{transform:scale(1);}} }}</style>
""", unsafe_allow_html=True)

# --- 4. AUTHENTICATION SYSTEM (LOGIN & REGISTER) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.markdown('<div class="auth-box">', unsafe_allow_html=True)
        auth_tab1, auth_tab2 = st.tabs(["🔐 เข้าสู่ระบบ", "📝 ลงทะเบียนใหม่"])
        
        with auth_tab1:
            with st.form("login_form"):
                u = st.text_input("AGENT ID")
                p = st.text_input("PASSWORD", type="password")
                if st.form_submit_button("CONNECT SYSTEM", use_container_width=True):
                    res = db.reference(f'users/{u}').get()
                    if res and res.get('password') == p:
                        st.session_state.logged_in, st.session_state.user = True, u
                        st.rerun()
                    else: st.error("ID หรือ รหัสผ่านไม่ถูกต้อง")
        
        with auth_tab2:
            with st.form("register_form"):
                new_u = st.text_input("ตั้ง AGENT ID ใหม่")
                new_p = st.text_input("ตั้ง PASSWORD", type="password")
                confirm_p = st.text_input("ยืนยัน PASSWORD", type="password")
                if st.form_submit_button("CREATE AGENT", use_container_width=True):
                    if not new_u or not new_p:
                        st.warning("กรุณากรอกข้อมูลให้ครบถ้วน")
                    elif new_p != confirm_p:
                        st.error("รหัสผ่านไม่ตรงกัน")
                    else:
                        # ตรวจสอบว่า ID ซ้ำไหม
                        existing_user = db.reference(f'users/{new_u}').get()
                        if existing_user:
                            st.error(f"ID '{new_u}' นี้มีผู้ใช้งานแล้ว")
                        else:
                            db.reference(f'users/{new_u}').set({
                                'password': new_p,
                                'created_at': datetime.now().isoformat()
                            })
                            st.success("ลงทะเบียนสำเร็จ! กรุณาเข้าสู่ระบบ")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- 5. REAL-TIME GPS (HIGH ACCURACY) ---
# ดึงพิกัดพยายามใช้ High Accuracy เพื่อความแม่นยำ
loc = get_geolocation() 
my_lat, my_lon = 0.0, 0.0

if loc and 'coords' in loc:
    my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']
    db.reference(f'active_locations/{st.session_state.user}').update({
        'lat': my_lat, 'lon': my_lon, 'ts': time.time()
    })

# --- 6. MAIN SYSTEM TABS ---
st.markdown(f"<div style='text-align:right; color:#39FF14; font-size:12px; margin-bottom:10px;'>AGENT: {st.session_state.user}</div>", unsafe_allow_html=True)
tab_radar, tab_private, tab_music, tab_sys = st.tabs(["🛰️ RADAR & GLOBAL", "🔒 PRIVATE LINK", "🎧 NEON MIXER", "⚙️ SYSTEM"])

# --- TAB: RADAR & GLOBAL CHAT ---
with tab_radar:
    # Radar Map (Google Hybrid)
    m = folium.Map(location=[my_lat, my_lon] if my_lat != 0 else [13.7, 100.5], 
                   zoom_start=16, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')
    
    active_agents = db.reference('active_locations').get()
    if active_agents:
        for uid, d in active_agents.items():
            # ถ้าเป็นตัวเองใช้สีแดง คนอื่นใช้สีเขียวสว่าง
            icon_color = 'red' if uid == st.session_state.user else 'lime'
            folium.Marker([d['lat'], d['lon']], popup=uid, icon=folium.Icon(color=icon_color)).add_to(m)
    st_folium(m, width="100%", height=350)

    # Global Chat Container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.caption("📡 GLOBAL SIGNAL BROADCAST")
    components.html(f"""
        <div id="g-chat" style="color:#39FF14; height:200px; overflow-y:auto; font-size:12px; font-family:sans-serif;"></div>
        <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
        <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
        <script>
            if(!firebase.apps.length) firebase.initializeApp({{databaseURL: "{st.secrets['firebase_db_url']}"}});
            firebase.database().ref('global_chat').limitToLast(15).on('child_added', (s)=>{{
                const d = s.val();
                document.getElementById('g-chat').innerHTML += `<div><span style="color:#555;">[${{new Date().toLocaleTimeString()}}]</span> <b>${{d.user}}:</b> ${{d.text}}</div>`;
                document.getElementById('g-chat').scrollTop = 9999;
            }});
        </script>
    """, height=210)
    
    with st.form("global_msg", clear_on_submit=True):
        g_msg = st.text_input("BROADCAST MESSAGE", placeholder="พิมพ์ข้อความ...", label_visibility="collapsed")
        if st.form_submit_button("SEND GLOBAL ⚡", use_container_width=True):
            if g_msg:
                db.reference('global_chat').push({'user': st.session_state.user, 'text': g_msg, 'ts': time.time()})
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB: PRIVATE LINK ---
with tab_private:
    st.markdown('<div class="private-container">', unsafe_allow_html=True)
    agent_list = [k for k in active_agents.keys() if k != st.session_state.user] if active_agents else []
    
    if not agent_list:
        st.info("ยังไม่มี Agent อื่นออนไลน์ในขณะนี้")
    else:
        target_agent = st.selectbox("ติดต่อ AGENT:", agent_list)
        chat_path = f"private_chats/{'_'.join(sorted([st.session_state.user, target_agent]))}"
        
        st.caption(f"PRIVATE LINK WITH: {target_agent}")
        components.html(f"""
            <div id="p-chat" style="color:#ff00de; height:250px; overflow-y:auto; font-size:12px; font-family:sans-serif;"></div>
            <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
            <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
            <script>
                if(!firebase.apps.length) firebase.initializeApp({{databaseURL: "{st.secrets['firebase_db_url']}"}});
                firebase.database().ref('{chat_path}').limitToLast(20).on('child_added', (s)=>{{
                    const d = s.val();
                    document.getElementById('p-chat').innerHTML += `<div><b>${{d.user}}:</b> ${{d.text}}</div>`;
                    document.getElementById('p-chat').scrollTop = 9999;
                }});
            </script>
        """, height=260)
        
        with st.form("private_msg", clear_on_submit=True):
            p_msg = st.text_input("PRIVATE MESSAGE", placeholder="กระซิบข้อมูล...", label_visibility="collapsed")
            if st.form_submit_button("SEND PRIVATE 🔒", use_container_width=True):
                if p_msg:
                    db.reference(chat_path).push({'user': st.session_state.user, 'text': p_msg, 'ts': time.time()})
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB: NEON MIXER ---
with tab_music:
    if len(all_songs) >= 2:
        st.markdown('<div style="border:5px solid #ff00de; border-radius:20px; padding:20px; background:#000; box-shadow: 0 0 20px #ff00de55;">', unsafe_allow_html=True)
        sA, sB = st.columns(2)
        songA = sA.selectbox("DECK A", all_songs, index=0)
        songB = sB.selectbox("DECK B", all_songs, index=1)
        
        components.html(f"""
            <div style="text-align:center;">
                <h3 style="color:#ff00de; text-shadow:0 0 10px #ff00de;">NEON MIXER ACTIVE</h3>
                <button id="playBtn" style="background:linear-gradient(45deg, #ff00de, #39FF14); border:none; padding:20px; border-radius:50px; color:white; width:100%; font-weight:bold; cursor:pointer; box-shadow: 0 0 15px #ff00de;">START CONTINUOUS PLAY</button>
            </div>
            <script>
                let ctx;
                document.getElementById('playBtn').onclick = async () => {{
                    ctx = new (window.AudioContext || window.webkitAudioContext)();
                    const load = async (b64) => ctx.decodeAudioData(await (await fetch('data:audio/mp3;base64,' + b64)).arrayBuffer());
                    let bA = await load('{get_base64(songA)}');
                    let bB = await load('{get_base64(songB)}');
                    const play = (b, isA) => {{
                        let s = ctx.createBufferSource(); s.buffer = b; s.connect(ctx.destination); s.start(0);
                        s.onended = () => play(isA ? bB : bA, !isA);
                    }};
                    play(bA, true);
                    document.getElementById('playBtn').innerText = "MIXING...";
                }};
            </script>
        """, height=220)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("กรุณาใส่ไฟล์เพลง .mp3 อย่างน้อย 2 เพลงในโฟลเดอร์แอป")

# --- TAB: SYSTEM ---
with tab_sys:
    st.subheader("SYSTEM MANAGEMENT")
    if st.button("LOGOUT / EXIT SYSTEM"):
        st.session_state.logged_in = False
        st.rerun()
    st.divider()
    st.caption("SYNAPSE OMNI V6.0 | อยู่นิ่งๆ ไม่เจ็บตัว")
