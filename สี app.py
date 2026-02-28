import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# --- 1. เชื่อมต่อ (ทำครั้งเดียว) ---
if not firebase_admin._apps:
    fb_dict = dict(st.secrets["firebase"])
    fb_dict["private_key"] = fb_dict["private_key"].replace("\\n", "\n")
    creds = credentials.Certificate(fb_dict)
    firebase_admin.initialize_app(creds, {
        'databaseURL': 'https://notty-101-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

# --- 2. ดึงรายชื่อ Agent มาก่อน (กิน Data น้อยมาก) ---
@st.cache_data(ttl=10) # 💡 สั่งให้จำค่าไว้ 10 วินาที ไม่ต้องดึงใหม่ทุกครั้งที่ขยับเมาส์
def get_agent_list():
    ref = db.reference('users')
    # ดึงแค่ 'คีย์' หรือชื่อ Agent ออกมา ไม่ดึงพิกัดทั้งหมด
    data = ref.get(shallow=True) 
    return list(data.keys()) if data else []

st.title("🛰️ COMMAND CENTER: DATA SAVER MODE")

agents = get_agent_list()

if agents:
    target = st.selectbox("🎯 เลือก Agent ของคุณ:", agents)
    
    # 💡 ดึงข้อมูลเฉพาะของคนที่เราเลือกคนเดียวเท่านั้น! (ลด Data มหาศาล)
    if st.button("📡 ดึงพิกัดสดเดี๋ยวนี้"):
        real_data = db.reference(f'users/{target}').get()
        
        if real_data:
            st.success(f"ดึงข้อมูลของ {target} สำเร็จ!")
            st.json(real_data)
        else:
            st.error("ไม่พบข้อมูลพิกัด")
else:
    st.warning("ไม่มีข้อมูลในระบบ หรือเชื่อมต่อไม่ได้")
