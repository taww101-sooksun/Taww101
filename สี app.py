import streamlit as st
import streamlit.components.v1 as components
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

# CSS: ซ่อนทุกอย่างของ Streamlit และแต่ง UI ใหม่ให้เหมือนแอปมือถือ
st.markdown(f"""
    <style>
    header, footer, .stDeployButton {{visibility: hidden; display: none !important;}}
    [data-testid="stSidebar"] {{display: none;}} /* ปิด Sidebar ไปเลย */
    
    .stApp {{ background-color: #000; color: #ffffff; }}
    
    .neon-btn {{
        background-color: #111;
        border: 2px solid {st.session_state.theme_color};
        color: {st.session_state.theme_color};
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 10px;
        cursor: pointer;
        font-family: 'Orbitron', sans-serif;
        box-shadow: 0 0 10px {st.session_state.theme_color};
    }}
    
    .neon-title {{
        color: {st.session_state.theme_color};
        text-shadow: 0 0 15px {st.session_state.theme_color};
        text-align: center;
        font-family: 'Orbitron', sans-serif;
        margin-bottom: 30px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- [ 2. NAVIGATION LOGIC ] ---
def go_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- [ 3. PAGE CONTENT ] ---

# หน้าเมนูหลัก (ใช้แทน Sidebar)
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

# หน้าลูก (Sub-pages)
else:
    # ปุ่มกดกลับเมนูหลัก (Home Button)
    if st.button("⬅️ BACK TO MENU"):
        go_to("MAIN MENU")
    st.write("---")

    if st.session_state.current_page == "SETTINGS":
        st.markdown("<h2 class='neon-title'>SETTINGS</h2>", unsafe_allow_html=True)
        st.session_state.user_name = st.text_input("AGENT NAME", value=st.session_state.user_name)
        color = st.color_picker("NEON COLOR", st.session_state.theme_color)
        if st.button("SAVE THEME"):
            st.session_state.theme_color = color
            st.rerun()

    elif st.session_state.current_page == "DECODER":
        st.markdown("<h2 class='neon-title'>COSMIC DECODER</h2>", unsafe_allow_html=True)
        # ฟังก์ชันคำนวณ 3 หัวข้อ (เดิม)
        st.write("1. รหัสฐานวัน:", round(date.today().isoweekday() * 1.618, 4))
        st.write("2. รหัสจันทรคติ: 29.53")
        st.write("3. รหัสสมดุล: ALPHA-01")
    elif menu == "🎧 ROOM 1: NEON MUSIC":
        st.markdown("<h2 class='neon-text'>🎧 SYNAPSE NEON DJ STATION</h2>", unsafe_allow_html=True)
    
    # ดึงรายชื่อไฟล์ MP3 จากโฟลเดอร์เดียวกัน
    all_songs = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
    
    if not all_songs:
        st.error("⚠️ ไม่พบไฟล์เพลง (.mp3) ใน Directory ของคุณ")
        st.info("กรุณาอัปโหลดไฟล์เพลงไว้ที่เดียวกับไฟล์โปรแกรมบน GitHub")
    else:
        st.write("เลือกเพลงสำหรับ DECK A และ B เพื่อเริ่มระบบ Auto-Mix")
        col_sel_a, col_sel_b = st.columns(2)
        
        with col_sel_a:
            song_a = st.selectbox("💿 DECK A (LEFT)", ["-- Select Song --"] + all_songs, key="sa")
        with col_sel_b:
            song_b = st.selectbox("💿 DECK B (RIGHT)", ["-- Select Song --"] + all_songs, key="sb")

        # ฟังก์ชันแปลงไฟล์เป็น Base64 เพื่อส่งเข้า HTML/JS
        def get_audio_base64(song_name):
            if song_name != "-- Select Song --":
                with open(song_name, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            return ""

        data_a = get_audio_base64(song_a)
        data_b = get_audio_base64(song_b)

        # --- ส่วนของ HTML/JS Visualizer + Auto-Mix ---
        mixer_html = f"""
        <div style="background: #000; border: 2px solid {st.session_state.theme_color}; border-radius: 20px; padding: 15px; font-family: 'Orbitron', sans-serif; color: white;">
            <canvas id="scope" style="width: 100%; height: 120px; background: #050505; border-radius: 15px; border: 1px solid #222; margin-bottom: 15px;"></canvas>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div id="deckA" style="border: 1px solid {st.session_state.theme_color}; padding: 10px; border-radius: 15px; text-align: center; transition: 0.5s;">
                    <div style="display: flex; justify-content: space-between; font-size: 10px; color: {st.session_state.theme_color};">
                        <span id="curA">00:00</span><span id="labelA">DECK A</span><span id="remA">-00:00</span>
                    </div>
                    <div style="height: 6px; background: #222; border-radius: 10px; margin: 10px 0; overflow: hidden;">
                        <div id="barA" style="height: 100%; width: 0%; background: linear-gradient(90deg, {st.session_state.theme_color}, #fff);"></div>
                    </div>
                </div>

                <div id="deckB" style="border: 1px solid #FF00DE; padding: 10px; border-radius: 15px; text-align: center; transition: 0.5s;">
                    <div style="display: flex; justify-content: space-between; font-size: 10px; color: #FF00DE;">
                        <span id="curB">00:00</span><span id="labelB">DECK B</span><span id="remB">-00:00</span>
                    </div>
                    <div style="height: 6px; background: #222; border-radius: 10px; margin: 10px 0; overflow: hidden;">
                        <div id="barB" style="height: 100%; width: 0%; background: linear-gradient(90deg, #FF00DE, #fff);"></div>
                    </div>
                </div>
            </div>

            <button onclick="startMix()" style="width: 100%; margin-top: 15px; padding: 15px; background: linear-gradient(45deg, {st.session_state.theme_color}, #FF00DE); border: none; border-radius: 10px; color: white; font-weight: bold; cursor: pointer; letter-spacing: 2px;">🔥 START AUTO-MIX ENGINE</button>
            <div id="status" style="font-size: 10px; text-align: center; mt-3; color: #555; margin-top: 10px;">READY TO MIX</div>

            <audio id="audioA" src="data:audio/mp3;base64,{data_a}"></audio>
            <audio id="audioB" src="data:audio/mp3;base64,{data_b}"></audio>

            <script>
                const audA = document.getElementById('audioA');
                const audB = document.getElementById('audioB');
                let ctx, analyser, active = 'A', isPlaying = false;

                function initAudio() {{
                    if (!ctx) {{
                        ctx = new (window.AudioContext || window.webkitAudioContext)();
                        analyser = ctx.createAnalyser();
                        const sA = ctx.createMediaElementSource(audA);
                        const sB = ctx.createMediaElementSource(audB);
                        const gainA = ctx.createGain(); const gainB = ctx.createGain();
                        
                        sA.connect(gainA).connect(analyser);
                        sB.connect(gainB).connect(analyser);
                        analyser.connect(ctx.destination);
                        
                        window.gainNodes = {{ A: gainA, B: gainB }};
                        renderVisualizer();
                    }}
                }}

                function renderVisualizer() {{
                    const can = document.getElementById('scope');
                    const c = can.getContext('2d');
                    analyser.fftSize = 128;
                    const data = new Uint8Array(analyser.frequencyBinCount);

                    function draw() {{
                        requestAnimationFrame(draw);
                        analyser.getByteFrequencyData(data);
                        c.clearRect(0, 0, can.width, can.height);
                        let bw = (can.width / data.length) * 2.5;
                        let x = 0;
                        for(let i=0; i<data.length; i++) {{
                            let h = (data[i]/255) * can.height;
                            c.fillStyle = `hsl(${{(i*5 + Date.now()/20)%360}}, 100%, 50%)`;
                            c.fillRect(x, can.height - h, bw - 1, h);
                            x += bw;
                        }}
                        updateLogic();
                    }}
                    draw();
                }}

                function startMix() {{
                    if(!audA.src || !audB.src) return alert("เลือกเพลงให้ครบก่อนครับ!");
                    initAudio();
                    audA.play();
                    window.gainNodes.A.gain.value = 1;
                    window.gainNodes.B.gain.value = 0;
                    isPlaying = true;
                    document.getElementById('deckA').style.boxShadow = "0 0 20px {st.session_state.theme_color}";
                }}

                function updateLogic() {{
                    if(!isPlaying) return;
                    const cur = active === 'A' ? audA : audB;
                    const next = active === 'A' ? audB : audA;
                    const rem = cur.duration - cur.currentTime;

                    // UI Updates
                    updateUI('A', audA); updateUI('B', audB);

                    // AUTO CROSSFADE: เมื่อเหลือ 7 วินาทีสุดท้าย
                    if (rem > 0 && rem < 7 && next.paused) {{
                        next.currentTime = 0;
                        next.play();
                        let now = ctx.currentTime;
                        window.gainNodes[active].gain.linearRampToValueAtTime(0, now + 6);
                        window.gainNodes[active === 'A' ? 'B' : 'A'].gain.linearRampToValueAtTime(1, now + 6);
                        
                        document.getElementById('status').innerText = "MIXING TO DECK " + (active === 'A' ? 'B' : 'A');
                        setTimeout(() => {{ 
                            active = (active === 'A' ? 'B' : 'A'); 
                            document.getElementById('deckA').style.boxShadow = active === 'A' ? "0 0 20px {st.session_state.theme_color}" : "none";
                            document.getElementById('deckB').style.boxShadow = active === 'B' ? "0 0 20px #FF00DE" : "none";
                        }}, 6000);
                    }}
                }}

                function updateUI(id, aud) {{
                    const fmt = s => new Date(s * 1000).toISOString().substr(14, 5);
                    document.getElementById('cur'+id).innerText = fmt(aud.currentTime);
                    if(aud.duration) {{
                        document.getElementById('rem'+id).innerText = "-" + fmt(aud.duration - aud.currentTime);
                        document.getElementById('bar'+id).style.width = (aud.currentTime / aud.duration * 100) + "%";
                    }}
                }}
            </script>
        </div>
        """
        components.html(mixer_html, height=500)
        st.caption("Tactical Engine: ตรวจพบไฟล์เสียงในระบบ พร้อมสำหรับการ Mix ต่อเนื่อง")

    

    elif st.session_state.current_page == "GPS":
        st.markdown("<h2 class='neon-title'>GPS RADAR</h2>", unsafe_allow_html=True)
        # ใส่โค้ด GPS ของคุณที่นี่

    elif st.session_state.current_page == "SENSOR":
        st.markdown("<h2 class='neon-title'>SENSOR LAB</h2>", unsafe_allow_html=True)
        # ใส่โค้ด Sensor ของคุณที่นี่
