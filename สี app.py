import streamlit as st
import os
import datetime
import pandas as pd
import math
import time
import base64
from datetime import datetime, date, timedelta
import streamlit.components.v1 as components
import firebase_admin
from firebase_admin import credentials, db
import hashlib
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import base64

def get_base64(file_path):
    """ฟังก์ชันสำหรับแปลงไฟล์เพลงเป็น Base64 เพื่อให้เล่นบน HTML5 Player ได้"""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    except Exception as e:
        st.error(f"❌ ไม่สามารถอ่านไฟล์ได้: {e}")
        return None

# --- 1. SETUP & ลบติ่ง (อยู่นิ่งๆ ไม่เจ็บตัว) ---
st.set_page_config(page_title="SYNAPSE HUB", layout="wide")

def setup_ui():
    st.markdown("""
        <style>
        /* ลบ Header, Footer และเมนูเดิมของ Streamlit */
        header, footer, #MainMenu {visibility: hidden;}
        .stApp { background: #000; color: #00f2fe; }
        
        /* สไตล์ปุ่มเมนู */
        .stButton>button {
            border-radius: 15px;
            border: 1px solid #00f2fe;
            background: rgba(0, 242, 254, 0.1);
            color: white;
            height: 100px;
            font-size: 18px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background: #00f2fe;
            color: #000;
            box-shadow: 0 0 20px #00f2fe;
        }
        
        /* ตัวหนังสือวิ้ง */
        .neon-text {
            text-align: center;
            color: #fff;
            text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

setup_ui()

# --- 2. การจัดการหน้าจอ (Navigation) ---
if 'page' not in st.session_state:
    st.session_state.page = "HOME"

# ฟังก์ชันย้อนกลับ
if st.session_state.page != "HOME":
    if st.button("⬅️ กลับหน้าหลัก"):
        st.session_state.page = "HOME"
        st.rerun()

# --- 3. เนื้อหาแต่ละหน้า ---

# [ หน้าแรก: ศูนย์รวม 10 แอป ]
if st.session_state.page == "HOME":
    # วาง LOGO แทนที่ติ่ง
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        if os.path.exists("logo1.png"):
            st.image("logo1.png", use_container_width=True)
        else:
            st.markdown("<h1 class='neon-text'>SYNAPSE</h1>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center;'>ศูนย์ควบคุมระบบ: เลือกฟังก์ชันการใช้งาน</h3>", unsafe_allow_html=True)
    st.divider()

    # สร้าง Grid 10 แอป (แบ่งเป็น 2 คอลัมน์)
    c1, c2 = st.columns(2)

    with c1:
        if st.button("🎵 1. MUSIC PLAYER\nฟังเพลง MP3 จากคลังข้อมูล", use_container_width=True):
            st.session_state.page = "1"; st.rerun()
        st.caption("ความสามารถ: เล่นไฟล์เสียง 1.mp3 และระบบควบคุมเสียงผ่านหน้าเว็บ")

        if st.button("🖼️ 2. IMAGE SEARCH\nค้นหาภาพจากดาวเทียม", use_container_width=True):
            st.session_state.page = "3"; st.rerun()
        st.caption("ความสามารถ: ดึงรูปภาพจากคลัง Unsplash ตามคำค้นหาที่ต้องการ")

        if st.button("✨ 3. NEON GENERATOR\nสร้างตัวอักษรเรืองแสง", use_container_width=True):
            st.session_state.page = "5"; st.rerun()
        st.caption("ความสามารถ: แปลงข้อความธรรมดาให้เป็นศิลปะนีออนวิ้งๆ")

        if st.button("💖 4. DESTINY CHECK\nตรวจดวงชะตาคู่ขนาน", use_container_width=True):
            st.session_state.page = "7"; st.rerun()
        st.caption("ความสามารถ: วิเคราะห์ดวงชะตาในมิติที่ 4 ผ่านระบบฐานข้อมูลชื่อ")

        if st.button("📝 5. SYSTEM LOG\nบันทึกข้อมูลการใช้งาน", use_container_width=True):
            st.session_state.page = "9"; st.rerun()
        st.caption("ความสามารถ: จดบันทึกข้อความและเหตุการณ์สำคัญลงในหน่วยความจำ")

    with c2:
        if st.button("💬 6. CHAT SYSTEM\nระบบสื่อสารอัจฉริยะ", use_container_width=True):
            st.session_state.page = "2"; st.rerun()
        st.caption("ความสามารถ: โต้ตอบผ่านข้อความกับระบบจัดการ AI")

        if st.button("🎬 7. VIDEO HUB\nศูนย์รวมวิดีโอวงจรปิด", use_container_width=True):
            st.session_state.page = "4"; st.rerun()
        st.caption("ความสามารถ: เชื่อมต่อและฉายภาพวิดีโอจาก YouTube หรือ Link ตรง")

        if st.button("🌍 8. WORLD CLOCK\nเวลาโลกแบบเรียลไทม์", use_container_width=True):
            st.session_state.page = "6"; st.rerun()
        st.caption("ความสามารถ: ตรวจสอบเวลาปัจจุบันในโซนต่างๆ ทั่วโลก")

        if st.button("🔢 9. DAILY CODE\nรหัสลับประจำวัน", use_container_width=True):
            st.session_state.page = "8"; st.rerun()
        st.caption("ความสามารถ: เจนรหัสตัวเลขนำโชคและรหัสรักษาความปลอดภัยรายวัน")

        if st.button("🎨 10. COLOR MASTER\nปรับแต่งธีมสีระบบ", use_container_width=True):
            st.session_state.page = "10"; st.rerun()
        st.caption("ความสามารถ: เปลี่ยนสีสันของ Interface เพื่อความสวยงามตามใจชอบ")

# --- ส่วนนี้คือที่วางโค้ดของแต่ละแอปย่อย (ทำเหมือนเดิม) ---
# --- [ แก้ไขเฉพาะส่วนหน้า 1 (CORE ROOM) ] ---
elif st.session_state.page == "1":
    # ดึงรายชื่อเพลง .mp3 ทั้งหมดในโฟลเดอร์
    all_music = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    
    # กำหนดสีประจำห้อง CORE ROOM
    c1, c2 = "#39FF14", "#00FFDD" 

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
        .title-core {{
            font-family: 'Orbitron', sans-serif; color: #fff; text-align: center;
            text-shadow: 0 0 10px {c1}; font-size: 2rem; margin-bottom: 20px;
        }}
        </style>
        <h1 class="title-core">🔥 CORE ROOM</h1>
    """, unsafe_allow_html=True)

    if all_music:
        # ตรวจสอบลำดับเพลง
        if 'global_song_idx' not in st.session_state:
            st.session_state.global_song_idx = 0
            
        current_song_name = all_music[st.session_state.global_song_idx % len(all_music)]
        song_b64 = get_base64(current_song_name) # เรียกใช้ฟังก์ชันแปลงไฟล์ที่คุณมี
        
        if song_b64:
            # ส่วนแสดงผล Visualizer และปุ่มเล่นเพลง (HTML/JS จากที่คุณส่งมา)
            html_code = f"""
            <div style="background: rgba(0,0,0,0.5); padding: 20px; border-radius: 20px; border: 1px solid {c1}44;">
                <canvas id="canvas-core" style="width:100%; height:150px; background:#000; border-radius:10px;"></canvas>
                <button id="btn-core" style="width:100%; padding:20px; margin-top:15px; background:transparent; color:{c1}; border:2px solid {c1}; font-family:'Orbitron'; cursor:pointer; border-radius:10px; font-weight:bold; font-size:18px;">
                    ACTIVATE CORE SYSTEM ⚡
                </button>
                <audio id="audio-core" src="data:audio/mp3;base64,{song_b64}"></audio>
                <p style="color:{c1}; font-family:'Orbitron'; font-size:14px; text-align:center; margin-top:10px;">
                    TRACK: {current_song_name}
                </p>
            </div>
            <script>
                const audio = document.getElementById('audio-core');
                const btn = document.getElementById('btn-core');
                const canvas = document.getElementById('canvas-core');
                const ctx = canvas.getContext('2d');
                let audioCtx, analyser, source, dataArray;

                btn.onclick = function() {{
                    if (!audioCtx) {{
                        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                        analyser = audioCtx.createAnalyser();
                        source = audioCtx.createMediaElementSource(audio);
                        source.connect(analyser);
                        analyser.connect(audioCtx.destination);
                        analyser.fftSize = 256; 
                        dataArray = new Uint8Array(analyser.frequencyBinCount);
                        render();
                    }}
                    if (audio.paused) {{ audio.play(); btn.innerText = "SYSTEM ONLINE 🟢"; }}
                    else {{ audio.pause(); btn.innerText = "SYSTEM PAUSED 🔴"; }}
                }};

                function render() {{
                    requestAnimationFrame(render);
                    analyser.getByteFrequencyData(dataArray);
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    const bWidth = (canvas.width / dataArray.length) * 2;
                    let x = 0;
                    for (let i = 0; i < dataArray.length; i++) {{
                        let h = (dataArray[i] / 255) * canvas.height;
                        let grad = ctx.createLinearGradient(0, canvas.height, 0, canvas.height - h);
                        grad.addColorStop(0, "{c1}"); grad.addColorStop(1, "{c2}");
                        ctx.fillStyle = grad;
                        ctx.shadowBlur = 10; ctx.shadowColor = "{c1}";
                        ctx.fillRect(x, canvas.height - h, bWidth - 1, h);
                        x += bWidth;
                    }}
                }}
            </script>
            """
            st.components.v1.html(html_code, height=350)
            
            # --- ส่วนจัดการ Playlist ใต้เครื่องเล่น ---
            st.write("---")
            col_skip, col_shuf = st.columns(2)
            with col_skip:
                if st.button("⏭️ เพลงถัดไป"):
                    st.session_state.global_song_idx += 1
                    st.rerun()
            with col_shuf:
                if st.button("🎲 สุ่มเพลง"):
                    st.session_state.global_song_idx = random.randint(0, len(all_music)-1)
                    st.rerun()

            with st.expander("📂 เลือกเพลงจากคลัง (52 TRACKS)"):
                for i, song in enumerate(all_music):
                    is_current = (i == st.session_state.global_song_idx % len(all_music))
                    label = f"▶️ {song}" if is_current else f"▪️ {song}"
                    if st.button(label, key=f"track_{i}", use_container_width=True):
                        st.session_state.global_song_idx = i
                        st.rerun()
        else:
            st.error("ไม่สามารถโหลดไฟล์เพลงได้ (Base64 Error)")
    else:
        st.warning("ไม่พบไฟล์ .mp3 ในโฟลเดอร์หลัก กรุณาเพิ่มไฟล์เพลงก่อนครับ")
# --- [ แก้ไขเฉพาะส่วนหน้า 2 (CHAT SYSTEM -> STUDIO MIXER) ] ---
elif st.session_state.page == "2":
    # โหลด Logo สำหรับใช้ในหน้า Mixer (เรียกฟังก์ชันที่คุณมี)
    logo_base64 = get_base64("logo1.png")
    logo_html_link = f"data:image/png;base64,{logo_base64}" if logo_base64 else ""

    # CSS เฉพาะของหน้า 2 เพื่อปรับแต่ง UI ให้ดูเป็นห้อง Mixer
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
        
        .neon-title-mixer {{
            font-family: 'Orbitron', sans-serif;
            color: #fff;
            text-align: center;
            text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 20px #ff00de, 0 0 30px #00f3ff;
            font-size: 1.5rem;
            margin-bottom: 20px;
        }}
        /* ปรับแต่ง Container ของ HTML ให้พอดี */
        iframe {{ border-radius: 20px; box-shadow: 0 0 30px rgba(255, 0, 222, 0.2); }}
        </style>
        <h1 class="neon-title-mixer">🎧 SYNAPSE STUDIO MIXER</h1>
    """, unsafe_allow_html=True)

    # โค้ด HTML/JS Mixer (ตัวที่คุณส่งมา)
    mixer_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            body {{ background: #000; color: white; font-family: 'Inter', sans-serif; overflow: hidden; padding: 10px; }}
            .neon-box {{ border: 1px solid rgba(255, 255, 255, 0.1); background: rgba(15, 15, 15, 1); box-shadow: 0 0 20px rgba(255,0,222,0.1); }}
            .deck-box {{ border-left: 4px solid; background: rgba(25, 25, 25, 1); transition: 0.3s; }}
            .visualizer-container {{ height: 100px; background: #000; border-radius: 12px; border: 1px solid #333; }}
            .btn-neon {{ transition: 0.2s; font-weight: bold; text-transform: uppercase; font-size: 11px; letter-spacing: 1px; }}
            .neon-red {{ border: 2px solid #ff0055; color: #ff0055; text-shadow: 0 0 5px #ff0055; }}
            .neon-red:hover {{ background: #ff0055; color: white; }}
            .neon-green {{ border: 2px solid #00ffcc; color: #00ffcc; text-shadow: 0 0 5px #00ffcc; }}
            .neon-green:hover {{ background: #00ffcc; color: black; }}
            .progress-bg {{ height: 5px; background: #1a1a1a; border-radius: 3px; overflow: hidden; }}
            .progress-fill {{ height: 100%; width: 0%; background: linear-gradient(90deg, #ff00de, #00f3ff); }}
        </style>
    </head>
    <body>
        <div class="max-w-md mx-auto p-4 neon-box rounded-3xl">
            <canvas id="visualizer" class="visualizer-container w-full mb-4"></canvas>

            <div class="p-3 deck-box border-pink-600 rounded-r-xl mb-2">
                <div class="flex justify-between items-center mb-1">
                    <span class="text-[9px] text-pink-500 font-bold uppercase">Deck A</span>
                    <span id="timeA" class="text-[9px] font-mono text-gray-400">READY</span>
                </div>
                <div id="nameA" class="text-[10px] font-semibold mb-2 truncate text-gray-100">เลือกไฟล์เพลง A...</div>
                <input type="file" id="inputA" accept="audio/*" class="hidden" onchange="loadAudio(this.files[0], 'A')">
                <button onclick="document.getElementById('inputA').click()" class="text-[8px] bg-pink-900/30 px-2 py-1 rounded border border-pink-500/50 text-pink-200">LOAD A</button>
                <div class="progress-bg mt-2"><div id="barA" class="progress-fill"></div></div>
            </div>

            <div class="p-3 deck-box border-cyan-400 rounded-r-xl mb-4">
                <div class="flex justify-between items-center mb-1">
                    <span class="text-[9px] text-cyan-400 font-bold uppercase">Deck B</span>
                    <span id="timeB" class="text-[9px] font-mono text-gray-400">READY</span>
                </div>
                <div id="nameB" class="text-[10px] font-semibold mb-2 truncate text-gray-100">เลือกไฟล์เพลง B...</div>
                <input type="file" id="inputB" accept="audio/*" class="hidden" onchange="loadAudio(this.files[0], 'B')">
                <button onclick="document.getElementById('inputB').click()" class="text-[8px] bg-cyan-900/30 px-2 py-1 rounded border border-cyan-500/50 text-cyan-200">LOAD B</button>
                <div class="progress-bg mt-2"><div id="barB" class="progress-fill" style="background: #00ffcc;"></div></div>
            </div>

            <div class="grid grid-cols-2 gap-3">
                <button onclick="startPlaying()" class="btn-neon neon-red py-2 rounded-xl">Start Mix</button>
                <button onclick="startCrossfade()" class="btn-neon neon-green py-2 rounded-xl">Crossfade</button>
            </div>
        </div>

        <script>
            let audioCtx, analyser, songA, songB, gainA, gainB, sourceA, sourceB;
            let isPlaying = false, current = 'A', dataArray;

            function initAudio() {{
                if (!audioCtx) {{
                    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    analyser = audioCtx.createAnalyser();
                    analyser.fftSize = 128;
                    dataArray = new Uint8Array(analyser.frequencyBinCount);
                    draw();
                }}
            }}

            function draw() {{
                requestAnimationFrame(draw);
                if (!analyser) return;
                analyser.getByteFrequencyData(dataArray);
                const canvas = document.getElementById('visualizer');
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                const bWidth = (canvas.width / dataArray.length) * 2;
                let x = 0;
                for(let i = 0; i < dataArray.length; i++) {{
                    let h = (dataArray[i] / 255) * canvas.height;
                    ctx.fillStyle = `hsl(${{280 + i*4}}, 100%, 50%)`;
                    ctx.fillRect(x, canvas.height - h, bWidth - 1, h);
                    x += bWidth;
                }}
                updateUI();
            }}

            async function loadAudio(file, key) {{
                initAudio();
                document.getElementById('name'+key).innerText = "Loading...";
                const buffer = await audioCtx.decodeAudioData(await file.arrayBuffer());
                if(key === 'A') songA = buffer; else songB = buffer;
                document.getElementById('name'+key).innerText = file.name;
            }}

            function startPlaying() {{
                if (!songA || !songB) return alert("โหลดเพลงให้ครบ A และ B ก่อนครับ!");
                if (isPlaying) return;
                sourceA = audioCtx.createBufferSource(); sourceA.buffer = songA;
                gainA = audioCtx.createGain(); sourceA.connect(gainA).connect(analyser).connect(audioCtx.destination);
                sourceB = audioCtx.createBufferSource(); sourceB.buffer = songB;
                gainB = audioCtx.createGain(); gainB.gain.value = 0;
                sourceB.connect(gainB).connect(analyser).connect(audioCtx.destination);
                sourceA.start(0); sourceB.start(0);
                isPlaying = true;
            }}

            function startCrossfade() {{
                if(!isPlaying) return;
                const now = audioCtx.currentTime;
                if(current === 'A') {{
                    gainA.gain.linearRampToValueAtTime(1, now); gainA.gain.linearRampToValueAtTime(0, now+5);
                    gainB.gain.linearRampToValueAtTime(0, now); gainB.gain.linearRampToValueAtTime(1, now+5);
                    current = 'B';
                }} else {{
                    gainB.gain.linearRampToValueAtTime(1, now); gainB.gain.linearRampToValueAtTime(0, now+5);
                    gainA.gain.linearRampToValueAtTime(0, now); gainA.gain.linearRampToValueAtTime(1, now+5);
                    current = 'A';
                }}
            }}

            function updateUI() {{
                if(!isPlaying) return;
                const now = audioCtx.currentTime;
                // อัปเดต Progress Bar และเวลาที่นี่ (ย่อ Logic เพื่อความกระชับ)
            }}
        </script>
    </body>
    </html>
    """
    # แสดงผล Mixer
    st.components.v1.html(mixer_html, height=550)
# --- [ แก้ไขเฉพาะส่วนหน้า 3 (IMAGE SEARCH -> COSMIC DECODER) ] ---
elif st.session_state.page == "3":
    # 1. สไตล์เฉพาะหน้า 3 (Dark Neon สไตล์อาจารย์ต๊ะ)
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
        .cosmic-title {
            font-family: 'Orbitron', sans-serif;
            color: #ff00ff;
            text-shadow: 0 0 10px #ff00ff, 0 0 20px #00f3ff;
            text-align: center;
            font-size: 2rem;
            margin-bottom: 5px;
        }
        .stMetric {
            background-color: rgba(30, 33, 48, 0.5);
            border-radius: 15px;
            padding: 15px;
            border: 1px solid #00f3ff;
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
        }
        </style>
        <h1 class="cosmic-title">🌌 COSMIC AUTO-DECODER</h1>
        <p style='text-align: center; color: #00f3ff; font-family: "Orbitron";'>QUANTUM REALITY CHECK</p>
    """, unsafe_allow_html=True)

    # 2. ส่วนรับข้อมูล
    with st.container():
        st.write("### 📅 เลือกวันที่ต้องการถอดรหัส")
        selected_date = st.date_input("", datetime.now(), label_visibility="collapsed")
    
    st.divider()

    # 3. Logic คำนวณอัตโนมัติ (ความจริงล้วนๆ)
    # A. วันในสัปดาห์
    day_of_week = selected_date.isoweekday()
    day_name_th = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"][day_of_week-1]

    # B. ปีนักษัตร
    thai_year = selected_date.year + 543
    zodiac_list = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
    current_zodiac = zodiac_list[thai_year % 12]

    # C. คำนวณข้างขึ้นข้างแรม (Approximate Lunar Phase)
    def get_lunar_phase(date):
        reference_date = datetime(2000, 1, 6) # วันแรม 15 ค่ำ
        diff = (date - reference_date.date()).days
        lunar_cycle = 29.530588853
        phase_pos = (diff % lunar_cycle) / lunar_cycle
        current_pos = phase_pos * 29.53
        if current_pos <= 14.76:
            step = round(current_pos if current_pos >= 1 else 1)
            return "ข้างขึ้น (-)", step, -1
        else:
            step = round(current_pos - 14.76 if (current_pos - 14.76) >= 1 else 1)
            return "ข้างแรม (+)", step, 1

    lunar_label, lunar_step, lunar_sign = get_lunar_phase(selected_date)

    # D. สูตรสมดุลจักรวาล (PHI Ratio)
    PHI = 1.618
    balance_point = lunar_step - 7.5
    lunar_modifier = balance_point * lunar_sign if lunar_sign == 1 else -balance_point
    result = (day_of_week * PHI) + lunar_modifier

    # 4. แสดงผลลัพธ์
    col1, col2, col3 = st.columns(3)
    col1.metric("DAY", day_name_th)
    col2.metric("ZODIAC", current_zodiac)
    col3.metric("LUNAR", f"{lunar_step} ค่ำ")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # แสดงเลขรหัสรหัสจักรวาล
    st.write("### 🎯 COSMIC INDEX (ค่าความสั่นสะเทือน)")
    st.metric(label="Energy Code", value=f"{abs(result):.4f}")

    # 5. ถอดรหัสตัวเลขเด่น
    raw_num = str(abs(result)).replace('.', '')
    if len(raw_num) > 4:
        st.success(f"**รหัสตัวเลขนำโชคประจำวัน:** `{raw_num[1:3]}` , `{raw_num[2:4]}`")

    # 6. รายละเอียดเชิงลึก
    with st.expander("📝 เจาะลึกกระบวนการถอดรหัส (Log)"):
        st.latex(r"Result = (Day \times 1.618) \pm (Lunar_{Balance})")
        st.info(f"""
        - **ฐานแรงโน้มถ่วงวัน:** {day_of_week} × {PHI} = {day_of_week * PHI:.3f}
        - **อิทธิพลจันทรคติ:** {lunar_label} {lunar_step} ค่ำ
        - **สถานะ:** วิเคราะห์ข้อมูลจากวันที่ {selected_date.strftime('%d/%m/%Y')} สำเร็จ
        """)
    
    st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | Reality Decoder Mode")
# --- [ แก้ไขเฉพาะส่วนหน้า 4 (VIDEO HUB -> DESTINY SCANNER) ] ---
elif st.session_state.page == "4":
    import pandas as pd
    import math

    # 1. สไตล์เฉพาะหน้า 4 (Matrix Style)
    st.markdown("""
        <style>
        .logic-box { 
            background-color: rgba(16, 26, 36, 0.8); 
            padding: 15px; 
            border-left: 5px solid #00ff41; 
            border-radius: 10px;
            margin-bottom: 20px;
            color: #f0f0f0;
        }
        .stMetric { background-color: #0e161f; border: 1px solid #00ff41; border-radius: 10px; }
        </style>
        <h1 style='text-align: center; color: #00ff41; font-family: "Courier New";'>🛰️ DESTINY SCANNER</h1>
        <p style='text-align: center; color: #00ff41;'>ระบบวิเคราะห์ความถี่รหัสชีวิตรายบุคคล | ID: Ta101</p>
    """, unsafe_allow_html=True)

    # ฟังก์ชันคำนวณ Logic (ย่อจากที่คุณส่งมาเพื่อให้รันในหน้าเดียวได้)
    def get_destiny_logic(dt):
        ref_date = date(1900, 1, 1)
        diff = (dt - ref_date).days
        lunar_cycle = 29.530589
        pos = (diff - 0.5) % lunar_cycle
        day_val = dt.weekday() + 1
        day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
        day_name = day_names[dt.weekday()]
        
        if pos <= 14.765:
            m_num = int(pos) + 1
            phase = f"ขึ้น {m_num} ค่ำ"
            res = math.sqrt((day_val**2) + (m_num**2))
            formula = f"√({day_val}² + {m_num}²)"
            l_type = "แรงผลักดัน (Vector)"
        else:
            m_num = int(pos - 14.765) + 1
            phase = f"แรม {m_num} ค่ำ"
            res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
            formula = f"({day_val} × 1.618) / {m_num}"
            l_type = "สมดุลทองคำ (Golden)"
        return {"res": round(res, 4), "phase": phase, "day_name": day_name, "formula": formula, "type": l_type}

    def scan_future(target_res):
        future_data = []
        today = date.today()
        for i in range(180):
            current_date = today + timedelta(days=i)
            d = get_destiny_logic(current_date)
            gap = abs(d['res'] - target_res)
            status = ""
            if gap < 0.5: status = "💎 รหัสบรรจบ (เจอ/รวมตัว)"
            elif 3.8 <= gap <= 4.2: status = "🌀 สัญญาณสะท้อน (ดึงดูด)"
            elif gap > 10.0: status = "🚩 รหัสแยกตัว (อิสระ)"
            if status:
                future_data.append({"วันที่": current_date.strftime('%d/%m/%Y'), "พิกัดวัน": d['day_name'], "สถานะ": status, "Gap": round(gap, 4)})
        return pd.DataFrame(future_data)

    # ส่วน UI
    c1, c2 = st.columns(2)
    with c1:
        dob1 = st.date_input("👤 วันเกิดคุณ (ตัวตั้งต้น)", value=date(1995, 1, 1), key="d1")
    with c2:
        dob2 = st.date_input("👤 วันเกิดเป้าหมาย (คู่สแกน)", value=date(1995, 1, 1), key="d2")

    if dob1 and dob2:
        d1, d2 = get_destiny_logic(dob1), get_destiny_logic(dob2)
        
        # แสดงผล
        st.divider()
        res_a, res_b = st.columns(2)
        res_a.metric("รหัสประจำตัว (1)", d1['res'])
        res_b.metric("รหัสประจำตัว (2)", d2['res'])
        
        gap = abs(d1['res'] - d2['res'])
        st.subheader(f"🔍 วิเคราะห์ Gap: {gap:.4f}")
        
        if gap < 1.0: st.warning("🔮 ระดับ: รหัสแฝด (Twin Code)")
        elif 3.5 <= gap <= 4.5: st.error("⚠️ ระดับ: รหัสคู่ขนาน (Parallel Connection)"); st.balloons()
        else: st.success("✅ ระดับ: พลังงานอิสระ")

        # สแกนอนาคต
        st.write("---")
        st.subheader("🗓️ พยากรณ์พิกัดเวลา (180 วันข้างหน้า)")
        timeline_df = scan_future(d1['res'])
        if not timeline_df.empty:
            st.dataframe(timeline_df, use_container_width=True, hide_index=True)
        else:
            st.info("ไม่พบพิกัดที่สอดคล้องในช่วงนี้")

    st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | Destiny Scanner Mode")
# --- [ แก้ไขเฉพาะส่วนหน้า 5 (NEON GENERATOR -> FULL CYCLE SCANNER) ] ---
elif st.session_state.page == "5":
    import pandas as pd
    import math

    # 1. สไตล์เฉพาะหน้า 5 (Cyan Neon & Logic Box)
    st.markdown("""
        <style>
        .formula-box {
            background: rgba(0, 229, 255, 0.05);
            border-left: 5px solid #00e5ff;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            color: #fff;
        }
        .stMetric { background-color: #0e161f; border: 1px solid #00e5ff; border-radius: 10px; }
        </style>
        <h1 style='text-align: center; color: #fff; text-shadow: 0 0 10px #00e5ff;'>🛰️ SYNAPSE : FULL CYCLE SCANNER</h1>
        <p style='text-align: center; color: #00e5ff;'>ระบบสแกนพิกัดรหัสชีวิต 365 วัน (ย้อนหลัง-ล่วงหน้า)</p>
    """, unsafe_allow_html=True)

    # ฟังก์ชันคำนวณ Logic (Non-Fictional)
    def get_synapse_logic(dt):
        if dt is None: return None
        ref_date = date(1900, 1, 1)
        diff = (dt - ref_date).days
        lunar_cycle = 29.530589
        pos = (diff - 0.5) % lunar_cycle
        day_val = dt.weekday() + 1
        day_names = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
        is_waxing = pos <= 14.765
        m_num = int(pos) + 1 if is_waxing else int(pos - 14.765) + 1
        if is_waxing:
            res = math.sqrt((day_val**2) + (m_num**2))
            formula = f"√({day_val}² + {m_num}²)"
            type_text = "Vector Energy (ขึ้น)"
        else:
            res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
            formula = f"({day_val} × 1.618) / {m_num}"
            type_text = "Golden Ratio (แรม)"
        return {"res": round(res, 4), "phase": f"{'ขึ้น' if is_waxing else 'แรม'} {m_num} ค่ำ",
                "day": day_names[dt.weekday()], "formula": formula, "type": type_text}

    def run_scanner(target_res, base_date, days, mode="future"):
        results = []
        for i in range(days + 1):
            current_date = base_date + timedelta(days=i) if mode == "future" else base_date - timedelta(days=i)
            d = get_synapse_logic(current_date)
            gap = abs(target_res - d['res'])
            status = "อิสระ"
            if gap < 0.5: status = "💎 บรรจบ"
            elif 3.8 <= gap <= 4.2: status = "🌀 สะท้อน (Gap 4)"
            elif gap > 10.0: status = "🚩 แยกตัว"
            if status != "อิสระ":
                results.append({"วันที่": current_date.strftime("%d/%m/%Y"), "วัน": d['day'], 
                                "สถานะพิกัด": status, "Gap": round(gap, 4), "รหัสวัน": d['res']})
        return pd.DataFrame(results)

    # ส่วนรับข้อมูล
    user_dob = st.date_input("📅 ระบุวันเกิดของคุณเพื่อหาค่าตั้งต้น", value=None, key="scan_dob")

    if user_dob:
        u_data = get_synapse_logic(user_dob)
        st.markdown(f"""
            <div class="formula-box">
                <span style='font-size: 1.1rem;'>รหัสประจำตัวของคุณ: <b style='color:#00e5ff;'>{u_data['res']}</b></span><br>
                พิกัด: {u_data['day']} ({u_data['phase']}) | 🧬 สูตร: <code>{u_data['formula']}</code>
            </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.subheader("🔍 ขอบเขตการสแกนรอบวงจร")
        c1, c2 = st.columns(2)
        p_range = c1.slider("สแกนอดีต (วัน)", 0, 365, 180)
        f_range = c2.slider("สแกนอนาคต (วัน)", 0, 365, 180)

        t_past, t_future = st.tabs(["⏪ ข้อมูลพิกัดอดีต", "🔮 ข้อมูลพิกัดอนาคต"])
        with t_past:
            df_p = run_scanner(u_data['res'], date.today(), p_range, "past")
            st.dataframe(df_p, use_container_width=True, hide_index=True) if not df_p.empty else st.write("ไม่พบพิกัดพิเศษ")
        with t_future:
            df_f = run_scanner(u_data['res'], date.today(), f_range, "future")
            st.dataframe(df_f, use_container_width=True, hide_index=True) if not df_f.empty else st.write("ไม่พบพิกัดพิเศษ")
    else:
        st.info("🛰️ กรุณาระบุวันเกิดของคุณเพื่อเริ่มระบบสแกน 365 วัน")

    st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | Synapse Cycle Scanner v3.2")
# --- [ แก้ไขเฉพาะส่วนหน้า 6 (WORLD CLOCK -> PRIVATE AGENT CHAT) ] ---
elif st.session_state.page == "6":
    import base64
    import time

    # 1. สไตล์เฉพาะหน้า 6 (Agent Dark Mode)
    st.markdown("""
        <style>
        .agent-title {
            font-family: 'Orbitron', sans-serif;
            color: #ff4b4b;
            text-shadow: 0 0 10px #ff4b4b;
            text-align: center;
            font-size: 1.8rem;
        }
        .chat-bubble {
            padding: 10px 15px;
            border-radius: 15px;
            color: white;
            display: inline-block;
            max-width: 80%;
            margin-bottom: 5px;
        }
        </style>
        <h1 class="agent-title">🔐 SECURE AGENT CHAT</h1>
        <p style='text-align: center; color: #ff4b4b;'>ระบบสื่อสารเข้ารหัสระดับสูง | ID: Ta101</p>
    """, unsafe_allow_html=True)

    # ตรวจสอบการ Login (สมมติว่ามีระบบ User ใน session_state)
    if 'user' not in st.session_state:
        st.session_state.user = "AGENT_TA" # กำหนด User เริ่มต้นถ้ายังไม่มี

    # 2. ส่วนเลือกคู่สาย AGENT (ดึงข้อมูลจาก Firebase ของคุณ)
    try:
        users_ref = db.reference('users').get()
        friends = [u for u in users_ref.keys() if u != st.session_state.user] if users_ref else []
    except:
        friends = ["AGENT_ALPHA", "AGENT_BETA", "AGENT_UNKNOWN"] # Mock data ถ้าไม่มี DB

    target = st.selectbox("🎯 ระบุพิกัด AGENT เป้าหมาย:", ["-- เลือกเป้าหมาย --"] + friends)

    if target != "-- เลือกเป้าหมาย --":
        # สร้าง ID ห้องแชตเฉพาะ (เรียงตามตัวอักษรเพื่อความคงที่)
        rid = "_".join(sorted([st.session_state.user, target]))
        
        # 3. ส่วนส่งข้อมูล (Form)
        with st.form("private_media_form", clear_on_submit=True):
            msg = st.text_input(f"🔒 ข้อความลับถึง {target}...")
            uploaded_file = st.file_uploader("📸 แนบไฟล์ Media (JPG/PNG/MP4)", type=['jpg', 'png', 'mp4', 'mov'])
            
            if st.form_submit_button("🚀 LOCK & SEND"):
                file_data = None
                file_type = None
                
                if uploaded_file is not None:
                    bytes_data = uploaded_file.getvalue()
                    file_data = base64.b64encode(bytes_data).decode()
                    file_type = uploaded_file.type

                if msg or file_data:
                    # ส่งเข้า Firebase
                    try:
                        db.reference(f'private_rooms/{rid}').push({
                            'u': st.session_state.user,
                            'm': msg,
                            'file': file_data,
                            'ft': file_type,
                            'ts': time.time()
                        })
                        st.success("ส่งรหัสข้อมูลสำเร็จ")
                        time.sleep(0.5)
                        st.rerun()
                    except:
                        st.error("การเชื่อมต่อฐานข้อมูลล้มเหลว")

        # 4. ส่วนแสดงผลข้อความในห้องลับ
        st.divider()
        try:
            msgs_ref = db.reference(f'private_rooms/{rid}').order_by_key().limit_to_last(15).get()
        except:
            msgs_ref = None

        if msgs_ref:
            # เรียงจากใหม่ไปเก่า หรือตามลำดับเวลา
            for v in reversed(list(msgs_ref.values())):
                u_name = v.get('u', 'Unknown')
                msg_text = v.get('m', '')
                f_data = v.get('file')
                f_type = v.get('ft')
                
                side = "right" if u_name == st.session_state.user else "left"
                bg_color = "#ff4b4b" if u_name == st.session_state.user else "#333333"
                align = "right" if side == "right" else "left"

                st.markdown(f"""
                    <div style="text-align:{align}; margin-bottom:10px;">
                        <div class="chat-bubble" style="background:{bg_color}; text-align: left;">
                            <small style="opacity:0.7; font-size:10px;">{u_name}</small><br>
                            {f'<p style="margin:5px 0;">{msg_text}</p>' if msg_text else ''}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if f_data:
                    try:
                        decoded = base64.b64decode(f_data)
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with (col3 if side == "right" else col1):
                            if "image" in str(f_type):
                                st.image(decoded, use_container_width=True)
                            elif "video" in str(f_type):
                                st.video(decoded)
                    except:
                        st.caption("⚠️ ไม่สามารถถอดรหัสไฟล์ได้")
        else:
            st.info("🌑 สัญญาณว่างเปล่า... เริ่มต้นการสนทนาลับ")
    else:
        st.info("🛰️ กรุณาเลือกเป้าหมายเพื่อเปิดช่องสัญญาณลับ")

    st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | Private Agent Network v7.0")
# --- [ แก้ไขเฉพาะส่วนหน้า 7 (DESTINY CHECK -> AGENT RADAR) ] ---
elif st.session_state.page == "7":
    import folium
    from streamlit_folium import st_folium
    import math

    # ฟังก์ชันคำนวณระยะห่าง Haversine (ความจริงทางภูมิศาสตร์)
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371  # รัศมีโลก (กม.)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    st.markdown("""
        <h1 style='text-align: center; color: #00ff41; font-family: "Orbitron"; text-shadow: 0 0 10px #00ff41;'>🛰️ AGENT RADAR SYSTEM</h1>
        <p style='text-align: center; color: #00ff41;'>ระบบตรวจจับพิกัดเครือข่าย SYNAPSE</p>
    """, unsafe_allow_html=True)

    # 1. ดึงพิกัดปัจจุบัน (ดึงจากฟังก์ชัน get_geolocation หรือ Mock Up ถ้ายังไม่มี)
    # ในที่นี้ผมใช้พิกัดเริ่มต้นเป็นกรุงเทพฯ เพื่อความปลอดภัย
    my_lat, my_lon = 13.7563, 100.5018 
    
    st.info(f"📡 พิกัดปัจจุบันของคุณ (ORIGIN): {my_lat}, {my_lon}")

    # 2. สร้างแผนที่ธีม Dark Ops
    m = folium.Map(location=[my_lat, my_lon], zoom_start=12, tiles="CartoDB dark_matter")
    
    # 🔴 จุดของคุณ (Center)
    folium.Marker(
        [my_lat, my_lon], 
        tooltip="คุณ (ORIGIN)",
        icon=folium.Icon(color='red', icon='crosshairs', prefix='fa')
    ).add_to(m)

    # วงแหวนเรดาร์ (รัศมี 1km, 3km, 5km)
    for radius in [1000, 3000, 5000]:
        folium.Circle(
            radius=radius,
            location=[my_lat, my_lon],
            color="#00ff41",
            fill=False,
            dash_array='10, 10',
            opacity=0.3
        ).add_to(m)

    # 3. ดึงข้อมูล AGENT อื่นจาก Firebase
    try:
        users_ref = db.reference('users').get()
        if users_ref:
            for uid, data in users_ref.items():
                if uid != st.session_state.get('user', 'ADMIN'):
                    u_lat = data.get('lat')
                    u_lon = data.get('lon')
                    
                    if u_lat and u_lon:
                        dist = haversine(my_lat, my_lon, u_lat, u_lon)
                        
                        # ปักหมุดเพื่อน
                        folium.Marker(
                            [u_lat, u_lon],
                            popup=f"AGENT: {uid}<br>ระยะห่าง: {dist:.2f} กม.",
                            tooltip=f"{uid}: {dist:.2f} km",
                            icon=folium.Icon(color='green', icon='signal', prefix='fa')
                        ).add_to(m)
                        
                        # ลากเส้นเชื่อมต่อแบบประวิบวับ
                        folium.PolyLine(
                            locations=[[my_lat, my_lon], [u_lat, u_lon]],
                            color="#00ff41",
                            weight=1,
                            opacity=0.4,
                            dash_array='5, 5'
                        ).add_to(m)
    except Exception as e:
        st.warning("⚠️ ไม่สามารถเชื่อมต่อฐานข้อมูลพิกัดได้ (ระบบ Offline)")

    # 4. แสดงผลแผนที่
    st_folium(m, width="100%", height=500)

    # 5. ปุ่มอัปเดตพิกัดสด
    if st.button("🛰️ กระจายสัญญาณพิกัดสด (LIVE UPDATE)", use_container_width=True):
        try:
            db.reference(f'users/{st.session_state.user}').update({
                'lat': my_lat, 
                'lon': my_lon, 
                'ts': time.time()
            })
            st.success(f"พิกัด {my_lat}, {my_lon} ถูกส่งเข้าดาวเทียมแล้ว!")
        except:
            st.error("ไม่สามารถอัปเดตพิกัดได้ กรุณาเช็คการเชื่อมต่อ Firebase")

    st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | Global Radar Network v7.2")
# --- [ แก้ไขเฉพาะส่วนหน้า 8 (AI CHAT -> MUSIC STATION) ] ---
elif st.session_state.page == "8":
    import os
    import base64
    import streamlit.components.v1 as components

    # 1. สไตล์เฉพาะหน้า 8 (Music Player Theme)
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
        .music-title {
            font-family: 'Orbitron', sans-serif;
            color: #ff8c00;
            text-shadow: 0 0 10px #ff8c00;
            text-align: center;
            font-size: 1.8rem;
        }
        .song-info {
            background: rgba(255, 140, 0, 0.1);
            border: 1px solid #ff8c00;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            margin-bottom: 20px;
        }
        </style>
        <h1 class="music-title">🎧 SYNAPSE MUSIC STATION</h1>
        <p style='text-align: center; color: #ff8c00;'>ระบบสถานีเพลงต่อเนื่อง (Non-Stop)</p>
    """, unsafe_allow_html=True)

    # ตรวจสอบสถานะดัชนีเพลง
    if 'song_index' not in st.session_state:
        st.session_state.song_index = 0

    # 2. ตรวจสอบไฟล์เพลงในโฟลเดอร์
    music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลง .mp3 ใน Server (กรุณาอัปโหลดไฟล์เพลงไว้ที่โฟลเดอร์เดียวกับโปรแกรม)")
    else:
        # ป้องกัน Index Out of Range
        if st.session_state.song_index >= len(music_files):
            st.session_state.song_index = 0

        current_song = music_files[st.session_state.song_index]

        # 3. ส่วนแสดงข้อมูลเพลงที่กำลังเล่น
        st.markdown(f"""
            <div class="song-info">
                <p style="font-size: 0.9rem; color: #aaa; margin-bottom: 5px;">NOW PLAYING</p>
                <h3 style="color: #fff; margin: 0;">🎵 {current_song}</h3>
                <p style="font-size: 0.8rem; color: #ff8c00; margin-top: 5px;">ลำดับที่ {st.session_state.song_index + 1} / {len(music_files)}</p>
            </div>
        """, unsafe_allow_html=True)

        # 4. แปลงไฟล์เป็น Base64 เพื่อส่งเข้า HTML5 Player
        try:
            with open(current_song, "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                audio_url = f"data:audio/mp3;base64,{b64}"

            # JS Trick: เมื่อเพลงจบ (ended) ให้ส่งค่ากลับมาเพื่อเปลี่ยนเพลง
            audio_html = f"""
                <audio id="audio-player" controls autoplay style="width: 100%;">
                    <source src="{audio_url}" type="audio/mp3">
                </audio>
                <script>
                    var audio = document.getElementById('audio-player');
                    audio.onended = function() {{
                        window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'next'}}, '*');
                    }};
                </script>
            """
            
            # รัน HTML/JS ผ่าน Component
            result = components.html(audio_html, height=100)

            # 5. ปุ่มควบคุม (Manual Control)
            col1, col2, col3 = st.columns(3)
            if col1.button("⏮️ ก่อนหน้า", use_container_width=True):
                st.session_state.song_index = (st.session_state.song_index - 1) % len(music_files)
                st.rerun()
            
            if col2.button("🔄 เริ่มใหม่", use_container_width=True):
                st.rerun()

            # ตรวจสอบว่าเพลงจบจาก JS หรือผู้ใช้กด Next
            if col3.button("⏭️ ถัดไป", use_container_width=True) or (result == 'next'):
                st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
                st.rerun()

            # 6. รายชื่อเพลงทั้งหมด (Playlist)
            st.write("---")
            with st.expander("📂 คลังเพลง (Playlist)"):
                for i, f_name in enumerate(music_files):
                    active_style = "⭐" if i == st.session_state.song_index else "🎼"
                    if st.button(f"{active_style} {f_name}", key=f"s_{i}", use_container_width=True):
                        st.session_state.song_index = i
                        st.rerun()
        except Exception as e:
            st.error(f"❌ ระบบเครื่องเล่นขัดข้อง: {e}")

    st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | Synapse Music Station v8.0")
# --- [ แก้ไขเฉพาะส่วนหน้า 9 (SETTINGS -> CONTROL CENTER) ] ---
elif st.session_state.page == "9":
    import hashlib

    # 1. ฟังก์ชันความปลอดภัย (ความจริงที่ไม่หลอกลวง)
    def hash_pw(password):
        return hashlib.sha256(str.encode(password)).hexdigest()

    # 2. ส่วนหัวของหน้า Settings
    st.markdown(f"""
        <h1 style='text-align: center; color: {st.session_state.theme_color}; font-family: "Orbitron";'>⚙️ CONTROL CENTER</h1>
        <p style='text-align: center;'>ระบบจัดการตัวตนและสภาพแวดล้อม | User: <b>{st.session_state.user}</b></p>
    """, unsafe_allow_html=True)

    st.divider()

    # 3. การจัดการธีม (Theme Selection)
    st.subheader("🎨 ปรับแต่งสภาพแวดล้อม (Theme)")
    theme_options = {
        "Matrix (Green)": "#39FF14",
        "Ocean (Blue)": "#00A8E8",
        "Ember (Red)": "#FF4D4D",
        "Cyber (Coral)": "#FF7F50",
        "Deep Sea (Turquoise)": "#AFEEEE"
    }
    
    # เลือกธีมแล้วอัปเดตลง session_state ทันที
    selected_theme_name = st.selectbox("เลือกโทนสีของระบบ:", list(theme_options.keys()))
    if st.button("💾 บันทึกและปรับใช้ธีม"):
        st.session_state.theme_color = theme_options[selected_theme_name]
        st.success(f"ปรับใช้ธีม {selected_theme_name} สำเร็จ!")
        time.sleep(0.5)
        st.rerun()

    st.divider()

    # 4. ข้อมูลบัญชีและการรักษาความปลอดภัย
    st.subheader("🛡️ บัญชีและความปลอดภัย")
    with st.expander("🔑 เปลี่ยนรหัสผ่าน"):
        old_p = st.text_input("รหัสผ่านเดิม", type="password")
        new_p = st.text_input("รหัสผ่านใหม่", type="password")
        if st.button("ยืนยันการเปลี่ยนรหัส"):
            # ตรวจสอบรหัสเดิมจาก Firebase (Logic สมมติ)
            acc = db.reference(f'accounts/{st.session_state.user}').get()
            if acc and acc.get('pw') == hash_pw(old_p):
                db.reference(f'accounts/{st.session_state.user}').update({'pw': hash_pw(new_p)})
                st.success("เปลี่ยนรหัสผ่านเรียบร้อยแล้ว")
            else:
                st.error("รหัสผ่านเดิมไม่ถูกต้อง")

    # 5. ล้างข้อมูลและออกจากระบบ
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🧹 ล้างแคชระบบ (Clear Cache)", use_container_width=True):
            st.cache_data.clear()
            st.success("ล้างข้อมูลชั่วคราวสำเร็จ")
    with c2:
        if st.button("🚪 ออกจากระบบ (Logout)", use_container_width=True):
            st.session_state.auth_status = False
            st.session_state.user = None
            st.rerun()

    # 6. แสดงสถิติการใช้งาน (Reality Code)
    st.divider()
    st.caption(f"SYNAPSE OS v4.0 | พัฒนาโดย: {st.session_state.user}")
    st.caption(f"Last Login: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
# --- [ แก้ไขหน้า 10 (THE FINAL SENSOR -> TRIPLE REALITY CHECK) ] ---
elif st.session_state.page == "10":
    import streamlit.components.v1 as components

    # 1. ส่วนหัวของห้องปฏิบัติการ
    st.markdown("""
        <h1 style='text-align: center; color: #FFD700; font-family: "Orbitron"; text-shadow: 0 0 10px #FFD700;'>🛰️ SYNAPSE X : TRIPLE SENSOR</h1>
        <p style='text-align: center; color: #FFD700;'>ระบบตรวจวัดความจริงผ่านฮาร์ดแวร์ (Microphone & Accelerometer)</p>
    """, unsafe_allow_html=True)

    # 2. รวมเซนเซอร์ทั้งหมดเข้าด้วยกัน (Triple Tab)
    tab_audio, tab_motion, tab_spectrum = st.tabs(["🔊 AUDIO SENSOR", "📳 MOTION SENSOR", "📊 SPECTRUM ANALYZER"])

    with tab_audio:
        st.write("ตรวจสอบความดัง (dB) และความถี่หลัก (Hz) ของบรรยากาศ")
        audio_direct_js = """
        <div style="background-color: #000; color: #FFD700; padding: 20px; border: 2px solid #FFD700; border-radius: 15px; text-align: center; font-family: monospace;">
            <h2 id="st_audio">🔴 กำลังสแกนคลื่นเสียง...</h2>
            <hr style="border-color: #FFD700;">
            <div style="display: flex; justify-content: space-around;">
                <div><h3>dB</h3><h1 id="db_v" style="font-size: 50px; color:#0f0;">0</h1></div>
                <div><h3>Hz</h3><h1 id="hz_v" style="font-size: 50px; color:#0ff;">0</h1></div>
            </div>
            <p id="inf_audio" style="color: #888;">สถานะ: รอสัญญาณคลื่น</p>
        </div>
        <script>
            async function startA() {
                try {
                    const s = await navigator.mediaDevices.getUserMedia({ audio: true });
                    const ctx = new (window.AudioContext || window.webkitAudioContext)();
                    const ana = ctx.createAnalyser();
                    const src = ctx.createMediaStreamSource(s);
                    src.connect(ana); ana.fftSize = 2048;
                    const buf = new Uint8Array(ana.frequencyBinCount);
                    function up() {
                        ana.getByteFrequencyData(buf);
                        let sum = 0, mVal = 0, mIdx = 0;
                        for(let i=0; i<buf.length; i++) { sum += buf[i]; if(buf[i]>mVal){mVal=buf[i]; mIdx=i;} }
                        let db = Math.round((sum/buf.length)*2);
                        let hz = Math.round(mIdx * ctx.sampleRate / ana.fftSize);
                        document.getElementById('db_v').innerText = db;
                        document.getElementById('hz_v').innerText = hz;
                        document.getElementById('st_audio').innerText = "🟢 SENSOR ACTIVE";
                        requestAnimationFrame(up);
                    } up();
                } catch(e) { document.getElementById('st_audio').innerText = "❌ เซนเซอร์ไม่ทำงาน"; }
            } startA();
        </script>
        """
        components.html(audio_direct_js, height=280)

    with tab_motion:
        st.write("ตรวจจับแรงสั่นสะเทือนพื้นผิว (Magnitude)")
        motion_js = """
        <div style="background-color: #111; color: #FFD700; padding: 20px; border: 2px solid #FFD700; border-radius: 15px; text-align: center; font-family: monospace;">
            <small>Magnitude (G-Force)</small>
            <h1 id="mag_v" style="font-size: 60px; color: #0f0;">1.0000</h1>
            <p id="mot_st">🟢 สถานะนิ่ง (ความจริงคงที่)</p>
            <hr style="border-color: #333;">
            <div style="font-size: 12px; display:flex; justify-content: space-around;">
                <span>X: <b id="x_v">0</b></span> <span>Y: <b id="y_v">0</b></span> <span>Z: <b id="z_v">0</b></span>
            </div>
        </div>
        <script>
            async function startM() {
                if (typeof DeviceMotionEvent.requestPermission === 'function') { await DeviceMotionEvent.requestPermission(); }
                window.addEventListener('devicemotion', (e) => {
                    const acc = e.accelerationIncludingGravity;
                    if(!acc) return;
                    let x=acc.x||0, y=acc.y||0, z=acc.z||0;
                    let mag = Math.sqrt(x*x + y*y + z*z) / 9.80665;
                    document.getElementById('mag_v').innerText = mag.toFixed(4);
                    document.getElementById('x_v').innerText = x.toFixed(2);
                    document.getElementById('y_v').innerText = y.toFixed(2);
                    document.getElementById('z_v').innerText = z.toFixed(2);
                    let el = document.getElementById('mag_v');
                    if(mag > 1.05 || mag < 0.95) { el.style.color="#f00"; document.getElementById('mot_st').innerText="⚠️ MOTION DETECTED!"; }
                    else { el.style.color="#0f0"; document.getElementById('mot_st').innerText="🟢 SYSTEM STABLE"; }
                });
            } startM();
        </script>
        """
        components.html(motion_js, height=280)

    with tab_spectrum:
        st.write("วิเคราะห์สเปกตรัมเสียงแบบ Visualizer")
        spectrum_js = """
        <div style="background-color: #111; padding: 20px; border: 2px solid #FFD700; border-radius: 15px;">
            <canvas id="spec" style="width: 100%; height: 100px; background: #222; border-radius: 5px;"></canvas>
            <button id="btnS" style="width:100%; margin-top:10px; padding:10px; background:#FFD700; border:none; border-radius:5px; font-weight:bold;">🎙️ START SPECTRUM</button>
        </div>
        <script>
            const btn = document.getElementById('btnS');
            const cvs = document.getElementById('spec');
            const ctx = cvs.getContext('2d');
            btn.onclick = async () => {
                const s = await navigator.mediaDevices.getUserMedia({ audio: true });
                const aCtx = new (window.AudioContext || window.webkitAudioContext)();
                const ana = aCtx.createAnalyser();
                aCtx.createMediaStreamSource(s).connect(ana);
                ana.fftSize = 128;
                const buf = new Uint8Array(ana.frequencyBinCount);
                btn.style.display = 'none';
                function draw() {
                    requestAnimationFrame(draw);
                    ana.getByteFrequencyData(buf);
                    ctx.clearRect(0,0,cvs.width, cvs.height);
                    for(let i=0; i<buf.length; i++) {
                        ctx.fillStyle = '#FFD700';
                        ctx.fillRect(i*3, cvs.height - buf[i]/2, 2, buf[i]/2);
                    }
                } draw();
            };
        </script>
        """
        components.html(spectrum_js, height=220)

    st.divider()
    st.write("**⚠️ หลักฐานความจริง (Reality Evidence):**")
    st.info("ค่าทั้งหมดนี้ดึงจาก 'เซนเซอร์กายภาพ' ของมือถือโดยตรง ถ้าคุณอยู่นิ่งๆ ค่า G จะนิ่งที่ 1.0 ถ้ามีเสียงดัง ค่า dB จะดีดขึ้นทันที นี่คือข้อมูลที่ไม่ผ่านการปรุงแต่งครับ")
    st.caption(f"SYNAPSE X FINAL VERSION | STATUS: SECURE | {datetime.now().year}")


# (เพิ่ม elif ไปจนครบหน้า 10 ตามโครงเดิมได้เลยครับ...)
