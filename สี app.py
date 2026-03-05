import streamlit as st
import firebase_admin
from firebase_admin import credentials, db, storage
from datetime import datetime
import uuid

# --- 1. INITIALIZE ---
if not st.session_state.get("init"):
    st.set_page_config(page_title="SYNAPSE COMMAND CENTER", layout="wide")
    st.session_state.init = True

def init_firebase():
    if not firebase_admin._apps:
        try:
            fb_creds = dict(st.secrets["firebase_service_account"])
            cred = credentials.Certificate(fb_creds)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app',
                'storageBucket': 'notty-101.appspot.com' # ตรวจสอบชื่อ bucket ดีๆ นะครับ มักจะลงท้ายด้วย .appspot.com
            })
        except Exception as e:
            st.error(f"Firebase Error: {e}")
            return None
    return storage.bucket()

bucket = init_firebase()

# --- 2. AUTHENTICATION (ปรับปรุงใหม่) ---
if not st.session_state.authenticated:
    st.title("🔐 SYNAPSE ACCESS CONTROL")
    with st.form("Login"):
        u_id = st.text_input("User ID").strip()
        u_pw = st.text_input("Password", type="password")
        if st.form_submit_button("UNLOCK"):
            if u_pw == "99999999" and u_id:
                # ตรวจสอบก่อนว่า Firebase พร้อมใช้งานไหม
                try:
                    # ลองเช็คว่าแอปถูก init หรือยัง
                    firebase_admin.get_app() 
                    
                    st.session_state.authenticated = True
                    st.session_state.my_id = u_id
                    db.reference(f'/users/{u_id}').update({'last_seen': datetime.now().timestamp()})
                    st.rerun()
                except ValueError:
                    st.error("❌ ระบบ Firebase ยังไม่ได้เชื่อมต่อ กรุณาเช็ค Secrets Configuration")
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาด: {e}")
    st.stop()



# --- 3. SIDEBAR & USERS ---
with st.sidebar:
    st.title("S Y N A P S E")
    st.success(f"Online: {my_id}")
    
    users_data = db.reference('/users').get()
    friend_list = [u for u in users_data.keys() if u != my_id] if users_data else []
    target_chat = st.selectbox("💬 Select Partner:", ["-- Select --"] + friend_list)
    
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# --- 4. MAIN CHAT INTERFACE ---
if target_chat != "-- Select --":
    st.subheader(f"Chatting with: {target_chat}")
    
    chat_room_id = "_".join(sorted([my_id, target_chat]))
    chat_ref = db.reference(f'/chats/{chat_room_id}')

    # ดึงข้อมูลและเรียงลำดับ (Firebase dict -> sorted list)
    raw_msgs = chat_ref.order_by_child('timestamp').limit_to_last(30).get()
    
    # ส่วนแสดงผลข้อความ
    chat_placeholder = st.container(height=500)
    with chat_placeholder:
        if raw_msgs:
            # สำคัญ: Firebase คืนค่าเป็น Dict ต้องเรียงลำดับด้วย timestamp อีกครั้งเพื่อความชัวร์
            sorted_msgs = sorted(raw_msgs.values(), key=lambda x: x['timestamp'])
            for m in sorted_msgs:
                role = "user" if m['sender'] == my_id else "assistant"
                with st.chat_message(role):
                    st.write(f"**{m['sender']}**")
                    if m.get('text'): st.write(m['text'])
                    if m.get('url'):
                        if m.get('type') == 'image': st.image(m['url'])
                        elif m.get('type') == 'video': st.video(m['url'])
                    st.caption(m.get('time', ''))

    # ส่วนส่งข้อความ
    with st.form("input_form", clear_on_submit=True):
        col_msg, col_file = st.columns([3, 1])
        with col_msg:
            msg_text = st.text_input("Message...", label_visibility="collapsed")
        with col_file:
            uploaded_file = st.file_uploader("Media", type=['jpg','png','mp4'], label_visibility="collapsed")
        
        if st.form_submit_button("SEND 🚀"):
            new_msg = {
                'sender': my_id,
                'timestamp': datetime.now().timestamp(),
                'time': datetime.now().strftime('%H:%M'),
                'type': 'text'
            }
            
            if uploaded_file:
                with st.spinner("Uploading..."):
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
    st.info("👈 เลือกเพื่อนในแถบด้านซ้ายเพื่อเริ่มคุย")
