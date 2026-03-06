import streamlit as st
import numpy as np
import scipy.io.wavfile as wavfile
import io

# --- ส่วนของเครื่องยนต์ (Engine ของพี่) ---
class SynapseSingingEngine:
    def __init__(self, sr=44100):
        self.sr = sr

    def generate_vocal_tone(self, freq, duration, vibrato_hz, transition_ms):
        t = np.linspace(0, duration, int(self.sr * duration))
        # มิติความสมจริง: ลูกคอ
        vibrato = 1 + 0.02 * np.sin(2 * np.pi * vibrato_hz * t)
        f0 = freq * vibrato
        
        # สร้างเสียง Harmonic (เนื้อเสียง)
        phase = np.cumsum(f0) / self.sr
        glottal_source = np.sin(2 * np.pi * phase)
        vocal_out = glottal_source + 0.5 * np.sin(4 * np.pi * phase) + 0.25 * np.sin(6 * np.pi * phase)
        
        # ปรับความดังเบา (Envelope)
        envelope = np.ones_like(t)
        fade_samples = int(self.sr * (transition_ms / 1000))
        if len(t) > fade_samples * 2:
            envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
            envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        
        return vocal_out * envelope

# --- ส่วนของหน้าแอป (UI) ---
st.set_page_config(page_title="Synapse Vocal Engine", page_icon="🎤")
st.title("🎤 Synapse Vocal Engine")
st.write("เปลี่ยนตัวเลขให้เป็นเสียงร้อง (สระ 'อา')")

# แผงควบคุม (Dashboard)
with st.sidebar:
    st.header("⚙️ ตั้งค่าเสียง")
    freq_input = st.slider("ความถี่ (Hz) - โน้ตเพลง", 100, 1000, 261)
    duration_input = st.slider("ความยาว (วินาที)", 0.5, 5.0, 2.0)
    vibrato_input = st.slider("ลูกคอ (Hz)", 0.0, 10.0, 6.0)
    tuning_432 = st.checkbox("ใช้ระบบ 432Hz (Pure Truth)", value=True)

# คำนวณความถี่จริง
final_freq = freq_input * (432/440) if tuning_432 else freq_input

# ปุ่มกดร้องเพลง
if st.button("🔴 กดเพื่อให้แปร้องเพลง (Generate Audio)"):
    engine = SynapseSingingEngine()
    
    with st.spinner('กำลังวอร์มเสียง...'):
        vocal_wav = engine.generate_vocal_tone(
            freq=final_freq,
            duration=duration_input,
            vibrato_hz=vibrato_input,
            transition_ms=150
        )
        
        # แปลงเป็นไฟล์ในหน่วยความจำ (RAM) ไม่ต้องเซฟลงเครื่องจริง
        virtual_file = io.BytesIO()
        wavfile.write(virtual_file, 44100, (vocal_wav * 32767).astype(np.int16))
        
        st.success(f"ร้องโน้ตความถี่ {final_freq:.2f} Hz เรียบร้อย!")
        st.audio(virtual_file, format='audio/wav')

st.divider()
st.info("สโลแกน: อยู่นิ่งๆ ไม่เจ็บตัว - แต่ถ้าอยากขยับเสียง ลองปรับ Slider ดูครับ")
