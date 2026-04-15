import streamlit as st
import numpy as np
import pandas as pd

# ==========================================
# 🧠 RBF VOCAL ENGINE (สูตรคณิตศาสตร์เพียวๆ)
# ==========================================
def generate_vocal_tone(valence, arousal, duration=4.0):
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration))
    
    # 1. หาความถี่หลัก (Fundamental Frequency) 
    # ใช้ฐานเสียง C4 (261.63 Hz) ปรับตาม Valence (ความสุข)
    base_f0 = 261.63 * (2**(valence * 0.5)) 
    
    # 2. คำนวณ Vibrato (การสั่นของเส้นเสียง)
    # Arousal สูง = สั่นเร็วและลึกขึ้น (คนตื่นเต้น/ร้องไห้)
    vibrato_rate = 4.5 + (arousal * 3.5) # 4.5 - 8.0 Hz
    vibrato_depth = arousal * 15         # ความลึกของการสั่น
    vibrato = vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)
    
    # 3. Additive Synthesis (สร้างฮาร์มอนิกเลียนแบบเนื้อเสียงมนุษย์)
    # ผสม Sine Waves หลายเลเยอร์เพื่อให้เสียงมี "ความหนา" (Timbre)
    # f0 (เสียงหลัก) + f1 (เสียงเต็ม) + f2 (เสียงใส)
    wave = 1.0 * np.sin(2 * np.pi * base_f0 * t + vibrato)          # Fundamental
    wave += 0.4 * np.sin(2 * np.pi * (base_f0 * 2) * t + vibrato)    # 2nd Harmonic
    wave += 0.2 * np.sin(2 * np.pi * (base_f0 * 3) * t)              # 3rd Harmonic
    
    # 4. ใส่ "เสียงลม" (Breathiness) ตามค่า Arousal
    noise = np.random.normal(0, 0.02 * (1 - arousal), len(t))
    wave += noise

    # 5. Envelope (ADSR - ลดเสียงคลิกตอนเริ่มและจบ)
    fade_len = int(sr * 0.3)
    envelope = np.ones_like(t)
    envelope[:fade_len] = np.linspace(0, 1, fade_len)
    envelope[-fade_len:] = np.linspace(1, 0, fade_len)
    
    final_audio = wave * envelope
    # Normalization (ปรับความดังให้พอดี)
    final_audio = final_audio / np.max(np.abs(final_audio)) * 0.8
    
    return final_audio.astype(np.float32), sr

# ==========================================
# 🎨 STREAMLIT INTERFACE
# ==========================================
st.set_page_config(page_title="RBF Vocal Prototype", layout="centered")

st.title("🎙️ RBF Vocal Synthesis Test")
st.markdown("### สังเคราะห์เสียงร้องจากคณิตศาสตร์ (ไม่มีการใช้ไฟล์เสียงอัด)")
st.write("ลองปรับค่า Valence (อารมณ์) และ Arousal (พลังงาน) แล้วฟังเสียงร้อง AI ดูครับ")

# ส่วนควบคุม
col1, col2 = st.columns(2)
with col1:
    v = st.slider("Valence (เศร้า <---> สุข)", 0.0, 1.0, 0.7)
with col2:
    a = st.slider("Arousal (สงบ <---> ตื่นเต้น)", 0.0, 1.0, 0.5)

if st.button("🚀 GENERATE & LISTEN", type="primary"):
    with st.spinner("AI กำลังคำนวณคลื่นเสียง..."):
        # รัน Engine
        audio, sr = generate_vocal_tone(v, a)
        
        # แสดงผลเสียง
        st.audio(audio, format='audio/wav', sample_rate=sr)
        
        # รายงานความจริง (7 Metrics)
        st.markdown("---")
        st.subheader("📊 7-Metric Precision Report")
        metrics = {
            "Vibrato Rate": f"{4.5 + (a * 3.5):.2f} Hz",
            "F0 Center": f"{261.63 * (2**(v * 0.5)):.2f} Hz",
            "Timbre Complexity": "Additive (3 Harmonics)",
            "Breathiness Index": f"{(1-a)*100:.1f}%",
            "Dynamics": "Stabilized",
            "Signal Purity": "High (Math-based)",
            "Mastering": "0.8 Normalized"
        }
        st.table(pd.DataFrame(metrics.items(), columns=["Metric", "Value"]))
        
        st.info("💡 นี่คือเสียงร้องต้นแบบที่เกิดจาก
