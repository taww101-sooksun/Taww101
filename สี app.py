import streamlit as st
from datetime import datetime

# --- [ 1. ตั้งค่าหน้าสถานี ] ---
st.set_page_config(page_title="สถานีอยู่นิ่งๆ ไม่เจ็บตัว", page_icon="📻", layout="centered")

# ระบบเก็บโพสต์ (ถ้าคนเข้าเยอะๆ จะเห็นข้อความกันหมด)
if 'public_posts' not in st.session_state:
    st.session_state.public_posts = []

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; text-align: center; }
    .post-box {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #FFD700;
        margin-bottom: 10px;
        text-align: left;
    }
    </style>
    """, unsafe_allow_html=True)

# 🌍 โลโก้ (ใช้รูปจากเน็ตเพื่อกัน Error 404)
st.image("https://img.freepik.com/free-vector/world-map-globe-isolated_24877-60511.jpg", width=250)

st.markdown("<h2 style='color: #FFD700;'>📻 STATION: อยู่นิ่งๆ ไม่เจ็บตัว</h2>", unsafe_allow_html=True)

# ✨ 1. ตัวหนังสือวิ่งบนสุด
st.markdown("""<marquee style="color: white; font-weight: bold; background: #050505; padding: 12px; border-radius: 10px; border: 1px solid #FFD700;">📢 ยินดีต้อนรับเข้าสู่สถานี อยู่นิ่งๆ ไม่เจ็บตัว ...เพื่อนๆ เข้ามาพิมพ์คุยกันทักทายกันได้เลยครับ ✨</marquee>""", unsafe_allow_html=True)

# --- [ 2. ส่วน YouTube 3 จุด ] ---
st.write("---")
# 1. Playlist
playlist_url = "https://www.youtube.com/embed/videoseries?list=PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
st.markdown(f'<iframe width="100%" height="400" src="{playlist_url}" frameborder="0" allowfullscreen style="border-radius:15px; border: 2px solid #333;"></iframe>', unsafe_allow_html=True)

# ✨ 2. ตัวหนังสือวิ่งคั่น YouTube 1
st.markdown("<marquee style='background: #FFD700; color: black; padding: 8px; font-weight: bold; border-radius: 5px; margin-top: 10px;'>🔴 กำลังรับฟังผลงานเพลงจากช่อง S.S.S Music 🔴</marquee>", unsafe_allow_html=True)

st.write("---")
# 2. วิดีโอเพลง
st.video("https://youtu.be/cbcuYnyr828?si=gCdCngKZztQVVZCe")

# ✨ 3. ตัวหนังสือวิ่งคั่น YouTube 2
st.markdown("<marquee style='background: #FF0000; color: white; padding: 8px; font-weight: bold; border-radius: 5px; margin-bottom: 10px;'>📺 ยินดีต้อนรับสู่ช่อง อยู่นิ้งๆไม่เจ็บตัว 🎬</marquee>", unsafe_allow_html=True)

# 3. วิดีโอช่อง
st.video("https://youtu.be/Bb3Jtsik3nY?si=Qyz3WtZLcxML3uF_")

# --- [ 3. กระดานโพสต์คุยกัน (Public Board) ] ---
st.write("---")
st.subheader("💬 กระดานคุยกันของเพื่อนๆ (Public)")
col_n, col_m = st.columns([1, 2])
with col_n:
    user_name = st.text_input("ชื่อของคุณ", placeholder="ชื่ออะไรดี?")
with col_m:
    user_msg = st.text_input("ข้อความ", placeholder="พิมพ์ทักทายเพื่อนๆ...")

if st.button("🚀 ส่งข้อความลงกระดาน"):
    if user_name and user_msg:
        now = datetime.now().strftime("%H:%M")
        st.session_state.public_posts.insert(0, {"name": user_name, "msg": user_msg, "time": now})
        st.balloons()
    else:
        st.warning("ใส่ชื่อกับข้อความด้วยนะเพื่อน")

# แสดงโพสต์ 5 อันล่าสุด
for p in st.session_state.public_posts[:5]:
    st.markdown(f"""<div class="post-box"><b>👤 {p['name']}</b> <small>({p['time']})</small><br>{p['msg']}</div>""", unsafe_allow_html=True)

# --- [ 4. ส่วนอัปโหลด & แชร์ ] ---
st.write("---")
# ✨ 4. ตัวหนังสือวิ่งส่วนอัปโหลด
st.markdown("<marquee style='background: #0000FF; color: white; padding: 8px; font-weight: bold; border-radius: 5px;'>📸 พื้นที่อัปโหลดรูปภาพและวิดีโอส่วนตัวของคุณ 📸</marquee>", unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    up_img = st.file_uploader("แปะรูป", type=["jpg", "png"], key="img_1")
    if up_img: st.image(up_img)
with c2:
