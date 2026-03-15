import streamlit as st
import time
from firebase_admin import credentials, db, initialize_app, _apps

# --- 1. SETUP FIREBASE (ปรับปรุงให้รองรับ Service Account เต็มรูปแบบ) ---
if not _apps: # ตรวจสอบว่ายังไม่มีการ Initialize
    try:
        # วิธีที่ชัวร์ที่สุด: ให้คุณเอา JSON Service Account ทั้งหมดใส่ใน st.secrets["firebase_service_account"]
        # หรือถ้าแยกเป็นตัวแปร ให้เขียนแบบนี้ครับ:
        firebase_info = {
            "type": "service_account",
            "project_id": st.secrets["project_id"],
            "private_key_id": st.secrets.get("private_key_id"), # ถ้ามี
            "private_key": st.secrets["private_key"].replace('\\n', '\n'),
            "client_email": st.secrets["client_email"],
            "client_id": st.secrets.get("client_id"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": st.secrets.get("client_x509_cert_url")
        }
        
        cred = credentials.Certificate(firebase_info)
        initialize_app(cred, {
            'databaseURL': "https://notty-101-default-rtdb.firebaseio.com/" 
        })
        st.success("✅ เชื่อมต่อฐานข้อมูลสำเร็จ")
    except Exception as e:
        st.error(f"การเชื่อมต่อ Firebase ผิดพลาด: {e}")

# --- 2. LOGIC แชทส่วนตัว (เพิ่มการดัก Error ถ้า Database ว่างเปล่า) ---
def private_chat_logic(my_name, target_name, p_msg=None):
    try:
        pair = sorted([my_name, target_name])
        room_id = f"priv_{pair[0]}_{pair[1]}"
        ref = db.reference(f'private_rooms/{room_id}')
        
        if p_msg:
            ref.push({
                'name': my_name, 
                'msg': p_msg, 
                'ts': time.time()
            })
        
        raw_p_msgs = ref.get()
        if raw_p_msgs:
            # Firebase คืนค่าเป็น Dict ต้องแปลงเป็น List ก่อนเรียงลำดับ
            if isinstance(raw_p_msgs, dict):
                msgs = list(raw_p_msgs.values())
            else:
                msgs = [m for m in raw_p_msgs if m is not None] # กันค่า null
            return sorted(msgs, key=lambda x: x.get('ts', 0))[-15:]
    except Exception as e:
        st.warning(f"ยังไม่มีข้อความในห้องนี้ หรือเกิดข้อผิดพลาด: {e}")
    return []

# --- 3. UI (เหมือนเดิมแต่ปรับปรุงส่วนแสดงผล) ---
st.title("📍 GPS Real-time & Private Chat")

# ระบบเสียงและ GPS (เหมือนเดิมที่คุณต้องการ)
# ... (ก๊อปส่วน play_audio และ JavaScript GPS จากโค้ดเดิมมาวางตรงนี้ได้เลย) ...

my_name = st.text_input("ชื่อของคุณ", value="User1")
target_name = st.text_input("ชื่อคู่สนทนา", value="User2")

if my_name and target_name:
    messages = private_chat_logic(my_name, target_name)
    
    # แสดงข้อความ
    for m in messages:
        with st.chat_message("user" if m['name'] == my_name else "assistant"):
            st.write(f"**{m['name']}**: {m['msg']}")

    # ส่วนส่งข้อความ
    with st.form("chat_input_form", clear_on_submit=True):
        msg = st.text_input("พิมพ์ข้อความที่นี่...")
        if st.form_submit_button("ส่ง") and msg:
            private_chat_logic(my_name, target_name, p_msg=msg)
            st.rerun()
