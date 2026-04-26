# =========================================================
# 🛡️ SYNAPSE COMMAND CENTER - FULL POWER v4.2
# =========================================================

import streamlit as st
import base64
import math
from datetime import datetime, date, timedelta

# --- 1. CONFIG & THEME ---
st.set_page_config(page_title="SYNAPSE COMMAND", layout="wide")
primary_neon = "#1F51FF" 

# ฟังก์ชันแปลงรูปโลโก้
def get_base64(file):
    try:
        with open(file, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return None

logo_data = get_base64("logo1.png")

# --- 2. CUSTOM CSS (หนา 2px + โยกสะบัด + ปรับขนาดปุ่ม) ---
st.markdown(f"""
    <style>
    #MainMenu, footer, header {{visibility: hidden;}}
    .stApp {{ background-color: #000; }}

    /* โลโก้เต้น */
    .logo-container {{
        display: flex; justify-content: center;
        animation: logo-dance 3s ease-in-out infinite;
        margin-bottom: 10px;
    }}
    @keyframes logo-dance {{
        0%, 100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-5px); }}
    }}

    /* สโลแกนนีออนโยกสะบัด */
    .neon-wrapper {{
        text-align: center;
        font-family: 'Courier New', monospace;
        font-weight: bold;
        background: linear-gradient(to right, #FF3131, #FFF01F, #00F3FF, #FF44CC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: rainbow-glow 3s linear infinite, slogan-shake 2s ease-in-out infinite;
    }}
    @keyframes slogan-shake {{
        0%, 100% {{ transform: scale(1) rotate(0); }}
        50% {{ transform: scale(1.05) rotate(1deg); }}
    }}
    @keyframes rainbow-glow {{
        0% {{ filter: hue-rotate(0deg) drop-shadow(0 0 10px {primary_neon}); }}
        100% {{ filter: hue-rotate(360deg) drop-shadow(0 0 10px {primary_neon}); }}
    }}

    /* ปุ่ม UNIT ปรับให้เล็กลงและหนาตามสั่ง */
    button[kind="secondary"] {{
        background-color: transparent !important;
        color: {primary_neon} !important;
        border: 2px solid {primary_neon} !important;
        border-radius: 10px !important;
        height: 55px !important;
        font-weight: bold !important;
        font-size: 13px !important;
        box-shadow: 0 0 10px {primary_neon} !important;
        transition: 0.3s;
    }}
    button[kind="secondary"]:hover {{
        background-color: {primary_neon} !important;
        color: #000 !important;
        box-shadow: 0 0 20px {primary_neon} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. HEADER ---
if logo_data:
    st.markdown(f'''<div class="logo-container"><img src="data:image/png;base64,{logo_data}" style="width:120px;"></div>''', unsafe_allow_html=True)

st.markdown(f'''<div class="neon-wrapper"><div style="font-size:28px; letter-spacing:4px;">SYNAPSE</div><div style="font-size:24px; letter-spacing:6px;">อยู่นิ่งๆไม่เจ็บตัว</div></div>''', unsafe_allow_html=True)

# --- 4. NAVIGATION HUB LOGIC ---
if 'page' not in st.session_state: 
    st.session_state.page = "HOME"

if st.session_state.page == "HOME":
    st.write("##")
    num_cols = 4 
    cols = st.columns(num_cols) 
    
    unit_names = {
        1: "🎵 01: DJ STATION", 2: "🛰️ 02: TACTICAL RADAR", 3: "🔮 03: TRUTH LOGIC",
        4: "⚡ 04: SENSOR SCAN", 5: "🎨 05: UI DESIGNER", 6: "💬 06: COMMS CENTER",
        7: "🛠️ 07: DIY MASTER", 8: "🧬 08: SYNAPSE CORE", 9: "📹 09: MEDIA STUDIO",
        10: "💾 10: FIREBASE DB", 11: "🏴 11: COMMAND POST"
    }

    for i in range(1, 12):
        with cols[(i-1) % num_cols]: 
            if st.button(unit_names[i], key=f"u{i}", use_container_width=True):
                st.session_state.page = str(i)
                st.rerun()

# --- 5. UNIT PAGES ---
else:
    # แถบปุ่มกลับ (Back Button)
    if st.button("⬅️ BACK TO HUB"):
        st.session_state.page = "HOME"
        st.rerun()
    
    st.divider()
    page = st.session_state.page

     # ==========================================
    # 🎵 UNIT 01: DJ STATION (MUSIC PLAYER)
    # ==========================================
    if st.session_state.page == "1":
        st.markdown("<h2 class='neon-wrapper' style='font-size:30px;'>🎧 SYNAPSE DJ STATION V.3</h2>", unsafe_allow_html=True)
        
        # 1. ดึงรายชื่อไฟล์เพลงในโฟลเดอร์
        all_songs = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
        
        if not all_songs:
            st.warning("⚠️ ไม่พบไฟล์ .mp3 ในระบบ กรุณาอัปโหลดไฟล์เพลงไว้ในโฟลเดอร์เดียวกับโค้ด")
        else:
            # 2. ส่วนเลือกเพลงแยก 2 ฝั่ง
            col_sel_a, col_sel_b = st.columns(2)
            with col_sel_a:
                song_a = st.selectbox("💿 DECK A (LEFT)", ["-- Select --"] + all_songs, key="sa")
            with col_sel_b:
                song_b = st.selectbox("💿 DECK B (RIGHT)", ["-- Select --"] + all_songs, key="sb")

            # แปลงไฟล์เป็น Base64
            data_a = get_base64(song_a) if song_a != "-- Select --" else ""
            data_b = get_base64(song_b) if song_b != "-- Select --" else ""

            # 3. HTML & JS Mixer Engine (Visualizer + Control)
            mixer_html = f"""
            <div style="background: #000; border: 2px solid {primary_neon}; border-radius: 20px; padding: 15px; font-family: monospace;">
                
                <marquee style="color: {primary_neon}; margin-bottom: 10px;"> 
                    Now Playing Deck A: {song_a} | Deck B: {song_b} --- Synapse High-Res Audio System --- 
                </marquee>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div style="border: 1px solid {primary_neon}; padding: 10px; border-radius: 15px; text-align: center;">
                        <div style="display: flex; justify-content: space-between; font-size: 10px; color: {primary_neon};">
                            <span id="curA">00:00</span><span id="remA">-00:00</span>
                        </div>
                        <canvas id="canvasA" style="width: 100%; height: 60px; background: #111; margin: 5px 0; border-radius:5px;"></canvas>
                        <input type="range" id="volA" min="0" max="1" step="0.01" value="0.7" style="width: 100%; accent-color: {primary_neon};">
                        <div style="margin-top: 10px;">
                            <button onclick="play('A')" style="background:{primary_neon}; border:none; padding:5px 15px; border-radius:5px; color:#000; font-weight:bold; cursor:pointer;">PLAY A</button>
                            <button onclick="pause('A')" style="background:none; border:1px solid {primary_neon}; color:{primary_neon}; padding:5px 15px; border-radius:5px; cursor:pointer;">PAUSE</button>
                        </div>
                    </div>

                    <div style="border: 1px solid #FF44CC; padding: 10px; border-radius: 15px; text-align: center;">
                        <div style="display: flex; justify-content: space-between; font-size: 10px; color: #FF44CC;">
                            <span id="curB">00:00</span><span id="remB">-00:00</span>
                        </div>
                        <canvas id="canvasB" style="width: 100%; height: 60px; background: #111; margin: 5px 0; border-radius:5px;"></canvas>
                        <input type="range" id="volB" min="0" max="1" step="0.01" value="0.7" style="width: 100%; accent-color: #FF44CC;">
                        <div style="margin-top: 10px;">
                            <button onclick="play('B')" style="background:#FF44CC; border:none; padding:5px 15px; border-radius:5px; color:#fff; font-weight:bold; cursor:pointer;">PLAY B</button>
                            <button onclick="pause('B')" style="background:none; border:1px solid #FF44CC; color:#FF44CC; padding:5px 15px; border-radius:5px; cursor:pointer;">PAUSE</button>
                        </div>
                    </div>
                </div>

                <div style="margin-top:20px; text-align:center;">
                    <small style="color:#888;">CROSSFADER (A <-> B)</small><br>
                    <input type="range" id="fader" min="0" max="1" step="0.01" value="0.5" style="width: 80%; accent-color: white;">
                </div>

                <audio id="audioA" src="data:audio/mp3;base64,{data_a}" crossorigin="anonymous"></audio>
                <audio id="audioB" src="data:audio/mp3;base64,{data_b}" crossorigin="anonymous"></audio>

                <script>
                    const audA = document.getElementById('audioA');
                    const audB = document.getElementById('audioB');
                    const ctx = new (window.AudioContext || window.webkitAudioContext)();
                    const fader = document.getElementById('fader');
                    
                    function setupVisualizer(audioElem, canvasID, color) {{
                        const src = ctx.createMediaElementSource(audioElem);
                        const analyser = ctx.createAnalyser();
                        const canvas = document.getElementById(canvasID);
                        const canvasCtx = canvas.getContext("2d");

                        src.connect(analyser);
                        analyser.connect(ctx.destination);
                        analyser.fftSize = 256;

                        const bufferLength = analyser.frequencyBinCount;
                        const dataArray = new Uint8Array(bufferLength);

                        function draw() {{
                            requestAnimationFrame(draw);
                            analyser.getByteFrequencyData(dataArray);
                            canvasCtx.fillStyle = "#111";
                            canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
                            
                            const barWidth = (canvas.width / bufferLength) * 2;
                            let x = 0;
                            for(let i = 0; i < bufferLength; i++) {{
                                let barHeight = dataArray[i] / 4;
                                canvasCtx.fillStyle = color;
                                canvasCtx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
                                x += barWidth + 1;
                            }}
                        }}
                        draw();
                    }}

                    let setupA = false, setupB = false;
                    function play(deck) {{
                        if (ctx.state === 'suspended') ctx.resume();
                        if (deck === 'A') {{
                            if(!setupA) {{ setupVisualizer(audA, 'canvasA', '{primary_neon}'); setupA = true; }}
                            audA.play();
                        }} else {{
                            if(!setupB) {{ setupVisualizer(audB, 'canvasB', '#FF44CC'); setupB = true; }}
                            audB.play();
                        }}
                    }}
                    function pause(deck) {{ deck === 'A' ? audA.pause() : audB.pause(); }}

                    // Link fader to volumes
                    fader.oninput = () => {{
                        audA.volume = (1 - fader.value) * document.getElementById('volA').value;
                        audB.volume = fader.value * document.getElementById('volB').value;
                    }};

                    function updateTime(aud, curID, remID) {{
                        aud.ontimeupdate = () => {{
                            let cM = Math.floor(aud.currentTime/60), cS = Math.floor(aud.currentTime%60);
                            document.getElementById(curID).innerText = (cM<10?'0'+cM:cM)+":"+(cS<10?'0'+cS:cS);
                            let r = aud.duration - aud.currentTime;
                            if(!isNaN(r)) {{
                                let rM = Math.floor(r/60), rS = Math.floor(r%60);
                                document.getElementById(remID).innerText = "-"+(rM<10?'0'+rM:rM)+":"+(rS<10?'0'+rS:rS);
                            }}
                        }};
                    }}
                    updateTime(audA, 'curA', 'remA');
                    updateTime(audB, 'curB', 'remB');
                </script>
            </div>
            """
            components.html(mixer_html, height=450)
            st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | Tactical Sound Module v4.2")
            # ==========================================
    # 🛰️ UNIT 06: TACTICAL TEXT COMMAND (Local Sync)
    # ==========================================
    elif st.session_state.page == "2":
        st.markdown("<h2 class='neon-wrapper'>🛰️ UNIT 06: REAL-TIME TEXT COMMAND</h2>", unsafe_allow_html=True)

        # 1. ฐานข้อมูลแชตชั่วคราวในเครื่อง
        if "cmd_chat" not in st.session_state:
            st.session_state.cmd_chat = [
                {"user": "SYSTEM", "msg": "ระบบ Synapse พร้อมใช้งาน", "time": "21:00", "type": "sys"}
            ]

        # 2. หน้าจอแสดงผลแชต (เน้นอ่านง่าย สไตล์กองบัญชาการ)
        st.markdown("""
            <div style="background:rgba(0,255,65,0.05); padding:15px; border-radius:10px; border:1px solid #00ff41; height:450px; overflow-y:auto;">
        """, unsafe_allow_html=True)
        
        for m in st.session_state.cmd_chat:
            if m["type"] == "sys":
                st.caption(f"🛡️ {m['time']} | {m['msg']}")
            else:
                st.markdown(f"""
                    <div style="margin-bottom:10px;">
                        <span style="color:#00ff41; font-weight:bold;">[{m['time']}] {m['user']}:</span> 
                        <span style="color:#ffffff;">{m['msg']}</span>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # 3. ส่วนควบคุมการส่งข้อความ
        st.divider()
        with st.container():
            c1, c2 = st.columns([0.8, 0.2])
            with c1:
                # ช่องกรอกข้อความ (ส่งไว ไม่ดีเลย์)
                user_input = st.text_input("ป้อนข้อความคำสั่ง...", key="cmd_input", label_visibility="collapsed")
            with c2:
                send_btn = st.button("EXECUTE", use_container_width=True)

            if send_btn and user_input:
                # บันทึกข้อมูลลงเครื่องทันที
                now = datetime.now().strftime("%H:%M")
                new_entry = {"user": "AGENT-TA", "msg": user_input, "time": now, "type": "user"}
                st.session_state.cmd_chat.append(new_entry)
                
                # แจ้งเตือนเด้งหน้าจอ (Notification)
                st.toast(f"ส่งข้อความสำเร็จ: {user_input}", icon="📡")
                
                # สั่ง Rerun เพื่ออัปเดตหน้าจอทันที
                st.rerun()

        # 4. ส่วนวิเคราะห์สถานะ (จำลอง GPS/Weather รอไว้)
        st.write("---")
        col_st1, col_st2 = st.columns(2)
        with col_st1:
            st.write("📍 **Location:** 101 Command Center")
        with col_st2:
            st.write("⚡ **Latent:** 0.00ms (Local Mode)")



    
    elif st.session_state.page == "3":
        st.markdown("<h2 style='color:#00ff41;'>🔮 UNIT 05: THE TRUTH SCANNER</h2>", unsafe_allow_html=True)

        # ---------------------------------------------------------
        # 1. ตรวจสอบพิกัดวันเดี่ยว (Single Day Decoder)
        # ---------------------------------------------------------
        st.subheader("1️⃣ ตรวจสอบรหัสความจริงรายวัน (1960-2026)")
        t_date = st.date_input("เลือกวันที่ที่อยากรู้", value=date.today(), 
                               min_value=date(1960,1,1), max_value=date(2026,12,31), key="single_q")
        if t_date:
            d_info = get_detailed_logic(t_date)
            st.info(f"วัน{d_info['day_name']} | {d_info['phase']} | รหัสประจำวัน: {d_info['res']}")

        st.divider()

        # ---------------------------------------------------------
        # 2. สแกนคู่ขนาน & หาค่า GAP (แฉวิธีคำนวณ ธร-เพชร-กงจักร)
        # ---------------------------------------------------------
        st.subheader("2️⃣ วิเคราะห์รหัสคู่ขนาน & สัญญาณ GAP")
        c1, c2 = st.columns(2)
        with c1:
            dob1 = st.date_input("👤 AGENT 1 (ตัวตั้งต้น)", value=None, min_value=date(1960,1,1), key="u1_main")
        with c2:
            dob2 = st.date_input("👤 AGENT 2 (คู่สแกน)", value=None, min_value=date(1960,1,1), key="u2_main")

        if dob1 and dob2:
            dat1 = get_detailed_logic(dob1)
            dat2 = get_detailed_logic(dob2)
            g_val = abs(dat1['res'] - dat2['res'])

            # --- ส่วนอธิบายการคำนวณ (คำนวณให้ดูสดๆ) ---
            st.markdown("#### 🛠️ กระบวนการถอดรหัสเลข")
            col_ex1, col_ex2 = st.columns(2)
            with col_ex1:
                st.markdown(f"**AGENT 1:** {dob1}")
                st.write(f"- วัน{dat1['day_name']} = `{dat1['day_val']}`")
                st.write(f"- {dat1['phase']} = `{dat1['m_num']}`")
                st.code(f"สูตร: {dat1['formula']} = {dat1['res']}")
            with col_ex2:
                st.markdown(f"**AGENT 2:** {dob2}")
                st.write(f"- วัน{dat2['day_name']} = `{dat2['day_val']}`")
                st.write(f"- {dat2['phase']} = `{dat2['m_num']}`")
                st.code(f"สูตร: {dat2['formula']} = {dat2['res']}")

            st.markdown(f"<h1 style='text-align:center; color:#00ff41;'>GAP: {g_val:.4f}</h1>", unsafe_allow_html=True)
            
            # ลำดับความสำคัญ ธร-เพชร-กงจักร
            if g_val <= 1.0:
                st.error("💎 **ระดับ: เพชร (Diamond)** - รหัสบรรจบขั้นสูงสุด")
            elif 3.8 <= g_val <= 4.2:
                st.warning("🌀 **ระดับ: ธร (Tor)** - สัญญาณสะท้อนคู่ขนาน (สำคัญ)")
            elif g_val >= 10.0:
                st.success("⚙️ **ระดับ: กงจักร (Chakra)** - รหัสตัดขาด/แยกตัวอิสระ")

            # ---------------------------------------------------------
            # 3. แผนที่พิกัดเวลา (Past & Future Timeline)
            # ---------------------------------------------------------
            st.divider()
            st.subheader("3️⃣ แผนที่พิกัดกาลเวลา (อดีต-อนาคต)")
            st.write(f"วิเคราะห์รอบเวลาจากรหัสหลัก: **{dat1['res']}**")
            t_back, t_next = st.tabs(["⏪ อดีต (365 วัน)", "🔮 อนาคต (365 วัน)"])
            with t_back:
                st.dataframe(run_scanner(dat1['res'], date.today(), 365, "past"), use_container_width=True)
            with t_next:
                st.dataframe(run_scanner(dat1['res'], date.today(), 365, "future"), use_container_width=True)

        

    elif page == "4":
        st.markdown("<h2 class='neon-wrapper'>⚡ UNIT 04: SENSOR SCAN</h2>", unsafe_allow_html=True)
        st.info("📶 ตรวจรับสัญญาณเซนเซอร์...")

    elif page == "5":
        st.markdown("<h2 class='neon-wrapper'>🎨 UNIT 05: UI DESIGNER</h2>", unsafe_allow_html=True)
        st.info("🌈 ปรับแต่งสี Interface...")

    elif page == "6":
        st.markdown("<h2 class='neon-wrapper'>💬 UNIT 06: COMMS CENTER</h2>", unsafe_allow_html=True)
        st.info("🛰️ ช่องทางสื่อสารลับ...")

    elif page == "7":
        st.markdown("<h2 class='neon-wrapper'>🛠️ UNIT 07: DIY MASTER</h2>", unsafe_allow_html=True)
        st.info("🔧 บันทึกงานซ่อมบำรุง...")

    elif page == "8":
        st.markdown("<h2 class='neon-wrapper'>🧬 UNIT 08: SYNAPSE CORE</h2>", unsafe_allow_html=True)
        st.info("🧠 ระบบ AI ประมวลผล...")

    elif page == "9":
        st.markdown("<h2 class='neon-wrapper'>📹 UNIT 09: MEDIA STUDIO</h2>", unsafe_allow_html=True)
        st.info("🎬 จัดการสื่อวิดีโอ...")

    elif page == "10":
        st.markdown("<h2 class='neon-wrapper'>💾 UNIT 10: FIREBASE DB</h2>", unsafe_allow_html=True)
        st.info("📂 จัดการฐานข้อมูล Cloud...")

    elif page == "11":
        st.markdown("<h2 class='neon-wrapper'>🏴 11: COMMAND POST</h2>", unsafe_allow_html=True)
        st.info("🏁 สรุปสถานะภารกิจ...")

# --- 6. FOOTER ---
st.write("---")
st.caption(f"SYNAPSE OS v4.2 | AGENT STATUS: ONLINE | {datetime.now().strftime('%H:%M:%S')}")
