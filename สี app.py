import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os  # <--- เพิ่มบรรทัดนี้เพื่อแก้ NameError
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer, WebRtcMode

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="SYNAPSE - Live Control", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .status-box { padding: 15px; border-radius: 12px; border: 1px solid #4facfe; background: #1a1c24; margin-bottom: 20px; }
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
        st.error(f"Firebase Connection Error: {e}")

# --- 3. ตรวจสอบพิกัดจริง ---
location = get_geolocation()

# --- 4. ส่วนหัวและโลโก้ (Header & Logo) ---
# ตรวจสอบไฟล์โลโก้และแสดงผล
if os.path.exists("logo3.jpg"):
    col_l, col_m, col_r = st.columns([1, 1, 1])
    with col_m:
        st.image("logo3.jpg", use_container_width=True)
else:
    st.markdown("<h1 style='text-align: center; color: #4facfe;'>🌐 SYNAPSE CONTROL</h1>", unsafe_allow_html=True)

# แถบ Status Dashboard
st.markdown("<div class='status-box'>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f"🛰️ **GPS:** {'🟢 CONNECTED' if location else '🔴 SEARCHING...'}")
with c2: st.markdown("🎵 **MUSIC:** 🟢 ONLINE")
with c3: st.markdown(f"🔥 **DB:** {'🟢 SYNCED' if firebase_admin._apps else '🔴 ERROR'}")
st.markdown("</div>", unsafe_allow_html=True)

# --- 5. แท็บการใช้งาน ---
tab1, tab2, tab3 = st.tabs(["🚀 Experience", "📊 Global Map", "💬 Community"])

with tab1:
    user_display_name = st.text_input("👤 ระบุชื่อผู้ใช้:", placeholder="ระบุชื่อของคุณ")
    if st.button("🚀 UPDATE JOURNEY"):
        if user_display_name and location:
            user_ref = db.reference(f'users/{user_display_name}')
            user_ref.set({
                'lat': location['coords']['latitude'],
                'lon': location['coords']['longitude'],
                'time': datetime.datetime.now().strftime("%H:%M")
            })
            st.success("✅ บันทึกพิกัดใหม่และล้างข้อมูลเก่าแล้ว!")

    st.markdown("---")
    playlist_id = "PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
    embed_url = f"https://www.youtube.com/embed/videoseries?list={playlist_id}&autoplay=1&mute=1"
    st.components.v1.html(f'<iframe width="100%" height="200" src="{embed_url}" frameborder="0" allow="autoplay; encrypted-media"></iframe>', height=220)

with tab2:
    st.subheader("📍 แผนที่ตรวจสอบพิกัดจริง")
    if firebase_admin._apps:
        if st.button("🗑️ Reset Map (ล้างทุกคน)"):
            db.reference('users').delete()
            st.rerun()

        users = db.reference('users').get()
        if users:
            center = [location['coords']['latitude'], location['coords']['longitude']] if location else [13.75, 100.5]
            m = folium.Map(location=center, zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google")
            for name, info in users.items():
                if isinstance(info, dict) and 'lat' in info:
                    folium.Marker([info['lat'], info['lon']], popup=name).add_to(m)
            st_folium(m, width="100%", height=500)

with tab3:
    st.subheader("🎥 Live Community")
    room_id = st.text_input("🔑 ห้อง:", value="private-room-01")
    if user_display_name:
        webrtc_streamer(
            key=f"call-final-{room_id}",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            media_stream_constraints={"video": True, "audio": True}
        )
        st.markdown("---")
        chat_ref = db.reference(f'chats/{room_id}')
        user_msg = st.chat_input("ส่งข้อความ...")
        if user_msg:
            chat_ref.push({'name': user_display_name, 'msg': user_msg, 'time': datetime.datetime.now().strftime("%H:%M")})
            st.rerun()
        
        msgs = chat_ref.order_by_key().limit_to_last(15).get()
        if msgs:
            for m_id in msgs:
                data = msgs[m_id]
                is_me = data.get('name') == user_display_name
                align = "right" if is_me else "left"
                st.markdown(f"<div style='text-align:{align};'><b>{data.get('name')}</b>: {data.get('msg')}</div>", unsafe_allow_html=True)
