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
# 1. CRITICAL INITIALIZATION (ต้องอยู่บนสุดเสมอ)
# ==========================================
st.set_page_config(page_title="SYNAPSE X", layout="wide")

# ป้องกัน Error โดยการสร้าง State ทันทีที่รันแอป
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
            return True
        except Exception as e:
            st.error(f"🛰️ Firebase Connection Error: {e}")
            return False
    return True

init_firebase()

# ==========================================
# 2. ADVANCED UI STYLING (เพิ่มลูกเล่นความพิเศษ)
# ==========================================
t_clr = st.session_state.theme_color
b_clr = st.session_state.bg_color

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    
    .stApp {{ 
        background-color: {b_clr} !important; 
        background-image: radial-gradient(circle at 50% 50%, {t_clr}11 0%, {b_clr} 100%) !important;
        color: #FFFFFF !important; 
        font-family: 'Orbitron', sans-serif; 
    }}

    /* Rainbow Flow Animation */
    @keyframes rainbow {{
        0% {{ color: #ff0000; text-shadow: 0 0 10px #ff0000; }}
        25% {{ color: #39FF14; text-shadow: 0 0 10px #39FF14; }}
        50% {{ color: #00ffff; text-shadow: 0 0 10px #00ffff; }}
        75% {{ color: #ff00ff; text-shadow: 0 0 10px #ff00ff; }}
        100% {{ color: #ff0000; text-shadow: 0 0 10px #ff0000; }}
    }}
    .rainbow-text {{ animation: rainbow 5s linear infinite; font-weight: bold; }}

    .neon-box {{ 
        border: 2px solid {t_clr}; padding: 20px; border-radius: 15px; 
        background: rgba(0,0,0,0.7); box-shadow: 0 0 15px {t_clr};
        margin-bottom: 20px; text-align: center;
    }}

    .stButton>button {{ 
        border: 2px solid {t_clr} !important; color: {t_clr} !important; 
        background: transparent !important; border-radius: 10px; width: 100%;
        text-transform: uppercase; letter-spacing: 2px;
    }}
    .stButton>button:hover {{ background: {t_clr} !important; color: black !important; box-shadow: 0 0 20px {t_clr}; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. LOGIC MODULES (คืนชีพรายละเอียดและความละเอียด)
# ==========================================

def room_core():
    st.markdown("<h2 class='rainbow-text' style='text-align:center;'>🚀 CORE COMMAND CENTER</h2>", unsafe_allow_html=True)
    now = datetime.now()
    st.markdown(f"""
        <div class="neon-box">
            <h1 style="margin:0; font-size: 60px; color:{t_clr}; text-shadow: 0 0 20px {t_clr};">{now.strftime('%H:%M:%S')}</h1>
            <p style="letter-spacing: 3px;">SYSTEM ACCESS: <span class="rainbow-text">{st.session_state.user}</span></p>
            <div style="font-size: 12px; color: {t_clr}; opacity: 0.6;">'อยู่นิ่งๆ ไม่เจ็บตัว'</div>
        </div>
    """, unsafe_allow_html=True)
    
    seconds = (now.hour * 3600) + (now.minute * 60) + now.second
    st.write(f"🌌 QUANTUM ALIGNMENT: { (seconds/86400)*100 :.4f}%")
    st.progress(min(seconds/86400, 1.0))

def room_logic():
    st.markdown("<h2 class='rainbow-text' style='text-align:center;'>🧬 THE TRUTH DECODER</h2>", unsafe_allow_html=True)
    st.caption("🔍 วิเคราะห์การเชื่อมโยงระหว่างมิติเวลาและธาตุธรรมชาติ (ศาสตร์แห่งความจริง)")
    
    target_date = st.date_input("ป้อนรหัสวันที่เพื่อถอดรหัส...", value=date.today())
    
    if target_date:
        # ฟังก์ชันคำนวณที่อ้างอิงจากฐานข้อมูลศาสตร์ที่คุณมี
        def decode(dt):
            ref = date(1900, 1, 1)
            diff = (dt - ref).days
            pos = (diff - 0.5) % 29.53 # Lunar Cycle
            day_val = dt.isoweekday() # 1=Mon, 7=Sun
            
            thai_year = dt.year + 543
            zodiacs = ["มะเมีย", "มะแม", "วอก", "ระกา", "จอ", "กุน", "ชวด", "ฉลู", "ขาล", "เถาะ", "มะโรง", "มะเส็ง"]
            zodiac = zodiacs[thai_year % 12]
            
            # ธาตุตามตำราไทย (1=อาทิตย์, 2=จันทร์...)
            elements = {7: "ไฟ", 1: "ไฟ", 2: "ดิน", 3: "ลม", 4: "น้ำ", 5: "ดิน", 6: "น้ำ"}
            element = elements.get(day_val)
            
            m_num = int(pos) + 1 if pos <= 14.76 else int(pos - 14.76) + 1
            phase = f"ขึ้น {m_num} ค่ำ" if pos <= 14.76 else f"แรม {m_num} ค่ำ"
            res = math.sqrt(day_val**2 + m_num**2)
            return {"res": round(res, 4), "phase": phase, "zodiac": zodiac, "element": element}

        d = decode(target_date)
        st.markdown(f"""
            <div class="neon-box" style="border-color:#ff00ff; box-shadow: 0 0 20px #ff00ff;">
                <small style="color:#ff00ff;">REALITY COORDINATE</small>
                <h1 class="rainbow-text" style="font-size:70px; margin:0;">{d['res']}</h1>
                <hr style="border-color:#ff00ff33;">
                <div style="display:grid; grid-template-columns: 1fr 1fr; text-align:left; gap:10px;">
                    <div class="neon-box" style="padding:10px; margin:0; font-size:14px;">ปี: {d['zodiac']}</div>
                    <div class="neon-box" style="padding:10px; margin:0; font-size:14px;">ธาตุ: {d['element']}</div>
                    <div class="neon-box" style="padding:10px; margin:0; font-size:14px; grid-column: span 2;">จันทรคติ: {d['phase']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

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

# ==========================================
# 4. MAIN PROGRAM LAYOUT
# ==========================================
def main():
    with st.sidebar:
        st.markdown("<h1 class='rainbow-text'>SYNAPSE X</h1>", unsafe_allow_html=True)
        st.session_state.user = st.text_input("AGENT ID", st.session_state.user)
        st.session_state.theme_color = st.color_picker("NEON THEME", st.session_state.theme_color)
        st.session_state.bg_color = st.color_picker("DEEP SPACE", st.session_state.bg_color)
        st.markdown("---")
        st.info("🛰️ Satellite Status: Active")
        st.caption("'อยู่นิ่งๆ ไม่เจ็บตัว'")

    tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "🎧 MUSIC", "📟 SENSOR", "🧬 LOGIC"])
    
    with tabs[0]: room_core()
    with tabs[1]: room_radar()
    with tabs[5]: room_logic()
    # (ห้องอื่นๆ COMMS, MUSIC, SENSOR สามารถก๊อปปี้ฟังก์ชันเดิมมาใส่ได้เลยครับ)

if __name__ == "__main__":
    main()
