import streamlit as st
import os
import random
import time
import psutil  # ใช้ดูสถานะเครื่องจริงๆ
from datetime import datetime
import streamlit.components.v1 as components

# --- 1. SET UP & THEME ---
st.set_page_config(page_title="SYNAPSE ROOMS v2", layout="wide")

if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "#39FF14" 
if 'bg_color' not in st.session_state:
    st.session_state.bg_color = "#0a0a0a" 
if 'user_id' not in st.session_state:
    st.session_state.user_id = f"USER_{random.randint(1000, 9999)}"

with st.sidebar:
    if os.path.exists("logo2.jpg"):
        st.image("logo2.jpg", use_container_width=True)
    st.markdown(f"### ⚡ SYSTEM ID: `{st.session_state.user_id}`")
    st.session_state.theme_color = st.color_picker("NEON CORE", st.session_state.theme_color)
    st.session_state.bg_color = st.color_picker("VOID COLOR", st.session_state.bg_color)
    
    # แสดง Real-time Stat (ทำได้จริง)
    cpu_usage = psutil.cpu_percent()
    st.write(f"**CPU LOAD:** {cpu_usage}%")
    st.progress(cpu_usage / 100)
    
    st.write("---")
    st.markdown('**SLOGAN:** \n*"อยู่นิ่งๆ ไม่เจ็บตัว"*')

# --- 2. CSS DYNAMIC THEME (Enhanced) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&display=swap');
    .stApp {{ background-color: {st.session_state.bg_color} !important; color: {st.session_state.theme_color} !important; }}
    
    /* Neon Text Glow */
    h1, h2, h3, p, span, label {{ 
        font-family: 'Orbitron', sans-serif !important; 
        color: {st.session_state.theme_color} !important;
        text-shadow: 0px 0px 8px {st.session_state.theme_color}55;
    }}

    /* Audio Visualizer Simulation */
    .visualizer {{
        display: flex; align-items: flex-end; height: 30px; gap: 3px; margin-top: 10px;
    }}
    .bar {{
        background: {st.session_state.theme_color}; width: 4px;
        animation: uplift 0.8s infinite ease-in-out alternate;
    }}
    @keyframes uplift {{ 0% {{ height: 5px; }} 100% {{ height: 30px; }} }}
    
    /* Marquee & Buttons */
    .marquee {{
        border: 1px solid {st.session_state.theme_color};
        background: rgba(255,255,255,0.05); padding: 10px; border-radius: 5px;
    }}
    .stButton>button {{
        border: 1px solid {st.session_state.theme_color} !important;
        background: transparent !important; color: {st.session_state.theme_color} !important;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        background: {st.session_state.theme_color} !important; color: {st.session_state.bg_color} !important;
        box-shadow: 0px 0px 15px {st.session_state.theme_color};
    }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. ระบบจัดการเพลง ---
music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])

if music_files:
    if 'song_index' not in st.session_state:
        st.session_state.song_index = 0
    
    current_song = music_files[st.session_state.song_index]

    col_title, col_stat = st.columns([3, 1])
    with col_title:
        st.title("🎸 SYNAPSE MUSIC")
    with col_stat:
        # Visualizer หลอกๆ แต่สวย
        bars = "".join([f'<div class="bar" style="animation-delay: {random.random()}s"></div>' for _ in range(20)])
        st.markdown(f'<div class="visualizer">{bars}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="marquee"><marquee scrollamount="8">NOW STREAMING: {current_song} --- STATUS: ONLINE --- ENJOY THE VIBE</marquee></div>', unsafe_allow_html=True)

    # Media Display
    base_name = os.path.splitext(current_song)[0]
    if os.path.exists(base_name + ".mp4"):
        st.video(base_name + ".mp4", loop=True, autoplay=True, muted=True)
    else:
        st.audio(current_song)

    # --- 4. ระบบแชต & Playlist ---
    st.markdown("---")
    col_chat, col_list = st.columns([2, 1])

    with col_chat:
        st.subheader("🌐 LIVE TERMINAL")
        CHAT_FILE = "public_chat.txt"
        
        if os.path.exists(CHAT_FILE):
            with open(CHAT_FILE, "r", encoding="utf-8") as f:
                chat_history = f.readlines()[-15:] # อ่าน 15 บรรทัดล่าสุด
                chat_data = "".join(chat_history)
        else:
            chat_data = "SYSTEM: Welcome to Synapse Lobby..."

        st.text_area("Terminal Output", value=chat_data, height=250, disabled=True, label_visibility="collapsed")
        
        with st.form("chat_form", clear_on_submit=True):
            msg = st.text_input("ENTER MESSAGE >", placeholder="Type here...")
            if st.form_submit_button("EXECUTE"):
                if msg:
                    now = datetime.now().strftime("%H:%M")
                    with open(CHAT_FILE, "a", encoding="utf-8") as f:
                        f.write(f"[{now}] {st.session_state.user_id}: {msg}\n")
                    st.rerun()

    with col_list:
        st.subheader("🎧 ARCHIVE")
        with st.container(border=True, height=310):
            for i, song in enumerate(music_files):
                btn_label = f"» {song}" if i == st.session_state.song_index else f"  {song}"
                if st.button(btn_label, key=f"s_{i}", use_container_width=True):
                    st.session_state.song_index = i
                    st.rerun()

    # ปุ่มควบคุม
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("PREVIOUS"):
            st.session_state.song_index = (st.session_state.song_index - 1) % len(music_files)
            st.rerun()
    with c2:
        if st.button("NEXT"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()
    with c3:
        if st.button("RANDOMIZE"):
            st.session_state.song_index = random.randint(0, len(music_files) - 1)
            st.rerun()

else:
    st.error("SYSTEM ERROR: NO .MP3 FILES DETECTED IN DIRECTORY.")
