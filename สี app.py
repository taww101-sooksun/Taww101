import streamlit as st
import librosa
import numpy as np
import soundfile as sf
import io

st.title("🎙️ SYNAPSE: Perfect Hard-Sync")

uploaded_files = st.file_uploader("อัปโหลด loop_r&b และ tsta", accept_multiple_files=True)

if uploaded_files:
    beat_file = next((f for f in uploaded_files if "loop" in f.name.lower()), None)
    voice_file = next((f for f in uploaded_files if "tsta" in f.name.lower()), None)

    if beat_file and voice_file:
        if st.button("🚀 รันระบบ Hard-Sync (ล็อคจังหวะตกหน้า)"):
            with st.spinner("กำลังจูนเสียงให้ตรงจังหวะกลอง..."):
                y_beat, sr = librosa.load(beat_file)
                y_voice, _ = librosa.load(voice_file, sr=sr)

                # --- 1. ตัดส่วนเงียบ (Silence) ของเสียงคนออกให้เหลือแต่ 'เนื้อเสียง' ---
                # เพื่อให้เรารู้ว่า 'คำแรก' เริ่มต้นจริงๆ ที่ตรงไหน
                y_voice_trim, _ = librosa.effects.trim(y_voice, top_db=20)

                # --- 2. หาจังหวะกลองแรกในเพลง (First Downbeat) ---
                tempo, beat_frames = librosa.beat.beat_track(y=y_beat, sr=sr)
                beat_times = librosa.frames_to_time(beat_frames, sr=sr)
                first_beat_sample = int(beat_times[0] * sr)

                # --- 3. วางเสียงลงไปในแม่พิมพ์ ---
                # สร้างพื้นที่ว่างเท่ากับความยาวดนตรี
                output_voice = np.zeros_like(y_beat)
                
                # เอาเสียงร้องที่ตัดหัวเงียบออกแล้ว มาวางเริ่มที่ 'จังหวะกลองแรก' พอดีเป๊ะ
                v_len = min(len(y_voice_trim), len(output_voice) - first_beat_sample)
                output_voice[first_beat_sample : first_beat_sample + v_len] = y_voice_trim[:v_len]

                # --- 4. รวมเสียง (เสียงร้องที่ล็อคเป้าแล้ว + บีท) ---
                combined = y_beat + (output_voice * 0.9)

                buffer = io.BytesIO()
                sf.write(buffer, combined, sr, format='WAV')
                buffer.seek(0)
                st.audio(buffer, format='audio/wav')
                st.success(f"ล็อคหัวเสียงให้ตรงกับจังหวะกลองที่ {tempo:.2f} BPM แล้วครับ!")
