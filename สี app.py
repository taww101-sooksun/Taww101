import streamlit as st
import streamlit.components.v1 as components
import os
import base64
import math
from datetime import datetime, date

# --- [ 1. INITIAL SETUP & THEME ] ---
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00ff41" # สีเขียว Neon เริ่มต้น
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'current_page' not in st.session_state:
    st.session_state.current_page = "MAIN MENU"

st.set_page_config(page_title="SYNAPSE X", layout="wide")

# CSS: กู้คืนความหล่อแบบแอปมือถือ ซ่อนทุกอย่างของ Streamlit
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    header, footer, .stDeployButton {{visibility: hidden; display: none !important;}}
    [data-testid="stSidebar"] {{display: none;}}
    
    .stApp {{ 
        background-color: #000; 
        color: #ffffff; 
        font-family: 'Orbitron', sans-serif;
    }}
    
    .neon-title {{
        color: {st.session_state.theme_color};
        text-shadow: 0 0 15px {st.session_state.theme_color};
        text-align: center;
        margin-bottom: 25px;
    }}
    
    /* สไตล์ปุ่มในหน้าเมนูหลัก */
    div.stButton > button {{
        background-color: #111;
        border: 2px solid {st.session_state.theme_color};
        color: {st.session_state.theme_color};
        border-radius: 15px;
        padding: 20px;
        font-weight: bold;
        transition: 0.3s;
        box-shadow: 0 0 10px rgba(0,255,0,0.1);
    }}
    div.stButton > button:hover {{
        background-color: {st.session_state.theme_color};
        color: black;
        box-shadow: 0 0 20px {st.session_state.theme_color};
    }}
    </style>
    """, unsafe_allow_html=True)

# ฟังก์ชันสำหรับเปลี่ยนหน้า
def go_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- [ 2. MAIN INTERFACE ] ---

# A. หน้าเมนูหลัก (MAIN MENU)
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
    st.caption(f"AGENT: {st.session_state.user_name if st.session_state.user_name else 'Unknown'} | 'อยู่นิ่งๆ ไม่เจ็บตัว'")

# B. หน้าลูกต่างๆ (SUB-PAGES)
else:
    # ปุ่ม Back สำหรับทุกหน้า
    if st.button("⬅️ BACK TO MENU"):
        go_to("MAIN MENU")
    st.write("---")

    # 1. หน้า SETTINGS
    if st.session_state.current_page == "SETTINGS":
        st.markdown(f"<h2 class='neon-title' style='color:{st.session_state.theme_color}'>SETTINGS</h2>", unsafe_allow_html=True)
        st.session_state.user_name = st.text_input("ระบุชื่อ Agent ของคุณ", value=st.session_state.user_name)
        new_color = st.color_picker("เลือกสี Neon ของคุณ", st.session_state.theme_color)
        if st.button("บันทึกการตั้งค่า"):
            st.session_state.theme_color = new_color
            st.rerun()

    # 2. หน้า MUSIC (ไฮไลต์: กราฟบน รายการล่าง)
    elif st.session_state.current_page == "MUSIC":
        st.markdown(f"<h2 class='neon-title' style='color:{st.session_state.theme_color}'>🎧 DJ STATION</h2>", unsafe_allow_html=True)
        
        # ดึงไฟล์เพลงจาก Directory
        all_songs = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
        
        if not all_songs:
            st.error("⚠️ ไม่พบไฟล์ .mp3 ใน Directory")
        else:
            # เลือกเพลง
            song_a = st.session_state.get('sa', "-- Select --")
            song_b = st.session_state.get('sb', "-- Select --")

            def get_base64_audio(file):
                if file != "-- Select --":
                    with open(file, "rb") as f:
                        return base64.b64encode(f.read()).decode()
                return ""

            data_a = get_base64_audio(song_a)
            data_b = get_base64_audio(song_b)

            # HTML/JS: Visualizer (บน) + Deck Control
            mixer_html = f"""
            <div style="background:#000; border:2px solid {st.session_state.theme_color}; border-radius:20px; padding:15px; color:white; font-family:sans-serif;">
                <canvas id="scope" style="width:100%; height:160px; background:#050505; border-radius:15px; border:1px solid #222;"></canvas>
                
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:15px;">
                    <div id="deckA" style="border:1px solid {st.session_state.theme_color}; padding:10px; border-radius:12px; text-align:center;">
                        <small id="curA" style="color:{st.session_state.theme_color};">00:00</small>
                        <div style="height:4px; background:#222; margin-top:5px;"><div id="barA" style="height:100%; width:0%; background:{st.session_state.theme_color};"></div></div>
                    </div>
                    <div id="deckB" style="border:1px solid #FF00DE; padding:10px; border-radius:12px; text-align:center;">
                        <small id="curB" style="color:#FF00DE;">00:00</small>
                        <div style="height:4px; background:#222; margin-top:5px;"><div id="barB" style="height:100%; width:0%; background:#FF00DE;"></div></div>
                    </div>
                </div>

                <button onclick="startMix()" style="width:100%; margin-top:15px; padding:15px; background:linear-gradient(45deg, {st.session_state.theme_color}, #FF00DE); border:none; border-radius:10px; color:white; font-weight:bold; cursor:pointer;">🔥 START AUTO-MIX</button>
                
                <audio id="audioA" src="data:audio/mp3;base64,{data_a}"></audio>
                <audio id="audioB" src="data:audio/mp3;base64,{data_b}"></audio>

                <script>
                    const audA = document.getElementById('audioA');
                    const audB = document.getElementById('audioB');
                    let ctx, analyser, active='A', isPlaying=false;

                    function init() {{
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
                    }}

                    function startMix() {{
                        if(!audA.src || !audB.src) return;
                        init(); audA.play(); 
                        window.gains.A.gain.value = 1; window.gains.B.gain.value = 0;
                        isPlaying = true; render();
                    }}

                    function render() {{
                        requestAnimationFrame(render);
                        const data = new Uint8Array(analyser.frequencyBinCount);
                        analyser.getByteFrequencyData(data);
                        const can = document.getElementById('scope');
                        const c = can.getContext('2d');
                        c.clearRect(0,0,can.width,can.height);
                        let bw = (can.width/data.length)*2.5;
                        for(let i=0; i<data.length; i++) {{
                            let h = (data[i]/255)*can.height;
                            c.fillStyle = `hsl(${{(i*5+Date.now()/20)%360}},100%,50%)`;
                            c.fillRect(i*bw, can.height-h, bw-1, h);
                        }}
                        if(isPlaying) update();
                    }}

                    function update() {{
                        const cur = active==='A'?audA:audB;
                        const next = active==='A'?audB:audA;
                        document.getElementById('curA').innerText = fmt(audA.currentTime);
                        document.getElementById('curB').innerText = fmt(audB.currentTime);
                        document.getElementById('barA').style.width = (audA.currentTime/audA.duration*100)+'%';
                        document.getElementById('barB').style.width = (audB.currentTime/audB.duration*100)+'%';

                        if(cur.duration - cur.currentTime < 7 && next.paused) {{
                            next.currentTime = 0; next.play();
                            let now = ctx.currentTime;
                            window.gains[active].gain.linearRampToValueAtTime(0, now+6);
                            window.gains[active==='A'?'B':'A'].gain.linearRampToValueAtTime(1, now+6);
                            active = (active==='A'?'B':'A');
                        }}
                    }}
                    function fmt(s) {{ return new Date(s*1000).toISOString().substr(14,5); }}
                </script>
            </div>
            """
            components.html(mixer_html, height=450)

            # ส่วนเลือกเพลง (รายการอยู่ข้างล่าง)
            st.write("---")
            st.markdown("### 📂 TRACK SELECTION")
            c1, c2 = st.columns(2)
            with c1:
                st.selectbox("💿 DECK A (LEFT)", ["-- Select --"] + all_songs, key="sa")
            with c2:
                st.selectbox("💿 DECK B (RIGHT)", ["-- Select --"] + all_songs, key="sb")
            if st.button("🔄 UPDATE PLAYLIST"): st.rerun()

    # 3. หน้า DECODER
    elif st.session_state.current_page == "DECODER":
        st.markdown(f"<h2 class='neon-title' style='color:{st.session_state.theme_color}'>COSMIC DECODER</h2>", unsafe_allow_html=True)
        st.write("1. รหัสฐานวัน:", round(date.today().isoweekday() * 1.618, 4))
        st.write("2. รหัสจันทรคติ: 29.53 (Full Moon Cycle)")
        st.write("3. รหัสสมดุลชีวิต: " + str(math.sqrt(618)))

    # 4. หน้า GPS
    elif st.session_state.current_page == "GPS":
        st.markdown(f"<h2 class='neon-title' style='color:{st.session_state.theme_color}'>GPS RADAR</h2>", unsafe_allow_html=True)
        st.warning("⚠️ กำลังรอสัญญาณพิกัด...")

    # 5. หน้า SENSOR
    elif st.session_state.current_page == "SENSOR":
        st.markdown(f"<h2 class='neon-title' style='color:{st.session_state.theme_color}'>SENSOR LAB</h2>", unsafe_allow_html=True)
        st.info("ระบบวัดค่าความสั่นสะเทือน (G-Force)")
