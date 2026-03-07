import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import time

# --- 1. SETTING & STYLE (Dark Mode Green Glow) ---
st.set_page_config(page_title="SYNAPSE COMMAND", layout="wide", page_icon="🛰️")

st.markdown("""
    <style>
    .stApp { background: #0e1117; color: #00ff00; }
    div[data-testid="stVerticalBlock"] > div {
        background: rgba(0, 50, 0, 0.2);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #00ff00;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FIREBASE CONNECTION ---
if not firebase_admin._apps:
    try:
        if "firebase" in st.secrets:
            fb_dict = dict(st.secrets["firebase"])
            fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
            creds = credentials.Certificate(fb_dict)
            firebase_admin.initialize_app(creds, {
                'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
            })
        else:
            st.error("🔑 ไม่พบข้อมูล Firebase ใน Secrets")
    except Exception as e:
        st.error(f"⚠️ Firebase Error: {e}")

# --- 3. SIDEBAR (MUSIC & PROFILE) ---
with st.sidebar:
    st.title("🛰️ COMMAND PANEL")
    my_id = st.text_input("รหัส (ID):", value="Ta101")
    st.write("---")
    st.subheader("🎵 SYNAPSE PLAYER")
    # เพลย์ลิสต์ R&B/Hip Hop ของคุณ
    playlist_id = "PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
    st.components.v1.iframe(
        src=f"https://www.youtube.com/embed/videoseries?list={playlist_id}",
        height=300
    )
    st.caption("🎧 'อยู่นิ่งๆ ไม่เจ็บตัว' | BY Ta101")

# --- 4. HEADER ---
st.title("SYNAPSE COMMAND CENTER")

# --- 5. CORE SYSTEM (Tabs) ---
tabs = st.tabs(["🚀 RADAR & GPS", "💬 CHAT ROOMS", "📞 TELE-CALL"])

# TAB 1: GPS & RADAR
with tabs[0]:
    loc = get_geolocation()
    if loc:
        lat, lon = loc['coords']['latitude'], loc['coords']['longitude']
        st.success(f"📍 พิกัดปัจจุบัน: {lat}, {lon}")
        if st.button("🛰️ อัปเดตตำแหน่งลงฐานข้อมูล"):
            db.reference(f'users/{my_id}').update({'lat': lat, 'lon': lon, 'last_update': time.time()})
            st.toast("บันทึกตำแหน่งแล้ว!", icon="✅")
    
    # Map Display
    st.subheader("🛰️ STRATEGIC MAP")
    all_users = db.reference('users').get() or {}
    m = folium.Map(location=[13.75, 100.5], zoom_start=12, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google")
    for name, info in all_users.items():
        if isinstance(info, dict) and 'lat' in info:
            is_online = (time.time() - info.get('last_update', 0)) < 300
            color = 'green' if is_online else 'red'
            folium.Marker([info['lat'], info['lon']], tooltip=name, icon=folium.Icon(color=color)).add_to(m)
    st_folium(m, width="100%", height=450)

# TAB 2: CHAT 2 ROOMS
with tabs[1]:
    room_choice = st.selectbox("เลือกห้องแชต:", ["🛰️ กองบัญชาการ (Room 1)", "🛠️ หน่วยปฏิบัติการ (Room 2)"])
    room_id = "room_1" if "1" in room_choice else "room_2"
    
    chat_ref = db.reference(f'chats/{room_id}')
    messages = chat_ref.order_by_child('timestamp').limit_to_last(15).get() or {}

    with st.container(height=300):
        for msg_id, data in messages.items():
            st.markdown(f"**{data['user']}**: {data['text']}")

    with st.form("send_msg", clear_on_submit=True):
        msg_text = st.text_input("พิมพ์ข้อความ...")
        if st.form_submit_button("ส่ง") and msg_text:
            chat_ref.push({'user': my_id, 'text': msg_text, 'timestamp': time.time()})
            st.rerun()

# TAB 3: VIDEO CALL (Whereby)
with tabs[2]:
    st.subheader("📞 DIRECT CALL (Whereby)")
    whereby_url = "https://ta-sooksun.whereby.com/ta0b9934f8-ae2a-4e0f-b513-58a0616fd29a"
    # เพิ่ม allow เพื่อให้เบราว์เซอร์ยอมใช้กล้อง/ไมค์
    st.components.v1.iframe(
        src=f"{whereby_url}?embed&vpa=1&chat=1",
        height=600,
        allow="camera; microphone; fullscreen; speaker; display-capture"
    )
