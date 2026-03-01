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
# 1. SETUP & THEME (สีธีม & Auto Refresh)
# ==========================================
st.set_page_config(page_title="SYNAPSE ULTIMATE", layout="wide")
st_autorefresh(interval=5000, key="global_refresh") # รีเฟรชหน้าจอทุก 5 วิเพื่ออัปเดตแชต/พิกัด

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00f2fe"

# CSS ฉีดสีตามธีมที่เลือก
st.markdown(f"""
    <style>
    .stApp {{ background: radial-gradient(circle, #001 0%, #000 100%); color: {st.session_state.theme_color}; font-family: 'Courier New', Courier, monospace; }}
    .neon-header {{ 
        font-size: 38px; font-weight: 900; text-align: center;
        color: #fff; text-shadow: 0 0 10px {st.session_state.theme_color}, 0 0 20px #ff00de;
        border: 2px solid {st.session_state.theme_color}; padding: 15px; background: rgba(0,0,0,0.8);
        border-radius: 15px; margin-bottom: 25px; letter-spacing: 10px;
    }}
    .clock-box {{
        background: rgba(0,0,0,0.6); border: 1px solid {st.session_state.theme_color};
        padding: 10px; border-radius: 8px; text-align: center;
    }}
    .clock-time {{ color: #ff00de; font-size: 22px; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

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
        st.error(f"DATABASE ERROR: {e}")

# ==========================================
# 3. SIDEBAR (ปรับสี, สโลแกน, เพลง)
# ==========================================
with st.sidebar:
    st.markdown("### 🛰️ NETWORK CENTER")
    st.session_state.theme_color = st.color_picker("เลือกสีนีออนของคุณ", st.session_state.theme_color)
    user_id = st.text_input("CODENAME:", value="Agent_001")
    st.write("---")
    st.write('**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')
    
    # --- 🎵 MUSIC PLAYER ---
    st.markdown("### 🎵 เพลงพื้นหลัง")
    # ใส่ลิงก์เพลง YouTube ที่คุณชอบ
    st.video("https://www.youtube.com/watch?v=wQGq7GWzIuc") 

# ==========================================
# 4. WORLD CLOCK & HEADER
# ==========================================
st.markdown('<div class="neon-header">SYNAPSE ULTIMATE</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
zones = {'BANGKOK': 'Asia/Bangkok', 'NEW YORK': 'America/New_York', 'LONDON': 'Europe/London', 'TOKYO': 'Asia/Tokyo'}
for col, (city, zone) in zip([c1, c2, c3, c4], zones.items()):
    now = datetime.datetime.now(pytz.timezone(zone)).strftime('%H:%M:%S')
    col.markdown(f"<div class='clock-box'><small>{city}</small><br><span class='clock-time'>{now}</span></div>", unsafe_allow_html=True)

st.write("---")

# ==========================================
# 5. MAIN TABS (GPS, แชต, คอล)
# ==========================================
tab_gps, tab_chat, tab_call = st.tabs(["🛰️ GPS & RADAR", "💬 COMMS", "📞 VOICE CALL"])

# --- TAB 1: GPS & RADAR ---
with tab_gps:
    col_map1, col_map2 = st.columns([1, 3])
    with col_map1:
        if st.button("🛰️ TRANSMIT GPS"):
            loc = get_geolocation()
            if loc:
                db.reference(f'users/{user_id}').set({
                    'lat': loc['coords']['latitude'], 
                    'lon': loc['coords']['longitude'],
                    'ts': time.time()
                })
                st.success("POSITION UPDATED")
    with col_map2:
        m = folium.Map(location=[13.75, 100.5], zoom_start=6)
        users = db.reference('users').get()
        if users:
            for name, data in users.items():
                if isinstance(data, dict) and 'lat' in data:
                    folium.Marker([data['lat'], data['lon']], popup=name).add_to(m)
        st_folium(m, width="100%", height=450)

# --- TAB 2: CHAT (Group & Private) ---
with tab_chat:
    all_users = db.reference('users').get()
    u_list = ["🌐 Global Group"]
    if all_users:
        u_list += [u for u in all_users.keys() if u != user_id]
    
    chat_target = st.selectbox("เลือกห้องแชต/ผู้รับ:", u_list)
    room_path = 'chats/global' if chat_target == "🌐 Global Group" else f'chats/private/{"_".join(sorted([user_id, chat_target]))}'

    # แสดงข้อความ
    chat_box = st.container(height=350)
    messages = db.reference(room_path).order_by_child('ts').get()
    if messages:
        for m in sorted(messages.values(), key=lambda x: x.get('ts', 0)):
            u_name = m.get('user', 'Unknown')
            u_msg = m.get('msg', '')
            c = st.session_state.theme_color if u_name == user_id else "#ff00de"
            chat_box.markdown(f"<b style='color:{c}'>{u_name}</b>: {u_msg}", unsafe_allow_html=True)

    with st.form("send_msg", clear_on_submit=True):
        input_msg = st.text_input("TRANSMIT MESSAGE:")
        if st.form_submit_button("SEND 🚀") and input_msg:
            db.reference(room_path).push({'user': user_id, 'msg': input_msg, 'ts': time.time()})
            st.rerun()

# --- TAB 3: VOICE CALL ---
with tab_call:
    st.info("Ice Server: Google STUN")
    webrtc_streamer(
        key="voice-call",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": True, "audio": True},
    )
