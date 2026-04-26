Import streamlit as st
import os 
import time
import base64
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from folium.features import DivIcon
from streamlit_folium import st_folium
from math import radians, cos, sin, asin, sqrt
import pytz
from timezonefinder import TimezoneFinder
from datetime import datetime, date
import math
import random
from streamlit_js_eval import get_geolocation 
# 1. ฟังก์ชั่นดึงข้อมูล (สีแดงบนสุด)
def get_base64_data(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except Exception:
        return ""


#2.ตั้งค่าสีและสถานะเริ่มต้น
# --- ตรวจสอบสถานะสีและหน้าจอ (ห้ามมีภาษาไทยในคำสั่ง) ---
if 'main_color' not in st.session_state:
    st.session_state.main_color = "#00f3ff"

if 'sub_color' not in st.session_state:
    st. session_state . sub_color = "#ff00de"

if 'page' not in st.session_state:
    st.session_state.page = "HOME"

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

#การแสดงส่วน :root ใน Style ของคุณต๊ะให้เป็นเช่นนั้น
# --- ส่วนนี้คือตัวคุมโลโก้ให้แสดงทุกหน้า ---
logo_b64 = get_base64_data("logo1.png") # ดึงไฟล์รูปโลโก้

st.markdown(f"""
    <style>
    /* ตั้งค่าให้โลโก้อยู่กับที่ (Fixed) ไม่ว่าจะเลื่อนไปหน้าไหน */
    .global-logo {{
        position: fixed; 
        top: 15px;      /* ระยะห่างจากขอบบน */
        right: 25px;    /* ระยะห่างจากขอบขวา */
        width: 65px;    /* ขนาดความกว้างโลโก้ */
        z-index: 10000; /* ตั้งค่าให้อยู่ชั้นบนสุดของทุกอย่าง */
        filter: drop-shadow(0 0 10px var(--primary)); /* ใส่แสงเรืองแสงตามสีหลัก */
        animation: pulse 2s infinite alternate; /* ใส่เอฟเฟกต์เต้นตุบๆ */
    }}
    
    @keyframes pulse {{ 
        from {{ transform: scale(1); }} 
        to {{ transform: scale(1.1); }} 
    }}
    </style>
    
    <img src="data:image/png;base64,{logo_b64}" class="global-logo">
""", unsafe_allow_html=True)
# แก้ไขส่วน :root ใน Style ของคุณต๊ะให้เป็นแบบนี้
st.markdown(f"""
    <style>
    :root {{
        --primary: {st.session_state.main_color};
        --secondary: {st.session_state.sub_color};
        --glow: {st.session_state.get('bg_glow', '#00f3ff')};
    }}

    /* ทุกปุ่มในทุกห้องจะเปลี่ยนตาม */
    .stButton>button {{
        border: 1px solid var(--primary) !important;
        background: rgba(0,0,0,0.2) !important;
        color: white !important;
        box-shadow: 0 0 5px var(--primary);
    }}
    
    .stButton>button:hover {{
        border-color: var(--secondary) !important;
        box-shadow: 0 0 20px var(--secondary) !important;
    }}

    /* หัวข้อทุกห้องจะเรืองแสงตามสีที่เลือก */
    .neon-text {{
        color: var(--primary) !important;
        text-shadow: 0 0 10px var(--primary), 0 0 20px var(--secondary) !important;
    }}
    
    /* ขอบหน้าจอแอป */
    .stApp {{
        border: 2px solid var(--primary);
        transition: all 0.8s ease;
    }}
    </style>
""", unsafe_allow_html=True)
st.markdown("""
    <style>
    /* 1. เอาติ่งข้างล่าง (Footer) ออก */
    footer {visibility: hidden;}
    
    /* 2. เอาแถบเมนู (Header) ข้างบนออก */
    header {visibility: hidden;}
    
    /* 3. เอาปุ่มจุดสามจุด (MainMenu) ออก */
    #MainMenu {visibility: hidden;}
    
    /* แถม: ปรับระยะขอบใหม่ให้เต็มจอหลังจากเอาติ่งออก */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 0rem;
    }
    </style>
""", unsafe_allow_html=True)


# 4. SIDEBAR: ระบบเปลี่ยนสีและเพลงพื้นหลัง (เพื่อให้เพลงเล่นต่อเนื่อง)
with st.sidebar:
    st.markdown("<h2 class='neon-text'>CONTROL PANEL</h2>", unsafe_allow_html=True)
    
    # ส่วนเปลี่ยนสี
    with st.expander("🎨 THEME COLORS"):
        st.session_state.main_color = st.color_picker("Main Neon", st.session_state.main_color)
        st.session_state.sub_color = st.color_picker("Sub Neon", st.session_state.sub_color)
    
    # ส่วนเพลงพื้นหลัง (เล่นต่อเนื่องทุกหน้า)
    all_songs = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
    selected_bg = st.selectbox("🎵 Background Music", ["Off"] + all_songs)
    
    if selected_bg != "Off":
        bg_audio_data = get_base64_data(selected_bg)
        st.markdown(f"""
            <audio id="bgAudio" autoplay loop controls style="width: 100%; height: 40px; margin-top:10px;">
                <source src="data:audio/mp3;base64,{bg_audio_data}" type="audio/mp3">
            </audio>
        """, unsafe_allow_html=True)

# --- 5. การจัดการหน้า (Navigation) เริ่มต่อจากตรงนี้ ---
# if st.session_state.page == "HOME":
# elif st.session_state.page == "1":



# --- [ หัวใจคำนวณ: ระบบถอดรหัส Lunar ] ---
def get_detailed_logic(dt):
    if dt is None: return None
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
        formula, logic_type = f"√({day_val}² + {m_num}²)", "Vector Energy"
    else:
        m_num = int(pos - 14.765) + 1
        phase = f"แรม {m_num} ค่ำ"
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        formula, logic_type = f"({day_val} × 1.618) / {m_num}", "Golden Ratio"

    return {"res": round(res, 4), "phase": phase, "day_name": day_name, "day_val": day_val, "m_num": m_num, "formula": formula, "type": logic_type}
# --- ตั้งค่าหน้าจอ ---
st.set_page_config(page_title="SYNAPSE HUB", layout="wide")

# --- 1. SETUP & ลบติ่ง (อยู่นิ่งๆ ไม่เจ็บตัว) ---
st.set_page_config(page_title="SYNAPSE HUB", layout="wide")
# --- ส่วนหน้าจอลงชื่อเข้าใช้ (Login / Register) ---
if not st.session_state.get('logged_in', False):
    st.markdown("<h2 style='text-align:center; color:#00f3ff; font-family:Orbitron;'>REGISTER AGENT</h2>", unsafe_allow_html=True)
    
    with st.container():
        new_user = st.text_input("ENTER AGENT NAME", placeholder="เช่น ต๊ะ101, บาส").strip()
        
        if st.button("ACTIVATE SYSTEM", use_container_width=True):
            if new_user:
                # 1. เช็ค/ลงทะเบียนใน Firebase (โค้ดเดิมของเพื่อน)
                user_check = db.reference(f'users/{new_user}').get()
                
                if not user_check:
                    db.reference(f'users/{new_user}').set({
                        'created_at': time.time(),
                        'lat': 13.7367,
                        'lon': 100.5231
                    })
                
                # 2. จุดสำคัญ: สั่งให้ระบบ "จดจำ" ข้อมูลลงใน Session
                st.session_state.user = new_user        # จำชื่อรหัส
                st.session_state.logged_in = True     # เปลี่ยนสถานะเป็นล็อกอินแล้ว
                st.session_state.page = "HOME"         # สั่งให้ไปหน้าหลัก (HOME) ทันที

                # 3. แสดงผลความสำเร็จและรีโหลดแอป
                st.success(f"WELCOME AGENT: {new_user}")
                st.balloons()
                time.sleep(1.5) # หน่วงเวลาให้เห็นความสำเร็จนิดนึง
                st.rerun()      # รีเฟรชแอปเพื่อเข้าหน้าหลักด้วยชื่อใหม่ทันที
            else:
                st.warning("กรุณาใส่ชื่อ AGENT ของคุณก่อน!")
    st.stop() 

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
elif st.session_state.page == "1":
    st.markdown("<h2 class='neon-text'>🎧 SYNAPSE DJ STATION V.3</h2>", unsafe_allow_html=True)
    
    all_songs = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
    
    col_sel_a, col_sel_b = st.columns(2)
    with col_sel_a:
        song_a = st.selectbox("💿 DECK A", ["-- Select --"] + all_songs, key="sa")
    with col_sel_b:
        song_b = st.selectbox("💿 DECK B", ["-- Select --"] + all_songs, key="sb")

    data_a = get_base64_data(song_a) if song_a != "-- Select --" else ""
    data_b = get_base64_data(song_b) if song_b != "-- Select --" else ""

    mixer_html = f"""
    <div style="background: #000; border: 2px solid #333; border-radius: 20px; padding: 15px; font-family: 'Orbitron';">
        
        <marquee style="color: #00f3ff; margin-bottom: 10px;"> Now Playing Deck A: {song_a} | Deck B: {song_b} --- Synapse Unit High-Resolution Audio --- </marquee>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <div style="border: 1px solid #00f3ff; padding: 10px; border-radius: 15px; text-align: center;">
                <div style="display: flex; justify-content: space-between; font-size: 10px; color: #00f3ff;">
                    <span id="curA">00:00</span><span id="remA">-00:00</span>
                </div>
                <canvas id="canvasA" style="width: 100%; height: 50px; background: #111; margin: 5px 0;"></canvas>
                
                <input type="range" id="volA" min="0" max="1" step="0.01" value="0.7" style="width: 100%; accent-color: #00f3ff;">
                <div style="margin-top: 10px;">
                    <button onclick="play('A')" style="background:#00f3ff; border:none; padding:5px 15px; border-radius:5px;">PLAY</button>
                    <button onclick="pause('A')" style="background:none; border:1px solid #00f3ff; color:#00f3ff; padding:5px 15px; border-radius:5px;">PAUSE</button>
                </div>
            </div>

            <div style="border: 1px solid #ff00de; padding: 10px; border-radius: 15px; text-align: center;">
                <div style="display: flex; justify-content: space-between; font-size: 10px; color: #ff00de;">
                    <span id="curB">00:00</span><span id="remB">-00:00</span>
                </div>
                <canvas id="canvasB" style="width: 100%; height: 50px; background: #111; margin: 5px 0;"></canvas>

                <input type="range" id="volB" min="0" max="1" step="0.01" value="0.7" style="width: 100%; accent-color: #ff00de;">
                <div style="margin-top: 10px;">
                    <button onclick="play('B')" style="background:#ff00de; border:none; padding:5px 15px; border-radius:5px; color:white;">PLAY</button>
                    <button onclick="pause('B')" style="background:none; border:1px solid #ff00de; color:#ff00de; padding:5px 15px; border-radius:5px;">PAUSE</button>
                </div>
            </div>
        </div>

        <button onclick="autoFade()" style="width:100%; margin-top:15px; background: linear-gradient(90deg, #00f3ff, #ff00de); border:none; padding:10px; border-radius:10px; color:white; font-weight:bold;">🔄 10s AUTO CROSSFADE</button>

        <audio id="audioA" src="data:audio/mp3;base64,{data_a}" crossorigin="anonymous"></audio>
        <audio id="audioB" src="data:audio/mp3;base64,{data_b}" crossorigin="anonymous"></audio>

        <script>
            const audA = document.getElementById('audioA');
            const audB = document.getElementById('audioB');
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            
            function setupVisualizer(audioElem, canvasID, color) {{
                const src = ctx.createMediaElementSource(audioElem);
                const analyzer = ctx.createAnalyser();
                const canvas = document.getElementById(canvasID);
                const canvasCtx = canvas.getContext("2d");

                src.connect(analyzer);
                analyzer.connect(ctx.destination);
                analyzer.fftSize = 512; // ความละเอียดตามที่ขอ

                const bufferLength = analyzer.frequencyBinCount;
                const dataArray = new Uint8Array(bufferLength);

                function draw() {{
                    requestAnimationFrame(draw);
                    analyzer.getByteFrequencyData(dataArray);
                    canvasCtx.fillStyle = "#111";
                    canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
                    
                    const barWidth = (canvas.width / bufferLength) * 2.5;
                    let barHeight;
                    let x = 0;

                    for(let i = 0; i < bufferLength; i++) {{
                        barHeight = dataArray[i] / 2;
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
                    if(!setupA) {{ setupVisualizer(audA, 'canvasA', '#00f3ff'); setupA = true; }}
                    audA.play();
                }} else {{
                    if(!setupB) {{ setupVisualizer(audB, 'canvasB', '#ff00de'); setupB = true; }}
                    audB.play();
                }}
            }}
            function pause(deck) {{ deck === 'A' ? audA.pause() : audB.pause(); }}

            // ระบบเวลาถอยหลัง
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

            function autoFade() {{
                let steps = 100, interval = 100, volStep = 1/steps;
                audB.volume = 0; audB.play();
                if(!setupB) {{ setupVisualizer(audB, 'canvasB', '#ff00de'); setupB = true; }}
                let count = 0;
                let fade = setInterval(() => {{
                    if (count >= steps) {{ clearInterval(fade); audA.pause(); }}
                    else {{ 
                        if (audA.volume > volStep) audA.volume -= volStep;
                        if (audB.volume < 1-volStep) audB.volume += volStep;
                        count++;
                    }}
                }}, interval);
            }}
        </script>
    </div>
    """
    st.components.v1.html(mixer_html, height=550)
                        
 
    st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | Synapse Studio v.1")
elif st.session_state.page == "2":
    from streamlit_autorefresh import st_autorefresh
    
    # --- [ จุดสำคัญ: ระบบ AUTO REFRESH ] ---
    # สั่งให้หน้านี้รีเฟรชตัวเองทุก 8 วินาที เพื่อดึงแชตและพิกัดใหม่
    # (ไม่ตั้งให้เร็วเกินไป เพื่อป้องกันหน้าจอกะพริบจนใช้งานลำบาก)
    st_autorefresh(interval=8000, key="synapse_update")

    st.markdown("<h2 style='text-align:center; color:#00f3ff; font-family:Orbitron;'>🛰️ TACTICAL RADAR & PRIVATE CHAT</h2>", unsafe_allow_html=True)

    # --- ส่วนที่ 1: RADAR (GPS) ---
    from streamlit_js_eval import get_geolocation
    from streamlit_folium import st_folium
    import folium

    loc = get_geolocation()
    my_lat, my_lon = 13.7367, 100.5231 # Default BKK
    if loc and 'coords' in loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']

    # แสดงแผนที่ Satellite
    m = folium.Map(location=[my_lat, my_lon], zoom_start=15, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                   attr='Google Satellite')
    
    folium.Marker([my_lat, my_lon], icon=folium.Icon(color='red', icon='star'), tooltip="YOU").add_to(m)

    # ดึงพิกัดเพื่อนๆ จาก Firebase
    try:
        users_ref = db.reference('users').get()
        if users_ref:
            for uid, data in users_ref.items():
                if uid != st.session_state.user and 'lat' in data:
                    folium.Marker([data['lat'], data['lon']], 
                                 icon=folium.Icon(color='blue'), 
                                 tooltip=f"AGENT: {uid}").add_to(m)
    except: pass

    st_folium(m, width="100%", height=300)

    # ปุ่ม Broadcast พิกัดตัวเอง
    if st.button("📡 BROADCAST POSITION", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.toast("พิกัดถูกส่งแล้ว!")

    st.write("---")

    # --- ส่วนที่ 2: PRIVATE CHAT ---
    st.markdown("<h4 style='color:#ff00de; font-family:Orbitron;'>🔐 PRIVATE SECURE CHAT</h4>", unsafe_allow_html=True)

    try:
        all_users = db.reference('users').get()
        if all_users:
            friends = [u for u in all_users.keys() if u != st.session_state.user]
            target_agent = st.selectbox("🎯 เลือก AGENT ที่ต้องการติดต่อ:", friends)

            if target_agent:
                # สร้าง ID ห้องแบบคู่ (เช่น user1_user2)
                room_id = "_".join(sorted([st.session_state.user, target_agent]))
                chat_ref = db.reference(f'private_messages/{room_id}')

                # ฟอร์มส่งข้อความ
                with st.form("private_chat_form", clear_on_submit=True):
                    msg = st.text_input(f"TO: {target_agent}", placeholder="พิมพ์ข้อความที่นี่...")
                    if st.form_submit_button("SEND SIGNAL"):
                        if msg:
                            chat_ref.push({
                                'sender': st.session_state.user,
                                'text': msg,
                                'ts': time.time()
                            })
                            st.rerun()

                # แสดงผลข้อความล่าสุด 10 ข้อความ
                messages = chat_ref.order_by_child('ts').limit_to_last(10).get()
                if messages:
                    for mid in reversed(list(messages.keys())):
                        m_data = messages[mid]
                        is_me = m_data['sender'] == st.session_state.user
                        align = "right" if is_me else "left"
                        color = "#00f3ff" if is_me else "#ff00de"
                        bg = "rgba(0, 243, 255, 0.15)" if is_me else "rgba(255, 0, 222, 0.15)"
                        
                        st.markdown(f"""
                            <div style="text-align:{align}; margin-bottom:10px;">
                                <div style="display:inline-block; background:{bg}; padding:8px 15px; border-radius:15px; border:1px solid {color};">
                                    <b style="color:{color}; font-size:0.75rem;">{m_data['sender']}</b><br>
                                    <span style="color:white;">{m_data['text']}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("ระบบพร้อมสำหรับการสื่อสารลับ...")
    except Exception as e:
        st.error(f"ระบบขัดข้อง: {e}")

    st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | Tactical Module v.2 (Auto-Update)")
elif st.session_state.page == "3":
    st.markdown("<h2 style='color:#00ff41; font-family:Orbitron;'>🧬 PERSONAL CODE DECODER</h2>", unsafe_allow_html=True)
    
    # ส่วนรับข้อมูล: ช่วงปี 1960 - 2026
    dob = st.date_input("📅 ระบุวันเกิดเพื่อถอดรหัส", 
                        min_value=date(1960, 1, 1), 
                        max_value=date(2026, 12, 31))

    if dob:
        d = get_detailed_logic(dob)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("YOUR CODE", d['res'])
        with col2:
            st.info(f"พิกัด: วัน{d['day_name']} | {d['phase']}")

        # --- อธิบายที่มาของตัวเลข (ความจริง) ---
        st.markdown(f"""
        <div class="logic-box">
            <h4>📝 ที่มาของรหัสประจำตัว (The Truth)</h4>
            <ul>
                <li><b>เลขฐานวัน ({d['day_val']}):</b> มาจากลำดับวันในสัปดาห์ (จันทร์=1 จนถึง อาทิตย์=7)</li>
                <li><b>เลขจันทรคติ ({d['m_num']}):</b> คำนวณจากระยะห่างระหว่างวันเกิดกับจุด New Moon ของดาราศาสตร์</li>
                <li><b>วิธีคำนวณ:</b> ระบบใช้ <b>{d['type']}</b></li>
                <li><b>สมการที่ใช้จริง:</b> <code>{d['formula']}</code></li>
            </ul>
            <p style='font-size:0.8rem; color:#888;'>*หมายเหตุ: ขึ้นค่ำใช้สมการ Vector (ความชัน), แรมค่ำใช้สมการ Golden Ratio (สมดุล)*</p>
        </div>
        """, unsafe_allow_html=True)
elif st.session_state.page == "6":
    import streamlit.components.v1 as components
    
    st.markdown("<h2 style='text-align:center; color:#FFD700; font-family:Orbitron;'>⚡ SYNAPSE VIBRATION UNIT</h2>", unsafe_allow_html=True)
    
    # 1. สร้าง Tab สำหรับแยกการวัด
    tab_sonic, tab_motion, tab_power = st.tabs(["🎙️ SONIC SCAN", "📳 MOTION SCAN", "🔋 POWER INFO"])

    with tab_sonic:
        st.subheader("🎙️ REAL-TIME SONIC ANALYZER")
        # โค้ดวัดเสียง (ดึง dB และ Hz)
        audio_js = """
        <div style="background-color: #111; color: #FFD700; padding: 20px; border: 2px solid #FFD700; border-radius: 15px; text-align: center; font-family: monospace;">
            <div style="display: flex; justify-content: space-around;">
                <div><small>ความดัง</small><h1 id="db_val" style="font-size: 40px; color:#0f0;">0</h1><small>เดซิเบล (dB)</small></div>
                <div><small>ความถี่</small><h1 id="hz_val" style="font-size: 40px; color:#00ffff;">0</h1><small>เฮิรตซ์ (Hz)</small></div>
            </div>
            <p id="audio_status" style="margin-top:10px; color:#888;">🔴 รอสัญญาณเสียง...</p>
        </div>
        <script>
            async function startAudio() {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    const analyser = audioCtx.createAnalyser();
                    const source = audioCtx.createMediaStreamSource(stream);
                    source.connect(analyser);
                    analyser.fftSize = 2048;
                    const dataArray = new Uint8Array(analyser.frequencyBinCount);
                    function update() {
                        analyser.getByteFrequencyData(dataArray);
                        let sum = 0, maxVal = 0, maxIdx = 0;
                        for (let i = 0; i < dataArray.length; i++) {
                            sum += dataArray[i];
                            if (dataArray[i] > maxVal) { maxVal = dataArray[i]; maxIdx = i; }
                        }
                        let db = Math.round(sum / dataArray.length * 2);
                        let hz = Math.round(maxIdx * audioCtx.sampleRate / analyser.fftSize);
                        document.getElementById('db_val').innerText = db;
                        document.getElementById('hz_val').innerText = hz;
                        document.getElementById('audio_status').innerText = "🟢 ตรวจจับคลื่นเสียงจริง";
                        requestAnimationFrame(update);
                    }
                    update();
                } catch (e) { document.getElementById('audio_status').innerText = "❌ เข้าถึงไมค์ไม่ได้"; }
            }
            startAudio();
        </script>
        """
        components.html(audio_js, height=250)
        st.info("**ที่มาของตัวเลข (The Truth):** ค่าความถี่ (Hz) วัดจากรอบการสั่นของอากาศที่กระทบไมค์จริง ไม่มีการจำลอง")

    with tab_motion:
        st.subheader("📳 MOTION & VIBRATION SENSOR")
        # โค้ดวัดแรงสั่น (G-Force)
        motion_js = """
        <div style="background-color: #111; color: #FFD700; padding: 20px; border: 2px solid #FFD700; border-radius: 15px; text-align: center; font-family: monospace;">
            <small>แรงสั่นสะเทือนรวม (Magnitude)</small>
            <h1 id="mag_val" style="font-size: 50px; color: #0f0;">1.000</h1>
            <p>G-Force</p>
            <p id="motion_info" style="color: #888;">สถานะ: รอนิ่ง...</p>
        </div>
        <script>
            window.addEventListener('devicemotion', (e) => {
                const acc = e.accelerationIncludingGravity;
                if (!acc) return;
                let magnitude = Math.sqrt(acc.x**2 + acc.y**2 + acc.z**2) / 9.80665;
                document.getElementById('mag_val').innerText = magnitude.toFixed(3);
                document.getElementById('mag_val').style.color = (magnitude > 1.05 || magnitude < 0.95) ? "#f00" : "#0f0";
            });
        </script>
        """
        components.html(motion_js, height=250)
        st.info("**ที่มาของตัวเลข (The Truth):** วัดจากเซนเซอร์ Accelerometer ภายในเครื่อง ยึดตามแรงโน้มถ่วงโลก (1G) เป็นเกณฑ์")

    with tab_power:
        # ส่วนแบตเตอรี่ (Power) ที่แกมีอยู่แล้ว
        st.write("ระบบวิเคราะห์พลังงานสำรอง")
        # components.html(battery_js, height=300)

    st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | VIBRATION ENGINE v.1.2")
        
elif st.session_state.page == "4":
    st.markdown("<h2 style='color:#00ff41; font-family:Orbitron;'>🛰️ PARALLEL SCANNER</h2>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        dob1 = st.date_input("วันเกิด AGENT 1", min_value=date(1960,1,1), max_value=date(2026,12,31), key="p1")
    with c2:
        dob2 = st.date_input("วันเกิด AGENT 2", min_value=date(1960,1,1), max_value=date(2026,12,31), key="p2")

    if dob1 and dob2:
        d1 = get_detailed_logic(dob1)
        d2 = get_detailed_logic(dob2)
        gap = abs(d1['res'] - d2['res'])

        st.divider()
        st.subheader(f"🔍 ค่าความต่างพิกัด (Gap): {gap:.4f}")
        
        # อธิบายที่มาของ Gap
        st.markdown(f"""
        <div class="logic-box" style="border-left-color: #ff7f50;">
            <h4>📊 การถอดค่าความสัมพันธ์</h4>
            คำนวณจาก: <code>|รหัสคนแรก ({d1['res']}) - รหัสคนที่สอง ({d2['res']})|</code><br><br>
            <b>เกณฑ์การอ่านค่าที่เกิดขึ้นจริง:</b>
            <ul>
                <li><b>0.0 - 1.0 (รหัสแฝด):</b> ความถี่ใกล้กันมาก มักคุยกันรู้เรื่องเร็ว</li>
                <li><b>3.8 - 4.2 (สัญญาณสะท้อน):</b> ค่า Gap 4 ตามหลัก Synapse คือแรงดึงดูดที่มองไม่เห็น</li>
                <li><b>มากกว่า 10.0 (แยกตัว):</b> พลังงานอิสระต่อกัน ไม่ผูกมัด</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
elif st.session_state.page == "5":
    st.markdown("<h2 style='color:#00ff41; font-family:Orbitron; text-align:center;'>🔮 DESTINY TIMELINE</h2>", unsafe_allow_html=True)
    
    # ส่วนรับข้อมูล (1960-2026)
    user_dob = st.date_input("📅 กรอกวันเกิดเพื่อสแกนหาพิกัดเพชร/ธรรม/กระจก", 
                             min_value=date(1960,1,1), 
                             max_value=date(2026,12,31), key="t1")

    if user_dob:
        d_logic = get_detailed_logic(user_dob)
        my_code = d_logic['res']
        
        st.write(f"🧬 รหัสประจำตัวของคุณคือ: **{my_code}**")
        
        # --- เริ่มการสแกน 180 วัน ---
        future_results = []
        for i in range(180):
            target_date = date.today() + timedelta(days=i)
            d = get_detailed_logic(target_date)
            gap = abs(d['res'] - my_code)
            
            # การแบ่งประเภทตามหลักอาจารย์ต๊ะ
            status = "อิสระ"
            symbol = "⚪"
            if gap < 0.5: 
                status = "💎 พิกัดเพชร (บรรจบ/โอกาส)"
                symbol = "💎"
            elif 3.8 <= gap <= 4.2: 
                status = "🌀 พิกัดธรรม (สะท้อน/ดึงดูด)"
                symbol = "🌀"
            elif gap > 10.0: 
                status = "🪞 พิกัดกระจก (แยกตัว/อิสระ)"
                symbol = "🪞"
            
            if status != "อิสระ":
                future_results.append({
                    "วันที่": target_date.strftime('%d/%m/%Y'),
                    "วัน": d['day_name'],
                    "ประเภทพิกัด": status,
                    "ค่า Gap": round(gap, 4),
                    "สัญลักษณ์": symbol
                })

        # แสดงตารางผลลัพธ์
        if future_results:
            df = pd.DataFrame(future_results)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("ไม่พบพิกัดพิเศษในช่วง 180 วันนี้ (ช่วงเวลาปกติ)")

        # --- ส่วนอธิบายที่มาของ "เพชร/ธรรม/กระจก" (ความจริงสำหรับคนใหม่) ---
        st.write("---")
        with st.expander("📝 คู่มืออ่านพิกัดรหัส (ที่มาของตัวเลข)", expanded=True):
            st.markdown(f"""
            <div class="logic-box">
                <h4>🔍 ความหมายของพิกัดที่คุณเห็น:</h4>
                <ol>
                    <li><b>💎 พิกัดเพชร (Gap < 0.5):</b> <br>
                        คือวันที่รหัสจักรวาล (Computed Code) วิ่งมาทับกับรหัสคุณพอดี เหมือนเพชรที่เจียระไนลงตัว เป็นวันแห่งการ <b>"บรรจบ"</b> หรือเริ่มต้นสิ่งใหม่</li>
                    <li><b>🌀 พิกัดธรรม (Gap 3.8 - 4.2):</b> <br>
                        คือวันที่เกิดค่าสะท้อน (Reflection) ตามกฎเลข 4 ของระบบ Synapse เป็นวันที่มีแรงดึงดูดสูง มักมีเรื่องไม่คาดฝันหรือ <b>"ธรรมะจัดสรร"</b> ให้เจอ</li>
                    <li><b>🪞 พิกัดกระจก (Gap > 10.0):</b> <br>
                        คือวันที่รหัสดีดตัวออกจากกันจนสุดขอบ เหมือนกระจกที่สะท้อนภาพออกไปคนละทาง เป็นวันแห่งการ <b>"แยกตัว"</b> หรือการเป็นอิสระจากพันธนาการ</li>
                </ol>
                <hr>
                <p><b>ที่มาของตัวเลข:</b> ทั้งหมดคำนวณจาก <code>|รหัสประจำตัว - รหัสประจำวัน|</code> โดยรหัสแต่ละวันมาจากการคำนวณตำแหน่งดวงจันทร์และฐานวันจริงทางดาราศาสตร์</p>
            </div>
        """, unsafe_allow_html=True)
elif st.session_state.page == "6":
    import streamlit.components.v1 as components # ต้องมีตัวนี้เพื่อรัน JS
    
    st.markdown("<h2 style='text-align:center; color:#FFD700; font-family:Orbitron;'>⚡ SYNAPSE SENSOR UNIT</h2>", unsafe_allow_html=True)
    
    # 1. นิยามโค้ด JavaScript สำหรับเซนเซอร์ (ถ้ายังไม่มีให้ก๊อปอันนี้ไปวาง)
    bio_js = """
    <div style="background-color: #111; color: #FFD700; padding: 15px; border: 2px solid #FFD700; border-radius: 15px; font-family: monospace;">
        <video id="v" style="display:none;" autoplay playsinline></video>
        <canvas id="c" width="100" height="100" style="display:none;"></canvas>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: center;">
            <div style="border: 1px solid #333; padding: 10px;">
                <small>BPM</small><h2 id="bpm" style="color:#0f0;">--</h2><small>ครั้ง/นาที</small>
            </div>
            <div style="border: 1px solid #333; padding: 10px;">
                <small>SpO2</small><h2 id="spo2" style="color:#00ffff;">--</h2><small>%</small>
            </div>
            <div style="border: 1px solid #333; padding: 10px;">
                <small>PI</small><h2 id="pi">0.0</h2><small>Index</small>
            </div>
            <div style="border: 1px solid #333; padding: 10px;">
                <small>RGB</small><h2 id="rgb" style="font-size: 14px;">0,0,0</h2><small>R,G,B</small>
            </div>
        </div>
        <div id="status" style="margin-top: 10px; text-align: center; color: #f00;">🔴 รอการสแกนปลายนิ้ว...</div>
    </div>
    <script>
        // ... (ใส่ Script ที่ผมเคยให้ไว้สำหรับเริ่มกล้องและคำนวณค่า) ...
    </script>
    """

    tab_bio, tab_env, tab_power = st.tabs(["🩸 BIO-SCAN", "🎨 ENV-SCAN", "🔋 POWER-SCAN"])

    with tab_bio:
        st.markdown("### 🩸 REAL-TIME BIO-DATA SCANNER")
        
        # --- จุดที่หายไปคือบรรทัดนี้ครับ! ---
        components.html(bio_js, height=300) 
        # ----------------------------------
        
        st.info("**ที่มาของตัวเลข (The Truth):** ...")

# --- [ ห้องที่ 7: DESTINY CHECK (ตรวจดวงชะตาคู่ขนาน) ] ---
elif st.session_state.page == "7":
    st.markdown("<h2 style='text-align:center; color:#ff00de; font-family:Orbitron;'>💖 DESTINY CHECK (DIMENSION 4)</h2>", unsafe_allow_html=True)
    st.write("วิเคราะห์ความสัมพันธ์ผ่านระบบผลรวมรหัสตัวอักษร (Unicode Hash)")

    col1, col2 = st.columns(2)
    with col1:
        name1 = st.text_input("ชื่อ AGENT 1:", placeholder="ระบุชื่อคนที่ 1")
    with col2:
        name2 = st.text_input("ชื่อ AGENT 2:", placeholder="ระบุชื่อคนที่ 2")

    if st.button("⚡ เดินเครื่องสแกนความถี่", use_container_width=True):
        if name1 and name2:
            # ใช้หลักการความจริง: แปลงตัวอักษรเป็นค่าตัวเลข Unicode แล้วหาผลรวม
            score1 = sum(ord(char) for char in name1)
            score2 = sum(ord(char) for char in name2)
            
            # คำนวณส่วนต่างและหาค่าความเข้ากันได้ (คิดเป็นเปอร์เซ็นต์แบบมีตรรกะ)
            gap = abs(score1 - score2)
            # เอา gap มา mod ด้วย 100 เพื่อให้อยู่ในสเกล 0-99 แล้วลบออกจาก 100
            match_percent = 100 - (gap % 100)
            
            st.divider()
            st.metric("ระดับความสอดคล้องของคลื่นความถี่ (Synchronization)", f"{match_percent} %")
            
            # อธิบายความจริงให้ผู้ใช้รู้ว่าเลขมาจากไหน
            st.markdown(f"""
            <div style="background: rgba(255, 0, 222, 0.1); border-left: 4px solid #ff00de; padding: 10px; border-radius: 5px;">
                <h4 style="color:#ff00de;">📝 ที่มาของตัวเลข (The Truth)</h4>
                <ul>
                    <li><b>พลังงานชื่อที่ 1:</b> {score1} (ผลรวม Unicode)</li>
                    <li><b>พลังงานชื่อที่ 2:</b> {score2} (ผลรวม Unicode)</li>
                    <li><b>ส่วนต่าง (Gap):</b> {gap}</li>
                    <li><b>สูตรคณิตศาสตร์:</b> <code>100 - ({gap} % 100)</code> = {match_percent}%</li>
                </ul>
                <p style="font-size: 0.8rem; color:#ccc;">เราไม่ใช้ AI สุ่มตัวเลขเดาใจ แต่เราใช้ค่ารหัสคอมพิวเตอร์ที่ตายตัวของชื่อคุณทั้งสองคน</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("กรุณาระบุชื่อเป้าหมายทั้งสองให้ครบถ้วน")

# --- [ ห้องที่ 8: DAILY CODE (รหัสลับประจำวัน) ] ---
elif st.session_state.page == "8":
    st.markdown("<h2 style='text-align:center; color:#00f3ff; font-family:Orbitron;'>🔢 DAILY SECURITY CODE</h2>", unsafe_allow_html=True)
    
    # 1. ตรวจสอบพิกัดเวลาปัจจุบัน
    today_str = date.today().strftime("%Y-%m-%d")
    st.write(f"📅 พิกัดเวลาปัจจุบัน: **{today_str}**")
    
    # 2. ดึงชื่อผู้ใช้แบบปลอดภัย (หัวใจสำคัญที่ทำให้ไม่พัง)
    # ถ้ายังไม่ได้ Login หรือหาชื่อไม่เจอ ให้ใช้ 'Guest_Agent' แทน
    current_agent = st.session_state.get('user', 'Guest_Agent')
    
    # 3. สร้างวัตถุดิบสำหรับทำรหัส (ประกาศตัวแปรให้ชัดเจนก่อนเรียกใช้)
    raw_data = f"{today_str}_{current_agent}_SYNAPSE"
    
    try:
        # 4. บรรทัดที่เคยพัง (717): ตอนนี้ raw_data จะมีค่าแน่นอนแล้ว
        hash_object = hashlib.sha256(raw_data.encode('utf-8')).hexdigest()
        
        # 5. แปลง Hash เป็นรหัสตัวเลข
        daily_4_digit = str(int(hash_object[:4], 16))[-4:].zfill(4)
        daily_6_digit = str(int(hash_object[4:10], 16))[-6:].zfill(6)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style="text-align:center; border: 2px solid #00f3ff; padding: 20px; border-radius: 15px; background: rgba(0, 243, 255, 0.05);">
                <small style="color:#00f3ff;">ACCESS PIN (4 DIGIT)</small>
                <h1 style="color:#fff; font-family: monospace;">{daily_4_digit}</h1>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div style="text-align:center; border: 2px solid #ff00de; padding: 20px; border-radius: 15px; background: rgba(255, 0, 222, 0.05);">
                <small style="color:#ff00de;">MASTER KEY (6 DIGIT)</small>
                <h1 style="color:#fff; font-family: monospace;">{daily_6_digit}</h1>
            </div>
            """, unsafe_allow_html=True)

        st.info(f"**สถานะ:** กำลังใช้รหัสเฉพาะของ AGENT: **{current_agent}**")

    except Exception as e:
        # ถ้าพังอีก ให้แสดง Error แบบนุ่มนวลแทนการหยุดทำงาน
        st.error(f"ระบบถอดรหัสขัดข้อง: {e}")

    st.caption("รหัสจะเปลี่ยนโดยอัตโนมัติทุกๆ 24 ชั่วโมง ตามพิกัดเวลาโลก")


# --- [ ห้องที่ 9: SYSTEM LOG (บันทึกข้อมูลการใช้งาน) ] ---
elif st.session_state.page == "9":
    st.markdown("<h2 style='text-align:center; color:#50C878; font-family:Orbitron;'>📝 SYNAPSE MEMORY LOG</h2>", unsafe_allow_html=True)
    st.write("บันทึกเหตุการณ์ลงฐานข้อมูล Firebase โดยตรง")

    with st.form("log_form", clear_on_submit=True):
        log_entry = st.text_area("✍️ ข้อความบันทึก:", placeholder="พิมพ์สิ่งที่คุณต้องการจดจำ...")
        submit_log = st.form_submit_button("💾 SAVE TO CLOUD")
        
        if submit_log and log_entry:
            try:
                # ดันข้อมูลเข้า Firebase ใต้ UID ของตัวเอง
                db.reference(f'system_logs/{st.session_state.user}').push({
                    'text': log_entry,
                    'timestamp': time.time(),
                    'datetime': str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                })
                st.success("บันทึกข้อมูลเข้าสู่ศูนย์บัญชาการเรียบร้อย!")
            except Exception as e:
                st.error(f"ระบบฐานข้อมูลขัดข้อง: {e}")

    st.divider()
    st.markdown("#### 📂 บันทึกล่าสุดของคุณ")
    try:
        # ดึงข้อมูล 5 อันดับล่าสุดมาแสดง
        my_logs = db.reference(f'system_logs/{st.session_state.user}').order_by_child('timestamp').limit_to_last(5).get()
        if my_logs:
            for key, val in reversed(list(my_logs.items())):
                st.markdown(f"""
                <div style="background: rgba(80, 200, 120, 0.1); border-left: 3px solid #50C878; padding: 10px; margin-bottom: 10px;">
                    <small style="color:#50C878;">🕒 {val.get('datetime', 'N/A')}</small><br>
                    <span style="color: white;">{val.get('text', '')}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("ยังไม่มีข้อมูลบันทึกในระบบ")
    except:
        st.warning("ไม่สามารถดึงประวัติได้ ตรวจสอบการเชื่อมต่อ Firebase")


# --- [ ห้องที่ 10: COLOR MASTER (ปรับแต่งธีมสีระบบ) ] ---
elif st.session_state.page == "10":
    st.markdown("<h2 class='neon-text' style='color:var(--primary); text-shadow: 0 0 20px var(--primary);'>🎨 MULTI-COLOR INTERFACE</h2>", unsafe_allow_html=True)
    st.write("ปรับแต่งรังสีออร่าแยกส่วนของระบบ Synapse")

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.session_state.main_color = st.color_picker("🔵 สีหลัก (Primary Neon)", st.session_state.main_color)
        st.session_state.bg_glow = st.color_picker("✨ สีเรืองแสงพื้นหลัง", "#0015ff") # ตัวแปรใหม่
    with col_c2:
        st.session_state.sub_color = st.color_picker("🔴 สีรอง (Secondary Neon)", st.session_state.sub_color)
        st.info("สีที่เลือกจะถูกกระจายไปยังทุกโมดูล (DJ, Radar, Timeline) ทันที")

    if st.button("🔥 APPLY ALL DIMENSIONS (รีเซ็ตสีทั่วแอป)", use_container_width=True):
        st.balloons()
        st.rerun()

    # ตัวอย่างการแสดงผล
    st.markdown(f"""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 20px;">
            <div style="border: 2px solid var(--primary); padding: 20px; text-align: center; border-radius: 10px; box-shadow: 0 0 15px var(--primary);">
                <b style="color:var(--primary);">PRIMARY UNIT</b>
            </div>
            <div style="border: 2px solid var(--secondary); padding: 20px; text-align: center; border-radius: 10px; box-shadow: 0 0 15px var(--secondary);">
                <b style="color:var(--secondary);">SECONDARY UNIT</b>
            </div>
        </div>
    """, unsafe_allow_html=True)

    
    st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | Synapse Interface Control")


# (เพิ่ม elif ไปจนครบหน้า 10 ตามโครงเดิมได้เลยครับ...)

if 'primary_color' not in st.session_state:
    st.session_state.primary_color = "#00f3ff"
if 'page' not in st.session_state:
    st.session_state.page = "HOME"

ผมอยากให้เอาไว้ตอนนี้คือ.ห้อง1.เพลง
ห้อง6.แชต กุับ GPS
ิห้อง10.การเปรียนสี
และห้องเครื่องวัดเสียงและการสัน

ที่เหลือ.เอามาอยู่ห้องเดียวกันเลยครับ.เพราะสูตรการคำนวนมันอันเดียวดัน.เราเอามาอยู่ในห้องเดียวกัน.แลวะแยกหัวข้อได้ใช้ใไหมครับ
import streamlit as st
import streamlit.components.v1 as components
import os
import base64

# ฟังก์ชันช่วยแปลงไฟล์ (ต้องมีอยู่ในโค้ดหลักของคุณ)
def get_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

# สมมติค่าตัวแปรเบื้องต้น
primary_neon = "#00FFCC"

if "page" not in st.session_state:
    st.session_state.page = "1"

if st.session_state.page == "1":
    st.markdown("<h2 style='color:#00FFCC; font-family:monospace;'>🎧 SYNAPSE DJ STATION V.3</h2>", unsafe_allow_html=True)
    
    all_songs = [f for f in os.listdir('.') if f.lower().endswith('.mp3')]
    
    if not all_songs:
        st.warning("⚠️ ไม่พบไฟล์ .mp3 ในระบบ")
    else:
        col_sel_a, col_sel_b = st.columns(2)
        with col_sel_a:
            song_a = st.selectbox("💿 DECK A (LEFT)", ["-- Select --"] + all_songs, key="sa")
        with col_sel_b:
            song_b = st.selectbox("💿 DECK B (RIGHT)", ["-- Select --"] + all_songs, key="sb")

        data_a = get_base64(song_a) if song_a != "-- Select --" else ""
        data_b = get_base64(song_b) if song_b != "-- Select --" else ""

        mixer_html = f"""
        <div style="background: #000; border: 2px solid {primary_neon}; border-radius: 20px; padding: 15px; font-family: monospace; color: white;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                <div style="border: 1px solid {primary_neon}; padding: 10px; border-radius: 15px; text-align: center;">
                    <div style="display: flex; justify-content: space-between; font-size: 10px; color: {primary_neon};">
                        <span id="curA">00:00</span><span id="remA">-00:00</span>
                    </div>
                    <canvas id="canvasA" style="width: 100%; height: 60px; background: #111; margin: 5px 0; border-radius:5px;"></canvas>
                    <input type="range" id="volA" min="0" max="1" step="0.01" value="0.7" style="width: 100%;">
                    <div style="margin-top: 10px;">
                        <button onclick="control('A', 'play')" style="background:{primary_neon}; border:none; padding:5px 10px; border-radius:5px; cursor:pointer;">PLAY</button>
                        <button onclick="control('A', 'pause')" style="background:none; border:1px solid {primary_neon}; color:{primary_neon}; padding:5px 10px; border-radius:5px; cursor:pointer;">PAUSE</button>
                    </div>
                </div>

                <div style="border: 1px solid #FF44CC; padding: 10px; border-radius: 15px; text-align: center;">
                    <div style="display: flex; justify-content: space-between; font-size: 10px; color: #FF44CC;">
                        <span id="curB">00:00</span><span id="remB">-00:00</span>
                    </div>
                    <canvas id="canvasB" style="width: 100%; height: 60px; background: #111; margin: 5px 0; border-radius:5px;"></canvas>
                    <input type="range" id="volB" min="0" max="1" step="0.01" value="0.7" style="width: 100%;">
                    <div style="margin-top: 10px;">
                        <button onclick="control('B', 'play')" style="background:#FF44CC; border:none; padding:5px 10px; border-radius:5px; color:white; cursor:pointer;">PLAY</button>
                        <button onclick="control('B', 'pause')" style="background:none; border:1px solid #FF44CC; color:#FF44CC; padding:5px 10px; border-radius:5px; cursor:pointer;">PAUSE</button>
                    </div>
                </div>
            </div>

            <div style="margin-top:20px; text-align:center;">
                <small>CROSSFADER (A <-> B)</small><br>
                <input type="range" id="fader" min="0" max="1" step="0.01" value="0.5" style="width: 80%;">
            </div>

            <audio id="audioA" src="data:audio/mp3;base64,{data_a}"></audio>
            <audio id="audioB" src="data:audio/mp3;base64,{data_b}"></audio>

            <script>
                const audA = document.getElementById('audioA');
                const audB = document.getElementById('audioB');
                const fader = document.getElementById('fader');
                let audioCtx;
                let analyserA, analyserB;
                let sourceA, sourceB;

                function initAudio() {{
                    if (!audioCtx) {{
                        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                        
                        // Setup Deck A
                        analyserA = audioCtx.createAnalyser();
                        sourceA = audioCtx.createMediaElementSource(audA);
                        sourceA.connect(analyserA);
                        analyserA.connect(audioCtx.destination);
                        
                        // Setup Deck B
                        analyserB = audioCtx.createAnalyser();
                        sourceB = audioCtx.createMediaElementSource(audB);
                        sourceB.connect(analyserB);
                        analyserB.connect(audioCtx.destination);

                        startVisualizer('canvasA', analyserA, '{primary_neon}');
                        startVisualizer('canvasB', analyserB, '#FF44CC');
                    }}
                }}

                function startVisualizer(canvasID, analyser, color) {{
                    const canvas = document.getElementById(canvasID);
                    const ctx = canvas.getContext('2d');
                    analyser.fftSize = 64;
                    const bufferLength = analyser.frequencyBinCount;
                    const dataArray = new Uint8Array(bufferLength);

                    function draw() {{
                        requestAnimationFrame(draw);
                        analyser.getByteFrequencyData(dataArray);
                        ctx.clearRect(0, 0, canvas.width, canvas.height);
                        let barWidth = (canvas.width / bufferLength) * 2.5;
                        let x = 0;
                        for(let i = 0; i < bufferLength; i++) {{
                            let barHeight = dataArray[i] / 5;
                            ctx.fillStyle = color;
                            ctx.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
                            x += barWidth + 1;
                        }}
                    }}
                    draw();
                }}

                function control(deck, action) {{
                    initAudio();
                    if (audioCtx.state === 'suspended') audioCtx.resume();
                    const target = (deck === 'A') ? audA : audB;
                    if (action === 'play') target.play();
                    else target.pause();
                }}

                // Volume & Fader Logic
                function updateVolumes() {{
                    const volA = document.getElementById('volA').value;
                    const volB = document.getElementById('volB').value;
                    const f = parseFloat(fader.value);
                    audA.volume = volA * (1 - f);
                    audB.volume = volB * f;
                }}

                fader.oninput = updateVolumes;
                document.getElementById('volA').oninput = updateVolumes;
                document.getElementById('volB').oninput = updateVolumes;

                // Time Update
                const updateUI = (aud, cur, rem) => {{
                    aud.ontimeupdate = () => {{
                        const fmt = s => new Date(s * 1000).toISOString().substr(14, 5);
                        document.getElementById(cur).innerText = fmt(aud.currentTime);
                        if(aud.duration) document.getElementById(rem).innerText = "-" + fmt(aud.duration - aud.currentTime);
                    }};
                }}
                updateUI(audA, 'curA', 'remA');
                updateUI(audB, 'curB', 'remB');
            </script>
        </div>
        """
        components.html(mixer_html, height=450)
        st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | Tactical Sound Module v4.2")

import streamlit as st
import base64

# ==========================================
# ส่วนที่ 1: การตั้งค่าหน้าจอและ CSS (กู้คืนสีสัน Neon ขั้นสุด)
# ==========================================

st.set_page_config(page_title="Synapse Neon Mixer", layout="centered")

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except: return ""

logo_base64 = get_base64_image("logo1.png")
logo_html_link = f"data:image/png;base64,{logo_base64}" if logo_base64 else ""

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    .stApp {{ background-color: #000; }}

    /* Logo ตรงกลางพร้อมแสง Neon หมุนสลับสี */
    .block-container::before {{
        content: "";
        position: absolute;
        top: 10px; left: 50%;
        transform: translateX(-50%);
        width: 100px; height: 100px;
        background-image: url("{logo_html_link}");
        background-size: contain;
        background-repeat: no-repeat;
        z-index: 999;
        filter: drop-shadow(0 0 10px #ff00de);
        animation: logo-glow 4s infinite alternate;
    }}

    @keyframes logo-glow {{
        0% {{ filter: drop-shadow(0 0 10px #ff00de); transform: translateX(-50%) scale(1); }}
        50% {{ filter: drop-shadow(0 0 25px #00f3ff); transform: translateX(-50%) scale(1.1); }}
        100% {{ filter: drop-shadow(0 0 10px #ff8c00); transform: translateX(-50%) scale(1); }}
    }}

    .neon-title {{
        font-family: 'Orbitron', sans-serif;
        color: #fff;
        text-align: center;
        text-shadow: 0 0 10px #ff00de, 0 0 20px #00f3ff;
        font-size: 1.6rem;
        margin-top: 110px;
        letter-spacing: 3px;
        animation: text-flicker 2s infinite;
    }}
    @keyframes text-flicker {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.8; }}
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="neon-title">SYNAPSE NEON MIXER</h1>', unsafe_allow_html=True)

# ==========================================
# ส่วนที่ 2: HTML/JS - ระบบเล่นต่อเนื่อง + สีสันสะบัด
# ==========================================

html_code = """
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background: transparent; color: white; overflow: hidden; font-family: 'Inter', sans-serif; }
        .neon-card { border: 2px solid #333; background: rgba(0,0,0,0.9); box-shadow: 0 0 30px rgba(255,0,222,0.2); }
        
        /* กราฟเสียงสีรุ้งสะบัด */
        .visualizer-box { height: 150px; background: #050505; border-radius: 15px; border: 1px solid #222; }
        
        .deck { padding: 15px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 10px; transition: 0.5s; }
        .deck-active { border: 1px solid #00f3ff; box-shadow: 0 0 15px #00f3ff; background: rgba(0,243,255,0.05); }
        
        /* ปุ่มสไตล์ Cyberpunk */
        .btn-mix { 
            background: linear-gradient(45deg, #ff00de, #00f3ff);
            color: white; font-weight: bold; padding: 12px; border-radius: 10px;
            text-transform: uppercase; letter-spacing: 2px; transition: 0.3s;
            box-shadow: 0 0 15px rgba(255,0,222,0.4);
        }
        .btn-mix:hover { transform: scale(1.05); box-shadow: 0 0 25px rgba(0,243,255,0.6); }
        
        .progress-bar { height: 6px; background: #222; border-radius: 10px; overflow: hidden; }
        .progress-inner { height: 100%; width: 0%; background: linear-gradient(90deg, #ff00de, #ff8c00); }
    </style>
</head>
<body>
    <div class="max-w-md mx-auto p-4 neon-card rounded-3xl">
        <canvas id="scope" class="visualizer-box w-full mb-4"></canvas>

        <div id="cardA" class="deck">
            <div class="flex justify-between text-[10px] mb-2">
                <span id="labelA" class="text-pink-500 font-bold">DECK A</span>
                <span id="timeA" class="font-mono">00:00</span>
            </div>
            <input type="file" id="inA" class="hidden" onchange="handleFile(this.files[0], 'A')">
            <button onclick="document.getElementById('inA').click()" class="text-[10px] border border-gray-600 px-3 py-1 rounded">LOAD A</button>
            <div id="nameA" class="text-[11px] mt-1 truncate text-gray-400">No Song</div>
            <div class="progress-bar mt-2"><div id="barA" class="progress-inner"></div></div>
        </div>

        <div id="cardB" class="deck">
            <div class="flex justify-between text-[10px] mb-2">
                <span id="labelB" class="text-cyan-400 font-bold">DECK B</span>
                <span id="timeB" class="font-mono">00:00</span>
            </div>
            <input type="file" id="inB" class="hidden" onchange="handleFile(this.files[0], 'B')">
            <button onclick="document.getElementById('inB').click()" class="text-[10px] border border-gray-600 px-3 py-1 rounded">LOAD B</button>
            <div id="nameB" class="text-[11px] mt-1 truncate text-gray-400">No Song</div>
            <div class="progress-bar mt-2"><div id="barB" class="progress-inner" style="background: #00f3ff;"></div></div>
        </div>

        <button onclick="startMix()" class="btn-mix w-full mt-2">🔥 START AUTO-MIX</button>
        <div id="status" class="text-[10px] text-center mt-3 text-gray-500 uppercase tracking-widest">System Ready</div>
    </div>

    <script>
        let ctx, analyser, songA, songB, gainA, gainB, sourceA, sourceB;
        let active = 'A', isPlaying = false, data;

        function init() {
            if (!ctx) {
                ctx = new (window.AudioContext || window.webkitAudioContext)();
                analyser = ctx.createAnalyser();
                analyser.fftSize = 256;
                data = new Uint8Array(analyser.frequencyBinCount);
                render();
            }
        }

        async function handleFile(file, side) {
            init();
            document.getElementById('name'+side).innerText = "Loading...";
            const buffer = await ctx.decodeAudioData(await file.arrayBuffer());
            if(side === 'A') songA = buffer; else songB = buffer;
            document.getElementById('name'+side).innerText = file.name;
        }

        function render() {
            requestAnimationFrame(render);
            if(!analyser) return;
            analyser.getByteFrequencyData(data);
            const can = document.getElementById('scope');
            const c = can.getContext('2d');
            c.clearRect(0,0,can.width,can.height);
            
            let bw = (can.width / data.length) * 2.5;
            let x = 0;
            for(let i=0; i<data.length; i++) {
                let h = (data[i]/255) * can.height;
                let hue = (i * 3) + (Date.now() / 50) % 360;
                c.fillStyle = `hsl(${hue}, 100%, 50%)`;
                c.fillRect(x, can.height - h, bw - 1, h);
                x += bw;
            }
            updateEngine();
        }

        function startMix() {
            if(!songA || !songB) return alert("อาจารย์ครับ โหลดเพลงให้ครบ A/B ก่อน!");
            if(isPlaying) return;
            
            sourceA = ctx.createBufferSource(); sourceA.buffer = songA;
            gainA = ctx.createGain(); 
            sourceA.connect(gainA).connect(analyser).connect(ctx.destination);
            
            sourceB = ctx.createBufferSource(); sourceB.buffer = songB;
            gainB = ctx.createGain(); gainB.gain.value = 0;
            sourceB.connect(gainB).connect(analyser).connect(ctx.destination);
            
            sourceA.loop = true; sourceB.loop = true;
            sourceA.start(0); sourceB.start(0);
            isPlaying = true;
            document.getElementById('status').innerText = "Playing: Deck A";
            document.getElementById('cardA').classList.add('deck-active');
        }

        function updateEngine() {
            if(!isPlaying) return;
            let now = ctx.currentTime;
            
            // ระบบเช็กเวลาและ Auto-Crossfade เมื่อเพลงใกล้จบ (สมมติเล่น Loop)
            // ในที่นี้ใช้การอัปเดต Progress Bar และ UI
            updateUI('A', songA, gainA);
            updateUI('B', songB, gainB);
        }

        function updateUI(s, buffer, gain) {
            let bar = document.getElementById('bar'+s);
            let time = document.getElementById('time'+s);
            // จำลองการเดินของเวลาใน Loop
            let p = (ctx.currentTime % buffer.duration) / buffer.duration;
            bar.style.width = (p * 100) + "%";
            
            let rem = buffer.duration - (ctx.currentTime % buffer.duration);
            let m = Math.floor(rem/60), sec = Math.floor(rem%60);
            time.innerText = (m<10?'0':'')+m+":"+(sec<10?'0':'')+sec;

            // AUTO CROSSFADE LOGIC: เมื่อเหลือ 5 วินาทีสุดท้าย
            if(active === s && rem < 5) {
                crossfade();
            }
        }

        function crossfade() {
            let next = (active === 'A' ? 'B' : 'A');
            let now = ctx.currentTime;
            let dur = 4; // วินาทีในการ Fade
            
            if(active === 'A') {
                gainA.gain.linearRampToValueAtTime(0, now + dur);
                gainB.gain.linearRampToValueAtTime(1, now + dur);
                document.getElementById('cardA').classList.remove('deck-active');
                document.getElementById('cardB').classList.add('deck-active');
            } else {
                gainB.gain.linearRampToValueAtTime(0, now + dur);
                gainA.gain.linearRampToValueAtTime(1, now + dur);
                document.getElementById('cardB').classList.remove('deck-active');
                document.getElementById('cardA').classList.add('deck-active');
            }
            active = next;
            document.getElementById('status').innerText = "Auto-Mixing to: Deck " + active;
        }
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=650)

st.markdown("""
<div style='text-align: center; color: #555; font-size: 12px; font-family: "Orbitron"; letter-spacing: 2px;'>
    อยู่นิ่งๆ ไม่เจ็บตัว | AUTO-MIX ENGINE v5.0 | © 2026
</div>
""", unsafe_allow_html=True)
