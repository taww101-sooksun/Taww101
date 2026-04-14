import streamlit as st
import os
import random
import streamlit.components.v1 as components

# --- 1. SET UP & THEME SELECTOR ---
st.set_page_config(page_title="SYNAPSE ROOMS", layout="wide")

# ประกาศค่าเริ่มต้นให้ครบเพื่อกัน Error
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
if 'bg_color' not in st.session_state: st.session_state.bg_color = "#121212"
if 'song_index' not in st.session_state: st.session_state.song_index = 0
if 'user' not in st.session_state: st.session_state.user = "Guest" # ดักไว้ก่อนถ้ายังไม่ login

with st.sidebar:
    if os.path.exists("logo2.jpg"):
        st.image("logo2.jpg", use_container_width=True)
    st.markdown("### 🎨 ปรับแต่งสีระบบ")
    st.session_state.theme_color = st.color_picker("เลือกสีนีออน", st.session_state.theme_color)
    st.session_state.bg_color = st.color_picker("เลือกสีพื้นหลัง", st.session_state.bg_color)
    st.write("---")
    st.markdown('**สโลแกน:** \n*"อยู่นิ่งๆ ไม่เจ็บตัว"*')

# --- 2. CSS DYNAMIC THEME (ตัวหนังสือวิ่งวิ้งๆ) ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {st.session_state.bg_color} !important; color: {st.session_state.theme_color} !important; }}
    .marquee {{
        width: 100%; overflow: hidden; white-space: nowrap; background: rgba(0,0,0,0.6);
        padding: 15px 0; border: 2px solid {st.session_state.theme_color}; border-radius: 12px;
        margin-bottom: 20px;
    }}
    .marquee p {{
        display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite;
        font-size: 22px; color: {st.session_state.theme_color}; 
        text-shadow: 0px 0px 10px {st.session_state.theme_color};
    }}
    @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. ระบบจัดการเพลง ---
music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

if music_files:
    current_song = music_files[st.session_state.song_index]
    
    # บรรทัดเจ้าปัญหาที่แก้แล้ว: เช็คชื่อ User ก่อนแสดงผล
    display_user = st.session_state.get('user', 'Guest')
    st.markdown(f'''
        <div class="marquee">
            <p>NOW PLAYING: {current_song} •--• SYNAPSE MUSIC STATION •--• AGENT: {display_user} </p>
        </div>
    ''', unsafe_allow_html=True)

    st.audio(current_song)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⏭️ เพลงถัดไป"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()
    with col2:
        if st.button("🎲 สุ่มเพลง"):
            st.session_state.song_index = random.randint(0, len(music_files) - 1)
            st.rerun()
else:
    st.error("ไม่พบไฟล์เพลง .mp3 ในโฟลเดอร์ครับ")
