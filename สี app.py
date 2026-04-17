import streamlit as st
import librosa
import soundfile as sf
import io
import numpy as np

st.title("🎙️ SYNAPSE: Precision R&B Mold")

# ส่วนรับไฟล์ (ให้คุณต๊ะอัปโหลดทั้ง 2 ไฟล์พร้อมกันได้เลย)
uploaded_files = st.file_uploader("อัปโหลดไฟล์ loop_r&b และ tsta เข้ามาครับ", accept_multiple_files=True)

if uploaded_files:
    beat_data = None
    voice_data = None
    sr_final = 22050

    # ระบบคัดแยกไฟล์อัตโนมัติ
    for file in uploaded_files:
        if "loop_r&b" in file.name.lower():
            beat_data, sr_final = librosa.load(file, sr=None)
            st.success(f"เจอแม่พิมพ์แล้ว: {file.name} (92 BPM)")
        elif "tsta" in file.name.lower():
            voice_data, _ = librosa.load(file, sr=sr_final)
            st.success(f"เจอวัตถุดิบเสียงแล้ว: {file.name}")

    if beat_data is not None and voice_data is not None:
        if st.button("🚀 รันการรวมร่าง (Sync 92 BPM)"):
            with st.spinner("กำลังล็อคเสียง tsta ให้เข้ากับจังหวะ R&B..."):
                # 1. คำนวณความยาว
                dur_beat = len(beat_data) / sr_final
                dur_voice = len(voice_data) / sr_final
                
                # 2. บังคับยืดหด (The Math) 
                # บีบเสียง tsta ให้ยาวเท่ากับบีท 92 BPM เป๊ะๆ
                sync_rate = dur_voice / dur_beat
                voice_synced = librosa.effects.time_stretch(voice_data, rate=sync_rate)
                
                # 3. รวมเสียง (Mixing)
                # ตัดให้เท่ากันเพื่อความชัวร์
                length = min(len(beat_data), len(voice_synced))
                combined = beat_data[:length] + (voice_synced[:length] * 0.8) # ปรับเสียงร้องให้เบากว่าบีทนิดหน่อยเพื่อให้เนียน
                
                # 4. ส่งออกไฟล์ที่แก้แล้ว
                buffer = io.BytesIO()
                sf.write(buffer, combined, sr_final, format='WAV')
                buffer.seek(0)
                
                st.subheader("🎵 ผลลัพธ์ที่รวมร่างแล้ว:")
                st.audio(buffer, format='audio/wav')
                st.balloons()
