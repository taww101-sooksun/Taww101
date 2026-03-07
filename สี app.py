import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import time
from datetime import datetime

# --- 1. SETTING & STYLE (Rainbow Background) ---
st.set_page_config(page_title="SYNAPSE COMMAND", layout="wide", page_icon="🛰️")

st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
        background-size: 1200% 1200%;
        animation: rainbow 15s ease infinite;
    }}
    @keyframes rainbow {{
        0%{{background-position:0% 50%}}
        50%{{background-position:100% 50%}}
        100%{{background-position:0% 50%}}
    }}
    .stTabs, .stMarkdown, .stTextInput, .stButton {{
        background: rgba(0, 0, 0, 0.85);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(0, 255, 0, 0.4);
        color: white;
    }}
    .chat-box {{
        background: rgba(20, 20, 20, 0.9);
        padding: 10px;
        border-radius: 10px;
        height: 300px;
        overflow-y: auto;
        border-left: 4px solid #00ff00;
        margin-bottom: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 2. FIREBASE CONNECTION ---
if not firebase_admin._apps:
    try:
        fb_dict = dict(st.secrets["firebase"])
        fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
        creds = credentials.Certificate(fb_dict)
        firebase_admin.initialize_app(creds, {
            'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })
    except:
        st.error("🚨 ระบบ Firebase ขัดข้อง เช็คการตั้งค่า Secrets")

# --- 3. HEADER & MUSIC ---
col_l, col_r = st.columns([1, 4])
with col_l:
    try: st.image("logo3.jpg", width=500)
    except: st.subheader("🛰️ LOGO")
with col_r:
    st.title("🛰️ SYNAPSE COMMAND CENTER")
    st.caption("อยู่นิ่งๆ ไม่เจ็บตัว | BY Ta101")

yt_playlist = "https://www.youtube.com/embed/videoseries?list=PL6S211I3urvqVH9bDPIr0SLQkENDsNx3Y"
st.markdown(f'<iframe width="100%" height="80" src="{yt_playlist}" frameborder="0" allow="autoplay; encrypted-media"></iframe>', unsafe_allow_html=True)

# --- 4. CORE LOGIC ---
loc = get_geolocation()
if 'my_id' not in st.session_state:
    st.session_state.my_id = "Ta101"

tabs = st.tabs(["🚀 CORE & RADAR", "💬 CHAT CENTER", "📞 TELE-CALL"])

# --- TAB 1: RADAR & GPS ---
with tabs[0]:
    st.session_state.my_id = st.text_input("ระบุชื่อรหัสของคุณ:", value=st.session_state.my_id)
    
    col_gps, col_map = st.columns([1, 2])
    
    with col_gps:
        if loc and 'coords' in loc:
            lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
            st.success(f"📍 GPS Online: {lat}, {lon}")
            if st.button("🛰️ บันทึกพิกัดดาวเทียม"):
                db.reference(f'users/{st.session_state.my_id}').update({
                    'lat': lat, 'lon': lon, 'last_update': time.time()
                })
                st.toast("ส่งข้อมูลพิกัดแล้ว!")
        else:
            st.warning("🚨 รอสัญญาณ GPS...")

    with col_map:
        all_users = db.reference('users').get()
        v_lat, v_lon = 13.75, 100.5
        if all_users and st.session_state.my_id in all_users:
            v_lat = all_users[st.session_state.my_id].get('lat', 13.75)
            v_lon = all_users[st.session_state.my_id].get('lon', 100.5)

        m = folium.Map(location=[v_lat, v_lon], zoom_start=15, 
                       tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google")

        if all_users:
            for name, info in all_users.items():
                if 'lat' in info and 'lon' in info:
                    # สีหมุด: เรา=เขียว, ออนไลน์=ฟ้า, ออฟไลน์=แดง
                    is_active = (time.time() - info.get('last_update', 0)) < 500
                    color = 'green' if name == st.session_state.my_id else ('blue' if is_active else 'red')
                    folium.Marker([info['lat'], info['lon']], tooltip=name,
                                  icon=folium.Icon(color=color, icon='star')).add_to(m)
        st_folium(m, width="100%", height=500)

# --- TAB 2: CHAT SYSTEM (2 ROOMS) ---
with tabs[1]:
    st.subheader("💬 SYNAPSE MESSENGER")
    chat_mode = st.radio("เลือกห้องแชต:", ["🌐 PUBLIC ROOM", "🔒 COMMAND ROOM"], horizontal=True)
    
    room_path = 'chats/public' if chat_mode == "🌐 PUBLIC ROOM" else 'chats/command'
    
    # ดึงข้อความ
    msgs = db.reference(room_path).order_by_child('timestamp').limit_to_last(20).get()
    
    # แสดงกล่องแชต
    chat_display = ""
    if msgs:
        for m_id, m_data in msgs.items():
            t = datetime.fromtimestamp(m_data['timestamp']).strftime('%H:%M')
            chat_display += f"[{t}] **{m_data['user']}**: {m_data['text']}\n\n"
    
    st.markdown(f'<div class="chat-box">{chat_display}</div>', unsafe_allow_html=True)
    
    # ส่งข้อความ
    with st.container():
        msg_text = st.text_input("พิมพ์ข้อความ...", key="chat_input")
        if st.button("🚀 SEND") and msg_text:
            db.reference(room_path).push({
                'user': st.session_state.my_id,
                'text': msg_text,
                'timestamp': time.time()
            })
            st.rerun()

# --- TAB 3: TELE-CALL ---
with tabs[2]:
    st.subheader("📞 DIRECT CALL")
    call_url = "https://ta-sooksun.whereby.com/ta0b9934f8-ae2a-4e0f-b513-58a0616fd29a"
    st.markdown(f'<iframe src="{call_url}?embed&vpa=1&chat=1" allow="camera; microphone; fullscreen; display-capture; compute-pressure" style="height: 650px; width: 100%; border: 2px solid #00ff00; border-radius: 15px;"></iframe>', unsafe_allow_html=True)
