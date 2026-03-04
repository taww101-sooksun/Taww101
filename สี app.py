import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time, datetime, pytz
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from streamlit_autorefresh import st_autorefresh

# ==========================================
# 1. SETUP & THEME
# ==========================================
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")
# รีเฟรชหน้าจออัตโนมัติทุก 10 วินาที เพื่ออัปเดตแชตและเรดาร์
st_autorefresh(interval=10000, key="global_refresh") 

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00f2fe"

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### 🔐 ACCESS CONTROL")
    user_id = st.text_input("CODENAME:", value="Agent_001")
    st.session_state.theme_color = st.color_picker("เลือกสีประจำตัว / หมุด", st.session_state.theme_color)
    
    st.write("---")
    st.write(f"USER: **{user_id}**")
    st.write(f"STATUS: **ONLINE**")
    st.write('**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')
    
    st.markdown("---")
    st.markdown("### 🌍 WORLD CLOCK")
    zones = {'Bangkok': 'Asia/Bangkok', 'Tokyo': 'Asia/Tokyo', 'London': 'Europe/London'}
    for city, zone in zones.items():
        t = datetime.datetime.now(pytz.timezone(zone)).strftime('%H:%M:%S')
        st.write(f"**{city}:** {t}")

# --- CSS CUSTOM STYLE ---
st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; font-family: 'Courier New', monospace; }}
    .neon-text {{ 
        color: #fff; text-shadow: 0 0 10px {st.session_state.theme_color};
        text-align: center; border: 2px solid {st.session_state.theme_color}; 
        padding: 15px; background: rgba(0,0,0,0.8); border-radius: 15px; margin-bottom: 25px;
    }}
    .chat-msg {{ border-left: 3px solid {st.session_state.theme_color}; padding-left: 10px; margin-bottom: 5px; background: rgba(255,255,255,0.05); }}
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"<h1 class='neon-text'>SYNAPSE COMMAND CENTER</h1>", unsafe_allow_html=True)

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
        st.subheader("📡 GPS CONTROL")
        if st.button("🛰️ TRANSMIT LOCATION", use_container_width=True):
            if loc and 'coords' in loc:
                try:
                    db.reference(f'users/{user_id}').update({
                        'lat': loc['coords']['latitude'], 
                        'lon': loc['coords']['longitude'],
                        'color': st.session_state.theme_color,
                        'last_update': time.time()
                    })
                    st.success("ส่งพิกัดสำเร็จ!")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("🚨 กรุณากด Allow GPS")

    with col_map_display:
        all_users = db.reference('users').get()
        view_lat, view_lon = 13.75, 100.5 
        if all_users and user_id in all_users:
            view_lat = all_users[user_id].get('lat', 13.75)
            view_lon = all_users[user_id].get('lon', 100.5)

        m = folium.Map(location=[view_lat, view_lon], zoom_start=18, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", 
                       attr="Google Satellite")

        if all_users:
            for name, data in all_users.items():
                if isinstance(data, dict) and 'lat' in data:
                    u_lat, u_lon = data['lat'], data['lon']
                    diff = time.time() - data.get('last_update', 0)
                    m_color = 'blue' if name == user_id else 'red'
                    if diff > 120: m_color = 'gray'

                    folium.Marker([u_lat, u_lon], tooltip=name, 
                                  icon=folium.Icon(color=m_color)).add_to(m)
                    folium.Circle([u_lat, u_lon], radius=40, color=data.get('color', '#00f2fe'), 
                                  fill=True, fill_opacity=0.2).add_to(m)

        st_folium(m, width="100%", height=500, key=f"map_{user_id}")

# --- [TAB 2: COMMS / แชต] ---
with tab_chat:
    users_data = db.reference('users').get() or {}
    target_list = ["🌐 Global Group"] + [u for u in users_data.keys() if u != user_id]
    
    target = st.selectbox("ช่องทาง:", target_list)
    path = 'chats/global' if target == "🌐 Global Group" else f"chats/private/{'_'.join(sorted([user_id, target]))}"

    chat_container = st.container(height=350)
    try:
        messages = db.reference(path).order_by_child('ts').limit_to_last(20).get()
        if messages:
            for m in sorted(messages.values(), key=lambda x: x.get('ts', 0)):
                c = st.session_state.theme_color if m['user'] == user_id else "#ff00de"
                chat_container.markdown(f"<div class='chat-msg'><b style='color:{c}'>{m['user']}:</b> {m['msg']}</div>", unsafe_allow_html=True)
    except: pass

    with st.form("chat_form", clear_on_submit=True):
        col_in, col_bt
