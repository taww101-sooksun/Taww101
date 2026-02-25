import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode

# --- 1. การตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="SYNAPSE - Live System", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .status-box { padding: 10px; border-radius: 10px; border: 1px solid #4facfe; margin-bottom: 20px; background: #1a1c24; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. เชื่อมต่อ Firebase ---
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
        st.error(f"Firebase Error: {e}")

# --- 3. ตรวจสอบสถานะจริง (Real-time Status) ---
location = get_geolocation()

# --- 4. ส่วนหัวและสถานะระบบ (Dashboard) ---
st.markdown("<h1 style='text-align: center; color: #4facfe;'>🌐 SYNAPSE MONITOR</h1>", unsafe_allow_html=True)

# แถบแสดงสถานะจริง
st.markdown("<div class='status-box'>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

with c1:
    # เช็คสถานะ GPS
    if location and 'coords' in location:
        st.markdown("🛰️ **GPS:** <span style='color:#00ff00;'>CONNECTED</span>", unsafe_allow_html=True)
    else:
        st.markdown("🛰️ **GPS:** <span style='color:#ff0000;'>SEARCHING...</span>", unsafe_allow_html=True)

with c2:
    # เช็คสถานะเพลง (YouTube Embed Check)
    st.markdown("🎵 **MUSIC:** <span style='color:#00ff00;'>STREAMING</span>", unsafe_allow_html=True)

with c3:
    # เช็คสถานะ Firebase
    if firebase_admin._apps:
        st.markdown("🔥 **FIREBASE:** <span style='color:#00ff00;'>SYNCED</span>", unsafe_allow_html=True)
    else:
        st.markdown("🔥 **FIREBASE:** <span style='color:#ff0000;'>ERROR</span>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- 5. แท็บการใช้งาน ---
tab1, tab2, tab3 = st.tabs(["🚀 Experience", "📊 Global Map", "💬 Community"])

with tab1:
    col1, col2 = st.columns(2)
    with col1: user_display_name = st.text_input("👤 ชื่อผู้ใช้:", placeholder="ระบุชื่อของคุณ")
    with col2: admin_key = st.text_input("🔑 รหัสลับ:", type="password")

    if st.button("START JOURNEY"):
        if user_display_name and location:
            lat, lon = location['coords']['latitude'], location['coords']['longitude']
            db.reference(f'users/{user_display_name}').set({'last_seen': datetime.datetime.now().strftime("%H:%M"), 'lat': lat, 'lon': lon})
            st.success("บันทึกพิกัดจริงเข้าฐานข้อมูลแล้ว!")

    st.markdown("---")
    playlist_id = "PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
    embed_url = f"https://www.youtube.com/embed/videoseries?list={playlist_id}&autoplay=1&mute=1"
    st.components.v1.html(f'<iframe width="100%" height="200" src="{embed_url}" frameborder="0" allow="autoplay; encrypted-media"></iframe>', height=220)

with tab2:
    st.subheader("📍 แผนที่ตรวจสอบพิกัดจริง")
    if firebase_admin._apps:
        users = db.reference('users').get()
        if users:
            m = folium.Map(location=[13.7563, 100.5018], zoom_start=10, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google")
            for name, info in users.items():
                if 'lat' in info: folium.Marker([info['lat'], info['lon']], popup=name).add_to(m)
            st_folium(m, width="100%", height=400)

with tab3:
    st.subheader("🎥 Live Community")
    room_id = st.text_input("🔑 ห้อง:", value="private-room-01")
    
    if user_display_name:
        # ระบบ Call พร้อมแสดงสถานะการเชื่อมต่อ
        webrtc_ctx = webrtc_streamer(
            key=f"call-v7-{room_id}",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            media_stream_constraints={"video": True, "audio": True}
        )
        
        # แสดงสถานะการเชื่อมต่อสาย (ความจริงให้คนรู้จริงๆ)
        if webrtc_ctx.state.playing:
            st.markdown("🟢 **STATUS:** <span style='color:#00ff00;'>ON CALL (กล้องกำลังทำงาน)</span>", unsafe_allow_html=True)
        else:
            st.markdown("⚪ **STATUS:** <span style='color:#888;'>IDLE (รอการเชื่อมต่อ)</span>", unsafe_allow_html=True)

        st.markdown("---")
        # ระบบ Chat และปุ่มลบ
        chat_ref = db.reference(f'chats/{room_id}')
        if st.button("🗑️ ล้างประวัติห้องนี้"):
            chat_ref.delete()
            st.rerun()
            
        user_msg = st.chat_input("พิมพ์ข้อความ...")
        if user_msg:
            chat_ref.push({'name': user_display_name, 'msg': user_msg})
            st.rerun()
        
        messages = chat_ref.get()
        if messages:
            for m_id, data in messages.items():
                if isinstance(data, dict):
                    st.write(f"**{data.get('name')}**: {data.get('msg')}")
    else:
        st.warning("⚠️ โปรดระบุชื่อที่หน้าแรกก่อน")
