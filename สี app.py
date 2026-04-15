import streamlit as st
import librosa
import soundfile as sf
import numpy as np
import io

# --- 1. ตั้งค่าแม่พิมพ์ (ตรงนี้คือหัวใจที่คุณสั่ง) ---
# คุณสามารถมาแก้ตัวเลข rate หรือคำสั่งสอนผู้ใช้ได้ที่นี่
GENRE_MOLDS = {
    "R&B": {
        "rate": 0.8, 
        "guide": "ร้องเสียง 'อาาา' หรือ 'อู้ววว' ลากยาวๆ นุ่มๆ ประมาณ 5 วินาที",
        "color": "#FF4B4B"
    },
    "HipHop": {
        "rate": 1.0, 
        "guide": "ทำเสียง 'ตึก-โป๊ะ' หรือเดาะปากเป็นจังหวะหนักๆ 4 ครั้ง",
        "color": "#1E90FF"
    },
    "RAP": {
        "rate": 1.4, 
        "guide": "พูดคำคมๆ สั้นๆ เช่น 'โย่ว!' 'เช็ค!' หรือ 'เอ้อ!' รัวๆ 4-5 ครั้ง",
        "color": "#32CD32"
    }
}

st.set_page_config(page_title="SYNAPSE Engine", layout="centered")
st.title("🎙️ SYNAPSE: Voice Mold")
st.write("---")

# --- 2. ส่วนเลือกแนวเพลง ---
selected_genre = st.selectbox("เลือกแนวเพลงที่จะเจนเสียง:", list(GENRE_MOLDS.keys()))

# แสดงคำแนะนำตามแม่พิมพ์ที่เลือก
mold = GENRE_MOLDS[selected_genre]
st.markdown(f"### {selected_genre} Mode")
st.info(mold['guide'])

# --- 3. ส่วนรับไฟล์เสียงจากผู้ใช้ ---
uploaded_file = st.file_uploader("อัปโหลดเสียงที่คุณเจนตามคำสั่งด้านบน", type=['wav', 'mp3', 'm4a'])

if uploaded_file:
    st.success("ได้รับวัตถุดิบแล้ว!")
    
    if st.button(f"🚀 เริ่มรันแม่พิมพ์ {selected_genre}"):
        with st.spinner("กำลังใช้คณิตศาสตร์จัดระเบียบจังหวะ..."):
            try:
                # โหลดไฟล์เสียง (จำกัด  120วินาทีเพื่อป้องกันเครื่องค้าง)
                y, sr = librosa.load(uploaded_file, duration=120.0)
                
                # --- 4. จุดที่ทำตามสั่ง (การยืดหดเสียง) ---
                # นี่คือจุดที่ 'บังคับ' ให้เสียงวิ่งตาม Rate ที่คุณตั้งไว้
                y_stretched = librosa.effects.time_stretch(y, rate=mold['rate'])
                
                # เตรียมไฟล์สำหรับเล่น
                buffer = io.BytesIO()
                sf.write(buffer, y_stretched, sr, format='WAV')
                
                st.write("---")
                st.subheader("ผลลัพธ์ที่ตรงจังหวะแม่พิมพ์:")
                st.audio(buffer, format='audio/wav')
                st.balloons()
                
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาด: {e}")

st.write("---")
st.caption("สโลแกน: อยู่นิ่งๆ ไม่เจ็บตัว | ระบบจัดการจังหวะด้วยคณิตศาสตร์")
