import streamlit as st
import numpy as np
import pandas as pd
from scipy.signal import butter, lfilter

# --- 1. CORE MATH ENGINE (ฟังก์ชันจัดการเสียงแต่ละเลเยอร์) ---

def apply_vocal_filter(data, cutoff, sr, btype='low'):
    """ฟิลเตอร์จัดการความถี่เพื่อลดเสียงกังวานแมลงหวี่"""
    nyq = 0.5 * sr
    normal_cutoff = cutoff / nyq
    b, a = butter(2, normal_cutoff, btype=btype, analog=False)
    return lfilter(b, a, data)

def generate_human_vocal(text_type, valence, arousal, duration=1.5):
    sr = 44100
    t = np.linspace(0, duration, int(sr * duration))
    
    # -- Layer 1: Fundamental Tone (เสียงร้องหลัก) --
    # ปรับ Pitch ตามความสุข (Valence)
    f0 = 220 * (2**(valence * 0.5)) 
    vibrato = (arousal * 10) * np.sin(2 * np.pi * (4 + arousal * 4) * t)
    vocal_core = np.sin(2 * np.pi * f0 * t + vibrato)
    vocal_core += 0.5 * np.sin(2 * np.pi * (f0 * 2) * t) # Harmonic 1
    
    # -- Layer 2: Breath & Air (เสียงลมหายใจ) --
    # สร้างเสียงซ่า (White Noise) แล้วกรองให้เหลือแต่เสียงลม (High Frequency Air)
    noise = np.random.normal(0, 0.1, len(t))
    breath_layer = apply_vocal_filter(noise, 8000, sr, btype='high') 
    # เสียงลมจะดังขึ้นตามค่า Arousal (ตื่นเต้น/เหนื่อย)
    breath_layer *= (0.05 + (1 - valence) * 0.1) 

    # -- Layer 3: Mouth & Tongue Transients (เสียงริมฝีปาก/เดาะปาก) --
    # เป็นเสียง "คลิก" สั้นๆ ตอนเริ่มคำ (Transient)
    click_t = np.linspace(0, 0.05, int(sr * 0.05))
    click = np.sin(2 * np.pi * 1000 * click_t) * np.exp(-100 * click_t)
    mouth_noise = np.zeros_like(t)
    mouth_noise[:len(click)] = click * 0.3 # ใส่ไว้ตอนเริ่มคำ

    # -- การคำนวณจุดรวมเสียง (Multi-Layer Summation) --
    # ใช้ Envelope คุมจังหวะไม่ให้เสียงตีกันจนเป็นคนละภาษา
    envelope = np.sin(np.pi * np.linspace(0, 1, len(t))) 
    
    # ผสมเลเยอร์ (The Secret Formula)
    final_audio = (vocal_core * envelope * 0.6) + (breath_layer * envelope * 0.3) + (mouth_noise * 0.1)
    
    # Normalize ปรับความดัง
    final_audio = final_audio / np.max(np.abs(final_audio)) * 0.8
    return final_audio.astype(np.float32), sr

# --- 2. STREAMLIT INTERFACE ---

st.title("🎙️ SYNAPSE: Full Vocal Multi-Layer Engine")
st.write("ระบบคำนวณแยก Layer: เสียงหลัก + เสียงลม + เสียงปาก")

col1, col2 = st.columns(2)
with col1:
    v = st.slider("ความสุข (Valence)", 0.0, 1.0, 0.5)
    a = st.slider("พลังงาน/การสั่น (Arousal)", 0.0, 1.0, 0.5)
with col2:
    st.info("ระบบจะใช้คณิตศาสตร์คำนวณจุดที่เสียงลมและเสียงปากเข้ามารวมกับเสียงหลัก เพื่อป้องกันเสียงกังวานแบบหุ่นยนต์")

if st.button("▶️ GENERATE FULL VOICE", type="primary"):
    with st.spinner("กำลังผสมเลเยอร์เสียง..."):
        audio, sr = generate_human_vocal("test", v, a)
        
        st.audio(audio, format='audio/wav', sample_rate=sr)
        
        # แสดงกราฟความจริงของเสียง
        st.subheader("📊 Signal Analysis (วิเคราะห์ 3 เลเยอร์)")
        chart_data = pd.DataFrame({
            "Waveform": audio[::100] # sampling มาแสดงผล
        })
        st.line_chart(chart_data)
        
        st.success("รวมเลเยอร์สำเร็จ: สังเกตช่วงเริ่มจะมีเสียง Mouth Noise และมีเสียง Breath คลุมตลอดทาง")

st.markdown("""
---
### 🧐 ทำไมตัวนี้ถึงต่างจากเดิม?
1. **แยก Layer ชัดเจน:** มีตัวแปร `breath_layer` และ `mouth_noise` แยกจากเสียงหลัก
2. **คุม Noise:** ไม่ใช่แค่เสียงซ่ามั่วๆ แต่ใช้ `apply_vocal_filter` กรองความถี่ให้เป็น "ลม" จริงๆ
3. **Envelope Tracking:** ใช้รูปคลื่นระฆังคว่ำคุมให้ลมหายใจเกิดพร้อมเสียงพูด ไม่ใช่ดังค้างยาวจนรบกวนหู
""")
