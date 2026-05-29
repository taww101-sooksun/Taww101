import streamlit as st
import requests  # ใช้สำหรับยิงอินเทอร์เน็ตไปหา AI ข้างนอก

# 1. สร้างช่องให้เพื่อนพิมพ์สั่งเพลงบนหน้าจอ Streamlit
user_prompt = st.text_input("อยากได้เพลงแนวไหน สั่งมาเลยเพื่อน:", "เพลงแร็ปเดือดๆ สโลแกน อยู่นิ่งๆไม่เจ็บตัว")

if st.button("🚀 สั่ง AI เริ่มแต่งเพลง"):
    with st.spinner("AI กำลังแต่งเนื้อร้องและทำนองตามสั่ง ใจเย็นๆ นะเพื่อน..."):
        
        # 2. ส่งคำสั่งไปหาเซิร์ฟเวอร์ AI ข้างนอก (สมมติว่าใช้บริการยี่ห้อหนึ่ง)
        api_url = "https://api.aimusicgenerator.com/v1/generate"
        headers = {"Authorization": "Bearer KEY_ลับ_ของเรา"}
        payload = {"prompt": user_prompt, "style": "cyberpunk"}
        
        response = requests.post(api_url, json=payload, headers=headers)
        
        # 3. เมื่อ AI แต่งเสร็จ มันจะส่งลิงก์ไฟล์เพลงกลับมา
        if response.status_code == 200:
            result = response.json()
            audio_url = result["audio_url"] # ได้ลิงก์ไฟล์เพลงมาแล้ว!
            
            # 4. โค้ด Python สั่งให้เอาลิงก์เพลงนี้ ส่งเข้าไปเปิดในเครื่องเล่นบนหน้าจอทันที
            st.success("แต่งเพลงเสร็จแล้ว! กดฟังได้เลยด้านล่าง")
            
            # ส่งค่าไปให้เครื่องเล่นรัน (อันนี้คือคำสั่งเล่นเสียงพื้นฐานของ Streamlit)
            st.audio(audio_url) 
        else:
            st.error("เกิดข้อผิดพลาดในการเชื่อมต่อกับ AI แต่งเพลง")
