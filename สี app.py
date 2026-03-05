import streamlit as st
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

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#ff0033"

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo3.jpg"):
        st.image("logo3.jpg", use_container_width=True)
    
    st.markdown("### 🔐 ACCESS CONTROL")
    user_id = st.text_input("CODENAME:", value="Agent_001")
    st.session_state.theme_color = st.color_picker("RADAR COLOR", st.session_state.theme_color)
    
    st.markdown("---")
    st.subheader("🧹 ADMIN CONTROL")
    admin_key = st.text_input("ADMIN PASS:", type="password", placeholder="กรอกรหัสเพื่อล้างประวัติ")
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

# ==========================================
# 2. MAIN LOGO & HEADER
# ==========================================
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:
    if os.path.exists("logo3.jpg"):
        st.image("logo3.jpg", use_container_width=True)

st.markdown(f"<h1 class='neon-text'>SYNAPSE COMMAND CENTER 2026</h1>", unsafe_allow_html=True)

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

# ==========================================
# 4. MAIN TABS (GPS, CHAT, CALL)
# ==========================================
tab_gps, tab_chat, tab_call = st.tabs(["🛰️ GPS & RADAR", "💬 COMMS (แชต)", "📞 VOICE / VIDEO CALL"])

# --- [TAB 1: GPS & RADAR] ---
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
                    'last_update': time.time()
                })
                st.success("อัปเดตพิกัดแล้ว!")

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
                    # แสดงเฉพาะคนที่ Online ภายใน 10 นาที
                    if (current_time - data.get('last_update', 0)) < 600:
                        u_c = data.get('color', st.session_state.theme_color)
                        folium.CircleMarker([data['lat'], data['lon']], radius=10, color=u_c, fill=True, popup=name).add_to(m)
        st_folium(m, width="100%", height=500, key="radar_main")

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
st.caption(f"SYNAPSE v4.2 PRO | {user_id} | อยู่นิ่งๆ ไม่เจ็บตัว 🤫")
