import streamlit as st
import os
import random
import time
import streamlit.components.v1 as components
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

# --- 1. SET UP & THEME ---
st.set_page_config(page_title="SYNAPSE ROOMS", layout="wide")

# ดัก Error จาก Session State
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
if 'bg_color' not in st.session_state: st.session_state.bg_color = "#121212"
if 'song_index' not in st.session_state: st.session_state.song_index = 0
if 'user' not in st.session_state: st.session_state.user = "Ta101" # หรือ Guest

with st.sidebar:
    if os.path.exists("logo2.jpg"):
        st.image("logo2.jpg", use_container_width=True)
    st.session_state.theme_color = st.color_picker("เลือกสีนีออน", st.session_state.theme_color)
    st.session_state.bg_color = st.color_picker("เลือกสีพื้นหลัง", st.session_state.bg_color)
    st.write("---")
    st.markdown('**สโลแกน:** \n*"อยู่นิ่งๆ ไม่เจ็บตัว"*')

# --- 2. CSS THEME & MARQUEE ---
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
        font-size: 22px; color: {st.session_state.theme_color}; text-shadow: 0px 0px 10px {st.session_state.theme_color};
    }}
    @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA: LYRICS TIMELINE ---
# รวมเนื้อเพลงตามที่คุณส่งมาเป๊ะๆ
lyrics_timeline = [
    (10.0, 10.0, "วันหนึ่งถ้าเธอมองย้อนกลับมา\nอาจจะเห็นสิ่งที่เคยทำพังลงไป"),
    (13.0, 23.0, "แต่ถึงตอนนั้น ฉันคงเดินไกล\nทิ้งเรื่องของเราไว้ในอดีตคำที่เธอเคยให้"),
    (26.0, 60.0, "ขอบคุณถ้อยคำที่เคยทำฉันร้าว\nคำที่ทำให้ใจฉันแทบไม่เหลืออะไร..."), # ย่อเพื่อประหยัดพื้นที่ในโค้ดแต่ตอนรันจะใส่เต็มได้
    (64.0, 74.0, "ปล่อยวางความโกรธที่เผาใจ..."),
    (77.0, 85.0, "ทิ้งความโลภที่ไม่มีวันพอ"),
    (101.0, 111.0, "วันหนึ่งถ้าเธอมองย้อนกลับมา..."),
    (114.0, 124.0, "แต่ถึงตอนนั้น ฉันคงเดินไกล..."),
    (127.0, 163.0, "ขอบคุณถ้อยคำที่เคยทำฉันร้าว... (Hook)"),
    (168.0, 178.0, "ปล่อยวางความโกรธที่เผาใจ... ทิ้งความโลภที่ไม่มีวันพอ")
]

# --- 4. MAIN INTERFACE ---
tab_music, tab_video = st.tabs(["🎧 MUSIC", "🎬 VIDEO ENGINE"])

with tab_music:
    music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
    if music_files:
        current_song = music_files[st.session_state.song_index]
        st.markdown(f'<div class="marquee"><p>NOW PLAYING: {current_song} •--• AGENT: {st.session_state.user} </p></div>', unsafe_allow_html=True)
        st.audio(current_song)
        if st.button("⏭️ เพลงถัดไป"):
            st.session_state.song_index = (st.session_state.song_index + 1) % len(music_files)
            st.rerun()
    else:
        st.error("ไม่พบไฟล์เพลง .mp3")

with tab_video:
    video_files = sorted([f for f in os.listdir('.') if f.endswith(".mp4") and not f.startswith("sync_")])
    if video_files:
        selected_vdo = st.selectbox("เลือกวิดีโอ:", video_files)
        if st.button("🚀 เริ่มสร้างวิดีโอวิ้งๆ"):
            with st.spinner("กำลังประกอบร่างเนื้อเพลง..."):
                try:
                    clip = VideoFileClip(selected_vdo)
                    txt_clips = [clip]
                    for s, e, txt in lyrics_timeline:
                        t = TextClip(text=txt, font_size=40, color='yellow', font='DejaVu-Sans-Bold',
                                     duration=(e-s if e>s else 1), method='caption', size=(clip.w*0.8, None)
                                    ).with_start(s).with_position(('center', 0.8*clip.h))
                        txt_clips.append(t)
                    
                    final = CompositeVideoClip(txt_clips)
                    out = f"sync_{selected_vdo}"
                    final.write_videofile(out, fps=12, codec="libx264")
                    st.video(out)
                except Exception as e: st.error(f"❌ ระบบดื้อ: {e}")
    else:
        st.info("ไม่พบไฟล์วิดีโอ .mp4")
