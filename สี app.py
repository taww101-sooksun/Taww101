import streamlit as st
from datetime import datetime

# --- [ 1. ตั้งค่าหน้าสถานี ] ---
st.set_page_config(page_title="สถานีอยู่นิ่งๆ ไม่เจ็บตัว", page_icon="📻", layout="wide")

# ระบบเก็บโพสต์ชั่วคราว
if 'posts' not in st.session_state:
    st.session_state.posts = []

# --- [ 2. เมนูแยกส่วนด้านข้าง (Sidebar) ] ---
st.sidebar.image("globe.jpg", width=150)
st.sidebar.title("เมนูสถานี")
choice = st.sidebar.radio("เลือกส่วนที่ต้องการ:", ["🎵 หน้าสถานีเพลง", "💬 กระดานคุยกัน", "📞 ห้องโทรคอลสด"])

st.sidebar.write("---")
st.sidebar.write('**สโลแกน:** "อยู่นิ่งๆ ไม่เจ็บตัว"')

# --- [ 3. ส่วนที่ 1: หน้าสถานีเพลง ] ---
if choice == "🎵 หน้าสถานีเพลง":
    st.markdown("<h2 style='color: #FFD700; text-align: center;'>📻 STATION: อยู่นิ่งๆ ไม่เจ็บตัว</h2>", unsafe_allow_html=True)
    st.markdown("""<marquee style="color: white; font-weight: bold; background: #050505; padding: 12px; border-radius: 10px; border: 1px solid #FFD700;">📢 ยินดีต้อนรับ! เลือกเมนูซ้ายมือเพื่อโพสต์คุยหรือโทรคอลกับเพื่อนๆ ได้เลยครับ ✨</marquee>""", unsafe_allow_html=True)
    
    st.write("---")
    playlist_url = "https://www.youtube.com/embed/videoseries?list=PL6S211I3urvpt47sv8mhbexif2YOzs2gO"
    st.markdown(f'<iframe width="100%" height="500" src="{playlist_url}" frameborder="0" allowfullscreen style="border-radius:15px; border: 2px solid #333;"></iframe>', unsafe_allow_html=True)
    
    st.markdown("<marquee style='background: #FFD700; color: black; padding: 8px; font-weight: bold;'>🔴 กำลังรับฟังเพลงจากช่อง S.S.S Music 🔴</marquee>", unsafe_allow_html=True)

# --- [ 4. ส่วนที่ 2: กระดานคุยกัน ] ---
elif choice == "💬 กระดานคุยกัน":
    st.header("💬 กระดานข้อความสาธารณะ")
    st.info("พิมพ์ทิ้งไว้ เพื่อนคนอื่นที่เข้ามาก็จะเห็นข้อความคุณครับ")
    
    col_n, col_m = st.columns([1, 2])
    with col_n:
        name = st.text_input("ชื่อของคุณ")
    with col_m:
        msg = st.text_input("ข้อความ")
    
    if st.button("🚀 ส่งโพสต์"):
        if name and msg:
            st.session_state.posts.insert(0, {"name": name, "msg": msg, "time": datetime.now().strftime("%H:%M")})
            st.balloons()
    
    st.write("---")
    for p in st.session_state.posts[:15]:
        st.markdown(f"**{p['name']}** ({p['time']}): {p['msg']}")
        st.write("---")

# --- [ 5. ส่วนที่ 3: ห้องโทรคอล (Video Call) ] ---
elif choice == "📞 ห้องโทรคอลสด":
    st.header("📞 ระบบวิดีโอคอล (คุยเห็นหน้า)")
    st.write("เราใช้ระบบ Jitsi Meet เพื่อความปลอดภัยและไม่ต้องใช้กุญแจ API ครับ")
    
    room_name = "OyuNingNingMaiJebTua_Room" # ตั้งชื่อห้องของคุณเองได้เลย
    call_url = f"https://meet.jit.si/{room_name}"
    
    st.warning("คำแนะนำ: เมื่อกดปุ่มด้านล่าง ระบบจะเปิดหน้าต่างใหม่เพื่อเข้าห้องคอล")
    st.link_button("🔥 กดเพื่อเข้าสู่ห้องคอล (Video Call) 🔥", call_url, use_container_width=True)
    
    st.image("https://img.freepik.com/free-vector/video-calling-concept-illustration_114360-1282.jpg", width=400)

# --- [ 6. ส่วนปิดท้าย (ตัววิ่งเขียว) ] ---
st.write("---")
st.markdown("<marquee style='color: #00FF00; font-family: Courier; background: #000; padding: 10px; border-radius: 10px;'>🚀 ขอบคุณที่แวะมาจอยกันที่สถานี อยู่นิ่งๆ ไม่เจ็บตัว... เพลงดี มิตรภาพเด่น... 🎧 🎶</marquee>", unsafe_allow_html=True)
