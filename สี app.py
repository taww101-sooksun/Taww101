import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time, datetime, pytz
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from streamlit_autorefresh import st_autorefresh

# 1. SETUP & THEME
st.set_page_config(page_title="SYNAPSE ULTIMATE", layout="wide")
st_autorefresh(interval=10000, key="global_refresh") # ปรับเป็น 10 วินาที เพื่อไม่ให้หนักเครื่อง

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00f2fe"

# --- CSS: สร้างบรรยากาศ Hacker Mode ---
st.markdown(f"""
    <style>
    .stApp {{ background: radial-gradient(circle, #001 0%, #000 100%); color: {st.session_state.theme_color}; }}
    .neon-card {{
        border: 2px solid {st.session_state.theme_color};
        padding: 20px; border-radius: 15px;
        background: rgba(0,0,0,0.7);
        box-shadow: 0 0 15px {st.session_state.theme_color};
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. FIREBASE (เชื่อมต่อแบบเน้นความชัวร์)
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {'databaseURL': st.secrets["firebase_config"]["databaseURL"]})
    except Exception as e:
        st.error(f"⚠️ DATABASE ERROR: {e}")

# 3. SIDEBAR & WORLD CLOCK
with st.sidebar:
    st.markdown("### 🔐 IDENTITY")
    user_id = st.text_input("CODENAME:", value="Agent_101")
    st.session_state.theme_color = st.color_picker("THEME COLOR", st.session_state.theme_color)
    st.write(f"**STATUS:** ONLINE 🟢")
    st.write("---")
    st.write("🌍 **GLOBAL TIME**")
    t_bkk = datetime.datetime.now(pytz.timezone('Asia/Bangkok')).strftime('%H:%M:%S')
    st.write(f"BKK: {t_bkk}")

# 4. MAIN INTERFACE
st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color}; text-shadow: 2px 2px 10px {st.session_state.theme_color};'>SYNAPSE ULTIMATE</h1>", unsafe_allow_html=True)

tab_radar, tab_comms, tab_call = st.tabs(["🛰️ RADAR", "💬 COMMS", "📞 CALL"])

# --- TAB: RADAR (พิกัดดาวเทียม) ---
with tab_radar:
    col_ctrl, col_map = st.columns([1, 3])
    with col_ctrl:
        st.markdown('<div class="neon-card">', unsafe_allow_html=True)
        st.write("📡 **GPS TRANSMITTER**")
        loc = get_geolocation()
        if st.button("🛰️ TRANSMIT LOCATION"):
            if loc:
                db.reference(f'users/{user_id}').set({
                    'lat': loc['coords']['latitude'], 
                    'lon': loc['coords']['longitude'],
                    'color': st.session_state.theme_color,
                    'ts': time.time()
                })
                st.success("POSITION SENT")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_map:
        m = folium.Map(location=[13.75, 100.5], zoom_start=5, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
        try:
            users = db.reference('users').get()
            if users:
                for name, data in users.items():
                    folium.CircleMarker(
                        location=[data['lat'], data['lon']], radius=10,
                        popup=name, color=data.get('color', '#fff'), fill=True
                    ).add_to(m)
        except: pass
        st_folium(m, width="100%", height=500, key="map_radar")

# --- TAB: COMMS (แชตที่เสถียรขึ้น) ---
with tab_comms:
    st.markdown('<div class="neon-card">', unsafe_allow_html=True)
    msg_container = st.container(height=300)
    with st.form("chat_form", clear_on_submit=True):
        input_msg = st.text_input("MESSAGE:")
        if st.form_submit_button("SEND") and input_msg:
            db.reference('global_chat').push({
                'user': user_id, 'msg': input_msg, 'ts': time.time(), 'color': st.session_state.theme_color
            })
    
    # ดึงข้อความมาโชว์
    messages = db.reference('global_chat').order_by_child('ts').limit_to_last(10).get()
    if messages:
        for m_id in messages:
            m = messages[m_id]
            msg_container.markdown(f"<span style='color:{m.get('color','#fff')}'><b>{m['user']}</b></span>: {m['msg']}")
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB: CALL (ส่วนที่ทำให้แอปคุณไม่เหมือนใคร) ---
with tab_call:
    st.warning("⚠️ การสื่อสารผ่าน Video Call ต้องการการอนุญาตใช้กล้องและไมโครโฟน")
    webrtc_streamer(
        key="v-call", 
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    )

st.markdown("---")
st.caption("SYNAPSE ULTIMATE v4.0 | [ อยู่นิ่งๆ ไม่เจ็บตัว ]")
