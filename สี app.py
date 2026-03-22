import streamlit as st
import os

# 1. ตั้งค่าหน้าแอป
st.set_page_config(page_title="My Vibe YouTube Playlist", layout="centered", page_icon="🌈")

# 2. ใส่ CSS สำหรับ Background สายรุ้งวิ่งและปรับแต่งธีม
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

    h1, h2, h3, p {{
        font-family: 'Orbitron', sans-serif;
        color: #FFFFFF !important;
        text-shadow: 2px 2px 4px #000000;
    }}

    /* ปรับแต่งปุ่มและส่วนประกอบอื่นๆ */
    .stButton>button {{
        background-color: #AFEEEE !important;
        color: #333 !important;
        border-radius: 15px !important;
        border: 2px solid white !important;
        font-weight: bold;
    }}
    </style>
    """, unsafe_allow_html=True)

# 3. แสดงโลโก้ (logo3.jpg)
if os.path.exists("logo3.jpg"):
    col_logo1, col_logo2, col_logo3 = st.columns([1, 1.5, 1])
    with col_logo2:
        st.image("logo3.jpg", use_container_width=True)

st.title("📺 MY PRIVATE PLAYLIST")
st.write("คลังเพลง 35 เพลงสุดฟิน ฟังต่อเนื่องได้เลย!")

# 4. ใส่ลิงก์ Playlist ของคุณ (ดึงจากที่คุณส่งมา)
playlist_url = "https://youtube.com/playlist?list=PL6S211I3urvqVH9bDPIr0SLQkENDsNx3Y&si=nuIyO4KQ5r5-vx0c"

st.markdown("---")

# 5. ส่วนเครื่องเล่นวิดีโอ (YouTube Embed)
# ระบบจะจัดการเรื่องเล่นต่อเนื่องและยอดวิวให้เองครับ
st.video(playlist_url)

st.info("""
    💡 **ทิปพิเศษ:** - กดปุ่ม **Playlist** (รูปขีดสามขีดตรงขวาบนของวิดีโอ) เพื่อดูรายชื่อเพลงทั้ง 35 เพลง
    - ระบบจะเล่นเพลงถัดไปให้เองอัตโนมัติ (Autoplay) ตามระบบของ YouTube ครับ
    - ทุกครั้งที่เพื่อนฟัง ยอดวิวจะขึ้นให้เจ้าของคลิปปกติเลย
""")

st.divider()

# 6. ส่วนคอมเมนต์ (เผื่อเพื่อนอยากฝากอะไรไว้)
st.subheader("💬 ฝากข้อความถึงเพื่อน")
name = st.text_input("ชื่อเล่นของคุณ:")
msg = st.text_area("อยากบอกอะไรไหม:")
if st.button("ส่งความรู้สึก"):
    if name and msg:
        st.success(f"ขอบคุณนะ {name}! ข้อความของคุณถูกส่งแล้ว")
        st.balloons()
    else:
        st.warning("กรุณากรอกชื่อและข้อความด้วยนะ")

