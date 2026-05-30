import streamlit as st
import requests
from datetime import datetime

# ตั้งค่าหน้าแอป
st.set_page_config(page_title="Firebase Realtime Chat", page_icon="💬")
st.title("💬 แอปแชตต่อระบบฐานข้อมูลจริง")

# 1. ดึงค่าคอนฟิกจาก Secrets ที่เราทดสอบผ่านแล้ว
firebase_url = st.secrets["firebase"]["firebase_url"]
api_key = st.secrets["firebase"]["api_key"]

# กำหนด Path ใน Firebase สำหรับเก็บข้อความแชต (จะเก็บไว้ในห้องชื่อ room_1)
CHAT_URL = f"{firebase_url}/chat_room_1.json?auth={api_key}"

# ฟังก์ชันสำหรับดึงข้อมูลแชตล่าสุดจาก Firebase
def load_chat_history():
    try:
        response = requests.get(CHAT_URL)
        if response.status_code == 200 and response.json():
            # ดึงข้อมูลออกมา (Firebase จะส่งกลับมาเป็น Dictionary ที่มีคีย์สุ่ม)
            raw_data = response.json()
            # แปลงข้อมูลและเรียงลำดับตามเวลา (Timestamp)
            messages = list(raw_data.values())
            return sorted(messages, key=lambda x: x.get("timestamp", ""))
    except Exception as e:
        st.error(f"โหลดข้อมูลล้มเหลว: {e}")
    return []

# ฟังก์ชันสำหรับส่งข้อความใหม่ไปบันทึกบน Firebase
def send_message_to_firebase(role, content):
    try:
        payload = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        # ใช้ POST เพื่อสร้างโหนดข้อมูลใหม่เพิ่มเข้าไปเรื่อยๆ
        requests.post(CHAT_URL, json=payload)
    except Exception as e:
        st.error(f"ส่งข้อมูลล้มเหลว: {e}")

# --- เริ่มทำงานบนหน้าจอ Streamlit ---

# 2. โหลดประวัติการคุยจาก Firebase จริงๆ มาแสดง
chat_history = load_chat_history()

for message in chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. ช่องรับข้อความแชตจากผู้ใช้
if prompt := st.chat_input("พิมพ์ข้อความส่งไป Firebase..."):
    
    # แสดงฝั่งผู้ใช้ทันทีบนหน้าจอ
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # บันทึกข้อความผู้ใช้ลง Firebase database
    send_message_to_firebase("user", prompt)
    
    # จำลองการตอบกลับจากบอท (บอทระบบ)
    bot_reply = f"ระบบได้รับข้อความ '{prompt}' ของคุณและบันทึกสถิติลงฐานข้อมูลเรียบร้อยแล้ว!"
    
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
        
    # บันทึกข้อความของบอทลง Firebase database เช่นกัน
    send_message_to_firebase("assistant", bot_reply)
    
    # สั่งให้ Streamlit รีเฟรชหน้าจอเพื่ออัปเดตลำดับแชตให้เสร็จสรรพ
    st.rerun()
