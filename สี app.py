import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode

# --- 1. การตั้งค่าหน้าเว็บและการออกแบบ ---
st.set_page_config(page_title="SYNAPSE - Live System", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .status-box { padding: 15px; border-radius: 12px; border: 1px solid #4facfe; margin-bottom: 20px; background: #1a1c24; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    .stApp { color: #ffffff; }
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

# --- 3. ดึงพิกัด (ใช้ตรวจสอบสถานะ GPS) ---
location = get_geolocation()

# --- 4. Dashboard แสดงสถานะจริง (ความจริงให้คนรู้จริงๆ) ---
st.markdown("<h1 style='text-align: center; color: #4facfe;'>🌐 SYNAPSE CONTROL</h1>", unsafe_allow_html=True)

st.markdown("<div class='status-box'>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

with c1:
    if location and 'coords' in location:
        st.markdown("🛰️ **GPS Signal:** <span style='color:#00ff00;'>CONNECTED</span>", unsafe_allow_html=True)
    else:
        st.markdown("🛰️ **GPS Signal:** <span style='color:#ff9900;'>SEARCHING...</span>", unsafe_allow_html=True)

with c2:
    # สถานะเพลง/YouTube
    st.markdown("🎵 **MUSIC SYSTEM:** <span style='color:#00ff00;'>ONLINE</span>", unsafe_allow_html=True)

with c3:
    if firebase_admin._apps:
        st.markdown("🔥 **DATABASE:** <span style='color:#00ff00;'>SYNCED</span>", unsafe_allow_html=True)
    else:
        st.markdown("🔥 **DATABASE:** <span style='color:#ff0000;'>DISCONNECTED</span>", unsafe_allow_html=True)
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
            db.reference(f'users/{user_display_name}').set({
                'last_seen': datetime.datetime.now().strftime("%H:%M"),
                'lat': lat, 'lon': lon
            })
            st.success(f"เชื่อมต่อสำเร็จ! พบพิกัดจริงที่: {lat}, {lon}")

    st.markdown("---")
    playlist_id = "PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
    embed_url = f"https://www.youtube.com/embed/videoseries?list={playlist_id}&autoplay=1&mute=1"
    st.components.v1.html(f'<iframe width="100%" height="200" src="{embed_url}" frameborder="0" allow="autoplay; encrypted-media"></iframe>', height=220)

with tab2:
    st.subheader("📍 Real-time Map Connection")
    if firebase_admin._apps:
        users = db.reference('users').get()
        if users:
            m = folium.Map(location=[13.75, 100.5], zoom_start=10, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google")
            for name, info in users.items():
                if isinstance(info, dict) and 'lat' in info:
                    folium.Marker([info['lat'], info['lon']], popup=f"{name} (Active)").add_to(m)
            st_folium(m, width="100%", height=450)

with tab3:
    st.subheader("🎥 Live Community & Call")
    room_id = st.text_input("🔑 ชื่อห้องที่จะเข้า:", value="private-room-01")
    
    if user_display_name:
        # --- ระบบ Video Call + ตัวโชว์สถานะจริง ---
        webrtc_ctx = webrtc_streamer(
            key=f"call-v9-final-{room_id}",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            media_stream_constraints={"video": True, "audio": True},
            video_html_attrs={"style": {"width": "100%", "border-radius": "10px"}, "autoPlay": True}
        )
        
        # โชว์สถานะการโทรจริง
        if webrtc_ctx.state.playing:
            st.markdown("<div style='background:#004400; padding:10px; border-radius:5px;'>🟢 **STATUS:** การเชื่อมต่อสายเสร็จสมบูรณ์ (ON CALL)</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background:#333; padding:10px; border-radius:5px;'>⚪ **STATUS:** รอการกดปุ่ม Start เพื่อเชื่อมต่อสาย</div>", unsafe_allow_html=True)

        st.markdown("---")

        # --- ระบบ Chat (เรียงลำดับใหม่ ไม่ย้อนหลัง) ---
        chat_ref = db.reference(f'chats/{room_id}')
        
        # ดึง 15 ข้อความล่าสุด
        messages_data = chat_ref.order_by_key().limit_to_last(15).get()

        st.write("💬 ข้อความในห้อง:")
        chat_box = st.container()
        with chat_box:
            if messages_data:
                # เรียงจากเก่าไปใหม่ เพื่อให้ข้อความล่าสุดอยู่ล่างสุด
                for m_id in messages_data:
                    data = messages_data[m_id]
                    if isinstance(data, dict):
                        is_me = data.get('name') == user_display_name
                        align = "right" if is_me else "left"
                        color = "#4facfe" if is_me else "#262730"
                        st.markdown(f"""
                            <div style='text-align: {align}; margin-bottom: 10px;'>
                                <div style='display: inline-block; background:{color}; padding:8px 15px; border-radius:15px;'>
                                    <small style='opacity:0.6;'>{data.get('name')}</small><br>{data.get('msg')}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

        user_msg = st.chat_input("พิมพ์ข้อความคุยกับเพื่อน...")
        if user_msg:
            chat_ref.push({
                'name': user_display_name,
                'msg': user_msg,
                'time': datetime.datetime.now().strftime("%H:%M")
            })
            st.rerun()

        if st.button("🗑️ ล้างประวัติแชท"):
            chat_ref.delete()
            st.rerun()
    else:
        st.warning("⚠️ โปรดระบุชื่อที่หน้า 🚀 Experience ก่อนนะเพื่อน")
