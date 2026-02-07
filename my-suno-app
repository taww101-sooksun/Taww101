import streamlit as st
import requests
import time

# ดึงค่าจาก Secrets
API_KEY = st.secrets["APIFRAME_KEY"]
API_URL = st.secrets["API_URL"]

st.title("🎵 Suno AI by Apiframe")

prompt = st.text_area("อธิบายเพลงที่ต้องการ:", placeholder="A cheerful Thai pop song...")

if st.button("สร้างเพลง"):
    headers = {
        "Authorization": API_KEY, # Apiframe มักใช้โทเค็นตรงๆ หรือ Bearer
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": prompt,
        "model": "v3.5", # หรือ v3
        "custom": False
    }

    with st.spinner("กำลังส่งคำขอไปยัง Apiframe..."):
        response = requests.post(API_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            res_data = response.json()
            task_id = res_data.get("task_id")
            st.success(f"รับงานสำเร็จ! Task ID: {task_id}")
            st.info("รอสักครู่ ระบบกำลังเจนนิ่งเพลง... (ต้องใช้เวลา 1-2 นาที)")
            
            # หมายเหตุ: ในแอปจริงคุณต้องเขียนระบบ Loop เพื่อ Get ผลลัพธ์จาก task_id อีกครั้ง
            st.write("ตรวจสอบสถานะเพลงได้ที่หน้า Dashboard ของ Apiframe")
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
