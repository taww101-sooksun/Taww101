import streamlit as st
import random

# ตั้งค่าหน้าตาของเว็บแอป
st.set_page_config(page_title="แอปแชตสุดเจ๋ง", page_icon="💬")
st.title("💬 แอปแชตจำลอง (รันได้จริง)")

# 1. ตรวจสอบและสร้างตัวเก็บประวัติการคุยใน Session State (ถ้ายังไม่มีให้สร้างเป็นลิสต์ว่าง)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. แสดงข้อความเก่าทั้งหมดที่เคยคุยกันไว้บนหน้าจอ
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. สร้างช่องรับข้อความแชตจากผู้ใช้ (Chat Input)
if prompt := st.chat_input("พิมพ์ข้อความของคุณที่นี่..."):
    
    # แสดงข้อความที่ผู้ใช้เพิ่งพิมพ์ลงในหน้าจอทันที
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # บันทึกข้อความของผู้ใช้ลงในประวัติ (Session State)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 4. สร้างการตอบกลับจำลองจากบอท (ตรงนี้ถ้าคุณมี API คีย์ของบอทอื่นค่อยเอามาเชื่อมต่อได้)
    # ในตัวอย่างนี้ขอใช้การสุ่มคำตอบแบบฮาๆ เพื่อให้เห็นภาพการทำงานจริงครับ
    bot_responses = [
        f"นายบอกว่า '{prompt}' หรอ? น่าสนใจดีนะ!",
        "อยู่นิ่งๆ ไม่เจ็บตัว... แต่ถ้าคุยกับเราบ่อยๆ อบอุ่นแน่นอน!",
        "รับทราบครับเพื่อน มีอะไรให้ช่วยอีกไหม?",
        "ฮั่นแน่ พิมพ์อะไรมาน่ะ อ่านแล้วยิ้มเลย"
    ]
    response = random.choice(bot_responses)

    # แสดงข้อความตอบกลับของบอทบนหน้าจอ
    with st.chat_message("assistant"):
        st.markdown(response)
        
    # บันทึกข้อความของบอทลงในประวัติ (Session State)
    st.session_state.messages.append({"role": "assistant", "content": response})
