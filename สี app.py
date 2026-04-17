import streamlit as st
import librosa
import numpy as np
import soundfile as sf
import io

st.title("🎙️ SYNAPSE: Dynamic Warp Engine")

uploaded_files = st.file_uploader("อัปโหลด loop_r&b และ tsta", accept_multiple_files=True)

if uploaded_files:
    beat_file = next((f for f in uploaded_files if "loop" in f.name.lower()), None)
    voice_file = next((f for f in uploaded_files if "tsta" in f.name.lower()), None)

    if beat_file and voice_file:
        if st.button("🚀 รันระบบ Warp (ยืด-หดเฉพาะจุดให้เข้าจังหวะ)"):
            with st.spinner("กำลังคำนวณจุดยืดหด..."):
                y_beat, sr = librosa.load(beat_file)
                y_voice, _ = librosa.load(voice_file, sr=sr)

                # 1. หาจังหวะกลอง (Target Beats)
                _, beat_frames = librosa.beat.beat_track(y=y_beat, sr=sr)
                beat_times = librosa.frames_to_time(beat_frames, sr=sr)

                # 2. หาจังหวะที่คนพูด (Voice Onsets)
                onset_frames = librosa.onset.onset_detect(y=y_voice, sr=sr)
                onset_times = librosa.frames_to_time(onset_frames, sr=sr)

                # 3. ระบบ Dynamic Warp (ผสานเสียงไม่ให้ขาด)
                y_final_voice = []
                last_voice_time = 0
                
                for i in range(min(len(onset_times), len(beat_times))):
                    # ช่วงเวลาในเสียงร้องที่ต้องจัดการ
                    current_onset = onset_times[i]
                    next_onset = onset_times[i+1] if i+1 < len(onset_times) else librosa.get_duration(y=y_voice)
                    
                    # ช่วงเวลาในบีทที่ต้องไปให้ถึง
                    target_start = beat_times[i]
                    target_end = beat_times[i+1] if i+1 < len(beat_times) else target_start + (next_onset - current_onset)
                    
                    # คำนวณความเร็วที่ต้องใช้ "เฉพาะในช่วงคำนี้"
                    segment_duration = next_onset - current_onset
                    target_duration = target_end - target_start
                    local_rate = segment_duration / target_duration
                    
                    # ตัดเสียงช่วงนั้นมา Warp
                    voice_segment = y_voice[int(current_onset*sr):int(next_onset*sr)]
                    if len(voice_segment) > 0:
                        warped_segment = librosa.effects.time_stretch(voice_segment, rate=local_rate)
                        y_final_voice.extend(warped_segment)

                y_final_voice = np.array(y_final_voice)

                # 4. รวมเสียง (เสียงร้องที่ Warp แล้ว + บีท)
                # จัดตำแหน่งให้เริ่มพร้อมจังหวะแรก
                start_offset = int(beat_times[0] * sr)
                output = y_beat.copy()
                max_len = min(len(y_final_voice), len(output) - start_offset)
                output[start_offset:start_offset+max_len] += y_final_voice[:max_len] * 0.8

                buffer = io.BytesIO()
                sf.write(buffer, output, sr, format='WAV')
                buffer.seek(0)
                st.audio(buffer, format='audio/wav')
                st.success("Warp เรียบร้อย! เสียงลื่นไหลและตรงจังหวะแล้วครับ")
