import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from streamlit_autorefresh import st_autorefresh

# --- 1. SETUP & THEME CUSTOMIZATION ---
st.set_page_config(page_title="SYNAPSE - NEON CONTROL", layout="wide")
st_autorefresh(interval=5000, key="global_refresh")

# แต่ง UI แบบจัดเต็ม (Neon, Shadow, Custom Fonts)
st.markdown("""
    <style>
    /* พื้นหลังดำสนิท */
    .stApp { background: #000; color: #00f2fe; font-family: 'Courier New', Courier, monospace; }
    
    /* หัวข้อใหญ่ ลวดลายเรืองแสง */
    .main-title { 
        font-size: 50px; font-weight: bold; text-align: center;
        color: #fff; text-shadow: 0 0 10px #00f2fe, 0 0 20px #00f2fe, 0 0 40px #00f2fe;
        border-bottom: 2px solid #00f2fe; padding-bottom: 10px; margin-bottom: 20px;
    }
    
    /* ปุ่มกดสไตล์ Futuristic */
    div.stButton > button {
        background: linear-gradient(45deg, #00f2fe, #000);
        color: white; border: 1px solid #00f2fe; border-radius: 0px;
        padding: 10px 20px; text-transform: uppercase; letter-spacing: 2px;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.5); transition: 0.3s;
    }
    div.stButton > button:hover {
        background: #00f2fe; color: #000; box-shadow: 0 0 25px #00f2fe; transform: scale(1.05);
    }
    
    /* กรอบข้อความลวดลาย */
    .content-box {
        border: 1px solid #00f2fe; background: rgba(0, 242, 254, 0.05);
        padding: 15px; border-radius: 5px; margin-bottom: 10px;
    }
    
    /* Tab ให้ดูเหมือนเมนูยานอวกาศ */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #111; border: 1px solid #00f2fe;
        padding: 10px 20px; border-radius: 5px 5px 0 0; color: #00f2fe;
    }
    .stTabs [aria-selected="true"] { background-color: #00f2fe !important; color: #000 !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-title">S Y N A P S E _ V . 1 0 1</div>', unsafe_allow_html=True)

# --- 2. LOGO & MUSIC (Hidden) ---
if os.path.exists("logo3.jpg"):
    st.image("logo3.jpg", width=150)
st.components.v1.html(f"""
    <div style="display:none;">
        <audio id="bg-audio" loop>
            <source src="{direct_link}" type="audio/mpeg">
        </audio>
    </div>
    <script>
        var audio = document.getElementById("bg-audio");
        audio.volume = 0.4;

        // ฟังก์ชันสั่งเล่นเพลง
        function playMusic() {{
            audio.play().catch(function(error) {{
                console.log("Waiting for user interaction...");
            }});
        }}

        // ปลดล็อกเสียงทันทีที่มีการคลิก หรือขยับในแอป
        window.parent.document.addEventListener('mousedown', playMusic, {{ once: true }});
        window.parent.document.addEventListener('keydown', playMusic, {{ once: true }});
        
        // รันซ้ำเผื่อกรณี Refresh
        playMusic();
    </script>
""", height=0)

# --- 3. FIREBASE & LOGIC ---
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        if "private_key" in fb_dict: fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except: pass

# --- 4. NAVIGATION TABS (จัดเต็ม 7 TABS) ---
tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "📊 DATA", "🎵 AUDIO", "📺 MEDIA", "🛠 SYSTEM"])

with tabs[0]: # CORE (EXPERIENCE เดิม)
    st.markdown('<div class="content-box"><h3>USER IDENTIFICATION</h3></div>', unsafe_allow_html=True)
    st.session_state.my_name = st.text_input("ENTER NAME:", value=st.session_state.get('my_name', 'Guest'))
    if st.button("ACTIVATE SYSTEM"):
        loc = get_geolocation()
        if loc:
            raw_time = loc.get('timestamp', datetime.datetime.now().timestamp())
            local_time = datetime.datetime.fromtimestamp(raw_time/1000).strftime('%Y-%m-%d %H:%M:%S')
            db.reference(f'users/{st.session_state.my_name}').set({
                'lat': loc['coords']['latitude'], 'lon': loc['coords']['longitude'],
                'gps_time': local_time, 'status': 'online'
            })
            st.success("SYNCHRONIZED WITH GLOBAL SATELLITES.")

with tabs[1]: # RADAR (MAP เดิม)
    st.markdown('<div class="content-box"><h3>SATELLITE SURVEILLANCE</h3></div>', unsafe_allow_html=True)
    users = db.reference('users').get()
    if users:
        m = folium.Map(location=[13.75, 100.5], zoom_start=2, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
        for name, info in users.items():
            if isinstance(info, dict) and 'lat' in info:
                m_color = 'cadetblue' if name == st.session_state.my_name else 'red'
                folium.Marker([info['lat'], info['lon']], popup=f"{name} ({info.get('gps_time')})",
                              icon=folium.Icon(color=m_color, icon='flash')).add_to(m)
        st_folium(m, width="100%", height=500)

with tabs[2]: # COMMS (CHAT เดิม)
    st.markdown('<div class="content-box"><h3>ENCRYPTED COMMUNICATION</h3></div>', unsafe_allow_html=True)
    col_u, col_chat = st.columns([1, 2])
    # ... ใส่โค้ดแชทแยกสี ฟ้า-แดง ที่เราทำไว้ ...
    st.info("SECURE CONNECTION ESTABLISHED.")

with tabs[4]: # AUDIO
    st.markdown('<div class="content-box"><h3>AUDIO FREQUENCY CONTROL</h3></div>', unsafe_allow_html=True)
    st.write("Current Track: **27-Min Ambient Drive**")
    st.slider("VOLUME CONTROL (EMULATED)", 0, 100, 40)
    st.button("SCAN NEXT TRACK") # ปุ่มหลอกๆ ให้ดูเยอะตามที่เพื่อนชอบ

with tabs[6]: # SYSTEM (SETTINGS เดิม)
    st.markdown('<div class="content-box"><h3>KERNEL SETTINGS</h3></div>', unsafe_allow_html=True)
    st.code("System Version: 1.0.1-NEON\nKernel: Stable\nUptime: 08:23:45", language="text")
    if st.button("HARD RESET"): st.session_state.clear(); st.rerun()

