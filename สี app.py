import streamlit as st
# แก้การ import ใหม่ตามมาตรฐานเวอร์ชั่น 2.0+
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import TextClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
import os

def create_lyrics_video():
    if not os.path.exists("ta101.mp4"):
        st.error("ไม่พบไฟล์ ta101.mp4")
        return

    # 1. โหลดวิดีโอ
    video = VideoFileClip("ta101.mp4")

    # 2. เนื้อเพลงพร้อมเวลา (นาที.วินาที)
    lyrics_data = [
        (1.0, 10.0, "วันหนึ่งถ้าเธมองย้อนกลับมา\nอาจจะเห็นสิ่งที่เคยทำพังลงไป"),
        (13.0, 23.0, "แต่ถึงตอนนั้น ฉันคงเดินไกล\nทิ้งเรื่องของเราไว้ในอดีต")
    ]

    clips = [video]

    # 3. สร้าง Text (เวอร์ชั่นใหม่ต้องระบุพารามิเตอร์ชัดเจน)
    for start, end, text in lyrics_data:
        try:
            txt_clip = (TextClip(text=text, font_size=50, color='yellow', font='Arial')
                        .with_start(start)
                        .with_duration(end - start)
                        .with_position(('center', 0.8 * video.h)))
            clips.append(txt_clip)
        except Exception as e:
            st.warning(f"เลเยอร์ข้อความติดปัญหา: {e}")

    # 4. รวมร่าง
    final = CompositeVideoClip(clips)
    output_file = "ta101_lyrics_v2.mp4"
    
    # เขียนไฟล์
    final.write_videofile(output_file, fps=24, codec="libx264")
    return output_file

st.title("🎬 SYNAPSE LYRICS VIDEO")
if st.button("🚀 เริ่มทำวิดีโอ (Fix Error)"):
    with st.spinner("กำลังประมวลผล..."):
        res = create_lyrics_video()
        if res:
            st.video(res)
