import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode

# --- 1. SETTING & CUSTOM NEON UI ---
st.set_page_config(page_title="SYNAPSE - Ultra Control", layout="wide")

st.markdown("""
    <style>
    /* พื้นหลังแบบล้ำสมัย */
    .stApp {
        background: radial-gradient(circle at top right, #0a2342, #0e1117);
        color: #ffffff;
    }
    
    /* กล่อง Glassmorphism */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border-radius: 20px;
        border: 1px solid rgba(0, 242, 254, 0.2);
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    /* ปุ่มกดสไตล์ Neon Glow */
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        background: transparent;
        color: #00f2fe;
        border: 2px solid #00f2fe;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 2px;
        padding: 12px 20px;
        transition: all 0.4s ease;
        box-shadow: 0 0 10px rgba(0, 242, 254, 0.2);
    }
    
    .stButton>button:hover {
        background: #00f2fe;
        color: #0e1117;
        box-shadow: 0 0 30px rgba(0, 242, 254, 0.6);
        transform: scale(1.02);
    }

    /* ตกแต่ง Chat Bubble */
    .chat-bubble {
        padding: 12px 18px;
        border-radius: 20px;
        margin-bottom: 10px;
        max-width: 85%;
        line-height: 1.4;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FIREBASE CONNECTION ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_dict = dict(st.secrets["firebase"])
            if "private_key" in fb_dict:
                fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            creds = credentials.Certificate(fb_dict)
            firebase_admin.initialize_app(creds, {
                'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
    except Exception as e:
        st.error(f"Firebase Connection Error: {e}")

# --- 3. GET LOCATION ---
location = get_geolocation()

# --- 4. HEADER SECTION ---
if os.path.exists("logo3.jpg"):
    col_l, col_m, col_r = st.columns([1, 1, 1])
    with col_m:
        st.image("logo3.jpg", use_container_width=True)
else:
    st.markdown("<h1 style='text-align: center; color: #00f2fe; text-shadow: 0 0 20px rgba(0,242,254,0.5);'>SYNAPSE CONTROL</h1>", unsafe_allow_html=True)

# Dashboard
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f"🛰️ **GPS STATUS:** {'<span style=\"color:#00f2fe\">ONLINE</span>' if location else '<span style=\"color:red\">OFFLINE</span>'}", unsafe_allow_html=True)
with c2: st.markdown("🎵 **SYSTEM:** <span style='color:#00f2fe'>STABLE</span>", unsafe_allow_html=True)
with c3: st.markdown(f"🔥 **DATABASE:** {'<span style=\"color:#00f2fe\">SYNCED</span>' if firebase_admin._apps else '<span style=\"color:red\">ERROR</span>'}", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- 5. TABS ---
tab1, tab2, tab3 = st.tabs(["🚀 EXPERIENCE", "📊 GLOBAL MONITOR", "💬 NEON CHAT"])

with tab1:
    if 'my_name' not in st.session_state: st.session_state.my_name = ""
    
    st.markdown("### 👤 USER IDENTIFICATION")
    name_input = st.text_input("ระบุตัวตนของคุณ:", value=st.session_state.my_name, placeholder="NAME / CODE NAME")
    
    if st.button("🚀 ACTIVATE STATUS"):
        if name_input and location:
            st.session_state.my_name = name_input
            db.reference(f'users/{name_input}').set({
                'lat': location['coords']['latitude'],
                'lon': location['coords']['longitude'],
                'time': datetime.datetime.now().strftime("%H:%M")
            })
            st.success(f"ACCESS GRANTED: {name_input}")
    
    st.markdown("---")
    playlist_id = "PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
    embed_url = f"https://www.youtube.com/embed/videoseries?list={playlist_id}&autoplay=1&mute=1"
    st.components.v1.html(f'<iframe width="100%" height="250" src="{embed_url}" frameborder="0" style="border-radius:15px;" allow="autoplay; encrypted-media"></iframe>', height=270)

with tab2:
    st.subheader("📍 LIVE GEOLOCATION")
    if firebase_admin._apps:
        if st.button("🗑️ CLEAR ALL DATA"):
            db.reference('users').delete()
            st.rerun()
            
        users_data = db.reference('users').get()
        if users_data:
            center = [location['coords']['latitude'], location['coords']['longitude']] if location else [13.75, 100.5]
            m = folium.Map(location=center, zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Hybrid")
            for name, info in users_data.items():
                if isinstance(info, dict) and 'lat' in info:
                    folium.Marker([info['lat'], info['lon']], popup=name, icon=folium.Icon(color='blue', icon='info-sign')).add_to(m)
            st_folium(m, width="100%", height=550)

with tab3:
    my_name = st.session_state.get('my_name', "")
    if not my_name:
        st.warning("โปรดระบุตัวตนที่หน้า 🚀 EXPERIENCE ก่อนเข้าสู่ระบบแชท")
    else:
        all_u = db.reference('users').get()
        col_list, col_chat = st.columns([1, 2])

        with col_list:
            st.markdown("### 👥 ONLINE")
            if all_u:
                for f_name in all_u.keys():
                    if f_name != my_name:
                        if st.button(f"⚡ {f_name}", key=f"btn-{f_name}"):
                            pair = sorted([my_name, f_name])
                            st.session_state.private_room = f"secret_{pair[0]}_{pair[1]}"
                            st.session_state.target_name = f_name
            else: st.write("Searching for users...")

        with col_chat:
            room = st.session_state.get('private_room', None)
            target = st.session_state.get('target_name', None)
            
            if room and target:
                st.markdown(f"#### 🔒 ENCRYPTED: {target}")
                
                # VIDEO CALL v12
                webrtc_streamer(
                    key=f"call-v12-{room}",
                    mode=WebRtcMode.SENDRECV,
                    rtc_configuration={"iceServers": [
                        {"urls": ["stun:stun.l.google.com:19302"]},
                        {"urls": ["stun:global.stun.twilio.com:3478"]},
                        {"urls": ["stun:stun.services.mozilla.com"]}
                    ]},
                    media_stream_constraints={"video": True, "audio": True},
                    async_processing=True
                )
                
                st.markdown("---")
                chat_ref = db.reference(f'chats/{room}')
                
                # Chat Input
                msg_in = st.chat_input(f"Send message to {target}...")
                if msg_in:
                    chat_ref.push({'name': my_name, 'msg': msg_in, 'ts': datetime.datetime.now().timestamp()})
                    st.rerun()
                
                # Message Display
                msgs = chat_ref.order_by_child('ts').limit_to_last(20).get()
                if msgs:
                    for m_id in msgs:
                        d = msgs[m_id]
                        is_me = d.get('name') == my_name
                        align = "right" if is_me else "left"
                        bg = "rgba(0, 242, 254, 0.3)" if is_me else "rgba(255, 255, 255, 0.08)"
                        st.markdown(f"""
                            <div style='text-align: {align};'>
                                <div class='chat-bubble' style='display: inline-block; background: {bg}; border: 1px solid rgba(0,242,254,0.1);'>
                                    <small style='color:#00f2fe; font-size:10px;'>{d.get('name')}</small><br>{d.get('msg')}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                
                if st.button("🗑️ CLEAR ROOM"):
                    chat_ref.delete()
                    st.rerun()
            else:
                st.info("👈 SELECT A USER TO START SECURE CHAT")
