import streamlit as st
import streamlit.components.v1 as components
import os
import base64
import math
import time
import folium
import firebase_admin
from firebase_admin import credentials, db
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
from datetime import datetime, date

# --- [ 1. FIREBASE INITIALIZATION ] ---
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            if "\\n" in fb_creds["private_key"]:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(fb_creds)
            return firebase_admin.initialize_app(cred, {
                'databaseURL': "https://sooksun1-default-rtdb.firebaseio.com/"
            })
        except Exception as e:
            st.error(f"❌ Firebase Error: {e}")
            return None
    return firebase_admin.get_app()

firebase_app = init_firebase()

# --- [ 2. SESSION STATE ] ---
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#00ff41"
if 'user_name' not in st.session_state: st.session_state.user_name = "AGENT_X"
if 'current_page' not in st.session_state: st.session_state.current_page = "MAIN MENU"

st.set_page_config(page_title="SYNAPSE X", layout="wide")

# --- [ 3. CSS STYLE ] ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    header, footer, .stDeployButton {{visibility: hidden; display: none !important;}}
    [data-testid="stSidebar"] {{display: none;}}
    .stApp {{ background-color: #000; color: #ffffff; font-family: 'Orbitron', sans-serif; }}
    .neon-title {{ color: {st.session_state.theme_color}; text-shadow: 0 0 15px {st.session_state.theme_color}; text-align: center; margin-bottom: 25px; }}
    div.stButton > button {{ background-color: #111; border: 2px solid {st.session_state.theme_color}; color: {st.session_state.theme_color}; border-radius: 15px; padding: 15px; font-weight: bold; }}
    div.stButton > button:hover {{ background-color: {st.session_state.theme_color}; color: black; box-shadow: 0 0 20px {st.session_state.theme_color}; }}
    </style>
    """, unsafe_allow_html=True)

def go_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- [ 4. INTERFACE LOGIC ] ---

if st.session_state.current_page == "MAIN MENU":
    st.markdown("<h1 class='neon-title'>SYNAPSE X</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 SETTINGS", use_container_width=True): go_to("SETTINGS")
        if st.button("🛰️ GPS & CHAT", use_container_width=True): go_to("GPS")
    with col2:
        if st.button("🎧 MUSIC", use_container_width=True): go_to("MUSIC")
        if st.button("🧬 DECODER", use_container_width=True): go_to("DECODER")
    if st.button("🎙️ SENSOR LAB", use_container_width=True): go_to("SENSOR")
    st.divider()
    st.caption(f"AGENT: {st.session_state.user_name} | 'อยู่นิ่งๆ ไม่เจ็บตัว'")

else:
    if st.button("⬅️ BACK TO MENU"): go_to("MAIN MENU")
    st.write("---")

    # --- PAGE: SETTINGS ---
    if st.session_state.current_page == "SETTINGS":
        st.markdown("<h2 class='neon-title'>SETTINGS</h2>", unsafe_allow_html=True)
        st.session_state.user_name = st.text_input("AGENT NAME", value=st.session_state.user_name)
        st.session_state.theme_color = st.color_picker("THEME COLOR", st.session_state.theme_color)
        if st.button("SAVE"): st.rerun()

    # --- PAGE: MUSIC ---
    elif st.session_state.current_page == "MUSIC":
        st.markdown("<h2 class='neon-title'>🎧 DJ STATION</h2>", unsafe_allow_html=True)
        all_songs = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
        if not all_songs: st.error("No .mp3 files found.")
        else:
            s_a = st.selectbox("DECK A", ["-- Select --"] + all_songs, key="sa")
            s_b = st.selectbox("DECK B", ["-- Select --"] + all_songs, key="sb")
            
            def get_b64(f): 
                if f == "-- Select --": return ""
                return base64.b64encode(open(f, "rb").read()).decode()
            
            d_a, d_b = get_b64(s_a), get_b64(s_b)
            mixer_html = f"""
            <div style="background:#000; border:2px solid {st.session_state.theme_color}; border-radius:20px; padding:15px;">
                <canvas id="v" style="width:100%; height:150px; background:#050505; border-radius:10px;"></canvas>
                <button onclick="play()" style="width:100%; margin-top:10px; padding:15px; background:linear-gradient(45deg, {st.session_state.theme_color}, #FF00DE); border:none; border-radius:10px; color:white; font-weight:bold;">START MIX</button>
                <audio id="audA" src="data:audio/mp3;base64,{d_a}"></audio>
                <audio id="audB" src="data:audio/mp3;base64,{d_b}"></audio>
                <script>
                    const a=document.getElementById('audA'), b=document.getElementById('audB');
                    let ctx, ans;
                    function play() {{
                        if(!ctx) {{
                            ctx=new(window.AudioContext||window.webkitAudioContext)(); ans=ctx.createAnalyser();
                            const sA=ctx.createMediaElementSource(a), sB=ctx.createMediaElementSource(b);
                            const gA=ctx.createGain(), gB=ctx.createGain();
                            sA.connect(gA).connect(ans); sB.connect(gB).connect(ans); ans.connect(ctx.destination);
                            window.gs={{A:gA, B:gB}};
                        }}
                        a.play(); window.gs.A.gain.value=1; window.gs.B.gain.value=0; loop();
                    }}
                    function loop() {{
                        requestAnimationFrame(loop); const d=new Uint8Array(ans.frequencyBinCount); ans.getByteFrequencyData(d);
                        const c=document.getElementById('v').getContext('2d'); c.clearRect(0,0,300,150);
                        for(let i=0;i<d.length;i++) {{ c.fillStyle=`hsl(${{i*5}},100%,50%)`; c.fillRect(i*2, 150-(d[i]/2), 1, d[i]/2); }}
                    }}
                </script>
            </div>"""
            components.html(mixer_html, height=250)

    # --- PAGE: GPS & CHAT ---
    elif st.session_state.current_page == "GPS":
        st.markdown("<h2 class='neon-title'>🛰️ COMMAND CENTER</h2>", unsafe_allow_html=True)
        loc = get_geolocation()
        my_lat, my_lon = (loc['coords']['latitude'], loc['coords']['longitude']) if loc else (13.7367, 100.5231)

        tab1, tab2, tab3 = st.tabs(["📡 RADAR VIEW", "🌐 PUBLIC CHAT", "🔐 SECURE LINE"])

        with tab1: # GPS Map
            m = folium.Map(location=[my_lat, my_lon], zoom_start=18, 
                          tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr='Google Hybrid')
            folium.Marker([my_lat, my_lon], popup="YOU", icon=folium.Icon(color='red')).add_to(m)
            st_folium(m, width="100%", height=400, key="radar_map")
            if st.button("📡 BROADCAST POSITION", use_container_width=True):
                db.reference(f'users/{st.session_state.user_name}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
                st.success("Broadcasted!")

        with tab2: # Chat
            with st.form("chat_form", clear_on_submit=True):
                msg = st.text_input("Message...")
                if st.form_submit_button("SEND"):
                    if msg:
                        db.reference('public_chat').push({'u': st.session_state.user_name, 'm': msg, 'ts': time.time()})
                        st.rerun()
            
            st.write("---")
            data = db.reference('public_chat').order_by_key().limit_to_last(10).get()
            if data:
                for k, v in reversed(list(data.items())):
                    st.write(f"**{v.get('u')}**: {v.get('m')}")

    elif st.session_state.current_page == "DECODER":
        st.markdown("<h2 class='neon-title'>COSMIC DECODER</h2>", unsafe_allow_html=True)
        st.write("รหัสฐานวัน:", round(date.today().isoweekday() * 1.618, 4))

    elif st.session_state.current_page == "SENSOR":
        st.markdown("<h2 class='neon-title'>SENSOR LAB</h2>", unsafe_allow_html=True)
        st.info("System scanning...")
