import streamlit as st
import os

# 1. ตั้งค่าหน้าจอและธีมนีออนที่คุณชอบ
st.set_page_config(page_title="SYNAPSE STATION", layout="wide")
theme_color = "#00f2fe"

st.markdown(f"""
    <style>
    .stApp {{ background-color: #121212 !important; color: {theme_color} !important; }}
    .player-card {{
        background: #000; padding: 30px; border-radius: 20px;
        border: 2px solid {theme_color}; text-align: center;
        box-shadow: 0 0 15px {theme_color}55;
    }}
    h1, h2 {{ color: {theme_color} !important; font-family: sans-serif; }}
    </style>
""", unsafe_allow_html=True)

# 2. ค้นหาไฟล์เพลง (ดึงชื่อจริงจากในเครื่องคุณ)
music_files = [f for f in os.listdir('.') if f.lower().endswith(".mp3")]

if music_files:
    if 'idx' not in st.session_state: st.session_state.idx = 0
    current_song = music_files[st.session_state.idx]

    st.title("🎧 SYNAPSE DJ STATION")
    
    # 3. ส่วนแสดงผลเครื่องเล่น
    st.markdown(f"""
        <div class="player-card">
            <h2>ตอนนี้คือเพลง: {current_song}</h2>
            <br>
            <audio controls autoplay style="width: 100%;">
                <source src="app/static/{current_song}" type="audio/mpeg">
                <source src="{current_song}" type="audio/mpeg">
                เบราว์เซอร์ของคุณไม่รองรับการเล่นเสียง
            </audio>
            <p style="margin-top: 20px; opacity: 0.6;">"อยู่นิ่งๆ ไม่เจ็บตัว"</p>
        </div>
    """, unsafe_allow_html=True)

    # 4. ปุ่มควบคุมแบบ Streamlit (ใช้งานได้จริง)
    st.write("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⏮️ เพลงก่อนหน้า"):
            st.session_state.idx = (st.session_state.idx - 1) % len(music_files)
            st.rerun()
    with c2:
        st.write(f"เพลงที่ {st.session_state.idx + 1} / {len(music_files)}")
    with c3:
        if st.button("⏭️ เพลงถัดไป"):
            st.session_state.idx = (st.session_state.idx + 1) % len(music_files)
            st.rerun()
else:
    st.error("ไม่พบไฟล์ .mp3 ในโฟลเดอร์ครับเพื่อน เช็กไฟล์ในหน้า GitHub อีกทีนะ")
