import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time, datetime, os, hashlib
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. SETUP & CONFIG
# ==========================================
st.set_page_config(page_title="SYNAPSE 2026 PRO", layout="wide")
# รีเฟรชทุก 10 วินาทีเพื่อให้แผนที่และแชตเป็นปัจจุบัน
st_autorefresh(interval=10000, key="global_refresh")

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00f2fe"

# ==========================================
# 2. FIREBASE CONNECTION
# ==========================================
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {
            'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
    except Exception as e:
        st.error(f"⚠️ DATABASE ERROR: {e}")

# ==========================================
# 3. LOGIN SYSTEM
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo3.jpg"):
            st.image("logo3.jpg", use_container_width=True)
        st.markdown("<h2 style='text-align:center;'>SYNAPSE LOGIN</h2>", unsafe_allow_html=True)
        
        mode = st.radio("SELECT MODE:", ["LOGIN", "REGISTER"])
        user_input = st.text_input("CODENAME")
        pw_input = st.text_input("PASSWORD", type="password")
        
        if mode == "REGISTER":
            if st.button("CONFIRM REGISTRATION", use_container_width=True):
                if user_input and pw_input:
                    db.reference(f'accounts/{user_input}').set({'password': hash_pass(pw_input)})
                    st.success("ลงทะเบียนสำเร็จ! โปรดเปลี่ยนไปโหมด LOGIN")
        else:
            if st.button("ACCESS SYSTEM", use_container_width=True):
                stored = db.reference(f'accounts/{user_input}').get()
                if stored and stored['password'] == hash_pass(pw_input):
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_input
                    st.rerun()
                else:
                    st.error("ไอดีหรือรหัสผ่านไม่ถูกต้อง")
    st.stop()

# --- ข้อมูลผู้ใช้ ---
user_id = st.session_state.user_id

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"### 👤 AGENT: {user_id}")
    st.write("STATUS: **ONLINE**")
    if st.button("🔌 LOGOUT", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()
    st.session_state.theme_color = st.color_picker("RADAR COLOR", st.session_state.theme_color)
    st.markdown("---")
    st.caption('สโลแกน: "อยู่นิ่งๆ ไม่เจ็บตัว"')

# --- CSS STYLE ---
st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; font-family: 'Courier New', monospace; }}
    .chat-msg {{ border-left: 3px solid {st.session_state.theme_color}; padding-left: 10px; margin-bottom: 8px; background: rgba(255,255,255,0.05); border-radius: 0 5px 5px 0; }}
    .neon-text {{ text-shadow: 0 0 10px {st.session_state.theme_color}; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# --- หน้าหลัก Header ---
col_logo, col_title = st.columns([1, 5])
with col_logo:
    if os.path.exists("logo3.jpg"):
        st.image("logo3.jpg", width=80)
with col_title:
    st.markdown(f"<h1 class='neon-text'>SYNAPSE COMMAND CENTER 2026</h1>", unsafe_allow_html=True)

# ==========================================
# 4. MAIN TABS
# ==========================================
tab_gps, tab_chat, tab_call = st.tabs(["🛰️ GPS RADAR", "💬 COMMUNICATION", "📞 VOICE CALL"])

# --- TAB 1: GPS RADAR (เรียลไทม์ 60 วินาที) ---
with tab_gps:
    loc = get_geolocation()
    col_ctrl, col_map = st.columns([1, 3])
    
    with col_ctrl:
        st.subheader("📡 RADAR")
        if st.button("🛰️ TRANSMIT POSITION", use_container_width=True):
            if loc:
                db.reference(f'users/{user_id}').update({
                    'lat': loc['coords']['latitude'], 
                    'lon': loc['coords']['longitude'],
                    'color': st.session_state.theme_color,
                    'last_update': time.time()
                })
                st.success("พิกัดถูกส่งเข้าสู่ระบบแล้ว")
        st.caption("หมุดจะแสดงเฉพาะผู้ที่ออนไลน์ใน 60 วินาทีล่าสุด")

    with col_map:
        all_users = db.reference('users').get()
        v_lat, v_lon = 13.75, 100.5
