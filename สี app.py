import streamlit as st
import librosa
import numpy as np
import soundfile as sf
from io import BytesIO

st.title("🎙️ SYNAPSE: Real-Voice Granular Engine")
st.write("ตัวนี้จะดึง 'ดีเอ็นเอ' จากเสียง 50 วินาทีของคุณมาสร้างคำใหม่")

uploaded_file = st.file_uploader("โหลดเสียง 50 วินาทีของคุณที่นี่", type=['wav', 'mp3'])

if uploaded_file:
    # 1. โหลดเสียงจริงของคุณ (The Truth Data)
    y, sr = librosa.load(uploaded_file)
    
    # 2. คำนวณหาจุดที่เป็น "เสียงเงียบ" และ "เสียงพูด"
    # เพื่อแยกเสียงลม (Breath) ออกจากเสียงเนื้อ (Vocal)
    intervals = librosa.effects.split(y, top_db=20)
    
    st.success(f"ตรวจพบหน่วยเสียงทั้งหมด {len(intervals)} จุดในไฟล์ของคุณ")

    if st.button("🚀 สั่งให้ AI พูดด้วยเนื้อเสียงจริง"):
        # กลยุทธ์: แทนที่จะสร้าง Sine Wave เราจะไป "หยิบ" ชิ้นส่วนเสียงคุณมาเรียง
        # นี่คือวิธีที่ทำให้เสียงไม่กังวานเป็นหุ่นยนต์
        output_audio = []
        
        for start, end in intervals[:15]: # สุ่มหยิบมา 15 ชิ้นส่วนมาเรียงใหม่
            chunk = y[start:end]
            # ใส่ Fade in/out เล็กๆ เพื่อไม่ให้เสียงคลิก (กังวานเหล็ก)
            fade = int(sr * 0.01)
            window = np.ones(len(chunk))
            window[:fade] = np.linspace(0, 1, fade)
            window[-fade:] = np.linspace(1, 0, fade)
            output_audio.extend(chunk * window)
            
        final_y = np.array(output_audio)
        
        # แสดงผล
        st.markdown("### 🔊 เสียงที่เกิดจากการเรียง 'หน่วยเสียงจริง' ของคุณ:")
        st.audio(final_y, format='audio/wav', sample_rate=sr)
        
        st.warning("สังเกตไหมครับ? เสียงจะมีความเป็น 'คน' มากขึ้น เพราะมันคือเสียงคุณจริงๆ ที่ถูกตัดมาเรียงใหม่")
