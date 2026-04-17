import streamlit as st
import librosa
import soundfile as sf
import io

st.title("🎙️ SYNAPSE: Voice Transform")

# 1. ตั้งค่าตัวเลขให้ "สุด" ไปเลย จะได้เห็นความต่าง
# Rate > 1.0 คือ เร็วขึ้น (Rap)
# Rate < 1.0 คือ ช้าลง (R&B)
rate = st.slider("ปรับความเร็ว (Rate):", 0.5, 2.0, 1.0) 

uploaded_file = st.file_uploader("ส่งไฟล์เสียงมาลองดู")

if uploaded_file:
    # โหลดไฟล์ต้นฉบับ
    y, sr = librosa.load(uploaded_file)
    st.audio(uploaded_file, format='audio/wav', caption="เสียงเดิม")

    if st.button("🚀 สั่งรันแม่พิมพ์"):
        # --- จุดที่ต้องแก้เพื่อให้เปลี่ยนจริง ---
        # เราต้องเอาผลลัพธ์จากการ stretch ไปใส่ในตัวแปรใหม่ (y_changed)
        y_changed = librosa.effects.time_stretch(y, rate=rate) 
        
        # เขียนไฟล์ใหม่ลงใน Buffer เพื่อให้เครื่องเล่นไฟล์ที่ "แก้แล้ว" ไม่ใช่ไฟล์เดิม
        buffer = io.BytesIO()
        sf.write(buffer, y_changed, sr, format='WAV')
        buffer.seek(0) # กลับไปจุดเริ่มไฟล์เพื่อเตรียมเล่น
        
        st.write(f"--- เสียงที่เปลี่ยนไป (Rate: {rate}) ---")
        st.audio(buffer, format='audio/wav') 
        st.success("ตอนนี้เสียงเปลี่ยนแล้วครับ!")
