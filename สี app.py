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
st.set_page_config(page_title="SYNAPSE 2026", layout="wide")
st_autorefresh(interval=10000, key="global_refresh")

# ฟังก์ชันเข้ารหัสผ่านเพื่อความปลอดภัย (ความจริงคือห้ามเก็บรหัสตรงๆ)
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
        firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except: pass

# ==========================================
# 3. LOGIN SYSTEM (Username & Password)
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
        user = st.text_input("CODENAME (ไอดี)")
        pw = st.text_input("PASSWORD (รหัสผ่าน)", type="password")
        
        if mode == "ลงทะเบียนเอเจนท์ใหม่":
            if st.button("ยืนยันการลงทะเบียน", use_container_width=True):
                if user and pw:
                    db.reference(f'accounts/{user}').set({'password': hash_pass(pw)})
                    st.success("ลงทะเบียนสำเร็จ! กรุณาเปลี่ยนเป็นหน้าเข้าสู่ระบบ")
        else:
            if st.button("ACCESS SYSTEM", use_container_width=True):
                stored_data = db.reference(f'accounts/{user}').get()
                if stored_data and stored_data['password'] == hash_pass(pw):
                    st.session_state.logged_in = True
                    st.session_state.user_id = user
                    st.rerun()
                else:
                    st.error("ไอดีหรือรหัสผ่านไม่ถูกต้อง")
    st.stop()

# ข้อมูลผู้ใช้ปัจจุบัน
user_id = st.session_state.user_id

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"### 👤 AGENT: {user_id}")
    if st.button("🔌 LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()
    st.session_state.theme_color = st.color_picker("RADAR COLOR", st.session_state.theme_color)

# --- CSS STYLE ---
st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; }}
    .neon-box {{ border: 2px solid {st.session_state.theme_color}; padding: 20px; border-radius: 15px; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

# --- หน้าหลักพร้อม LOGO ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    if os.path.exists("logo3.jpg"):
        st.image("logo3.jpg", width=100)
with col_title:
    st.markdown(f"<h1 style='text-shadow: 0 0 10px {st.session_state.theme_color};'>SYNAPSE COMMAND CENTER</h1>", unsafe_allow_html=True)

# ==========================================
# 4. MAIN TABS (GPS / CHAT / CALL)
# ==========================================
tab_gps, tab_chat, tab_call = st.tabs(["🛰️ GPS RADAR", "💬 COMMUNICATION", "📞 VOICE CALL"])

with tab_gps:
    # (โค้ดแผนที่คงเดิมจาก v4.0 เพื่อความเรียลไทม์)
    st.write("ระบบเรดาร์ติดตามเอเจนท์ออนไลน์")
    loc = get_geolocation()
    if st.button("🛰️ TRANSMIT LOCATION"):
        if loc:
            db.reference(f'users/{user_id}').update({
                'lat': loc['coords']['latitude'], 'lon': loc['coords']['longitude'],
                'color': st.session_state.theme_color, 'last_update': time.time()
            })
            st.success("ส่งพิกัดแล้ว")
    # ... (ส่วนการวาดแผนที่ Folium) ...

with tab_chat:
    chat_mode = st.radio("เลือกโหมดการสื่อสาร:", ["🌐 แชตหลัก (Global)", "🔒 แชตส่วนตัว (Private)"], horizontal=True)
    
    if chat_mode == "🌐 แชตหลัก (Global)":
        path = 'chats/global'
        st.subheader("GLOBAL CHANNEL")
    else:
        all_users = db.reference('accounts').get() or {}
        other_agents = [u for u in all_users.keys() if u != user_id]
        target = st.selectbox("เลือกเอเจนท์ที่จะคุยด้วย:", other_agents)
        # สร้างห้องแชตเฉพาะ 2 คน (เรียงชื่อตามตัวอักษรเพื่อให้ได้ ID เดียวกัน)
        room_id = "_".join(sorted([user_id, target]))
        path = f'chats/private/{room_id}'
        st.subheader(f"PRIVATE: {user_id} ↔️ {target}")

    # แสดงข้อความ
    chat_box = st.container(height=300)
    messages = db.reference(path).order_by_child('ts').get()
    if messages:
        for m in messages.values():
            color = st.session_state.theme_color if m['user'] == user_id else "#fff"
            chat_box.markdown(f"<p style='color:{color}'><b>{m['user']}:</b> {m['msg']}</p>", unsafe_allow_html=True)

    with st.form("send_msg", clear_on_submit=True):
        msg = st.text_input("พิมพ์ข้อความ...")
        if st.form_submit_button("SEND 🚀") and msg:
            db.reference(path).push({'user': user_id, 'msg': msg, 'ts': time.time()})
            st.rerun()

with tab_call:
    st.write("ระบบสื่อสารด้วยเสียงกำลังทำงาน...")
