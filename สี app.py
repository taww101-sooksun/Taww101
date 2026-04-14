import streamlit as st
import os
import random
import streamlit.components.v1 as components
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

# --- 1. SET UP & THEME SELECTOR ---
st.set_page_config(page_title="SYNAPSE ROOMS", layout="wide")

if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
if 'bg_color' not in st.session_state: st.session_state.bg_color = "#121212"
if 'song_index' not in st.session_state: st.session_state.song_index = 0

with st.sidebar:
    if os.path.exists("logo2.jpg"):
        st.image("logo2.jpg", use_container_width=True)
    
    st.markdown("### 🎨 ปรับแต่งสีระบบ")
    st.session_state.theme_color = st.color_picker("เลือกสีนีออน", st.session_state.theme_color)
    st.session_state.bg_color = st.color_picker("เลือกสีพื้นหลัง", st.session_state.bg_color)
    
    st.write("---")
    st.markdown('**สโลแกน:** \n*"อยู่นิ่งๆ ไม่เจ็บตัว"*')

# --- 2. CSS DYNAMIC THEME ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {st.session_state.bg_color} !important; color: {st.session_state.theme_color} !important; }}
    [data-testid="stVVerticalBlock"] > div > div > [data-testid="stVerticalBlockBorderWrapper"] {{
        border: 2px solid {st.session_state.theme_color} !important;
        background: rgba(0, 0, 0, 0.4) !important;
    }}
    .marquee {{
        width: 100%; overflow: hidden; white-space: nowrap; background: rgba(0,0,0,0.6);
        padding: 15px 0; border: 2px solid {st.session_state.theme_color}; border-radius: 12px;
    }}
    .marquee p {{
        display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite;
        font-size: 22px; color: {st.session_state.theme_color}; text-shadow: 0px 0px 10px {st.session_state.theme_color};
    }}
    @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
    .stButton>button {{
        background-color: transparent !important; color: {st.session_state.theme_color} !important;
        border: 1px solid {st.session_state.theme_color} !important; transition: 0.3s;
    }}
    .stButton>button:hover {{ background-color: {st.session_state.theme_color} !important; color: {st.session_state.bg_color} !important; }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. ระบบจัดการเพลงและวิดีโอ ---
music_files = sorted([f for f in os.listdir('.') if f.lower().endswith(".mp3")])
video_files = sorted([f for f in os.listdir('.') if f.endswith(".mp4") and not f.startswith("sync_")])

tab_music, tab_video = st.tabs(["🎧 MUSIC PLAYER", "🎬 VIDEO ENGINE"])

with tab_music:
    if music_files:
        current_song = music_files[st.session_state.song_index]
        st.markdown(f'<div class="marquee"><p>NOW PLAYING: {current_song} •--• SYNAPSE STATION </p></div>', unsafe_allow_html=True)
        
        # แสดงวิดีโอประกอบหรือรูปภาพ
        base_name = os.path.splitext(current_song)[0]
        if os.path.exists(base_name + ".mp4"): st.video(base_name + ".mp4", loop=True, autoplay=True, muted=True)
        
        st.audio(current_song)
        
        with st.container(border=True, height=250):
            for i, song in enumerate(music_files):
                if st.button(f"{'▶️' if i==st.session_state.song_index else ''} {i+1}. {song}", key=f"ms_{i}"):
                    st.session_state.song_index = i
                    st.rerun()
    else:
        st.error("ไม่พบไฟล์เพลงครับ")

with tab_video:
    st.subheader("🎬 ระบบผลิตวิดีโอเนื้อเพลง")
    if video_files:
        selected_vdo = st.selectbox("เลือกวิดีโอต้นฉบับ:", video_files)
        
        # Timeline ที่เพื่อนส่งมาล่าสุด
        lyrics_data = [
            (1.0, 10.0, "วันหนึ่งถ้าเธอมองย้อนกลับมา\nอาจจะเห็นสิ่งที่เคยทำพังลงไป"),
            (13.0, 23.0, "แต่ถึงตอนนั้น ฉันคงเดินไกล\nทิ้งเรื่องของเราไว้ในอดีตคำที่เธอเคยให้")
        ]

        if st.button("🚀 เริ่มผลิตวิดีโอ (วิ้งๆ)"):
            with st.spinner("กำลังเสกตัวหนังสือ..."):
                try:
                    clip = VideoFileClip(selected_vdo)
                    txt_clips = [clip]
                    for s, e, txt in lyrics_data:
                        t = TextClip(text=txt, font_size=50, color='yellow', font='DejaVu-Sans-Bold',
                                     duration=(e-s), method='caption', size=(clip.w*0.8, None)
                                    ).with_start(s).with_position(('center', 0.8*clip.h))
                        txt_clips.append(t)
                    
                    final = CompositeVideoClip(txt_clips)
                    out = f"sync_{selected_vdo}"
                    final.write_videofile(out, fps=12, codec="libx264")
                    st.video(out)
                except Exception as e: st.error(f"❌ ระบบดื้อ: {e}")
    else:
        st.info("ไม่พบไฟล์วิดีโอ .mp4 สำหรับทำเนื้อเพลง")

# --- 4. AUTO NEXT JAVASCRIPT ---
components.html("""<script> /* JS Code เดิมของเพื่อนที่เวิร์ค */ </script>""", height=0)
