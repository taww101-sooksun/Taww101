import streamlit as st
import librosa
import soundfile as sf
import numpy as np

st.title("🎙️ SYNAPSE: Dynamic Mode")

file1 = st.file_uploader("ไฟล์ที่ 1 (จังหวะสั้น)", type=['wav', 'mp3'])
file2 = st.file_uploader("ไฟล์ที่ 2 (จังหวะยาว)", type=['wav', 'mp3'])

if file1 and file2:
    st.success("โหลดไฟล์สำเร็จ!")
    
    # เพิ่มปุ่มกด เพื่อไม่ให้รันอัตโนมัติจนเครื่องค้าง
    if st.button("🚀 เริ่มผสมเสียง (ฉบับประหยัด RAM)"):
        with st.spinner("กำลังประมวลผล..."):
            # โหลดแค่ 5 วินาทีแรกมาทดสอบก่อน เพื่อไม่ให้ Server ล่ม
            y1, sr = librosa.load(file1, duration=5.0) 
            y2, _ = librosa.load(file2, duration=5.0)
            
            # Logic การยืดหดแบบง่าย
            min_len = min(len(y1), len(y2))
            combined = (y1[:min_len] * 0.5) + (y2[:min_len] * 0.5)
            
            st.audio(combined, format='audio/wav', sample_rate=sr)
            st.balloons()
