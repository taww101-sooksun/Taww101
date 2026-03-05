import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time, datetime, os, hashlib
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. SETUP & UTILS
# ==========================================
st.set_page_config(page_title="SYNAPSE 2026 PRO", layout="wide")
st_autorefresh(interval=10000, key="global_refresh") 

# ฟังก์ชันเข้ารหัสผ่าน (เพื่อความปลอดภัยตามหลักความจริง)
def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#ff0033"

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
# 3. LOGIN & REGISTER SYSTEM
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if os.path.exists("logo3.jpg"):
            st.image("logo3.jpg", use_container_width=True)
        st.markdown("<h2 style='text-align:center;'>SYNAPSE ACCESS</h2>", unsafe_allow_html=True)
        
        auth_mode = st.tabs(["เข้าสู่ระบบ", "ลงทะเบียนใหม่"])
        
        with auth_mode[0]:
            l_user = st.text_input("CODENAME:", key="l_user")
            l_pass = st.text_input("PASSWORD:", type="password", key="l_pass")
            if st.button("เข้าสู่ระบบ 🔓", use_container_width=True):
                user_data = db.reference(f'accounts/{l_user}').get()
                if user_data and user_data['pw'] == hash_pass(l_pass):
                    st.session_state.logged_in = True
                    st.session_state.user_id = l_user
                    st.rerun()
                else:
                    st.error("ไอดีหรือรหัสผ่านไม่ถูกต้อง")

        with auth_mode[1]:
            r_user = st.text_input("ตั้ง CODENAME:", key="r_user")
            r_pass = st.text_input("ตั้ง PASSWORD:", type="password", key="r_pass")
            if st.button("ยืนยันการลงทะเบียน 📝", use_container_width=True):
                if r_user and r_pass:
                    db.reference(f'accounts/{r_user}').set({'pw': hash_pass(r_pass)})
                    st.success("ลงทะเบียนสำเร็จ! โปรดสลับไปหน้าเข้าสู่ระบบ")
    st.stop()

# --- ข้อมูลหลัง Login ---
user_id = st.session_state.user_id

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"### 👤 AGENT: {user_id}")
    if st.button("🔌 LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()
    st.session_state.theme_color = st.color_picker("RADAR COLOR", st.session_state.theme_color)
    st.markdown("---")
    st.write('**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

# --- CSS STYLE ---
st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; font-family: 'Courier New', monospace; }}
    .neon-text {{ 
        color: #fff; text-shadow: 0 0 10px {st.session_state.theme_color};
        text-align: center; border: 2px solid {st.session_state.theme_color}; 
        padding: 15px; border-radius: 15px; background: rgba(0,0,0,0.8);
    }}
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"<h1 class='neon-text'>SYNAPSE COMMAND CENTER 2026</h1>", unsafe_allow_html=True)

# ==========================================
# 4. MAIN TABS
# ==========================================
tab_gps, tab_chat, tab_call = st.tabs(["🛰️ GPS & RADAR", "💬 COMMS (แชต)", "📞 CALL"])

with tab_gps:
    loc = get_geolocation()
    col_c, col_d = st.columns([1, 3])
    
    with col_c:
        st.subheader("📡 RADAR")
        if st.button("🛰️ TRANSMIT LOCATION", use_container_width=True):
            if loc:
                db.reference(f'users/{user_id}').update({
                    'lat': loc['coords']['latitude'], 
                    'lon': loc['coords']['longitude'],
                    'color': st.session_state.theme_color,
                    'last_update': time.time()
                })
                st.success("พิกัดถูกส่งแล้ว!")

    with col_d:
        all_users = db.reference('users').get()
        v_lat, v_lon = 13.75, 100.5
        if all_users and user_id in all_users:
            v_lat, v_lon = all_users[user_id]['lat'], all_users[user_id]['lon']

        m = folium.Map(location=[v_lat, v_lon], zoom_start=18, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
        
        curr_t = time.time()
        if all_users:
            for name, data in all_users.items():
                if isinstance(data, dict) and 'lat' in data:
                    # ออนไลน์ไม่เกิน 10 นาที
                    if (curr_t - data.get('last_update', 0)) < 600:
                        u_color = data.get('color', st.session_state.theme_color)
                        
                        # --- ส่วนสำคัญ: เพิ่มชื่อบนหมุด (Marker Tooltip/Permanent Label) ---
                        folium.Marker(
                            [data['lat'], data['lon']],
                            icon=folium.DivIcon(html=f"""
                                <div style="font-family: 'Courier New'; font-weight: bold; color: white; 
                                background: {u_color}; border: 1px solid white; padding: 2px 5px; 
                                border-radius: 5px; font-size: 10pt; white-space: nowrap;">
                                {name}
                                </div>
                            """)
                        ).add_to(m)
                        
                        folium.CircleMarker(
                            [data['lat'], data['lon']], 
                            radius=8, color=u_color, fill=True
                        ).add_to(m)
# --- [TAB 2: CHAT SYSTEM] ---
with tab_chat:
    users_data = db.reference('users').get() or {}
    target_list = ["🌐 Global Group"] + [u for u in users_data.keys() if u != user_id]
    target = st.selectbox("เลือกช่องทางสื่อสาร:", target_list)
    
    path = 'chats/global' if target == "🌐 Global Group" else f"chats/private/{'_'.join(sorted([user_id, target]))}"
    
    chat_container = st.container(height=350)
    messages = db.reference(path).order_by_child('ts').get()
    if messages:
        for m in sorted(messages.values(), key=lambda x: x.get('ts', 0)):
            u_name = m.get('user', 'Unknown')
            txt_c = st.session_state.theme_color if u_name == user_id else "#ff00de"
            chat_container.markdown(f"<div class='chat-msg'><b style='color:{txt_c}'>{u_name}:</b> {m.get('msg')}</div>", unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        col_in, col_bt = st.columns([4, 1])
        msg_in = col_in.text_input("TRANSMIT MESSAGE:", label_visibility="collapsed")
        if col_bt.form_submit_button("SEND 🚀") and msg_in:
            db.reference(path).push({'user': user_id, 'msg': msg_in, 'ts': time.time()})
            st.rerun()

# --- [TAB 3: VIDEO CALL SYSTEM] ---
with tab_call:
    st.markdown("### 📞 P2P ENCRYPTED CALL")
    st.info("เปิดกล้องและไมค์เพื่อสื่อสารกับเอเจนท์คนอื่นในเครือข่าย")
    webrtc_streamer(
        key="synapse-vcall-2026",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": True, "audio": True}
    )

st.write("---")
st.caption(f"SYNAPSE v4.2 PRO | {user_id} | อยู่นิ่งๆ ไม่เจ็บตัว 🤫")        st_folium(m, width="100%", height=500, key="radar_main")

# (ส่วนแชตและ Call ใช้โค้ดเดิมที่เพื่อนมีได้เลยครับ)
# ... [CHAT & CALL CODE] ...
