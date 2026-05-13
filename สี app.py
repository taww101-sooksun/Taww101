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

# --- 1. CONFIG & CSS NEON STYLE ---
st.set_page_config(page_title="SYNAPSE OMNI", layout="wide", initial_sidebar_state="collapsed")

def apply_neon_theme():
    st.markdown("""
        <style>
            #MainMenu, footer, header {visibility: hidden;}
            .stApp { top: -60px; background-color: #000; }
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
            * { font-family: 'Orbitron', sans-serif !important; }
            
            /* Neon Border for Tabs and Containers */
            .stTabs [data-baseweb="tab-list"] { gap: 10px; }
            .stTabs [aria-selected="true"] {
                background-color: #39FF1422 !important;
                border: 3px solid #39FF14 !important;
                box-shadow: 0 0 20px #39FF14;
                color: #39FF14 !important;
            }
            .neon-container {
                border: 5px solid #ff00de;
                border-radius: 20px;
                padding: 20px;
                box-shadow: 0 0 30px #ff00de55;
                background: rgba(10,10,10,0.9);
            }
        </style>
    """, unsafe_allow_html=True)

apply_neon_theme()

# --- 2. FIREBASE & CORE FUNCTIONS ---
if not firebase_admin._apps:
    fb_creds = dict(st.secrets["firebase_credentials"])
    fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate(fb_creds)
    firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})

def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

# --- 3. SESSION & DATA ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = None

logo_b64 = get_base64("logo1.png")
notif_b64 = get_base64("notification.mp3")
all_songs = sorted([f for f in os.listdir('.') if f.endswith('.mp3')])

# --- 4. LOGIN SYSTEM ---
if not st.session_state.logged_in:
    st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo_b64}" width="150"></div>', unsafe_allow_html=True)
    cols = st.columns([1, 2, 1])
    with cols[1]:
        u = st.text_input("AGENT ID")
        p = st.text_input("PASSWORD", type="password")
        if st.button("BOOT SYSTEM", use_container_width=True):
            res = db.reference(f'users/{u}').get()
            if res and res.get('password') == p:
                st.session_state.logged_in, st.session_state.user = True, u
                st.rerun()
    st.stop()

# --- 5. MAIN INTERFACE ---
st.markdown(f"<div style='text-align:center; color:#39FF14; text-shadow:0 0 10px #39FF14;'>CONNECTED: {st.session_state.user}</div>", unsafe_allow_html=True)
tab_radar, tab_music, tab_sys = st.tabs(["🛰️ RADAR & COMMS", "🎧 NEON MIXER", "⚙️ SYSTEM"])

# --- TAB: RADAR & COMMS ---
with tab_radar:
    loc = get_geolocation()
    my_lat, my_lon = 13.7563, 100.5018 # Default BKK
    
    if loc and 'coords' in loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']
        db.reference(f'active_locations/{st.session_state.user}').update({
            'lat': my_lat, 'lon': my_lon, 'ts': time.time()
        })

    # Display Map
    m = folium.Map(location=[my_lat, my_lon], zoom_start=15, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')
    
    # ดึงพิกัดเพื่อนๆ มาปักหมุด
    others = db.reference('active_locations').get()
    if others:
        for uid, data in others.items():
            color = 'red' if uid == st.session_state.user else 'blue'
            folium.Marker([data['lat'], data['lon']], popup=uid, icon=folium.Icon(color=color, icon='user', prefix='fa')).add_to(m)
    
    st_folium(m, width="100%", height=400)

    # Chat Room
    chat_html = f"""
    <div id="chat" style="background:#050505; border:2px solid #39FF14; height:300px; overflow-y:auto; padding:10px; border-radius:10px; margin-top:10px;">
        <div id="msgs"></div>
    </div>
    <audio id="beep"><source src="data:audio/mp3;base64,{notif_b64}" type="audio/mp3"></audio>
    <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
    <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
    <script>
        const conf = {{ databaseURL: "{st.secrets['firebase_db_url']}" }};
        if(!firebase.apps.length) firebase.initializeApp(conf);
        firebase.database().ref('global_chat').limitToLast(10).on('child_added', (s) => {{
            const m = s.val();
            const div = document.createElement('div');
            div.style = "color:#fff; font-size:12px; margin-bottom:5px; border-bottom:1px solid #222;";
            div.innerHTML = `<b>${{m.user}}:</b> ${{m.text}}`;
            document.getElementById('msgs').appendChild(div);
            document.getElementById('chat').scrollTop = 9999;
            if(m.user !== "{st.session_state.user}") document.getElementById('beep').play();
        }});
    </script>
    """
    components.html(chat_html, height=320)
    
    msg_txt = st.text_input("MESSAGE", label_visibility="collapsed")
    if st.button("SEND SIGNAL ⚡", use_container_width=True):
        if msg_txt:
            db.reference('global_chat').push({'user': st.session_state.user, 'text': msg_txt, 'ts': time.time()})
            st.rerun()

# --- TAB: NEON MIXER ---
with tab_music:
    st.markdown('<div class="neon-container">', unsafe_allow_html=True)
    if len(all_songs) >= 2:
        c1, c2 = st.columns(2)
        sA = c1.selectbox("DECK A", all_songs, index=0)
        sB = c2.selectbox("DECK B", all_songs, index=1)
        
        mix_html = f"""
        <div style="text-align:center;">
            <canvas id="scope" style="width:100%; height:100px; background:#000; border:2px solid #39FF14; border-radius:10px;"></canvas>
            <h2 id="status" style="color:#ff00de; text-shadow:0 0 10px #ff00de;">SYSTEM READY</h2>
            <button onclick="start()" style="background:linear-gradient(45deg, #ff00de, #39FF14); border:none; padding:20px; border-radius:50px; color:white; font-weight:bold; width:100%; cursor:pointer; box-shadow: 0 0 20px #ff00de;">START CONTINUOUS PLAY</button>
        </div>
        <script>
            let ctx, songA, songB;
            async function start() {{
                ctx = new (window.AudioContext || window.webkitAudioContext)();
                const load = async (b64) => {{
                    const r = await fetch('data:audio/mp3;base64,' + b64);
                    return await ctx.decodeAudioData(await r.arrayBuffer());
                }};
                document.getElementById('status').innerText = "LOADING...";
                songA = await load('{get_base64(sA)}');
                songB = await load('{get_base64(sB)}');
                play(songA, true);
            }}
            function play(buf, isA) {{
                let s = ctx.createBufferSource(); s.buffer = buf;
                s.connect(ctx.destination);
                s.start(0);
                document.getElementById('status').innerText = isA ? "PLAYING: DECK A" : "PLAYING: DECK B";
                s.onended = () => play(isA ? songB : songA, !isA);
            }}
        </script>
        """
        components.html(mix_html, height=350)
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB: SYSTEM ---
with tab_sys:
    if st.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()
    st.caption("SYNAPSE OMNI V4.0 | 'อยู่นิ่งๆ ไม่เจ็บตัว'")
