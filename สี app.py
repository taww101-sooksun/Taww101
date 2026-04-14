import streamlit as st
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

# --- 1. SET UP ---
st.set_page_config(page_title="SYNAPSE ROOMS", layout="wide")

if 'theme_color' not in st.session_state: st.session_state.theme_color = "#39FF14"
if 'bg_color' not in st.session_state: st.session_state.bg_color = "#121212"
if 'user' not in st.session_state: st.session_state.user = "Ta101"

with st.sidebar:
    st.title("⚙️ CONTROL")
    st.session_state.theme_color = st.color_picker("เลือกสีนีออน", st.session_state.theme_color)
    st.session_state.bg_color = st.color_picker("เลือกสีพื้นหลัง", st.session_state.bg_color)
    st.write("---")
    st.markdown('**สโลแกน:** \n*"อยู่นิ่งๆ ไม่เจ็บตัว"*')

# --- 2. CSS & MARQUEE ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: {st.session_state.bg_color} !important; color: {st.session_state.theme_color} !important; }}
    .marquee {{
        width: 100%; overflow: hidden; white-space: nowrap; background: rgba(0,0,0,0.6);
        padding: 15px 0; border: 2px solid {st.session_state.theme_color}; border-radius: 12px;
    }}
    .marquee p {{
        display: inline-block; padding-left: 100%; animation: marquee 20s linear infinite;
        font-size: 22px; color: {st.session_state.theme_color}; text-shadow: 0px 0px 10px {st.session_state.theme_color};
    }}
    @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA: LYRICS TIMELINE (วินาที) ---
lyrics_timeline = [
    (10, 10, "วันหนึ่งถ้าเธอมองย้อนกลับมา\nอาจจะเห็นสิ่งที่เคยทำพังลงไป"),
    (13, 23, "แต่ถึงตอนนั้น ฉันคงเดินไกล\nทิ้งเรื่องของเราไว้ในอดีต"),
    (26, 60, "ขอบคุณถ้อยคำที่เคยทำฉันร้าว\n(AGENT: Ta101)"),
    (64, 74, "ปล่อยวางความโกรธที่เผาใจ..."),
    (77, 85, "ทิ้งความโลภที่ไม่มีวันพอ"),
    (101, 111, "วันหนึ่งถ้าเธอมองย้อนกลับมา (Reprise)"),
    (114, 124, "แต่ถึงตอนนั้น ฉันคงเดินไกล (Reprise)"),
    (127, 163, "ยิ้มทั้งที่แผลยังสด\nกอดตัวเองเพราะไม่มีใครอยู่"),
    (168, 178, "ปล่อยวางความโกรธที่เผาใจ...\nทิ้งความโลภที่ไม่มีวันพอ")
]

# --- 4. MAIN INTERFACE ---
tab1, tab2 = st.tabs(["🎧 MUSIC", "🎬 VIDEO ENGINE"])

with tab1:
    st.markdown(f'<div class="marquee"><p>NOW PLAYING: ta101.mp3 •--• BY: {st.session_state.user} </p></div>', unsafe_allow_html=True)
    if os.path.exists("ta101.mp3"):
        st.audio("ta101.mp3")
    else:
        st.error("❌ ไม่พบไฟล์ ta101.mp3 ในระบบ")

with tab2:
    st.subheader("🎬 ระบบเสกเนื้อเพลงลงวิดีโอ")
    if os.path.exists("ta101.mp4"):
        if st.button("🚀 เริ่มสร้างวิดีโอวิ้งๆ (ta101.mp4)"):
            with st.spinner("กำลังประกอบร่าง..."):
                try:
                    clip = VideoFileClip("ta101.mp4")
                    txt_clips = [clip]
                    for s, e, txt in lyrics_timeline:
                        t = TextClip(text=txt, font_size=45, color='yellow', font='DejaVu-Sans-Bold',
                                     duration=(e-s if e>s else 1), method='caption', size=(clip.w*0.8, None)
                                    ).with_start(s).with_position(('center', 0.8*clip.h))
                        txt_clips.append(t)
                    
                    final = CompositeVideoClip(txt_clips)
                    final.write_videofile("sync_ta101.mp4", fps=12, codec="libx264")
                    st.video("sync_ta101.mp4")
                    st.success("✅ สร้างสำเร็จแล้วครับ Ta101!")
                except Exception as e:
                    st.error(f"❌ พังเพราะ: {e}")
    else:
        st.error("❌ ไม่พบไฟล์ ta101.mp4 ในระบบ")
