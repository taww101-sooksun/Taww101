import streamlit as st
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

def make_video():
    video_file = "ta101.mp4"
    
    # เช็กไฟล์วิดีโอก่อน
    if not os.path.exists(video_file):
        st.error(f"❌ Video file '{video_file}' not found!")
        return None

    try:
        # 1. โหลดวิดีโอ
        clip = VideoFileClip(video_file)
        
        # 2. ใส่เนื้อเพลงภาษาอังกฤษ (ใช้ฟอนต์มาตรฐาน)
        # เราจะไม่ระบุ font_path แต่จะใช้ชื่อฟอนต์กลางๆ แทน
        txt = (TextClip(
                text="One day if you look back...", 
                font_size=70, 
                color='yellow', 
                font='Arial', # ฟอนต์มาตรฐานภาษาอังกฤษ
                duration=5
            ).with_start(1).with_position(('center', 'center')))
        
        # 3. รวมร่าง
        final = CompositeVideoClip([clip, txt])
        output = "synapse_test_en.mp4"
        
        # 4. เขียนไฟล์ (ตั้งค่าแบบประหยัด RAM)
        final.write_videofile(
            output, 
            fps=15, 
            codec="libx264", 
            audio_codec="aac",
            threads=1,
            logger=None
        )
        
        clip.close()
        return output

    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None

# --- UI ---
st.title("🎬 SYNAPSE Video Test (English)")
st.write("Testing video processing without Thai fonts...")

if st.button("🚀 Run English Version"):
    with st.spinner("Processing... Please wait."):
        res = make_video()
        if res:
            st.video(res)
            st.success("English version works!")
