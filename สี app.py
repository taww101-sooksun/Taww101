import streamlit as st
import os

st.set_page_config(page_title="My Music Hub", layout="centered")

st.title("🎵 คลังเพลงเพื่อนรัก")
st.write("เลือกเพลงที่อยากฟังจากรายการด้านล่างได้เลย!")

# กำหนดโฟลเดอร์ที่เก็บไฟล์เพลง (ต้องมีโฟลเดอร์นี้ใน GitHub ด้วย)
music_folder = "music"

# ตรวจสอบว่ามีโฟลเดอร์ไหม ถ้าไม่มีให้สร้าง (ป้องกัน Error)
if not os.path.exists(music_folder):
    os.makedirs(music_folder)
    st.info("กรุณาอัปโหลดไฟล์เพลง .mp3 ลงในโฟลเดอร์ 'music' บน GitHub ของคุณ")

# ดึงรายชื่อไฟล์เพลง
music_files = [f for f in os.listdir(music_folder) if f.endswith(".mp3")]

if music_files:
    # ลูกเล่น: ตัวเลือกเพลง
    selected_song = st.selectbox("เลือกเพลง:", music_files)
    
    # Path ของเพลงที่เลือก
    song_path = os.path.join(music_folder, selected_song)
    
    # ตัวเล่นเพลง
    st.audio(song_path)
    
    # เพิ่มลูกเล่นง่ายๆ: แสดงชื่อเพลงที่กำลังเล่นแบบเน้นๆ
    st.success(f"กำลังเล่นเพลง: {selected_song}")
else:
    st.warning("ยังไม่มีเพลงในคลังเลย ลองเพิ่มไฟล์ .mp3 ดูนะ")

# ลูกเล่นเพิ่มเติม: ให้เพื่อนโหวตเพลงหรือคอมเมนต์
st.divider()
st.subheader("💬 คุยกันท้ายเพลง")
comment = st.text_input("พิมพ์อะไรบอกเจ้าของแอปหน่อย...")
if st.button("ส่งความเห็น"):
    st.toast(f"ขอบคุณสำหรับความเห็น: {comment}")
