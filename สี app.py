import streamlit as st
import numpy as np
import scipy.io.wavfile as wavfile
import io

# --- เครื่องยนต์สร้างเสียง 3 เลเยอร์ (คณิตศาสตร์ล้วน) ---
class SynapseTuedEngine:
    def __init__(self, sr=44100):
        self.sr = sr

    def generate_layered_tone(self, freq, duration, v_low, v_mid, v_high):
        t = np.linspace(0, duration, int(self.sr * duration))
        
        # 1. เลเยอร์ต่ำ (Sub/Low): คลื่น Sine หนาๆ ทุ้มๆ (ลดลง 1 Octave)
        low_wave = np.sin(2 * np.pi * (freq / 2) * t) * v_low
        
        # 2. เลเยอร์กลาง (Mid): คลื่น Square ให้ความตืดแบบ Synth (ความถี่หลัก)
        mid_wave = np.sign(np.sin(2 * np.pi * freq * t)) * v_mid
        
        # 3. เลเยอร์สูง (High): คลื่น Sawtooth แหลมสว่าง (เพิ่มขึ้น 1 Octave)
        high_wave = (2 * (t * (freq * 2) - np.floor(0.5 + t * (freq * 2)))) * v_high
        
        # รวมร่างและเกลี่ยเสียงไม่ให้แตก
        combined = (low_wave + mid_wave + high_wave)
        if np.max(np.abs(combined)) > 0:
            combined = combined / np.max(np.abs(combined))
            
        # Envelope: ให้มันกระแทกตอนต้นแล้วค่อยๆ จาง (Decay)
        env = np.exp(-4 * t)
        return (combined * env * 0.5 * 32767).astype(np.int16)

# --- หน้าแอป ---
st.set_page_config(page_title="Synapse 3-Slide Synth", layout="wide")
st.title("🎛️ Synapse 3-Layer Tued Machine")
st.write("ปรับสไลเดอร์เพื่อผสมเสียง **สูง-กลาง-ต่ำ** แล้วกดเล่นโน้ตด้านล่าง")

# --- แถบควบคุมข้างซ้าย (3 ตัวสไลด์ที่พี่บอก) ---
with st.sidebar:
    st.header("🎚️ Master Mix")
    vol_low = st.slider("เสียงต่ำ (Low/Sub)", 0.0, 1.0, 0.8)
    vol_mid = st.slider("เสียงกลาง (Mid/Synth)", 0.0, 1.0, 0.5)
    vol_high = st.slider("เสียงสูง (High/Lead)", 0.0, 1.0, 0.2)
    st.divider()
    use_432 = st.checkbox("ระบบ 432Hz (Pure Truth)", value=True)

# ข้อมูลโน้ต โด-เร-มี-ฟา-ซอล-ลา-ที-โด
DO_RE_MI = {
    "โด (C)": 261.63, "เร (D)": 293.66, "มี (E)": 329.63, 
    "ฟา (F)": 349.23, "ซอล (G)": 392.00, "ลา (A)": 440.00, 
    "ที (B)": 493.88, "โด+ (C2)": 523.25
}

# --- ส่วนแสดงผลคีย์บอร์ด ---
st.subheader("🎹 บันไดเสียง (12 คีย์มาตรฐาน)")
cols = st.columns(8) # เรียง โด-โด+ 8 ปุ่มหลัก
engine = SynapseTuedEngine()
factor = (432/440) if use_432 else 1.0

for i, (name, f) in enumerate(DO_RE_MI.items()):
    with cols[i]:
        if st.button(name, use_container_width=True, type="primary"):
            # สร้างเสียง 3 เลเยอร์สดๆ ตามค่า Slider
            audio_data = engine.generate_layered_tone(
                freq=f * factor,
                duration=0.8,
                v_low=vol_low,
                v_mid=vol_mid,
                v_high=vol_high
            )
            
            # เล่นเสียงทันที
            buf = io.BytesIO()
            wavfile.write(buf, 44100, audio_data)
            st.audio(buf, format='audio/wav', autoplay=True)

st.divider()
st.info("💡 **ทริค:** ลองลด Mid/High ให้เป็น 0 แล้วดัน Low สุด พี่จะได้เสียงเบสเตะอกแบบในผับเลยครับ!")
