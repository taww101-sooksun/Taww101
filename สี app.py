import streamlit as st
import os
import base64

# --- ตั้งค่าธีมและหน้าจอ ---
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
    </style>
""", unsafe_allow_html=True)

# ฟังก์ชันแปลงไฟล์เพลงเป็นข้อมูล (Base64)
def get_audio_bytes(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- ระบบจัดการไฟล์ ---
music_files = [f for f in os.listdir('.') if f.lower().endswith(".mp3")]

if music_files:
    if 'idx' not in st.session_state: st.session_state.idx = 0
    current_song = music_files[st.session_state.idx]
    
    # ดึงข้อมูลเพลงมาเตรียมไว้
    audio_base64 = get_audio_bytes(current_song)
    audio_link = f"data:audio/mpeg;base64,{audio_base64}"

    st.title("🎧 SYNAPSE DJ STATION")
    
    st.markdown(f"""
        <div class="player-card">
            <h2 style="color:{theme_color};">เพลง: {current_song}</h2>
            <br>
            <audio controls autoplay style="width: 100%;">
                <source src="{audio_link}" type="audio/mpeg">
            </audio>
            <p style="margin-top: 20px; opacity: 0.6; color:{theme_color};">"อยู่นิ่งๆ ไม่เจ็บตัว"</p>
        </div>
    """, unsafe_allow_html=True)

    # --- ปุ่มควบคุม ---
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
    st.error("ไม่พบไฟล์เพลงในระบบครับ")
