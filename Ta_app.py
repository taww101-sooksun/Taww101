import streamlit as st
import requests

st.title("🔌 ทดสอบการเชื่อมต่อ Firebase")

# 1. ดึงข้อมูลจาก st.secrets ที่เราตั้งค่าไว้
try:
    firebase_url = st.secrets["firebase"]["firebase_url"]
    api_key = st.secrets["firebase"]["api_key"]
    
    st.write(f"🔄 กำลังพยายามเชื่อมต่อฐานข้อมูล: `{firebase_url}`")
    
    # 2. ยิงคำสั่งไปดึงข้อมูลที่ฐานข้อมูล (ลองดึงที่รูท / หรือโฟลเดอร์ test)
    # เราจะใส่ .json ต่อท้าย URL ตามหลักการของ Firebase REST API
    test_url = f"{firebase_url}/.json"
    
    response = requests.get(test_url)
    
    # 3. ตรวจสอบผลลัพธ์
    if response.status_code == 200:
        st.success("✅ เชื่อมต่อ Firebase สำเร็จ! JSON ของคุณใช้งานได้จริง")
        
        # แสดงข้อมูลที่มีอยู่ในฐานข้อมูลออกมาดู
        data = response.json()
        st.write("ข้อมูลปัจจุบันในฐานข้อมูลของคุณ:")
        st.json(data)
        
    else:
        st.error(f"❌ เชื่อมต่อไม่สำเร็จ (Error Code: {response.status_code})")
        st.write("เหตุผลที่เป็นไปได้: คุณอาจจะยังไม่ได้ตั้งค่า Rules ใน Firebase ให้เป็นสาธารณะ (Public)")

except KeyError:
    st.error("❌ ไม่พบข้อมูลคอนฟิกใน `.streamlit/secrets.toml` กรุณาตรวจสอบชื่อตัวแปร")
except Exception as e:
    st.error(f"❌ เกิดข้อผิดพลาด: {e}")
