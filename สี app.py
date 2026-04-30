import streamlit as st
import os 
import time
import base64
import math
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from math import radians, cos, sin, asin, sqrt
import pytz
from timezonefinder import TimezoneFinder
from datetime import datetime, date
from streamlit_js_eval import get_geolocation 

# ==========================================
# 0. CONFIG & INITIALIZATION
# ==========================================
st.set_page_config(page_title="SYNAPSE OS", layout="wide", initial_sidebar_state="collapsed")

def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'user' not in st.session_state: st.session_state.user = "AGENT-X"
    
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            if "private_key" in fb_creds:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"🛰️ ระบบเชื่อมต่อขัดข้อง: {e}")

def apply_custom_background():
    st.markdown(f"""
        <style>
        .stApp {{
            background: linear-gradient(270deg, #111, #222, {st.session_state.theme_color}11);
            background-size: 400% 400%;
            animation: Gradient 15s ease infinite;
        }}
        @keyframes Gradient {{ 0%{{background-position:0% 50%}} 50%{{background-position:100% 50%}} 100%{{background-position:0% 50%}} }}
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(0, 0, 0, 0.7);
            border-radius: 15px; padding: 5px;
            border: 1px solid {st.session_state.theme_color};
            box-shadow: 0 0 10px {st.session_state.theme_color}44;
        }}
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 1. THE MODULES (Rooms)
# ==========================================

def room_logic():
    st.markdown(f"<h2 style='color:{st.session_state.theme_color}; text-shadow: 0 0 20px {st.session_state.theme_color}; text-align:center;'>🧬 THE TRUTH DECODER</h2>", unsafe_allow_html=True)
    
    def decode_truth(dt):
        ref_date = date(1900, 1, 1)
        diff = (dt - ref_date).days
        lunar_cycle = 29.530589
        pos = (diff - 0.5) % lunar_cycle
        day_val = dt.weekday() + 1
        
        # ปีนักษัตร
        thai_year = dt.year + 543
        zodiacs = ["วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง", "มะเมีย", "มะแม"]
        zodiac = zodiacs[thai_year % 12]
        
        # ธาตุประจำวัน
        elements = {1: "ดิน", 2: "น้ำ", 3: "ไฟ", 4: "ลม", 5: "ทอง", 6: "น้ำ", 7: "ดิน"}
        element = elements.get(day_val)

        if pos <= 14.765:
            m_num = int(pos) + 1
            phase = f"ขึ้น {m_num} ค่ำ"
            res = math.sqrt((day_val**2) + (m_num**2))
            formula = f"√({day_val}² + {m_num}²)"
            p_type = "แรงผลักดัน (Vector)"
        else:
            m_num = int(pos - 14.765) + 1
            phase = f"แรม {m_num} ค่ำ"
            res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
            formula = f"({day_val} × 1.618) / {m_num}"
            p_type = "สมดุลสัดส่วนทองคำ (Phi)"
            
        return {"res": round(res, 4), "phase": phase, "zodiac": zodiac, "element": element, "formula": formula, "type": p_type, "day_num": day_val, "lunar_num": m_num, "diff": diff}

    st.subheader("🔍 วิเคราะห์พิกัดความจริง (อดีต-อนาคต)")
    target_date = st.date_input("เลือกวันที่ตรวจสอบ", value=date.today(), min_value=date(1950,1,1), max_value=date(2026,12,31))
    
    if target_date:
        d = decode_truth(target_date)
        st.markdown(f"""
            <div style="text-align:center; padding:20px; border:2px solid {st.session_state.theme_color}; border-radius:20px; background:rgba(0,0,0,0.3);">
                <small>รหัสพิกัดจักรวาล</small>
                <h1 style="color:{st.session_state.theme_color}; font-size:60px; margin:0;">{d['res']}</h1>
                <p style="color:#888;">{d['type']}</p>
            </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📅 **ฐานวัน ({d['day_num']}):** แรงดึงดูดโลก")
            st.info(f"🌙 **จันทรคติ ({d['phase']}):** แรงดึงดูดดวงจันทร์")
        with col2:
            st.success(f"🐎 **ปีนักษัตร:** ปี{d['zodiac']}")
            st.success(f"💎 **ธาตุประจำวัน:** ธาตุ{d['element']}")

        st.markdown(f"""
            <div style="background:#111; padding:15px; border-left:5px solid {st.session_state.theme_color}; border-radius:10px; margin-top:10px;">
                <p style="font-size:14px; color:#aaa; margin:0;">
                    <b>สูตรการคำนวณ:</b> {d['formula']}<br>
                    คำนวณจากวันที่สะสมตั้งแต่ปี 1900 รวมทั้งสิ้น {d['diff']:,} วัน
                </p>
            </div>
        """, unsafe_allow_html=True)

        if target_date < date.today(): st.warning("⏪ ตรวจสอบรอยเท้าพลังงานใน **'อดีต'**")
        elif target_date > date.today(): st.error("🔮 ตรวจสอบพิกัดเป้าหมายใน **'อนาคต'**")
        else: st.success("🟢 พิกัดพลังงานใน **'ปัจจุบัน'**")

def room_music():


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

    st.subheader("🎧 SYNAPSE MUSIC STATION")
    music_files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if not music_files:
        st.warning("⚠️ ไม่พบไฟล์เพลงในระบบ")
        return
    
    current_song = music_files[st.session_state.song_index % len(music_files)]
    st.info(f"🎵 กำลังเล่น: {current_song}")
    
    with open(current_song, "rb") as f:
        audio_bytes = f.read()
    st.audio(audio_bytes, format="audio/mp3", autoplay=True)
    
    col1, col2, col3 = st.columns(3)
    if col1.button("⏮️ BACK", use_container_width=True):
        st.session_state.song_index -= 1
        st.rerun()
    if col2.button("🔄 RELOAD", use_container_width=True): 
        st.rerun()
    if col3.button("⏭️ NEXT", use_container_width=True):
        st.session_state.song_index += 1
        st.rerun()

def room_settings():
    st.subheader("🎨 SYSTEM THEME")
    color_presets = {"🟢 CYBER": "#39FF14", "🔵 DEEP": "#1408BF", "🔴 ALERT": "#FF0000", "🟣 VIBE": "#800080"}
    selected = st.selectbox("เลือกโทนสีระบบ", list(color_presets.keys()))
    if st.button("APPLY THEME", use_container_width=True):
        st.session_state.theme_color = color_presets[selected]
        st.rerun()
    
    st.write("---")
    if st.button("🚪 LOGOUT", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ==========================================
# 2. MAIN SYSTEM
# ==========================================
def main():
    init_system()
    apply_custom_background()
    loc = get_geolocation()

    if not st.session_state.logged_in:
        st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color};'>SYNAPSE OS</h1>", unsafe_allow_html=True)
        with st.form("login_form"):
            u = st.text_input("AGENT ID")
            p = st.text_input("PASSWORD", type="password")
            if st.form_submit_button("LOGIN", use_container_width=True):
                # ตรงนี้คุณสามารถใส่โค้ดเช็ค Firebase จริงได้
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
    else:
        st.sidebar.write(f"👤 AGENT: {st.session_state.user}")
        st.sidebar.caption("'อยู่นิ่งๆ ไม่เจ็บตัว'")
        
        tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "💬 CHAT", "🎧 MUSIC", "🧬 LOGIC", "⚙️ SETTINGS"])
        with tabs[3]: room_music()
        with tabs[4]: room_logic()
        with tabs[5]: room_settings()

if __name__ == "__main__":
    main()
