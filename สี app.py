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
# รีเฟรชทุก 10 วินาที เพื่อให้หมุดที่ไม่ออนไลน์หายไปตามเวลาจริง
st_autorefresh(interval=10000, key="global_refresh") 

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00f2fe"

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("logo3.jpg"):
        st.image("logo3.jpg", use_container_width=True)
    
    st.markdown("### 🔐 ACCESS CONTROL")
    user_id = st.text_input("CODENAME:", value="Agent_001")
    st.session_state.theme_color = st.color_picker("เลือกสีประจำตัว / สีหมุด", st.session_state.theme_color)
    
    st.markdown("---")
    st.write(f"USER: **{user_id}**")
    st.write(f"STATUS: **📡 MONITORING**")
    st.write(f'**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')
    
    st.markdown("---")
    st.markdown("### 🗺️ MAP SETTINGS")
    map_style = st.selectbox("รูปแบบแผนที่:", ["Satellite", "Hybrid", "Dark"])

# --- CSS STYLE ---
st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; font-family: 'Courier New', Courier, monospace; }}
    .neon-text {{ 
        color: #fff; text-shadow: 0 0 10px {st.session_state.theme_color};
        text-align: center; border: 2px solid {st.session_state.theme_color}; 
        padding: 15px; background: rgba(0,0,0,0.8); border-radius: 15px; margin-bottom: 25px;
    }}
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
    loc = get_geolocation() 
    col_map_ctrl, col_map_display = st.columns([1, 3])
    
    with col_map_ctrl:
        st.subheader("📡 RADAR CONTROL")
        if st.button("🛰️ TRANSMIT LOCATION", use_container_width=True):
            if loc and 'coords' in loc:
                db.reference(f'users/{user_id}').update({
                    'lat': loc['coords']['latitude'], 
                    'lon': loc['coords']['longitude'],
                    'color': st.session_state.theme_color,
                    'last_update': time.time() # ส่ง Timestamp ปัจจุบันไป
                })
                st.success("ส่งสัญญาณพิกัดแล้ว!")
            else:
                st.warning("กรุณาเปิด GPS")
        
        st.write("---")
        st.caption("ระบบจะแสดงหมุดเฉพาะเอเจนท์ที่ออนไลน์ล่าสุดภายใน 1 นาทีเท่านั้น")

    with col_map_display:
        # เลือก Map Tiles
        tiles = "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}" if map_style == "Satellite" else \
                "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}" if map_style == "Hybrid" else \
                "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"

        all_users = db.reference('users').get()
        v_lat, v_lon = 13.75, 100.5
        if all_users and user_id in all_users:
            v_lat, v_lon = all_users[user_id].get('lat', 13.75), all_users[user_id].get('lon', 100.5)

        m = folium.Map(location=[v_lat, v_lon], zoom_start=18, tiles=tiles, attr="Google/Carto")

        # --- ส่วนสำคัญ: กรองเฉพาะคนที่ ONLINE อยู่จริง ---
        current_time = time.time()
        if all_users:
            for name, data in all_users.items():
                if isinstance(data, dict) and 'lat' in data and 'last_update' in data:
                    # เช็คว่าอัปเดตพิกัดภายใน 60 วินาทีที่ผ่านมาหรือไม่
                    if (current_time - data['last_update']) < 60:
                        u_c = data.get('color', st.session_state.theme_color)
                        folium.CircleMarker(
                            location=[data['lat'], data['lon']],
                            radius=10, 
                            popup=f"Agent: {name} (Online)", 
                            color=u_c, fill=True, fill_color=u_c
                        ).add_to(m)
        
        st_folium(m, width="100%", height=500, key=f"map_{map_style}")

# --- [TAB 2: CHAT] (ใช้โค้ดเดิมที่ใช้งานได้อยู่แล้ว) ---
with tab_chat:
    # ... ส่วนของแชตเหมือนเดิม ...
    st.write("ระบบแชตทำงานปกติ")

# --- [TAB 3: VIDEO CALL] ---
with tab_call:
    webrtc_streamer(
        key="synapse-vcall",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": True, "audio": True}
    )

st.write("---")
st.caption(f"SYNAPSE v4.0 PRO | {user_id} | อยู่นิ่งๆ ไม่เจ็บตัว 🤫")
