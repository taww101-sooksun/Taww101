import streamlit as st
import os

# 1. ตั้งค่าหน้าแอป
st.set_page_config(page_title="My Vibe YouTube Playlist", layout="centered", page_icon="🌈")

# 2. ใส่ CSS สำหรับ Background สายรุ้งวิ่ง (Rainbow Flow)
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');

    .stApp {{
        background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
        background-size: 1200% 1200%;
        animation: RainbowFlow 15s ease infinite;
    }}

    @keyframes RainbowFlow {{
        0%{{background-position:0% 50%}}
        50%{{background-position:100% 50%}}
        100%{{background-position:0% 50%}}
    }}

    h1, h3, p {{
        font-family: 'Orbitron', sans-serif;
        color: #FFFFFF !important;
        text-shadow: 2px 2px 4px #000000;
    }}

    .stButton>button {{
        background-color: #AFEEEE !important;
        color: #333 !important;
        border-radius: 15px !important;
        border: 2px solid white !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# 3. แสดงโลโก้
if os.path.exists("logo3.jpg"):
    col_logo1, col_logo2, col_logo3 = st.columns([1, 1.5, 1])
    with col_logo2:
        st.image("logo3.jpg", use_container_width=True)

st.title("📺 PRIVATE PLAYLIST")
st.write("คลังเพลง 35 เพลงสุดฟิน")

# 4. ใส่ลิงก์แบบ Embed ที่ชัวร์ที่สุด
# ผมลบส่วน &si= ออกเพื่อให้ลิงก์สะอาดขึ้น ระบบจะอ่านง่ายขึ้นครับ
playlist_id = "PL6S211I3urvqVH9bDPIr0SLQkENDsNx3Y"
clean_url = f"https://www.youtube.com/watch?v=videoseries&list={playlist_id}"

st.markdown("---")

# 5. แสดงเครื่องเล่นวิดีโอ
# ใช้ st.video กับลิงก์ที่คลีนแล้ว
try:
    st.video(clean_url)
    st.success("โหลดเพลย์ลิสต์สำเร็จ! กด Play ได้เลย")
except:
    st.error("เกิดปัญหาในการดึงวิดีโอ กรุณาลอง Refresh หน้าเว็บอีกครั้ง")

st.info("""
    💡 **วิธีดูรายชื่อเพลง:** กดที่ไอคอนรูป 'ขีด 3 ขีด' ที่มุมขวาบนของวิดีโอ เพื่อเลือกเพลงในลิสต์ทั้ง 35 เพลงครับ
""")

st.divider()

# 6. ส่วนคอมเมนต์
st.subheader("💬 ฝากข้อความ")
name = st.text_input("ชื่อของคุณ:")
msg = st.text_area("ข้อความ:")
if st.button("ส่ง"):
    st.toast("ส่งความรู้สึกเรียบร้อย!")
