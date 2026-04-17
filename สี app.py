import streamlit as st
import librosa
import numpy as np
import soundfile as sf
import io

st.title("🎙️ SYNAPSE: The DNA Quantizer")

uploaded_files = st.file_uploader("อัปโหลดไฟล์ของคุณเข้ามาครับ", accept_multiple_files=True)

if uploaded_files:
    beat_file = next((f for f in uploaded_files if "loop" in f.name.lower()), None)
    voice_file = next((f for f in uploaded_files if "tsta" in f.name.lower()), None)

    if beat_file and voice_file:
        if st.button("🚀 รันระบบ Quantize (ผ่าตัดจังหวะคำ)"):
            with st.spinner("กำลังซิงค์พยางค์คำพูดให้ลงล็อค 92 BPM..."):
                # 1. โหลดไฟล์
                y_beat, sr = librosa.load(beat_file)
                y_voice, _ = librosa.load(voice_file, sr=sr)

                # 2. หาจังหวะกลองในเพลง (Beats)
                tempo, beat_frames = librosa.beat.beat_track(y=y_beat, sr=sr)
                beat_times = librosa.frames_to_time(beat_frames, sr=sr)

                # 3. หาจุดที่คนเริ่มพูดแต่ละคำ (Onsets)
                onset_frames = librosa.onset.onset_detect(y=y_voice, sr=sr)
                onset_times = librosa.frames_to_time(onset_frames, sr=sr)

                # 4. การ "ผ่าตัด" (Phase Vocoding / Time Stretching per Segment)
                # เราจะสร้างเสียงใหม่ที่ขยับทุกคำพูดให้ตรงกับจังหวะกลองที่ใกล้ที่สุด
                y_synced = np.zeros_like(y_beat)
                
                # ลูปเพื่อดึงแต่ละคำที่ตรวจเจอ ไปแปะไว้ที่จังหวะกลอง
                for i in range(min(len(onset_times), len(beat_times))):
                    start_sample_voice = int(onset_times[i] * sr)
                    start_sample_beat = int(beat_times[i] * sr)
                    
                    # ตัดคำพูดมา 1 ช่วง (ประมาณ 0.5 วินาที หรือถึงคำถัดไป)
                    end_sample_voice = int(onset_times[i+1] * sr) if i+1 < len(onset_times) else len(y_voice)
                    word_segment = y_voice[start_sample_voice:end_sample_voice]
                    
                    # วางคำพูดลงในจุดจังหวะดนตรีเป๊ะๆ
                    if start_sample_beat + len(word_segment) < len(y_synced):
                        y_synced[start_sample_beat : start_sample_beat + len(word_segment)] += word_segment

                # 5. รวมเสียง (เสียงร้องที่ถูกจัดระเบียบใหม่ + บีทเดิม)
                combined = y_beat + (y_synced * 0.7)

                buffer = io.BytesIO()
                sf.write(buffer, combined, sr, format='WAV')
                buffer.seek(0)
                
                st.audio(buffer, format='audio/wav')
                st.success(f"ทำการ Quantize คำพูดให้ตรงกับ {tempo:.2f} BPM เรียบร้อย!")
