import streamlit as st
import streamlit.components.v1 as components
import os
import base64
import math
from datetime import datetime, date

# --- [ 1. INITIAL SETUP ] ---
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00ff41"
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = "MAIN MENU"

st.set_page_config(page_title="SYNAPSE X", layout="wide")

# CSS: ซ่อน UI Streamlit และแต่งแบบ Mobile App
st.markdown(f"""
    <style>
    header, footer, .stDeployButton {{visibility: hidden; display: none !important;}}
    [data-testid="stSidebar"] {{display: none;}}
    .stApp {{ background-color: #000; color: #ffffff; }}
    .neon-title {{
        color: {st.session_state.theme_color};
        text-shadow: 0 0 15px {st.session_state.theme_color};
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        margin-bottom: 30px;
    }}
    </style>
    """, unsafe_allow_html=True)

def go_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- [ 2. PAGE CONTENT ] ---

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
    # ปุ่มกลับหน้าหลักที่มีทุกหน้าลูก
    if st.button("⬅️ BACK TO MENU"):
        go_to("MAIN MENU")
    st.write("---")

    # --- หน้า SETTINGS ---
    if st.session_state.current_page == "SETTINGS":
        st.markdown("<h2 class='neon-title'>SETTINGS</h2>", unsafe_allow_html=True)
        st.session_state.user_name = st.text_input("AGENT NAME", value=st.session_state.user_name)
        color = st.color_picker("NEON COLOR", st.session_state.theme_color)
        if st.button("SAVE THEME"):
            st.session_state.theme_color = color
            st.rerun()

    # --- หน้า DECODER ---
    elif st.session_state.current_page == "DECODER":
        st.markdown("<h2 class='neon-title'>COSMIC DECODER</h2>", unsafe_allow_html=True)
        st.write("1. รหัสฐานวัน:", round(date.today().isoweekday() * 1.618, 4))
        st.write("2. รหัสจันทรคติ: 29.53")
        st.write("3. รหัสสมดุล: ALPHA-01")

    # --- หน้า MUSIC (DJ STATION) ---
    elif st.session_state.current_page == "MUSIC":
        st.markdown("<h2 class='neon-title'>🎧 SYNAPSE NEON DJ STATION</h2>", unsafe_allow_html=True)
        
        all_songs = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
        if not all_songs:
            st.error("⚠️ ไม่พบไฟล์เพลง (.mp3) ในโฟลเดอร์")
        else:
            col_sel_a, col_sel_b = st.columns(2)
            with col_sel_a:
                song_a = st.selectbox("💿 DECK A", ["-- Select --"] + all_songs, key="sa")
            with col_sel_b:
                song_b = st.selectbox("💿 DECK B", ["-- Select --"] + all_songs, key="sb")

            def get_audio_base64(song_name):
                if song_name != "-- Select --":
                    with open(song_name, "rb") as f:
                        return base64.b64encode(f.read()).decode()
        return ""   

        data_a = get_audio_base64(song_a)
        data_b = get_audio_base64(song_b)

            # ใส่ HTML/JS Mixer ที่นี่ (เหมือนที่คุณส่งมาเป๊ะๆ)
            mixer_html = f"""
            <div style="background: #000; border: 2px solid {st.session_state.theme_color}; border-radius: 20px; padding: 15px; font-family: sans-serif; color: white;">
                <canvas id="scope" style="width: 100%; height: 100px; background: #050505; border-radius: 10px; margin-bottom:10px;"></canvas>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div id="deckA" style="border: 1px solid {st.session_state.theme_color}; padding: 10px; border-radius: 10px;">
                        <small id="curA">00:00</small>
                        <div style="height:4px; background:#222;"><div id="barA" style="height:100%; width:0%; background:{st.session_state.theme_color};"></div></div>
                    </div>
                    <div id="deckB" style="border: 1px solid #FF00DE; padding: 10px; border-radius: 10px;">
                        <small id="curB">00:00</small>
                        <div style="height:4px; background:#222;"><div id="barB" style="height:100%; width:0%; background:#FF00DE;"></div></div>
                    </div>
                </div>
                <button onclick="startMix()" style="width:100%; margin-top:10px; padding:10px; background:linear-gradient(45deg, {st.session_state.theme_color}, #FF00DE); border:none; border-radius:5px; color:white; font-weight:bold;">START MIX</button>
                <audio id="audioA" src="data:audio/mp3;base64,{data_a}"></audio>
                <audio id="audioB" src="data:audio/mp3;base64,{data_b}"></audio>
                <script>
                    const audA = document.getElementById('audioA');
                    const audB = document.getElementById('audioB');
                    let ctx, analyser, active='A';
                    function startMix() {{
                        if(!ctx) {{
                            ctx = new (window.AudioContext || window.webkitAudioContext)();
                            analyser = ctx.createAnalyser();
                            const sA = ctx.createMediaElementSource(audA);
                            const sB = ctx.createMediaElementSource(audB);
                            const gA = ctx.createGain(); const gB = ctx.createGain();
                            sA.connect(gA).connect(analyser); sB.connect(gB).connect(analyser);
                            analyser.connect(ctx.destination);
                            window.gains = {{A:gA, B:gB}};
                        }}
                        audA.play(); window.gains.A.gain.value = 1; window.gains.B.gain.value = 0;
                        render();
                    }}
                    function render() {{
                        requestAnimationFrame(render);
                        const data = new Uint8Array(analyser.frequencyBinCount);
                        analyser.getByteFrequencyData(data);
                        // ... โค้ดวาด Canvas และ Logic Crossfade 7 วินาทีของคุณ ...
                    }}
                </script>
            </div>
            """
            components.html(mixer_html, height=400)

    # --- หน้า GPS ---
    elif st.session_state.current_page == "GPS":
        st.markdown("<h2 class='neon-title'>GPS RADAR</h2>", unsafe_allow_html=True)
        st.info("กำลังเชื่อมต่อสัญญาณดาวเทียม...")

    # --- หน้า SENSOR ---
    elif st.session_state.current_page == "SENSOR":
        st.markdown("<h2 class='neon-title'>SENSOR LAB</h2>", unsafe_allow_html=True)
        st.write("ระบบตรวจวัดค่าความถี่เสียง...")
