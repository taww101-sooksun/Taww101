import streamlit as st
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

# ==========================================
# 0. CONFIG & CSS STYLING (Matrix & Neon Style)
# ==========================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide", initial_sidebar_state="collapsed")

def apply_custom_background():
    theme = st.session_state.get('theme_color', "#1408BF")
    st.markdown(f"""
        <style>
        /* ส่วนของ Tabs - ขอบใหญ่ขึ้นไฟฟุ้งขึ้น */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: rgba(0, 0, 0, 0.8) !important;
            border-radius: 25px !important;
            padding: 12px !important;
            border: 6px solid {theme} !important; /* <--- ปรับขอบใหญ่ตรงนี้ */
            box-shadow: 0 0 40px {theme};         /* <--- ปรับไฟฟุ้งตรงนี้ */
            margin: 15px 0px !important;
        }}
        
        /* ส่วนของปุ่ม - ขอบหนาขึ้น */
        div.stButton > button {{
            background: linear-gradient(145deg, #000, #222) !important;
            color: white !important;
            border: 5px solid {theme} !important; /* <--- ขอบปุ่มหนาๆ */
            border-radius: 20px !important;
            filter: drop-shadow(0 0 15px {theme}); /* <--- ไฟนูนๆ */
            transition: all 0.3s ease;
        }}

        /* ส่วนของกล่องคำนวณ - ขอบเขียวหนาๆ */
        .logic-box {{
            background: rgba(0, 10, 0, 0.9);
            border: 5px solid #00ff41;             /* <--- ขอบหนาตรงนี้ */
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 0 30px rgba(0, 255, 65, 0.6);
        }}
        </style>
    """, unsafe_allow_html=True)


def show_logo():
    theme = st.session_state.get('theme_color', "#1408BF")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if os.path.exists("logo1.png"):
            with open("logo1.png", "rb") as f:
                data = base64.b64encode(f.read()).decode()
            st.markdown(f"""
                <div style="text-align:center; filter: drop-shadow(0 0 15px {theme}); margin-bottom: 25px;">
                    <img src="data:image/png;base64,{data}" style="width:100%; max-width:240px; border-radius:20px;">
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"<h1 style='text-align:center; color:{theme}; text-shadow: 0 0 15px {theme};'>SYNAPSE OS</h1>", unsafe_allow_html=True)

# ==========================================
# 1. UTILS & CALCULATION LOGIC
# ==========================================
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon, dlat = lon2 - lon1, lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * 6371

def get_reality_logic(dt):
    """สูตรคำนวณรหัสคู่ขนานตามวันที่"""
    ref_date = date(1900, 1, 1)
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

def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = "#1408BF"
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except: pass

def get_local_time(lat, lon):
    try:
        tf = TimezoneFinder()
        tz_str = tf.timezone_at(lat=lat, lng=lon)
        return datetime.now(pytz.timezone(tz_str)) if tz_str else datetime.now()
    except: return datetime.now()

# ==========================================
# 2. CORE MODULES
# ==========================================
def room_login():
    show_logo()
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="logic-box" style="text-align:center; border-color:#1408BF;">', unsafe_allow_html=True)
        tab_l, tab_r = st.tabs(["🔑 UNLOCK", "📝 NEW AGENT"])
        with tab_l:
            with st.form("login_form"):
                uid = st.text_input("AGENT ID")
                pw = st.text_input("PASSWORD", type="password")
                if st.form_submit_button("ACCESS GRANTED", use_container_width=True):
                    user_data = db.reference(f'users/{uid}').get()
                    if user_data and user_data.get('pw') == pw:
                        st.session_state.user = uid
                        st.session_state.logged_in = True
                        st.rerun()
                    else: st.error("ACCESS DENIED: ข้อมูลไม่ถูกต้อง")
        with tab_r:
            with st.form("reg_form"):
                new_id = st.text_input("CREATE ID")
                new_pw = st.text_input("CREATE PASSWORD", type="password")
                if st.form_submit_button("REGISTER", use_container_width=True):
                    db.reference(f'users/{new_id}').set({'pw': new_pw, 'ts': time.time()})
                    st.success("AGENT REGISTERED!")
        st.markdown('</div>', unsafe_allow_html=True)

def room_core(loc):
    st.subheader("🏠 CORE CONTROL - อยู่นิ่งๆไม่เจ็บตัว")
    lat, lon = 13.7367, 100.5231
    if loc and 'coords' in loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
    
    current_time = get_local_time(lat, lon)
    st.markdown(f"""
        <div style="text-align:center; padding:40px; border:4px solid {st.session_state.theme_color}; border-radius:25px; background:rgba(0,0,0,0.6); box-shadow: 0 0 30px {st.session_state.theme_color}88;">
            <h1 style="font-size:6em; color:{st.session_state.theme_color}; margin:0; font-family: 'Courier New'; text-shadow: 0 0 20px {st.session_state.theme_color};">
                {current_time.strftime('%H:%M:%S')}
            </h1>
            <p style="color:#FFF; font-size:1.2em; letter-spacing: 4px;">DATE: {current_time.strftime('%Y-%m-%d')}</p>
            <hr style="border-color:{st.session_state.theme_color}; opacity:0.3;">
            <p style="color:#00ff41; font-family:monospace;">📍 POSITION: {lat:.5f}, {lon:.5f}</p>
            <p style="color:{st.session_state.theme_color}; font-weight:bold; font-size:1.5em;">AGENT {st.session_state.user} IS ONLINE</p>
        </div>
    """, unsafe_allow_html=True)

def room_radar(loc):
    st.subheader("🛰️ STRATEGIC RADAR SCANNER")
    my_lat, my_lon = 13.7367, 100.5231 
    if loc and 'coords' in loc:
        my_lat, my_lon = loc['coords']['latitude'], loc['coords']['longitude']
    
    m = folium.Map(location=[my_lat, my_lon], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr='Google Satellite')
    
    # Marker เรา
    folium.Marker([my_lat, my_lon], 
                  icon=folium.Icon(color='red', icon='screenshot', prefix='fa'),
                  tooltip="MY POSITION").add_to(m)
    
    # วงรัศมี
    folium.Circle([my_lat, my_lon], radius=400, color="#00ff41", fill=True, opacity=0.1).add_to(m)

    # ดึงพิกัด AGENTS อื่นๆ
    try:
        users = db.reference('users').get()
        if users:
            for uid, data in users.items():
                if uid != st.session_state.user and 'lat' in data:
                    u_lat, u_lon = data['lat'], data['lon']
                    dist = haversine(my_lat, my_lon, u_lat, u_lon)
                    folium.Marker([u_lat, u_lon], 
                                  icon=folium.Icon(color='blue', icon='user', prefix='fa'),
                                  tooltip=f"AGENT: {uid} | DIST: {dist:.2f} km").add_to(m)
                    folium.PolyLine([[my_lat, my_lon], [u_lat, u_lon]], color=st.session_state.theme_color, weight=1, dash_array='5').add_to(m)
    except: pass

    st_folium(m, width="100%", height=450)
    
    if st.button("📡 BROADCAST MY SIGNAL", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.toast("SIGNAL BROADCASTED TO NETWORK")

def room_reality_scanner():
        min_date = dt.date(1960, 1, 1) # แก้ไขตามคำขอ: ปี 1960
        max_date = dt.date.today()
    
        col1, col2 = st.columns(2)
with col1:
        u1 = st.date_input("AGENT 1 (วันเกิด)", value=dt.date(1996, 8, 17), min_value=min_date, max_value=max_date, format="YYYY/MM/DD") 
with col2:
        u2 = st.date_input("AGENT 2 (วันเกิด)", value=max_date, min_value=min_date, max_value=max_date, format="YYYY/MM/DD")

   if st.button("COMPUTE GAP", use_container_width=True):
        r1 = get_reality_logic(u1)
        r2 = get_reality_logic(u2)
        gap = abs(r1['res'] - r2['res'])
        st.markdown(f"""
            <div class="logic-box">
                <h2 style="color:#00ff41;">RESULT GAP: {gap:.4f}</h2>
                <hr style="border-color:#00ff41; opacity:0.3;">
                <p>CODE 1: {r1['res']} ({r1['phase']})</p>
                <p>CODE 2: {r2['res']} ({r2['phase']})</p>
            </div>
        """, unsafe_allow_html=True)

def room_secure_chat():
    st.subheader("💬 SECURE REAL-TIME MESSENGER")
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    target = st.selectbox("🎯 SELECT TARGET AGENT:", friends)
    
    if target:
        rid = "_".join(sorted([st.session_state.user, target]))
        chat_container = st.container(height=150, border=True)
        
        # Load Messages
        chats = db.reference(f'private_rooms/{rid}').order_by_key().limit_to_last(25).get()
        
        with chat_container:
            if chats:
                for c in chats.values():
                    is_me = c['u'] == st.session_state.user
                    align = "right" if is_me else "left"
                    bg = st.session_state.theme_color if is_me else "#222"
                    st.markdown(f"""
                        <div style="text-align:{align}; margin-bottom:12px;">
                            <div style="display:inline-block; background:{bg}; padding:10px 18px; border-radius:18px; color:white; border:1px solid rgba(255,255,255,0.1);">
                                <small style="opacity:0.6;">{c['u']}</small><br>{c['m']}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else: st.caption("No communication history found.")

        with st.form("msg_form", clear_on_submit=True):
            c_input, c_btn = st.columns([4, 1])
            msg = c_input.text_input("Enter Message...", label_visibility="collapsed")
            if c_btn.form_submit_button("SEND", use_container_width=True):
                if msg:
                    db.reference(f'private_rooms/{rid}').push({'u': st.session_state.user, 'm': msg, 'ts': time.time()})
                    st.rerun()

def room_voice_call():
    st.subheader("📞 P2P ENCRYPTED VOICE CALL")
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    target = st.selectbox("CALL TO:", friends, key="v_call_target")
    
    if target:
        st.markdown(f"""
            <div style="background:#000; padding:30px; border-radius:20px; border:2px solid {st.session_state.theme_color}; text-align:center; box-shadow: 0 0 20px {st.session_state.theme_color}55;">
                <h2 style="color:{st.session_state.theme_color};">VOICE CHANNEL ACTIVE</h2>
                <audio id="remoteAudio" autoplay></audio>
                <div style="margin: 20px 0;">
                    <div style="width:100px; height:100px; border-radius:50%; border:5px solid {st.session_state.theme_color}; display:inline-block; animation: pulse 1.5s infinite;"></div>
                </div>
                <button id="startCall" style="background:{st.session_state.theme_color}; color:white; padding:12px 30px; border:none; border-radius:10px; cursor:pointer;">START CALL</button>
                <button onclick="location.reload()" style="background:red; color:white; padding:12px 30px; border:none; border-radius:10px; cursor:pointer; margin-left:10px;">HANG UP</button>
            </div>
            <style> @keyframes pulse {{ 0%{{box-shadow:0 0 0 0 {st.session_state.theme_color}aa;}} 70%{{box-shadow:0 0 0 20px rgba(0,0,0,0);}} 100%{{box-shadow:0 0 0 0 rgba(0,0,0,0);}} }} </style>
            
            <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
            <script>
                const peer = new Peer('{st.session_state.user}');
                peer.on('call', call => {{
                    navigator.mediaDevices.getUserMedia({{audio: true, video: false}}).then(s => {{
                        call.answer(s);
                        call.on('stream', rs => {{ document.getElementById('remoteAudio').srcObject = rs; }});
                    }});
                }});
                document.getElementById('startCall').onclick = () => {{
                    navigator.mediaDevices.getUserMedia({{audio: true, video: false}}).then(s => {{
                        const call = peer.call('{target}', s);
                        call.on('stream', rs => {{ document.getElementById('remoteAudio').srcObject = rs; }});
                    }});
                }};
            </script>
        """, unsafe_allow_html=True)

def room_music():
    st.subheader("🎧 SYNAPSE MUSIC STATION")
    files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if not files:
        st.warning("⚠️ No MP3 files detected in root directory.")
        return

    song = files[st.session_state.song_index]
    st.info(f"🎶 NOW STREAMING: {song}")
    
    with open(song, "rb") as f:
        st.audio(f.read(), format="audio/mp3", autoplay=True)

    # UI Controls
    c1, c2, c3 = st.columns(3)
    if c1.button("⏮️ PREVIOUS", use_container_width=True):
        st.session_state.song_index = (st.session_state.song_index - 1) % len(files)
        st.rerun()
    if c2.button("🔄 REFRESH", use_container_width=True): st.rerun()
    if c3.button("⏭️ NEXT", use_container_width=True):
        st.session_state.song_index = (st.session_state.song_index + 1) % len(files)
        st.rerun()

# ==========================================
# 3. MAIN CONTROLLER
# ==========================================
def main():
    init_system()
    apply_custom_background()
    loc = get_geolocation() 

    if not st.session_state.get('logged_in', False):
        room_login()
        return

    show_logo()

    # Sidebar Settings
    with st.sidebar:
        st.markdown(f"### 👤 AGENT: {st.session_state.user}")
        st.caption("Status: AUTHENTICATED")
        st.write("---")
        st.session_state.theme_color = st.color_picker("🎨 SYSTEM THEME (Neon)", st.session_state.theme_color)
        if st.button("🚪 LOGOUT SYSTEM", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        st.write("---")
        st.write("'อยู่นิ่งๆ ไม่เจ็บตัว'")

    # Main Navigation
    tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "🧬 SCANNER", "💬 CHAT", "📞 VOICE", "🎧 MUSIC"])
    
    with tabs[0]: room_core(loc)
    with tabs[1]: room_radar(loc)
    with tabs[2]: room_reality_scanner()
    with tabs[3]: room_secure_chat()
    with tabs[4]: room_voice_call()
    with tabs[5]: room_music()

if __name__ == "__main__":
    main()
