import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import datetime
import os
from streamlit_js_eval import get_geolocation
import folium
from streamlit_folium import st_folium

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(page_title="SYNAPSE - Fixed", layout="wide")

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
        st.error(f"Firebase Setup Error: {e}")

# ฟังก์ชันคำนวณเวลา
def get_time_by_coords(lon):
    if lon is None: return datetime.datetime.now()
    offset = round(float(lon) / 15)
    return datetime.datetime.utcnow() + datetime.timedelta(hours=offset)

# --- 3. ส่วนหัว ---
col1, col2 = st.columns([1, 5])
with col1:
    if os.path.exists("logo3.jpg"): st.image("logo3.jpg", width=300)
    else: st.write("### 🌐 SYNAPSE")
with col2:
    st.title("SYNAPSE - Music Therapy")

location = get_geolocation()

# --- 4. ระบบแจ้งเตือนแชท ---
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
                    if os.path.exists("notification.mp3"):
                        st.audio("notification.mp3", format="audio/mp3", autoplay=True)
                st.session_state.last_chat_count = current_count
    except: pass

check_notifications()

# --- 5. แท็บการใช้งาน ---
tab1, tab2, tab3 = st.tabs(["🚀 เช็คอิน & ฟังเพลง", "📊 แผนที่", "💬 ห้องสนทนา"])

with tab1:
    user_display_name = st.text_input("ระบุชื่อของคุณ:", placeholder="เช่น Ta101")
    admin_key = st.text_input("รหัสผ่านผู้ดูแล (ถ้ามี):", type="password")

    if st.button("Start Journey"):
        if user_display_name and location and 'coords' in location:
            lat, lon = location['coords']['latitude'], location['coords']['longitude']
            true_time_str = get_time_by_coords(lon).strftime("%H:%M")
            if firebase_admin._apps:
                db.reference(f'users/{user_display_name}').set({'last_seen': true_time_str, 'lat': lat, 'lon': lon})
                st.success(f"เช็คอินสำเร็จ! เวลาพิกัดโลก: {true_time_str}")

    # ส่วนเพลง YouTube
    st.write("---")
    if user_display_name == "Ta101" and admin_key == "@0970801941":
        st.subheader("🎛️ แผงควบคุมดีเจ (Admin Only)")
        playlist_url = "https://www.youtube.com/embed/videoseries?list=PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
        st.components.v1.html(
            f'<iframe width="100%" height="315" src="{playlist_url}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>',
            height=350,
        )
    elif user_display_name != "":
        st.subheader("🎧 เพลงบำบัดสำหรับคุณ")
        playlist_url = "https://www.youtube.com/embed/videoseries?list=PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
        st.components.v1.html(
            f'<iframe width="100%" height="315" src="{playlist_url}" frameborder="0" allowfullscreen></iframe>',
            height=350,
        )

with tab2:
    st.header("📊 แผนที่พิกัดจริง")
    if firebase_admin._apps:
        users_ref = db.reference('users').get()
        if users_ref:
            valid_users = []
            for k, v in users_ref.items():
                if isinstance(v, dict) and 'lat' in v:
                    valid_users.append({'name': k, 'lat': v['lat'], 'lon': v['lon'], 'time': v.get('last_seen', '--:--')})
            if valid_users:
                m = folium.Map(location=[valid_users[0]['lat'], valid_users[0]['lon']], zoom_start=18, tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", attr="Google")
                for u in valid_users:
                    folium.Marker([u['lat'], u['lon']], popup=f"{u['name']} ({u['time']})").add_to(m)
                # แก้ไขตรงนี้ให้ถูกต้องแล้วครับ
                st_folium(m, width=700, height=500)

with tab3:
    st.header("💬 ห้องสนทนา")
    with st.form("chat_form", clear_on_submit=True):
        c_msg = st.text_input("พิมพ์ข้อความ:")
        if st.form_submit_button("ส่ง") and user_display_name and c_msg:
            lon = location['coords']['longitude'] if location else None
            db.reference('chats').push({'name': user_display_name, 'msg': c_msg, 'time': get_time_by_coords(lon).strftime("%H:%M")})
    
    chats = db.reference('chats').order_by_key().limit_to_last(15).get()
    if chats:
        for _, data in reversed(chats.items()):
            st.write(f"**{data.get('name')}** ({data.get('time')}): {data.get('msg')}")
            st.divider()
