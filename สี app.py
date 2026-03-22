import streamlit as st
import os

# 1. ตั้งค่าหน้าแอป
st.set_page_config(page_title="My Vibe Music", layout="centered")

# 2. ใส่ CSS สายรุ้งวิ่ง (Rainbow Flow) เหมือนเดิม
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
        color: white !important;
        text-shadow: 2px 2px 4px #000;
    }}
    /* สไตล์ปุ่มกดขนาดใหญ่ */
    .stButton>button {{
        width: 100%;
        height: 60px;
        background-color: #AFEEEE !important;
        color: #333 !important;
        font-size: 20px !important;
        border-radius: 15px !important;
        font-weight: bold;
        border: 2px solid white !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# 3. แสดงโลโก้
if os.path.exists("logo3.jpg"):
    st.image("logo3.jpg", width=150)

st.title("🎧 MY PRIVATE VIBE")
st.write("กดปุ่มด้านล่างเพื่อเข้าสู่เพลย์ลิสต์ 35 เพลง")

# 4. ปุ่มเข้าสู่ YouTube (วิธีนี้เล่นได้แน่นอน 100%)
playlist_url = "https://youtube.com/playlist?list=PL6S211I3urvqVH9bDPIr0SLQkENDsNx3Y"

st.markdown("---")

# สร้างปุ่มที่กดแล้วเด้งไปแอป YouTube
st.link_button("🚀 เปิดฟังเพลงใน YouTube (35 เพลง)", playlist_url)

st.info("""
    💡 **ทำไมต้องกดปุ่ม?** เนื่องจากบางเพลงมีลิขสิทธิ์ทำให้เปิดในแอปโดยตรงไม่ได้ 
    การกดปุ่มนี้จะทำให้เพื่อนของคุณดูวิดีโอได้ลื่นไหล ยอดวิวขึ้น และฟังได้ต่อเนื่องครับ
""")

st.divider()

# 5. กระดานข้อความ (ยังอยู่เหมือนเดิม)
st.subheader("💬 ฝากความคิดถึง")
name = st.text_input("ชื่อของคุณ:")
msg = st.text_area("ข้อความ:")
if st.button("ส่งข้อความ"):
    st.success("ขอบคุณที่แวะมาฟังเพลงครับ!")
    st.balloons()
