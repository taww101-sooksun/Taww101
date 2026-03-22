import streamlit as st
import os
import random

# 1. ตั้งค่าหน้าแอป
st.set_page_config(page_title="Music Rainbow Hub", layout="centered", page_icon="🌈")

# 2. ใส่ CSS สำหรับ Background สายรุ้งวิ่ง และปรับแต่งสีตัวอักษร
st.markdown(f"""
    <style>
    /* ส่วนของ Background ทั้งแอป */
    .stApp {{
        background: linear-gradient(270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff);
        background-size: 1200% 1200%;
        animation: RainbowFlow 10s ease infinite;
    }}

    @keyframes RainbowFlow {{
        0%{{background-position:0% 50%}}
        50%{{background-position:100% 50%}}
        100%{{background-position:0% 50%}}
    }}

    /* ปรับแต่งสีกล่องข้อความและสีพื้นหลังบางส่วนให้เข้ากับสีที่คุณเลือก */
    .stSelectbox, .stButton>button {{
        background-color: #AFEEEE !important; /* Pale Turquoise */
        color: #333 !important;
        border-radius: 10px;
    }}
    
    h1, h2, h3, p {{
        color: #FFFFFF; /* สีตัวอักษรขาวเพื่อให้ตัดกับพื้นหลัง */
        text-shadow: 2px 2px 4px #000000; /* ใส่เงาให้ดูลอยออกมา */
    }}

    /* ปรับแต่งขอบ Sidebar */
    [data-testid="stSidebar"] {{
        background-color: #FF7F50 !important; /* Coral */
    }}
    </style>
    """, unsafe_allow_html=True)

# 3. แสดงโลโก้ (logo2.jpg)
if os.path.exists("logo2.jpg"):
    # จัดวางโลโก้ให้อยู่ตรงกลาง
    col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
    with col_logo2:
        st.image("logo3.jpg", use_container_width=True)
else:
    st.warning("⚠️ ไม่พบไฟล์ logo2.jpg ใน GitHub ของคุณ")

st.title("🎵 คลังเพลง Rainbow Vibe")
st.markdown("---")

# 4. ส่วนของเครื่องเล่นเพลง (ดึงโค้ดเดิมมาปรับใช้)
current_dir = os.getcwd() 
music_files = [f for f in os.listdir(current_dir) if f.lower().endswith(".mp3")]

if music_files:
    selected_song = st.selectbox("🎧 เลือกเพลงที่จะเปิด:", music_files)
    st.write(f"### กำลังเล่น: **{selected_song}**")
    st.audio(selected_song)
    
    # เพิ่มลูกเล่นปุ่มสี Coral
    if st.button("🎲 สุ่มเพลงใหม่"):
        st.session_state.selected_song = random.choice(music_files)
        st.rerun()
else:
    st.error("❌ ยังไม่มีไฟล์เพลง .mp3 ในเครื่อง")

st.info("💡 พื้นหลังกำลังวิ่งแบบ Rainbow Flow ตามที่คุณต้องการเลย!")
