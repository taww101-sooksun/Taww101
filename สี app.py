import streamlit as st
import os

st.set_page_config(page_title="My Music Hub", layout="centered")

st.title("🎵 คลังเพลงเพื่อนรัก")

# 1. กำหนดชื่อโฟลเดอร์ให้ชัดเจน (แนะนำให้ใช้ภาษาอังกฤษตัวพิมพ์เล็ก)
music_folder = "music_library"

# 2. ตรวจสอบเงื่อนไขก่อน list ไฟล์
if not os.path.exists(music_folder):
    # ถ้าไม่มีโฟลเดอร์ ให้สร้างใหม่
    os.makedirs(music_folder)
    st.info(f"สร้างโฟลเดอร์ '{music_folder}' เรียบร้อยแล้ว กรุณาอัปโหลดไฟล์ .mp3 ลงไป")
    music_files = []
elif not os.path.isdir(music_folder):
    # ป้องกันกรณีมีไฟล์ชื่อเดียวกับโฟลเดอร์
    st.error(f"Error: มีไฟล์ที่ชื่อ '{music_folder}' อยู่แล้ว ทำให้สร้างโฟลเดอร์ไม่ได้")
    music_files = []
else:
    # อ่านไฟล์เพลงเฉพาะที่เป็น .mp3
    music_files = [f for f in os.listdir(music_folder) if f.lower().endswith(".mp3")]

# 3. ส่วนการแสดงผล
if music_files:
    selected_song = st.selectbox("เลือกเพลงที่อยากฟัง:", music_files)
    song_path = os.path.join(music_folder, selected_song)
    
    # แสดงตัวเล่นเพลง
    st.audio(song_path)
    st.success(f"กำลังเล่น: {selected_song}")
else:
    st.warning("ยังไม่พบไฟล์เพลงในระบบ")
    st.write("วิธีแก้: ตรวจสอบใน GitHub ว่าคุณมีโฟลเดอร์ชื่อ `music_library` และมีไฟล์ .mp3 อยู่ข้างในนั้นแล้วหรือยัง")
