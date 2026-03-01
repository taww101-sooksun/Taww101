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
# 1. SETUP & THEME (สีธีมต้องนิ่งและคุมทั้งแอป)
# ==========================================
st.set_page_config(page_title="SYNAPSE ULTIMATE", layout="wide")
st_autorefresh(interval=5000, key="global_refresh") # รีเฟรชอัตโนมัติทุก 5 วิ

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#00f2fe"

# --- SIDEBAR: LOGIN & COLOR PICKER ---
with st.sidebar:
    st.markdown("### 🔐 ACCESS CONTROL")
    user_id = st.text_input("CODENAME:", value="Agent_001")
    # สีธีมที่จะกลายเป็นสีหมุด GPS ของคุณด้วย
    st.session_state.theme_color = st.color_picker("เลือกสีประจำตัว / สีหมุด", st.session_state.theme_color)
    
    st.write("---")
    st.write(f"USER: **{user_id}**")
    st.write(f"STATUS: **ONLINE**")
    st.write(f'**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')
    
    # เพิ่มนาฬิกาโลกใน Sidebar ให้ดูเท่ๆ
    st.markdown("---")
    st.markdown("### 🌍 WORLD CLOCK")
    for city, zone in {'Bangkok': 'Asia/Bangkok', 'New York': 'America/New_York'}.items():
        t = datetime.datetime.now(pytz.timezone(zone)).strftime('%H:%M:%S')
        st.write(f"**{city}:** {t}")

# --- CSS CUSTOM STYLE (ฉีดสีธีมให้ทำงานจริง) ---
st.markdown(f"""
    <style>
    .stApp {{ background: #000; color: {st.session_state.theme_color}; }}
    .neon-text {{ 
        color: #fff; text-shadow: 0 0 10px {st.session_state.theme_color}, 0 0 20px {st.session_state.theme_color};
        text-align: center; font-weight: bold;
    }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{
        border: 1px solid {st.session_state.theme_color};
        padding: 10px 20px; border-radius: 10px 10px 0 0;
    }}
    .chat-msg {{ border-left: 3px solid {st.session_state.theme_color}; padding-left: 10px; margin-bottom: 5px; }}
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LOGO & HEADER (จัดวางกึ่งกลาง)
# ==========================================
col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
with col_l2:
    try:
        st.image("logo3.jpg", use_container_width=True)
    except:
        st.error("⚠️ ไม่พบไฟล์ logo3.jpg ในระบบ")

st.markdown(f"<h1 class='neon-text'>SYNAPSE COMMAND CENTER</h1>", unsafe_allow_html=True)

# ==========================================
# 3. FIREBASE CONNECTION (เช็กการเชื่อมต่อ)
# ==========================================
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'})
    except Exception as e:
        st.error(f"Firebase Error: {e}")

# ==========================================
# 4. MAIN MENU TABS (ทุกเมนูต้องใช้งานได้จริง)
# ==========================================
tab_gps, tab_chat, tab_call = st.tabs(["🛰️ GPS & RADAR", "💬 COMMS (แชต)", "📞 VOICE CALL"])

# --- [TAB: GPS] แก้ปัญหาหมุดหาย และ สีหมุดตามคนเลือก ---
with tab_gps:
    col_map_ctrl, col_map_display = st.columns([1, 3])
    
    with col_map_ctrl:
        st.subheader("📡 ระบบระบุพิกัด")
        if st.button("🛰️ TRANSMIT MY LOCATION"):
            loc = get_geolocation()
            if loc:
                # ส่งพิกัด + สีธีมที่เลือก เข้าไปเก็บใน Firebase
                db.reference(f'users/{user_id}').set({
                    'lat': loc['coords']['latitude'], 
                    'lon': loc['coords']['longitude'],
                    'color': st.session_state.theme_color,
                    'last_update': time.time()
                })
                st.success("ส่งพิกัดสำเร็จ!")
    
    with col_map_display:
        # ดึงข้อมูลทุกคนจาก Firebase มาปักหมุด (หมุดจะไม่หายเพราะดึงใหม่ทุกครั้ง)
        m = folium.Map(location=[13.75, 100.5], zoom_start=6)
        all_users = db.reference('users').get()
        if all_users:
            for name, data in all_users.items():
                if isinstance(data, dict) and 'lat' in data:
                    u_color = data.get('color', st.session_state.theme_color)
                    folium.CircleMarker(
                        location=[data['lat'], data['lon']],
                        radius=10, popup=f"Agent: {name}",
                        color=u_color, fill=True, fill_color=u_color, fill_opacity=0.7
                    ).add_to(m)
        st_folium(m, width="100%", height=500)

# --- [TAB: COMMS] แชตกลุ่ม & แชตส่วนตัว ---
with tab_chat:
    users_data = db.reference('users').get()
    target_list = ["🌐 Global Group"]
    if users_data:
        target_list += [u for u in users_data.keys() if u != user_id]
    
    target = st.selectbox("เลือกช่องทางสื่อสาร:", target_list)
    
    # กำหนดเส้นทางห้องแชต
    if target == "🌐 Global Group":
        path = 'chats/global'
    else:
        room_id = "_".join(sorted([user_id, target]))
        path = f'chats/private/{room_id}'

    # แสดงข้อความแชต
    st.subheader(f"📟 Room: {target}")
    chat_container = st.container(height=400)
    messages = db.reference(path).order_by_child('ts').get()
    
    if messages:
        for m_id, m in messages.items():
            u_name = m.get('user', 'Unknown')
            u_msg = m.get('msg', '')
            txt_color = st.session_state.theme_color if u_name == user_id else "#ff00de"
            chat_container.markdown(f"<div class='chat-msg'><b style='color:{txt_color}'>{u_name}:</b> {u_msg}</div>", unsafe_allow_html=True)

    # ฟอร์มส่งข้อความ
    with st.form("chat_form", clear_on_submit=True):
        msg_input = st.text_input("ระบุข้อความ...")
        if st.form_submit_button("SEND 🛰️") and msg_input:
            db.reference(path).push({
                'user': user_id, 'msg': msg_input, 'ts': time.time()
            })
            st.rerun()

# --- [TAB: CALL] ระบบคอล (WebRTC) ---
with tab_call:
    st.markdown("### 📞 ระบบสื่อสารด้วยเสียงและภาพ (Peer-to-Peer)")
    st.info("กรุณากด 'Start' และอนุญาตให้เข้าถึงไมค์/กล้อง เพื่อเริ่มการโทร")
    webrtc_streamer(
        key="synapse-vcall",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": True, "audio": True}
    )

# ==========================================
# 5. FOOTER (รักษาสโลแกน)
# ==========================================
st.write("---")
st.caption(f"SYNAPSE SYSTEM v2.0 | Logged in as: {user_id} | Theme: {st.session_state.theme_color}")
