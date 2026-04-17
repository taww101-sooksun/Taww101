import streamlit as st
import librosa
import soundfile as sf
import io

st.title("🎙️ SYNAPSE: Voice Transform")

# 1. ให้ผู้ใช้เลือกไฟล์ก่อน
uploaded_file = st.file_uploader("ส่งไฟล์เสียงมาลองดู", type=['wav', 'mp3', 'm4a'])

# 2. เช็คว่ามีไฟล์ถูกอัปโหลดขึ้นมาหรือยัง (ป้องกัน Error บรรทัดที่ 18)
if uploaded_file is not None:
    
    # แสดงเสียงต้นฉบับ (ย้ายมาไว้ใน if เพื่อให้แน่ใจว่ามีไฟล์แน่ๆ)
    st.audio(uploaded_file, format='audio/wav')
    st.info("ไฟล์พร้อมแล้ว กดปุ่มรันแม่พิมพ์ได้เลย")

    # ตั้งค่า Rate
    rate = st.slider("ปรับความเร็ว (Rate):", 0.5, 2.0, 1.0) 

    if st.button("🚀 สั่งรันแม่พิมพ์"):
        with st.spinner("กำลังประมวลผล..."):
            try:
                # อ่านไฟล์จาก Memory (ต้องใช้ BytesIO เพื่อความชัวร์)
                data, sr = librosa.load(uploaded_file)
                
                # --- จุดสั่งเปลี่ยนเสียงตามแม่พิมพ์ ---
                y_changed = librosa.effects.time_stretch(data, rate=rate) 
                
                # เขียนลง Buffer ใหม่
                buffer = io.BytesIO()
                sf.write(buffer, y_changed, sr, format='WAV')
                buffer.seek(0)
                
                st.write(f"--- ผลลัพธ์ (ความเร็ว {rate}x) ---")
                st.audio(buffer, format='audio/wav')
                st.success("เปลี่ยนเสียงเรียบร้อย!")
                
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการแปลงเสียง: {e}")
else:
    st.warning("กรุณาอัปโหลดไฟล์เสียงก่อนครับ")
