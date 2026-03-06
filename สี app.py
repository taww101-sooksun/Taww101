import streamlit as st
import numpy as np
import scipy.io.wavfile as wavfile
import io

# --- เครื่องยนต์สร้างเสียง (ตัวเดิมที่พี่ชอบ แต่ทำให้เสถียรขึ้น) ---
def generate_vocal_note(freq, duration, sr=44100):
    t = np.linspace(0, duration, int(sr * duration))
    vibrato_hz = 6.0
    vibrato = 1 + 0.02 * np.sin(2 * np.pi * vibrato_hz * t)
    f0 = freq * vibrato
    
    phase = np.cumsum(f0) / sr
    # สร้างเสียงที่มี Harmonic (เนื้อเสียงสระอา)
    vocal_out = np.sin(2 * np.pi * phase) + 0.5 * np.sin(4 * np.pi * phase) + 0.25 * np.sin(6 * np.pi * phase)
    
    # Fade in/out กันเสียงกึก
    envelope = np.ones_like(t)
    fade = min(int(sr * 0.05), len(t)//2) 
    envelope[:fade] = np.linspace(0, 1, fade)
    envelope[-fade:] = np.linspace(1, 0, fade)
    
    return (vocal_out * envelope * 0.5 * 32767).astype(np.int16)

# --- ข้อมูลตัวโน้ต 12 คีย์ (อิงตามหลักความจริง) ---
NOTES = {
    "C": 261.63, "C#": 277.18, "D": 293.66, "D#": 311.13, 
    "E": 329.63, "F": 349.23, "F#": 369.99, "G": 392.00, 
    "G#": 415.30, "A": 440.00, "A#": 466.16, "B": 493.88
}

# --- หน้าแอป ---
st.set_page_config(layout="wide")
st.title("🎹 Synapse Sound Bank (12 Keys x 4 Timing)")
st.write(f"สร้างเสียงอัตโนมัติ 48 รูปแบบ: จังหวะ 4, 8, 16, 32 | สโลแกน: **อยู่นิ่งๆ ไม่เจ็บตัว**")

# เลือกจังหวะ
timing = st.select_slider("เลือกความยาว (Beat/Timing):", options=[4, 8, 16, 32])
# แปลงจังหวะเป็นวินาที (สมมติ 120 BPM: 4 beats = 2 sec)
duration = timing / 2 

st.subheader(f"🎶 กำลังเล่นที่ความยาว: {timing} จังหวะ ({duration} วินาที)")

# สร้างปุ่ม 12 คีย์
cols = st.columns(4) # แบ่งเป็น 4 คอลัมน์ แถวละ 3 ปุ่ม
note_names = list(NOTES.keys())

for i, note in enumerate(note_names):
    with cols[i % 4]:
        if st.button(f"🎵 Key {note}", use_container_width=True):
            # คำนวณความถี่แบบ 432Hz ตามที่พี่ตั้งไว้
            freq = NOTES[note] * (432/440)
            audio_data = generate_vocal_note(freq, duration)
            
            # ส่งออกเป็นไฟล์เสียงเล่นทันที
            buf = io.BytesIO()
            wavfile.write(buf, 44100, audio_data)
            st.audio(buf)
            st.caption(f"{note} ({freq:.2f} Hz)")

st.divider()
st.write("📌 **วิธีใช้:** เลือกจังหวะด้านบน แล้วกดที่คีย์เพื่อฟังเสียงร้องสังเคราะห์ครับ")
