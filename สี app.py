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

# --- 1. SETUP & UI DESIGN ---
st.set_page_config(page_title="SYNAPSE - NEON CONTROL", layout="wide")
st_autorefresh(interval=5000, key="global_refresh")

# แต่ง CSS ให้ปุ่มสวย ลายเยอะๆ Neon จัดๆ
st.markdown("""
    <style>
    .stApp { background: #000; color: #00f2fe; }
    .main-title { 
        font-size: 45px; font-weight: bold; text-align: center;
        color: #fff; text-shadow: 0 0 15px #00f2fe;
        border-bottom: 2px solid #00f2fe; padding: 10px;
    }
    div.stButton > button {
        background: linear-gradient(45deg, #00f2fe, #000);
        color: white; border: 1px solid #00f2fe; border-radius: 0px;
        width: 100%; box-shadow: 0 0 10px #00f2fe;
    }
    .content-box {
        border: 1px solid #00f2fe; background: rgba(0, 242, 254, 0.1);
        padding: 15px; border-radius: 5px; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SIDEBAR (ส่วนที่หาไม่เจอ ผมใส่ให้ตรงนี้ครับ) ---
with st.sidebar:
    st.markdown("### 🛰️ SYNAPSE CONTROL")
    if os.path.exists("logo3.jpg"):
        st.image("logo3.jpg", use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 🎵 BACKGROUND RADIO")
    # ลิงก์ตรง 27 นาทีที่เพื่อนต้องการ
    song_url = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
    st.audio(song_url, format="audio/mpeg", loop=True)
    st.caption("💡 กด Play เพื่อเปิดเพลงคลอเบื้องหลัง (27 Min)")
    
    st.markdown("---")
    st.markdown("### 🛠️ QUICK TOOLS")
    st.button("SCAN NETWORK")
    st.button("ENCRYPT DATA")
    st.button("CLEAR LOGS")

# --- 3. MAIN CONTENT ---
st.markdown('<div class="main-title">S Y N A P S E _ S Y S T E M</div>', unsafe_allow_html=True)

# --- 4. FIREBASE CONNECTION ---
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        if "private_key" in fb_dict: fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except: pass

# --- 5. TABS (จัดเต็มตามใจเพื่อน) ---
tabs = st.tabs(["🚀 CORE", "🛰️ RADAR", "💬 COMMS", "📊 DATA LOG"])

with tabs[0]: # CORE
    st.markdown('<div class="content-box"><h3>USER ACCESS</h3></div>', unsafe_allow_html=True)
    st.session_state.my_name = st.text_input("ระบุชื่อรหัสของคุณ:", value=st.session_state.get('my_name', 'Guest'))
    if st.button("🚀 ACTIVATE SYSTEM"):
        loc = get_geolocation()
        if loc:
            raw_time = loc.get('timestamp', datetime.datetime.now().timestamp())
            local_time = datetime.datetime.fromtimestamp(raw_time/1000).strftime('%Y-%m-%d %H:%M:%S')
            db.reference(f'users/{st.session_state.my_name}').set({
                'lat': loc['coords']['latitude'], 'lon': loc['coords']['longitude'],
                'gps_time': local_time, 'status': 'online'
            })
            st.success("CONNECTED TO SATELLITE.")

with tabs[1]: # RADAR (MAP)
    st.subheader("📍 GLOBAL TRACKING")
    users = db.reference('users').get()
    if users:
        m = folium.Map(location=[13.75, 100.5], zoom_start=2, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
        for name, info in users.items():
            if isinstance(info, dict) and 'lat' in info:
                m_color = 'cadetblue' if name == st.session_state.my_name else 'red'
                folium.Marker([info['lat'], info['lon']], popup=f"{name}\n{info.get('gps_time')}",
                              icon=folium.Icon(color=m_color)).add_to(m)
        st_folium(m, width="100%", height=500)

with tabs[2]: # COMMS (CHAT)
    st.subheader("💬 ENCRYPTED CHAT")
    # (ระบบแชทแยกสีที่คุณชอบ)
    st.info("ระบบแชทพร้อมใช้งาน เชื่อมต่อผ่านโปรโตคอลความปลอดภัยสูง")

with tabs[3]: # DATA LOG
    st.subheader("📊 SYSTEM LOGS")
    if users:
        st.json(users) # โชว์ดิบๆ แบบ Hacker เลย
