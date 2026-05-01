import streamlit as st
import os 
import time
import base64
import math
import pandas as pd
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from datetime import datetime, date, timedelta
from streamlit_js_eval import get_geolocation 

# ==========================================
# 1. SYSTEM INITIALIZATION (Login & Security)
# ==========================================
st.set_page_config(page_title="SYNAPSE OS V5", layout="wide", initial_sidebar_state="collapsed")

def init_firebase():
    if not firebase_admin._apps:
        try:
            # ใช้ Secrets จาก Streamlit เพื่อความปลอดภัย
            fb_creds = dict(st.secrets["firebase_credentials"])
            if "private_key" in fb_creds:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except Exception as e:
            st.error(f"ระบบ Firebase ไม่ได้เชื่อมต่อ: {e}")

def apply_custom_ui():
    p = st.session_state.get('theme_color', "#39FF14")
    bg = st.session_state.get('bg_color', "#000000")
    # CSS เพื่อลบหัว Streamlit และทำให้ตัวหนังสือวิ้ง (Neon Animation)
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
        
        #MainMenu, footer, header {{visibility: hidden;}}
        .stApp {{ background: {bg}; color: white; font-family: 'Orbitron', sans-serif; }}
        
        /* ตัวหนังสือวิ้ง Neon Effect */
        .neon-text {{
            color: {p};
            text-shadow: 0 0 5px {p}, 0 0 10px {p}, 0 0 20px {p};
            animation: blink 2s infinite;
        }}
        @keyframes blink {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.6; }}
        }}
        
        .stButton>button {{
            width: 100%; border: 1px solid {p} !important;
            background: rgba(0,0,0,0.5) !important; color: {p} !important;
            border-radius: 10px; height: 50px; transition: 0.3s;
        }}
        .stButton>button:hover {{
            box-shadow: 0 0 15px {p}; background: {p} !important; color: black !important;
        }}
        
        .room-box {{
            border: 1px solid {p}33; padding: 20px; border-radius: 15px;
            background: rgba(255,255,255,0.05); margin-bottom: 20px;
        }}
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LOGIC CORE (ไส้ในห้องสูตร)
# ==========================================
def calculate_synapse_logic(dt):
    ref = date(1900, 1, 1)
    diff = (dt - ref).days
    lunar = (diff - 0.5) % 29.530589
    day_val = dt.weekday() + 1
    is_waxing = lunar <= 14.765
    m_num = int(lunar) + 1 if is_waxing else int(lunar - 14.765) + 1
    
    if is_waxing:
        res = math.sqrt((day_val**2) + (m_num**2))
        f, t = f"√({day_val}² + {m_num}²)", "Vector Force (พลังขับเคลื่อนขาขึ้น)"
    else:
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        f, t = f"({day_val} × 1.618) / {m_num}", "Phi Balance (ความสมดุลขาแรม)"
    return {"res": round(res, 4), "phase": f"{'ขึ้น' if is_waxing else 'แรม'} {m_num} ค่ำ", "formula": f, "tech": t, "diff": diff}

def scan_365_days(target_res, base_date):
    data = []
    for i in range(-182, 183):
        d = base_date + timedelta(days=i)
        logic = calculate_synapse_logic(d)
        gap = abs(target_res - logic['res'])
        status = "อิสระ"
        if gap < 0.5: status = "💎 บรรจบ (เพชร)"
        elif 3.8 <= gap <= 4.2: status = "🌀 สะท้อน (ธร)"
        elif gap > 10.0: status = "🚩 แยกตัว (กงจักร)"
        data.append({"วันที่": d, "พิกัด": logic['res'], "GAP": round(gap, 4), "สถานะ": status})
    return pd.DataFrame(data)

# ==========================================
# 3. ROOM MODULES (ไส้ในแต่ละห้อง)
# ==========================================

def room_dashboard():
    st.markdown(f"<h1 class='neon-text'>SYNAPSE DASHBOARD</h1>", unsafe_allow_html=True)
    st.write("'อยู่นิ่งๆ ไม่เจ็บตัว'")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='room-box'><h3>SYSTEM STATUS</h3><p>🟢 Online & Encrypted</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='room-box'><h3>AGENT ID</h3><p>{st.session_state.user_id}</p></div>", unsafe_allow_html=True)

def room_music():
    st.markdown("<h2 class='neon-text'>🎧 SYNAPSE MUSIC STATION</h2>", unsafe_allow_html=True)
    st.info("💡 **วิธีใช้งาน:** ห้องนี้ใช้ปรับคลื่นสมองผ่านเสียง (Sound Healing) เลือกเพลงที่ต้องการเพื่อเริ่มซิงค์สัญญาณ")
    
    songs = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if songs:
        s = st.selectbox("เลือกสัญญาณเสียง (Signal Source)", songs)
        with open(s, "rb") as f: b64 = base64.b64encode(f.read()).decode()
        components.html(f"""
            <div style="background:#000; border:1px solid {st.session_state.theme_color}; border-radius:15px; padding:15px; text-align:center;">
                <canvas id="v" style="width:100%; height:120px;"></canvas>
                <audio id="a" src="data:audio/mp3;base64,{b64}"></audio>
                <button id="p" style="width:100%; padding:10px; background:none; border:1px solid {st.session_state.theme_color}; color:{st.session_state.theme_color}; cursor:pointer; font-family:monospace;">[ ACTIVATE SIGNAL ]</button>
            </div>
            <script>
                const a=document.getElementById('a'), v=document.getElementById('v'), ctx=v.getContext('2d'), btn=document.getElementById('p');
                let ac, an, sr, dt;
                btn.onclick=()=>{{
                    if(!ac){{ ac=new (window.AudioContext||window.webkitAudioContext)(); an=ac.createAnalyser(); sr=ac.createMediaElementSource(a); sr.connect(an); an.connect(ac.destination); dt=new Uint8Array(an.frequencyBinCount); run(); }}
                    a.paused ? a.play() : a.pause();
                }};
                function run(){{ requestAnimationFrame(run); an.getByteFrequencyData(dt); ctx.clearRect(0,0,v.width,v.height); dt.forEach((val,i)=>{{ ctx.fillStyle='{st.session_state.theme_color}'; ctx.fillRect(i*3, v.height-val/2, 2, val/2); }}); }}
            </script>
        """, height=250)
    else: st.warning("ไม่พบไฟล์ .mp3 ในเครื่อง")

def room_comms_gps():
    st.markdown("<h2 class='neon-text'>💬 COMM & SATELLITE</h2>", unsafe_allow_html=True)
    st.info("💡 **วิธีใช้งาน:** ใช้ระบุพิกัดตัวตนบนแผนที่โลกและส่งสัญญาณแชทผ่านดาวเทียม")
    
    t1, t2 = st.tabs(["🛰️ GPS SATELLITE", "🌐 GLOBAL CHAT"])
    with t1:
        loc = get_geolocation()
        lat, lon = (loc['coords']['latitude'], loc['coords']['longitude']) if loc else (13.75, 100.5)
        m = folium.Map(location=[lat, lon], zoom_start=17, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google")
        folium.Marker([lat, lon], tooltip="จุดที่อยู่ปัจจุบัน").add_to(m)
        st_folium(m, width="100%", height=400)
    with t2:
        with st.form("c", clear_on_submit=True):
            msg = st.text_input("ส่งข้อความ...")
            if st.form_submit_button("SEND"):
                db.reference('chat').push({'u': st.session_state.user_id, 'm': msg, 't': time.time()})
        chat_data = db.reference('chat').order_by_key().limit_to_last(10).get()
        if chat_data:
            for c in reversed(list(chat_data.values())): st.write(f"🟢 **{c['u']}**: {c['m']}")

def room_logic():
    st.markdown("<h2 class='neon-text'>🧬 LOGIC CALCULATOR</h2>", unsafe_allow_html=True)
    st.info("💡 **วิธีใช้งาน:** ตรวจสอบรหัสความจริงรายวันของคุณ และค้นหาจุดบรรจบ (เพชร) ในรอบ 1 ปี")
    
    d_in = st.date_input("เลือกวันที่ตรวจสอบ", value=date.today())
    l = calculate_synapse_logic(d_in)
    
    st.markdown(f"""
        <div class="room-box" style="text-align:center;">
            <h1 style="color:{st.session_state.theme_color}; font-size:60px;">{l['res']}</h1>
            <h4>สภาวะ: {l['tech']}</h4>
            <p>จันทรคติ: {l['phase']} | สะสม: {l['diff']:,} วัน</p>
            <code>สูตรคำนวณ: {l['formula']}</code>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔍 สแกนจุดบรรจบ 365 วัน (+/- 6 เดือน)"):
        df = scan_365_days(l['res'], d_in)
        st.dataframe(df[df['สถานะ'] != "อิสระ"], use_container_width=True)

def room_sensor():
    st.markdown("<h2 class='neon-text'>📟 REAL-TIME SENSORS</h2>", unsafe_allow_html=True)
    st.info("💡 **วิธีใช้งาน:** ใช้มือถือของคุณวัดระดับเสียงและการสั่นสะเทือนเพื่อพิสูจน์ความจริงเชิงกายภาพ")
    
    components.html(f"""
        <div style="background:#111; border:2px solid {st.session_state.theme_color}; border-radius:15px; padding:20px; color:white; text-align:center;">
            <div style="display:flex; justify-content:space-around; margin-bottom:20px;">
                <div><small>SONIC LEVEL</small><h2 id="vol" style="color:cyan;">0</h2></div>
                <div><small>MOTION G-FORCE</small><h2 id="acc" style="color:magenta;">1.00</h2></div>
            </div>
            <button id="s" style="width:100%; padding:15px; border-radius:10px; background:none; border:1px solid {st.session_state.theme_color}; color:{st.session_state.theme_color}; cursor:pointer;">[ INITIALIZE SCANNER ]</button>
        </div>
        <script>
            const btn=document.getElementById('s');
            btn.onclick=async()=>{{
                btn.style.display='none';
                const str=await navigator.mediaDevices.getUserMedia({{audio:true}});
                const ac=new AudioContext(); const ana=ac.createAnalyser();
                ac.createMediaStreamSource(str).connect(ana);
                const d=new Uint8Array(ana.frequencyBinCount);
                if(window.DeviceMotionEvent && typeof DeviceMotionEvent.requestPermission==='function') await DeviceMotionEvent.requestPermission();
                function run() {{ requestAnimationFrame(run); ana.getByteFrequencyData(d); document.getElementById('vol').innerText=Math.round(d.reduce((a,b)=>a+b)/d.length); }}
                window.addEventListener('devicemotion',e=>{{ let g=e.accelerationIncludingGravity; let v=Math.sqrt(g.x**2+g.y**2+g.z**2)/9.8; document.getElementById('acc').innerText=v.toFixed(2); }});
                run();
            }}
        </script>
    """, height=300)

def room_settings():
    st.markdown("<h2 class='neon-text'>⚙️ SYSTEM SETTINGS</h2>", unsafe_allow_html=True)
    st.session_state.user_id = st.text_input("AGENT ID", st.session_state.user_id)
    st.session_state.theme_color = st.color_picker("THEME COLOR", st.session_state.theme_color)
    st.session_state.bg_color = st.color_picker("BACKGROUND COLOR", st.session_state.bg_color)
    if st.button("UPDATE & REBOOT"): st.rerun()

# ==========================================
# 4. LOGIN & NAVIGATION CONTROL
# ==========================================
def main():
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'user_id' not in st.session_state: st.session_state.user_id = "Agent-X"
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
    if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
    
    init_firebase()
    apply_custom_ui()
    
    if not st.session_state.logged_in:
        # หน้า Login แบบเนียนๆ
        st.markdown("<div style='text-align:center; margin-top:100px;'>", unsafe_allow_html=True)
        st.markdown("<h1 class='neon-text' style='font-size:80px;'>SYNAPSE</h1>", unsafe_allow_html=True)
        u = st.text_input("ACCESS KEY (ID)", placeholder="กรุณาใส่ชื่อของคุณ...")
        if st.button("INITIALIZE SYSTEM"):
            if u:
                st.session_state.user_id = u
                st.session_state.logged_in = True
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # ระบบ Sidebar Navigation ที่ดีด UI Streamlit ออก
        with st.sidebar:
            st.markdown("<h1 class='neon-text'>SYNAPSE</h1>", unsafe_allow_html=True)
            st.write(f"Agent: {st.session_state.user_id}")
            st.write("---")
            menu = st.radio("CONTROL ROOM", ["🏠 หน้าหลัก", "🎧 เพลง", "💬 แชท & GPS", "🧬 สูตรคำนวณ", "📟 เซนเซอร์", "⚙️ ตั้งค่าแอป"])
            if st.button("LOGOUT"):
                st.session_state.logged_in = False
                st.rerun()
        
        # จัดการหน้าแต่ละห้อง
        if menu == "🏠 หน้าหลัก": room_dashboard()
        elif menu == "🎧 เพลง": room_music()
        elif menu == "💬 แชท & GPS": room_comms_gps()
        elif menu == "🧬 สูตรคำนวณ": room_logic()
        elif menu == "📟 เซนเซอร์": room_sensor()
        elif menu == "⚙️ ตั้งค่าแอป": room_settings()

if __name__ == "__main__":
    main()
