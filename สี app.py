import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium

# --- 1. ตั้งค่าหน้าเว็บและการออกแบบ (Premium Dark UI) ---
st.set_page_config(page_title="SYNAPSE - Stable", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stApp { color: #ffffff; }
    .stButton>button {
        width: 100%; border-radius: 20px;
        background: linear-gradient(45deg, #00f2fe 0%, #4facfe 100%);
        color: white; border: none; font-weight: bold;
    }
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

# --- 3. ส่วนหัว ---
st.markdown("<h1 style='text-align: center; color: #4facfe;'>🌐 SYNAPSE</h1>", unsafe_allow_html=True)

location = get_geolocation()

# --- 4. ระบบเช็คแจ้งเตือน (แบบตัวหนังสือเท่านั้น ไม่ใช้เสียงเพื่อป้องกันเพลงดับ) ---
if 'last_chat_count' not in st.session_state:
    st.session_state.last_chat_count = 0

def check_notifications_silent():
    try:
        chats = db.reference('chats').get()
        if chats:
            current_count = len(chats)
            if current_count > st.session_state.last_chat_count:
                if st.session_state.last_chat_count != 0:
                    st.toast("💬 มีข้อความใหม่ในห้องสนทนา!", icon="🔔") # แจ้งเตือนแค่ภาพพอ
                st.session_state.last_chat_count = current_count
    except: pass

check_notifications_silent()

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
    
    # ส่วนของเพลง YouTube (เพิ่ม Parameter เพื่อความเสถียรสูงสุด)
    playlist_id = "PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
    embed_url = f"https://www.youtube.com/embed/videoseries?list={playlist_id}&autoplay=1&loop=1&playlist={playlist_id}&enablejsapi=1"
    
    if user_display_name == "Ta101" and admin_key == "@0970801941":
        st.markdown("<h3 style='color: #00f2fe;'>🎧 Admin Console Active</h3>", unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='color: #888;'>🎧 Streaming Therapy...</h3>", unsafe_allow_html=True)

    st.components.v1.html(
        f'''
        <div style="border-radius: 15px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
            <iframe width="100%" height="250" src="{embed_url}" 
            frameborder="0" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>
        </div>
        ''',
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
                m = folium.Map(location=[valid_users[0]['lat'], valid_users[0]['lon']], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google")
                for u in valid_users: folium.Marker([u['lat'], u['lon']], popup=u['name']).add_to(m)
                st_folium(m, width=None, height=450)

with tab3:
    st.subheader("💬 สนทนาแบบเรียลไทม์")
    with st.form("chat_form", clear_on_submit=True):
        c_msg = st.text_input("พิมพ์ข้อความ...")
        if st.form_submit_button("SEND"):
            if user_display_name and c_msg:
                lon = location['coords']['longitude'] if location else None
                db.reference('chats').push({'name': user_display_name, 'msg': c_msg, 'time': get_time_by_coords(lon).strftime("%H:%M")})
    
    chats = db.reference('chats').order_by_key().limit_to_last(10).get()
    if chats:
        for _, data in reversed(chats.items()):
            st.markdown(f"<div style='background-color: #1a1c24; padding: 10px; border-radius: 10px; margin-bottom: 5px; border-left: 5px solid #4facfe;'><b style='color: #4facfe;'>{data.get('name')}</b>: {data.get('msg')}</div>", unsafe_allow_html=True)
