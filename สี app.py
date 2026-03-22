import streamlit as st
import os

st.set_page_config(page_title="My Music Hub", layout="centered")

st.title("🎵 คลังเพลงเพื่อนรัก")

# เปลี่ยนมาดึงไฟล์จากหน้าแรก (Root) แทนการเข้าโฟลเดอร์
# วิธีนี้จะช่วยลดปัญหา NotADirectoryError ได้ 100%
current_dir = os.getcwd() 
music_files = [f for f in os.listdir(current_dir) if f.lower().endswith(".mp3")]

if music_files:
    selected_song = st.selectbox("เลือกเพลงที่อยากฟัง:", music_files)
    
    # เล่นเพลงจากหน้าแรกได้เลย
    st.audio(selected_song)
    st.success(f"กำลังเล่น: {selected_song}")
    
    st.divider()
    st.info("💡 ทิป: อัปโหลดไฟล์ .mp3 เพิ่มเข้าไปใน GitHub แล้วกด Refresh หน้าเว็บเพื่ออัปเดตเพลงใหม่ได้เลย!")
else:
    st.warning("⚠️ ยังไม่พบไฟล์เพลง .mp3 ใน GitHub")
    st.write("วิธีแก้: อัปโหลดไฟล์เพลง (นามสกุล .mp3) ไว้ที่หน้าแรกคู่กับไฟล์ app.py ของคุณครับ")
