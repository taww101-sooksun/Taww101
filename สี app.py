import streamlit as st
import os
import random

# ตั้งค่าหน้าแอป
st.set_page_config(page_title="My Music Hub", layout="centered")

st.title("🎵 คลังเพลงเพื่อนรัก")

# --- ส่วนของการดึงข้อมูลเพลง ---
current_dir = os.getcwd() 
music_files = [f for f in os.listdir(current_dir) if f.lower().endswith(".mp3")]

if music_files:
    # ลูกเล่นที่ 1: ระบบสุ่มเพลง (Shuffle)
    if st.button("🔀 สุ่มเพลงให้หน่อย"):
        st.session_state.selected_song = random.choice(music_files)
        st.toast(f"สุ่มได้เพลง: {st.session_state.selected_song}")

    # ตรวจสอบว่ามีเพลงที่เลือกค้างไว้ไหม ถ้าไม่มีให้เอาเพลงแรกในลิสต์
    if 'selected_song' not in st.session_state:
        st.session_state.selected_song = music_files[0]

    # ลูกเล่นที่ 2: ช่องเลือกเพลง (จะเปลี่ยนตามปุ่มสุ่ม หรือเลือกเองก็ได้)
    index = music_files.index(st.session_state.selected_song)
    selected_song = st.selectbox("เลือกเพลงที่อยากฟัง:", music_files, index=index)
    
    # อัปเดตค่าที่เลือกปัจจุบันลง session_state
    st.session_state.selected_song = selected_song

    # --- ส่วนการแสดงผลตัวเล่นเพลง ---
    st.write(f"### 🎧 กำลังเล่น: **{selected_song}**")
    st.audio(selected_song)
    
    # ลูกเล่นที่ 3: ใส่เนื้อเพลง (ตัวอย่างเฉพาะเพลงที่คุณมี)
    lyrics_data = {
        "ขอบคุณทุกคำที่ทำให้ฉันเจ็บ.mp3": "เนื้อเพลง: ...ขอบคุณที่ทิ้งกันในวันนั้น ทำให้ฉันแข็งแกร่งกว่าเดิม...",
        # คุณสามารถเพิ่มเพลงอื่นๆ ตรงนี้ได้
    }

    if selected_song in lyrics_data:
        with st.expander("📖 ดูเนื้อเพลง"):
            st.write(lyrics_data[selected_song])
    else:
        with st.expander("📖 ดูเนื้อเพลง"):
            st.write("ขออภัย ยังไม่มีเนื้อเพลงสำหรับเพลงนี้ในระบบ")

    st.divider()
    st.info("💡 ส่งลิงก์หน้านี้ให้เพื่อนฟังไปพร้อมกันได้เลย!")

else:
    st.warning("⚠️ ยังไม่พบไฟล์เพลง .mp3 ใน GitHub")
    st.write("อัปโหลดไฟล์เพลงไว้ที่หน้าเดียวกับไฟล์ app.py นะครับ")

# ลูกเล่นที่ 4: ส่วนคอมเมนต์ท้ายแอป
st.subheader("💬 คุยกับเจ้าของคลังเพลง")
name = st.text_input("ชื่อของคุณ:")
msg = st.text_area("อยากบอกอะไรไหม:")
if st.button("ส่งข้อความ"):
    if name and msg:
        st.success(f"ขอบคุณนะ {name}! ข้อความของคุณถูกส่งแล้ว (จำลอง)")
    else:
        st.error("กรุณากรอกชื่อและข้อความด้วยนะ")
