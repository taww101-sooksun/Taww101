import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation
import time
import streamlit.components.v1 as components

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
    .my-msg { text-align: right; color: #00ff00; background: rgba(0,255,0,0.1); padding: 8px; border-radius: 8px; margin-bottom: 5px; }
    .other-msg { text-align: left; color: #ffffff; background: rgba(255,255,255,0.1); padding: 8px; border-radius: 8px; margin-bottom: 5px; }
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
            st.error("🔑 ไม่พบข้อมูล Firebase ใน Secrets ของ Streamlit Cloud")
    except Exception as e:
        st.error(f"⚠️ Firebase Error: {e}")

# --- 3. SIDEBAR (MUSIC & PROFILE) ---
with st.sidebar:
    st.title("🛰️ COMMAND PANEL")
    my_id = st.text_input("รหัส (ID):", value="Ta101")
    st.write("---")
    st.subheader("🎵 SYNAPSE PLAYER")
    playlist_id = "PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
    
    # ฝัง YouTube แบบ HTML ดิบ เพื่อให้อยู่ในแอป ไม่เด้งออกไปกวนที่อื่น
    components.html(
        f"""
        <iframe width="100%" height="300" 
        src="https://www.youtube.com/embed/videoseries?list={playlist_id}&rel=0" 
        frameborder="0" allow="autoplay; encrypted-media" allowfullscreen>
        </iframe>
        """,
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
            try:
                db.reference(f'users/{my_id}').update({'lat': lat, 'lon': lon, 'last_update': time.time()})
                st.toast("บันทึกตำแหน่งแล้ว!", icon="✅")
            except:
                st.warning("ระบบฐานข้อมูลยังไม่พร้อมเชื่อมต่อ")
    
    st.subheader("🛰️ STRATEGIC MAP")
    try:
        all_users = db.reference('users').get() or {}
        m = folium.Map(location=[13.75, 100.5], zoom_start=12, tiles="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}", attr="Google")
        for name, info in all_users.items():
            if isinstance(info, dict) and 'lat' in info:
                is_online = (time.time() - info.get('last_update', 0)) < 300
                color = 'green' if is_online else 'red'
                folium.Marker([info['lat'], info['lon']], tooltip=name, icon=folium.Icon(color=color)).add_to(m)
        st_folium(m, width="100%", height=450)
    except:
        st.info("รอการเชื่อมต่อแผนที่และพิกัดเพื่อน...")

# TAB 2: CHAT 2 ROOMS (แก้ให้เรียงเวลา และแชตได้จริง)
with tabs[1]:
    room_choice = st.selectbox("เลือกห้องแชต:", ["🛰️ กองบัญชาการ (Room 1)", "🛠️ หน่วยปฏิบัติการ (Room 2)"])
    room_id = "room_1" if "1" in room_choice else "room_2"
    
    try:
        chat_ref = db.reference(f'chats/{room_id}')
        messages_data = chat_ref.order_by_child('timestamp').limit_to_last(20).get() or {}
        
        with st.container(height=350):
            if messages_data:
                # เรียงข้อความตามเวลาที่ส่งจริง
                sorted_msgs = sorted(messages_data.values(), key=lambda x: x.get('timestamp', 0))
                for msg in sorted_msgs:
                    # แยกสีตัวเรากับเพื่อน
                    if msg.get('user') == my_id:
                        st.markdown(f"<div class='my-msg'><b>{msg.get('user')}</b>: {msg.get('text')}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='other-msg'><b>{msg.get('user')}</b>: {msg.get('text')}</div>", unsafe_allow_html=True)

        # ช่องพิมพ์ข้อความ
        with st.form("send_msg", clear_on_submit=True):
            col1, col2 = st.columns([8, 2])
            with col1:
                msg_text = st.text_input("พิมพ์ข้อความ...", label_visibility="collapsed")
            with col2:
                submitted = st.form_submit_button("ส่งข้อความ 🚀")
                
            if submitted and msg_text:
                chat_ref.push({'user': my_id, 'text': msg_text, 'timestamp': time.time()})
                st.rerun() # รีเฟรชหน้าเพื่อโชว์ข้อความใหม่ทันที
    except Exception as e:
        st.error(f"ระบบแชตยังไม่พร้อม: กรุณาเช็ก Firebase Secrets")

# TAB 3: VIDEO CALL (Whereby) - แก้ให้กล้อง/ไมค์ติดชัวร์ๆ
with tabs[2]:
    st.subheader("📞 DIRECT CALL (Whereby)")
    whereby_url = "https://ta-sooksun.whereby.com/ta0b9934f8-ae2a-4e0f-b513-58a0616fd29a"
    
    # ⚠️ นี่คือคำสั่งของจริงที่อนุญาตให้เปิดกล้องและไมค์ได้ (ต้องใช้ components.html)
    components.html(
        f"""
        <iframe 
            src="{whereby_url}?embed=true&vpa=1&chat=1" 
            allow="camera; microphone; fullscreen; speaker; display-capture" 
            style="width: 100%; height: 600px; border: 2px solid #00ff00; border-radius: 10px;">
        </iframe>
        """,
        height=600
    )
