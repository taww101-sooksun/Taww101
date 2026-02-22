import streamlit as st
import google.generativeai as genai

# ส่วนการตั้งค่า
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    # --- วิธีแก้จุดตาย: ลองใช้ชื่อรุ่นที่ชัวร์ที่สุด ---
    # ถ้าอันแรกไม่ได้ ให้ลองอันที่สองครับ
    model = genai.GenerativeModel('gemini-1.5-flash-latest') 
    
except Exception as e:
    st.error(f"ตรวจพบข้อผิดพลาด: {e}")
    st.stop()

# --- เพิ่มปุ่มพิเศษเพื่อเช็กว่าเราใช้รุ่นไหนได้บ้าง (ป้องกันการหลอก) ---
if st.button("เช็กชื่อรุ่นที่ใช้ได้จริง"):
    models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    st.write("กุญแจของคุณใช้รุ่นเหล่านี้ได้:")
    st.write(models)
