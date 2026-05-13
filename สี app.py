import streamlit as st
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
import base64
import os
import time
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# --- 1. CONFIG & STYLING ---
st.set_page_config(page_title="SYNAPSE OMNI", layout="wide", initial_sidebar_state="collapsed")

def apply_synapse_ui():
    st.markdown("""
        <style>
            #MainMenu, footer, header {visibility: hidden;}
            .stApp { top: -60px; background-color: #000; }
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
            * { font-family: 'Orbitron', sans-serif !important; }
            
            /* Chat Bubble Styling */
            .msg-container { display: flex; flex-direction: column; gap: 10px; padding: 10px; }
            .msg-right { align-self: flex-end; background: #39FF1422; border: 1px solid #39FF14; 
                         color: #39FF14; padding: 8px 15px; border-radius: 15px 15px 0 15px; max-width: 80%; }
            .msg-left { align-self: flex-start; background: #ff00de22; border: 1px solid #ff00de; 
                        color: #ff00de; padding: 8px 15px; border-radius: 15px 15px 15px 0; max-width: 80%; }
            
            .stTabs [aria-selected="true"] { border: 4px solid #39FF14 !important; box-shadow: 0 0 20px #39FF14; }
        </style>
    """, unsafe_allow_html=True)

apply_synapse_ui()

# --- 2. DATA UTILS ---
def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f: return base64.b64encode(f.read()).decode()
    return ""

all_songs = sorted([f for f in os.listdir('.') if f.endswith('.mp3')])
notif_sound = get_base64("notification.mp3") # ต้องมีไฟล์เสียงนี้ในโฟลเดอร์

if not firebase_admin._apps:
    fb_creds = dict(st.secrets["firebase_credentials"])
    fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
    cred = credentials.Certificate(fb_creds)
    firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})

# --- 3. STICKY LOGO ---
logo_b64 = get_base64("logo1.png")
st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{logo_b64}" width="100"></div>', unsafe_allow_html=True)

# --- 4. AUTH ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    # (ส่วน Login/Register เหมือนเดิม)
    u = st.text_input("AGENT ID")
    p = st.text_input("PASSWORD", type="password")
    if st.button("CONNECT"):
        res = db.reference(f'users/{u}').get()
        if res and res.get('password') == p:
            st.session_state.logged_in, st.session_state.user = True, u
            st.rerun()
    st.stop()

# --- 5. GPS ---
loc = get_geolocation()
my_lat, my_lon = (loc['coords']['latitude'], loc['coords']['longitude']) if loc else (13.75, 100.5)
db.reference(f'active_locations/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})

# --- 6. MAIN TABS ---
tab_r, tab_p, tab_m = st.tabs(["🛰️ RADAR", "🔒 PRIVATE", "🎧 MIXER"])

# --- RADAR & GLOBAL ---
with tab_r:
    m = folium.Map(location=[my_lat, my_lon], zoom_start=16, tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google')
    st_folium(m, width="100%", height=250)
    
    st.caption("GLOBAL SIGNAL")
    components.html(f"""
        <div id="gbox" style="display:flex; flex-direction:column; gap:8px; height:200px; overflow-y:auto; padding:10px; background:#000; border:1px solid #333;"></div>
        <audio id="beep"><source src="data:audio/mp3;base64,{notif_sound}" type="audio/mp3"></audio>
        <script>
            const db = firebase.initializeApp({{databaseURL: "{st.secrets['firebase_db_url']}"}}).database();
            db.ref('global_chat').limitToLast(10).on('child_added', (s) => {{
                const d = s.val();
                const isMe = d.user === "{st.session_state.user}";
                const div = `<div style="align-self:${{isMe?'flex-end':'flex-start'}}; background:${{isMe?'#39FF1422':'#ff00de22'}}; border:1px solid ${{isMe?'#39FF14':'#ff00de'}}; color:${{isMe?'#39FF14':'#ff00de'}}; padding:5px 12px; border-radius:10px; font-size:12px; max-width:80%;"><b>${{d.user}}:</b> ${{d.text}}</div>`;
                const box = document.getElementById('gbox');
                box.innerHTML += div; box.scrollTop = box.scrollHeight;
                if(!isMe) document.getElementById('beep').play();
            }});
        </script>
        <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-app.js"></script>
        <script src="https://www.gstatic.com/firebasejs/8.10.0/firebase-database.js"></script>
    """, height=220)
    
    g_msg = st.text_input("SIGNAL", key="g_in")
    if st.button("SEND ⚡"):
        if g_msg: db.reference('global_chat').push({'user': st.session_state.user, 'text': g_msg})

# --- PRIVATE (LEFT-RIGHT CHAT) ---
with tab_p:
    agents = db.reference('active_locations').get()
    target = st.selectbox("AGENT:", [k for k in agents.keys() if k != st.session_state.user] if agents else ["None"])
    if target != "None":
        path = f"private/{'_'.join(sorted([st.session_state.user, target]))}"
        components.html(f"""
            <div id="pbox" style="display:flex; flex-direction:column; gap:8px; height:250px; overflow-y:auto; padding:10px; background:#000;"></div>
            <script>
                if(!window.fb_p) {{
                    window.fb_p = firebase.initializeApp({{databaseURL: "{st.secrets['firebase_db_url']}"}}, "p_app").database();
                }}
                window.fb_p.ref('{path}').limitToLast(15).on('child_added', (s) => {{
                    const d = s.val();
                    const isMe = d.user === "{st.session_state.user}";
                    document.getElementById('pbox').innerHTML += `<div style="align-self:${{isMe?'flex-end':'flex-start'}}; background:${{isMe?'#39FF1411':'#ff00de11'}}; border:1px solid ${{isMe?'#39FF14':'#ff00de'}}; color:${{isMe?'#39FF14':'#ff00de'}}; padding:8px; border-radius:10px; font-size:12px;">${{d.text}}</div>`;
                    document.getElementById('pbox').scrollTop = 9999;
                }});
            </script>
        """, height=260)
        p_msg = st.text_input("PRIVATE", key="p_in")
        if st.button("WHISPER 🔒"):
            if p_msg: db.reference(path).push({'user': st.session_state.user, 'text': p_msg})

# --- NEON MIXER (CONTINUOUS PLAY) ---
with tab_m:
    if len(all_songs) >= 2:
        sA, sB = st.columns(2)
        songA = sA.selectbox("DECK A", all_songs, index=0)
        songB = sB.selectbox("DECK B", all_songs, index=1)
        
        components.html(f"""
            <div style="border:5px solid #ff00de; border-radius:20px; padding:20px; text-align:center; background:#111;">
                <h3 style="color:#ff00de;">SYSTEM MIXER ACTIVE</h3>
                <button id="btn" style="background:#39FF14; color:#000; padding:15px; border-radius:30px; font-weight:bold; width:100%; cursor:pointer;">START CONTINUOUS FLOW</button>
            </div>
            <script>
                let ctx;
                document.getElementById('btn').onclick = async () => {{
                    ctx = new (window.AudioContext || window.webkitAudioContext)();
                    const load = async (b64) => ctx.decodeAudioData(await (await fetch('data:audio/mp3;base64,' + b64)).arrayBuffer());
                    let bA = await load('{get_base64(songA)}');
                    let bB = await load('{get_base64(songB)}');
                    const play = (b, isA) => {{
                        let s = ctx.createBufferSource(); s.buffer = b; s.connect(ctx.destination);
                        s.onended = () => play(isA ? bB : bA, !isA);
                        s.start(0);
                    }};
                    play(bA, true);
                    document.getElementById('btn').innerText = "SYSTEM FLOWING...";
                }};
            </script>
        """, height=250)
    else:
        st.warning("ต้องการ .mp3 อย่างน้อย 2 ไฟล์")
