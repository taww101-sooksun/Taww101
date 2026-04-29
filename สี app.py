import streamlit as st
import streamlit.components.v1 as components
import os
import base64
import math
import time
import folium
from streamlit_folium import st_folium
from datetime import datetime, date

# --- [ 1. INITIAL SETUP ] ---
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00ff41"
if 'user_name' not in st.session_state:
    st.session_state.user_name = "AGENT_X"
if 'current_page' not in st.session_state:
    st.session_state.current_page = "MAIN MENU"

st.set_page_config(page_title="SYNAPSE X", layout="wide")

# CSS Style
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

# --- [ 2. INTERFACE LOGIC ] ---

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
    if st.button("⬅️ BACK TO MENU"):
        go_to("MAIN MENU")
    st.write("---")

    # --- PAGE: SETTINGS ---
    if st.session_state.current_page == "SETTINGS":
        st.markdown(f"<h2 class='neon-title'>SETTINGS</h2>", unsafe_allow_html=True)
        st.session_state.user_name = st.text_input("AGENT NAME", value=st.session_state.user_name)
        st.session_state.theme_color = st.color_picker("THEME COLOR", st.session_state.theme_color)
        if st.button("SAVE"): st.rerun()

    # --- PAGE: MUSIC (กราฟบน รายการล่าง) ---
    elif st.session_state.current_page == "MUSIC":
        st.markdown(f"<h2 class='neon-title'>🎧 DJ STATION</h2>", unsafe_allow_html=True)
        all_songs = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
        if not all_songs: st.error("No .mp3 files found.")
        else:
            s_a = st.session_state.get('sa', "-- Select --")
            s_b = st.session_state.get('sb', "-- Select --")
            def get_b64(f): return base64.b64encode(open(f, "rb").read()).decode() if f != "-- Select --" else ""
            d_a, d_b = get_b64(s_a), get_b64(s_b)
            
            mixer_html = f"""
            <div style="background:#000; border:2px solid {st.session_state.theme_color}; border-radius:20px; padding:15px;">
                <canvas id="v" style="width:100%; height:150px; background:#050505; border-radius:10px;"></canvas>
                <button onclick="play()" style="width:100%; margin-top:10px; padding:15px; background:linear-gradient(45deg, {st.session_state.theme_color}, #FF00DE); border:none; border-radius:10px; color:white; font-weight:bold;">START MIX</button>
                <audio id="audA" src="data:audio/mp3;base64,{d_a}"></audio>
                <audio id="audB" src="data:audio/mp3;base64,{d_b}"></audio>
                <script>
                    const a=document.getElementById('audA'), b=document.getElementById('audB');
                    let ctx, ans, active='A';
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
                        if(a.duration-a.currentTime<7 && b.paused) {{ b.play(); window.gs.A.gain.linearRampToValueAtTime(0, ctx.currentTime+6); window.gs.B.gain.linearRampToValueAtTime(1, ctx.currentTime+6); }}
                    }}
                </script>
            </div>"""
            components.html(mixer_html, height=250)
            c1, c2 = st.columns(2)
            with c1: st.selectbox("DECK A", ["-- Select --"] + all_songs, key="sa")
            with c2: st.selectbox("DECK B", ["-- Select --"] + all_songs, key="sb")
            if st.button("🔄 UPDATE"): st.rerun()

    # --- PAGE: GPS & CHAT (รวมร่าง) ---
    elif st.session_state.current_page == "GPS":
        st.markdown(f"<h2 class='neon-title'>🛰️ COMMAND CENTER</h2>", unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["📡 RADAR", "🌐 PUBLIC", "🔐 SECURE"])
        
        with t1: # RADAR
            lat, lon = 13.7367, 100.5231
            m = folium.Map(location=[lat, lon], zoom_start=18, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr='Google')
            folium.Marker([lat, lon], icon=folium.Icon(color='red')).add_to(m)
            st_folium(m, width="100%", height=400)
            if st.button("📡 BROADCAST"): st.success("Position Shared")

        with t2: # PUBLIC CHAT
            with st.form("pub", clear_on_submit=True):
                m = st.text_input("Message")
                f = st.file_uploader("Media", type=['jpg','png','mp4'])
                if st.form_submit_button("📢 SEND"): st.toast("Sent to Public Hub")
            st.write("---")
            st.caption("Intelligence Feed is Active...")

        with t3: # SECURE CHAT
            target = st.selectbox("TARGET AGENT", ["-- Select --", "Agent_Alpha", "Agent_Beta"])
            if target != "-- Select --":
                with st.form("sec", clear_on_submit=True):
                    sm = st.text_input(f"Lock on {target}")
                    sf = st.file_uploader("Secure File", type=['jpg','png','mp4'])
                    if st.form_submit_button("🚀 LOCK & SEND"): st.success("Encrypted")

    # --- PAGE: DECODER ---
    elif st.session_state.current_page == "DECODER":
        st.markdown(f"<h2 class='neon-title'>COSMIC DECODER</h2>", unsafe_allow_html=True)
        st.write("รหัสฐานวัน:", round(date.today().isoweekday() * 1.618, 4))
        st.write("รหัสจันทรคติ: 29.53")

    # --- PAGE: SENSOR ---
    elif st.session_state.current_page == "SENSOR":
        st.markdown(f"<h2 class='neon-title'>SENSOR LAB</h2>", unsafe_allow_html=True)
        st.info("System scanning for G-Force vibrations...")
