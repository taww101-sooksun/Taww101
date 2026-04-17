import streamlit as st
import librosa
import numpy as np
import soundfile as sf
import io

st.title("🎙️ SYNAPSE: Intelligent Beat Match")

uploaded_files = st.file_uploader("อัปโหลด loop_r&b และ tsta", accept_multiple_files=True)

if uploaded_files:
    beat_file = next((f for f in uploaded_files if "loop" in f.name.lower()), None)
    voice_file = next((f for f in uploaded_files if "tsta" in f.name.lower()), None)

    if beat_file and voice_file:
        if st.button("🚀 รันระบบล็อคเป้าจังหวะ (Precision Sync)"):
            with st.spinner("กำลังวิเคราะห์จังหวะบีท..."):
                # 1. โหลดไฟล์
                y_beat, sr = librosa.load(beat_file)
                y_voice, _ = librosa.load(voice_file, sr=sr)

                # 2. ค้นหาจังหวะในดนตรี (Beat Tracking)
                # โค้ดจะ "ฟัง" หาเสียงกลอง 92 BPM
                tempo, beat_frames = librosa.beat.beat_track(y=y_beat, sr=sr)
                beat_times = librosa.frames_to_time(beat_frames, sr=sr)

                # 3. จัดระเบียบเสียงผู้ใช้ให้ลงล็อค
                # เราจะบังคับให้เสียงร้อง 'เริ่มต้น' ที่จังหวะแรกของดนตรีเป๊ะๆ
                first_beat_time = beat_times[0]
                first_beat_sample = int(first_beat_time * sr)

                # สร้างอาเรย์ใหม่ที่ขยับเสียงร้องไปเริ่มที่จังหวะแรก
                voice_aligned = np.zeros_like(y_beat)
                
                # ตัด/แปะ เสียงร้องลงในจุดที่จังหวะเริ่ม
                v_len = min(len(y_voice), len(y_beat) - first_beat_sample)
                voice_aligned[first_beat_sample : first_beat_sample + v_len] = y_voice[:v_len]

                # 4. รวมเสียง
                combined = y_beat + (voice_aligned * 0.7)

                # ส่งผลลัพธ์
                buffer = io.BytesIO()
                sf.write(buffer, combined, sr, format='WAV')
                buffer.seek(0)
                
                st.audio(buffer, format='audio/wav')
                st.success(f"ตรวจพบ Tempo: {tempo:.2f} BPM และล็อคจังหวะแรกให้แล้วครับ!")
