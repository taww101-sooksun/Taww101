import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
import base64
import os
import time
from streamlit_js_eval import get_geolocation

# --- 1. CONFIG & CSS CUSTOMIZATION (Hide Streamlit UI) ---
st.set_page_config(page_title="SYNAPSE OMNI", layout="wide", initial_sidebar_state="collapsed")

def apply_neon_theme():
    st.markdown("""
        <style>
            /* Hide Streamlit Elements */
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp { top: -60px; background-color: #000; }
            
            /* Global Neon Style */
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
            * { font-family: 'Orbitron', sans-serif !important; }
            
            .stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: transparent; }
            .stTabs [data-baseweb="tab"] {
                background-color: #111; border: 1px solid #333;
                border-radius: 5px; padding: 10px 20px; color: #555;
            }
            .stTabs [aria-selected="true"] {
                background-color: #39FF1422 !important;
                border-color: #39FF14 !important; color: #39FF14 !important;
                box-shadow: 0 0 10px #39FF14;
            }
            
            /* Custom Scrollbar */
            ::-webkit-scrollbar { width: 5px; }
            ::-webkit-scrollbar-thumb { background: #39FF14; border-radius: 10px; }
        </style>
    """, unsafe_allow_html=True)

apply_neon_theme()

# --- 2. CORE FUNCTIONS ---
def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

# --- 3. FIREBASE CONNECTION ---
if not firebase_admin._apps:
    try:
        fb_creds = dict(st.secrets["firebase_credentials"])
        fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(fb_creds)
        firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
    except Exception as e:
        st.error(f"Firebase Error: {e}")

# --- 4. SESSION INITIALIZATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None

logo_b64 = get_base64("logo1.png")
notif_b64 = get_base64("notification.mp3")
all_songs = sorted([f for f in os.listdir('.') if f.endswith('.mp3')])

# --- 5. ANIMATED HEADER ---
header_html = f"""
<div style="text-align:center; padding: 20px;">
    <style>
        @keyframes dance {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.1) rotate(3deg); }} }}
        @keyframes wink {{ 0%, 100% {{ opacity: 1; text-shadow: 0 0 20px #39FF14; }} 50% {{ opacity: 0.3; }} }}
        .logo {{ width: 80px; animation: dance 1s infinite alternate; filter: drop-shadow(0 0 10px #39FF14); }}
        .slogan {{ color: #39FF14; font-size: 18px; font-weight: bold; animation: wink 2s infinite; margin-top: 10px; }}
    </style>
    <img src="data:image/png;base64,{logo_b64}" class="logo">
    <div class="slogan">SYNAPSE: อยู่นิ่งๆ ไม่เจ็บตัว</div>
</div>
"""
components.html(header_html, height=160)

# --- 6. AUTHENTICATION PAGE ---
if not st.session_state.logged_in:
    cols = st.columns([1, 2, 1])
    with cols[1]:
        auth_tab1, auth_tab2 = st.tabs(["🔐 LOGIN", "📝 REGISTER"])
        with auth_tab1:
            with st.form("login"):
                u = st.text_input("AGENT ID")
                p = st.text_input("PASSWORD", type="password")
                if st.form_submit_button("ACCESS SYSTEM", use_container_width=True):
                    res = db.reference(f'users/{u}').get()
                    if res and res.get('password') == p:
                        st.session_state.logged_in = True
                        st.session_state.user = u
                        st.rerun()
                    else: st.error("Access Denied")
        with auth_tab2:
            with st.form("reg"):
                nu = st.text_input("NEW AGENT ID")
                np = st.text_input("NEW PASSWORD", type="password")
                if st.form_submit_button("CREATE ACCOUNT", use_container_width=True):
                    if nu and np:
                        db.reference(f'users/{nu}').set({'password': np, 'created_at': datetime.now().isoformat()})
                        st.success("Success! Please Login.")
    st.stop()

# --- 7. MAIN SYSTEM (TABS) ---
st.markdown(f"<div style='text-align:right; color:#39FF14; font-size:12px; margin-bottom:10px;'>CONNECTED: {st.session_state.user}</div>", unsafe_allow_html=True)

tab_comms, tab_music, tab_sys = st.tabs(["💬 COMMS & RADAR", "🎧 NEON MIXER", "⚙️ SYSTEM"])

# --- TAB: COMMS & RADAR (Chat + GPS) ---
with tab_comms:
    # 1. ดึงพิกัดจาก Browser
    loc = get_geolocation()
    
    # 2. ตรวจสอบก่อนว่ามีข้อมูลพิกัดจริงไหม (กัน Error)
    if loc and 'coords' in loc:
        user_lat = loc['coords']['latitude']
        user_lon = loc['coords']['longitude']
        
        # แสดงสถานะให้ Agent รู้ว่าล็อกเป้าแล้ว
        st.success(f"🎯 GPS LOCKED: {user_lat:.4f}, {user_lon:.4f}")

        # Update GPS เข้า Firebase
        db.reference(f'active_locations/{st.session_state.user}').update({
            'lat': user_lat, 
            'lon': user_lon, 
            'ts': time.time()
        })
    else:
        # ถ้ายังไม่มีพิกัด ให้ตั้งค่าเริ่มต้นไว้ก่อน และแจ้งเตือนเบาๆ
        user_lat, user_lon = 0.0, 0.0
        st.info("🛰️ กำลังค้นหาสัญญาณดาวเทียม... กรุณาเปิด GPS")

        user_lat, user_lon = loc['coords']['latitude'], loc['coords']['longitude']
        # Update GPS to Firebase for others to see
        db.reference(f'active_locations/{st.session_state.user}').set({
            'lat': user_lat, 'lon': user_lon, 'ts': time.time()
        })

    chat_html = f"""
    <div id="chat-box" style="background:#0a0a0a; border:1px solid #39FF14; height:400px; overflow-y:auto; padding:15px; border-radius:10px; box-shadow: inset 0 0 10px #39FF1433;">
        <div id="msgs"></div>
    </div>
    <audio id="beep"><source src="data:audio/mp3;base64,{notif_b64}" type="audio/mp3"></audio>
    <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
    <script>
        const conf = {{ databaseURL: "{st.secrets['firebase_db_url']}" }};
        if(!firebase.apps.length) firebase.initializeApp(conf);
        const db = firebase.database();
        
        db.ref('global_chat').limitToLast(15).on('child_added', (s) => {{
            const m = s.val();
            const isMe = m.user === "{st.session_state.user}";
            const div = document.createElement('div');
            div.style = `margin:10px 0; padding:8px 12px; border-radius:8px; max-width:80%; font-size:13px; ${{isMe?'margin-left:auto; background:#39FF1422; border-right:3px solid #39FF14;':'background:#222; border-left:3px solid #777;'}}`;
            
            let content = `<div style="color:#777; font-size:9px;">${{m.user}} ${{m.loc? '📍 '+m.loc : ''}}</div>`;
            if(m.text) content += `<div>${{m.text}}</div>`;
            if(m.img) content += `<img src="data:image/png;base64,${{m.img}}" style="width:100%; margin-top:5px; border-radius:5px;">`;
            
            div.innerHTML = content;
            document.getElementById('msgs').appendChild(div);
            document.getElementById('chat-box').scrollTop = 9999;
            if(!isMe) document.getElementById('beep').play();
        }});
    </script>
    """
    components.html(chat_html, height=420)

    with st.container():
        c1, c2, c3 = st.columns([3, 1, 1])
        msg_in = c1.text_input("SIGNAL", placeholder="Type message...", label_visibility="collapsed")
        img_in = c2.file_uploader("IMG", type=['png','jpg'], label_visibility="collapsed")
        if c3.button("SEND ⚡", use_container_width=True):
            if msg_in or img_in:
                payload = {'user': st.session_state.user, 'loc': f"{user_lat:.4f},{user_lon:.4f}"}
                if msg_in: payload['text'] = msg_in
                if img_in: payload['img'] = base64.b64encode(img_in.read()).decode()
                db.reference('global_chat').push(payload)
                st.rerun()

# --- TAB: MUSIC MIXER (Continuous Play) ---
with tab_music:
    if len(all_songs) >= 2:
        m_col1, m_col2 = st.columns(2)
        sA = m_col1.selectbox("DECK A", all_songs, index=0)
        sB = m_col2.selectbox("DECK B", all_songs, index=1 if len(all_songs)>1 else 0)
        
        audio_a = get_base64(sA)
        audio_b = get_base64(sB)

        mixer_html = f"""
        <div style="background:#111; border:2px solid #ff00de; border-radius:15px; padding:20px; text-align:center;">
            <canvas id="scope" style="width:100%; height:80px; background:#000; border-radius:10px;"></canvas>
            <div id="m-status" style="color:#ff00de; font-size:12px; margin:10px 0;">READY TO MIX</div>
            <button onclick="startMix()" style="background:linear-gradient(45deg, #ff00de, #00f3ff); border:none; color:white; padding:15px 30px; border-radius:30px; font-weight:bold; cursor:pointer; width:100%;">START CONTINUOUS PLAY</button>
        </div>
        <script>
            let actx, aA, aB, sA, sB, gA, gB;
            async function startMix() {{
                actx = new (window.AudioContext || window.webkitAudioContext)();
                const load = async (b) => {{
                    const r = await fetch('data:audio/mp3;base64,' + b);
                    return await actx.decodeAudioData(await r.arrayBuffer());
                }};
                sA = await load('{audio_a}'); sB = await load('{audio_b}');
                play(sA, true);
            }}
            function play(buf, isA) {{
                let s = actx.createBufferSource(); s.buffer = buf;
                let g = actx.createGain(); s.connect(g).connect(actx.destination);
                s.start(0);
                document.getElementById('m-status').innerText = isA ? "PLAYING DECK A" : "PLAYING DECK B";
                s.onended = () => {{ play(isA ? sB : sA, !isA); }};
            }}
        </script>
        """
        components.html(mixer_html, height=300)
    else:
        st.warning("Please add at least 2 .mp3 files to the folder.")

# --- TAB: SYSTEM ---
with tab_sys:
    st.subheader("SYSTEM CONTROL")
    if st.button("LOGOUT", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    st.divider()
    st.caption("SYNAPSE OMNI V3.0 | 'อยู่นิ่งๆ ไม่เจ็บตัว'")
