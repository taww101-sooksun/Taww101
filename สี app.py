import streamlit as st
import librosa
import numpy as np
import soundfile as sf
import io

st.title("🎙️ SYNAPSE: Final Precision Sync")

uploaded_files = st.file_uploader("ส่ง loop_r&b และ tsta มาครับ", accept_multiple_files=True)

if uploaded_files:
    beat_file = next((f for f in uploaded_files if "loop" in f.name.lower()), None)
    voice_file = next((f for f in uploaded_files if "tsta" in f.name.lower()), None)

    if beat_file and voice_file:
        if st.button("🚀 รันระบบ Sync (แก้ไข Error)"):
            try:
                # 1. โหลดไฟล์ (ใช้ sr=None เพื่อเอาค่าจริง)
                y_beat, sr = librosa.load(beat_file, sr=22050)
                y_voice, _ = librosa.load(voice_file, sr=22050)

                # 2. ตัดหัวเงียบของเสียงคน
                y_voice_trim, _ = librosa.effects.trim(y_voice)

                # 3. คำนวณความยาวบีท 1 ห้อง (ของ 92 BPM)
                # เพลง 92 BPM หนึ่งห้อง (4 จังหวะ) จะยาวประมาณ 2.6 วินาที
                # เราจะบีบเสียงคนให้ยาวเท่ากับ 1 ห้องของบีทพอดี
                target_len = len(y_beat) 
                current_len = len(y_voice_trim)
                
                # บังคับยืดหดให้เท่ากันเป๊ะก่อนผสม
                rate = current_len / target_len
                y_voice_final = librosa.effects.time_stretch(y_voice_trim, rate=rate)

                # 4. รวมเสียง (Mix)
                # ตัดให้เท่ากันเพื่อป้องกัน Error
                min_len = min(len(y_beat), len(y_voice_final))
                combined = y_beat[:min_len] + (y_voice_final[:min_len] * 0.8)

                # 5. ส่งผลลัพธ์
                buffer = io.BytesIO()
                sf.write(buffer, combined, sr, format='WAV')
                buffer.seek(0)
                
                st.audio(buffer, format='audio/wav')
                st.success("ล็อคจังหวะเรียบร้อย!") # ตัด f-string ซับซ้อนออกเพื่อกัน Error
                
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {str(e)}")
