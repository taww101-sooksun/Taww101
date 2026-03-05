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
st.set_page_config(page_title="SYNAPSE 2026", layout="wide")
st_autorefresh(interval=5000, key="global_refresh") 

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00f2fe"

# --- SIDEBAR: การเข้าถึงและตั้งค่า (รวบตึงให้จบในที่เดียว) ---
with st.sidebar:
    if os.path.exists("logo3.jpg"):
        st.image("logo3.jpg", use_container_width=True)
    
    st.markdown("### 🔐 ACCESS CONTROL")
    user_id = st.text_input("CODENAME:", value="Agent_001")
    st.session_state.theme_color = st.color_picker("เลือกสีประจำตัว / สีหมุด", st.session_state.theme_color)
    
    st.markdown("---")
    st.markdown("### 🗺️ MAP ENGINE 2026")
    map_style = st.selectbox("ระดับความชัด/รูปแบบ:", 
        ["Satellite (ชัดพิเศษ 2026)", "Hybrid (ดาวเทียม+ถนน)", "Dark Radar (ไซไฟ)"])
    
    st.write("---")
    st.write(f"USER: **{user_id}**")
    st.write(f"STATUS: **ONLINE**")
    st.write(f'**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')
    
    st.markdown("---")
    st.markdown("### 🌍 WORLD CLOCK")
    zones = {'Bangkok': 'Asia/Bangkok', 'New York': 'America/New_York', 'London': 'Europe/London', 'Tokyo': 'Asia/Tokyo'}
    for city, zone in zones.items():
        t = datetime.datetime.now(pytz.timezone(zone)).strftime('%H:%M:%S')
        st.write(f"**{city}:** {t}")

# --- CSS CUSTOM STYLE (Neon Hacker) ---
st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; font-family: 'Courier New', Courier, monospace; }}
    .neon-text {{ 
        color: #fff; text-shadow: 0 0 10px {st.session_state.theme_color}, 0 0 20px {st.session_state.theme_color};
        text-align: center; font-weight: 900; border: 2px solid {st.session_state.theme_color}; 
        padding: 15px; background: rgba(0,0,0,0.8); border-radius: 15px; margin-bottom: 25px; letter-spacing: 5px;
    }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{ border: 1px solid {st.session_state.theme_color}; padding: 10px 20px; border-radius: 10px 10px 0 0; }}
    .chat-msg {{ border-left: 3px solid {st.session_state.theme_color}; padding-left: 10px; margin-bottom: 5px; background-color: rgba(255,255,255,0.05); }}
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"<h1 class='neon-text'>SYNAPSE COMMAND CENTER 2026</h1>", unsafe_allow_html=True)

# ==========================================
# 2. FIREBASE CONNECTION
# ==========================================
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except Exception as e:
        st.error(f"⚠️ DATABASE ERROR: {e}")

# ==========================================
# 3. MAIN MENU TABS
# ==========================================
tab_gps, tab_chat, tab_call = st.tabs(["🛰️ GPS & RADAR", "💬 COMMS (แชต)", "📞 VOICE / VIDEO CALL"])

# --- [TAB 1: GPS & RADAR] ---
with tab_gps:
    col_map_ctrl, col_map_display = st.columns([1, 3])
    loc = get_geolocation() 
    
    with col_map_ctrl:
        st.subheader("📡 POSITIONING")
        st.write("กดปุ่มเพื่อส่งตำแหน่งจริงเข้าสู่ระบบ")
        if st.button("🛰️ TRANSMIT LOCATION", use_container_width=True):
            if loc and 'coords' in loc:
                db.reference(f'users/{user_id}').update({
                    'lat': loc['coords']['latitude'], 
                    'lon': loc['coords']['longitude'],
                    'color': st.session_state.theme_color,
                    'last_update': time.time()
                })
                st.success("ส่งพิกัดสำเร็จ!")
            else:
                st.warning("กรุณาเปิด GPS ในเบราว์เซอร์")
    
    with col_map_display:
        # เลือก Engine แผนที่ตามที่ตั้งค่า
        if map_style == "Satellite (ชัดพิเศษ 2026)":
            tile_url = "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}" # Satellite เพียวๆ
            attr = "Google Satellite"
        elif map_style == "Hybrid (ดาวเทียม+ถนน)":
            tile_url = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}" # Hybrid
            attr = "Google Hybrid"
        else:
            tile_url = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" # Dark Mode
            attr = "CartoDB Dark"

        # ตั้งค่าจุดศูนย์กลาง (Center) ไปที่ตัวเรา หรือ กรุงเทพฯ
        all_users = db.reference('users').get()
        v_lat, v_lon = 13.75, 100.5
        if all_users and user_id in all_users:
            v_lat, v_lon = all_users[user_id].get('lat', 13.75), all_users[user_id].get('lon', 100.5)

        m = folium.Map(location=[v_lat, v_lon], zoom_start=18, tiles=tile_url, attr=attr)

        if all_users:
            for name, data in all_users.items():
                if isinstance(data, dict) and 'lat' in data:
                    u_c = data.get('color', st.session_state.theme_color)
                    # วงกลมเรดาร์กะพริบ (Circle)
                    folium.Circle(
                        location=[data['lat'], data['lon']],
                        radius=30, color=u_c, fill=True, fill_opacity=0.2
                    ).add_to(m)
                    # จุดเอเจนท์ (CircleMarker)
                    folium.CircleMarker(
                        location=[data['lat'], data['lon']],
                        radius=8, popup=f"Agent: {name}", color=u_c, fill=True, fill_color=u_c
                    ).add_to(m)
            
        st_folium(m, width="100%", height=600, key=f"map_engine_{map_style}")

# --- [TAB 2: COMMS / แชต] ---
with tab_chat:
    users_data = db.reference('users').get() or {}
    target_list = ["🌐 Global Group"] + [u for u in users_data.keys() if u != user_id]
    
    col_chat1, col_chat2 = st.columns([1, 2])
    with col_chat1:
        target = st.selectbox("เลือกห้อง:", target_list)
    
    path = 'chats/global' if target == "🌐 Global Group" else f"chats/private/{'_'.join(sorted([user_id, target]))}"
    
    chat_container = st.container(height=400)
    try:
        messages = db.reference(path).order_by_child('ts').get()
        if messages:
            for m in sorted(messages.values(), key=lambda x: x.get('ts', 0)):
                c = st.session_state.theme_color if m.get('user') == user_id else "#ff00de"
                chat_container.markdown(f"<div class='chat-msg'><b style='color:{c}'>{m.get('user')}:</b> {m.get('msg')}</div>", unsafe_allow_html=True)
    except: pass

    with st.form("chat_form", clear_on_submit=True):
        col_input, col_btn = st.columns([4, 1])
        msg_input = col_input.text_input("TRANSMIT MESSAGE:", label_visibility="collapsed")
        if col_btn.form_submit_button("SEND 🚀") and msg_input:
            db.reference(path).push({'user': user_id, 'msg': msg_input, 'ts': time.time()})
            st.rerun()

# --- [TAB 3: VOICE & VIDEO CALL] ---
with tab_call:
    st.info("📞 ระบบ WebRTC Peer-to-Peer 2026")
    webrtc_streamer(
        key="synapse-vcall",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": True, "audio": True}
    )

st.write("---")
st.caption(f"SYNAPSE SYSTEM v4.0 PRO | {user_id} | อยู่นิ่งๆ ไม่เจ็บตัว 🤫")
