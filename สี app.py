import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import time, datetime, os, hashlib
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. ⚡ SETUP & THEME
# ==========================================
st.set_page_config(page_title="SYNAPSE 2026 PRO", layout="wide")
st_autorefresh(interval=10000, key="global_refresh")

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00f2fe"

# ==========================================
# 2. 🛰️ FIREBASE CONNECTION
# ==========================================
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {
            'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
    except: pass

# ==========================================
# 3. 🔐 LOGIN SYSTEM
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo3.jpg"):
            st.image("logo3.jpg", use_container_width=True)
        st.markdown("<h2 style='text-align:center;'>SYNAPSE LOGIN</h2>", unsafe_allow_html=True)
        
        mode = st.radio("เลือกรายการ:", ["เข้าสู่ระบบ", "ลงทะเบียนเอเจนท์ใหม่"])
        user_input = st.text_input("CODENAME (ไอดี)")
        pw_input = st.text_input("PASSWORD (รหัสผ่าน)", type="password")
        
        if mode == "ลงทะเบียนเอเจนท์ใหม่":
            if st.button("ยืนยันการลงทะเบียน", use_container_width=True):
                if user_input and pw_input:
                    db.reference(f'accounts/{user_input}').set({'password': hash_pass(pw_input)})
                    st.success("ลงทะเบียนสำเร็จ! โปรดเข้าสู่ระบบ")
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

# --- ข้อมูลเอเจนท์ ---
user_id = st.session_state.user_id

# ==========================================
# 4. 🎵 MUSIC & SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown(f"### 👤 AGENT: {user_id}")
    # บังคับเล่นเพลง (ยักษ์ในตัวฉัน)
    music_url = "https://docs.google.com/uc?export=download&id=1AhClqXudsgLtFj7CofAUqPqfX8YW1T7a"
    st.audio(music_url, format="audio/mpeg", loop=True)
    st.caption("🎵 กำลังเล่น: ยักษ์ในตัวฉัน (Loop)")
    
    st.session_state.theme_color = st.color_picker("RADAR COLOR", st.session_state.theme_color)
    if st.button("🔌 LOGOUT", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ==========================================
# 5. 🚀 MAIN INTERFACE
# ==========================================
st.markdown(f"<h1 style='text-align:center; color:{st.session_state.theme_color}; text-shadow: 0 0 10px {st.session_state.theme_color};'>🛰️ SYNAPSE COMMAND CENTER</h1>", unsafe_allow_html=True)

tabs = st.tabs(["🚀 CORE & COMMS", "🛰️ RADAR SYSTEM"])

# --- TAB 1: ระบบส่งพิกัดและแชต ---
with tabs[0]:
    loc = get_geolocation()
    col_pos, col_chat = st.columns([1, 1])
    
    with col_pos:
        st.subheader("📍 POSITIONING")
        if loc:
            lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
            st.success(f"ตรวจพบตำแหน่งจริง: {lat}, {lon}")
            if st.button("🛰️ บันทึกและส่งพิกัดจริง"):
                db.reference(f'users/{user_id}').update({
                    'lat': lat, 'lon': lon, 'color': st.session_state.theme_color, 'last_update': time.time()
                })
                st.balloons()
        else:
            st.warning("🚨 กรุณาเปิด GPS บนเบราว์เซอร์")

    with col_chat:
        st.subheader("💬 GLOBAL CHAT")
        chat_box = st.container(height=250)
        msgs = db.reference('chats/global').order_by_child('ts').limit_to_last(20).get()
        if msgs:
            for m in sorted(msgs.values(), key=lambda x: x.get('ts', 0)):
                chat_box.write(f"**{m['user']}:** {m['msg']}")
        
        with st.form("send_msg", clear_on_submit=True):
            m_input = st.text_input("พิมพ์ข้อความ...")
            if st.form_submit_button("ส่ง 🚀") and m_input:
                db.reference('chats/global').push({'user': user_id, 'msg': m_input, 'ts': time.time()})
                st.rerun()

# --- TAB 2: ระบบแผนที่อัจฉริยะ ---
with tabs[1]:
    all_users = db.reference('users').get()
    
    # โฟกัสไปที่พิกัดเรา ถ้าไม่มีให้ไปกรุงเทพฯ
    v_lat, v_lon = 13.75, 100.5
    if all_users and user_id in all_users:
        v_lat = all_users[user_id].get('lat', 13.75)
        v_lon = all_users[user_id].get('lon', 100.5)

    m = folium.Map(location=[v_lat, v_lon], zoom_start=17, 
                   tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                   attr="Google Satellite")

    curr = time.time()
    if all_users:
        for name, info in all_users.items():
            if 'lat' in info and (curr - info.get('last_update', 0)) < 300: # แสดงเฉพาะคนที่ออนไลน์ใน 5 นาที
                # 🔵 ตัวคุณ (ใช้สีที่เลือก) | 🔴 คนอื่น
                marker_color = 'blue' if name == user_id else 'red'
                folium.Marker(
                    [info['lat'], info['lon']], 
                    tooltip=f"Agent: {name}",
                    icon=folium.Icon(color=marker_color, icon='screenshot', prefix='fa')
                ).add_to(m)
                
    st_folium(m, width="100%", height=600, key="radar_map")

st.caption(f"SYNAPSE v6.0 | ยึดมั่นความจริง | อยู่นิ่งๆ ไม่เจ็บตัว 🤫")
