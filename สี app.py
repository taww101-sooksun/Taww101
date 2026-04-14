import streamlit as st
import os
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

def make_video():
    # 1. รายชื่อไฟล์ที่ต้องมี (เช็คชื่อให้ตรงกับใน GitHub นะเพื่อน)
    video_file = "ta101.mp4"
    font_file = "THSarabunNew.ttf"

    # แสดงรายชื่อไฟล์ทั้งหมดที่ระบบมองเห็น (เพื่อช่วยเพื่อนเช็คความจริง)
    all_files = os.listdir(".")
    st.write("ไฟล์ที่ระบบมองเห็นตอนนี้:", all_files)

    # 2. เช็คไฟล์วิดีโอ
    if not os.path.exists(video_file):
        st.error(f"❌ ไม่พบไฟล์วิดีโอชื่อ {video_file}")
        return None

    # 3. เช็คไฟล์ฟอนต์
    if not os.path.exists(font_file):
        st.error(f"❌ ไม่พบไฟล์ฟอนต์ชื่อ {font_file}")
        st.info("ลองเช็คดูว่าชื่อไฟล์มี .ttf ซ้อนกันไหม หรือเป็นตัวพิมพ์เล็ก/ใหญ่ครับ")
        return None

    try:
        base_video = VideoFileClip(video_file)
        
        # เนื้อเพลง
        lyrics_data = [
            (1.0, 10.0, "วันหนึ่งถ้าเธอมองย้อนกลับมา\nอาจจะเห็นสิ่งที่เคยทำพังลงไป"),
            (13.0, 23.0, "แต่ถึงตอนนั้น ฉันคงเดินไกล\nทิ้งเรื่องของเราไว้ในอดีต")
        ]
        
        clips = [base_video]
        for start, end, text in lyrics_data:
            txt_clip = (TextClip(
                text=text, 
                font_size=70, 
                color='yellow', 
                font=font_file, 
                duration=(end - start)
            ).with_start(start).with_position(('center', 0.8 * base_video.h)))
            clips.append(txt_clip)
        
        final = CompositeVideoClip(clips)
        output_name = "synapse_v1.mp4"
        final.write_videofile(output_name, fps=24, codec="libx264")
        return output_name

    except Exception as e:
        st.error(f"❌ เกิดข้อผิดพลาด: {e}")
        return None

st.title("🎬 SYNAPSE Lyrics Maker")
if st.button("🚀 เริ่มทำวิดีโอ"):
    res = make_video()
    if res:
        st.video(res)
