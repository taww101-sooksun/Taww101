import streamlit as st
import librosa
import soundfile as sf
import numpy as np
import io

st.title("🎙️ SYNAPSE: Full Music Mold")

uploaded_file = st.file_uploader("ส่งไฟล์เสียงมาลองดู", type=['wav', 'mp3', 'm4a'])

if uploaded_file is not None:
    # 1. โหลดเสียงต้นฉบับ
    y, sr = librosa.load(uploaded_file)
    
    # 2. ตั้งค่าแม่พิมพ์ (ความเร็ว และ แนวเพลง)
    genre = st.radio("เลือกแม่พิมพ์แนวเพลง:", ["HipHop (เร็ว/หนัก)", "R&B (ช้า/นุ่ม)"])
    rate = 1.3 if genre == "HipHop" else 0.8  # กำหนดค่าตามมาตรฐานสากลที่ผมรู้

    if st.button("🚀 รันแม่พิมพ์ (รวมดนตรี)"):
        with st.spinner("กำลังประกอบร่างเสียงร้องกับดนตรี..."):
            # --- ก. ปรับความเร็วเสียงร้อง (ที่คุณบอก) ---
            y_stretched = librosa.effects.time_stretch(y, rate=rate)
            
            # --- ข. สร้างเสียงดนตรีจำลอง (กอง + กีต้าร์มาว) ---
            # สร้างจังหวะให้ยาวเท่ากับเสียงที่ปรับแล้ว
            duration = len(y_stretched) / sr
            t = np.linspace(0, duration, len(y_stretched))
            
            # สร้างเสียง 'ตึก-โป๊ะ' (Kick/Snare) แบบคณิตศาสตร์
            kick = np.sign(np.sin(2 * np.pi * 50 * t)) * (np.sin(2 * np.pi * 5 * t) > 0)
            
            # --- ค. รวมร่าง (Mix) ---
            # เอาเสียงร้องที่ปรับความเร็วแล้ว มาผสมกับเสียงดนตรีจำลอง
            final_mix = y_stretched + (kick * 0.1)  # ใส่ดนตรีเบาๆ ไม่ให้กลบเสียงร้อง
            
            # 3. ส่งไฟล์คืน
            buffer = io.BytesIO()
            sf.write(buffer, final_mix, sr, format='WAV')
            buffer.seek(0)
            
            st.subheader(f"ผลลัพธ์แนว {genre}:")
            st.audio(buffer, format='audio/wav')
            st.success("นี่คือแม่พิมพ์ที่สมบูรณ์ครับ มีทั้งความเร็วที่เปลี่ยนและดนตรีประกอบ!")
