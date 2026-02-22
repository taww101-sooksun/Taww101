import streamlit as st
import google.generativeai as genai

# --- 1. ตั้งค่าหน้าตาแอป ---
st.set_page_config(page_title="AI Proxy Chat", layout="centered")

# --- 2. ดึงกุญแจลับ ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # ใช้รุ่น 1.5-flash เพื่อไม่ให้แดง 404
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"🚨 กุญแจมีปัญหา: {e}")
    st.stop()

# --- 3. ส่วนหน้าตาแอป (UI) ---
st.title("🤖 AI Chat: สไตล์อยู่นิ่งๆ ไม่เจ็บตัว")
st.write("แอปนี้จะช่วยร่างคำตอบให้คุณเลือก โดยที่คุณไม่ต้องพิมพ์เอง")

st.divider()
friend_input = st.text_input("💬 ข้อความที่ได้รับจากเพื่อน:", placeholder="เช่น... พรุ่งนี้ไปเที่ยวกันไหม?")

if friend_input:
    with st.spinner('AI กำลังคิดคำตอบให้...'):
        try:
            prompt = f"เพื่อนส่งแชตมาว่า: '{friend_input}' ช่วยร่างคำตอบสั้นๆ 3 แบบ: 1.ตกลง 2.ปฏิเสธ 3.กวนๆ (เอาเฉพาะข้อความตอบกลับ)"
            response = model.generate_content(prompt)
            suggestions = response.text.strip().split('\n')
            
            # ลบเลขข้อออกเพื่อให้เหลือแต่ข้อความเพียวๆ
            clean_suggestions = [s.split('. ')[-1] if '. ' in s else s for s in suggestions if s.strip()]

            st.write("---")
            st.subheader("🎯 เลือกคำตอบที่โดนใจ:")
            
            for choice in clean_suggestions[:3]:
                if st.button(choice, use_container_width=True):
                    st.success(f"✅ ส่งแล้ว: {choice}")
                    st.balloons()
        except Exception as e:
            st.error(f"AI Error: {e}")
