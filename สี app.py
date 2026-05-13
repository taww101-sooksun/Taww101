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
                border: 3px solid #39FF14;
                border-radius: 15px;
                padding: 10px;
                background: rgba(0,0,0,0.8);
                box-shadow: inset 0 0 15px #39FF1444;
            }
            .private-container {
                border: 3px solid #ff00de;
                border-radius: 15px;
                padding: 10px;
                box-shadow: inset 0 0 15px #ff00de44;
            }
        </style>
    """, unsafe_allow_html=True)

apply_synapse_theme()

# --- 2. DATA UTILITIES ---
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
        <h3 style="color:#39FF14; text-shadow: 0 0 10px #39FF14; margin-top:5px;">SYNAPSE COMMAND</h3>
    </div>
    <style>@keyframes pulse {{ 0% {{transform:scale(1);}} 50% {{transform:scale(1.05);}} 100% {{transform:scale(1);}} }}</style>
""", unsafe_allow_html=True)

# --- 4. SESSION CHECK ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    u = st.text_input("AGENT ID")
    p = st.text_input("PASSWORD", type="password")
    if st.button("BOOT SYSTEM"):
        res = db.reference(f'users/{u}').get()
        if res and res.get('password') == p:
            st.session_state.logged_in, st.session_state.user = True, u
            st.rerun()
    st.stop()

# --- 5. REAL-TIME GPS (HIGH ACCURACY) ---
# บังคับใช้พิกัดจาก GPS ชิปโดยตรง
loc = get_geolocation(component_ready_pin=True) 
my_lat, my_lon = 0.0, 0.0

if loc and 'coords' in loc:
    my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']
    db.reference(f'active_locations/{st.session_state.user}').update({
        'lat': my_lat, 'lon': my_lon, 'ts': time.time()
    })

# --- 6. NAVIGATION TABS ---
tab_radar, tab_private, tab_music, tab_sys = st.tabs(["🛰️ RADAR & GLOBAL", "🔒 PRIVATE LINK", "🎧 NEON MIXER", "⚙️ SYSTEM"])

# --- TAB: RADAR & GLOBAL CHAT ---
with tab_radar:
    # Radar Map
    m = folium.Map(location=[my_lat, my_lon] if my_lat != 0 else [13.7, 100.5], 
                   zoom_start=16, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Hybrid')
    
    active_agents = db.reference('active_locations').get()
    if active_agents:
        for uid, d in active_agents.items():
            icon_color = 'red' if uid == st.session_state.user else 'lime'
            folium.Marker([d['lat'], d['lon']], popup=uid, icon=folium.Icon(color=icon_color)).add_to(m)
    st_folium(m, width="100%", height=350)

    # Global Chat
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.caption("GLOBAL SIGNAL")
    components.html(f"""
        <div id="g-chat" style="color:#39FF14; height:200px; overflow-y:auto; font-size:12px;"></div>
        <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
        <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
        <script>
            if(!firebase.apps.length) firebase.initializeApp({{databaseURL: "{st.secrets['firebase_db_url']}"}});
            firebase.database().ref('global_chat').limitToLast(10).on('child_added', (s)=>{{
                document.getElementById('g-chat').innerHTML += `<div><b>${{s.val().user}}:</b> ${{s.val().text}}</div>`;
                document.getElementById('g-chat').scrollTop = 9999;
            }});
        </script>
    """, height=210)
    g_msg = st.text_input("BROADCAST MESSAGE", key="g_in")
    if st.button("SEND GLOBAL ⚡"):
        db.reference('global_chat').push({'user': st.session_state.user, 'text': g_msg, 'ts': time.time()})
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB: PRIVATE LINK ---
with tab_private:
    st.markdown('<div class="private-container">', unsafe_allow_html=True)
    target_agent = st.selectbox("SELECT AGENT", [k for k in active_agents.keys() if k != st.session_state.user] if active_agents else ["No Agents Online"])
    
    # สร้าง Path แชทส่วนตัวแบบไม่สลับกัน (เรียงตามชื่อ)
    chat_path = f"private_chats/{'_'.join(sorted([st.session_state.user, target_agent]))}"
    
    components.html(f"""
        <div id="p-chat" style="color:#ff00de; height:250px; overflow-y:auto; font-size:12px;"></div>
        <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
        <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
        <script>
            if(!firebase.apps.length) firebase.initializeApp({{databaseURL: "{st.secrets['firebase_db_url']}"}});
            firebase.database().ref('{chat_path}').limitToLast(15).on('child_added', (s)=>{{
                document.getElementById('p-chat').innerHTML += `<div><b>${{s.val().user}}:</b> ${{s.val().text}}</div>`;
                document.getElementById('p-chat').scrollTop = 9999;
            }});
        </script>
    """, height=260)
    p_msg = st.text_input("PRIVATE MESSAGE", key="p_in")
    if st.button("SEND PRIVATE 🔒"):
        db.reference(chat_path).push({'user': st.session_state.user, 'text': p_msg, 'ts': time.time()})
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB: NEON MIXER (Continuous Play) ---
with tab_music:
    if len(all_songs) >= 2:
        sA, sB = st.columns(2)
        songA = sA.selectbox("DECK A", all_songs, index=0)
        songB = sB.selectbox("DECK B", all_songs, index=1)
        
        components.html(f"""
            <div style="border:5px solid #ff00de; border-radius:20px; padding:20px; text-align:center; background:#000;">
                <h3 style="color:#ff00de; text-shadow:0 0 10px #ff00de;">NEON MIXER ACTIVE</h3>
                <button onclick="start()" style="background:linear-gradient(45deg, #ff00de, #39FF14); border:none; padding:20px; border-radius:50px; color:white; width:100%; font-weight:bold; cursor:pointer;">START CONTINUOUS PLAY</button>
            </div>
            <script>
                let ctx;
                async function start() {{
                    ctx = new AudioContext();
                    const load = async (b64) => ctx.decodeAudioData(await (await fetch('data:audio/mp3;base64,' + b64)).arrayBuffer());
                    let bA = await load('{get_base64(songA)}');
                    let bB = await load('{get_base64(songB)}');
                    const play = (b, isA) => {{
                        let s = ctx.createBufferSource(); s.buffer = b; s.connect(ctx.destination); s.start(0);
                        s.onended = () => play(isA ? bB : bA, !isA);
                    }};
                    play(bA, true);
                }}
            </script>
        """, height=300)

# --- TAB: SYSTEM ---
with tab_sys:
    if st.button("EXIT SYSTEM"):
        st.session_state.logged_in = False
        st.rerun()
    st.caption("SYNAPSE OMNI V5.0 | อยู่นิ่งๆ ไม่เจ็บตัว")
