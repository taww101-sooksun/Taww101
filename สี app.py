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

# --- SIDEBAR ---
with st.sidebar:
    # แสดง LOGO
    if os.path.exists("logo3.jpg"):
        st.image("logo3.jpg", use_container_width=True)
    
    st.markdown("### 🔐 ACCESS CONTROL")
    user_id = st.text_input("CODENAME:", value="Agent_001")
    st.session_state.theme_color = st.color_picker("RADAR COLOR", st.session_state.theme_color)
    
    # ตัวเลือกแผนที่แบบใหม่ปี 2026
    st.markdown("---")
    st.markdown("### 🗺️ MAP ENGINE 2026")
    map_style = st.selectbox("เลือกรูปแบบแผนที่:", 
        ["Satellite (ชัดพิเศษ)", "Hybrid (ดาวเทียม+ถนน)", "Dark Radar (ไซไฟ)"])
    
    st.write(f"USER: **{user_id}**")
    st.write('**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

# --- CSS NEON STYLE ---
st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; }}
    .neon-text {{ 
        color: #fff; text-shadow: 0 0 10px {st.session_state.theme_color};
        text-align: center; border: 2px solid {st.session_state.theme_color}; 
        padding: 15px; border-radius: 15px; background: rgba(0,0,0,0.8);
    }}
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
    except: pass

# ==========================================
# 3. TABS
# ==========================================
tab_gps, tab_chat, tab_call = st.tabs(["🛰️ GPS & RADAR", "💬 COMMS", "📞 CALL"])

# --- [TAB 1: GPS & RADAR] ---
with tab_gps:
    col_ctrl, col_disp = st.columns([1, 3])
    loc = get_geolocation()
    
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
                st.success("ส่งพิกัดสำเร็จ!")
                st.balloons()

    with col_disp:
        # เลือก Tiles ตามที่ User สั่ง
        if map_style == "Satellite (ชัดพิเศษ)":
            tile_url = "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}" # Satellite only
            attr = "Google Satellite"
        elif map_style == "Hybrid (ดาวเทียม+ถนน)":
            tile_url = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}" # Hybrid
            attr = "Google Hybrid"
        else:
            tile_url = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" # Dark Mode
            attr = "CartoDB Dark"

        all_users = db.reference('users').get()
        
        # ตั้งค่า Center
        v_lat, v_lon = 13.75, 100.5
        if all_users and user_id in all_users:
            v_lat, v_lon = all_users[user_id]['lat'], all_users[user_id]['lon']

        m = folium.Map(location=[v_lat, v_lon], zoom_start=18, tiles=tile_url, attr=attr)

        if all_users:
            for name, data in all_users.items():
                if isinstance(data, dict) and 'lat' in data:
                    # วาดหมุดและวงรัศมีเรดาร์
                    u_c = data.get('color', st.session_state.theme_color)
                    folium.CircleMarker(
                        location=[data['lat'], data['lon']],
                        radius=10, color=u_c, fill=True, popup=name
                    ).add_to(m)
                    folium.Circle(
                        location=[data['lat'], data['lon']],
                        radius=30, color=u_c, weight=1, fill=True, fill_opacity=0.1
                    ).add_to(m)

        st_folium(m, width="100%", height=600, key=f"map_{map_style}")

# --- [TAB 2: CHAT] ---
with tab_chat:
    # (โค้ดแชตเดิมที่คุณมีอยู่แล้ว สามารถวางต่อตรงนี้ได้เลย)
    st.write("💬 ระบบสื่อสารพร้อมใช้งาน...")
    # ... (ส่วนดึงข้อมูลแชตจาก Firebase)

# --- [TAB 3: CALL] ---
with tab_call:
    webrtc_streamer(key="call2026", mode=WebRtcMode.SENDRECV,
                    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

st.write("---")
st.caption(f"SYNAPSE v4.0 PRO | {user_id} | อยู่นิ่งๆ ไม่เจ็บตัว 🤫")
