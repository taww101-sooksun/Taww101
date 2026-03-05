import streamlit as st
import requests
from streamlit_js_eval import get_geolocation
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db, storage
import folium
from streamlit_folium import st_folium
import uuid

# --- 1. INITIALIZE (ต้องอยู่บรรทัดแรกสุด) ---
st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")

def init_firebase():
    if not firebase_admin._apps:
        try:
            # ใช้ secrets จาก streamlit
            fb_creds = dict(st.secrets["firebase_service_account"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app',
                'storageBucket': 'notty-101.firebasestorage.app'
            })
        except Exception as e:
            st.error(f"Firebase Connection Error: {e}")
            return None
    return storage.bucket()

bucket = init_firebase()

# --- 2. SECURITY GATE ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='text-align: center;'>🔐 SYNAPSE ACCESS CONTROL</h2>", unsafe_allow_html=True)
    with st.form("Login"):
        u_id = st.text_input("Enter your ID / ใส่ ID")
        u_pw = st.text_input("Password", type="password")
        if st.form_submit_button("UNLOCK SYSTEM"):
            if u_pw == "99999999" and u_id: 
                st.session_state.authenticated = True
                st.session_state.my_id = u_id.strip()
                # บันทึกสถานะ Online ใน DB จริงๆ
                db.reference(f'/users/{u_id.strip()}').update({'last_seen': datetime.now().timestamp()})
                st.rerun()
    st.stop()

my_id = st.session_state.my_id

# --- 3. CUSTOM STYLE ---
st.markdown("""
    <style>
    .stApp { background: #0f0c29; color: white; }
    .chat-container { 
        background: rgba(255, 255, 255, 0.05); 
        padding: 20px; 
        border-radius: 15px; 
        height: 500px; 
        overflow-y: auto;
        display: flex;
        flex-direction: column;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("S Y N A P S E")
    st.write(f"🟢 **Online:** {my_id}")
    
    # ดึงรายชื่อเพื่อนที่เคยเข้าระบบ
    users_ref = db.reference('/users').get()
    friend_list = [u for u in users_ref.keys() if u != my_id] if users_ref else []
    target_chat = st.selectbox("💬 เลือกเพื่อนสนทนา:", ["-- เลือกเพื่อน --"] + friend_list)
    
    st.divider()
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# --- 5. CHAT & SATELLITE ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📍 Satellite Tracking")
    location = get_geolocation()
    if location:
        coords = location.get('coords', {})
        lat, lon = coords.get('latitude'), coords.get('longitude')
        if lat and lon:
            m = folium.Map(location=[lat, lon], zoom_start=16, tiles='CartoDB dark_matter')
            folium.Marker([lat, lon], popup="Your Location").add_to(m)
            st_folium(m, width=350, height=300, key="map")

with col2:
    if target_chat != "-- เลือกเพื่อน --":
        st.subheader(f"Talking to: {target_chat}")
        
        chat_room_id = "_".join(sorted([my_id, target_chat]))
        chat_ref = db.reference(f'/chats/{chat_room_id}')

        # ดึงข้อความ 20 อันล่าสุด (ดึงจาก Server โดยตรงเพื่อความเร็ว)
        msgs_data = chat_ref.order_by_child('timestamp').limit_to_last(20).get()
        
        # แสดงผล
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        if msgs_data:
            for key in msgs_data:
                m = msgs_data[key]
                is_me = m['sender'] == my_id
                with st.chat_message("user" if is_me else "assistant"):
                    st.write(f"**{m['sender']}**")
                    if m.get('text'): st.write(m['text'])
                    if m.get('type') in ['image', 'video']:
                        if m.get('type') == 'image': st.image(m['url'])
                        else: st.video(m['url'])
                    st.caption(m.get('time', ''))
        
        # ฟอร์มส่งข้อความ
        with st.form("chat_form", clear_on_submit=True):
            msg_text = st.text_input("พิมพ์ข้อความ...")
            uploaded_file = st.file_uploader("แนบไฟล์ (Image/Video)", type=['jpg','png','mp4'])
            submit = st.form_submit_button("SEND 🚀")
            
            if submit:
                new_msg = {
                    'sender': my_id,
                    'timestamp': datetime.now().timestamp(),
                    'time': datetime.now().strftime('%H:%M'),
                    'type': 'text'
                }
                
                if uploaded_file:
                    file_id = f"{uuid.uuid4()}_{uploaded_file.name}"
                    blob = bucket.blob(f"chat_media/{file_id}")
                    blob.upload_from_file(uploaded_file, content_type=uploaded_file.type)
                    blob.make_public()
                    new_msg['url'] = blob.public_url
                    new_msg['type'] = 'image' if 'image' in uploaded_file.type else 'video'
                
                if msg_text:
                    new_msg['text'] = msg_text
                
                if msg_text or uploaded_file:
                    chat_ref.push(new_msg)
                    st.rerun()
    else:
        st.info("กรุณาเลือกเพื่อนเพื่อเริ่มการสนทนา")

