import streamlit as st
import streamlit.components.v1 as components
import requests
import json
from datetime import datetime

# ตั้งค่าหน้าจอแอป SYNAPSE ให้พอดีกับหน้าจอมือถือ
st.set_page_config(page_title="SYNAPSE CHAT & THERAPY", page_icon="🔮", layout="centered")

# --- 1. แสดงผลโลโก้ตัวจริง Logo1.png จาก GitHub ของนาย ---
logo_url = "https://raw.githubusercontent.com/taww101-sooksun/Taww101/main/Logo1.png"
try:
    st.image(logo_url, use_container_width=True)
except:
    st.title("🔮 SYNAPSE SYSTEM")

st.markdown("---")

# คอนฟิกฐานข้อมูล Firebase ของนาย และลิงก์เสียงเรดาร์ดิบจาก GitHub
FIREBASE_DB_URL = "https://sooksun1-default-rtdb.firebaseio.com"
synapse_radar_tone = "https://raw.githubusercontent.com/taww101-sooksun/Taww101/b41c648c082e24be27fed1407735e895ee6a4e43/SYNAPSE%20RADAR.mp3"

# ระบบเลือกชื่อเพื่อแยกบัญชีคนคุย ไม่ให้ข้อมูลมั่วกัน
my_name = st.selectbox("👤 โปรดระบุชื่อของคุณ :", ["นายกานต์", "นายบาส"])
friend_name = "นายบาส" if my_name == "นายกานต์" else "นายกานต์"

# จัดหน้าจอเป็น 2 ฝั่ง ซ้ายเป็นแชต ขวาเป็นเครื่องเล่นเพลง ไม่ต้องพับหน้าจอ
col_left, col_right = st.columns([1, 1])

# ==========================================
# 💬 ฝั่งซ้าย: ระบบห้องแชตสดและส่งพิกัด GPS
# ==========================================
with col_left:
    st.subheader("💬 ห้องแชตคู่สนทนา")
    
    # ดึงข้อมูลแชตล่าสุดจาก Firebase มาแสดงผล
    chat_room_id = f"chat_{min(my_name, friend_name)}_{max(my_name, friend_name)}"
    try:
        chat_response = requests.get(f"{FIREBASE_DB_URL}/chats/{chat_room_id}.json").json()
    except:
        chat_response = None

    # แสดงกล่องข้อความที่คุยกัน
    chat_placeholder = st.empty()
    chat_text = ""
    
    if chat_response:
        for msg_id, msg_data in chat_response.items():
            chat_text += f"**{msg_data['sender']}** ({msg_data['time']}): {msg_data['text']}\n\n"
    else:
        chat_text = "*ยังไม่มีข้อความแชต เริ่มพิมพ์คุยกันได้เลย*"
        
    chat_placeholder.markdown(chat_text)

    # ช่องพิมพ์ส่งข้อความแชต
    user_msg = st.text_input("พิมพ์ข้อความที่นี่...", key="chat_input")
    if st.button("✈️ ส่งข้อความ"):
        if user_msg:
            now = datetime.now().strftime("%H:%M:%S")
            new_msg = {
                "sender": my_name,
                "text": user_msg,
                "time": now
            }
            # ส่งบันทึกลง Firebase
            requests.post(f"{FIREBASE_DB_URL}/chats/{chat_room_id}.json", data=json.dumps(new_msg))
            
            # ยิงสัญญาณแจ้งเตือนไปที่ฝั่งเพื่อนทันที
            alert_data = {"new_message": True, "sender": my_name}
            requests.put(f"{FIREBASE_DB_URL}/users/{friend_name}/chat_alert.json", data=json.dumps(alert_data))
            st.rerun()

    st.markdown("---")
    st.subheader("🛰️ พิกัด GPS ล่าสุด")
    # ปุ่ม
