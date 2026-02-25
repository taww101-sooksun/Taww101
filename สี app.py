import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium
from streamlit_webrtc import webrtc_streamer # เพิ่มส่วนนี้สำหรับระบบคอล

# --- 1. ตั้งค่าหน้าเว็บและการออกแบบ (Premium Dark UI) ---
st.set_page_config(page_title="SYNAPSE - Premium System", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { color: #ffffff; }
    .stButton>button {
        width: 100%; border-radius: 20px;
        background: linear-gradient(45deg, #00f2fe 0%, #4facfe 100%);
        color: white; border: none; font-weight: bold; transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(0, 242, 254, 0.4); }
    .stTabs [aria-selected="true"] { background-color: #4facfe !important; }
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

def get_time_by_coords(lon):
    if lon is None: return datetime.datetime.now()
    offset = round(float(lon) / 15)
    return datetime.datetime.utcnow() + datetime.timedelta(hours=offset)

# --- 3. ส่วนหัว (Header) และโลโก้ ---
st.markdown("<h1 style='text-align: center; color: #4facfe;'>🌐 SYNAPSE</h1>", unsafe_allow_html=True)

# ตรวจสอบไฟล์โลโก้ (Logo3.jpg)
if os.path.exists("logo3.jpg"):
    col_l, col_m, col_r = st.columns([1,1,1])
    with col_m:
        st.image("logo3.jpg", width=300)
elif os.path.exists("logo3.jpg"):
    col_l, col_m, col_r = st.columns([1,1,1])
    with col_m:
        st.image("logo3.jpg", width=150)

location = get_geolocation()

# --- 4. ระบบแจ้งเตือน (เงียบ - ป้องกันเพลงดับ) ---
if 'last_chat_count' not in st.session_state:
    st.session_state.last_chat_count = 0
def check_notifications():
    try:
        chats = db.reference('chats').get()
        if chats:
            current_count = len(chats)
            if current_count > st.session_state.last_chat_count:
                if st.session_state.last_chat_count != 0:
                    st.toast("💬 มีข้อความใหม่!", icon="🔔")
                st.session_state.last_chat_count = current_count
    except: pass
check_notifications()

# --- 5. แท็บการใช้งาน ---
tab1, tab2, tab3 = st.tabs(["🚀 Experience", "📊 Global Map", "💬 Community"])

with tab1:
    col1, col2 = st.columns(2)
    with col1: user_display_name = st.text_input("👤 ชื่อผู้ใช้:", placeholder="ระบุชื่อของคุณ")
    with col2: admin_key = st.text_input("🔑 รหัสลับ:", type="password")

    if st.button("START JOURNEY"):
        if user_display_name and location and 'coords' in location:
            lat, lon = location['coords']['latitude'], location['coords']['longitude']
            time_str = get_time_by_coords(lon).strftime("%H:%M")
            if firebase_admin._apps:
                db.reference(f'users/{user_display_name}').set({'last_seen': time_str, 'lat': lat, 'lon': lon})
                st.success(f"เชื่อมต่อสำเร็จ! เวลา: {time_str}")

    st.markdown("---")
    # YouTube Playlist (วนลูป + ไม่ดับง่าย)
    playlist_id = "PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
    embed_url = f"https://www.youtube.com/embed/videoseries?list={playlist_id}&autoplay=1&loop=1&playlist={playlist_id}&enablejsapi=1"
    
    st.markdown("<h3 style='color: #888;'>🎧 Streaming Therapy...</h3>", unsafe_allow_html=True)
    st.components.v1.html(
        f'<div style="border-radius: 15px; overflow: hidden;"><iframe width="100%" height="250" src="{embed_url}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>',
        height=270,
    )

with tab2:
    st.subheader("📍 ตำแหน่งผู้ใช้งาน")
    if firebase_admin._apps:
        users_ref = db.reference('users').get()
        if users_ref:
            valid_users = []
            for k, v in users_ref.items():
                if isinstance(v, dict) and 'lat' in v:
                    valid_users.append({'name': k, 'lat': v['lat'], 'lon': v['lon'], 'time': v.get('last_seen', '--:--')})
            if valid_users:
                m = folium.Map(location=[valid_users[0]['lat'], valid_users[0]['lon']], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google Satellite")
                for u in valid_users: folium.Marker([u['lat'], u['lon']], popup=u['name']).add_to(m)
                st_folium(m, width=None, height=450)

with tab3:
    st.subheader("🎥 Live Call & Chat (Community)")
    
    # 1. กำหนดชื่อห้อง
    room_name = st.text_input("🔑 ระบุชื่อห้องที่จะเข้า:", value="private-room-01")
    
    if user_display_name:
        st.write(f"กำลังเข้าสู่ห้อง: **{room_name}**")
        
        # 2. ส่วนของระบบคอล (Video Call)
        webrtc_streamer(
            key=f"call-{room_name}",
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            media_stream_constraints={"video": True, "audio": True},
            video_html_attrs={
                "style": {"width": "100%", "border-radius": "15px", "border": "2px solid #4facfe"},
                "autoPlay": True,
            }
        )

        st.markdown("---")
        
        # 3. ส่วนของระบบแชท (Chat Room)
        chat_ref = db.reference(f'chats/{room_name}')
        messages = chat_ref.order_by_key().limit_to_last(10).get()

        # แสดงข้อความแชท
        if messages:
            for msg_id, data in messages.items():
                is_me = data.get('name') == user_display_name
                bg_color = "#4facfe" if is_me else "#1a1c24"
                align = "right" if is_me else "left"
                
                st.markdown(f"""
                    <div style='text-align: {align}; margin-bottom: 10px;'>
                        <div style='display: inline-block; background-color: {bg_color}; padding: 8px 15px; border-radius: 15px; color: white;'>
                            <small style='color: #ddd;'>{data.get('name')}</small><br>{data.get('msg')}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # ช่องพิมพ์ข้อความ
        user_msg = st.chat_input("พิมพ์ข้อความของคุณ...")
        if user_msg:
            chat_ref.push({
                'name': user_display_name,
                'msg': user_msg,
                'time': datetime.datetime.now().strftime("%H:%M")
            })
            st.rerun()
    else:
        st.warning("⚠️ กรุณาระบุชื่อผู้ใช้ที่หน้า Experience ก่อนใช้งาน")


   
