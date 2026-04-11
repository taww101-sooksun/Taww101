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
# 1. SYSTEM CONFIG & UI HIDING
# ==========================================
st.set_page_config(layout="wide", page_title="SYNAPSE", page_icon="⚡")

# ซ่อน UI ของ Streamlit ให้กริบที่สุดตามสไตล์ SYNAPSE
st.markdown("""
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppToolbar {display: none;}
    #MainMenu {visibility: hidden;}
    button[title="Manage app"] {display: none;}
    .block-container { padding-top: 0rem; padding-bottom: 0rem; }
    
    /* ตกแต่ง Tabs ให้ดูเป็นไซเบอร์ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(0,0,0,0.3);
        padding: 10px;
        border-radius: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SESSION STATE & INITIALIZATION
# ==========================================
def init_system():
    if 'theme_color' not in st.session_state: st.session_state.theme_color = '#620909'
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'song_index' not in st.session_state: st.session_state.song_index = 0
    if 'user' not in st.session_state: st.session_state.user = "Unknown"
    
    # เชื่อมต่อ Firebase
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_credentials"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {'databaseURL': st.secrets["firebase_db_url"]})
        except: pass

# ==========================================
# 3. UTILS & CALCULATION LOGIC
# ==========================================
def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon, dlat = lon2 - lon1, lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * 6371

def get_reality_logic(dt):
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

def get_local_time(lat, lon):
    try:
        tf = TimezoneFinder()
        tz_str = tf.timezone_at(lat=lat, lng=lon)
        return datetime.now(pytz.timezone(tz_str)) if tz_str else datetime.now()
    except: return datetime.now()

# ==========================================
# 4. CUSTOM UI COMPONENTS
# ==========================================
def apply_theme_css():
    theme = st.session_state.theme_color
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {theme} !important; }}
        .logic-box {{
            background: rgba(0, 10, 0, 0.8);
            border: 5px solid {theme};
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 0 30px {theme};
        }}
        /* ส่วนของ Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            border: 4px solid {theme} !important;
            box-shadow: 0 0 20px {theme};
        }}
        </style>
    """, unsafe_allow_html=True)

def draw_agent_card():
    theme = st.session_state.theme_color
    agent_html = f"""
    <div style="background-color: #1A1D21; border-radius: 15px; padding: 20px; color: white; border: 1px solid #333; box-shadow: 0 10px 20px rgba(0,0,0,0.5);">
        <div style="display: flex; align-items: center; font-size: 18px; font-weight: bold; gap: 10px;">👤 AGENT: {st.session_state.user}</div>
        <div style="color: #8C959F; font-size: 13px; margin-left: 32px; margin-bottom: 15px;">Status: AUTHENTICATED</div>
        <div style="background-color: #262B30; border-radius: 10px; padding: 15px;">
            <div style="font-size:11px; margin-bottom: 8px;">🎨 SYSTEM THEME (Neon)</div>
            <div style="width: 40px; height: 40px; background-color: {theme}; border-radius: 5px; margin-bottom: 10px;"></div>
            <div style="width: 100%; height: 80px; background: linear-gradient(to bottom, white, transparent, black), linear-gradient(to right, transparent, {theme}); background-color: {theme}; border-radius: 8px;"></div>
        </div>
        <div style="background-color: #0D1117; padding: 10px; border-radius: 5px; text-align: center; font-family: monospace; font-size: 20px; margin-top: 15px; border: 1px solid #444;">{theme}</div>
    </div>
    """
    st.sidebar.markdown(agent_html, unsafe_allow_html=True)

def draw_neon_strip():
    theme = st.session_state.theme_color
    st.markdown(f"""
    <style>
    .neon-strip {{
        width: 100%; height: 15px;
        background: linear-gradient(90deg, #ff0000, {theme}, #00ff00, #E60B3B, #0000ff);
        background-size: 400% 400%; border-radius: 10px; margin: 10px 0;
        box-shadow: 0 0 20px {theme};
        animation: RGBFlow 2s linear infinite;
    }}
    @keyframes RGBFlow {{ 0% {{ background-position: 0% 50%; }} 100% {{ background-position: 100% 50%; }} }}
    </style>
    <div class="neon-strip"></div>
    """, unsafe_allow_html=True)

# ==========================================
# 5. ROOMS MODULES
# ==========================================
def room_login():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="logic-box" style="text-align:center;">', unsafe_allow_html=True)
        t1, t2 = st.tabs(["🔑 UNLOCK", "📝 NEW AGENT"])
        with t1:
            with st.form("l_form"):
                u = st.text_input("AGENT ID")
                p = st.text_input("PASSWORD", type="password")
                if st.form_submit_button("ACCESS GRANTED", use_container_width=True):
                    user_data = db.reference(f'users/{u}').get()
                    if user_data and user_data.get('pw') == p:
                        st.session_state.user, st.session_state.logged_in = u, True
                        st.rerun()
                    else: st.error("DENIED")
        with t2:
            with st.form("r_form"):
                nu, np = st.text_input("NEW ID"), st.text_input("NEW PW", type="password")
                if st.form_submit_button("REGISTER"):
                    db.reference(f'users/{nu}').set({'pw': np, 'ts': time.time()})
                    st.success("REGISTERED")
        st.markdown('</div>', unsafe_allow_html=True)

def room_core(loc):
    lat, lon = (loc['coords']['latitude'], loc['coords']['longitude']) if loc else (13.7367, 100.5231)
    ct = get_local_time(lat, lon)
    st.markdown(f"""
        <div style="text-align:center; padding:40px; border:4px solid {st.session_state.theme_color}; border-radius:25px; background:rgba(0,0,0,0.6); box-shadow: 0 0 30px {st.session_state.theme_color};">
            <h1 style="font-size:6em; color:{st.session_state.theme_color}; margin:0; font-family: 'Courier New';">{ct.strftime('%H:%M:%S')}</h1>
            <p style="color:#00ff41; font-family:monospace;">📍 POSITION: {lat:.5f}, {lon:.5f}</p>
            <p style="font-weight:bold; font-size:1.5em; color:white;">AGENT {st.session_state.user} ONLINE</p>
        </div>
    """, unsafe_allow_html=True)

def room_radar(loc):
    st.subheader("🛰️ STRATEGIC RADAR")
    my_lat, my_lon = (loc['coords']['latitude'], loc['coords']['longitude']) if loc else (13.7367, 100.5231)
    m = folium.Map(location=[my_lat, my_lon], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr='Google')
    folium.Marker([my_lat, my_lon], icon=folium.Icon(color='red', icon='screenshot', prefix='fa')).add_to(m)
    
    try:
        users = db.reference('users').get()
        if users:
            for uid, data in users.items():
                if uid != st.session_state.user and 'lat' in data:
                    folium.Marker([data['lat'], data['lon']], tooltip=f"AGENT: {uid}", icon=folium.Icon(color='blue')).add_to(m)
    except: pass
    st_folium(m, width="100%", height=450)
    
    if st.button("📡 BROADCAST SIGNAL", use_container_width=True):
        db.reference(f'users/{st.session_state.user}').update({'lat': my_lat, 'lon': my_lon, 'ts': time.time()})
        st.toast("SIGNAL BROADCASTED")

def room_reality_scanner():
    st.subheader("🧬 Reality Extractor")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="logic-box">', unsafe_allow_html=True)
        dob = st.date_input("สแกนรหัสส่วนบุคคล (วันเกิด)", value=date.today())
        if dob:
            logic = get_reality_logic(dob)
            st.metric("REALITY CODE", logic['res'])
            st.write(f"**สภาวะ:** {logic['phase']}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="logic-box">', unsafe_allow_html=True)
        u1 = st.date_input("AGENT 1", value=date(1996, 8, 17))
        u2 = st.date_input("AGENT 2", value=date.today())
        if st.button("COMPUTE GAP"):
            r1, r2 = get_reality_logic(u1)['res'], get_reality_logic(u2)['res']
            gap = abs(r1 - r2)
            st.subheader(f"GAP: {gap:.4f}")
        st.markdown('</div>', unsafe_allow_html=True)

def room_secure_chat():
    st.subheader("💬 SECURE CHAT")
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    target = st.selectbox("🎯 TARGET:", friends)
    if target:
        rid = "_".join(sorted([st.session_state.user, target]))
        chats = db.reference(f'private_rooms/{rid}').order_by_key().limit_to_last(20).get()
        chat_box = st.container(height=200)
        with chat_box:
            if chats:
                for c in chats.values():
                    align = "right" if c['u'] == st.session_state.user else "left"
                    st.markdown(f"<div style='text-align:{align}; margin:5px;'><span style='background:#333; padding:8px; border-radius:10px;'>{c['u']}: {c['m']}</span></div>", unsafe_allow_html=True)
        
        with st.form("msg_f", clear_on_submit=True):
            m = st.text_input("Message...")
            if st.form_submit_button("SEND") and m:
                db.reference(f'private_rooms/{rid}').push({'u': st.session_state.user, 'm': m, 'ts': time.time()})
                st.rerun()

def room_audio_call():
    theme = st.session_state.theme_color
    st.markdown(f'<div class="logic-box" style="text-align:center;"><h2>📞 VOICE ENCRYPTION</h2></div>', unsafe_allow_html=True)
    users = db.reference('users').get()
    friends = [u for u in users.keys() if u != st.session_state.user] if users else []
    target = st.selectbox("SELECT TARGET:", friends, key="v_target")
    
    call_js = f"""
    <div id="call-ui" style="background:#000; padding:20px; border-radius:15px; border:2px solid {theme}; text-align:center; color:white;">
        <h3 id="c-status">📡 READY</h3>
        <audio id="remoteAudio" autoplay></audio>
        <button id="btn-call" style="background:{theme}; color:white; border:none; padding:10px 20px; border-radius:10px; cursor:pointer;">📞 CALL</button>
    </div>
    <script src="https://unpkg.com/peerjs@1.5.2/dist/peerjs.min.js"></script>
    <script>
        const peer = new Peer('{st.session_state.user}');
        peer.on('call', call => {{
            if(confirm("Incoming Call?")) {{
                navigator.mediaDevices.getUserMedia({{audio: true}}).then(s => {{
                    call.answer(s);
                    call.on('stream', rs => {{ document.getElementById('remoteAudio').srcObject = rs; }});
                    document.getElementById('c-status').innerText = "🎙️ CONNECTED";
                }});
            }}
        }});
        document.getElementById('btn-call').onclick = () => {{
            navigator.mediaDevices.getUserMedia({{audio: true}}).then(s => {{
                const call = peer.call('{target}', s);
                call.on('stream', rs => {{ document.getElementById('remoteAudio').srcObject = rs; }});
                document.getElementById('c-status').innerText = "🛰️ CALLING...";
            }});
        }};
    </script>
    """
    components.html(call_js, height=250)

def room_music():
    st.subheader("🎧 MUSIC STATION")
    files = sorted([f for f in os.listdir('.') if f.endswith(".mp3")])
    if files:
        song = files[st.session_state.song_index]
        st.info(f"🎶 Streaming: {song}")
        with open(song, "rb") as f:
            st.audio(f.read(), format="audio/mp3")
        c1, c2, c3 = st.columns(3)
        if c1.button("⏮️ PREV"): st.session_state.song_index = (st.session_state.song_index - 1) % len(files); st.rerun()
        if c3.button("⏭️ NEXT"): st.session_state.song_index = (st.session_state.song_index + 1) % len(files); st.rerun()

# ==========================================
# 6. MAIN CONTROLLER
# ==========================================
def main():
    init_system()
    apply_theme_css()
    loc = get_geolocation() 

    if not st.session_state.logged_in:
        room_login()
        return

    # Sidebar
    with st.sidebar:
        draw_agent_card()
        st.write("---")
        # Color Picker หัวใจหลัก
        picked_color = st.color_picker("🎨 ADJUST THEME", st.session_state.theme_color)
        if picked_color != st.session_state.theme_color:
            st.session_state.theme_color = picked_color
            st.rerun()
        if st.button("🚪 LOGOUT", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        st.write("'อยู่นิ่งๆ ไม่เจ็บตัว'")

    draw_neon_strip()

    # Main Navigation
    tabs = st.tabs(["🏠 CORE", "🛰️ RADAR", "🧬 SCANNER", "💬 CHAT", "📞 VOICE", "🎧 MUSIC"])
    with tabs[0]: room_core(loc)
    with tabs[1]: room_radar(loc)
    with tabs[2]: room_reality_scanner()
    with tabs[3]: room_secure_chat()
    with tabs[4]: room_audio_call()
    with tabs[5]: room_music()

if __name__ == "__main__":
    main()
