import streamlit as st
from streamlit_google_auth import Authenticate # ต้อง pip install streamlit-google-auth
import firebase_admin
from firebase_admin import credentials, db
import time, datetime, pytz, os
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. SETUP & THEME
# ==========================================
st.set_page_config(page_title="SYNAPSE 2026 PRO", layout="wide")
st_autorefresh(interval=10000, key="global_refresh") 

# --- ระบบ Google Login (เชื่อมกับ Secrets ที่คุณเพิ่งใส่ไป) ---
# --- แก้ไขบรรทัดที่ 19-22 ให้เป็นแบบนี้ครับ ---
# --- จัดระเบียบใหม่ให้ตรงกันแบบนี้ครับ ---
auth = Authenticate(
    secret_key=st.secrets["google"]["secret_key"],
    client_id=st.secrets["google"]["client_id"],
    client_secret=st.secrets["google"]["client_secret"],
    redirect_uri="https://sooksun101.streamlit.app/",
    cookie_name="sooksun_cookie"
)

    cookie_name="sooksun_cookie"
)

    redirect_uri="https://sooksun101.streamlit.app/",
    cookie_name="sooksun_cookie",
)

# ตรวจสอบว่าล็อกอินหรือยัง
auth.check_authenticity()

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#ff0033"

# ==========================================
# 2. CHECK CONNECTION
# ==========================================
if not st.session_state["connected"]:
    # ถ้ายังไม่เชื่อมต่อ ให้แสดงหน้า Login สวยๆ
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo3.jpg"):
            st.image("logo3.jpg", use_container_width=True)
        st.markdown("<h2 style='text-align:center;'>ACCESS RESTRICTED</h2>", unsafe_allow_html=True)
        st.info("กรุณาล็อกอินด้วย Google เพื่อยืนยันตัวตนเอเจนท์ (1 คน 1 ชื่อ)")
        auth.login()
    st.stop() # หยุดการทำงานที่เหลือจนกว่าจะล็อกอิน

# ดึงชื่อจริงจาก Google มาใช้เป็น user_id (แก้ไม่ได้)
user_info = st.session_state["user_info"]
user_id = user_info.get("name")
user_email = user_info.get("email")

# ==========================================
# 3. FIREBASE CONNECTION
# ==========================================
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except: pass

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo3.jpg"):
        st.image("logo3.jpg", use_container_width=True)
    
    st.markdown(f"### 👤 AGENT: {user_id}")
    st.caption(f"Email: {user_email}")
    st.session_state.theme_color = st.color_picker("RADAR COLOR", st.session_state.theme_color)
    
    if st.button("🔌 LOGOUT", use_container_width=True):
        auth.logout()

    st.markdown("---")
    st.subheader("🧹 ADMIN CONTROL")
    admin_key = st.text_input("ADMIN PASS:", type="password")
    if admin_key == "1234": 
        if st.button("☢️ ERASE ALL DATA", use_container_width=True):
            db.reference('chats').delete()
            db.reference('users').delete()
            st.success("ระบบถูกล้างข้อมูลแล้ว")
            st.rerun()

# --- CSS STYLE ---
st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; font-family: 'Courier New', Courier, monospace; }}
    .neon-text {{ 
        color: #fff; text-shadow: 0 0 10px {st.session_state.theme_color};
        text-align: center; border: 2px solid {st.session_state.theme_color}; 
        padding: 15px; border-radius: 15px; background: rgba(0,0,0,0.8);
    }}
    .chat-msg {{ border-left: 3px solid {st.session_state.theme_color}; padding-left: 10px; margin-bottom: 5px; background: rgba(255,255,255,0.05); }}
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"<h1 class='neon-text'>SYNAPSE COMMAND CENTER 2026</h1>", unsafe_allow_html=True)

# --- [TAB 1: GPS & RADAR] ---
# (โค้ด Tab GPS, Chat, Call ใช้ของเดิมได้เลยครับ เพราะเราเปลี่ยน user_id เป็นชื่อจาก Google แล้ว)
tab_gps, tab_chat, tab_call = st.tabs(["🛰️ GPS & RADAR", "💬 COMMS (แชต)", "📞 VOICE / VIDEO CALL"])

with tab_gps:
    loc = get_geolocation()
    col_ctrl, col_disp = st.columns([1, 3])
    
    with col_ctrl:
        st.subheader("📡 POSITIONING")
        if st.button("🛰️ TRANSMIT LOCATION", use_container_width=True):
            if loc:
                db.reference(f'users/{user_id}').update({
                    'lat': loc['coords']['latitude'], 
                    'lon': loc['coords']['longitude'],
                    'color': st.session_state.theme_color,
                    'last_update': time.time(),
                    'email': user_email
                })
                st.success("ส่งสัญญาณพิกัดแล้ว!")

    with col_disp:
        all_users = db.reference('users').get()
        v_lat, v_lon = 13.75, 100.5
        if all_users and user_id in all_users:
            v_lat, v_lon = all_users[user_id]['lat'], all_users[user_id]['lon']

        m = folium.Map(location=[v_lat, v_lon], zoom_start=18, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                       attr="Google Hybrid")
        
        current_time = time.time()
        if all_users:
            for name, data in all_users.items():
                if isinstance(data, dict) and 'lat' in data:
                    if (current_time - data.get('last_update', 0)) < 600:
                        u_c = data.get('color', st.session_state.theme_color)
                        folium.CircleMarker([data['lat'], data['lon']], radius=10, color=u_c, fill=True, popup=f"{name} ({data.get('email')})").add_to(m)
        st_folium(m, width="100%", height=500, key="radar_main")

# --- โค้ดส่วน Tab Chat และ Tab Call ต่อจากนี้ใช้ของเดิมได้เลยครับ ---
# (ประหยัดพื้นที่แชต ผมขอละไว้ในฐานที่เข้าใจว่ายกของเดิมมาวางต่อได้เลย)
