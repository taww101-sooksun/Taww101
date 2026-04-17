import streamlit as st
import librosa
import soundfile as sf
import numpy as np
import io

# --- 1. กำหนดค่าเครื่องดนตรีมาตรฐาน (Instrument Database) ---
INSTRUMENTS = {
    "Drums": {"volume": 0.8, "style": "HipHop Beat"},
    "Guitar_Dist": {"volume": 0.6, "style": "Rock/Aggressive"},
    "Guitar_Clean": {"volume": 0.5, "style": "Smooth/Chill"}
}

# --- 2. แม่พิมพ์รวมร่าง (The Master Mold) ---
def mix_instruments(user_voice, sr, style="Rock"):
    # สร้างจังหวะกลองจำลอง (แบบคณิตศาสตร์ ไม่ใช่ไฟล์เสียง)
    # เพื่อให้เสียงผู้ใช้ลงล็อคกับ "กอง" และ "กีต้าร์"
    duration = len(user_voice) / sr
    t = np.linspace(0, duration, len(user_voice))
    
    # จำลองเสียงกีต้าร์ (ใช้ Sine Wave พื้นฐานมาผสมให้เกิดคอร์ด)
    if style == "Rock":
        # กีต้าร์แผด (Distortion) - ใส่ Noise เล็กน้อยให้ดูดิบ
        guitar_layer = np.sin(2 * np.pi * 110 * t) + np.random.normal(0, 0.1, len(user_voice))
    else:
        # กีต้าร์ใส - เสียงนิ่งๆ นุ่มๆ
        guitar_layer = np.sin(2 * np.pi * 110 * t)

    # รวมเสียง: ผู้ใช้ + กีต้าร์ + กลอง (จำลอง)
    mixed_audio = user_voice + (guitar_layer * 0.2) 
    return mixed_audio

# --- 3. หน้าจอแอป ---
st.title("🎸 SYNAPSE: Multi-Instrument Mold")

# ส่วนเลือกเครื่องดนตรีที่จะมา "หุ้ม" เสียงผู้ใช้
st.subheader("เลือกเครื่องดนตรีที่จะใส่ในแม่พิมพ์")
col1, col2 = st.columns(2)
with col1:
    use_drums = st.checkbox("ใส่กอง (Drums)", value=True)
with col2:
    guitar_type = st.selectbox("เลือกสไตล์กีต้าร์:", ["กีต้าร์แผด", "กีต้าร์ใส"])

# คำสั่งเจนเสียง
st.info(f"🎤 สั่งการ: ทำเสียง 'ตึก-ตึก-โป๊ะ' ให้เข้ากับ {guitar_type} ครับ")

uploaded_file = st.file_uploader("อัปโหลดเสียงที่เจนมา")

if uploaded_file:
    if st.button("🚀 รันแม่พิมพ์รวมเครื่องดนตรี"):
        y, sr = librosa.load(uploaded_file)
        
        # เลือกสไตล์ตามที่ผู้ใช้เลือก
        style_mode = "Rock" if guitar_type == "กีต้าร์แผด" else "Clean"
        
        # รันระบบรวมเสียง
        final_mix = mix_instruments(y, sr, style=style_mode)
        
        # ส่งผลลัพธ์
        buffer = io.BytesIO()
        sf.write(buffer, final_mix, sr, format='WAV')
        st.audio(buffer, format='audio/wav')
        st.success(f"รวมร่างเสียงผู้ใช้ + กอง + {guitar_type} เรียบร้อย!")
