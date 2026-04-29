import streamlit as st
import os 
import base64
import random
import time
import math
from datetime import datetime, timedelta, date
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

# ==========================================
# 1. INITIAL SETUP & SAFETY (ห้ามย้ายลำดับ)
# ==========================================
st.set_page_config(page_title="SYNAPSE X", layout="wide")

# สร้าง Session State ตั้งแต่เริ่มต้น
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
if 'bg_color' not in st.session_state: st.session_state.bg_color = "#000000"
if 'user' not in st.session_state: st.session_state.user = "Ta101"
if 'song_index' not in st.session_state: st.session_state.song_index = 0

@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            if "private_key" in fb_creds:
                fb_creds["private_key"] = fb_creds["private_key"].replace("\\n", "\n").strip().strip('"')
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except: pass
init_firebase()

# ==========================================
# 2. UI STYLING (Neon Rainbow Theme)
# ==========================================
t_clr = st.session_state.theme_color
b_clr = st.session_state.bg_color

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp {{ background-color: {b_clr} !important; color: #FFFFFF !important; font-family: 'Orbitron', sans-serif; }}
    
    @keyframes rainbow {{
        0% {{ color: #ff0000; text-shadow: 0 0 10px #ff0000; }}
        25% {{ color: #39FF14; text-shadow: 0 0 10px #39FF14; }}
        50% {{ color: #00ffff; text-shadow: 0 0 10px #00ffff; }}
        75% {{ color: #ff00ff; text-shadow: 0 0 10px #ff00ff; }}
        100% {{ color: #ff0000; text-shadow: 0 0 10px #ff0000; }}
    }}
    .rainbow-text {{ animation: rainbow 5s linear infinite; font-weight: bold; }}
    .neon-box {{ border: 2px solid {t_clr}; padding: 20px; border-radius: 15px; background: rgba(0,0,0,0.7); box-shadow: 0 0 15px {t_clr}; margin-bottom: 20px; text-align: center; }}
    
    .stButton>button {{ border: 2px solid {t_clr} !important; color: {t_clr} !important; background: transparent !important; border-radius: 10px; width: 100%; }}
    .stButton>button:hover {{ background: {t_clr} !important; color: black !important; box-shadow: 0 0 20px {t_clr}; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. ROOM MODULES
# ==========================================

# --- ห้องที่ 1: CORE (ระบบสั่งการหลัก) ---
def room_core():
    st.markdown("<h2 class='rainbow-text' style='text-align:center;'>🚀 CORE COMMAND</h2>", unsafe_allow_html=True)
    now = datetime.now()
    st.markdown(f"""
        <div class="neon-box">
            <h1 style="margin:0; font-size: 60px; color:{t_clr};">{now.strftime('%H:%M:%S')}</h1>
            <p>AGENT: {st.session_state.user} | STATUS: <span style="color:#39FF14;">ONLINE</span></p>
            <small style="opacity:0.5;">'อยู่นิ่งๆ ไม่เจ็บตัว'</small>
        </div>
    """, unsafe_allow_html=True)
    st.progress(min(((now.hour * 3600) + (now.minute * 60) + now.second) / 86400, 1.0))

# --- ห้องที่ 2: RADAR (ตรวจจับตำแหน่งดาวเทียม) ---
def room_radar():
    st.markdown("<h2 class='rainbow-text' style='text-align:center;'>🛰️ SATELLITE RADAR</h2>", unsafe_allow_html=True)
    loc = get_geolocation()
    all_users = db.reference('users').get()
    lat, lon = (loc['coords']['latitude'], loc['coords']['longitude']) if loc else (13.7367, 100.5231)
    
    m = folium.Map(location=[lat, lon], zoom_start=16, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
    folium.Marker([lat, lon], tooltip="YOU", icon=folium.Icon(color='red', icon='user', prefix='fa')).add_to(m)
    
    if all_users:
        for uid, data in all_users.items():
            if uid != st.session_state.user and data.get('lat'):
                folium.Marker([data['lat'], data['lon']], tooltip=uid, icon=folium.Icon(color='green')).add_to(m)
    
    st_folium(m, width="100%", height=400, key="radar_map")
    if st.button("📡 BROADCAST POSITION"):
        db.reference(f'users/{st.session_state.user}').update({'lat': lat, 'lon': lon, 'ts': time.time()})
        st.toast("Intelligence Data Transmitted!")

# --- ห้องที่ 3: COMMS (ศูนย์การสื่อสารลับ) ---
def room_comms():
    st.markdown("<h2 class='rainbow-text' style='text-align:center;'>💬 COMM CENTER</h2>", unsafe_allow_html=True)
    with st.form("chat_form", clear_on_submit=True):
        msg = st.text_input("Enter Signal...")
        if st.form_submit_button("SEND"):
            if msg:
                db.reference('public_chat').push({'u': st.session_state.user, 'm': msg, 'ts': time.time()})
                st.rerun()
    
    msgs = db.reference('public_chat').order_by_key().limit_to_last(10).get()
    if msgs:
        for v in reversed(list(msgs.values())):
            st.write(f"🟢 **{v.get('u')}**: {v.get('m')}")

# --- ห้องที่ 4: MUSIC (สถานีความถี่เสียง) ---
def room_music():
    st.markdown("<h2 class='rainbow-text' style='text-align:center;'>🎧 MUSIC STATION</h2>", unsafe_allow_html=True)
    songs = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if songs:
        s_a = st.selectbox("🎯 SELECT SIGNAL", songs)
        with open(s_a, "rb") as f:
            song_b64 = base64.b64encode(f.read()).decode()
        st.components.v1.html(f"""
            <audio id="audio" src="data:audio/mp3;base64,{song_b64}" controls style="width:100%;"></audio>
            <script>document.getElementById('audio').volume = 0.5;</script>
        """, height=100)
    else:
        st.warning("No signal detected.")

# --- ห้องที่ 5: SENSOR (ตรวจจับการเคลื่อนไหว) ---
def room_sensor():
    st.markdown("<h2 class='rainbow-text' style='text-align:center;'>📟 SENSOR ARRAY</h2>", unsafe_allow_html=True)
    sensor_js = f"""
    <div style="background: #000; border: 2px solid {t_clr}; padding: 20px; border-radius: 15px; text-align:center;">
        <small style="color:{t_clr};">MOTION DETECTOR</small>
        <h1 id="mag" style="color:#ff00ff; font-size:50px;">1.000</h1>
    </div>
    <script>
        window.addEventListener('devicemotion', (e) => {{
            const acc = e.accelerationIncludingGravity;
            let m = Math.sqrt(acc.x**2 + acc.y**2 + acc.z**2) / 9.8;
            document.getElementById('mag').innerText = m.toFixed(3);
        }});
    </script>
    """
    components.html(sensor_js, height=200)

# --- ห้องที่ 6: LOGIC (ถอดรหัสความจริง 1950-2026) ---
def room_logic():
    st.markdown("<h2 class='rainbow-text' style='text-align:center;'>🧬 THE TRUTH DECODER</h2>", unsafe_allow_html=True)
    target_date = st.date_input("SCAN DATE", value=date.today(), min_value=date(1950, 1, 1), max_value=date(2026, 12, 31))
    
    def decode(dt):
        day_map = {0:2, 1:3, 2:4, 3:5, 4:6, 5:7, 6:1} # ปรับฐานวัน
        day_val = day_map[dt.weekday()]
        ref = date(1900, 1, 1)
        pos = ((dt - ref).days - 0.5) % 29.53
        elements = {1: "ไฟ", 2: "ดิน", 3: "ลม", 4: "น้ำ", 5: "ดิน", 6: "น้ำ", 7: "ไฟ"}
        zodiacs = ["มะเมีย", "มะแม", "วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง"]
        zodiac = zodiacs[(dt.year + 543) % 12]
        m_num = int(pos) + 1 if pos <= 14.76 else int(pos - 14.76) + 1
        res = math.sqrt(day_val**2 + m_num**2)
        return {"res": round(res, 4), "zodiac": zodiac, "element": elements.get(day_val), "phase": f"ขึ้น {m_num} ค่ำ" if pos <= 14.76 else f"แรม {m_num} ค่ำ"}

    d = decode(target_date)
    st.markdown(f"""
        <div class="neon-box" style="border-color:#ff00ff;">
            <small>รหัสพิกัดความจริง</small>
            <h1 class="rainbow-text" style="font-size:50px;">{d['res']}</h1>
            <p>ปี{d['zodiac']} | ธาตุ{d['element']} | {d['phase']}</p>
        </div>
    """, unsafe_allow_html=True)

# --- ห้องที่ 7: SETTINGS (ตั้งค่าระบบ) ---
def room_settings():
    st.markdown("<h2 class='rainbow-text' style='text-align:center;'>⚙️ SYSTEM SETTINGS</h2>", unsafe_allow_html=True)
    st.session_state.user = st.text_input("CHANGE AGENT ID", st.session_state.user)
    st.session_state.theme_color = st.color_picker("UPDATE NEON LIGHT", st.session_state.theme_color)
    st.session_state.bg_color = st.color_picker("UPDATE SPACE VOID", st.session_state.bg_color)
    if st.button("REBOOT SYSTEM"): st.rerun()

# ==========================================
# 4. MAIN EXECUTION
# ==========================================
def main():
    with st.sidebar:
        st.markdown("<h1 class='rainbow-text'>SYNAPSE X</h1>", unsafe_allow_html=True)
        st.write(f"WELCOME, {st.session_state.user}")
        st.write("---")
        st.caption("'อยู่นิ่งๆ ไม่เจ็บตัว'")

    tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "🎧 MUSIC", "📟 SENSOR", "🧬 LOGIC", "⚙️ SETTINGS"])
    rooms = [room_core, room_radar, room_comms, room_music, room_sensor, room_logic, room_settings]
    
    for i, tab in enumerate(tabs):
        with tab: rooms[i]()

if __name__ == "__main__":
    main()
