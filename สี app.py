import streamlit as st
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

def make_video():
    if not os.path.exists("ta101.mp4"):
        st.error("หาไฟล์ ta101.mp4 ไม่เจอครับ!")
        return

    # โหลดคลิป
    base_video = VideoFileClip("ta101.mp4")
    
    # สร้างข้อความ (ตรวจสอบว่าเครื่องมี ImageMagick แล้ว)
    try:
        txt = TextClip(
            text="วันหนึ่งถ้าเธอมองย้อนกลับมา",
            font_size=70,
            color='yellow',
            duration=5
        ).with_position(('center', 'center')).with_start(1)
        
        # รวมร่าง
        final = CompositeVideoClip([base_video, txt])
        final.write_videofile("result.mp4", fps=24)
        return "result.mp4"
    except Exception as e:
        st.error(f"ติดปัญหาเรื่องการสร้างตัวหนังสือ: {e}")
        st.info("เพื่อนลืมสร้างไฟล์ packages.txt หรือเปล่า?")
        return None

st.title("🎬 SYNAPSE Video Maker")
if st.button("🚀 เสกตัวหนังสือวิ้ง"):
    res = make_video()
    if res:
        st.video(res)
