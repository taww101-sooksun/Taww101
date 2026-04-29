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
    # --- หน้า MUSIC (DJ STATION V.4 - Visualizer Top) ---
    elif st.session_state.current_page == "MUSIC":
        st.markdown("<h2 class='neon-title'>🎧 SYNAPSE ANALYZER</h2>", unsafe_allow_html=True)
        
        # 1. เตรียมข้อมูลเพลง
        all_songs = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
        
        if not all_songs:
            st.error("⚠️ ไม่พบไฟล์ .mp3 ในระบบ")
        else:
            # ดึงเพลงที่เลือก (ถ้ามี)
            song_a = st.session_state.get('sa', "-- Select --")
            song_b = st.session_state.get('sb', "-- Select --")

            def get_audio_base64(song_name):
                if song_name != "-- Select --":
                    with open(song_name, "rb") as f:
                        return base64.b64encode(f.read()).decode()
                return ""

            data_a = get_audio_base64(song_a)
            data_b = get_audio_base64(song_b)

            # 2. เครื่องเล่นเพลง (HTML/JS) - วาง Visualizer ไว้บนสุด
            mixer_html = f"""
            <div style="background: #000; border: 2px solid {st.session_state.theme_color}; border-radius: 20px; padding: 15px; font-family: 'Orbitron', sans-serif; color: white;">
                
                <div style="text-align: center; margin-bottom: 5px;"><small style="color:{st.session_state.theme_color}; letter-spacing:2px;">FREQUENCY SPECTRUM</small></div>
                <canvas id="scope" style="width: 100%; height: 180px; background: #050505; border-radius: 15px; border: 1px solid #222; box-shadow: inset 0 0 20px rgba(0,255,0,0.1);"></canvas>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 15px;">
                    <div id="deckA" style="border: 1px solid {st.session_state.theme_color}; padding: 10px; border-radius: 12px; text-align: center;">
                        <div style="display: flex; justify-content: space-between; font-size: 10px; color: {st.session_state.theme_color};">
                            <span id="curA">00:00</span><span>DECK A</span>
                        </div>
                        <div style="height: 4px; background: #222; border-radius: 10px; margin-top: 5px; overflow: hidden;">
                            <div id="barA" style="height: 100%; width: 0%; background: {st.session_state.theme_color};"></div>
                        </div>
                    </div>
                    <div id="deckB" style="border: 1px solid #FF00DE; padding: 10px; border-radius: 12px; text-align: center;">
                        <div style="display: flex; justify-content: space-between; font-size: 10px; color: #FF00DE;">
                            <span id="curB">00:00</span><span>DECK B</span>
                        </div>
                        <div style="height: 4px; background: #222; border-radius: 10px; margin-top: 5px; overflow: hidden;">
                            <div id="barB" style="height: 100%; width: 0%; background: #FF00DE;"></div>
                        </div>
                    </div>
                </div>

                <button onclick="startMix()" style="width: 100%; margin-top: 15px; padding: 18px; background: linear-gradient(45deg, {st.session_state.theme_color}, #FF00DE); border: none; border-radius: 12px; color: white; font-weight: bold; cursor: pointer; text-transform: uppercase; letter-spacing: 2px;">🔥 ACTIVATE ENGINE</button>
                <div id="status" style="font-size: 9px; text-align: center; margin-top: 8px; color: #444;">SYSTEM READY</div>

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
                            const gA = ctx.createGain(); const gB = ctx.createGain();
                            sA.connect(gA).connect(analyser);
                            sB.connect(gB).connect(analyser);
                            analyser.connect(ctx.destination);
                            window.gains = {{ A: gA, B: gB }};
                            render();
                        }}
                    }}

                    function render() {{
                        const can = document.getElementById('scope');
                        const c = can.getContext('2d');
                        analyser.fftSize = 256;
                        const data = new Uint8Array(analyser.frequencyBinCount);

                        function draw() {{
                            requestAnimationFrame(draw);
                            analyser.getByteFrequencyData(data);
                            c.clearRect(0, 0, can.width, can.height);
                            let bw = (can.width / data.length) * 2;
                            let x = 0;
                            for(let i=0; i<data.length; i++) {{
                                let h = (data[i]/255) * can.height;
                                // สีสันจัดจ่านสไตล์รุ้งสะบัด
                                c.fillStyle = `hsl(${{(i*4 + Date.now()/15)%360}}, 100%, 50%)`;
                                c.fillRect(x, can.height - h, bw - 1, h);
                                x += bw;
                            }}
                            if(isPlaying) updateLogic();
                        }}
                        draw();
                    }}

                    function startMix() {{
                        if(!audA.src || !audB.src) return alert("อาจารย์ครับ! เลือกเพลงที่รายการด้านล่างก่อน!");
                        initAudio();
                        audA.play();
                        window.gains.A.gain.value = 1;
                        window.gains.B.gain.value = 0;
                        isPlaying = true;
                        document.getElementById('status').innerText = "ENGINE RUNNING: DECK A";
                    }}

                    function updateLogic() {{
                        const cur = active === 'A' ? audA : audB;
                        const next = active === 'A' ? audB : audA;
                        const rem = cur.duration - cur.currentTime;

                        document.getElementById('curA').innerText = fmt(audA.currentTime);
                        document.getElementById('curB').innerText = fmt(audB.currentTime);
                        document.getElementById('barA').style.width = (audA.currentTime/audA.duration*100) + "%";
                        document.getElementById('barB').style.width = (audB.currentTime/audB.duration*100) + "%";

                        if (rem < 7 && next.paused) {{
                            next.currentTime = 0;
                            next.play();
                            let now = ctx.currentTime;
                            window.gains[active].gain.linearRampToValueAtTime(0, now + 6);
                            window.gains[active==='A'?'B':'A'].gain.linearRampToValueAtTime(1, now + 6);
                            active = (active === 'A' ? 'B' : 'A');
                            document.getElementById('status').innerText = "AUTO-CROSSFADING TO DECK " + active;
                        }}
                    }}
                    function fmt(s) {{ return new Date(s * 1000).toISOString().substr(14, 5); }}
                </script>
            </div>
            """
            components.html(mixer_html, height=520)

            # 3. รายการเพลง (วางไว้ข้างล่างเครื่องเล่น)
            st.markdown("<div style='margin-top:20px; border-top:1px solid #333; padding-top:10px;'></div>", unsafe_allow_html=True)
            st.write("📂 **SELECT YOUR TRACKS**")
            col_sel_a, col_sel_b = st.columns(2)
            with col_sel_a:
                st.selectbox("💿 DECK A (LEFT)", ["-- Select --"] + all_songs, key="sa")
            with col_sel_b:
                st.selectbox("💿 DECK B (RIGHT)", ["-- Select --"] + all_songs, key="sb")
            
            if st.button("🔄 RELOAD TRACKS"):
                st.rerun()



    elif st.session_state.current_page == "GPS":
        st.markdown("<h2 class='neon-title'>GPS RADAR</h2>", unsafe_allow_html=True)
        # ใส่โค้ด GPS ของคุณที่นี่

    elif st.session_state.current_page == "SENSOR":
        st.markdown("<h2 class='neon-title'>SENSOR LAB</h2>", unsafe_allow_html=True)
        # ใส่โค้ด Sensor ของคุณที่นี่
