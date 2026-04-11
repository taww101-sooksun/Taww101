import streamlit as st
import datetime
import os 
import time
import base64
import firebase_admin
from firebase_admin import credentials, db
import streamlit.components.v1 as components
import folium
from folium.features import DivIcon
from streamlit_folium import st_folium
import math
from math import radians, cos, sin, asin, sqrt
import pytz
from timezonefinder import TimezoneFinder
from streamlit_js_eval import get_geolocation 

# ==========================================
# 0. INITIAL SETTINGS & CLEAN UI
# ==========================================
st.set_page_config(layout="wide", page_title="SYNAPSE COMMAND CENTER")

# ฟังก์ชันลบติ่ง Streamlit แบบถอนรากถอนโคน
def apply_clean_ui():
    bg = st.session_state.get('bg_color', '#620909')
    txt = st.session_state.get('text_color', '#FFFFFF')
    brd = st.session_state.get('border_color', '#00FF41')
    
    st.markdown(f"""
        <style>
        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .stAppToolbar {{display: none;}}
        #MainMenu {{visibility: hidden;}}
        button[title="Manage app"] {{display: none;}}
        .block-container {{ padding-top: 0rem; padding-bottom: 0rem; }}
        
        /* คุมสีทั้งแอป */
        .stApp {{ background-color: {bg} !important; color: {txt} !important; }}
        h1, h2, h3, p, span, label, .stMarkdown {{ color: {txt} !important; }}

        /* ดีไซน์ Tabs และ Logic Box */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(0,0,0,0.6) !important;
            border: 3px solid {brd} !important;
            border-radius: 20px !important;
            box-shadow: 0 0 15px {brd};
        }}
        .logic-box {{
            background: rgba(0, 0, 0, 0.7);
            border: 4px solid {brd};
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 0 20px {brd}88;
        }}
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# 1. CORE LOGIC
# ==========================================
def get_reality_logic(dt):
    ref_date = datetime.date(1900, 1, 1)
    diff = (dt - ref_date).days
    lunar_cycle = 29.530589
    pos = (diff - 0.5) % lunar_cycle
    day_val = dt.weekday() + 1
    if pos <= 14.765:
        m_num = int(pos) + 1
        res = math.sqrt((day_val**2) + (m_num**2))
        phase = f"ขึ้น {m_num} ค่ำ"
    else:
        m_num = int(pos - 14.765) + 1
        res = (day_val * 1.618) / (m_num if m_num != 0 else 1)
        phase = f"แรม {m_num} ค่ำ"
    return {"res": round(res, 4), "phase": phase}

def get_local_time(lat, lon):
    try:
        tf = TimezoneFinder()
        tz_str = tf.timezone_at(lng=lon, lat=lat)
        if tz_str:
            return datetime.datetime.now(pytz.timezone(tz_str))
        return datetime.datetime.now()
    except:
        return datetime.datetime.now()

def init_system():
    if 'bg_color' not in st.session_state: st.session_state.bg_color = '#620909'
    if 'text_color' not in st.session_state: st.session_state.text_color = '#FFFFFF'
    if 'border_color' not in st.session_state: st.session_state.border_color = '#00FF41'
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except: pass

def show_logo():
    brd = st.session_state.get('border_color', '#00FF41')
    if os.path.exists("logo1.png"):
        with open("logo1.png", "rb") as f:
            data = base64.b64encode(f.read()).decode()
        st.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{data}" style="width:200px; filter:drop-shadow(0 0 10px {brd});"></div>', unsafe_allow_html=True)
    else:
        st.markdown(f"<h1 style='text-align:center; color:{brd};'>SYNAPSE OS</h1>", unsafe_allow_html=True)

# ==========================================
# 2. ROOM MODULES
# ==========================================
def room_core(loc):
    lat, lon = 13.7367, 100.5231
    if loc and 'coords' in loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
    
    current_time = get_local_time(lat, lon)
    brd = st.session_state.border_color
    st.markdown(f"""
        <div style="text-align:center; padding:40px; border:4px solid {brd}; border-radius:25px; background:rgba(0,0,0,0.6); box-shadow: 0 0 30px {brd}88;">
            <h1 style="font-size:5em; color:{brd}; margin:0; font-family:monospace;">{current_time.strftime('%H:%M:%S')}</h1>
            <p>DATE: {current_time.strftime('%Y-%m-%d')}</p>
            <p style="color:#00ff41;">📍 {lat:.5f}, {lon:.5f}</p>
            <h3>AGENT {st.session_state.get('user', 'UNKNOWN')} ONLINE</h3>
        </div>
    """, unsafe_allow_html=True)

def room_reality_scanner():
    min_d, max_d = datetime.date(1900, 1, 1), datetime.date.today()
    st.subheader("🧬 Reality Extractor")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="logic-box">', unsafe_allow_html=True)
        dob = st.date_input("วันเกิด / วันเหตุการณ์", value=datetime.date(1970, 1, 1), min_value=min_d, max_value=max_d, key="dob_main")
        if dob:
            logic = get_reality_logic(dob)
            st.metric("REALITY CODE", logic['res'])
            st.write(f"**สภาวะ:** {logic['phase']}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="logic-box">', unsafe_allow_html=True)
        u1 = st.date_input("AGENT 1", value=datetime.date(1996, 8, 17), min_value=min_d, max_value=max_d, key="u1")
        u2 = st.date_input("AGENT 2", value=max_d, min_value=min_d, max_value=max_d, key="u2")
        if st.button("COMPUTE GAP"):
            r1, r2 = get_reality_logic(u1)['res'], get_reality_logic(u2)['res']
            gap = abs(r1 - r2)
            st.subheader(f"GAP: {gap:.4f}")
        st.markdown('</div>', unsafe_allow_html=True)
def room_music():
    st.subheader("🎧 SYNAPSE MUSIC STATION")
    
    # 1. สแกนหาไฟล์เพลง
    files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    
    if not files:
        st.warning("⚠️ No MP3 files detected in root directory.")
        return

    # 2. ส่วนแสดงรายชื่อเพลง (Playlist)
    st.markdown(f"""
        <div style='background: rgba(0,0,0,0.4); padding: 15px; border-radius: 15px; border: 1px solid {st.session_state.border_color}; margin-bottom: 20px;'>
            <h4 style='margin:0; color:{st.session_state.border_color};'>📜 PLAYLIST SCANNER</h4>
        </div>
    """, unsafe_allow_html=True)

    # สร้างกล่อง Scroll สำหรับรายชื่อเพลง
    playlist_html = ""
    for i, f in enumerate(files):
        # ถ้าเป็นเพลงที่กำลังเล่น ให้ทำไฮไลท์สีตามธีม
        active_style = f"background:{st.session_state.border_color}44; border-left: 5px solid {st.session_state.border_color}; font-weight:bold;" if i == st.session_state.song_index else "opacity:0.6;"
        playlist_html += f"""
            <div style="padding: 8px 15px; margin: 4px 0; border-radius: 5px; {active_style}">
                {i+1}. 🎵 {f}
            </div>
        """
    
    st.markdown(f'<div style="max-height: 200px; overflow-y: auto; margin-bottom: 20px; font-family: monospace; font-size: 14px;">{playlist_html}</div>', unsafe_allow_html=True)

    # 3. ส่วนเครื่องเล่นเพลง
    song = files[st.session_state.song_index]
    st.info(f"▶️ NOW PLAYING: {song}")
    
    with open(song, "rb") as f:
        st.audio(f.read(), format="audio/mp3")

    # 4. ปุ่มควบคุม
    c1, c2, c3 = st.columns(3)
    if c1.button("⏮️ PREVIOUS", use_container_width=True):
        st.session_state.song_index = (st.session_state.song_index - 1) % len(files)
        st.rerun()
    if c2.button("🔄 REFRESH", use_container_width=True): 
        st.rerun()
    if c3.button("⏭️ NEXT", use_container_width=True):
        st.session_state.song_index = (st.session_state.song_index + 1) % len(files)
        st.rerun()

def room_design():
    st.markdown('<div class="logic-box"><h3>🎨 DESIGN CENTER</h3>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    bg = c1.color_picker("พื้นหลัง", st.session_state.bg_color)
    txt = c2.color_picker("ตัวหนังสือ", st.session_state.text_color)
    brd = c3.color_picker("สีกรอบ/ไฟ", st.session_state.border_color)
    if bg != st.session_state.bg_color or txt != st.session_state.text_color or brd != st.session_state.border_color:
        st.session_state.bg_color, st.session_state.text_color, st.session_state.border_color = bg, txt, brd
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# (ห้องอื่นๆ เช่น room_radar, room_music, room_secure_chat ให้คงโค้ดเดิมของคุณไว้)

# ==========================================
# 3. MAIN EXECUTION
# ==========================================
def main():
    init_system()
    apply_clean_ui() # ลบติ่งและคุมสีทันที

    if not st.session_state.logged_in:
        # ใส่ room_login() ตรงนี้
        st.title("SYNAPSE LOGIN")
        uid = st.text_input("AGENT ID")
        if st.button("ACCESS"):
            st.session_state.user = uid
            st.session_state.logged_in = True
            st.rerun()
        return

    loc = get_geolocation()
    show_logo()

    tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "🧬 SCANNER", "💬 CHAT", "📞 VOICE", "🎧 MUSIC", "🎨 DESIGN"])
    with tabs[0]: room_core(loc)
    with tabs[1]: st.write("Radar Room (ใส่โค้ดเดิมของคุณ)")
    with tabs[2]: room_reality_scanner()
    with tabs[3]: st.write("Chat Room (ใส่โค้ดเดิมของคุณ)")
    with tabs[4]: st.write("Voice Room (ใส่โค้ดเดิมของคุณ)")
    with tabs[5]: room_music()
    with tabs[6]: room_design()

if __name__ == "__main__":
    main()
