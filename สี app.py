import streamlit as st
import os
import random
import streamlit.components.v1 as components

# 1. ตั้งค่าหน้าแอป
st.set_page_config(page_title="Vibe Player Final", layout="centered")

# 2. CSS สายรุ้ง + ตัววิ่ง + กราฟเสียง + ปรับแต่งปุ่ม
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;900&display=swap');
    
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

    /* ชื่อเพลงวิ่ง */
    .marquee {{
        width: 100%;
        overflow: hidden;
        background: rgba(0,0,0,0.7);
        padding: 12px 0;
        border-radius: 15px;
        border: 2px solid #AFEEEE;
        margin-bottom: 20px;
    }}
    .marquee p {{
        display: inline-block;
        white-space: nowrap;
        animation: marquee 15s linear infinite;
        font-family: 'Orbitron', sans-serif;
        font-size: 20px;
        color: #AFEEEE;
        margin: 0;
    }}
    @keyframes marquee {{
        0% {{ transform: translateX(100%); }}
        100% {{ transform: translateX(-100%); }}
    }}

    /* กราฟเสียง (Visualizer) แบบหลายแท่ง */
    .visualizer {{
        display: flex;
        align-items: flex-end;
        justify-content: center;
        height: 50px;
        gap: 3px;
        margin: 20px 0;
    }}
    .bar {{
        width: 8px;
        background: #AFEEEE;
        animation: equalize 0.8s infinite alternate;
        border-radius: 2px;
    }}
    @keyframes equalize {{
        0% {{ height: 5px; }}
        100% {{ height: 50px; }}
    }}

    /* ปรับแต่งปุ่มในรายการเพลง */
    .stButton>button {{
        width: 100%;
        background-color: rgba(175, 238, 238, 0.8) !important;
        color: #333 !important;
        border: 1px solid white !important;
        margin-bottom: 2px;
    }}

    h1, h3, p {{
        font-family: 'Orbitron', sans-serif;
        color: white !important;
        text-shadow: 2px 2px 4px #000;
    }}
    </style>
    """, unsafe_allow_html=True)

# 3. จัดการเพลง
music_files = [f for f in os.listdir('.') if f.lower().endswith(".mp3")]

if music_files:
    if 'song_index' not in st.session_state:
        st.session_state.song_index = 0
    
    current_song = music_files[st.session_state.song_index]

    st.title("🚀 MUSIC VIBE MAX")

    # --- ส่วนที่ 1: ชื่อเพลงวิ่ง ---
    st.markdown(f'<div class="marquee"><p>NOW PLAYING: {current_song} •--• NEXT TRACK LOADING... </p></div>', unsafe_allow_html=True)

    # --- ส่วนที่ 2: ปกวิดีโอ/รูป ---
    base_name = os.path.splitext(current_song)[0]
    if os.path.exists
